# Data Engineer — Handoff Document

SIH 2026 – National Weather Big Data Analytics Platform
Problem Statement: PS 26069
Author: Role 2 — Data Engineer

This document explains the entire Data Engineer module so any teammate can understand, run, and build on top of it without reading every line of code.

---

## 1. Purpose of the Data Engineer module

This module is responsible for getting weather data into the system, making it trustworthy, and making it available to every other role in a form they can actually use. Concretely, it:

- Fetches live weather readings from a public weather API.
- Cleans and validates those readings so bad data doesn't spread downstream.
- Stores clean readings in PostgreSQL for reliable, queryable storage.
- Publishes readings to Kafka so other components can consume them in near real time.
- Runs the readings through PySpark to demonstrate big-data-style batch processing, producing derived fields and aggregated statistics as Parquet files.

Everything else in the project (backend APIs, ML models, NLP, dashboards) is meant to be built **on top of** the outputs described here, not by re-implementing ingestion or cleaning.

---

## 2. Complete data pipeline architecture

```
Open-Meteo API
      │  (Python + Requests)
      ▼
Raw JSON file  ──────────────────────────────┐
(ingestion/data/raw/)                        │
      │  (Pandas + NumPy)                    │  (confluent-kafka)
      ▼                                      ▼
Cleaned CSV file                     Kafka topic: weather-data
(cleaning/data/processed/)           (broker: localhost:9092)
      │
      │  (psycopg2, parameterized SQL)
      ▼
PostgreSQL: weather_platform.weather_data

Cleaned CSV file
      │  (PySpark, local[*])
      ▼
records.parquet + summary.parquet
(spark/data/processed/run_<timestamp>/)
```

Two things consume the same cleaned CSV independently: the PostgreSQL loader and the PySpark job. The Kafka producer is a separate branch that reuses the same Open-Meteo fetch logic but publishes straight to Kafka instead of writing to disk.

---

## 3. Data source and why Open-Meteo is currently used

The long-term goal is to use IMD (India Meteorological Department) as the authoritative data source. IMD API access currently requires permissions/approval that the team does not yet have.

