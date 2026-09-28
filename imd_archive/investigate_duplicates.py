import sqlite3
import json

db_path = "backend/weather_platform.db"

def main():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. IDENTIFY THE 197 DUPLICATES
    query = """
    SELECT 
        event_type, station_id, source, timestamp, COUNT(*) as cnt
    FROM weather_events
    WHERE source = 'IMD' AND station_id IS NOT NULL
    GROUP BY event_type, station_id, source, timestamp
    HAVING COUNT(*) > 1
    """
    
    cursor.execute(query)
    duplicate_groups = cursor.fetchall()
    
    print(f"Total duplicate groups: {len(duplicate_groups)}")
    
    total_records_involved = 0
    redundant_records = 0
    groups_data = []
    
    for group in duplicate_groups:
        cursor.execute("""
            SELECT * FROM weather_events
            WHERE event_type = ? AND station_id = ? AND source = ? AND timestamp = ?
        """, (group["event_type"], group["station_id"], group["source"], group["timestamp"]))
        
        records = [dict(r) for r in cursor.fetchall()]
        total_records_involved += len(records)
        redundant_records += (len(records) - 1)
        groups_data.append(records)

    print(f"Total records involved: {total_records_involved}")
    print(f"Total redundant (extra) records: {redundant_records}")
    print("-" * 50)
    
    # 2. & 4. INSPECT EACH DUPLICATE GROUP & CHECK FIELD DIFFERENCES
    identical_groups = 0
    metadata_diff_groups = 0
    measurement_diff_groups = 0
    
    safe_to_remove = []
    preserve = []
    needs_investigation = []
    
    # Measurement fields that might differ (though not all might be present in the schema)
    measurement_fields = ['temperature', 'rainfall', 'humidity', 'wind_speed', 'wind_direction', 'pressure']
    
    for records in groups_data:
        base_record = records[0]
        is_completely_identical = True
        has_metadata_diff = False
        has_measurement_diff = False
        
        for r in records[1:]:
            for k in r.keys():
                if k == 'id':
                    continue
                if base_record[k] != r[k]:
                    is_completely_identical = False
                    if k in measurement_fields:
                        has_measurement_diff = True
                    else:
                        has_metadata_diff = True
        
        if is_completely_identical:
            identical_groups += 1
            safe_to_remove.extend([r['id'] for r in records[1:]])
        else:
            if has_measurement_diff:
                measurement_diff_groups += 1
                preserve.extend([r['id'] for r in records])
            else:
                metadata_diff_groups += 1
                needs_investigation.extend([r['id'] for r in records])
                print(f"Difference in group {base_record['station_id']} @ {base_record['timestamp']}:")
                for r in records:
                    print(f"  ID {r['id']}: city={r['city']}, state={r['state']}, lat={r['latitude']}, lon={r['longitude']}")
    
    print(f"Completely identical groups: {identical_groups}")
    print(f"Groups with metadata differences: {metadata_diff_groups}")
    print(f"Groups with measurement differences: {measurement_diff_groups}")
    print("-" * 50)
    
    # 3. DETERMINE INGESTION BATCH ORIGIN
    # We can check IDs. Usually lower IDs are historical.
    print("Sample Group Origin Analysis:")
    if groups_data:
        sample_group = groups_data[0]
        print(f"Group Station: {sample_group[0]['station_id']}, TS: {sample_group[0]['timestamp']}")
        for r in sample_group:
            print(f"  ID: {r['id']}, City: {r['city']}")
    print("-" * 50)
    
    # 7. HISTORICAL NULL-STATION RECORDS
    null_overlap_groups = 0
    for records in groups_data:
        base = records[0]
        cursor.execute("""
            SELECT id FROM weather_events 
            WHERE station_id IS NULL AND source='IMD' 
            AND timestamp=? AND city=? AND event_type=?
        """, (base['timestamp'], base['city'], base['event_type']))
        if cursor.fetchall():
            null_overlap_groups += 1
            
    print(f"Duplicate groups involving historical NULL-station matching city/timestamp: {null_overlap_groups}")
    print("-" * 50)
    
    # 8. FINAL CLASSIFICATION
    print("FINAL CLASSIFICATION COUNTS:")
    print(f"1. SAFE TO REMOVE: {len(safe_to_remove)} records")
    print(f"2. PRESERVE: {len(preserve)} records")
    print(f"3. NEEDS FURTHER INVESTIGATION: {len(needs_investigation)} records")
    
    if safe_to_remove:
        print(f"Sample SAFE TO REMOVE IDs: {safe_to_remove[:10]}")

if __name__ == "__main__":
    main()
