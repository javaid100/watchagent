from fastapi import APIRouter, Depends
from app.database.init_db import SessionLocal
from app.database.models import Reading, Event

router = APIRouter(prefix="/health", tags=["Health"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def health_check(db=Depends(get_db)):
    readings_count = db.query(Reading).count()
    events_count = db.query(Event).count()

    return {
        "status": "ok",
        "readings_stored": readings_count,
        "events_stored": events_count
    }
