"""
Weather Data Ingestion — Open-Meteo (temporary source)
SIH 2026 - National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer

Fetches current weather data from the Open-Meteo API for a given
location and saves the raw JSON response to disk with a timestamped
filename.

NOTE: IMD API access is currently blocked (no permission/API key yet).
Open-Meteo is used as a temporary, free, no-auth data source for
development purposes only.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
LATITUDE = 18.523726
LONGITUDE = 73.86876
TIMEZONE = "Asia/Kolkata"

CURRENT_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "weather_code",
]

API_URL = "https://api.open-meteo.com/v1/forecast"

# Save raw responses here (relative to this script's location)
RAW_DATA_DIR = Path(__file__).resolve().parent / "data" / "raw"


def fetch_current_weather(latitude: float, longitude: float, tz: str) -> dict:
    """Send a GET request to Open-Meteo and return the parsed JSON response."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": tz,
        "current": ",".join(CURRENT_FIELDS),
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[ERROR] Failed to fetch weather data: {exc}")
        sys.exit(1)

    try:
        return response.json()
    except ValueError as exc:
        print(f"[ERROR] Failed to parse JSON response: {exc}")
        sys.exit(1)


def extract_current_weather(payload: dict, latitude: float, longitude: float, tz: str) -> dict:
    """Pull out the 'current' block and attach location metadata."""
    current = payload.get("current", {})

    extracted = {
        "time": current.get("time"),
        "temperature_2m": current.get("temperature_2m"),
        "relative_humidity_2m": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "wind_speed_10m": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": tz,
    }
    return extracted


def save_raw_response(payload: dict) -> Path:
    """Save the raw API response as a timestamped JSON file."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"openmeteo_raw_{timestamp}.json"
    filepath = RAW_DATA_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return filepath


def main():
    print("Fetching current weather data from Open-Meteo...")
    print(f"Location: lat={LATITUDE}, lon={LONGITUDE}, timezone={TIMEZONE}")

    raw_payload = fetch_current_weather(LATITUDE, LONGITUDE, TIMEZONE)
    extracted = extract_current_weather(raw_payload, LATITUDE, LONGITUDE, TIMEZONE)
    saved_path = save_raw_response(raw_payload)

    print("\n[SUCCESS] Weather data fetched and saved.")
    print(f"Raw response saved to: {saved_path}")
    print("\nExtracted current weather:")
    for key, value in extracted.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
