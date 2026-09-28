# Data Cleaning & Standardization

SIH 2026 – National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer — Step 3.

## Input
The latest raw JSON file from ingestion, matching:
```
../ingestion/data/raw/openmeteo_raw_*.json
```
The script automatically picks the most recently modified file — no path needs to be passed manually.

## Cleaning operations
- Extracts the `current` block (+ `latitude`, `longitude`, `timezone`) into a single-row Pandas DataFrame.
- Renames raw Open-Meteo fields to standardized columns:

| Raw field | Standardized column |
|---|---|
| `time` | `timestamp` |
| `temperature_2m` | `temperature_c` |
| `relative_humidity_2m` | `relative_humidity_pct` |
| `precipitation` | `precipitation_mm` |
| `wind_speed_10m` | `wind_speed_kmh` |
| `weather_code` | `weather_code` |
| `latitude` | `latitude` |
| `longitude` | `longitude` |
| `timezone` | `timezone` |

- Converts `timestamp` to a real `datetime` (invalid/missing → `NaT`).
- Converts all numeric columns (`temperature_c`, `relative_humidity_pct`, `precipitation_mm`, `wind_speed_kmh`, `weather_code`, `latitude`, `longitude`) with `pd.to_numeric(..., errors="coerce")` (invalid/missing → `NaN`).
- **Missing values are never invented or filled in.** If a field is absent from the raw response, it stays `NaN`/`NaT`/`None` in the output, and is called out by name in the printed validation summary.

## Validation
Checks performed with Pandas/NumPy on the cleaned DataFrame:
- `temperature_c` is numeric.
- `relative_humidity_pct` is between 0 and 100.
- `precipitation_mm` is not negative.
- `wind_speed_kmh` is not negative.
- `latitude` is between -90 and 90.
- `longitude` is between -180 and 180.
- Missing values per column are reported (informational — does not fail validation, since we don't fabricate data).

Validation is marked **PASSED** only if no out-of-range values were found. Missing-value notes are shown separately.

## Output
A cleaned CSV file:
```
data-engineering/cleaning/data/processed/weather_cleaned_<UTC timestamp>.csv
```
Columns: `timestamp, latitude, longitude, timezone, temperature_c, relative_humidity_pct, precipitation_mm, wind_speed_kmh, weather_code`

## How to run
```bash
cd data-engineering/cleaning
pip install -r requirements.txt
python clean_weather.py
```

Prerequisite: at least one raw file must already exist in `../ingestion/data/raw/` (run `ingestion/fetch_openmeteo.py` first).

## Status
🚧 Cleaning stage (single latest file → single-row CSV) done. Database (PostgreSQL) and PySpark stages not started yet.
