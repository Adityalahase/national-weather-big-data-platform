"""
Runs run_pipeline_and_push.py on a repeating interval, so new events get
fetched, scored, and pushed to the backend automatically instead of by hand.

This is intentionally a plain Python loop, not a cron job or systemd timer —
it needs zero extra setup and works the same on Windows/Mac/Linux. For a
real deployment you'd more likely use cron (Linux/Mac) or Task Scheduler
(Windows) to run run_pipeline_and_push.py directly instead of this; this
script exists so "set it up to run on a schedule" doesn't require you to
configure OS-level scheduling just to test it.

Configuration (environment variable, optional):
    PIPELINE_INTERVAL_SECONDS   Seconds between runs. Default: 3600 (1 hour).
                                 For testing, set this low, e.g. 120.

Usage:
    python scheduler.py

Stop with Ctrl+C. Each run's full output is printed inline; a failed run
is logged and the loop keeps going (it retries on the next interval) rather
than exiting.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INTERVAL_SECONDS = int(os.environ.get("PIPELINE_INTERVAL_SECONDS", "3600"))


def run_once() -> int:
    print(f"\n########## Pipeline run starting at {datetime.now().isoformat()} ##########")
    result = subprocess.run([sys.executable, str(ROOT / "run_pipeline_and_push.py")])
    if result.returncode == 0:
        print(f"########## Pipeline run finished OK at {datetime.now().isoformat()} ##########")
    else:
        print(
            f"########## Pipeline run FAILED (exit {result.returncode}) at "
            f"{datetime.now().isoformat()} — will retry next interval ##########"
        )
    return result.returncode


def main():
    print(f"Scheduler starting. Interval: {INTERVAL_SECONDS} seconds. Ctrl+C to stop.")
    try:
        while True:
            run_once()
            print(f"Sleeping {INTERVAL_SECONDS} seconds until next run...")
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    main()
