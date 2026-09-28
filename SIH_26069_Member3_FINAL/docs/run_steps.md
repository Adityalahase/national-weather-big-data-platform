# EXACT STEPS FOR MEMBER 3

## Step 1 — Install
Open VS Code terminal or Google Colab.

Windows:
    py -m pip install -r requirements.txt

Colab:
    !pip install -r requirements.txt

## Step 2 — Fetch real data
    python src/fetch_real_weather.py

This downloads real historical weather data from Open-Meteo/ERA5.
Default dates: 2026-08-01 to 2026-08-31.

## Step 3 — Clean and engineer
    python src/data_pipeline.py

## Step 4 — Run Data Science
    python src/model.py

## Step 5 — Optional current weather
    python src/fetch_current_weather.py

This gives current weather separately for dashboard display.

## Step 6 — One-command version
    python src/run_all.py

## Final files for backend
Send:
    outputs/weather_events.json
    docs/backend_contract.md

## What to tell the backend member
"DS module real Open-Meteo/ERA5 weather data use karta hai. Output weather_events.json me event_type, severity, risk_score, confidence_score, anomaly_score, location, weather values, source aur reasons hain. Tum is JSON ko GET /api/weather-events se frontend ko serve karo."

## Important
Do not claim:
- "IMD data" unless the source field actually says IMD.
- "100% accurate".
- "official IMD prediction".
- "ML predicts future weather" unless a separately trained forecast model exists.

For the SIH prototype, describe it as:
"Hybrid weather-intelligence and decision-support engine using real historical weather data, anomaly detection and explainable event rules."

## If Open-Meteo is unavailable
Do not replace the data with random/synthetic values.
Use an exported genuine dataset and keep the original source metadata.
