"""
Pushes detected weather events into the running backend over HTTP, using
POST /internal/events/bulk (the endpoint that already existed in
backend/routers/internal_router.py but that nothing was calling).

This replaces the one-off, direct-to-SQLite backend/load_ml_events.py
approach with the real integration path: the pipeline calls the API, the
API validates/writes to whatever database it's configured for (SQLite today,
Postgres tomorrow), exactly as the backend was designed to be used.

Configuration (environment variables, all optional):
    BACKEND_URL         Base URL of the backend API. Default: http://127.0.0.1:8000
    INGESTION_API_KEY   Must match the backend's INGESTION_API_KEY. If unset,
                         uses the same placeholder default the backend falls
                         back to ("CHANGE_ME_INGESTION_KEY") - fine for local
                         testing only if you never set a real one on either side.

Usage:
    python push_events_to_backend.py

Exit codes:
    0  = all batches pushed successfully (or nothing to push)
    1  = source file missing / unreadable
    2  = one or more batches failed to push (network error or backend rejected them)
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, "..", "outputs")

CANDIDATE_FILES = [
    "evidence_scored_events.json",
    "verified_weather_events_v2.json",
    "weather_events.json",
]

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
INGESTION_API_KEY = os.environ.get("INGESTION_API_KEY", "CHANGE_ME_INGESTION_KEY")

STATUS_MAP = {
    "Supported": "Verified",
    "Contradicted": "Rejected",
    "Needs Review": "Pending",
}

BATCH_SIZE = 200
MAX_RAW_EVENTS = 500  # cap when falling back to the raw per-timestamp file


def find_source_file():
    for name in CANDIDATE_FILES:
        path = os.path.join(OUTPUTS_DIR, name)
        if os.path.exists(path):
            return name, path
    return None, None


def parse_timestamp(value: str) -> str:
    """Return an ISO 8601 string the backend's Pydantic datetime field accepts."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).isoformat()
        except ValueError:
            continue
    return datetime.fromisoformat(value).isoformat()


def to_event_payload(record: dict) -> Optional[dict]:
    location = record.get("location", {})
    city = location.get("city")
    state = location.get("state")
    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if not (city and state and latitude is not None and longitude is not None):
        return None

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

    verification_status = STATUS_MAP.get(record.get("verification_status"), "Pending")

    raw_timestamp = record.get("start_time") or record.get("timestamp")
    if not raw_timestamp:
        return None
    try:
        timestamp = parse_timestamp(raw_timestamp)
    except ValueError:
        return None

    return {
        "event_type": event_type,
        "city": city,
        "state": state,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "severity": severity,
        "confidence_score": confidence_score,
        "verification_status": verification_status,
        "timestamp": timestamp,
    }


def load_events():
    filename, path = find_source_file()
    if not path:
        print(
            "No data-science output found in "
            f"{os.path.normpath(OUTPUTS_DIR)}. Run the pipeline stages first."
        )
        return None

    print(f"Reading events from {filename} ...")
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    if filename == "weather_events.json" and len(records) > MAX_RAW_EVENTS:
        print(
            f"{filename} has {len(records)} raw rows; keeping only non-'Normal' "
            f"events, capped at {MAX_RAW_EVENTS}."
        )

    events = []
    for record in records:
        payload = to_event_payload(record)
        if payload is not None:
            events.append(payload)
        if filename == "weather_events.json" and len(events) >= MAX_RAW_EVENTS:
            break

    return events


def push_events(events):
    if not events:
        print("Nothing to push (no valid, non-'Normal' events found).")
        return True

    url = f"{BACKEND_URL}/internal/events/bulk"
    headers = {"X-API-Key": INGESTION_API_KEY, "Content-Type": "application/json"}

    all_ok = True
    for i in range(0, len(events), BATCH_SIZE):
        batch = events[i : i + BATCH_SIZE]
        try:
            resp = requests.post(url, json=batch, headers=headers, timeout=30)
        except requests.exceptions.RequestException as exc:
            print(f"Batch {i // BATCH_SIZE + 1}: request failed — {exc}")
            all_ok = False
            continue

        if resp.status_code == 201:
            print(f"Batch {i // BATCH_SIZE + 1}: pushed {len(batch)} events (201).")
        elif resp.status_code == 401:
            print(
                f"Batch {i // BATCH_SIZE + 1}: 401 Unauthorized — "
                "INGESTION_API_KEY here doesn't match the backend's. "
                "Set the same value in both places."
            )
            all_ok = False
        else:
            print(
                f"Batch {i // BATCH_SIZE + 1}: backend returned "
                f"{resp.status_code}: {resp.text[:300]}"
            )
            all_ok = False

    return all_ok


def main():
    events = load_events()
    if events is None:
        sys.exit(1)

    ok = push_events(events)
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
