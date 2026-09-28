import sys
from datetime import datetime, timezone, timedelta
sys.path.append('a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend')
from database import SessionLocal
import models

db = SessionLocal()

# Cleanup previous test data to be safe
db.query(models.WeatherEvent).filter(models.WeatherEvent.source == "TEST_IMD").delete()
db.commit()

# Create a baseline record in the DB
baseline_time = datetime(2026, 9, 28, 8, 15, 0, tzinfo=timezone.utc)
baseline_naive = baseline_time.replace(tzinfo=None)

baseline_event = models.WeatherEvent(
    event_type="Observation",
    city="Pune",
    state="Maharashtra",
    latitude=18.0,
    longitude=73.0,
    severity="Low",
    confidence_score=100,
    verification_status="Verified",
    timestamp=baseline_naive,
    source="TEST_IMD",
    station_id="STATION_A"
)
db.add(baseline_event)
db.commit()

test_cases = [
    # 1. Same station + same timestamp -> duplicate
    {
        "event_type": "Observation", "city": "Pune", "state": "Maharashtra", "latitude": 18.0, "longitude": 73.0,
        "severity": "Low", "confidence_score": 100, "source": "TEST_IMD", "station_id": "STATION_A",
        "time": baseline_time.isoformat()
    },
    # 2. Same station + different timestamp -> accepted
    {
        "event_type": "Observation", "city": "Pune", "state": "Maharashtra", "latitude": 18.0, "longitude": 73.0,
        "severity": "Low", "confidence_score": 100, "source": "TEST_IMD", "station_id": "STATION_A",
        "time": (baseline_time + timedelta(hours=1)).isoformat()
    },
    # 3. Different station + same timestamp + same city -> accepted
    {
        "event_type": "Observation", "city": "Pune", "state": "Maharashtra", "latitude": 18.1, "longitude": 73.1,
        "severity": "Low", "confidence_score": 100, "source": "TEST_IMD", "station_id": "STATION_B",
        "time": baseline_time.isoformat()
    },
    # 4. Different station + same timestamp + different city -> accepted
    {
        "event_type": "Observation", "city": "Mumbai", "state": "Maharashtra", "latitude": 19.0, "longitude": 72.8,
        "severity": "Low", "confidence_score": 100, "source": "TEST_IMD", "station_id": "STATION_C",
        "time": baseline_time.isoformat()
    }
]

results = []

for record in test_cases:
    ts = datetime.fromisoformat(record["time"].replace("Z", "+00:00"))
    ts_naive = ts.replace(tzinfo=None)
    
    exists = db.query(models.WeatherEvent).filter(
        models.WeatherEvent.event_type == record["event_type"],
        models.WeatherEvent.station_id == record["station_id"],
        models.WeatherEvent.source == "TEST_IMD",
        models.WeatherEvent.timestamp == ts_naive
    ).first()
    
    if exists:
        results.append("DUPLICATE")
    else:
        results.append("ACCEPTED")
        event = models.WeatherEvent(
            event_type=record["event_type"], city=record["city"], state=record["state"],
            latitude=record["latitude"], longitude=record["longitude"], severity=record["severity"],
            confidence_score=record["confidence_score"], verification_status="Verified",
            timestamp=ts_naive, source="TEST_IMD", station_id=record["station_id"]
        )
        db.add(event)
        db.commit()

print(results)
