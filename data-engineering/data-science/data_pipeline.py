from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "open_meteo_era5.csv"
OUT = ROOT / "data" / "processed" / "clean_weather.csv"

REQUIRED = [
    "timestamp","city","state","latitude","longitude",
    "temperature_c","humidity_pct","rainfall_mm",
    "wind_speed_kmh","pressure_hpa"
]

df = pd.read_csv(RAW)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

for c in REQUIRED[5:]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

before = len(df)
df = df.drop_duplicates()
df = df.dropna(subset=REQUIRED)

# Basic physical/data-quality checks, not weather forecasts.
df = df[df["humidity_pct"].between(0,100)]
df = df[df["temperature_c"].between(-30,60)]
df = df[df["rainfall_mm"].between(0,500)]
df = df[df["wind_speed_kmh"].between(0,250)]
df = df[df["pressure_hpa"].between(850,1100)]

df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.date

# Rolling features by city for anomaly/risk context.
df = df.sort_values(["city","timestamp"])
df["rain_6h_mm"] = (
    df.groupby("city")["rainfall_mm"]
      .transform(lambda s: s.rolling(6, min_periods=1).sum())
)
df["rain_24h_mm"] = (
    df.groupby("city")["rainfall_mm"]
      .transform(lambda s: s.rolling(24, min_periods=1).sum())
)
df["temp_24h_mean"] = (
    df.groupby("city")["temperature_c"]
      .transform(lambda s: s.rolling(24, min_periods=1).mean())
)
df["wind_gust_proxy"] = (
    df.groupby("city")["wind_speed_kmh"]
      .transform(lambda s: s.rolling(3, min_periods=1).max())
)

df.to_csv(OUT, index=False)

print(f"Input rows: {before:,}")
print(f"Clean rows: {len(df):,}")
print(f"Removed: {before-len(df):,}")
print(f"Saved: {OUT}")
