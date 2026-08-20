"""SentryyIQ Copilot orchestration — resolve acting principal, then call Salveris."""

from __future__ import annotations

from typing import Optional

from backend.integrations.salveris.exceptions import SalverisConfigError
from backend.integrations.salveris.models import (
    CopilotAskResponse,
    CopilotContext,
    CopilotSearchResponse,
)
from backend.integrations.salveris.salveris_client import (
    CAPABILITY_KNOWLEDGE_ANSWER,
    CAPABILITY_KNOWLEDGE_SEARCH,
    SalverisClient,
)
from backend.integrations.salveris.settings import get_salveris_settings
from backend.db_models import UserMaster
from backend.logging_config import get_logger
from backend.services.acting_principal import resolve_acting_principal

_logger = get_logger(__name__)


class CopilotService:
    def __init__(self, client: SalverisClient | None = None):
        self._client = client

    def _get_client(self) -> SalverisClient:
        if self._client is not None:
            return self._client
        try:
            settings = get_salveris_settings()
        except ValueError as exc:
            message = "Salveris client could not be created."
            _logger.error(message, exc_info=True)
            raise SalverisConfigError(str(exc)) from exc
        _logger.info(
            "Salveris client initialized (base_url='%s', calling_platform_id='%s', "
            "service_principal_id='%s')",
            settings.base_url,
            settings.calling_platform_id,
            settings.service_principal_id,
        )
        self._client = SalverisClient(settings)
        return self._client

    def search(
        self,
        question: str,
        context: Optional[CopilotContext] = None,
        *,
        user: UserMaster,
    ) -> CopilotSearchResponse:
        acting_id = resolve_acting_principal(user)
        _logger.info(
            "Copilot search started (capability='%s', user_id=%s, "
            "acting_principal_id='%s')",
            CAPABILITY_KNOWLEDGE_SEARCH,
            user.user_id,
            acting_id,
        )
        _logger.debug(
            "Copilot search request (question_len=%d, has_context=%s)",
            len(question),
            context is not None,
        )
        result = self._get_client().search(
            question,
            acting_principal_id=acting_id,
            context=context,
        )
        _logger.info("Copilot search completed (%d hit(s))", len(result.hits))
        return result

    def ask(
        self,
        question: str,
        context: Optional[CopilotContext] = None,
        *,
        user: UserMaster,
    ) -> CopilotAskResponse:
        acting_id = resolve_acting_principal(user)
        _logger.info(
            "Copilot ask started (capability='%s', user_id=%s, "
            "acting_principal_id='%s')",
            CAPABILITY_KNOWLEDGE_ANSWER,
            user.user_id,
            acting_id,
        )
        _logger.debug(
            "Copilot ask request (question_len=%d, has_context=%s)",
            len(question),
            context is not None,
        )
        result = self._get_client().answer(
            question,
            acting_principal_id=acting_id,
            context=context,
        )
        _logger.info(
            "Copilot ask completed (%d source(s))",
            len(result.sources),
        )
        return result


copilot_service = CopilotService()
