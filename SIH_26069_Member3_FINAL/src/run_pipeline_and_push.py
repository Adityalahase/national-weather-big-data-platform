"""
Runs the full pipeline that produces evidence_scored_events.json, then pushes
the result into the backend via POST /internal/events/bulk.

This chains together stages that existed as separate, manually-run scripts
with no orchestrator connecting them:

    1. fetch_real_weather.py        -> data/raw/open_meteo_era5.csv
    2. fetch_nasa_power.py          -> data/raw/nasa_power/nasa_power_weather.csv
    3. combine_weather_sources.py   -> data/processed/multi_source_weather.csv
    4. generate_multisource_events.py -> outputs/weather_events_multisource.json
    5. aggregate_weather_events.py  -> outputs/weather_event_episodes.json
    6. evidence_scoring.py          -> outputs/evidence_scored_events.json
    7. push_events_to_backend.py    -> POST /internal/events/bulk

Steps 1-2 need internet access (they call the Open-Meteo and NASA POWER
APIs). If either fails (e.g. no network, or the API is temporarily down),
this script stops there and does NOT push anything — it never falls back to
re-pushing old/stale data silently.

Usage:
    python run_pipeline_and_push.py

Note: this does not touch the separate Chain A (fetch_real_weather.py ->
data_pipeline.py -> model.py -> outputs/weather_events.json, run via
run_all.py) or the social-media/citizen-report scripts — those remain
manual/demo-data stages, as described in HOW_TO_RUN.md.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    "src/fetch_real_weather.py",
    "src/fetch_nasa_power.py",
    "src/combine_weather_sources.py",
    "src/generate_multisource_events.py",
    "src/aggregate_weather_events.py",
    "src/evidence_scoring.py",
    "src/push_events_to_backend.py",
]


def run_stage(relative_path: str) -> int:
    print("\n" + "=" * 70)
    print("RUNNING", relative_path)
    print("=" * 70)
    result = subprocess.run([sys.executable, str(ROOT / relative_path)])
    return result.returncode


def main() -> int:
    for stage in STAGES:
        code = run_stage(stage)
        if code != 0:
            print(f"\nStage '{stage}' failed (exit code {code}). Stopping — "
                  "nothing further will run, and no stale data was pushed.")
            return code

    print("\nPipeline run complete: events fetched, cross-verified, scored, "
          "and pushed to the backend.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
