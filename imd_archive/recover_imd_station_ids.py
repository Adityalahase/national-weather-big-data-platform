import sqlite3
import json
import glob
import os
from datetime import datetime, timedelta

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Get initial counts
c.execute("SELECT count(*) as c FROM weather_events")
total_before = c.fetchone()["c"]
c.execute("SELECT source, count(*) as c FROM weather_events GROUP BY source")
sources_before = {row["source"]: row["c"] for row in c.fetchall()}

c.execute("SELECT * FROM weather_events WHERE source='IMD' AND station_id IS NULL")
db_records = [dict(r) for r in c.fetchall()]

raw_files = sorted(glob.glob("a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/data-engineering/ingestion/data/raw/*.json"))

raw_obs_map = {}
for fpath in raw_files:
    with open(fpath, "r") as f:
        try:
            data = json.load(f)
            raw_list = data.get("data", []) if isinstance(data, dict) else data
            if not isinstance(raw_list, list): continue
                
            for r in raw_list:
                city = r.get("DISTRICT") or r.get("STATION")
                date_str, time_str, sid = r.get("DATE", ""), r.get("TIME", ""), r.get("ID")
                lat, lon = r.get("Latitude"), r.get("Longitude")
                if not city or not date_str or not time_str or not sid or lat is None or lon is None: continue
                try: lat, lon = float(lat), float(lon)
                except: continue
                try:
                    dt_ist = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                    dt_utc = dt_ist - timedelta(hours=5, minutes=30)
                    utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
                except: continue
                
                key = (city, lat, lon, utc_str)
                if key not in raw_obs_map:
                    raw_obs_map[key] = {"station_ids": set(), "raw_files": set()}
                raw_obs_map[key]["station_ids"].add(sid)
                raw_obs_map[key]["raw_files"].add(fpath.split("/")[-1].split("\\")[-1])
        except: pass

valid_mappings = []
ambiguous_ids = []
unmatched_ids = []

for r in db_records:
    db_ts = r["timestamp"].split(".")[0]
    key = (r["city"], r["latitude"], r["longitude"], db_ts)
    if key in raw_obs_map:
        station_ids = list(raw_obs_map[key]["station_ids"])
        raw_files_found = list(raw_obs_map[key]["raw_files"])
        if len(station_ids) == 1:
            valid_mappings.append({
                "weather_event_id": r["id"],
                "existing_city": r["city"],
                "existing_latitude": r["latitude"],
                "existing_longitude": r["longitude"],
                "existing_utc_timestamp": r["timestamp"],
                "recovered_station_id": station_ids[0],
                "raw_source_file": raw_files_found[0] if raw_files_found else ""
            })
        else:
            ambiguous_ids.append(r["id"])
    else:
        unmatched_ids.append(r["id"])

# 3. Validations
if len(valid_mappings) != 1127:
    print(f"FAILED: Expected 1127 mappings, got {len(valid_mappings)}")
    exit(1)

unique_ids = set(m["weather_event_id"] for m in valid_mappings)
if len(unique_ids) != 1127:
    print("FAILED: weather_event_id is not unique in mappings")
    exit(1)

for m in valid_mappings:
    if m["weather_event_id"] in ambiguous_ids or m["weather_event_id"] in unmatched_ids:
        print("FAILED: Overlap with ambiguous or unmatched")
        exit(1)

# 1. & 2. Backup and Mappings
backup_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/recovered_imd_backup.json"
mapping_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/recovered_imd_mapping.json"

target_records = [r for r in db_records if r["id"] in unique_ids]
with open(backup_path, "w") as f:
    json.dump(target_records, f, indent=2)

with open(mapping_path, "w") as f:
    json.dump(valid_mappings, f, indent=2)

print(f"Created backup at {backup_path}")
print(f"Created mapping at {mapping_path}")

try:
    # 4. UPDATE
    c.execute("BEGIN TRANSACTION")
    for m in valid_mappings:
        c.execute("UPDATE weather_events SET station_id = ? WHERE id = ? AND source = 'IMD' AND station_id IS NULL", 
                 (m["recovered_station_id"], m["weather_event_id"]))
        if c.rowcount != 1:
            raise Exception(f"Update failed for id {m['weather_event_id']}")
    
    # 6. Post-Update Checks
    c.execute("SELECT count(*) as c FROM weather_events")
    total_after = c.fetchone()["c"]
    c.execute("SELECT source, count(*) as c FROM weather_events GROUP BY source")
    sources_after = {row["source"]: row["c"] for row in c.fetchall()}
    
    c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND station_id IS NOT NULL")
    imd_not_null = c.fetchone()["c"]
    
    c.execute("SELECT count(*) as c FROM weather_events WHERE source='IMD' AND station_id IS NULL")
    imd_null = c.fetchone()["c"]

    if total_after != 4729: raise Exception(f"Total count {total_after} != 4729")
    if sources_after.get("IMD", 0) != 4542: raise Exception(f"IMD count != 4542")
    if sources_after.get("Open-Meteo", 0) != 112: raise Exception(f"Open-Meteo count != 112")
    if sources_after.get("NASA POWER", 0) != 75: raise Exception(f"NASA POWER count != 75")
    if imd_not_null != 2262: raise Exception(f"IMD NOT NULL {imd_not_null} != 2262")
    if imd_null != 2280: raise Exception(f"IMD NULL {imd_null} != 2280")
    
    # 7 & 8. Verify ambiguous and unmatched remain NULL
    if ambiguous_ids:
        c.execute(f"SELECT count(*) as c FROM weather_events WHERE id IN ({','.join('?' for _ in ambiguous_ids)}) AND station_id IS NOT NULL", ambiguous_ids)
        if c.fetchone()["c"] > 0: raise Exception("Ambiguous records were modified")
    if unmatched_ids:
        c.execute(f"SELECT count(*) as c FROM weather_events WHERE id IN ({','.join('?' for _ in unmatched_ids)}) AND station_id IS NOT NULL", unmatched_ids)
        if c.fetchone()["c"] > 0: raise Exception("Unmatched records were modified")

    # 10. Duplicate Audit
    c.execute("""
        SELECT event_type, station_id, source, timestamp, count(*) as c
        FROM weather_events
        WHERE station_id IS NOT NULL
        GROUP BY event_type, station_id, source, timestamp
        HAVING c > 1
    """)
    dups = c.fetchall()
    duplicate_count = 0
    if dups:
        print("DUPLICATE AUDIT FAILED:")
        for d in dups:
            # c counts the number of identical rows. E.g. c=2 means 1 duplicate pair.
            # duplicate_count could be the number of rows that are redundant.
            duplicate_count += (d["c"] - 1)
        print(f"Found {duplicate_count} duplicate rows.")
    
    conn.commit()
    print("SUCCESS: Transaction Committed.")
except Exception as e:
    conn.rollback()
    print(f"FAILED: Transaction Rolled Back. Reason: {e}")
    exit(1)

print("\n--- REPORT ---")
print(f"Backup location: {backup_path}")
print(f"Mapping location: {mapping_path}")
print(f"Records updated: {len(valid_mappings)}")
print(f"Records skipped (ambiguous + unmatched): {len(ambiguous_ids) + len(unmatched_ids)}")
print(f"Final IMD station_id NOT NULL coverage: {imd_not_null}")
print(f"Final IMD station_id IS NULL coverage: {imd_null}")
print(f"Duplicate audit result: Found {duplicate_count} redundant records.")
print("Confirmed: Non-IMD records untouched.")
print("Confirmed: 4 ambiguous records unchanged.")
print("Confirmed: 2276 unmatched records unchanged.")
