"""
Central logging for SentinelIQ (backend, consumer, producer, src pipelines).

Initialize once via setup_logging(). Read LOG_LEVEL from the environment
(INFO | DEBUG | ERROR), default INFO.
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGING_INITIALIZED = False

_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "ERROR": logging.ERROR,
}


def _resolve_log_level() -> int:
    raw = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    level = _LEVEL_MAP.get(raw)
    if level is None:
        return logging.INFO
    return level


def setup_logging(log_file: str = "application.log") -> None:
    """Configure console and rotating file logging. Safe to call multiple times."""
    global _LOGGING_INITIALIZED
    if _LOGGING_INITIALIZED:
        return

    log_level = _resolve_log_level()
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    _LOGGING_INITIALIZED = True

    boot = logging.getLogger(__name__)
    boot.info("Logging initialized (LOG_LEVEL=%s)", os.getenv("LOG_LEVEL", "INFO"))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
