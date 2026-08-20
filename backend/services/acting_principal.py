"""Acting principal resolution for Salveris calls.

Today: temporary default from SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID.
Later: map authenticated SentryyIQ user → Salveris principal.
"""

from __future__ import annotations

from backend.integrations.salveris.exceptions import SalverisConfigError
from backend.integrations.salveris.settings import get_salveris_settings
from backend.logging_config import get_logger

_logger = get_logger(__name__)


def resolve_acting_principal() -> str:
    """Return the Salveris acting principal for the current Copilot request."""
    try:
        settings = get_salveris_settings()
    except ValueError as exc:
        message = "Acting principal resolution failed."
        _logger.error(message, exc_info=True)
        raise SalverisConfigError(str(exc)) from exc

    acting_id = settings.default_acting_principal_id
    if not acting_id:
        message = "SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID is not configured."
        _logger.error(message)
        raise SalverisConfigError(message)
    _logger.debug(
        "Acting principal resolved (acting_principal_id='%s', "
        "source='SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID')",
        acting_id,
    )
    return acting_id
