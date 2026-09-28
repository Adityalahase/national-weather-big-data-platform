# How to run this locally

This replaces the scattered instructions in the various READMEs with one
straight-through path to a working demo: backend API + a populated database
+ frontend dashboard. Kafka and PySpark are intentionally left out — they
need external infra (a Kafka broker, Java) this guide doesn't set up; the
dashboard works fully without them.

Two terminals: one for the backend, one for the frontend.

## 1. Backend (Terminal 1)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Required for the automated pipeline below to work — the pipeline's push
# script and the backend must agree on this value. Pick any string.
export JWT_SECRET_KEY="any-long-random-string"
export INGESTION_API_KEY="any-other-long-random-string"

# Creates weather_platform.db + a default admin user + 2 sample events
python seed.py

uvicorn main:app --reload --port 8000
```

Leave this running. In a NEW terminal (Terminal 2), load some events into it —
either the one-off manual way or the automated way described in section 1b
below — before moving on to the frontend.

### Option A — one-off manual load (fastest, no HTTP call, no server needed)

```bash
cd backend
python load_ml_events.py
```

Inserts the ~185 pre-computed events directly into `weather_platform.db`.
Good for a quick check that the display side works, but it's a static
snapshot — running it again does nothing new.

### Option B — the actual automated pipeline (what was asked for)

This is a separate, new set of scripts under `SIH_26069_Member3_FINAL/src/`
that: fetches real weather data (Open-Meteo + NASA POWER) → combines the two
sources → detects events → cross-verifies them → scores them → **calls
`POST /internal/events/bulk` on the running backend itself** — no manual
DB writes, no copy-pasting JSON.

**Same terminal, same `INGESTION_API_KEY` value as the backend (Terminal 1):**
```bash
cd SIH_26069_Member3_FINAL
pip install -r requirements.txt
export INGESTION_API_KEY="any-other-long-random-string"   # must match Terminal 1
export BACKEND_URL="http://127.0.0.1:8000"                # default, shown for clarity

# Run the pipeline once, end to end, ending in a push to the backend:
python src/run_pipeline_and_push.py
```

This needs internet access (it calls the Open-Meteo and NASA POWER APIs). If
either call fails, the script stops and pushes nothing — it never pushes
stale data silently.

**To run it repeatedly on a schedule** instead of by hand:
```bash
export PIPELINE_INTERVAL_SECONDS=120   # every 2 minutes, for testing;
                                        # use something like 3600 (hourly) for real use
python src/scheduler.py
```
Leave this running in its own terminal; it loops `run_pipeline_and_push.py`
on that interval and keeps going even if one run fails (it just retries next
interval). Stop with Ctrl+C.

Visit `http://127.0.0.1:8000/docs` — you should see the Swagger UI with all
routes, and `GET /api/events` should return ~187 events.

Default admin login: `admin` / `ChangeMe123!` (change this — see
`backend/README.md`).

## 2. Frontend (Terminal 2, separate from backend)

```bash
cd frontend
npm install
npm run dev
```

Vite will print a local URL (typically `http://localhost:5173`). Open it —
the dashboard should load the India map with the events from step 1.

If `npm install` fails on a native dependency, delete `node_modules` and
`package-lock.json` and try again; this usually only happens if a
`node_modules` folder built on a different OS/CPU got carried over (this
repo no longer ships one).

## 3. What's deliberately not wired up

- **Kafka** (`data-engineering/ingestion/kafka_producer.py`) needs a broker
  running at `localhost:9092` — not started by this guide. It's a
  standalone one-shot publish, not required for the dashboard to work.
- **PySpark** (`data-engineering/spark/process_weather.py`) needs a local
  Java install and is a separate batch job producing Parquet files; also
  not required for the dashboard.
- **IMD data**: everything here uses Open-Meteo (live + ERA5 historical
  reanalysis) as a stand-in, since direct IMD API access is still pending
  for this project (see `data-engineering/DATA_ENGINEER_HANDOFF.md`,
  section 3). Don't present this as official IMD data.
- **Social media & citizen reports**: the processing/verification scripts
  for these (`process_social_media.py`, `verify_citizen_reports.py`, etc.)
  are real code, but their only inputs are small hand-written demo CSVs
  (`data/raw/social_media/social_media_posts.csv`,
  `data/raw/citizen/citizen_reports.csv`) — there's no live social-media
  feed or citizen-report submission form behind them, and they're not part
  of the automated pipeline below. Wiring up real sources here would need
  actual API access/credentials or a report-intake form, which is outside
  what this fix covers.

## 4. Testing the automated pipeline (fetch → filter → push → display)

This is the end-to-end test: confirm the pipeline itself is pushing new data
into the backend, not just that pre-loaded data displays.

1. **Start the backend** (Terminal 1) — section 1 above, ending in
   `uvicorn main:app --reload --port 8000`. Leave it running.

2. **Check the starting count.** In a third terminal:
   ```bash
   curl -s http://127.0.0.1:8000/api/analytics
   ```
   Note `total_events` (should be 2 right after `seed.py`, before you've
   loaded anything else).

