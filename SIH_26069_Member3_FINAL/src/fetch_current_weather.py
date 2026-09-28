"""
Optional: fetch current/live weather values for the dashboard.
This is separate from the historical ML baseline.
"""
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CITIES = pd.read_csv(ROOT / "data" / "cities.csv")
OUT = ROOT / "data" / "raw" / "current_weather.csv"

URL = "https://api.open-meteo.com/v1/forecast"

rows = []
for _, c in CITIES.iterrows():
    params = {
        "latitude": c["latitude"],
        "longitude": c["longitude"],
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl",
        "timezone": "Asia/Kolkata"
    }
    r = requests.get(URL, params=params, timeout=30)
    r.raise_for_status()
    cur = r.json()["current"]
    rows.append({
        "timestamp": cur["time"],
        "city": c["city"],
        "state": c["state"],
        "latitude": c["latitude"],
        "longitude": c["longitude"],
        "temperature_c": cur["temperature_2m"],
        "humidity_pct": cur["relative_humidity_2m"],
        "rainfall_mm": cur["precipitation"],
        "wind_speed_kmh": cur["wind_speed_10m"],
        "pressure_hpa": cur["pressure_msl"],
        "source": "Open-Meteo",
        "source_dataset": "Current forecast/model data"
    })

pd.DataFrame(rows).to_csv(OUT, index=False)
print(f"Saved current weather to {OUT}")
