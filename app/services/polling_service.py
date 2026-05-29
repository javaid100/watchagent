import asyncio

from app.database.init_db import SessionLocal
from app.services.weather_service import fetch_weather
from app.services.pipeline import (
    is_duplicate,
    save_reading,
    detect_events,
    save_events,
)
from app.core.config import settings
from app.core.logging import log_info, log_exception


CITIES = ["ottawa", "toronto", "vancouver"]


# =========================================================
# RETRY WRAPPER (IMPORTANT FIX)
# =========================================================
async def fetch_with_retry(city: str, retries: int = 3, delay: float = 1.0):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return await fetch_weather(city)

        except Exception as e:
            last_error = e
            log_exception(f"[FETCH_RETRY] city={city} attempt={attempt}")

            await asyncio.sleep(delay)

    raise Exception(f"fetch_weather failed after retries for city={city}") from last_error


# =========================================================
# SINGLE POLL CYCLE
# =========================================================
async def poll_once():
    log_info("[POLL_CYCLE_START]")

    for city in CITIES:
        db = SessionLocal()

        try:
            log_info(f"[FETCH_WEATHER] city={city}")

            weather = await fetch_with_retry(city)

            if not weather:
                log_exception(f"[EMPTY_WEATHER] city={city}")
                continue

            if is_duplicate(db, city, weather):
                log_info(f"[DUPLICATE_SKIPPED] city={city}")
                continue

            reading = save_reading(db, weather)
            log_info(f"[READING_SAVED] city={city} id={reading.id}")

            events = detect_events(db, city, weather)

            if events:
                created = save_events(db, city, events)
                log_info(f"[EVENTS_CREATED] city={city} count={len(created)}")
            else:
                log_info(f"[NO_EVENTS] city={city}")

        except Exception as e:
            log_error(f"[POLL_FAILURE] city={city} error={str(e)}")

        finally:
            db.close()


# =========================================================
# MAIN LOOP
# =========================================================
async def start_polling():
    log_info("[POLLING_SERVICE_STARTED]")

    while True:
        await poll_once()
        await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    asyncio.run(start_polling())