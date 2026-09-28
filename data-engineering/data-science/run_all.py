import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

scripts = [
    ROOT / "ingestion" / "fetch_real_weather.py",
    ROOT / "cleaning" / "historical" / "clean_historical_weather.py",
    ROOT / "data-science" / "feature_engineering.py",
    ROOT / "data-science" / "model.py",
]

for script in scripts:
    print("\n" + "=" * 70)
    print("RUNNING", script)
    print("=" * 70)

    subprocess.run(
        [sys.executable, str(script)],
        check=True
    )

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)

print("\nWeather events generated at:")
print(ROOT / "outputs" / "weather_events.json")