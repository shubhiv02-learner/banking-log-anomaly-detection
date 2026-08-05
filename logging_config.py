"""
Central logging for SentinelIQ (backend, consumer, producer, src pipelines).

Initialize once via setup_logging(). Read LOG_LEVEL from the environment
(INFO | DEBUG | ERROR), default INFO.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGING_INITIALIZED = False

_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "ERROR": logging.ERROR,
}

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


class SafeRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that tolerates Windows rename/lock failures on rollover."""

    def doRollover(self) -> None:
        try:
            super().doRollover()
        except OSError:
            # WinError 32 / PermissionError when another handle still holds the file.
            # Continue logging to the current file rather than crashing emit().
            if self.stream is None:
                self.stream = self._open()


def _resolve_log_level() -> int:
    raw = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    level = _LEVEL_MAP.get(raw)
    if level is None:
        return logging.INFO
    return level


def _process_label() -> str:
    """Short label for this process (script stem, else process name)."""
    argv0 = sys.argv[0] if sys.argv and sys.argv[0] else ""
    label = Path(argv0).stem if argv0 else ""
    # `-c` / flag-like argv0 is not a useful stem on Windows or interactive runs.
    if not label or label.startswith("-"):
        try:
            import multiprocessing

            label = multiprocessing.current_process().name
        except Exception:
            label = "process"
    label = _SAFE_NAME.sub("_", label).strip("._") or "process"
    return label


def _process_log_filename(base_name: str = "application.log") -> str:
    """Per-process log name under logs/ to avoid cross-process Windows file locks."""
    base = Path(base_name)
    stem = base.stem or "application"
    suffix = base.suffix or ".log"
    return f"{stem}-{_process_label()}-{os.getpid()}{suffix}"


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

    resolved_name = _process_log_filename(log_file)
    file_handler = SafeRotatingFileHandler(
        log_dir / resolved_name,
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
    boot.info(
        "Logging initialized (LOG_LEVEL=%s, file=%s)",
        os.getenv("LOG_LEVEL", "INFO"),
        resolved_name,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
