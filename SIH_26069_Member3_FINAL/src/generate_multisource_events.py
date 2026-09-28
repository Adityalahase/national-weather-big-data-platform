import pandas as pd
import numpy as np
import os
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR, "data", "processed", "multi_source_weather.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "outputs"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "weather_events_multisource.json"
)

print("Reading multi-source weather data...")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

# ==========================================
# FEATURE PREPARATION
# ==========================================

features = [
    "temperature_c",
    "humidity_pct",
    "rainfall_mm",
    "wind_speed_kmh",
    "pressure_hpa"
]

for col in features:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.dropna(
    subset=features
).copy()

# ==========================================
# ROLLING FEATURES
# ==========================================

df = df.sort_values(
    ["source", "city", "timestamp"]
)

df["rain_6h_mm"] = (
    df.groupby(["source", "city"])["rainfall_mm"]
    .transform(lambda x: x.rolling(6, min_periods=1).sum())
)

df["rain_24h_mm"] = (
    df.groupby(["source", "city"])["rainfall_mm"]
    .transform(lambda x: x.rolling(24, min_periods=1).sum())
)

# ==========================================
# ISOLATION FOREST
# ==========================================

print("Running anomaly detection...")

X = df[features].replace(
    [np.inf, -np.inf],
    np.nan
).fillna(0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=250,
    contamination=0.08,
    random_state=42
)

model.fit(X_scaled)

raw_anomaly = -model.decision_function(X_scaled)

# Convert anomaly score approximately to 0-100
anomaly_min = raw_anomaly.min()
anomaly_max = raw_anomaly.max()

if anomaly_max > anomaly_min:
    df["anomaly_score"] = (
        (raw_anomaly - anomaly_min)
        / (anomaly_max - anomaly_min)
        * 100
    )
else:
    df["anomaly_score"] = 0

# ==========================================
# EVENT DETECTION
# ==========================================

def detect_event(row):

    rain24 = row["rain_24h_mm"]
    rain6 = row["rain_6h_mm"]
    temp = row["temperature_c"]
    wind = row["wind_speed_kmh"]
    humidity = row["humidity_pct"]

    if rain24 >= 100 or rain6 >= 50:
        return "Heavy Rainfall"

    if temp >= 43:
        return "Heatwave"

    if wind >= 70:
        return "Strong Winds"

    if wind >= 45 and humidity >= 70:
        return "Thunderstorm"

    if humidity >= 90 and wind <= 8:
        return "Fog"

    if wind >= 40:
        return "Strong Winds"

    return "Normal"


df["event_type"] = df.apply(
    detect_event,
    axis=1
)

# ==========================================
# RISK SCORE
# ==========================================

def calculate_risk(row):

    rainfall_score = min(
        100,
        (row["rain_24h_mm"] / 100) * 100
    )

    wind_score = min(
        100,
        (row["wind_speed_kmh"] / 70) * 100
    )

    heat_score = min(
        100,
        (row["temperature_c"] / 43) * 100
    )

    anomaly_score = row["anomaly_score"]

    risk = (
        0.35 * rainfall_score +
        0.20 * wind_score +
        0.15 * heat_score +
        0.30 * anomaly_score
    )

    return round(
        min(100, risk),
        2
    )


df["risk_score"] = df.apply(
    calculate_risk,
    axis=1
)

# ==========================================
# SEVERITY
# ==========================================

def get_severity(score):

    if score >= 80:
        return "Critical"

    if score >= 60:
        return "High"

    if score >= 35:
        return "Medium"

    return "Low"


df["severity"] = df["risk_score"].apply(
    get_severity
)

# ==========================================
# CONFIDENCE
# ==========================================

df["confidence_score"] = (
    50 + (df["anomaly_score"] * 0.45)
).clip(50, 95).round(2)

# ==========================================
# REASONS
# ==========================================

def generate_reason(row):

    reasons = []

    if row["rain_24h_mm"] >= 100:
        reasons.append("very high 24h rainfall")

    elif row["rain_6h_mm"] >= 50:
        reasons.append("heavy recent rainfall")

    if row["temperature_c"] >= 43:
        reasons.append("extreme temperature")

    if row["wind_speed_kmh"] >= 70:
        reasons.append("very strong wind")

    if row["humidity_pct"] >= 90:
        reasons.append("very high humidity")

    if row["anomaly_score"] >= 70:
        reasons.append("unusual weather pattern detected")

    if not reasons:
        reasons.append("normal weather conditions")

    return reasons


df["reasons"] = df.apply(
    generate_reason,
    axis=1
)

# ==========================================
# CREATE JSON OUTPUT
# ==========================================

print("Creating multi-source event records...")

records = []

for _, row in df.iterrows():

    record = {
        "timestamp": row["timestamp"].strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "location": {
            "city": row["city"],
            "state": row["state"],
            "latitude": row["latitude"],
            "longitude": row["longitude"]
        },

        "event_type": row["event_type"],

        "severity": row["severity"],

        "risk_score": row["risk_score"],

        "confidence_score": row["confidence_score"],

        "anomaly_score": round(
            row["anomaly_score"],
            2
        ),

        "weather": {
            "temperature_c": row["temperature_c"],
            "humidity_pct": row["humidity_pct"],
            "rainfall_mm": row["rainfall_mm"],
            "wind_speed_kmh": row["wind_speed_kmh"],
            "pressure_hpa": row["pressure_hpa"],
            "rain_6h_mm": row["rain_6h_mm"],
            "rain_24h_mm": row["rain_24h_mm"]
        },

        "source": {
            "name": row["source"],
            "source_type": row["source_type"]
        },

        "reasons": row["reasons"]
    }

    records.append(record)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        records,
        f,
        indent=2,
        ensure_ascii=False
    )


# ==========================================
# SUMMARY
# ==========================================

print("\n======================================")
print("MULTI-SOURCE WEATHER EVENTS COMPLETE")
print("======================================")

print(f"Total records : {len(records)}")

print("\nSource distribution:")
print(
    df["source"].value_counts()
)

print("\nEvent distribution:")
print(
    df["event_type"].value_counts()
)

print("\nSeverity distribution:")
print(
    df["severity"].value_counts()
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("======================================")