"""
Weather Data Big-Data Processing — PySpark
SIH 2026 - National Weather Big Data Analytics Platform (PS 26069)
Role: Data Engineer

Reads the latest cleaned weather CSV produced by
`cleaning/clean_weather.py`, loads it into a Spark DataFrame with an
explicit schema, validates/filters it, derives a few extra fields, and
writes two Parquet outputs:

  1. records.parquet  — validated, enriched per-record data
                         (for the Data Scientist team)
  2. summary.parquet   — aggregated statistics per location
                         (for the Backend team / dashboards)

This is a local BATCH job. It does not read from Kafka and does not
use Spark Structured Streaming — that is a later stage.

Windows note on the final write step
-------------------------------------
All reading, schema enforcement, filtering, enrichment, and aggregation
above happen entirely in Spark, as before. Only the *final write* uses
`DataFrame.toPandas()` + PyArrow (`pandas.to_parquet`) instead of
Spark's own `.write.parquet(...)`. Spark's native Parquet writer goes
through Hadoop's `LocalFileSystem` / `FileOutputCommitter`, which needs
`winutils.exe` on Windows even for purely local file I/O — that's the
`HADOOP_HOME and hadoop.home.dir are unset` error. PyArrow writes
Parquet files directly with no Hadoop dependency, so it sidesteps that
requirement completely, with no extra binaries to download. This is
appropriate at the data sizes this stage runs at (single machine,
`local[*]`); if/when this job runs on a real multi-node cluster,
switch this one block back to `df.write.parquet(...)`.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROCESSED_CSV_DIR = Path(__file__).resolve().parent.parent / "cleaning" / "data" / "processed"
OUTPUT_ROOT_DIR = Path(__file__).resolve().parent / "data" / "processed"

# Matches the columns written by cleaning/clean_weather.py
CLEANED_SCHEMA = StructType(
    [
        StructField("timestamp", TimestampType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("timezone", StringType(), True),
        StructField("temperature_c", DoubleType(), True),
        StructField("relative_humidity_pct", DoubleType(), True),
        StructField("precipitation_mm", DoubleType(), True),
        StructField("wind_speed_kmh", DoubleType(), True),
        StructField("weather_code", IntegerType(), True),
    ]
)


def find_latest_cleaned_csv() -> Path:
    """Return the most recently modified cleaned CSV from cleaning/data/processed/."""
    if not PROCESSED_CSV_DIR.exists():
        print(f"[ERROR] Cleaned data directory not found: {PROCESSED_CSV_DIR}")
        sys.exit(1)

    csv_files = sorted(PROCESSED_CSV_DIR.glob("weather_cleaned_*.csv"))
    if not csv_files:
        print(f"[ERROR] No cleaned CSV files found in: {PROCESSED_CSV_DIR}")
        print("Run cleaning/clean_weather.py first.")
        sys.exit(1)

    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    return latest


def load_cleaned_csv(spark: SparkSession, filepath: Path) -> DataFrame:
    """Read the cleaned CSV with an explicit schema (no schema inference)."""
    df = (
        spark.read.option("header", True)
        .schema(CLEANED_SCHEMA)
        .csv(str(filepath))
    )
    return df


def validate_and_filter(df: DataFrame) -> DataFrame:
    """
    Keep only records that pass basic data-quality checks. This mirrors the
    validation rules already applied in cleaning/clean_weather.py, enforced
    again here at the Spark layer since this stage may later ingest data
    from other sources (e.g. Kafka) that skip the Pandas cleaning step.

    Records with a missing/null timestamp, latitude, longitude, or
    temperature are dropped (a location/time-less reading isn't usable for
    aggregation). Nothing is invented to replace missing values.
    """
    return df.filter(
        F.col("timestamp").isNotNull()
        & F.col("latitude").isNotNull()
        & F.col("longitude").isNotNull()
        & F.col("temperature_c").isNotNull()
        & F.col("latitude").between(-90, 90)
        & F.col("longitude").between(-180, 180)
        & (F.col("relative_humidity_pct").isNull() | F.col("relative_humidity_pct").between(0, 100))
        & (F.col("precipitation_mm").isNull() | (F.col("precipitation_mm") >= 0))
        & (F.col("wind_speed_kmh").isNull() | (F.col("wind_speed_kmh") >= 0))
    )


def enrich(df: DataFrame) -> DataFrame:
    """Add derived fields useful for downstream analysis."""
    return (
        df.withColumn("location_id", F.concat_ws("_", F.col("latitude"), F.col("longitude")))
        .withColumn("observation_date", F.to_date(F.col("timestamp")))
        .withColumn("temperature_f", F.round(F.col("temperature_c") * 9 / 5 + 32, 2))
        .withColumn("wind_speed_ms", F.round(F.col("wind_speed_kmh") / 3.6, 2))
    )


def summarize_by_location(df: DataFrame) -> DataFrame:
    """Aggregate weather stats grouped by location."""
    return df.groupBy("location_id", "latitude", "longitude", "timezone").agg(
        F.count("*").alias("record_count"),
        F.round(F.avg("temperature_c"), 2).alias("avg_temperature_c"),
        F.round(F.max("temperature_c"), 2).alias("max_temperature_c"),
        F.round(F.min("temperature_c"), 2).alias("min_temperature_c"),
        F.round(F.avg("relative_humidity_pct"), 2).alias("avg_humidity_pct"),
        F.round(F.sum("precipitation_mm"), 2).alias("total_precipitation_mm"),
        F.round(F.avg("wind_speed_kmh"), 2).alias("avg_wind_speed_kmh"),
    )


def write_parquet_no_hadoop(df: DataFrame, output_path: Path) -> None:
    """
    Write a Spark DataFrame to a single Parquet file using PyArrow, instead
    of Spark's own Hadoop-backed `.write.parquet(...)`. This avoids Hadoop's
    `LocalFileSystem` / `FileOutputCommitter`, which is what requires
    `winutils.exe` on Windows. The DataFrame is collected to the driver via
    `toPandas()` first — fine at this stage's local, single-machine scale.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pandas_df = df.toPandas()
    pandas_df.to_parquet(output_path, engine="pyarrow", index=False)


