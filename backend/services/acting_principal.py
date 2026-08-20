"""Acting principal resolution for Salveris calls.

Today: temporary default from SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID.
Later: map authenticated SentryyIQ user → Salveris principal.
"""

from __future__ import annotations

from backend.integrations.salveris.exceptions import SalverisConfigError
from backend.integrations.salveris.settings import get_salveris_settings


def resolve_acting_principal() -> str:
    """Return the Salveris acting principal for the current Copilot request."""
    try:
        settings = get_salveris_settings()
    except ValueError as exc:
        raise SalverisConfigError(str(exc)) from exc

    acting_id = settings.default_acting_principal_id
    if not acting_id:
        raise SalverisConfigError(
            "SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID is not configured"
        )
    return acting_id
