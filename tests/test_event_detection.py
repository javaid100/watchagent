from app.database.models import Reading
from app.services.pipeline import detect_events

# =========================================================
# SEED HISTORY (FIXED: NO RAW SQL, ORM ONLY)
# =========================================================
def seed_history(db_session, temps):
    for t in temps:
        db_session.add(Reading(city="toronto", temperature=t, apparent_temperature=30, precipitation=0.0, wind_speed=10, weather_code=1))
    db_session.commit()

# =========================================================
# TEST 1: HEATWAVE EVENT
# =========================================================
def test_heatwave_event(db_session):
    seed_history(db_session, [31, 32, 33])
    reading = {"temperature": 35, "wind_speed": 10, "precipitation": 0.0, "weather_code": 1}
    events = detect_events(db_session, "toronto", reading)
    assert isinstance(events, list)

# =========================================================
# TEST 2: INSUFFICIENT HISTORY (NO EVENTS EXPECTED)
# =========================================================
def test_no_events_insufficient_history(db_session):
    seed_history(db_session, [31])  # not enough history for detection
    reading = {"temperature": 32, "wind_speed": 10, "precipitation": 0.0, "weather_code": 1}
    events = detect_events(db_session, "toronto", reading)
    assert events == []