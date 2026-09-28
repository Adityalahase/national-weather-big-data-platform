import sqlite3
import json
import sys
import os

db_path = "backend/weather_platform.db"
backup_path = "deleted_imd_duplicates_backup.json"

def main():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # STEP 1: REBUILD THE DUPLICATE LIST
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
        
        if len(duplicate_groups) != 197:
            raise ValueError(f"Expected 197 duplicate groups, found {len(duplicate_groups)}")
            
        deletion_candidates = []
        backup_records = []
        
        for group in duplicate_groups:
            cursor.execute("""
                SELECT * FROM weather_events
                WHERE event_type = ? AND station_id = ? AND source = ? AND timestamp = ?
            """, (group["event_type"], group["station_id"], group["source"], group["timestamp"]))
            
            records = [dict(r) for r in cursor.fetchall()]
            
            # Sort by ID
            records.sort(key=lambda x: x["id"])
            lower_id_record = records[0]
            higher_id_record = records[-1]
            
            if len(records) != 2:
                raise ValueError(f"Expected exactly 2 records per duplicate group, found {len(records)} for {group['station_id']}")
            
            # Verify identical in every column except ID
            for k in lower_id_record.keys():
                if k == 'id': continue
                if lower_id_record[k] != higher_id_record[k]:
                    raise ValueError(f"Mismatch in column {k} between {lower_id_record['id']} and {higher_id_record['id']}")
                    
            # STEP 2: SAFETY VALIDATION
            candidate = higher_id_record
            if candidate["source"] != "IMD":
                raise ValueError("Candidate source is not IMD")
            if candidate["station_id"] is None:
                raise ValueError("Candidate station_id is NULL")
                
            deletion_candidates.append(candidate["id"])
            backup_records.append(candidate)
            
        if len(deletion_candidates) != 197:
            raise ValueError(f"Expected exactly 197 deletion candidates, found {len(deletion_candidates)}")

        # STEP 3: BACKUP
        with open(backup_path, "w") as f:
            json.dump(backup_records, f, indent=2)
        print(f"Backed up {len(backup_records)} records to {os.path.abspath(backup_path)}")
        
        # STEP 4: FINAL PRE-DELETE COUNT
        def get_count(q):
            cursor.execute(q)
            return cursor.fetchone()[0]
            
        total_events = get_count("SELECT COUNT(*) FROM weather_events")
        imd_count = get_count("SELECT COUNT(*) FROM weather_events WHERE source='IMD'")
        om_count = get_count("SELECT COUNT(*) FROM weather_events WHERE source='Open-Meteo'")
        nasa_count = get_count("SELECT COUNT(*) FROM weather_events WHERE source='NASA POWER'")
        
        print(f"Pre-delete Total: {total_events} (Expected 4729)")
        print(f"Pre-delete IMD: {imd_count} (Expected 4542)")
        print(f"Pre-delete Open-Meteo: {om_count} (Expected 112)")
        print(f"Pre-delete NASA POWER: {nasa_count} (Expected 75)")
        print(f"Deletion Candidates: {len(deletion_candidates)} (Expected 197)")
        
        if total_events != 4729 or imd_count != 4542 or om_count != 112 or nasa_count != 75 or len(deletion_candidates) != 197:
            raise ValueError("Pre-delete counts do not match expected values")
            
        # STEP 5: DELETE
        print("Executing delete...")
        cursor.execute("BEGIN TRANSACTION")
        
        placeholders = ','.join('?' * len(deletion_candidates))
        delete_query = f"DELETE FROM weather_events WHERE id IN ({placeholders})"
        cursor.execute(delete_query, tuple(deletion_candidates))
        
        if cursor.rowcount != 197:
            raise ValueError(f"Expected to delete 197 records, but {cursor.rowcount} were affected.")
            
        # STEP 6 & 7 & 8: POST-DELETION VALIDATION
        total_events_post = get_count("SELECT COUNT(*) FROM weather_events")
        imd_count_post = get_count("SELECT COUNT(*) FROM weather_events WHERE source='IMD'")
        om_count_post = get_count("SELECT COUNT(*) FROM weather_events WHERE source='Open-Meteo'")
        nasa_count_post = get_count("SELECT COUNT(*) FROM weather_events WHERE source='NASA POWER'")
        
        if total_events_post != 4532: raise ValueError(f"Post Total: {total_events_post} != 4532")
        if imd_count_post != 4345: raise ValueError(f"Post IMD: {imd_count_post} != 4345")
        if om_count_post != 112: raise ValueError(f"Post Open-Meteo: {om_count_post} != 112")
        if nasa_count_post != 75: raise ValueError(f"Post NASA POWER: {nasa_count_post} != 75")
        
        # Verify duplicate groups = 0
        cursor.execute(query)
        dup_groups_post = cursor.fetchall()
        if len(dup_groups_post) != 0:
            raise ValueError(f"Still found {len(dup_groups_post)} duplicate groups after deletion")
            
        # Verify IMD station_id NOT NULL = 2065
        imd_not_null_post = get_count("SELECT COUNT(*) FROM weather_events WHERE source='IMD' AND station_id IS NOT NULL")
        if imd_not_null_post != 2065:
            raise ValueError(f"Expected 2065 IMD station_id NOT NULL, got {imd_not_null_post}")
            
        # Verify IMD station_id IS NULL = 2280
        imd_null_post = get_count("SELECT COUNT(*) FROM weather_events WHERE source='IMD' AND station_id IS NULL")
        if imd_null_post != 2280:
            raise ValueError(f"Expected 2280 IMD station_id NULL, got {imd_null_post}")
            
        print("All validations passed. Committing deletion.")
        conn.commit()
        print(f"Successfully deleted {len(deletion_candidates)} records.")
        print(f"Sample deleted IDs: {deletion_candidates[:10]}")
        
    except Exception as e:
        conn.rollback()
        print(f"FAILED AND ROLLED BACK: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
