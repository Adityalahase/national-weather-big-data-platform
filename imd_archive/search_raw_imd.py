import sqlite3
import json
import glob
from datetime import datetime, timedelta

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 1. Get the 3,407 records
c.execute("SELECT * FROM weather_events WHERE source='IMD' AND station_id IS NULL")
db_records = [dict(r) for r in c.fetchall()]

if len(db_records) != 3407:
    print(f"Expected 3407 records, found {len(db_records)}")

print(f"Total db records to match: {len(db_records)}")
min_ts = min(r["timestamp"] for r in db_records)
max_ts = max(r["timestamp"] for r in db_records)
print(f"DB Timestamp range: {min_ts} to {max_ts}")

# 2. Load all raw json files
raw_files = sorted(glob.glob("a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/data-engineering/ingestion/data/raw/*.json"))

# We will index all raw observations by (city, timestamp) -> station_id
# Note: Since the DB records are already correctly timestamped in UTC (by the second batch), we need to compare them with the raw records shifted to UTC, or compare raw IST with unshifted DB records. Wait, the second batch was shifted correctly? Yes, the second batch had the correct timezone shift logic? Wait, NO! 
# Let's check: The user said "Old incorrectly timestamped IMD records: 1143". "Correctly timestamped IMD records: 3407".
# So the 3407 records HAVE correct UTC timestamps.
# The raw data has DATE and TIME in IST. So we will shift raw data to UTC for matching.

raw_obs_map = {}
total_raw_obs = 0
for fpath in raw_files:
    with open(fpath, "r") as f:
        try:
            data = json.load(f)
            raw_list = data.get("data", []) if isinstance(data, dict) else data
            
            if not isinstance(raw_list, list):
                continue
                
            for r in raw_list:
                city = r.get("DISTRICT") or r.get("STATION")
                date_str = r.get("DATE", "")
                time_str = r.get("TIME", "")
                sid = r.get("ID")
                
                if not city or not date_str or not time_str or not sid:
                    continue
                
                total_raw_obs += 1
                
                # compute correct UTC time
                try:
                    dt_ist = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                    dt_utc = dt_ist - timedelta(hours=5, minutes=30)
                    utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
                    # some DB timestamps might have microseconds if they came from fallback, but most shouldn't.
                except:
                    continue
                
                lat = r.get("Latitude")
                lon = r.get("Longitude")
                if lat is None or lon is None:
                    continue
                try:
                    lat = float(lat)
                    lon = float(lon)
                except ValueError:
                    continue
                
                key = (city, lat, lon, utc_str)
                if key not in raw_obs_map:
                    raw_obs_map[key] = []
                raw_obs_map[key].append(sid)
        except:
            pass

print(f"Total raw observations parsed: {total_raw_obs}")

# 3. Match DB records
matched_count = 0
unmatched_count = 0
ambiguous_count = 0

for r in db_records:
    # DB timestamps might have microseconds (e.g. .000000). Let's strip them for match.
    db_ts = r["timestamp"].split(".")[0]
    key = (r["city"], r["latitude"], r["longitude"], db_ts)
    
    matches = list(set(raw_obs_map.get(key, [])))
    if len(matches) == 1:
        matched_count += 1
    elif len(matches) > 1:
        ambiguous_count += 1
        if ambiguous_count == 1:
            print(f"DEBUG Ambiguous key: {key} -> {matches}")
    else:
        unmatched_count += 1

print("\n--- MATCHING RESULTS ---")
print(f"Successfully uniquely matched (can recover ID): {matched_count}")
print(f"Ambiguous matches (multiple stations in city at same time): {ambiguous_count}")
print(f"Unmatched (no corresponding raw data found): {unmatched_count}")
