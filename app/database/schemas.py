from pydantic import BaseModel
from datetime import datetime
from app.database.models import CityEnum


# ---------- READING ----------
class ReadingBase(BaseModel):
    city: CityEnum
    temperature: float
    apparent_temperature: float
    precipitation: float
    wind_speed: float
    weather_code: int

class ReadingCreate(ReadingBase):
    pass

class ReadingResponse(ReadingBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ---------- EVENT ----------
class EventBase(BaseModel):
    city: CityEnum
    event_type: str
    description: str

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True