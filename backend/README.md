# National Weather Big Data Analytics Platform — Backend

FastAPI backend implementing exactly the spec from the requirements doc:
- **Public weather APIs** — zero authentication, anyone can call them.
- **Admin APIs** — protected by JWT + role-based authorization (`role: admin`).
- Passwords hashed with Argon2. Tokens expire after 60 minutes.

## Project structure

```
backend/
├── main.py              # FastAPI app, CORS, router wiring
├── database.py           # SQLAlchemy engine/session (SQLite by default)
├── models.py              # User + WeatherEvent tables
├── schemas.py              # Pydantic request/response shapes
├── auth.py                  # password hashing, JWT, get_current_user, require_admin
├── seed.py                  # creates first admin user + sample events
├── internal_auth.py          # API-key check for the data pipeline (not a user JWT)
├── requirements.txt
└── routers/
    ├── auth_router.py     # POST /auth/login, GET /auth/me
    ├── public_router.py   # GET /api/events, /api/analytics, /api/events/map
    ├── admin_router.py    # GET/PATCH /api/admin/... (all require admin JWT)
    └── internal_router.py # POST /internal/events(/bulk) — pipeline ingestion, API-key protected
```

## Step-by-step setup

**1. Create a virtual environment (recommended)**
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Seed the database** — creates `weather_platform.db`, one admin user, and 2 sample events
```bash
python seed.py
```
This prints the default admin credentials (`admin` / `ChangeMe123!`). **Change
that password** — either edit `seed.py` before running it, or add an endpoint
later to update it.

**4. Run the server**
```bash
uvicorn main:app --reload --port 8000
```

**5. Open the interactive docs**
Go to `http://127.0.0.1:8000/docs`. You can test every endpoint from there.

## Testing the flow manually

**Public endpoint — no auth needed:**
```bash
curl http://127.0.0.1:8000/api/events
```

**Admin login:**
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ChangeMe123!"}'
```
Copy the `access_token` from the response.

**Call an admin endpoint with the token:**
```bash
curl http://127.0.0.1:8000/api/admin/events \
  -H "Authorization: Bearer PASTE_TOKEN_HERE"
```

**Without a token** (should return `401`):
```bash
curl http://127.0.0.1:8000/api/admin/events
```

## Connecting the React frontend

In your frontend `.env` or config, point API calls at `http://127.0.0.1:8000`.
For `/admin`:
1. POST to `/auth/login`, store the returned `access_token` (e.g. in memory or
   a secure httpOnly cookie set by a backend proxy — avoid `localStorage` for
   anything security-sensitive if you can help it).
2. Attach `Authorization: Bearer <token>` on every request to `/api/admin/*`.
3. On `401`/`403` responses, redirect to `/admin/login`.
4. Remove "Admin Panel" from `Sidebar.jsx` per the spec — the `/admin` route
   can stay, just don't link to it from public nav.

## Data pipeline ingestion (for the data-engineering/data-science side)

The pipeline pushes new events into this backend over HTTP — it does NOT
share the admin JWT system (there's no "user" logging in, just a script).
Instead it authenticates with a shared secret in a header.

**Set the shared secret** (both here and wherever the pipeline runs):
```bash
export INGESTION_API_KEY="some-long-random-string"
```
If unset, it falls back to a placeholder in `internal_auth.py` — change that
before anyone outside your laptop touches this.

**Single event:**
```bash
curl -X POST http://127.0.0.1:8000/internal/events \
  -H "Content-Type: application/json" \
  -H "X-API-Key: some-long-random-string" \
  -d '{
    "event_type": "Flood",
    "city": "Pune",
    "state": "Maharashtra",
    "latitude": 18.5204,
    "longitude": 73.8567,
    "severity": "High",
    "confidence_score": 92,
    "verification_status": "Pending",
    "timestamp": "2026-09-14T10:00:00"
  }'
```

**Bulk (batch/historical ingestion):**
```
POST /internal/events/bulk
```
same headers, body is a JSON array of the same object shape.

New events default to `"Pending"` if the pipeline doesn't set
`verification_status` — an admin has to review and mark them
Verified/Suspicious/Rejected via the `/api/admin/events/{id}/verify` route
before they're treated as confirmed. If instead you want pipeline-ingested
events to be public and visible immediately as "Pending", that already works
as-is since `/api/events` doesn't filter by status by default.

## Notes / things to decide together with your team

- **Token expiry** is set to 60 minutes in `auth.py` (`ACCESS_TOKEN_EXPIRE_MINUTES`) — adjust as needed.
- **SECRET_KEY** in `auth.py` is a placeholder — set it via the `JWT_SECRET_KEY` environment variable before any real deployment.
- **Event schema** in `models.py`/`schemas.py` deliberately matches the agreed
  frontend contract exactly (`id, event_type, city, state, latitude, longitude,
  severity, confidence_score, verification_status, timestamp`) — don't add
  fields without checking with the frontend/data-science members first.
- Swapping SQLite → PostgreSQL later is a one-line change in `database.py`.
- The data-engineering pipeline (your teammate's ingestion jobs) should insert
  rows into `weather_events` using the `WeatherEventCreate` schema shape — you
  may want to add a small internal-only ingestion endpoint or a direct DB
  write script for that, depending on how that pipeline is built.
