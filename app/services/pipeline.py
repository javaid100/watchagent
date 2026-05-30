import statistics
from sqlalchemy.orm import Session

from app.database.models import Reading, Event, CityEnum
from app.core.logging import log_info, log_error

from app.utils.weather_codes import get_weather_description, is_precipitation, get_weather_severity

# =========================================================
# THRESHOLDS
# =========================================================
MIN_HISTORY_POINTS = 3
ANOMALY_ZSCORE_THRESHOLD = 2
HIGH_SEVERITY_ZSCORE = 3
HEAVY_PRECIPITATION_MM = 2
CROSS_CITY_TEMP_GAP_C = 8


# =========================================================
# DEDUPLICATION
# =========================================================
def is_duplicate(db: Session, city: str, new_reading: dict) -> bool:
    last = (db.query(Reading).filter(Reading.city == CityEnum(city)).order_by(Reading.timestamp.desc()).first())
    if not last:
        return False
    def close(a, b, tol=0.01):
        return abs(a - b) <= tol
    return (
        close(last.temperature, new_reading["temperature"])
        and close(last.apparent_temperature, new_reading["apparent_temperature"])
        and close(last.precipitation, new_reading["precipitation"])
        and close(last.wind_speed, new_reading["wind_speed"])
        and last.weather_code == new_reading["weather_code"]
    )


# =========================================================
# SAVE READING
# =========================================================
def save_reading(db: Session, data: dict) -> Reading:
    reading = Reading(
        city=CityEnum(data["city"]),
        temperature=data["temperature"],
        apparent_temperature=data["apparent_temperature"],
        precipitation=data["precipitation"],
        wind_speed=data["wind_speed"],
        weather_code=data["weather_code"],
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


# =========================================================
# HISTORY
# =========================================================
def get_recent_readings(db: Session, city: str, limit: int = 10):
    return (db.query(Reading).filter(Reading.city == CityEnum(city)).order_by(Reading.timestamp.desc()).limit(limit).all())

def get_latest_city_readings(db: Session):
    cities = ["ottawa", "toronto", "vancouver"]
    latest = {}
    for c in cities:
        r = (db.query(Reading).filter(Reading.city == CityEnum(c)).order_by(Reading.timestamp.desc()).first())
        if r:
            latest[c] = r
    return latest


# =========================================================
# HELPERS
# =========================================================
def _zscore(value, mean, std):
    if std <= 0:
        return None
    return abs((value - mean) / std)


# =========================================================
# EVENT: TEMPERATURE ANOMALY
# =========================================================
def _temperature_event(city, current, avg, std):
    z = _zscore(current, avg, std)
    if z is None or z < ANOMALY_ZSCORE_THRESHOLD:
        return None
    severity = "HIGH" if z >= HIGH_SEVERITY_ZSCORE else "MEDIUM"
    return (
        "temp_anomaly",
        f"{get_weather_description(0)} context ignored | "
        f"Temperature anomaly in {city}: {current}°C vs {avg:.1f}°C "
        f"(severity={severity})",
    )


# =========================================================
# EVENT: WIND SPIKE
# =========================================================
def _wind_event(city, current, avg, std):
    z = _zscore(current, avg, std)
    if z is None or z < ANOMALY_ZSCORE_THRESHOLD:
        return None
    severity = "HIGH" if z >= HIGH_SEVERITY_ZSCORE else "MEDIUM"
    return ("wind_spike", f"Wind spike in {city}: {current} km/h vs {avg:.1f} km/h (severity={severity})")


# =========================================================
# EVENT: WEATHER CHANGE
# =========================================================
def _weather_change_event(last_code, new_code):
    if last_code == new_code:
        return None
    return (
        "weather_change",
        f"Weather changed from "
        f"{get_weather_description(last_code)} ({last_code}) "
        f"to "
        f"{get_weather_description(new_code)} ({new_code}) "
        f"[severity={get_weather_severity(new_code)}]",
    )


# =========================================================
# EVENT: PRECIPITATION
# =========================================================
def _precipitation_event(city, precip, weather_code):
    if precip <= HEAVY_PRECIPITATION_MM and not is_precipitation(weather_code):
        return None
    return ("heavy_precipitation", f"Heavy precipitation in {city}: {precip} mm ({get_weather_description(weather_code)})")

# =========================================================
# EVENT: CROSS CITY TEMP GAP
# =========================================================
def _cross_city_events(db: Session, city: str, current_temp: float):
    events = []
    latest = get_latest_city_readings(db)
    for other, reading in latest.items():
        if other == city:
            continue
        diff = abs(current_temp - reading.temperature)
        if diff >= CROSS_CITY_TEMP_GAP_C:
            direction = "warmer" if current_temp > reading.temperature else "colder"
            events.append(("cross_city_temp_gap", f"{city.capitalize()} is {diff:.1f}°C {direction} than {other.capitalize()}"))
    return events


# =========================================================
# MAIN EVENT ENGINE
# =========================================================
def detect_events(db: Session, city: str, new_reading: dict):
    log_info(f"[EVENT_DETECTION_START] city={city}")

    history = get_recent_readings(db, city)

    if len(history) < MIN_HISTORY_POINTS:
        log_info(f"[SKIP] insufficient history city={city}")
        return []

    temps = [r.temperature for r in history]
    winds = [r.wind_speed for r in history]

    avg_temp = statistics.mean(temps)
    avg_wind = statistics.mean(winds)

    std_temp = statistics.stdev(temps) if len(temps) > 1 else 0
    std_wind = statistics.stdev(winds) if len(winds) > 1 else 0

    current_temp = new_reading["temperature"]
    current_wind = new_reading["wind_speed"]
    current_precip = new_reading["precipitation"]
    current_code = new_reading["weather_code"]
    last_code = history[0].weather_code

    events = []

    # Core anomalies
    temp_event = _temperature_event(city, current_temp, avg_temp, std_temp)
    if temp_event:
        events.append(temp_event)

    wind_event = _wind_event(city, current_wind, avg_wind, std_wind)
    if wind_event:
        events.append(wind_event)

    # Weather intelligence layer (NEW)
    weather_event = _weather_change_event(last_code, current_code)
    if weather_event:
        events.append(weather_event)

    precip_event = _precipitation_event(city, current_precip, current_code)
    if precip_event:
        events.append(precip_event)

    # Cross-city comparison
    events.extend(_cross_city_events(db, city, current_temp))

    log_info(f"[EVENT_DETECTION_DONE] city={city} events={len(events)}")

    return events


# =========================================================
# SAVE EVENTS
# =========================================================
def save_events(db: Session, city: str, events: list):
    log_info(f"[SAVE_EVENTS_START] city={city} count={len(events)}")

    created = []
    city_enum = CityEnum(city)

    for event_type, description in events:
        ev = Event(city=city_enum, event_type=event_type, description=description)
        db.add(ev)
        created.append(ev)

    db.commit()

    for ev in created:
        db.refresh(ev)

    log_info(f"[SAVE_EVENTS_DONE] city={city} saved={len(created)}")

    return created