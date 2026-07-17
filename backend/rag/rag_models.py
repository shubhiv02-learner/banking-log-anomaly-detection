from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Document:
    """
    Represents a knowledge base document as it progresses through
    the RAG ingestion pipeline.
    """

    # ---------- File Information ----------
    file_name: str
    file_path: Path
    relative_path: str
    extension: str

    # ---------- Metadata ----------
    document_type: str | None = None
    category: str | None = None
    service_name: str | None = None
    title: str | None = None
    tags: list[str] = field(default_factory=list)

    # ---------- Content ----------
    content: str | None = None

    # ---------- Future ----------
    chunks: list = field(default_factory=list)