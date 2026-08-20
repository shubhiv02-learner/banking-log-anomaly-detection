"""Password hashing and JWT helpers for SentryyIQ login (no signup)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.orm import Session

from backend.db_models import UserMaster
from backend.logging_config import get_logger

_logger = get_logger(__name__)

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")
_venv_env = _ROOT / ".venv" / ".env"
if _venv_env.exists():
    load_dotenv(_venv_env)

JWT_ALGORITHM = "HS256"
DEFAULT_EXPIRE_MINUTES = 480


class AuthConfigError(Exception):
    """JWT_SECRET (or related auth config) is missing."""


def _jwt_secret() -> str:
    secret = (os.getenv("JWT_SECRET") or "").strip()
    if not secret:
        message = "JWT_SECRET is not configured."
        _logger.error(message)
        raise AuthConfigError(message)
    return secret


def jwt_expire_minutes() -> int:
    raw = (os.getenv("JWT_EXPIRE_MINUTES") or "").strip()
    if not raw:
        return DEFAULT_EXPIRE_MINUTES
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_EXPIRE_MINUTES
    return value if value > 0 else DEFAULT_EXPIRE_MINUTES


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def get_user_by_email(db: Session, email: str) -> UserMaster | None:
    return (
        db.query(UserMaster)
        .filter(UserMaster.email.ilike(email.strip()))
        .first()
    )


def get_user_by_id(db: Session, user_id: int) -> UserMaster | None:
    return db.query(UserMaster).filter(UserMaster.user_id == user_id).first()


def authenticate(db: Session, email: str, password: str) -> UserMaster | None:
    user = get_user_by_email(db, email)
    if user is None:
        _logger.info("Login failed (reason='unknown_user')")
        return None
    if not user.active:
        _logger.info("Login failed (reason='inactive', user_id=%s)", user.user_id)
        return None
    if not user.password_hash:
        _logger.info("Login failed (reason='no_password', user_id=%s)", user.user_id)
        return None
    if not verify_password(password, user.password_hash):
        _logger.info("Login failed (reason='bad_password', user_id=%s)", user.user_id)
        return None
    _logger.info("Login succeeded (user_id=%s)", user.user_id)
    return user


def create_access_token(user: UserMaster) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.user_id),
        "exp": now + timedelta(minutes=jwt_expire_minutes()),
        "iat": now,
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        _logger.info("Auth token rejected (reason='expired')")
        raise ValueError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        _logger.info("Auth token rejected (reason='invalid')")
        raise ValueError("Invalid token") from exc
    except AuthConfigError:
        raise

    sub = payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as exc:
        _logger.info("Auth token rejected (reason='bad_sub')")
        raise ValueError("Invalid token") from exc
    return user_id
