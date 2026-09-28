"""
Member 3 DS engine.
Hybrid approach:
- Isolation Forest for anomaly detection
- Explainable event rules for prototype event categories
- Risk score for decision support

This is NOT an official IMD forecast model.
"""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "clean_weather.csv"
MODEL_DIR = ROOT / "models"
OUT_DIR = ROOT / "outputs"
MODEL_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

FEATURES = [
    "temperature_c","humidity_pct","rainfall_mm",
    "wind_speed_kmh","pressure_hpa",
    "rain_6h_mm","rain_24h_mm"
]

df = pd.read_csv(DATA)
X = df[FEATURES].fillna(df[FEATURES].median())

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=250,
    contamination=0.08,
    random_state=42
)
model.fit(X_scaled)

joblib.dump(model, MODEL_DIR / "isolation_forest.joblib")
joblib.dump(scaler, MODEL_DIR / "feature_scaler.joblib")

raw = model.decision_function(X_scaled)
# Higher = more abnormal, scaled to 0-100.
p05, p95 = np.percentile(raw, [5,95])
anomaly_score = 100 * (p95 - raw) / max(p95-p05, 1e-9)
df["anomaly_score"] = np.clip(anomaly_score, 0, 100)

def detect_event(r):
    # Prototype event layer; thresholds are explicitly labelled as
    # prototype decision rules and should be validated with official labels.
    if r.rain_24h_mm >= 100 or r.rain_6h_mm >= 50:
        return "Heavy Rainfall"
    if r.temperature_c >= 43:
        return "Heatwave"
    if r.wind_speed_kmh >= 70 or r.wind_gust_proxy >= 85:
        return "Strong Winds"
    if r.wind_speed_kmh >= 45 and r.humidity_pct >= 70:
        return "Thunderstorm"
    if r.humidity_pct >= 90 and r.wind_speed_kmh <= 8:
        return "Fog"
    return "Normal"

def risk_score(r):
    rain = min(r.rain_24h_mm / 150 * 100, 100)
    wind = min(r.wind_speed_kmh / 100 * 100, 100)
    heat = min(max((r.temperature_c - 35) / 12 * 100, 0), 100)
    anomaly = r.anomaly_score
    return float(np.clip(
        0.35*rain + 0.20*wind + 0.15*heat + 0.30*anomaly, 0, 100
    ))

def severity(score):
    if score >= 80: return "Critical"
    if score >= 60: return "High"
    if score >= 35: return "Medium"
    return "Low"

events = []
for _, r in df.iterrows():
    event = detect_event(r)
    score = risk_score(r)

    reasons = []
    if r.rain_24h_mm >= 50: reasons.append("elevated 24-hour rainfall")
    if r.rain_6h_mm >= 30: reasons.append("elevated 6-hour rainfall")
    if r.wind_speed_kmh >= 45: reasons.append("strong wind")
    if r.temperature_c >= 40: reasons.append("high temperature")
    if r.humidity_pct >= 90: reasons.append("very high humidity")
    if r.anomaly_score >= 60: reasons.append("anomalous weather pattern")
    if not reasons: reasons.append("no major abnormal indicator")

    events.append({
        "timestamp": str(r.timestamp),
        "location": {
            "city": r.city,
            "state": r.state,
            "latitude": float(r.latitude),
            "longitude": float(r.longitude)
        },
        "event_type": event,
        "severity": severity(score),
        "risk_score": round(score,2),
        "confidence_score": round(float(np.clip(100 - abs(50-r.anomaly_score)*0.55, 50, 95)),2),
        "anomaly_score": round(float(r.anomaly_score),2),
        "weather": {
            "temperature_c": round(float(r.temperature_c),2),
            "humidity_pct": round(float(r.humidity_pct),2),
            "rainfall_mm": round(float(r.rainfall_mm),2),
            "wind_speed_kmh": round(float(r.wind_speed_kmh),2),
            "pressure_hpa": round(float(r.pressure_hpa),2),
            "rain_6h_mm": round(float(r.rain_6h_mm),2),
            "rain_24h_mm": round(float(r.rain_24h_mm),2)
        },
        "source": {
            "name": "Open-Meteo",
            "dataset": "ERA5 reanalysis",
            "note": "Historical model/reanalysis data; not direct IMD station observation."
        },
        "reasons": reasons
    })

out = OUT_DIR / "weather_events.json"
out.write_text(json.dumps(events, indent=2), encoding="utf-8")

# Also create a compact CSV for quick backend testing.
pd.DataFrame([{
    "timestamp": e["timestamp"],
    "city": e["location"]["city"],
    "state": e["location"]["state"],
    "event_type": e["event_type"],
    "severity": e["severity"],
    "risk_score": e["risk_score"],
    "confidence_score": e["confidence_score"],
    "anomaly_score": e["anomaly_score"],
    "source": e["source"]["name"],
    "dataset": e["source"]["dataset"]
} for e in events]).to_csv(OUT_DIR/"weather_events.csv", index=False)

print(f"Events generated: {len(events):,}")
print(f"JSON: {out}")
print(f"CSV: {OUT_DIR/'weather_events.csv'}")
print("\nEvent distribution:")
print(pd.Series([e["event_type"] for e in events]).value_counts())
