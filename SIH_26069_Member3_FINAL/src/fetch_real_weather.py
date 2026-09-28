"""
Fetch REAL historical weather data from Open-Meteo Historical Weather API.
The data source is ERA5 reanalysis, not synthetic/generated data.

Default period: 2026-08-01 to 2026-08-31.
Change START_DATE / END_DATE if required.
"""
from pathlib import Path
from datetime import date, timedelta
import time
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CITIES = pd.read_csv(ROOT / "data" / "cities.csv")
OUT = ROOT / "data" / "raw" / "open_meteo_era5.csv"

START_DATE = "2026-08-01"
END_DATE = "2026-08-31"

URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY = ",".join([
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "pressure_msl"
])

all_rows = []

for _, c in CITIES.iterrows():
    params = {
        "latitude": c["latitude"],
        "longitude": c["longitude"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": HOURLY,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": "Asia/Kolkata",
        "models": "era5"
    }

    print(f"Fetching {c['city']}, {c['state']} ...")
    r = requests.get(URL, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()

    hourly = data["hourly"]
    n = len(hourly["time"])

    for i in range(n):
        all_rows.append({
            "timestamp": hourly["time"][i],
            "city": c["city"],
            "state": c["state"],
            "latitude": c["latitude"],
            "longitude": c["longitude"],
            "temperature_c": hourly["temperature_2m"][i],
            "humidity_pct": hourly["relative_humidity_2m"][i],
            "rainfall_mm": hourly["precipitation"][i],
            "wind_speed_kmh": hourly["wind_speed_10m"][i],
            "pressure_hpa": hourly["pressure_msl"][i],
            "source": "Open-Meteo",
            "source_dataset": "ERA5 reanalysis"
        })
    time.sleep(0.2)

df = pd.DataFrame(all_rows)
df.to_csv(OUT, index=False)

print(f"\nSaved {len(df):,} REAL weather records to:")
print(OUT)
print("\nSource: Open-Meteo Historical Weather API / ERA5 reanalysis")
print("Do not label this as direct IMD station observation.")
