"""
Auth endpoints — the ONLY login mechanism in this app, and it's for admins only.
The public weather app never touches this router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()

    # Deliberately vague error — never reveal whether username or password
    # was the specific problem (per spec, Section 2).
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user or not user.is_active:
        raise invalid_credentials

    if not verify_password(payload.password, user.password_hash):
        raise invalid_credentials

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return schemas.TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=schemas.CurrentUser)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user
