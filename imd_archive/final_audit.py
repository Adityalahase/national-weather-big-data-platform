import sqlite3
import json

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

results = {}

# 1. DATABASE COUNTS
c.execute("SELECT count(*) as c FROM weather_events")
results["total_records"] = c.fetchone()["c"]

c.execute("SELECT source, count(*) as c FROM weather_events GROUP BY source")
sources = {row["source"]: row["c"] for row in c.fetchall()}
results["sources"] = sources

# 2. IMD STATION COVERAGE
imd_count = sources.get("IMD", 0)
results["total_imd"] = imd_count

c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND station_id IS NOT NULL")
results["imd_with_station_id"] = c.fetchone()["c"]

c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND station_id IS NULL")
results["imd_without_station_id"] = c.fetchone()["c"]

c.execute("SELECT count(DISTINCT station_id) as c FROM weather_events WHERE source='IMD' AND station_id IS NOT NULL")
results["unique_station_ids"] = c.fetchone()["c"]

c.execute("SELECT count(DISTINCT city) as c FROM weather_events WHERE source='IMD'")
results["unique_cities"] = c.fetchone()["c"]

# cities with multiple station_ids
c.execute("SELECT city, count(DISTINCT station_id) as c FROM weather_events WHERE source='IMD' AND station_id IS NOT NULL GROUP BY city HAVING c > 1")
results["cities_with_multiple_station_ids"] = len(c.fetchall())

# 3. TIMESTAMP VALIDATION
c.execute("SELECT min(timestamp) as min_ts, max(timestamp) as max_ts FROM weather_events WHERE source='IMD'")
ts_stats = c.fetchone()
results["min_timestamp"] = ts_stats["min_ts"]
results["max_timestamp"] = ts_stats["max_ts"]

# Check for suspicious timezone-shifted timestamps (the old buggy batch had timestamps > 2026-09-02 14:00 and ended around 2026-09-27 19:00 but were matching IST strings without UTC shift)
# Actually, min_ts for new batch should be correctly shifted. We will report min and max.
c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND timestamp > '2026-09-27 19:00:00' AND timestamp < '2026-09-28 00:00:00'")
# Since the bug was in the past and current time is 2026-09-28 19:52 IST (14:22 UTC), the timestamps should be correctly bounded.
results["suspicious_old_batch_count"] = c.fetchone()["c"]

# 4. DUPLICATE VALIDATION
c.execute("""
    SELECT event_type, station_id, timestamp, count(*) as c 
    FROM weather_events 
    WHERE source='IMD' AND event_type='Observation' AND station_id IS NOT NULL 
    GROUP BY event_type, station_id, timestamp 
    HAVING c > 1
""")
new_dupes = c.fetchall()
results["new_duplicates"] = len(new_dupes)

c.execute("""
    SELECT event_type, city, timestamp, count(*) as c 
    FROM weather_events 
    WHERE source='IMD' AND event_type='Observation' AND station_id IS NULL 
    GROUP BY event_type, city, timestamp 
    HAVING c > 1
""")
old_dupes = c.fetchall()
results["old_duplicates"] = len(old_dupes)

# 5. IMD DATA QUALITY
c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND (latitude IS NULL OR longitude IS NULL)")
results["missing_lat_lon"] = c.fetchone()["c"]
c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND (latitude < -90 OR latitude > 90 OR longitude < -180 OR longitude > 180)")
results["invalid_lat_lon"] = c.fetchone()["c"]
c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND city IS NULL")
results["missing_city"] = c.fetchone()["c"]
c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND state IS NULL")
results["missing_state"] = c.fetchone()["c"]
c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND timestamp IS NULL")
results["missing_timestamp"] = c.fetchone()["c"]
c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND event_type IS NULL")
results["missing_event_type"] = c.fetchone()["c"]

# 6. EVENT TYPES
c.execute("SELECT event_type, count(*) as c FROM weather_events WHERE source='IMD' GROUP BY event_type")
results["event_types"] = {row["event_type"]: row["c"] for row in c.fetchall()}

# 7. SEVERITY
c.execute("SELECT severity, count(*) as c FROM weather_events WHERE source='IMD' GROUP BY severity")
results["severities"] = {row["severity"]: row["c"] for row in c.fetchall()}

# 9. SCHEMA CHECK
c.execute("PRAGMA table_info(weather_events)")
schema = [row["name"] for row in c.fetchall()]
results["schema_contains_station_id"] = "station_id" in schema

print(json.dumps(results, indent=2))
