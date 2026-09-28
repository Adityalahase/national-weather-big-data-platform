import sqlite3
import shutil

# backup DB first
shutil.copy('weather_platform.db', 'weather_platform_backup.db')

conn = sqlite3.connect('weather_platform.db')
cur = conn.cursor()

cur.execute('SELECT source, COUNT(*) FROM weather_events GROUP BY source')
print('BEFORE:', cur.fetchall())

cur.execute("DELETE FROM weather_events WHERE source='IMD'")
print('Deleted IMD records:', cur.rowcount)

conn.commit()

cur.execute('SELECT source, COUNT(*) FROM weather_events GROUP BY source')
print('AFTER:', cur.fetchall())

conn.close()
