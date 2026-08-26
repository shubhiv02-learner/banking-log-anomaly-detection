"""Salveris integration settings (service credentials).

Acting principal for Copilot comes from user_master.external_reference, not env.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from backend.logging_config import get_logger

_logger = get_logger(__name__)

# Repo root .env (not CWD — uvicorn may start from backend/ or elsewhere)
_ROOT = Path(__file__).resolve().parents[3]
_ENV_PATH = _ROOT / ".env"
_VENV_ENV_PATH = _ROOT / ".venv" / ".env"

load_dotenv(dotenv_path=_ENV_PATH)
if _VENV_ENV_PATH.exists():
    load_dotenv(dotenv_path=_VENV_ENV_PATH)

_CONFIG_CHECKED = False


def _env(name: str) -> str:
    raw = (os.getenv(name) or "").strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        raw = raw[1:-1].strip()
    return raw


def _acting_principal_from_user_master(name: str) -> str:
    """Loads Salveris acting principal from user_master, never from seed constants."""
    try:
        from backend.database import SessionLocal
        from backend.db_models import UserMaster
    except Exception:
        return ""
    db = SessionLocal()
    try:
        user = (
            db.query(UserMaster)
            .filter(UserMaster.name.ilike(name), UserMaster.active.is_(True))
            .first()
        )
        if user is None:
            return ""
        return (user.external_reference or "").strip()
    except Exception:
        _logger.warning(
            "Could not load acting principal from user_master (name='%s')",
            name,
        )
        _logger.debug("user_master principal lookup failed", exc_info=True)
        return ""
    finally:
        db.close()


# Live investigate answers call Ollama after outbound fetches; 30s is too short
# when the model is cold or the grounded prompt is large.
_DEFAULT_TIMEOUT_SECONDS = 300.0


@dataclass(frozen=True)
class SalverisSettings:
    base_url: str
    calling_platform_id: str
    service_principal_id: str
    client_secret: str
    default_acting_principal_id: str = ""
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS


def _timeout_seconds() -> float:
    raw = _env("SALVERIS_TIMEOUT_SECONDS")
    if not raw:
        return _DEFAULT_TIMEOUT_SECONDS
    try:
        value = float(raw)
    except ValueError:
        _logger.warning(
            "Invalid SALVERIS_TIMEOUT_SECONDS='%s'; using default %.1f",
            raw,
            _DEFAULT_TIMEOUT_SECONDS,
        )
        return _DEFAULT_TIMEOUT_SECONDS
    if value <= 0:
        _logger.warning(
            "Non-positive SALVERIS_TIMEOUT_SECONDS=%.1f; using default %.1f",
            value,
            _DEFAULT_TIMEOUT_SECONDS,
        )
        return _DEFAULT_TIMEOUT_SECONDS
    return value


def get_salveris_settings() -> SalverisSettings:
    base_url = _env("SALVERIS_BASE_URL").rstrip("/")
    calling_platform_id = _env("SALVERIS_CALLING_PLATFORM_ID")
    service_principal_id = _env("SALVERIS_SERVICE_PRINCIPAL_ID")
    client_secret = _env("SALVERIS_CLIENT_SECRET")
    default_acting_principal_id = _acting_principal_from_user_master("Alice")
    timeout_seconds = _timeout_seconds()

    missing = [
        name
        for name, value in (
            ("SALVERIS_BASE_URL", base_url),
            ("SALVERIS_CALLING_PLATFORM_ID", calling_platform_id),
            ("SALVERIS_SERVICE_PRINCIPAL_ID", service_principal_id),
            ("SALVERIS_CLIENT_SECRET", client_secret),
        )
        if not value
    ]
    if missing:
        message = (
            "Salveris configuration failed (missing=%s, looked_in='%s', "
            "calling_platform_id_set=%s, service_principal_id_set=%s, "
            "alice_acting_principal_from_db=%s, client_secret_configured=%s)"
        )
        _logger.error(
            message,
            missing,
            _ENV_PATH,
            bool(calling_platform_id),
            bool(service_principal_id),
            bool(default_acting_principal_id),
            bool(client_secret),
        )
        raise ValueError(
            "Salveris is not configured. Missing env vars: " + ", ".join(missing)
            + f" (looked in {_ENV_PATH})"
        )

    settings = SalverisSettings(
        base_url=base_url,
        calling_platform_id=calling_platform_id,
        service_principal_id=service_principal_id,
        client_secret=client_secret,
        default_acting_principal_id=default_acting_principal_id,
        timeout_seconds=timeout_seconds,
    )
    _log_config_check_once(settings)
    return settings


def _log_config_check_once(settings: SalverisSettings) -> None:
    """Log seed/config IDs once. Never log SALVERIS_CLIENT_SECRET."""
    global _CONFIG_CHECKED
    if _CONFIG_CHECKED:
        return
    _logger.info(
        "Salveris configuration loaded (calling_platform_id='%s', "
        "service_principal_id='%s', default_acting_principal_id='%s', "
        "timeout_seconds=%.1f, client_secret_configured=%s)",
        settings.calling_platform_id,
        settings.service_principal_id,
        settings.default_acting_principal_id,
        settings.timeout_seconds,
        bool(settings.client_secret),
    )
    _logger.debug(
        "Salveris configuration resolved (base_url='%s', timeout_seconds=%.1f, "
        "env_path='%s')",
        settings.base_url,
        settings.timeout_seconds,
        _ENV_PATH,
    )
    _CONFIG_CHECKED = True
