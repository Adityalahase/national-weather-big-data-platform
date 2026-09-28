# Spark Big-Data Processing

SIH 2026 – National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer — Step 5 (batch processing).

## What PySpark is doing here
`process_weather.py` runs a local Spark batch job that:
1. Finds the **latest** cleaned CSV in `../cleaning/data/processed/`.
2. Loads it into a Spark DataFrame using an **explicit schema** (no schema inference).
3. **Validates/filters** records against the same data-quality rules used in the cleaning stage (valid lat/lon range, humidity 0–100, non-negative precipitation/wind, no null timestamp/location/temperature) — records that don't pass are dropped, nothing is invented to replace them.
4. **Derives** extra fields: `location_id` (lat_lon), `observation_date`, `temperature_f`, `wind_speed_ms`.
5. **Aggregates** the validated+enriched records by location, computing: record count, avg/max/min temperature, avg humidity, total precipitation, avg wind speed.
6. Writes two **Parquet** outputs per run.

This is a **local batch** job only — it reads from the cleaned CSVs on disk, not from Kafka, and does not use Spark Structured Streaming. Those are later stages.

## Why Spark for this problem (PS 26069)
A national weather platform needs to process readings from many locations, at high frequency, over time — far more volume than a single Pandas DataFrame in memory can comfortably handle. Spark:
- Scales the same DataFrame code from a laptop (`local[*]`) to a real cluster later, with no rewrite.
- Handles large-scale aggregation (grouping by location/time across millions of readings) efficiently via distributed execution.
- Produces **Parquet**, a compressed, columnar format well suited to the large historical/aggregated datasets the Data Scientist and Backend teams will query later.
- Is the natural place to later plug in Kafka structured streaming for real-time processing, once this batch version is proven.

## Installation
```bash
cd data-engineering/spark
pip install -r requirements.txt
```
PySpark needs a Java Runtime (JDK 8, 11, or 17) installed and on your `PATH` — see Windows setup notes below.

## Run
```bash
cd data-engineering/spark
python process_weather.py
```
Prerequisite: at least one cleaned CSV must already exist in `../cleaning/data/processed/` (run `cleaning/clean_weather.py` first).

## Input
The latest file matching:
```
../cleaning/data/processed/weather_cleaned_*.csv
```
Columns expected (same as produced by `clean_weather.py`):
`timestamp, latitude, longitude, timezone, temperature_c, relative_humidity_pct, precipitation_mm, wind_speed_kmh, weather_code`

## Output
Each run creates a new timestamped folder:
```
data-engineering/spark/data/processed/run_<UTC timestamp>/
├── records.parquet   # validated + enriched per-record data (for Data Scientist team)
└── summary.parquet   # aggregated stats per location (for Backend team / dashboards)
```
Each `.parquet` path is a single Parquet file (written via PyArrow, not Spark's own Hadoop-backed writer — see "Windows-specific setup" below), so it can be opened directly with `pandas.read_parquet(...)`, `pyarrow.parquet.read_table(...)`, or Spark's own `spark.read.parquet(...)`.

`records.parquet` columns: all cleaned columns plus `location_id`, `observation_date`, `temperature_f`, `wind_speed_ms`.

`summary.parquet` columns: `location_id, latitude, longitude, timezone, record_count, avg_temperature_c, max_temperature_c, min_temperature_c, avg_humidity_pct, total_precipitation_mm, avg_wind_speed_kmh`.

## Example output (console)
```
Input file: ../cleaning/data/processed/weather_cleaned_20260906T150000Z.csv
Records read: 3
Valid records after filtering: 3

Transformations performed:
  - Explicit schema applied (no inference)
  - Filtered invalid/out-of-range/missing-critical-field records
  - Derived fields added: location_id, observation_date, temperature_f, wind_speed_ms
  - Aggregated by location: avg/max/min temperature, avg humidity,
    total precipitation, avg wind speed, record count

[SUCCESS] Spark processing complete.
  Records output:  data/processed/run_20260906T190055Z/records.parquet
  Summary output:  data/processed/run_20260906T190055Z/summary.parquet

Summary preview:
+-----------+--------+---------+------------+------------+-----------------+-----------------+-----------------+----------------+----------------------+------------------+
|location_id|latitude|longitude|timezone    |record_count|avg_temperature_c|max_temperature_c|min_temperature_c|avg_humidity_pct|total_precipitation_mm|avg_wind_speed_kmh|
+-----------+--------+---------+------------+------------+-----------------+-----------------+-----------------+----------------+----------------------+------------------+
|18.5_73.875|18.5    |73.875   |Asia/Kolkata|2           |29.25            |29.4             |29.1             |59.0            |0.2                   |10.75             |
+-----------+--------+---------+------------+------------+-----------------+-----------------+-----------------+----------------+----------------------+------------------+
```
If the input CSV has zero data rows, or zero rows pass validation, the script logs a warning and exits cleanly without writing output — it never fabricates data to fill an empty result.

## Windows-specific setup
- **Java**: install a JDK (8, 11, or 17 recommended; 25 also works) and make sure `java -version` works from your terminal; set `JAVA_HOME` if PySpark can't find it automatically.
- **No `winutils.exe` needed.** Spark's own Parquet writer relies on Hadoop's `LocalFileSystem`/`FileOutputCommitter`, which needs `winutils.exe` on Windows even for local-only file I/O (this is the source of the `HADOOP_HOME and hadoop.home.dir are unset` error). To avoid depending on a third-party `winutils.exe` binary, this script does all Spark processing (read, schema, filter, enrich, aggregate) as normal, then writes the final Parquet output via **PyArrow** (`pandas.to_parquet(engine="pyarrow")`) instead of Spark's `.write.parquet(...)`. PyArrow writes Parquet directly with no Hadoop dependency, so no `winutils.exe`/`HADOOP_HOME` setup is required at all on Windows.
- Run from a plain `cmd`/PowerShell terminal (not inside a path with spaces or special characters, which can trip up Spark's local file URIs).
- The `local[*]` Spark master setting means this runs entirely on your own machine — no separate Spark cluster install is needed for this stage.
- Note: since the final write now collects each result DataFrame to the driver (`toPandas()`) before writing, this approach is intended for this stage's local/single-machine scale. If this job is later run on a real multi-node cluster with large data volumes, switch the write step back to Spark's native `.write.parquet(...)` (which works without issue on Linux clusters, where this Windows-only limitation doesn't apply).

## Status
🚧 Spark batch processing (cleaned CSV -> validated/enriched records + location summary, both Parquet) done. Kafka-to-Spark streaming not started yet.
