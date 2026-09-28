"""
Loads real ML-detected weather events into weather_platform.db.

Why this exists
----------------
The data-science module (SIH_26069_Member3_FINAL) produces detected weather
events as JSON files, but nothing in the project automatically pushes them
into the backend's database — the backend only has whatever seed.py inserted
(2 sample rows) until something calls POST /internal/events(/bulk), or a
script writes to the DB directly. This script does the latter: it reads the
data-science output and inserts it straight into the `weather_events` table
using the same models/session as the rest of the backend, so `python
seed.py` + `python load_ml_events.py` gives you a dashboard with real,
ML-detected events instead of just the 2 seed rows.

Run this from inside backend/, after seed.py, with the same venv active:
    python load_ml_events.py

Source file preference (first one found wins)
-----------------------------------------------
1. ../SIH_26069_Member3_FINAL/outputs/evidence_scored_events.json
   (curated, multi-source-verified event *episodes* — 185 records, the most
   meaningful ones for a dashboard)
2. ../SIH_26069_Member3_FINAL/outputs/verified_weather_events_v2.json
3. ../SIH_26069_Member3_FINAL/outputs/weather_events.json
   (raw per-timestamp detections, 5,952 rows — includes many "Normal" rows;
   those are filtered out here since they aren't really "events")

Field mapping
-------------
The data-science output and the backend's WeatherEvent schema don't use the
same shape (nested location/weather/source objects vs. a flat row, and
different field names for confidence/verification), so this script maps:

    event_type              -> event_type            (as-is)
    location.city           -> city
    location.state          -> state
    location.latitude       -> latitude
    location.longitude      -> longitude
    severity                -> severity               (as-is)
    model_confidence /
      confidence_score      -> confidence_score        (rounded to int)
    verification_status     -> verification_status      (remapped, see below)
    start_time / timestamp  -> timestamp

verification_status remapping (data-science vocabulary -> backend vocabulary):
    "Supported"     -> "Verified"
    "Contradicted"  -> "Rejected"
    "Needs Review"  -> "Pending"      (anything else also falls back to Pending)

This keeps the backend's existing admin workflow (Pending/Verified/
Suspicious/Rejected) intact — an admin can still re-review any of these
through the normal /api/admin/events/{id}/verify endpoint.
"""

import json
import os
from datetime import datetime
from typing import Optional

from database import SessionLocal, engine, Base
import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DS_OUTPUTS_DIR = os.path.join(
    BASE_DIR, "..", "SIH_26069_Member3_FINAL", "outputs"
)

CANDIDATE_FILES = [
    "evidence_scored_events.json",
    "verified_weather_events_v2.json",
    "weather_events.json",
]

STATUS_MAP = {
    "Supported": "Verified",
    "Contradicted": "Rejected",
    "Needs Review": "Pending",
}

# Cap how many rows we insert from the raw per-timestamp file (weather_events.json),
# since it has ~6,000 rows and most are "Normal" (not real events).
MAX_RAW_EVENTS = 500


def find_source_file():
    for name in CANDIDATE_FILES:
        path = os.path.join(DS_OUTPUTS_DIR, name)
        if os.path.exists(path):
            return name, path
    return None, None


def parse_timestamp(value: str) -> datetime:
    # Data-science outputs use "YYYY-MM-DD HH:MM:SS"; be lenient just in case.
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    # Last resort: let fromisoformat try (handles most ISO variants)
    return datetime.fromisoformat(value)


def to_weather_event(record: dict) -> Optional[models.WeatherEvent]:
    location = record.get("location", {})
    city = location.get("city")
    state = location.get("state")
    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if not (city and state and latitude is not None and longitude is not None):
        return None  # skip malformed rows rather than guessing values

    event_type = record.get("event_type", "Unknown")
    if event_type == "Normal":
        return None  # not a reportable event

    severity = record.get("severity", "Low")

    raw_confidence = record.get("confidence_score", record.get("model_confidence", 0))
    try:
        confidence_score = int(round(float(raw_confidence)))
    except (TypeError, ValueError):
        confidence_score = 0
    confidence_score = max(0, min(100, confidence_score))

    raw_status = record.get("verification_status")
    verification_status = STATUS_MAP.get(raw_status, "Pending")

    raw_timestamp = record.get("start_time") or record.get("timestamp")
    if not raw_timestamp:
        return None
    try:
        timestamp = parse_timestamp(raw_timestamp)
    except ValueError:
        return None

    return models.WeatherEvent(
        event_type=event_type,
        city=city,
        state=state,
        latitude=float(latitude),
        longitude=float(longitude),
        severity=severity,
        confidence_score=confidence_score,
        verification_status=verification_status,
        timestamp=timestamp,
        source=record.get("source", "Unknown"),
    )


def main():
    Base.metadata.create_all(bind=engine)

    filename, path = find_source_file()
    if not path:
        print(
            "No data-science output found in "
            f"{os.path.normpath(DS_OUTPUTS_DIR)}. "
            "Run the data-science pipeline first "
            "(python SIH_26069_Member3_FINAL/src/run_all.py), then re-run this script."
        )
        return

    print(f"Loading events from {filename} ...")
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    if filename == "weather_events.json" and len(records) > MAX_RAW_EVENTS:
        print(
            f"{filename} has {len(records)} raw per-timestamp rows; "
            f"keeping only non-'Normal' events, capped at {MAX_RAW_EVENTS}."
        )

    events = []
    for record in records:
        event = to_weather_event(record)
        if event is not None:
            events.append(event)
        if filename == "weather_events.json" and len(events) >= MAX_RAW_EVENTS:
            break

    if not events:
        print("Nothing to insert (no valid, non-'Normal' events found).")
        return

    db = SessionLocal()
    try:
        db.add_all(events)
        db.commit()
        print(f"Inserted {len(events)} events into weather_events.")
    except Exception as exc:
        db.rollback()
        print(f"Failed to insert events, rolled back: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
