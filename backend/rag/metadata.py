from backend.rag.rag_models import Document
from backend.logging_config import get_logger
from backend.rag.config import (FOLDER_TO_DOCUMENT_TYPE, DEFAULT_DOCUMENT_TYPE)
from pathlib import Path

logger = get_logger(__name__)

# TO_DO: Phase 2
# In a future version, if Markdown front matter exists,
# use it as the authoritative metadata source.
# Otherwise, derive metadata from the directory structure.

class MetadataExtractor:
    """
    Extracts metadata from document paths and filenames.
    """

    def extract_metadata(
        self,
        documents: list[Document],
    ) -> list[Document]:

        logger.info("Extracting metadata from %d documents", len(documents))

        for document in documents:
            self._populate_metadata(document)

        logger.info("Metadata extraction completed")

        return documents

    def _populate_metadata(
        self,
        document: Document,
    ) -> None:

        parts = Path(document.relative_path).parts

        self._extract_category(document, parts)
        self._extract_document_type(document)
        self._extract_service_name(document, parts)
        self._extract_title(document)

    def _extract_category(
        self,
        document: Document,
        parts: tuple[str, ...],
    ) -> None:

        if parts:
            document.category = parts[0]

    def _extract_document_type(
        self,
        document: Document,
    ) -> None:

        document.document_type = FOLDER_TO_DOCUMENT_TYPE.get(
            document.category,
            DEFAULT_DOCUMENT_TYPE,
        )

    def _extract_service_name(
        self,
        document: Document,
        parts: tuple[str, ...],
    ) -> None:

        if len(parts) >= 3:
            document.service_name = parts[1]

    def _extract_title(
        self,
        document: Document,
    ) -> None:

        document.title = (
            Path(document.file_name)
            .stem
            .replace("_", " ")
            .replace("-", " ")
            .title()
        )