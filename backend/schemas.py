"""
Pydantic schemas — these define the exact JSON shapes going in/out of the API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ---------- Auth ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str


# ---------- Weather Events ----------

class WeatherEventBase(BaseModel):
    event_type: str
    city: str
    state: str
    latitude: float
    longitude: float
    severity: str
    confidence_score: int
    verification_status: str = "Pending"
    timestamp: datetime
    source: str = "Unknown"


class WeatherEventCreate(WeatherEventBase):
    """Used internally / by data-engineering ingestion jobs, not by the public."""
    pass


class WeatherEventOut(WeatherEventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class VerifyStatusUpdate(BaseModel):
    verification_status: str  # "Verified" | "Suspicious" | "Rejected"


# ---------- Admin stats ----------

class AdminStatistics(BaseModel):
    total_events: int
    pending: int
    verified: int
    suspicious: int
    rejected: int
    by_severity: dict
