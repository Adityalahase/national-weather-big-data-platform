"""
Historical Weather Data Cleaning
SIH 2026 - National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer

Reads historical Open-Meteo/ERA5 CSV data produced by
ingestion/fetch_real_weather.py, cleans and standardizes it,
and writes the cleaned dataset for downstream Data Science.
"""

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "ingestion"
    / "data"
    / "raw"
    / "open_meteo_era5.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "historical_weather_cleaned.csv"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Convert numeric columns
    numeric_columns = [
        "latitude",
        "longitude",
        "temperature_c",
        "humidity_pct",
        "rainfall_mm",
        "wind_speed_kmh",
        "pressure_hpa",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove duplicate records
    df = df.drop_duplicates()

    # Remove rows with invalid timestamps
    df = df.dropna(subset=["timestamp"])

    # Validate physical ranges
    df = df[
        df["humidity_pct"].between(0, 100)
        & (df["rainfall_mm"] >= 0)
        & (df["wind_speed_kmh"] >= 0)
        & df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
    ]

    # Sort chronologically by city and timestamp
    df = df.sort_values(["city", "timestamp"]).reset_index(drop=True)

    return df


def main():
    print(f"Reading historical weather data from:\n{INPUT_FILE}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Input records: {len(df):,}")

    cleaned_df = clean_data(df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(OUTPUT_FILE, index=False)

    print("\n[SUCCESS] Historical weather data cleaned.")
    print(f"Output records: {len(cleaned_df):,}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()