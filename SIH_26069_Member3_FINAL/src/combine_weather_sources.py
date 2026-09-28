import pandas as pd
import os

# -----------------------------
# Project paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPEN_METEO_FILE = os.path.join(
    BASE_DIR, "data", "raw", "open_meteo_era5.csv"
)

NASA_FILE = os.path.join(
    BASE_DIR, "data", "raw", "nasa_power", "nasa_power_weather.csv"
)

CITIES_FILE = os.path.join(
    BASE_DIR, "data", "cities.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR, "data", "processed"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Read data
# -----------------------------
print("Reading Open-Meteo data...")
open_meteo = pd.read_csv(OPEN_METEO_FILE)

print("Reading NASA POWER data...")
nasa = pd.read_csv(NASA_FILE)

print("Reading city information...")
cities = pd.read_csv(CITIES_FILE)

# -----------------------------
# State mapping for NASA
# -----------------------------
city_state = dict(zip(cities["city"], cities["state"]))

# ============================================================
# OPEN-METEO
# ============================================================

open_common = pd.DataFrame()

open_common["source"] = ["Open-Meteo"] * len(open_meteo)
open_common["source_type"] = ["reanalysis_dataset"] * len(open_meteo)

open_common["timestamp"] = pd.to_datetime(
    open_meteo["timestamp"]
)

open_common["city"] = open_meteo["city"]
open_common["state"] = open_meteo["state"]

open_common["latitude"] = open_meteo["latitude"]
open_common["longitude"] = open_meteo["longitude"]

open_common["temperature_c"] = open_meteo["temperature_c"]
open_common["humidity_pct"] = open_meteo["humidity_pct"]

open_common["rainfall_mm"] = open_meteo["rainfall_mm"]

open_common["wind_speed_kmh"] = open_meteo["wind_speed_kmh"]

open_common["pressure_hpa"] = open_meteo["pressure_hpa"]

# ============================================================
# NASA POWER
# ============================================================

nasa_common = pd.DataFrame()

nasa_common["source"] = ["NASA POWER"] * len(nasa)
nasa_common["source_type"] = ["public_dataset"] * len(nasa)

# NASA timestamp format: YYYYMMDDHH
nasa_common["timestamp"] = pd.to_datetime(
    nasa["timestamp"].astype(str),
    format="%Y%m%d%H"
)

nasa_common["city"] = nasa["city"]

nasa_common["state"] = nasa["city"].map(city_state)

nasa_common["latitude"] = nasa["latitude"]
nasa_common["longitude"] = nasa["longitude"]

nasa_common["temperature_c"] = nasa["temperature"]

nasa_common["humidity_pct"] = nasa["humidity"]

nasa_common["rainfall_mm"] = nasa["rainfall"]

# NASA POWER WS10M is in m/s.
# Convert m/s to km/h.
nasa_common["wind_speed_kmh"] = nasa["wind_speed"] * 3.6

# NASA POWER PS is in kPa.
# Convert kPa to hPa.
nasa_common["pressure_hpa"] = nasa["pressure"] * 10

# ============================================================
# COMBINE
# ============================================================

combined = pd.concat(
    [open_common, nasa_common],
    ignore_index=True
)

# Sort by city, timestamp and source
combined = combined.sort_values(
    by=["city", "timestamp", "source"]
)

# Remove exact duplicate rows
combined = combined.drop_duplicates()

# ============================================================
# SAVE
# ============================================================

output_file = os.path.join(
    OUTPUT_DIR,
    "multi_source_weather.csv"
)

combined.to_csv(
    output_file,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print("\n======================================")
print("MULTI-SOURCE DATASET CREATED")
print("======================================")

print(f"Open-Meteo records : {len(open_common)}")
print(f"NASA POWER records : {len(nasa_common)}")
print(f"Combined records   : {len(combined)}")

print("\nRecords by source:")
print(combined["source"].value_counts())

print(f"\nSaved to:")
print(output_file)

print("======================================")