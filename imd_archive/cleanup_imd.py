import sqlite3
import json

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT count(*) FROM weather_events")
total_before = c.fetchone()[0]

c.execute("SELECT count(*) FROM weather_events WHERE source = 'IMD'")
imd_before = c.fetchone()[0]

c.execute("SELECT count(*) FROM weather_events WHERE source != 'IMD' AND source != 'TEST_IMD'")
non_imd_before = c.fetchone()[0]

c.execute("SELECT * FROM weather_events WHERE source = 'IMD' ORDER BY id ASC")
all_imd_records = [dict(r) for r in c.fetchall()]

candidates = all_imd_records[:1143]
candidate_ids = [r["id"] for r in candidates]

min_id = min(candidate_ids) if candidate_ids else None
max_id = max(candidate_ids) if candidate_ids else None
null_station_count = sum(1 for r in candidates if r["station_id"] is None)
not_null_station_count = sum(1 for r in candidates if r["station_id"] is not None)
timestamps = [r["timestamp"] for r in candidates]
min_ts = min(timestamps) if timestamps else None
max_ts = max(timestamps) if timestamps else None

print("Candidate Stats:")
print(f"Count: {len(candidates)}")
print(f"Min ID: {min_id}")
print(f"Max ID: {max_id}")
print(f"station_id IS NULL: {null_station_count}")
print(f"station_id IS NOT NULL: {not_null_station_count}")
print(f"Timestamp range: {min_ts} to {max_ts}")
print(f"Total before: {total_before}")
print(f"IMD before: {imd_before}")
print(f"Non-IMD before: {non_imd_before}")

if len(candidates) != 1143:
    print(f"ERROR: Expected 1143 candidates, found {len(candidates)}")
    exit(1)

if not_null_station_count > 0:
    print(f"ERROR: Found {not_null_station_count} candidates with station_id!")
    exit(1)

backup_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/data-engineering/ingestion/data/imd_old_batch_backup.json"
with open(backup_path, "w") as f:
    json.dump(candidates, f, indent=2)

print(f"Backup saved to: {backup_path}")

print("Deleting candidates...")
c.execute(f"DELETE FROM weather_events WHERE id IN ({','.join('?' for _ in candidate_ids)})", candidate_ids)
conn.commit()
print(f"Deleted {c.rowcount} records.")

c.execute("SELECT count(*) FROM weather_events")
total_after = c.fetchone()[0]

c.execute("SELECT count(*) FROM weather_events WHERE source = 'IMD'")
imd_after = c.fetchone()[0]

c.execute("SELECT count(*) FROM weather_events WHERE source != 'IMD' AND source != 'TEST_IMD'")
non_imd_after = c.fetchone()[0]

c.execute("SELECT count(*) FROM weather_events WHERE source = 'IMD' AND station_id IS NOT NULL")
imd_with_station = c.fetchone()[0]

c.execute("SELECT count(*) FROM weather_events WHERE source = 'IMD' AND station_id IS NULL")
imd_without_station = c.fetchone()[0]

print("\nPost-Cleanup Stats:")
print(f"Total after: {total_after}")
print(f"IMD after: {imd_after}")
print(f"Non-IMD after: {non_imd_after}")
print(f"IMD with station_id: {imd_with_station}")
print(f"IMD without station_id: {imd_without_station}")

conn.close()
