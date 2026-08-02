from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DocumentInfo:
    """
    Represents a discovered document.

    Metadata extraction happens later.
    """

    file_name: str
    file_path: Path
    relative_path: str
    extension: str