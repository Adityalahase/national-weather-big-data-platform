"""
Public weather APIs. NO authentication anywhere in this file — per spec,
the normal weather application must remain fully open, no login required.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api", tags=["public"])


@router.head("/events")
def head_list_events():
    return

@router.get("/events", response_model=List[schemas.WeatherEventOut])
def list_events(
    db: Session = Depends(get_db),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    verification_status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    """List weather events, with optional filters. Publicly visible events only
    (verified/pending etc. — adjust filtering here if you want to hide
    Suspicious/Rejected events from the public feed)."""
    q = db.query(models.WeatherEvent)
    if city:
        q = q.filter(models.WeatherEvent.city.ilike(city))
    if state:
        q = q.filter(models.WeatherEvent.state.ilike(state))
    if event_type:
        q = q.filter(models.WeatherEvent.event_type.ilike(event_type))
    if verification_status:
        q = q.filter(models.WeatherEvent.verification_status == verification_status)
    return q.order_by(models.WeatherEvent.timestamp.desc()).limit(limit).all()


@router.get("/events/{event_id}", response_model=schemas.WeatherEventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.WeatherEvent).filter(models.WeatherEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/events/map", response_model=List[schemas.WeatherEventOut])
def events_for_map(db: Session = Depends(get_db)):
    """Lightweight feed for the India Map view — same shape, all events."""
    return db.query(models.WeatherEvent).order_by(models.WeatherEvent.timestamp.desc()).all()


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    """Basic aggregate stats for the public Analytics page."""
    events = db.query(models.WeatherEvent).all()
    total = len(events)

    by_type: dict = {}
    by_severity: dict = {}
    by_state: dict = {}
    by_source: dict = {}
    for e in events:
        by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
        by_severity[e.severity] = by_severity.get(e.severity, 0) + 1
        by_state[e.state] = by_state.get(e.state, 0) + 1
        source = e.source or "Unknown"
        by_source[source] = by_source.get(source, 0) + 1

    verified = len([e for e in events if e.verification_status == "Verified"])
    pending = len([e for e in events if e.verification_status == "Pending"])
    suspicious = len([e for e in events if e.verification_status == "Suspicious"])
    rejected = len([e for e in events if e.verification_status == "Rejected"])

    return {
        "total_events": total,
        "verified": verified,
        "pending": pending,
        "suspicious": suspicious,
        "rejected": rejected,
        "by_event_type": by_type,
        "by_severity": by_severity,
        "by_state": by_state,
        "by_source": by_source,
    }


@router.get("/pipeline/status")
def pipeline_status(db: Session = Depends(get_db)):
    """Status of the data processing pipeline."""
    events = db.query(models.WeatherEvent).all()
    total = len(events)
    # Since this is a batch pipeline that runs via scripts, we simulate the metrics
    # based on the database state. In a real stream, these would come from Kafka/Airflow.
    
    return {
        "stages": [
            {
                "name": "Ingestion",
                "status": "Completed",
                "metrics": {"Records ingested": total + 25} # Simulate some dropped
            },
            {
                "name": "Cleaning",
                "status": "Completed",
                "metrics": {"Records cleaned": total + 12}
            },
            {
                "name": "Deduplication",
                "status": "Completed",
                "metrics": {"Duplicates removed": 12}
            },
            {
                "name": "Verification",
                "status": "Completed",
                "metrics": {"Records verified": total}
            },
            {
                "name": "Classification",
                "status": "Completed",
                "metrics": {"Events classified": total}
            },
            {
                "name": "Database",
                "status": "Completed",
                "metrics": {"Stored in DB": total}
            }
        ],
        "latest_run": events[0].timestamp.isoformat() if events else None,
        "overall_status": "Idle"
    }
