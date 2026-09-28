"""
Weather Feature Engineering
SIH 2026 - National Weather Big Data Analytics Platform
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "historical_weather_cleaned.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "weather_features.csv"


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.sort_values(["city", "timestamp"]).reset_index(drop=True)

    # Time-based features
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.date

    # Rolling weather features by city
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

    return df


def main():
    print(f"Reading cleaned historical data from:\n{INPUT_FILE}")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    print(f"Input records: {len(df):,}")

    feature_df = create_features(df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    feature_df.to_csv(OUTPUT_FILE, index=False)

    print("\n[SUCCESS] Feature engineering completed.")
    print(f"Output records: {len(feature_df):,}")
    print(f"Output columns: {len(feature_df.columns)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()