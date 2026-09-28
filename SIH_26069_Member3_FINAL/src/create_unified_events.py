import pandas as pd
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEATHER_FILE = os.path.join(
    BASE_DIR, "outputs", "weather_events.json"
)

CITIZEN_FILE = os.path.join(
    BASE_DIR, "data", "processed",
    "verified_citizen_reports.csv"
)

SOCIAL_FILE = os.path.join(
    BASE_DIR, "data", "processed",
    "verified_social_media.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "data", "processed"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "unified_weather_intelligence.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# READ DATA
# ==========================================

print("Reading weather events...")

with open(WEATHER_FILE, "r", encoding="utf-8") as f:
    weather_data = json.load(f)

weather = pd.json_normalize(weather_data)

print("Reading citizen reports...")
citizen = pd.read_csv(CITIZEN_FILE)

print("Reading social media reports...")
social = pd.read_csv(SOCIAL_FILE)


# ==========================================
# WEATHER DATA
# ==========================================

weather_common = pd.DataFrame({
    "timestamp": weather["timestamp"],
    "city": weather["location.city"],
    "state": weather["location.state"],
    "latitude": weather["location.latitude"],
    "longitude": weather["location.longitude"],
    "event_type": weather["event_type"],
    "severity": weather["severity"],
    "risk_score": weather["risk_score"],
    "credibility_score": weather["confidence_score"],
    "verification_status": "AI Analysed",
    "source": weather["source.name"],
    "source_type": "weather_dataset",
    "reason": weather["reasons"].apply(
        lambda x: "; ".join(x) if isinstance(x, list) else str(x)
    )
})


# ==========================================
# CITIZEN DATA
# ==========================================

citizen_common = pd.DataFrame({
    "timestamp": citizen["timestamp"],
    "city": citizen["city"],
    "state": "",
    "latitude": citizen["latitude"],
    "longitude": citizen["longitude"],
    "event_type": citizen["event_type"],
    "severity": "Medium",
    "risk_score": 0,
    "credibility_score": citizen["credibility_score"],
    "verification_status": citizen["verification_status"],
    "source": "Citizen",
    "source_type": citizen["source_type"],
    "reason": citizen["verification_reason"]
})


# ==========================================
# SOCIAL MEDIA DATA
# ==========================================

social_common = pd.DataFrame({
    "timestamp": social["timestamp"],
    "city": social["city"],
    "state": "",
    "latitude": social["latitude"],
    "longitude": social["longitude"],
    "event_type": social["event_type"],
    "severity": "Medium",
    "risk_score": 0,
    "credibility_score": social["credibility_score"],
    "verification_status": social["verification_status"],
    "source": social["platform"],
    "source_type": social["source_type"],
    "reason": social["verification_reason"]
})


# ==========================================
# COMBINE ALL SOURCES
# ==========================================

unified = pd.concat(
    [
        weather_common,
        citizen_common,
        social_common
    ],
    ignore_index=True
)


# ==========================================
# CLEAN DATA
# ==========================================

unified["timestamp"] = pd.to_datetime(
    unified["timestamp"],
    errors="coerce"
)

unified["latitude"] = pd.to_numeric(
    unified["latitude"],
    errors="coerce"
)

unified["longitude"] = pd.to_numeric(
    unified["longitude"],
    errors="coerce"
)

unified["risk_score"] = pd.to_numeric(
    unified["risk_score"],
    errors="coerce"
).fillna(0)

unified["credibility_score"] = pd.to_numeric(
    unified["credibility_score"],
    errors="coerce"
).fillna(0)


unified = unified.dropna(
    subset=[
        "timestamp",
        "city",
        "event_type",
        "latitude",
        "longitude"
    ]
)


# ==========================================
# SORT
# ==========================================

unified = unified.sort_values(
    by="timestamp",
    ascending=False
)


# ==========================================
# SAVE
# ==========================================

unified.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# SUMMARY
# ==========================================

print("\n======================================")
print("UNIFIED WEATHER INTELLIGENCE COMPLETE")
print("======================================")

print(f"Total unified records : {len(unified)}")

print("\nSource distribution:")
print(
    unified["source"].value_counts()
)

print("\nEvent distribution:")
print(
    unified["event_type"].value_counts()
)

print("\nVerification distribution:")
print(
    unified["verification_status"].value_counts()
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("======================================")