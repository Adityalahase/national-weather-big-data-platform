"""
Internal API key authentication — separate from the admin JWT system.

This is for service-to-service calls (the data-engineering pipeline pushing
new events into this backend), NOT for humans and NOT for the /admin panel.
Keep it simple: a single shared secret sent in a header.

Load the real key from an environment variable in any real deployment:
    export INGESTION_API_KEY="some-long-random-string"
"""

import os
import secrets

from fastapi import Header, HTTPException, status

INGESTION_API_KEY = os.environ.get("INGESTION_API_KEY", "CHANGE_ME_INGESTION_KEY")


def verify_ingestion_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    """FastAPI dependency: raises 401 if the caller doesn't present the
    correct shared secret in the X-API-Key header."""
    if not secrets.compare_digest(x_api_key, INGESTION_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
