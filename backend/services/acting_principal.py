"""Acting principal resolution for Salveris calls.

Uses the authenticated SentryyIQ user's user_master.external_reference
as X-Salveris-Acting-Principal-Id.
"""

from __future__ import annotations

from backend.db_models import UserMaster
from backend.logging_config import get_logger

_logger = get_logger(__name__)


class ActingPrincipalMissing(Exception):
    """Logged-in user has no Salveris acting-principal mapping."""


def resolve_acting_principal(user: UserMaster) -> str:
    """Return the Salveris acting principal for the current Copilot request."""
    acting_id = (user.external_reference or "").strip()
    if not acting_id:
        message = "Authenticated user has no Salveris acting principal mapping."
        _logger.error(
            "Acting principal missing (user_id=%s)",
            user.user_id,
        )
        raise ActingPrincipalMissing(message)
    _logger.debug(
        "Acting principal resolved (user_id=%s, acting_principal_id='%s', "
        "source='user_master.external_reference')",
        user.user_id,
        acting_id,
    )
    return acting_id
