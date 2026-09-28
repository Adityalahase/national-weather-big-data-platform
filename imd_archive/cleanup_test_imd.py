import sqlite3
import json

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Get before counts
c.execute("SELECT count(*) as c FROM weather_events")
total_before = c.fetchone()["c"]
c.execute("SELECT source, count(*) as c FROM weather_events GROUP BY source")
sources_before = {row["source"]: row["c"] for row in c.fetchall()}

c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND station_id IS NULL")
imd_null_before = c.fetchone()["c"]

# 1. Identify EXACT 4 records
c.execute("SELECT * FROM weather_events WHERE source = 'TEST_IMD'")
test_records = [dict(r) for r in c.fetchall()]

# 2. Print IDs and relevant fields
print("TEST_IMD Records:")
for r in test_records:
    print(f"ID: {r['id']}, source: {r['source']}, city: {r['city']}, timestamp: {r['timestamp']}, station: {r['station_id']}")

# 3. Verify exactly 4 records
if len(test_records) != 4:
    print(f"ERROR: Found {len(test_records)} TEST_IMD records, expected 4.")
    exit(1)

# 4. Delete only those 4
test_ids = [r["id"] for r in test_records]
c.execute(f"DELETE FROM weather_events WHERE id IN ({','.join('?' for _ in test_ids)})", test_ids)
conn.commit()
print(f"\nDeleted {c.rowcount} TEST_IMD records.\n")

# 5. Verify counts
c.execute("SELECT count(*) as c FROM weather_events")
total_after = c.fetchone()["c"]
c.execute("SELECT source, count(*) as c FROM weather_events GROUP BY source")
sources_after = {row["source"]: row["c"] for row in c.fetchall()}

c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND station_id IS NULL")
imd_null_after = c.fetchone()["c"]

print("--- BEFORE COUNTS ---")
print(f"Total: {total_before}")
print(f"IMD: {sources_before.get('IMD', 0)}")
print(f"Open-Meteo: {sources_before.get('Open-Meteo', 0)}")
print(f"NASA POWER: {sources_before.get('NASA POWER', 0)}")
print(f"TEST_IMD: {sources_before.get('TEST_IMD', 0)}")
print(f"IMD (station_id IS NULL): {imd_null_before}")

print("\n--- AFTER COUNTS ---")
print(f"Total: {total_after} (Expected 4729)")
print(f"IMD: {sources_after.get('IMD', 0)} (Expected 4542)")
print(f"Open-Meteo: {sources_after.get('Open-Meteo', 0)} (Expected 112)")
print(f"NASA POWER: {sources_after.get('NASA POWER', 0)} (Expected 75)")
print(f"TEST_IMD: {sources_after.get('TEST_IMD', 0)} (Expected 0)")
print(f"IMD (station_id IS NULL): {imd_null_after} (Expected 3407)")

conn.close()
