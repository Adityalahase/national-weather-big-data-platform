"""
Internal ingestion endpoints — for the data-engineering/data-science pipeline
to push newly detected/processed weather events into this backend.

NOT part of the public API and NOT part of the admin panel. Protected by a
shared API key (see internal_auth.py), not a user JWT — there's no "user"
on the other end, just another service/script.

The pipeline should send data matching WeatherEventCreate exactly:
    event_type, city, state, latitude, longitude, severity,
    confidence_score, verification_status, timestamp
New events default to verification_status="Pending" if the pipeline doesn't
set one, so an admin has to review them before they're marked Verified.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from internal_auth import verify_ingestion_key

router = APIRouter(
    prefix="/internal",
    tags=["internal-ingestion"],
    dependencies=[Depends(verify_ingestion_key)],  # applies to every route below
)


@router.post("/events", response_model=schemas.WeatherEventOut, status_code=201)
def ingest_event(payload: schemas.WeatherEventCreate, db: Session = Depends(get_db)):
    """Insert a single new weather event produced by the data pipeline."""
    event = models.WeatherEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.post("/events/bulk", response_model=List[schemas.WeatherEventOut], status_code=201)
def ingest_events_bulk(payloads: List[schemas.WeatherEventCreate], db: Session = Depends(get_db)):
    """Insert many events at once — useful for batch/historical ingestion runs."""
    if not payloads:
        raise HTTPException(status_code=400, detail="Empty event list")

    events = [models.WeatherEvent(**p.model_dump()) for p in payloads]
    db.add_all(events)
    db.commit()
    for e in events:
        db.refresh(e)
    return events
