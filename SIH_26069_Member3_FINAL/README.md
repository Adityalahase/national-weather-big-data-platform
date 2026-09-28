# SIH 26069 — FINAL Member 3 Data Science Package

This version intentionally contains NO synthetic weather dataset.

It fetches genuine historical weather data from Open-Meteo's Historical Weather
API using ERA5 reanalysis, then performs cleaning, feature engineering,
Isolation Forest anomaly detection, explainable event detection and risk scoring.

## Run

    pip install -r requirements.txt
    python src/run_all.py

Outputs:
- data/raw/open_meteo_era5.csv
- data/processed/clean_weather.csv
- models/isolation_forest.joblib
- models/feature_scaler.joblib
- outputs/weather_events.json
- outputs/weather_events.csv

## Architecture

Real Weather Data
→ Cleaning
→ Feature Engineering
→ Isolation Forest
→ Event Detection
→ Risk Score
→ Severity + Confidence
→ JSON
→ Backend
→ Dashboard

## Prototype event types

Heavy Rainfall
Heatwave
Strong Winds
Thunderstorm
Fog
Normal

## Backend handoff

Give the backend member:
1. outputs/weather_events.json
2. docs/backend_contract.md

## Honest presentation line

"We use real historical weather data from Open-Meteo's ERA5 reanalysis for the
prototype, preserve source provenance, and apply a hybrid anomaly-detection and
explainable event-intelligence layer. Official IMD observations can be integrated
as an additional authoritative source when available."

This is a decision-support prototype, not an official IMD forecast.
