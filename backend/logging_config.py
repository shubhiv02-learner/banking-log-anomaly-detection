"""Re-export root logging_config for backend imports and standalone backend deploys."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from logging_config import get_logger, setup_logging

__all__ = ["setup_logging", "get_logger"]
