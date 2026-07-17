from backend.rag.loader import DocumentLoader
from backend.rag.metadata import MetadataExtractor

from backend.logging_config import setup_logging, get_logger

setup_logging()

logger = get_logger(__name__)

logger.info("Starting Document Loader Test")

def main():
    loader = DocumentLoader()

    documents = loader.load_documents()

    logger.info("Documents discovered: %d", len(documents))

    for document in documents:
        logger.info("%s", document)

    logger.info("Document Loader Test Completed")
    logger.info("Verifying documents were loaded")

    assert len(documents) > 0, "No documents found in knowledge base"

    logger.info("Verification successful")
    extractor = MetadataExtractor()

    documents = extractor.extract_metadata(documents)

    logger.info("-" * 80)

    for document in documents:

        logger.info(
            "%s | %s | %s | %s",
            document.document_type,
            document.service_name,
            document.title,
            document.relative_path,
        )

    logger.info("-" * 80)

if __name__ == "__main__":
    main()