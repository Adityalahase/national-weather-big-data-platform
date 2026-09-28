# Data Engineering

This directory contains the data engineering components for the National Weather Big Data Analytics Platform (SIH 2026, PS 26069).

## Owner
Role 2 – Data Engineer

## Responsibilities
- Weather data ingestion
- Data cleaning and validation
- Data transformation
- PostgreSQL storage
- PySpark processing for large datasets
- Data pipeline orchestration

## Structure

```
data-engineering/
├── ingestion/   # Scripts/connectors for pulling raw weather data
├── cleaning/    # Data cleaning and validation logic
├── database/    # PostgreSQL schema, models, and connection utilities
└── spark/       # PySpark jobs for large-scale processing
```

## Ingestion Stage (current)

`ingestion/fetch_openmeteo.py` fetches **current weather data** from the
[Open-Meteo API](https://open-meteo.com/) (temporary source — IMD API
access is pending permissions) for Pune, and saves the raw JSON response
to `ingestion/data/raw/` with a timestamped filename.

### Setup
```bash
cd data-engineering/ingestion
pip install -r requirements.txt
```

### Run
```bash
python fetch_openmeteo.py
```

## Status
🚧 Ingestion (Open-Meteo, current weather) done. Cleaning, database, spark stages not started yet.
