"""
Weather Data Cleaning & Standardization
SIH 2026 - National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer

Reads the latest raw Open-Meteo JSON file produced by
`ingestion/fetch_openmeteo.py`, extracts the current-weather block into
a standardized Pandas DataFrame, validates it, and writes a cleaned
CSV file.

This stage does NOT invent missing values. If a field is missing in
the raw response, it is kept as NaN (numeric) or None (text) in the
output, and validation reports how many rows/fields were affected.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "ingestion" / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).resolve().parent / "data" / "processed"

# Raw field name -> standardized column name
FIELD_MAP = {
    "time": "timestamp",
    "temperature_2m": "temperature_c",
    "relative_humidity_2m": "relative_humidity_pct",
    "precipitation": "precipitation_mm",
    "wind_speed_10m": "wind_speed_kmh",
    "weather_code": "weather_code",
}

NUMERIC_COLUMNS = [
    "temperature_c",
    "relative_humidity_pct",
    "precipitation_mm",
    "wind_speed_kmh",
    "weather_code",
    "latitude",
    "longitude",
]


def find_latest_raw_file() -> Path:
    """Return the most recently modified raw JSON file in ingestion/data/raw/."""
    if not RAW_DATA_DIR.exists():
        print(f"[ERROR] Raw data directory not found: {RAW_DATA_DIR}")
        sys.exit(1)

    json_files = sorted(RAW_DATA_DIR.glob("openmeteo_raw_*.json"))
    if not json_files:
        print(f"[ERROR] No raw Open-Meteo JSON files found in: {RAW_DATA_DIR}")
        print("Run ingestion/fetch_openmeteo.py first.")
        sys.exit(1)

    # Filenames are timestamp-sortable (YYYYMMDDTHHMMSSZ), but fall back to
    # file modification time in case of manual renames.
    latest = max(json_files, key=lambda p: p.stat().st_mtime)
    return latest


def load_raw_json(filepath: Path) -> dict:
    """Load and parse the raw JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[ERROR] Failed to read/parse raw file {filepath}: {exc}")
        sys.exit(1)


def extract_dataframe(payload: dict) -> pd.DataFrame:
    """
    Build a one-row standardized DataFrame from the raw Open-Meteo payload.

    Missing fields are NOT invented — they are recorded as NaN/None and
    surfaced explicitly in the printed validation summary.
    """
    current = payload.get("current", {})

    row = {}
    for raw_key, std_col in FIELD_MAP.items():
        row[std_col] = current.get(raw_key, np.nan)

    row["latitude"] = payload.get("latitude", np.nan)
    row["longitude"] = payload.get("longitude", np.nan)
    row["timezone"] = payload.get("timezone", None)

    df = pd.DataFrame([row])

    # Reorder columns for readability
    column_order = [
        "timestamp",
        "latitude",
        "longitude",
        "timezone",
        "temperature_c",
        "relative_humidity_pct",
        "precipitation_mm",
        "wind_speed_kmh",
        "weather_code",
    ]
    df = df[column_order]
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convert types and handle missing values explicitly (no invented data)."""
    df = df.copy()

    # Timestamp -> proper datetime. Invalid/missing -> NaT (explicit, not guessed).
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Numeric coercion. Any non-numeric or missing value becomes NaN explicitly.
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # timezone stays a plain string; empty string -> treated as missing
    df["timezone"] = df["timezone"].replace("", np.nan)

    return df


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Run basic data-quality checks. Returns (passed, list_of_issues).
    Rows with missing values are reported, not silently dropped or filled.
    """
    issues = []

    # Missing-value report (explicit, not filled)
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing:
            issues.append(f"{missing} missing value(s) in '{col}' (left as NaN/NaT)")

    # temperature must be numeric (already enforced by coercion; check dtype)
    if not pd.api.types.is_numeric_dtype(df["temperature_c"]):
        issues.append("temperature_c is not numeric")

    # humidity 0-100
    bad_humidity = df["relative_humidity_pct"].dropna()
    bad_humidity = bad_humidity[(bad_humidity < 0) | (bad_humidity > 100)]
    if not bad_humidity.empty:
        issues.append(f"{len(bad_humidity)} row(s) with relative_humidity_pct outside 0-100")

    # precipitation >= 0
    bad_precip = df["precipitation_mm"].dropna()
    bad_precip = bad_precip[bad_precip < 0]
    if not bad_precip.empty:
        issues.append(f"{len(bad_precip)} row(s) with negative precipitation_mm")

    # wind speed >= 0
    bad_wind = df["wind_speed_kmh"].dropna()
    bad_wind = bad_wind[bad_wind < 0]
    if not bad_wind.empty:
        issues.append(f"{len(bad_wind)} row(s) with negative wind_speed_kmh")

    # latitude -90 to 90
    bad_lat = df["latitude"].dropna()
    bad_lat = bad_lat[(bad_lat < -90) | (bad_lat > 90)]
    if not bad_lat.empty:
        issues.append(f"{len(bad_lat)} row(s) with latitude outside -90..90")

    # longitude -180 to 180
    bad_lon = df["longitude"].dropna()
    bad_lon = bad_lon[(bad_lon < -180) | (bad_lon > 180)]
    if not bad_lon.empty:
        issues.append(f"{len(bad_lon)} row(s) with longitude outside -180..180")

    # A validation "pass" here means no out-of-range values were found.
    # Missing-value notes are informational and do not fail validation on
    # their own, since we intentionally do not invent data to fill them.
    range_issues = [
        i for i in issues
        if "missing value" not in i
    ]
    passed = len(range_issues) == 0
    return passed, issues


def save_cleaned_csv(df: pd.DataFrame) -> Path:
    """Save the cleaned DataFrame as a timestamped CSV."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"weather_cleaned_{timestamp}.csv"
    filepath = PROCESSED_DATA_DIR / filename

    df.to_csv(filepath, index=False)
    return filepath


def main():
    latest_raw_file = find_latest_raw_file()
    print(f"Reading latest raw file: {latest_raw_file}")

    payload = load_raw_json(latest_raw_file)
    df = extract_dataframe(payload)
    df = clean_dataframe(df)
    passed, issues = validate_dataframe(df)
    output_path = save_cleaned_csv(df)

    print("\n[SUCCESS] Weather data cleaned and saved.")
    print("\nSummary:")
    print(f"  Input file:        {latest_raw_file}")
    print(f"  Records:            {len(df)}")
    print(f"  Columns:            {len(df.columns)}")
    print(f"  Validation result:  {'PASSED' if passed else 'FAILED'}")
    if issues:
        print("  Validation notes:")
        for issue in issues:
            print(f"    - {issue}")
    print(f"  Output CSV path:    {output_path}")


if __name__ == "__main__":
    main()
