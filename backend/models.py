"""
SQLAlchemy ORM models.

WeatherEvent matches the exact schema from the project spec (Section 9 of the
requirements doc) — do not add fields like `reports`, `sources`, or
`description` without agreeing with the frontend/data-science team first.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func

from database import Base


class User(Base):
    """Admin/analyst users. Normal weather-app visitors are NOT stored here —
    the public app has no accounts at all, per the project requirement."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="admin")  # admin | analyst | user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WeatherEvent(Base):
    """Matches the agreed frontend schema exactly:
    id, event_type, city, state, latitude, longitude, severity,
    confidence_score, verification_status, timestamp.
    """

    __tablename__ = "weather_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)          # e.g. "Flood"
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String, nullable=False)             # e.g. "High"
    confidence_score = Column(Integer, nullable=False)     # 0-100
    verification_status = Column(String, nullable=False, default="Pending")
    # Pending | Verified | Suspicious | Rejected
    timestamp = Column(DateTime, nullable=False)
    source = Column(String, nullable=True, default="Unknown")
