from pathlib import Path

# Project structure
BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = BACKEND_ROOT / "data"
KNOWLEDGE_BASE = DATA_ROOT / "knowledgebase"

FOLDER_TO_DOCUMENT_TYPE = {
    "runbooks": "runbook",
    "architecture": "architecture",
    "system_design": "system_design",
    "error_catalog": "error_catalog",
    "sla": "sla",
    "operations": "operations",
    "service_docs": "service_doc",
    "resolutions": "resolution",
    "faq":"faq"
}

DEFAULT_DOCUMENT_TYPE = "general"

# Supported document formats
SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt",
}

# Chunking (used later)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Embedding model (used later)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Vector search
TOP_K = 5