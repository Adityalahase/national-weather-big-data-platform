import sqlite3
import json
import os
import glob
from datetime import datetime, timedelta

# Database paths
db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
raw_dir = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/data-engineering/ingestion/data/raw/"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

results = {}

# 1. IMD database state
cursor.execute("SELECT count(*) as cnt FROM weather_events")
results["total_records"] = cursor.fetchone()["cnt"]

cursor.execute("SELECT count(*) as cnt FROM weather_events WHERE source='IMD'")
results["total_imd"] = cursor.fetchone()["cnt"]

# Distinguish old vs new by ID threshold. The first batch had IDs < 1300 roughly, second > 1300.
# Alternatively, check for the hour/minute fraction differences. But ID is simplest.
cursor.execute("SELECT min(id), max(id), count(*) FROM weather_events WHERE source='IMD'")
min_id, max_id, _ = cursor.fetchone()

# Let's find a clear gap in IDs or timestamps.
# The new ones were just inserted, so their IDs are higher.
cursor.execute("SELECT id, timestamp, city, latitude, longitude FROM weather_events WHERE source='IMD' ORDER BY id")
all_imd = [dict(r) for r in cursor.fetchall()]

# A rough heuristic: check how many records we have
# The first run inserted 1143. The second run inserted 1134.
old_records = all_imd[:1143]
new_records = all_imd[1143:]

results["old_count"] = len(old_records)
results["new_count"] = len(new_records)

# Check overlaps
overlap_count = 0
new_dict = {}
for nr in new_records:
    # Use lat/lon + unshifted timestamp to match old
    dt = datetime.strptime(nr["timestamp"], "%Y-%m-%d %H:%M:%S.%f") if "." in nr["timestamp"] else datetime.strptime(nr["timestamp"], "%Y-%m-%d %H:%M:%S")
    dt_shifted = dt + timedelta(hours=5, minutes=30)
    key = (nr["latitude"], nr["longitude"], dt_shifted.strftime("%Y-%m-%d %H:%M:%S"))
    new_dict[key] = True

for or_r in old_records:
    base_ts = or_r["timestamp"].split(".")[0] if "." in or_r["timestamp"] else or_r["timestamp"]
    key = (or_r["latitude"], or_r["longitude"], base_ts)
    if key in new_dict:
        overlap_count += 1
        
results["overlap_count"] = overlap_count

# 2. Inspect IMD station identity from Raw JSON
latest_json = sorted(glob.glob(os.path.join(raw_dir, "*.json")))[-1]
with open(latest_json, "r") as f:
    raw_data = json.load(f)

# The raw data is a list or dict with 'data'
if isinstance(raw_data, dict) and "data" in raw_data:
    raw_list = raw_data["data"]
elif isinstance(raw_data, list):
    raw_list = raw_data
else:
    raw_list = []

station_ids = []
cities = []
missing_ids = 0
city_to_stations = {}

for r in raw_list:
    sid = r.get("ID")
    city = r.get("DISTRICT") or r.get("STATION")
    
    if sid:
        station_ids.append(sid)
        if city not in city_to_stations:
            city_to_stations[city] = set()
        city_to_stations[city].add(sid)
    else:
        missing_ids += 1
        
    if city:
        cities.append(city)

results["unique_station_ids"] = len(set(station_ids))
results["unique_cities"] = len(set(cities))
results["missing_ids"] = missing_ids

multiple_stations_per_city = {c: list(s) for c, s in city_to_stations.items() if len(s) > 1}
results["cities_with_multiple_stations"] = len(multiple_stations_per_city)
results["cities_with_multiple_stations_sample"] = dict(list(multiple_stations_per_city.items())[:5])

# 3. Evaluate duplicate identity
# Can two stations in the same city have the same timestamp?
same_city_same_time = 0
city_time_counts = {}
for r in raw_list:
    city = r.get("DISTRICT") or r.get("STATION")
    time_str = f"{r.get('DATE')} {r.get('TIME')}"
    key = (city, time_str)
    city_time_counts[key] = city_time_counts.get(key, 0) + 1

same_city_same_time_instances = {k: v for k, v in city_time_counts.items() if v > 1}
results["same_city_same_time_count"] = len(same_city_same_time_instances)
results["same_city_same_time_sample"] = [{"city": k[0], "time": k[1], "count": v} for k, v in list(same_city_same_time_instances.items())[:5]]

print(json.dumps(results, indent=2))
