import sqlite3
import json

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

audit_results = {}

# 1. Database audit
cursor.execute("SELECT count(*) as count FROM weather_events")
audit_results["total_records"] = cursor.fetchone()["count"]

cursor.execute("SELECT source, count(*) as count FROM weather_events GROUP BY source")
source_counts = {row["source"]: row["count"] for row in cursor.fetchall()}
audit_results["source_counts"] = source_counts

# IMD records with valid/missing fields
cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD'")
total_imd = cursor.fetchone()["count"]
audit_results["total_imd"] = total_imd

cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD' AND latitude IS NOT NULL")
audit_results["imd_valid_lat"] = cursor.fetchone()["count"]

cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD' AND longitude IS NOT NULL")
audit_results["imd_valid_lon"] = cursor.fetchone()["count"]

cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD' AND state IS NOT NULL AND state != ''")
audit_results["imd_valid_state"] = cursor.fetchone()["count"]

cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD' AND city IS NOT NULL AND city != ''")
audit_results["imd_valid_city"] = cursor.fetchone()["count"]

cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD' AND timestamp IS NOT NULL AND timestamp != ''")
audit_results["imd_valid_timestamp"] = cursor.fetchone()["count"]

cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD' AND event_type IS NOT NULL AND event_type != ''")
audit_results["imd_valid_event_type"] = cursor.fetchone()["count"]

cursor.execute("SELECT count(*) as count FROM weather_events WHERE source='IMD' AND severity IS NOT NULL AND severity != ''")
audit_results["imd_valid_severity"] = cursor.fetchone()["count"]

# 2. IMD data distribution
cursor.execute("SELECT state, count(*) as count FROM weather_events WHERE source='IMD' GROUP BY state")
audit_results["imd_states"] = {row["state"]: row["count"] for row in cursor.fetchall()}

cursor.execute("SELECT city, count(*) as count FROM weather_events WHERE source='IMD' GROUP BY city")
audit_results["imd_cities"] = len(cursor.fetchall()) # just count of unique cities

cursor.execute("SELECT event_type, count(*) as count FROM weather_events WHERE source='IMD' GROUP BY event_type")
audit_results["imd_event_types"] = {row["event_type"]: row["count"] for row in cursor.fetchall()}

cursor.execute("SELECT severity, count(*) as count FROM weather_events WHERE source='IMD' GROUP BY severity")
audit_results["imd_severities"] = {row["severity"]: row["count"] for row in cursor.fetchall()}

cursor.execute("SELECT MIN(timestamp) as min_ts, MAX(timestamp) as max_ts FROM weather_events WHERE source='IMD'")
ts_range = cursor.fetchone()
audit_results["imd_min_timestamp"] = ts_range["min_ts"]
audit_results["imd_max_timestamp"] = ts_range["max_ts"]

# 3. Inspect actual IMD records (Sample)
cursor.execute("SELECT * FROM weather_events WHERE source='IMD' LIMIT 5")
sample_records = [dict(row) for row in cursor.fetchall()]
audit_results["imd_sample"] = sample_records

conn.close()

print(json.dumps(audit_results, indent=2))
