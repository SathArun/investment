from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.service import (
    authenticate_advisor,
    create_access_token,
    create_refresh_token,
    rotate_refresh_token,
)
from app.db.base import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    advisor = authenticate_advisor(db, request.email, request.password)
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(advisor.id)
    refresh_token = create_refresh_token(db, advisor.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "advisor": {
            "id": advisor.id,
            "email": advisor.email,
            "name": advisor.name,
            "firm_name": advisor.firm_name,
        },
    }


@router.post("/refresh")
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    result = rotate_refresh_token(db, request.refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    new_raw_token, advisor_id = result
    access_token = create_access_token(advisor_id)
    return {
        "access_token": access_token,
        "refresh_token": new_raw_token,
    }
