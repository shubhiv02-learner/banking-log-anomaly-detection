"""Salveris integration settings (service credentials + default acting principal)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class SalverisSettings:
    base_url: str
    calling_platform_id: str
    service_principal_id: str
    client_secret: str
    default_acting_principal_id: str
    timeout_seconds: float = 30.0


def get_salveris_settings() -> SalverisSettings:
    base_url = (os.getenv("SALVERIS_BASE_URL") or "").strip().rstrip("/")
    calling_platform_id = (os.getenv("SALVERIS_CALLING_PLATFORM_ID") or "").strip()
    service_principal_id = (os.getenv("SALVERIS_SERVICE_PRINCIPAL_ID") or "").strip()
    client_secret = (os.getenv("SALVERIS_CLIENT_SECRET") or "").strip()
    default_acting_principal_id = (
        os.getenv("SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID") or ""
    ).strip()

    missing = [
        name
        for name, value in (
            ("SALVERIS_BASE_URL", base_url),
            ("SALVERIS_CALLING_PLATFORM_ID", calling_platform_id),
            ("SALVERIS_SERVICE_PRINCIPAL_ID", service_principal_id),
            ("SALVERIS_CLIENT_SECRET", client_secret),
            ("SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID", default_acting_principal_id),
        )
        if not value
    ]
    if missing:
        raise ValueError(
            "Salveris is not configured. Missing env vars: " + ", ".join(missing)
        )

    return SalverisSettings(
        base_url=base_url,
        calling_platform_id=calling_platform_id,
        service_principal_id=service_principal_id,
        client_secret=client_secret,
        default_acting_principal_id=default_acting_principal_id,
    )
