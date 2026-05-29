from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class CityEnum(str, enum.Enum):
    ottawa = "ottawa"
    toronto = "toronto"
    vancouver = "vancouver"

class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(SAEnum(CityEnum, native_enum=False, validate_strings=True), nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    apparent_temperature = Column(Float, nullable=False)
    precipitation = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    weather_code = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(SAEnum(CityEnum, native_enum=False, validate_strings=True), nullable=False, index=True)
    event_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)