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
    CopilotContext,
    CopilotSearchResponse,
    EvidenceHit,
    SourceRef,
)
from backend.integrations.salveris.settings import SalverisSettings
from backend.logging_config import get_logger

logger = get_logger(__name__)


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
        }

    def _build_body(self, query: str) -> dict[str, Any]:
        # KnowledgeSearch/AnswerRequestModel: extra="forbid" — query only.
        return {"query": query}

    def _request(
        self,
        method: str,
        path: str,
        *,
        acting_principal_id: str,
        json_body: dict[str, Any],
    ) -> Any:
        url = f"{self._settings.base_url}{path}"
        try:
            with httpx.Client(timeout=self._settings.timeout_seconds) as client:
                response = client.request(
                    method,
                    url,
                    headers=self._service_headers(acting_principal_id),
                    json=json_body,
                )
        except httpx.TimeoutException as exc:
            logger.error("Salveris timeout path=%s", path)
            raise SalverisUnavailable(f"Salveris timed out calling {path}") from exc
        except httpx.RequestError as exc:
            logger.error("Salveris unreachable path=%s error=%s", path, exc)
            raise SalverisUnavailable(f"Salveris unreachable: {exc}") from exc

        if response.status_code in (401, 403):
            logger.error(
                "Salveris auth failed path=%s status=%s",
                path,
                response.status_code,
            )
            raise SalverisAuthError(
                f"Salveris auth failed ({response.status_code})",
                status_code=response.status_code,
            )

        if response.status_code >= 500:
            logger.error(
                "Salveris server error path=%s status=%s",
                path,
                response.status_code,
            )
            raise SalverisUnavailable(
                f"Salveris server error ({response.status_code})",
                status_code=response.status_code,
            )

        if response.status_code >= 400:
            detail = response.text[:500]
            logger.error(
                "Salveris client error path=%s status=%s body=%s",
                path,
                response.status_code,
                detail,
            )
            raise SalverisError(
                f"Salveris error ({response.status_code}): {detail}",
                status_code=response.status_code,
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
            raise SalverisError("acting_principal_id is required")
        _ = context  # Salveris body forbids extra fields; context stays SentryyIQ-only.

        raw = self._request(
            "POST",
            "/v1/knowledge/search",
            acting_principal_id=acting_principal_id,
            json_body=self._build_body(query),
        )
        return self._normalize_search(raw)

    def answer(
        self,
        query: str,
        *,
        acting_principal_id: str,
        context: Optional[CopilotContext] = None,
    ) -> CopilotAskResponse:
        if not acting_principal_id:
            raise SalverisError("acting_principal_id is required")
        _ = context  # Salveris body forbids extra fields; context stays SentryyIQ-only.

        raw = self._request(
            "POST",
            "/v1/knowledge/answer",
            acting_principal_id=acting_principal_id,
            json_body=self._build_body(query),
        )
        return self._normalize_answer(raw)

    @staticmethod
    def _normalize_search(raw: Any) -> CopilotSearchResponse:
        if not isinstance(raw, dict):
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
            return CopilotAskResponse(answer=str(raw), confidence=None, sources=[])

        answer = (
            raw.get("answer")
            or raw.get("response")
            or raw.get("text")
            or ""
        )
        confidence_raw = raw.get("confidence") or raw.get("confidence_level")
        if isinstance(confidence_raw, dict):
            confidence = confidence_raw.get("level")
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
            sources=sources,
        )
