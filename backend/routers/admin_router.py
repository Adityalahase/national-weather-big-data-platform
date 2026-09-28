"""
Admin APIs. EVERY route here depends on require_admin, which itself depends on
get_current_user. That means, per route, FastAPI enforces:

    no token            -> 401 Unauthorized
    valid token, role != admin -> 403 Forbidden
    valid token, role == admin -> 200 OK, proceeds

This is the actual security boundary — the React /admin route guard is only a
UX nicety, never trust it alone (see spec Section 6/7).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import require_admin

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],  # applies to every route below
)


@router.get("/events", response_model=List[schemas.WeatherEventOut])
def list_all_events(db: Session = Depends(get_db)):
    """Admin sees everything, including Pending/Suspicious events."""
    return db.query(models.WeatherEvent).order_by(models.WeatherEvent.timestamp.desc()).all()


@router.get("/events/{event_id}", response_model=schemas.WeatherEventOut)
def get_event_detail(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.WeatherEvent).filter(models.WeatherEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/events/{event_id}/verify", response_model=schemas.WeatherEventOut)
def verify_event(event_id: int, payload: schemas.VerifyStatusUpdate, db: Session = Depends(get_db)):
    """Admin marks an event Verified / Suspicious / Rejected."""
    event = db.query(models.WeatherEvent).filter(models.WeatherEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    allowed = {"Pending", "Verified", "Suspicious", "Rejected"}
    if payload.verification_status not in allowed:
        raise HTTPException(status_code=400, detail=f"verification_status must be one of {allowed}")

    event.verification_status = payload.verification_status
    db.commit()
    db.refresh(event)
    return event


@router.patch("/events/{event_id}/status", response_model=schemas.WeatherEventOut)
def update_event_status(event_id: int, payload: schemas.VerifyStatusUpdate, db: Session = Depends(get_db)):
    """Alias of /verify — kept separate in case status and verification
    diverge in meaning later (per the suggested API structure in the spec)."""
    return verify_event(event_id, payload, db)


@router.get("/statistics", response_model=schemas.AdminStatistics)
def admin_statistics(db: Session = Depends(get_db)):
    events = db.query(models.WeatherEvent).all()
    by_severity: dict = {}
    for e in events:
        by_severity[e.severity] = by_severity.get(e.severity, 0) + 1

    def count(status_name: str) -> int:
        return sum(1 for e in events if e.verification_status == status_name)

    return schemas.AdminStatistics(
        total_events=len(events),
        pending=count("Pending"),
        verified=count("Verified"),
        suspicious=count("Suspicious"),
        rejected=count("Rejected"),
        by_severity=by_severity,
    )