3. **Run the pipeline once** (Terminal 2, same `INGESTION_API_KEY` as
   Terminal 1):
   ```bash
   cd SIH_26069_Member3_FINAL
   pip install -r requirements.txt
   export INGESTION_API_KEY="any-other-long-random-string"
   python src/run_pipeline_and_push.py
   ```
   Watch the output — it prints a `RUNNING <script>` banner for each of the
   7 stages (fetch, fetch, combine, detect, aggregate, score, push). The
   last stage (`push_events_to_backend.py`) should print something like
   `Batch 1: pushed <N> events (201).` If it instead prints a 401, your two
   `INGESTION_API_KEY` values don't match; if it prints a connection error,
   the backend isn't running or `BACKEND_URL` is wrong.

4. **Check the count went up:**
   ```bash
   curl -s http://127.0.0.1:8000/api/analytics
   ```
   `total_events` should now be higher than in step 2. `GET
   http://127.0.0.1:8000/api/events?limit=5` should show newly-pushed events
   at the top (they're sorted newest-first, but note their `timestamp` is
   the weather event's own time, not "when it was pushed" — so compare
   `total_events` counts, not just what's on top, to confirm new rows
   landed).

5. **Confirm filtering is real, not a pass-through.** Open
   `SIH_26069_Member3_FINAL/outputs/weather_events_multisource.json` (every
   raw detection, mostly `"Normal"`) versus
   `outputs/evidence_scored_events.json` (only the ~185 that survived
   aggregation into episodes + evidence scoring). Only the latter gets
   pushed — `"Normal"` events are explicitly dropped in
   `push_events_to_backend.py`'s `to_event_payload()`.

6. **Test the schedule, not just one run.** Instead of step 3:
   ```bash
   export PIPELINE_INTERVAL_SECONDS=120
   python src/scheduler.py
   ```
   Leave it running and re-check `total_events` after ~2–3 minutes without
   touching anything else — it should have run again on its own. Stop with
   Ctrl+C when done.

7. **Confirm the frontend reflects it** (section 2 above): start it, open
   the dashboard, and the newly-pushed events should appear on the India map
   and in the analytics/timeline views without any frontend changes needed
   — it was already reading from `GET /api/events`.

## 5. Changes made to get this running

- Removed a committed, Windows-specific `backend/venv` and `__pycache__`
  (not portable — create your own venv per the steps above).
- Removed the two redundant `backend (1).zip` / `backend (2).zip` archives
  (the `backend/` folder they duplicate was already present unpacked).
- Removed a committed `frontend/node_modules` and `frontend/dist` (large,
  and native sub-dependencies are platform-specific — run `npm install`
  fresh instead).
- Added `backend/load_ml_events.py` — a one-off manual loader (Option A
  above) that writes pre-computed events straight into the database. Useful
  for a quick check, but not the "real" integration.
- Added `SIH_26069_Member3_FINAL/src/push_events_to_backend.py` — calls the
  backend's existing (but previously unused) `POST /internal/events/bulk`
  endpoint with the pipeline's output.
- Added `SIH_26069_Member3_FINAL/src/run_pipeline_and_push.py` — chains the
  7 stages that were previously separate, manually-run scripts with no
  orchestrator connecting them (fetch → fetch → combine → detect →
  aggregate → score → push), stopping immediately without pushing anything
  if any stage fails.
- Added `SIH_26069_Member3_FINAL/src/scheduler.py` — loops
  `run_pipeline_and_push.py` on an interval (`PIPELINE_INTERVAL_SECONDS`),
  so new data gets fetched/scored/pushed automatically instead of by hand.

## 6. What I verified vs. couldn't verify

This was built and reviewed in a sandboxed environment with no internet
access, so `pip install` / `npm install` / actually starting the servers or
hitting the real Open-Meteo/NASA POWER APIs could not be run here. What was
checked:
- Every backend and pipeline `.py` file (including all 4 new scripts)
  compiles cleanly (`python -m py_compile`).
- The event field-mapping logic in both `load_ml_events.py` and
  `push_events_to_backend.py` was dry-run against the real
  `evidence_scored_events.json` already in this repo: all 185 records map
  successfully to the backend's expected schema, with no extra or missing
  fields.
- Traced the actual script-to-script file dependencies (which script reads
  which output file) to confirm the 7-stage order in
  `run_pipeline_and_push.py` matches how `evidence_scored_events.json` was
  really produced — this isn't the same chain as the project's own
  `run_all.py` (which stops at the raw, unfiltered `weather_events.json`).

What could not be verified here: an actual HTTP round-trip against a live
`uvicorn` server, and a live call to the Open-Meteo/NASA POWER APIs. Please
run through the "Testing the automated pipeline" steps above on your
machine — if `run_pipeline_and_push.py` errors on the fetch stages, it's
most likely a network/API issue, not a mapping issue (that part's been
checked against real data).
