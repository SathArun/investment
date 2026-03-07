from __future__ import annotations
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import bcrypt
import structlog
from jose import jwt
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.auth.models import Advisor, RefreshToken
from app.config import settings

# NOTE: switching to HMAC invalidates existing bcrypt-hashed refresh tokens — all users re-login once

logger = structlog.get_logger()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _hash_token(raw_token: str) -> str:
    """Hash a refresh token string for secure storage."""
    return hmac.new(settings.JWT_SECRET_KEY.encode(), raw_token.encode(), hashlib.sha256).hexdigest()


def _verify_token(raw_token: str, token_hash: str) -> bool:
    return hmac.compare_digest(_hash_token(raw_token), token_hash)


def create_advisor(session: Session, email: str, password: str, name: str, **kwargs) -> Advisor:
    advisor = Advisor(
        id=str(uuid.uuid4()),
        email=email,
        password_hash=hash_password(password),
        name=name,
        **kwargs,
    )
    session.add(advisor)
    session.commit()
    session.refresh(advisor)
    return advisor


def authenticate_advisor(session: Session, email: str, password: str) -> Optional[Advisor]:
    advisor = session.query(Advisor).filter(Advisor.email == email, Advisor.is_active == True).first()
    if not advisor or not verify_password(password, advisor.password_hash):
        return None
    return advisor


def create_access_token(advisor_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": advisor_id, "exp": expire, "type": "access"},
        settings.JWT_SECRET_KEY, algorithm="HS256",
    )


def create_refresh_token(session: Session, advisor_id: str) -> str:
    token_id = str(uuid.uuid4())
    raw_token = f"{token_id}.{uuid.uuid4().hex}"
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    token_hash = _hash_token(raw_token)
    session.add(RefreshToken(
        id=token_id,
        advisor_id=advisor_id,
        token_hash=token_hash,
        expires_at=expire.replace(tzinfo=None),
        is_revoked=False,
    ))
    session.commit()
    return raw_token


def rotate_refresh_token(session: Session, raw_token: str) -> Optional[Tuple[str, str]]:
    """Validate + revoke old refresh token, issue new one.

    Returns (new_raw_token, advisor_id) tuple or None if invalid.
    """
    # Token format: "{id}.{secret}"
    parts = raw_token.split(".", 1)
    if len(parts) != 2:
        return None
    token_id = parts[0]

    record = session.get(RefreshToken, token_id)
    if not record or record.is_revoked:
        return None

    # Compare expires_at (naive datetime from DB) with current UTC time (naive);
    # DB stores naive datetimes so we strip tz from utcnow to keep types consistent.
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    if record.expires_at < now_naive:
        return None

    if not _verify_token(raw_token, record.token_hash):
        return None

    advisor_id = record.advisor_id

    # Atomically revoke old token; rowcount guard prevents double-use races
    result = session.execute(
        update(RefreshToken)
        .where(RefreshToken.id == token_id, RefreshToken.is_revoked == False)
        .values(is_revoked=True)
    )
    if result.rowcount != 1:
        session.rollback()
        return None

    # Issue new token inline (single commit: revocation + new token)
    new_token_id = str(uuid.uuid4())
    new_raw_token = f"{new_token_id}.{uuid.uuid4().hex}"
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    session.add(RefreshToken(
        id=new_token_id,
        advisor_id=advisor_id,
        token_hash=_hash_token(new_raw_token),
        expires_at=expire.replace(tzinfo=None),
        is_revoked=False,
    ))
    session.commit()  # single commit: revocation + new token
    return new_raw_token, advisor_id
