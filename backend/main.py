"""
App entrypoint.

Run with:
    uvicorn main:app --reload --port 8000

Then visit http://127.0.0.1:8000/docs for interactive Swagger UI where you
can test every endpoint (including logging in and pasting the JWT into the
"Authorize" button to hit admin routes).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import auth_router, public_router, admin_router, internal_router

# Creates weather_platform.db and all tables on first run if they don't exist.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="National Weather Big Data Analytics Platform API",
    description="Public weather APIs (no auth) + JWT-protected Admin APIs.",
    version="1.0.0",
)

# Allow the React dev server to call this API. Tighten allow_origins for prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(public_router.router)
app.include_router(admin_router.router)
app.include_router(internal_router.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "national-weather-platform-api"}