**Open-Meteo** (https://open-meteo.com/) is used as a **temporary development substitute** because it:
- Requires no API key or signup.
- Returns current-weather fields comparable to what IMD is expected to provide (temperature, humidity, precipitation, wind speed, weather code).
- Lets every other role keep building and testing against real, live data while IMD access is pending.

When IMD access is granted, only `ingestion/fetch_openmeteo.py` needs to be replaced/extended — the cleaning, database, Kafka, and Spark stages were built against a generic set of standardized column names, not Open-Meteo-specific ones.

---

## 4. How weather data is fetched

File: `ingestion/fetch_openmeteo.py`

- Sends a GET request (via `requests`) to `https://api.open-meteo.com/v1/forecast`.
- Location is currently hardcoded to Pune: `latitude=18.523726`, `longitude=73.86876`, `timezone=Asia/Kolkata`.
- Requests these current fields: `temperature_2m`, `relative_humidity_2m`, `precipitation`, `wind_speed_10m`, `weather_code`.
- Checks for HTTP/network errors and JSON parse errors, and exits with a clear message if either fails.
- Saves the full raw API response as a timestamped JSON file, so nothing is lost even before cleaning.

`ingestion/kafka_producer.py` reuses the same fetch function (it imports it directly from `fetch_openmeteo.py`) rather than duplicating the API call.

---

## 5. Raw data format

Each run of `fetch_openmeteo.py` writes one file to `ingestion/data/raw/`, named like:
```
openmeteo_raw_20260906T135712Z.json
```
It is the **unmodified** Open-Meteo API response, e.g.:
```json
{
  "latitude": 18.5,
  "longitude": 73.875,
  "timezone": "Asia/Kolkata",
  "current": {
    "time": "2026-09-06T13:45",
    "temperature_2m": 27.3,
    "relative_humidity_2m": 68,
    "precipitation": 0.0,
    "wind_speed_10m": 9.4,
    "weather_code": 3
  }
}
```
Keeping the raw response untouched means we can always re-derive cleaned data differently later without re-fetching.

---

## 6. Cleaning and validation process

File: `cleaning/clean_weather.py`

- Automatically finds the **latest** raw JSON file in `ingestion/data/raw/`.
- Extracts the `current` block into a single-row Pandas DataFrame and renames fields to standardized names:

| Raw field | Standardized column |
|---|---|
| `time` | `timestamp` |
| `temperature_2m` | `temperature_c` |
| `relative_humidity_2m` | `relative_humidity_pct` |
| `precipitation` | `precipitation_mm` |
| `wind_speed_10m` | `wind_speed_kmh` |
| `weather_code` | `weather_code` |

- Converts `timestamp` to a real datetime and all measurement fields to numeric types (`pd.to_numeric(..., errors="coerce")`).
- **Never invents missing values.** If a field is absent, it stays `NaN`/`NaT` and is reported explicitly, not silently filled in.
- Validates: temperature is numeric; humidity is 0–100; precipitation and wind speed are non-negative; latitude is -90 to 90; longitude is -180 to 180.
- Saves the cleaned, single-row dataset as a timestamped CSV in `cleaning/data/processed/`, e.g. `weather_cleaned_20260906T142457Z.csv`, with columns:
  `timestamp, latitude, longitude, timezone, temperature_c, relative_humidity_pct, precipitation_mm, wind_speed_kmh, weather_code`

---

## 7. PostgreSQL database and weather_data table

File: `database/load_to_postgres.py`

- Database: `weather_platform`
- Table: `weather_data` (already created; the loader never creates or alters it):
  ```sql
  CREATE TABLE weather_data (
      id SERIAL PRIMARY KEY,
      timestamp TIMESTAMP NOT NULL,
      latitude DOUBLE PRECISION,
      longitude DOUBLE PRECISION,
      timezone VARCHAR(100),
      temperature_c DOUBLE PRECISION,
      relative_humidity_pct DOUBLE PRECISION,
      precipitation_mm DOUBLE PRECISION,
      wind_speed_kmh DOUBLE PRECISION,
      weather_code INTEGER
  );
  ```
- The loader finds the **latest** cleaned CSV, reads it with Pandas, and inserts each row using a parameterized SQL `INSERT` (never string-built SQL).
- Missing/NaN values are inserted as SQL `NULL`, never invented.
- Connects using `psycopg2`, with credentials read only from environment variables (see Section 13) — never hardcoded.
- On any insertion error, the transaction is rolled back and the connection is still closed safely.

This table is the durable, queryable historical record of every weather reading that's been loaded.

---

## 8. Kafka topic and message flow

File: `ingestion/kafka_producer.py`

- Broker: `localhost:9092` (Kafka 4.3.1, running in KRaft mode)
- Topic: `weather-data`
- Library: `confluent-kafka` (a librdkafka-based client), chosen for active maintenance and compatibility with modern Kafka brokers.
- Flow: the producer calls the same `fetch_current_weather` / `extract_current_weather` functions used by `fetch_openmeteo.py`, adds a `produced_at` timestamp, and publishes the result as a JSON message.
- Message key: `"<latitude>_<longitude>"` (e.g. `"18.523726_73.86876"`), so all readings for the same location land on the same partition and stay in order.
- Example message value:
  ```json
  {
    "time": "2026-09-06T13:45",
    "temperature_2m": 27.3,
    "relative_humidity_2m": 68,
    "precipitation": 0.0,
    "wind_speed_10m": 9.4,
    "weather_code": 3,
    "latitude": 18.523726,
    "longitude": 73.86876,
    "timezone": "Asia/Kolkata",
    "produced_at": "2026-09-06T18:48:36Z"
  }
  ```
- Delivery success/failure is logged per message via a delivery callback; connection and produce errors are caught and logged rather than crashing silently.
- **No consumer has been implemented yet** — any teammate consuming this topic needs to write their own consumer for now.

---

## 9. PySpark processing and derived fields

File: `spark/process_weather.py`

- Reads the **latest** cleaned CSV from `cleaning/data/processed/` using Spark, with an **explicitly defined schema** (no schema inference).
- Re-applies the same validation rules as the cleaning stage (valid lat/lon range, humidity 0–100, non-negative precipitation/wind, no null timestamp/location/temperature) — records failing these are filtered out, not repaired.
- Adds derived fields:
  - `location_id` — `"<latitude>_<longitude>"`
  - `observation_date` — date extracted from the timestamp
  - `temperature_f` — Fahrenheit conversion of `temperature_c`
  - `wind_speed_ms` — `wind_speed_kmh` converted to metres/second
- Aggregates by location, computing: record count, average/max/min temperature, average humidity, total precipitation, average wind speed.
- Runs locally (`local[*]` — no cluster needed).

---

## 10. Parquet outputs

Each run of `process_weather.py` creates a new timestamped folder:
```
data-engineering/spark/data/processed/run_<UTC timestamp>/
├── records.parquet   # validated + enriched per-record data
└── summary.parquet   # aggregated statistics per location
```
Both are single Parquet files (written via PyArrow — see Section 14), readable with `pandas.read_parquet(...)`, `pyarrow.parquet.read_table(...)`, or `spark.read.parquet(...)`.

`records.parquet` columns: all cleaned columns plus `location_id`, `observation_date`, `temperature_f`, `wind_speed_ms`.

`summary.parquet` columns: `location_id, latitude, longitude, timezone, record_count, avg_temperature_c, max_temperature_c, min_temperature_c, avg_humidity_pct, total_precipitation_mm, avg_wind_speed_kmh`.

---

## 11. How another teammate can run the pipeline

Each stage has its own `requirements.txt` and README with full detail. In short, run in this order:

```bash
# 1. Fetch raw weather data
cd data-engineering/ingestion
pip install -r requirements.txt
python fetch_openmeteo.py

# 2. Clean and validate it
cd ../cleaning
pip install -r requirements.txt
python clean_weather.py

# 3. Load cleaned data into PostgreSQL
cd ../database
pip install -r requirements.txt
cp .env.example .env   # then fill in your own local DB password
python load_to_postgres.py

# 4. (Optional, separate) Publish a live reading to Kafka
#    Requires a running Kafka broker at localhost:9092 with topic weather-data
cd ../ingestion
python kafka_producer.py

# 5. Run Spark processing on the cleaned data
cd ../spark
pip install -r requirements.txt
python process_weather.py
```

See each stage's own `README.md` for setup details, example output, and troubleshooting (in particular `spark/README.md` for the Windows/PyArrow note).

---

## 12. Which outputs each teammate should use

- **Backend Developer** — Query `weather_data` in PostgreSQL for the durable, queryable historical record; use `summary.parquet` for pre-aggregated stats to serve via API without recomputing them.
- **Data Scientist** — Use `records.parquet` (validated, enriched per-record data) as the primary input for modeling/analysis; `weather_data` in PostgreSQL is available for historical queries across many runs.
- **Frontend Developer** — Should not read raw files or Parquet directly; consume whatever the Backend Developer exposes via API (built on top of PostgreSQL / `summary.parquet`).
- **AI/NLP Engineer** — Use `weather_data` (PostgreSQL) or `records.parquet` as the underlying factual weather data to ground any generated text/insights; the Kafka topic `weather-data` is the place to consume live readings if/when real-time NLP features are built.

---

## 13. Configuration / environment variables

No passwords, keys, or secrets are stored in the repository. `database/.env` is git-ignored; only `database/.env.example` (a placeholder template) is committed.

| Variable | Used by | Notes |
|---|---|---|
| `DB_HOST` | `database/load_to_postgres.py` | e.g. `localhost` |
| `DB_PORT` | `database/load_to_postgres.py` | e.g. `5432` |
| `DB_NAME` | `database/load_to_postgres.py` | `weather_platform` |
| `DB_USER` | `database/load_to_postgres.py` | e.g. `postgres` |
| `DB_PASSWORD` | `database/load_to_postgres.py` | set locally only, never committed |

Kafka broker (`localhost:9092`) and topic (`weather-data`) are currently set as plain constants in `ingestion/kafka_producer.py` — no credentials are required since the local KRaft broker has no auth configured.

Open-Meteo requires no API key.

---

## 14. Current limitations

- **Open-Meteo instead of IMD**: the project uses Open-Meteo as a stand-in data source because direct IMD API access/permissions haven't been granted yet (see Section 3).
- **Kafka producer is a one-shot run, not a daemon**: `kafka_producer.py` fetches one current reading and publishes it, then exits. It is not a long-running/scheduled process yet — running it repeatedly (manually or via a scheduler) is currently the only way to get a stream of messages.
- **No Kafka consumer yet**: nothing currently reads from the `weather-data` topic.
- **PySpark on Windows uses PyArrow for the final write**: Spark's built-in Parquet writer depends on Hadoop's `LocalFileSystem`, which requires `winutils.exe` on Windows even for local file I/O. To avoid depending on a third-party `winutils.exe` binary, `process_weather.py` does all Spark processing normally, then writes the final `records.parquet`/`summary.parquet` using `pandas.to_parquet(engine="pyarrow")` instead of Spark's native writer. This works well at this project's current single-machine scale; on a real multi-node cluster (Linux), this isn't an issue and Spark's native writer could be used instead.
- **Single location only**: ingestion currently fetches one hardcoded location (Pune). Multi-location support would need parameterizing the fetch call.
- **No orchestration/scheduling**: each stage is run manually, in order, by a person. There is no scheduler or automatic pipeline trigger.

---

## 15. Future integration possibilities (not implemented)

These are directions the pipeline could grow in later — none of this exists yet:

- Direct IMD API integration once access/permissions are granted, replacing or supplementing Open-Meteo.
- A Kafka consumer that reads `weather-data` and writes to PostgreSQL and/or triggers Spark processing automatically, instead of the current manual, file-based hand-off between stages.
- Turning the Kafka producer into a long-running/scheduled process instead of a single fetch-and-publish run.
- Spark Structured Streaming reading directly from the `weather-data` Kafka topic, instead of today's batch read from cleaned CSV files.
- Multi-location ingestion (parameterizing latitude/longitude/timezone instead of the current hardcoded Pune location).
- Historical/time-series aggregation in Spark (e.g. daily/weekly trends) beyond the current single-run, per-location summary.

---

*This document reflects the pipeline as implemented at the time of writing. If any stage's code changes, please keep this document in sync.*

## 16. Historical Data Science Pipeline

The project also includes a historical weather analytics pipeline that feeds the Data Science module.

### Historical ingestion

File:

`ingestion/fetch_real_weather.py`

This script fetches historical weather data from the Open-Meteo Historical Weather API using ERA5 reanalysis data for 8 cities:

- Pune
- Mumbai
- Delhi
- Bengaluru
- Chennai
- Kolkata
- Jaipur
- Guwahati

The current dataset contains 5,952 hourly records.

Output:

`ingestion/data/raw/open_meteo_era5.csv`

This data is Open-Meteo/ERA5 historical reanalysis data and must not be described as direct IMD station observations.

### Historical cleaning

File:

`cleaning/historical/clean_historical_weather.py`

The Data Engineer cleaning stage:

- Converts timestamps to datetime.
- Converts weather measurements to numeric values.
- Removes duplicate records.
- Removes invalid timestamps.
- Validates humidity, rainfall, wind speed, latitude and longitude.
- Sorts records by city and timestamp.

Output:

`data/processed/historical_weather_cleaned.csv`

### Feature engineering

File:

`data-science/feature_engineering.py`

The Data Science feature engineering stage adds:

- Hour and day information.
- 6-hour rainfall totals.
- 24-hour rainfall totals.
- 24-hour temperature rolling mean.
- 3-hour wind gust proxy.

Output:

`data/processed/weather_features.csv`

### Weather event detection

File:

`data-science/model.py`

The Data Science model uses:

- StandardScaler for feature scaling.
- Isolation Forest for anomaly detection.
- Rule-based weather event detection.
- Risk scoring.
- Severity classification.
- Confidence scoring.

Detected event categories include:

- Heavy Rainfall
- Heatwave
- Strong Winds
- Thunderstorm
- Fog
- Normal

The trained models are stored in:

`models/feature_scaler.joblib`

`models/isolation_forest.joblib`

Generated event outputs:

`outputs/weather_events.json`

`outputs/weather_events.csv`

The generated events contain location, weather measurements, event type, severity, risk score, confidence score, anomaly score, data source information, and reasons.

### End-to-end execution

File:

`data-science/run_all.py`

The complete historical pipeline can be executed from the repository root using:

`python data-engineering/data-science/run_all.py`

The execution order is:

1. Historical weather ingestion.
2. Historical data cleaning.
3. Feature engineering.
4. Weather event detection.

The current tested pipeline successfully processes 5,952 historical records and generates 5,952 weather event records.

### Data Science integration note

`data-science/data_pipeline.py` is retained as a reference/backup from the original Data Scientist module. It is not used by the final `run_all.py` execution pipeline because historical cleaning is now handled by the Data Engineer cleaning stage.