def main():
    spark = SparkSession.builder.appName("WeatherBatchProcessing").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    try:
        latest_csv = find_latest_cleaned_csv()
        print(f"Input file: {latest_csv}")

        raw_df = load_cleaned_csv(spark, latest_csv)
        total_records = raw_df.count()
        print(f"Records read: {total_records}")

        if total_records == 0:
            print("[WARNING] Input file has no data rows. Nothing to process.")
            spark.stop()
            sys.exit(0)

        valid_df = validate_and_filter(raw_df)
        valid_count = valid_df.count()
        print(f"Valid records after filtering: {valid_count}")

        if valid_count == 0:
            print("[WARNING] No records passed validation. Skipping enrichment/aggregation.")
            spark.stop()
            sys.exit(0)

        enriched_df = enrich(valid_df)
        summary_df = summarize_by_location(enriched_df)

        print("\nTransformations performed:")
        print("  - Explicit schema applied (no inference)")
        print("  - Filtered invalid/out-of-range/missing-critical-field records")
        print("  - Derived fields added: location_id, observation_date, temperature_f, wind_speed_ms")
        print("  - Aggregated by location: avg/max/min temperature, avg humidity,")
        print("    total precipitation, avg wind speed, record count")

        run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = OUTPUT_ROOT_DIR / f"run_{run_timestamp}"
        records_path = run_dir / "records.parquet"
        summary_path = run_dir / "summary.parquet"

        write_parquet_no_hadoop(enriched_df, records_path)
        write_parquet_no_hadoop(summary_df, summary_path)

        print("\n[SUCCESS] Spark processing complete.")
        print(f"  Records output:  {records_path}")
        print(f"  Summary output:  {summary_path}")

        print("\nSummary preview:")
        summary_df.show(truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()

