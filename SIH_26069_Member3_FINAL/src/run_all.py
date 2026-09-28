import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scripts = [
    "src/fetch_real_weather.py",
    "src/data_pipeline.py",
    "src/model.py"
]

for s in scripts:
    print("\n" + "="*70)
    print("RUNNING", s)
    print("="*70)
    subprocess.run([sys.executable, str(ROOT/s)], check=True)

print("\nDONE. Give the backend member:")
print(ROOT / "outputs" / "weather_events.json")
