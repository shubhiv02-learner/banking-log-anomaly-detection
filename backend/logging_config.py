"""
Central logging configuration for the SentryyIQ backend.

This module configures application-wide logging and should be initialized
once during application startup.
"""

from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


_LOGGING_INITIALIZED = False


def setup_logging(
    log_level: int = logging.INFO,
    log_file: str = "application.log",
) -> None:
    """
    Configure console and rotating file logging.

    Safe to call multiple times.
    """

    global _LOGGING_INITIALIZED

    if _LOGGING_INITIALIZED:
        return

    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _LOGGING_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.
    """

    return logging.getLogger(name)