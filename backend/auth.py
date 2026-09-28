"""
Core authentication & authorization logic.

- Passwords are hashed with Argon2 (via pwdlib) — never stored in plain text.
- JWTs are signed with HS256 and carry {sub: user_id, role: role}.
- get_current_user(): "who are you?" (authentication)
- require_admin():    "are you allowed?" (authorization)

IMPORTANT: change SECRET_KEY before deploying anywhere real. Load it from an
environment variable in production, e.g. os.environ["JWT_SECRET_KEY"].
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import get_db
import models

# --- Config ---------------------------------------------------------------

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "CHANGE_ME_BEFORE_DEPLOYING")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # tune as needed

password_hasher = PasswordHash.recommended()  # uses Argon2 under the hood

# tokenUrl just tells the auto-docs (Swagger UI) where to get a token from
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


# --- Password helpers -------------------------------------------------------

def hash_password(plain_password: str) -> str:
    return password_hasher.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return password_hasher.verify(plain_password, password_hash)


# --- JWT helpers -------------------------------------------------------------

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Raises JWTError if invalid, expired, or malformed."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# --- FastAPI dependencies ----------------------------------------------------

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    'Who are you?'
    Verifies: token exists -> token is valid -> not expired -> user exists.
    Any failure -> 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    'Are you allowed to access this?'
    Must be called AFTER get_current_user succeeds (i.e. valid, non-expired token).
    Wrong role -> 403 Forbidden (not 401 — they ARE authenticated, just not
    authorized).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
