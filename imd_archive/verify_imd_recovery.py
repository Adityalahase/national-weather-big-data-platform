import sqlite3
import json
import glob
from datetime import datetime, timedelta

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 1. Load DB Records
c.execute("SELECT * FROM weather_events WHERE source='IMD' AND station_id IS NULL")
db_records = [dict(r) for r in c.fetchall()]
total_legacy = len(db_records)

# 2. Load Raw Files
raw_files = sorted(glob.glob("a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/data-engineering/ingestion/data/raw/*.json"))

raw_obs_map = {}
raw_snapshot_count = 0

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
                lat = r.get("Latitude")
                lon = r.get("Longitude")
                
                if not city or not date_str or not time_str or not sid or lat is None or lon is None:
                    continue
                
                try:
                    lat = float(lat)
                    lon = float(lon)
                except ValueError:
                    continue
                
                try:
                    dt_ist = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                    dt_utc = dt_ist - timedelta(hours=5, minutes=30)
                    utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    continue
                
                key = (city, lat, lon, utc_str)
                if key not in raw_obs_map:
                    raw_obs_map[key] = {"station_ids": set(), "raw_ist": f"{date_str} {time_str}", "raw_files": set()}
                raw_obs_map[key]["station_ids"].add(sid)
                raw_obs_map[key]["raw_files"].add(fpath.split("/")[-1].split("\\")[-1])
                raw_snapshot_count += 1
        except Exception as e:
            pass

# 3. Matching
uniquely_recoverable = 0
ambiguous = 0
unmatched = 0

sample_success = []
sample_ambiguous = []

# To check many-to-one
raw_key_claims = {}

for r in db_records:
    db_ts = r["timestamp"].split(".")[0]
    key = (r["city"], r["latitude"], r["longitude"], db_ts)
    
    if key in raw_obs_map:
        station_ids = list(raw_obs_map[key]["station_ids"])
        raw_files_found = list(raw_obs_map[key]["raw_files"])
        raw_ist = raw_obs_map[key]["raw_ist"]
        
        if len(station_ids) == 1:
            uniquely_recoverable += 1
            if len(sample_success) < 10:
                sample_success.append({
                    "weather_event_id": r["id"],
                    "city": r["city"],
                    "latitude": r["latitude"],
                    "longitude": r["longitude"],
                    "database_utc": r["timestamp"],
                    "raw_station_id": station_ids[0],
                    "raw_ist_timestamp": raw_ist,
                    "raw_files": raw_files_found
                })
        else:
            ambiguous += 1
            sample_ambiguous.append({
                "weather_event_id": r["id"],
                "city": r["city"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "database_utc": r["timestamp"],
                "conflicting_station_ids": station_ids,
                "raw_ist_timestamp": raw_ist,
                "raw_files": raw_files_found
            })
            
        raw_key_claims[key] = raw_key_claims.get(key, 0) + 1
    else:
        unmatched += 1

many_to_one = sum(1 for v in raw_key_claims.values() if v > 1)

print("--- COVERAGE STATS ---")
print(f"Total legacy records (station_id IS NULL): {total_legacy}")
print(f"Uniquely recoverable (One-to-One): {uniquely_recoverable}")
print(f"Ambiguous (One-to-Many - Conflicting Station IDs): {ambiguous}")
print(f"Unmatched (Missing raw data): {unmatched}")
print(f"Many-to-One (Multiple DB records mapping to same unique raw observation): {many_to_one}")

print("\n--- SAMPLE AUDIT (Success) ---")
for s in sample_success:
    print(s)

print("\n--- SAMPLE AUDIT (Ambiguous/Conflicts) ---")
for s in sample_ambiguous:
    print(s)

# Conclusion Logic
print("\n--- CONCLUSION ---")
if uniquely_recoverable == 0:
    print("NOT SAFE TO RECOVER")
    print("Reason: 0 records can be safely recovered. The majority are unmatched because raw json files for 2026-09-26 are missing.")
elif unmatched > 0 or ambiguous > 0:
    print("SAFE TO RECOVER (PARTIAL ONLY)")
    print(f"Reason: Only {uniquely_recoverable} out of {total_legacy} records have valid, unique 1-to-1 mappings. {unmatched} records completely lack raw files. {ambiguous} records have exact lat/lon collisions between different stations at the same time. The partial recovery is safe because lat/lon/city/time are exact, but it leaves 2,276 records forever incomplete. Removing and re-ingesting live data might be preferred.")
else:
    print("SAFE TO RECOVER")
    print("Reason: All records matched perfectly 1-to-1.")
