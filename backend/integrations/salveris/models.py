"""SentryyIQ Copilot models. Salveris HTTP bodies are mapped in SalverisClient."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class CopilotContext(BaseModel):
    service: Optional[str] = None
    route: Optional[str] = None
    ticket_id: Optional[str] = None
    extra: dict[str, Any] = Field(default_factory=dict)


class CopilotSearchRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: Optional[CopilotContext] = None


class CopilotAskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: Optional[CopilotContext] = None


class EvidenceHit(BaseModel):
    title: str
    snippet: Optional[str] = None
    score: Optional[float] = None
    source: Optional[str] = None
    document_id: Optional[str] = None


class CopilotSearchResponse(BaseModel):
    hits: list[EvidenceHit] = Field(default_factory=list)


class SourceRef(BaseModel):
    title: str
    snippet: Optional[str] = None
    source: Optional[str] = None


class CopilotAskResponse(BaseModel):
    answer: str
    confidence: Optional[str] = None
    sources: list[SourceRef] = Field(default_factory=list)
