
from pathlib import Path

from backend.rag.config import KNOWLEDGE_BASE, SUPPORTED_EXTENSIONS
from backend.rag.rag_models import Document

from backend.logging_config import get_logger

logger = get_logger(__name__)

class DocumentLoader:
    """Discovers supported knowledge base documents."""
    def __init__(self, knowledge_base: Path = KNOWLEDGE_BASE):
        self.knowledge_base = knowledge_base
        logger.debug("DocumentLoader initialized path=%s", knowledge_base)
    def load_documents(self) -> list[Document]:
        """
        Scan the knowledge base and return supported documents.
        """
        logger.info("Scanning knowledge base: %s", self.knowledge_base)

        documents: list[Document] = []

        skipped = 0

        for path in self.knowledge_base.rglob("*"):

            if not path.is_file():
                continue
            if path.name.startswith("."):
                continue
            if not self._is_supported(path):
                skipped += 1
                logger.debug("Skipping unsupported file: %s", path.name)
                continue
            
            document = Document(
                file_name=path.name,
                file_path=path.resolve(),
                relative_path=str(path.relative_to(self.knowledge_base)),
                extension=path.suffix.lower(),
            )
            logger.debug(document.relative_path)

            documents.append(document)

            documents.sort(key=lambda doc: doc.relative_path)

            logger.info(
                "Loaded %d supported documents (%d skipped)",
                len(documents),
                skipped,
        )

        return documents

    def _is_supported(self, path: Path) -> bool:
        """
        Return True if the document extension is supported.
        """
        return path.suffix.lower() in SUPPORTED_EXTENSIONS