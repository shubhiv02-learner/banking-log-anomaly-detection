"""HTTP client for Salveris knowledge APIs.

Does NOT resolve acting principal — callers must pass acting_principal_id.
Service credentials come from SalverisSettings (calling platform / service principal / secret).

Contract (Salveris inbound):
  POST /v1/knowledge/search
  POST /v1/knowledge/answer
  Headers: Authorization Bearer, X-Salveris-Calling-Platform-Id,
           X-Salveris-Service-Principal-Id, X-Salveris-Acting-Principal-Id
  Body: { "query": str, "as_of"?: datetime }  — extra fields are forbidden
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from backend.integrations.salveris.exceptions import (
    SalverisAuthError,
    SalverisError,
    SalverisUnavailable,
)
from backend.integrations.salveris.models import (
    CopilotAskResponse,
    CopilotCloseResponse,
    CopilotContext,
    CopilotSearchResponse,
    EvidenceHit,
    SourceRef,
)
from backend.integrations.salveris.settings import SalverisSettings
from backend.logging_config import get_logger

_logger = get_logger(__name__)

CAPABILITY_KNOWLEDGE_SEARCH = "KNOWLEDGE_SEARCH"
CAPABILITY_KNOWLEDGE_ANSWER = "KNOWLEDGE_ANSWER"
HEADER_CALLER_PROFILE = "X-Salveris-Caller-Profile"
DEFAULT_CALLER_PROFILE = "sentryyiq"


class SalverisClient:
    def __init__(self, settings: SalverisSettings):
        self._settings = settings

    def _service_headers(self, acting_principal_id: str) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self._settings.client_secret}",
            "X-Salveris-Calling-Platform-Id": self._settings.calling_platform_id,
            "X-Salveris-Service-Principal-Id": self._settings.service_principal_id,
            "X-Salveris-Acting-Principal-Id": acting_principal_id,
            HEADER_CALLER_PROFILE: DEFAULT_CALLER_PROFILE,
        }

    def _build_body(
        self,
        query: str,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query}
        if conversation_id:
            body["conversation_id"] = conversation_id
        return body

    def _log_outbound_identity(
        self,
        *,
        capability: str,
        path: str,
        headers: dict[str, str],
        query_len: int,
    ) -> None:
        """Log outbound IDs at INFO; compare with seed/config at DEBUG. Never log the secret."""
        sent_platform = headers.get("X-Salveris-Calling-Platform-Id", "")
        sent_service = headers.get("X-Salveris-Service-Principal-Id", "")
        sent_acting = headers.get("X-Salveris-Acting-Principal-Id", "")
        _logger.info(
            "Salveris outbound call started (capability='%s', "
            "calling_platform_id='%s', service_principal_id='%s', "
            "acting_principal_id='%s')",
            capability,
            sent_platform,
            sent_service,
            sent_acting,
        )
        _logger.debug(
            "Salveris outbound identity compared with config (path='%s', "
            "query_len=%d, config_calling_platform_id='%s', "
            "config_service_principal_id='%s', "
            "config_default_acting_principal_id='%s', platform_id_match=%s, "
            "service_principal_id_match=%s, acting_principal_id_match=%s, "
            "client_secret_configured=%s, authorization_header_set=%s)",
            path,
            query_len,
            self._settings.calling_platform_id,
            self._settings.service_principal_id,
            self._settings.default_acting_principal_id,
            sent_platform == self._settings.calling_platform_id,
            sent_service == self._settings.service_principal_id,
            sent_acting == self._settings.default_acting_principal_id,
            bool(self._settings.client_secret),
            bool(headers.get("Authorization")),
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        acting_principal_id: str,
        json_body: dict[str, Any],
        capability: str,
    ) -> Any:
        url = f"{self._settings.base_url}{path}"
        headers = self._service_headers(acting_principal_id)
        query = json_body.get("query")
        query_len = len(query) if isinstance(query, str) else 0
        self._log_outbound_identity(
            capability=capability,
            path=path,
            headers=headers,
            query_len=query_len,
        )
        try:
            with httpx.Client(timeout=self._settings.timeout_seconds) as client:
                response = client.request(
                    method,
                    url,
                    headers=headers,
                    json=json_body,
                )
        except httpx.TimeoutException as exc:
            message = (
                f"Salveris timed out calling {path} (capability='{capability}', "
                f"acting_principal_id='{acting_principal_id}')."
            )
            _logger.error(message, exc_info=True)
            raise SalverisUnavailable(message) from exc
        except httpx.RequestError as exc:
            message = (
                f"Salveris unreachable calling {path} (capability='{capability}', "
                f"acting_principal_id='{acting_principal_id}')."
            )
            _logger.error(message, exc_info=True)
            raise SalverisUnavailable(message) from exc

        if response.status_code in (401, 403):
            _logger.error(
                "Salveris authentication failed (capability='%s', path='%s', "
                "status=%d, calling_platform_id='%s', service_principal_id='%s', "
                "acting_principal_id='%s')",
                capability,
                path,
                response.status_code,
                self._settings.calling_platform_id,
                self._settings.service_principal_id,
                acting_principal_id,
            )
            raise SalverisAuthError(
                f"Salveris auth failed ({response.status_code})",
                status_code=response.status_code,
            )

        if response.status_code >= 500:
            _logger.error(
                "Salveris server error (capability='%s', path='%s', status=%d)",
                capability,
                path,
                response.status_code,
            )
            raise SalverisUnavailable(
                f"Salveris server error ({response.status_code})",
                status_code=response.status_code,
            )

        if response.status_code >= 400:
            detail = response.text[:500]
            _logger.error(
                "Salveris request failed (capability='%s', path='%s', "
                "status=%d, body='%s')",
                capability,
                path,
                response.status_code,
                detail,
            )
            raise SalverisError(
                f"Salveris error ({response.status_code}): {detail}",
                status_code=response.status_code,
            )

        _logger.debug(
            "Salveris response received (capability='%s', path='%s', status=%d)",
            capability,
            path,
            response.status_code,
        )
        if not response.content:
            return {}
        return response.json()

    def search(
        self,
        query: str,
        *,
        acting_principal_id: str,
        context: Optional[CopilotContext] = None,
    ) -> CopilotSearchResponse:
        if not acting_principal_id:
            message = "acting_principal_id is required."
            _logger.error(message)
            raise SalverisError(message)
        _ = context  # Salveris body forbids extra fields; context stays SentryyIQ-only.

        raw = self._request(
            "POST",
            "/v1/knowledge/search",
            acting_principal_id=acting_principal_id,
            json_body=self._build_body(query),
            capability=CAPABILITY_KNOWLEDGE_SEARCH,
        )
        result = self._normalize_search(raw)
        _logger.info(
            "Salveris knowledge search completed (%d hit(s))",
            len(result.hits),
        )
        return result

    def answer(
        self,
        query: str,
        *,
        acting_principal_id: str,
        context: Optional[CopilotContext] = None,
        conversation_id: str | None = None,
    ) -> CopilotAskResponse:
        if not acting_principal_id:
            message = "acting_principal_id is required."
            _logger.error(message)
            raise SalverisError(message)
        _ = context  # Salveris body forbids unknown extras; context stays local.

        raw = self._request(
            "POST",
            "/v1/knowledge/answer",
            acting_principal_id=acting_principal_id,
            json_body=self._build_body(query, conversation_id=conversation_id),
            capability=CAPABILITY_KNOWLEDGE_ANSWER,
        )
        result = self._normalize_answer(raw)
        _logger.info(
            "Salveris knowledge answer completed (%d source(s))",
            len(result.sources),
        )
        return result

    def close_conversation(
        self,
        conversation_id: str,
        *,
        acting_principal_id: str,
    ) -> CopilotCloseResponse:
        if not acting_principal_id:
            message = "acting_principal_id is required."
            _logger.error(message)
            raise SalverisError(message)
        if not conversation_id:
            message = "conversation_id is required."
            _logger.error(message)
            raise SalverisError(message)
        path = f"/v1/conversations/{conversation_id}/close"
        raw = self._request(
            "POST",
            path,
            acting_principal_id=acting_principal_id,
            json_body={},
            capability=CAPABILITY_KNOWLEDGE_ANSWER,
        )
        if not isinstance(raw, dict):
            return CopilotCloseResponse(
                conversation_id=conversation_id,
                status="CLOSED",
            )
        return CopilotCloseResponse(
            conversation_id=str(raw.get("conversation_id") or conversation_id),
            status=str(raw.get("status") or "CLOSED"),
        )

    @staticmethod
    def _normalize_search(raw: Any) -> CopilotSearchResponse:
        if not isinstance(raw, dict):
            _logger.debug(
                "Salveris search response was not a JSON object (type='%s')",
                type(raw).__name__,
            )
            return CopilotSearchResponse(hits=[])

        items = raw.get("search_results") or raw.get("hits") or raw.get("results") or []
        hits: list[EvidenceHit] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            title = (
                item.get("content_title")
                or item.get("title")
                or item.get("document_title")
                or item.get("name")
                or "Untitled"
            )
            document_id = item.get("document_id")
            hits.append(
                EvidenceHit(
                    title=str(title),
                    snippet=(
                        item.get("chunk_text")
                        or item.get("snippet")
                        or item.get("content")
                        or item.get("text")
                    ),
                    score=(
                        item.get("rerank_score")
                        or item.get("hybrid_score")
                        or item.get("score")
                        or item.get("relevance")
                    ),
                    source=item.get("content_reference") or item.get("source"),
                    document_id=str(document_id) if document_id is not None else None,
                )
            )
        return CopilotSearchResponse(hits=hits)

    @staticmethod
    def _normalize_answer(raw: Any) -> CopilotAskResponse:
        if not isinstance(raw, dict):
            _logger.debug(
                "Salveris answer response was not a JSON object (type='%s')",
                type(raw).__name__,
            )
            return CopilotAskResponse(answer=str(raw), confidence=None, sources=[])

        answer = (
            raw.get("answer")
            or raw.get("response")
            or raw.get("text")
            or ""
        )
        confidence_raw = raw.get("confidence") or raw.get("confidence_level")
        confidence_rationale = None
        if isinstance(confidence_raw, dict):
            confidence = confidence_raw.get("level")
            rationale_raw = confidence_raw.get("rationale")
            if rationale_raw is not None and str(rationale_raw).strip():
                confidence_rationale = str(rationale_raw).strip()
        else:
            confidence = confidence_raw
        if confidence is not None:
            confidence = str(confidence)

        source_items = raw.get("citations") or raw.get("sources") or raw.get("hits") or []
        sources: list[SourceRef] = []
        for item in source_items:
            if not isinstance(item, dict):
                continue
            title = (
                item.get("content_title")
                or item.get("title")
                or item.get("document_title")
                or item.get("name")
            )
            if not title:
                continue
            sources.append(
                SourceRef(
                    title=str(title),
                    snippet=item.get("quote") or item.get("snippet") or item.get("content"),
                    source=item.get("content_reference") or item.get("source"),
                )
            )

        return CopilotAskResponse(
            answer=str(answer),
            confidence=confidence,
            confidence_rationale=confidence_rationale,
            sources=sources,
            conversation_id=(
                str(raw["conversation_id"])
                if raw.get("conversation_id") is not None
                else None
            ),
            investigation_session_id=(
                str(raw["investigation_session_id"])
                if raw.get("investigation_session_id") is not None
                else None
            ),
        )
