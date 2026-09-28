import json

def inspect_json(filepath):
    print(f"\n--- Inspecting {filepath} ---")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            print(f"Type: List, Length: {len(data)}")
            if len(data) > 0:
                print("First record keys:", list(data[0].keys()))
                print("First record:", json.dumps(data[0], indent=2))
                
                has_station = any("ID" in r or "station_id" in r or "station" in (r.get("metadata") or {}) for r in data[:100])
                print(f"Contains station identifiers in first 100: {has_station}")
        elif isinstance(data, dict):
            print(f"Type: Dict, Keys: {list(data.keys())}")
            if "data" in data and isinstance(data["data"], list):
                sample = data["data"][0]
                print("First record:", json.dumps(sample, indent=2))
    except Exception as e:
        print(f"Error reading file: {e}")

inspect_json("A:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/SIH_26069_Member3_FINAL/outputs/weather_events.json")
inspect_json("A:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/SIH_26069_Member3_FINAL/outputs/weather_events_multisource.json")
