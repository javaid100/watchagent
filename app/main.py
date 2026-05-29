from fastapi import FastAPI, Depends
from app.api.health import router as health_router
from app.database.init_db import init_db, SessionLocal
from app.database.models import Reading, Event, CityEnum
from app.services.polling_service import start_polling
import asyncio

app = FastAPI(title="WatchAgent Weather Monitor")

# -----------------------------
# DATABASE DEPENDENCY
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# STARTUP EVENT
# -----------------------------
@app.on_event("startup")
async def startup_event():
    print("\n--- FASTAPI STARTUP EVENT FIRED ---")
    print("Initializing database...")
    init_db()
    print("Launching background weather poller...\n")
    asyncio.create_task(start_polling())

# -----------------------------
# ROUTES
# -----------------------------
app.include_router(health_router)

@app.get("/")
def root():
    return {"message": "WatchAgent API is running"}

# -----------------------------
# READINGS ENDPOINT
# -----------------------------
@app.get("/readings")
def get_readings(city: str | None = None, limit: int = 50, db=Depends(get_db)):
    q = db.query(Reading).order_by(Reading.timestamp.desc())
    if city:
        try:
            enum_city = CityEnum(city.lower())
            q = q.filter(Reading.city == enum_city)
        except ValueError:
            print(f"Invalid city provided: {city}")
            return {"error": f"Invalid city '{city}'. Valid: ottawa, toronto, vancouver"}
    results = q.limit(limit).all()
    return {"readings": results}

# -----------------------------
# EVENTS ENDPOINT
# -----------------------------
@app.get("/events")
def get_events(city: str | None = None, limit: int = 50, db=Depends(get_db)):
    q = db.query(Event).order_by(Event.timestamp.desc())
    if city:
        try:
            enum_city = CityEnum(city.lower())
            q = q.filter(Event.city == enum_city)
        except ValueError:
            print(f"Invalid city provided: {city}")
            return {"error": f"Invalid city '{city}'. Valid: ottawa, toronto, vancouver"}
    results = q.limit(limit).all()
    return {"events": results}
