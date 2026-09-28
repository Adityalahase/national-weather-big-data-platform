"""
One-time setup script.

Run once after installing dependencies:
    python seed.py

Creates the database tables (if not already created by main.py) and inserts
a default admin user + a couple of sample events so you can test the API
immediately. CHANGE THE DEFAULT PASSWORD before sharing this repo/demo.
"""

from datetime import datetime

from database import SessionLocal, engine, Base
import models
from auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "ChangeMe123!"  # change this immediately

existing = db.query(models.User).filter(models.User.username == DEFAULT_ADMIN_USERNAME).first()
if not existing:
    admin = models.User(
        username=DEFAULT_ADMIN_USERNAME,
        email="admin@example.com",
        password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print(f"Created admin user: username='{DEFAULT_ADMIN_USERNAME}' password='{DEFAULT_ADMIN_PASSWORD}'")
else:
    print("Admin user already exists, skipping.")

# Sample events matching the exact schema from the spec
sample_events = [
    models.WeatherEvent(
        event_type="Flood",
        city="Pune",
        state="Maharashtra",
        latitude=18.5204,
        longitude=73.8567,
        severity="High",
        confidence_score=92,
        verification_status="Verified",
        timestamp=datetime(2026, 9, 1, 22, 30, 0),
        source="NASA POWER"
    ),
    models.WeatherEvent(
        event_type="Cyclone",
        city="Visakhapatnam",
        state="Andhra Pradesh",
        latitude=17.6868,
        longitude=83.2185,
        severity="Medium",
        confidence_score=76,
        verification_status="Pending",
        timestamp=datetime(2026, 9, 5, 10, 15, 0),
        source="Open-Meteo"
    )
]

if db.query(models.WeatherEvent).count() == 0:
    db.add_all(sample_events)
    db.commit()
    print(f"Inserted {len(sample_events)} sample weather events.")
else:
    print("Weather events already exist, skipping sample insert.")

db.close()
