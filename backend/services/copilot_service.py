"""SentryyIQ Copilot orchestration — resolve acting principal, then call Salveris."""

from __future__ import annotations

from typing import Optional

from backend.integrations.salveris.exceptions import SalverisConfigError
from backend.integrations.salveris.models import (
    CopilotAskResponse,
    CopilotContext,
    CopilotSearchResponse,
)
from backend.integrations.salveris.salveris_client import SalverisClient
from backend.integrations.salveris.settings import get_salveris_settings
from backend.logging_config import get_logger
from backend.services.acting_principal import resolve_acting_principal

logger = get_logger(__name__)


class CopilotService:
    def __init__(self, client: SalverisClient | None = None):
        self._client = client

    def _get_client(self) -> SalverisClient:
        if self._client is not None:
            return self._client
        try:
            settings = get_salveris_settings()
        except ValueError as exc:
            raise SalverisConfigError(str(exc)) from exc
        return SalverisClient(settings)

    def search(
        self,
        question: str,
        context: Optional[CopilotContext] = None,
    ) -> CopilotSearchResponse:
        acting_id = resolve_acting_principal()
        logger.info(
            "Copilot search question_len=%s acting_principal=%s…",
            len(question),
            acting_id[:8],
        )
        return self._get_client().search(
            question,
            acting_principal_id=acting_id,
            context=context,
        )

    def ask(
        self,
        question: str,
        context: Optional[CopilotContext] = None,
    ) -> CopilotAskResponse:
        acting_id = resolve_acting_principal()
        logger.info(
            "Copilot ask question_len=%s acting_principal=%s…",
            len(question),
            acting_id[:8],
        )
        return self._get_client().answer(
            question,
            acting_principal_id=acting_id,
            context=context,
        )


copilot_service = CopilotService()
