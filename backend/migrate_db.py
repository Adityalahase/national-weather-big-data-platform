import sqlite3

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(weather_events);")
columns = [col[1] for col in cursor.fetchall()]

if "station_id" not in columns:
    print("Adding station_id column...")
    cursor.execute("ALTER TABLE weather_events ADD COLUMN station_id VARCHAR;")
    conn.commit()
    print("Column added successfully.")
else:
    print("station_id column already exists.")

conn.close()
