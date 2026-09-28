import sqlite3

db_path = "a:/ADITYA/Project/SIH/P1/national-weather-big-data-platform-fixed-2/national-weather-big-data-platform/backend/weather_platform.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT count(*) FROM weather_events")
print("Total records:", c.fetchone()[0])

c.execute("SELECT count(*) FROM weather_events WHERE station_id IS NOT NULL")
print("Records with station_id:", c.fetchone()[0])

c.execute("SELECT count(*) FROM weather_events WHERE source != 'IMD' AND source != 'TEST_IMD'")
print("Non-IMD records:", c.fetchone()[0])

conn.close()
