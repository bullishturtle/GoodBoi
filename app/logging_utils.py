"""Central logging configuration for GoodBoy.AI.

This module provides a get_logger() helper that returns a module-scoped logger
with consistent formatting and both console + file handlers.

Usage:
    from .logging_utils import get_logger
    log = get_logger(__name__)
    log.info("Something happened", extra={"context": "details"})
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .config import ROOT

_LOGGER_CACHE: dict[str, logging.Logger] = {}


def _ensure_log_dir() -> Path:
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def configure_root_logger(level: int = logging.INFO) -> None:
    """Idempotently configure the root logger.

    This avoids re-adding handlers if called multiple times (e.g. in tests
    and scripts).
    """

    if getattr(configure_root_logger, "_configured", False):  # type: ignore[attr-defined]
        return

    logging.basicConfig(level=level)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    log_dir = _ensure_log_dir()
    file_handler = RotatingFileHandler(
        log_dir / "goodboy_core.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Ensure at least one console handler with same format
    has_console = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    if not has_console:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root_logger.addHandler(console)

    setattr(configure_root_logger, "_configured", True)  # type: ignore[attr-defined]


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger configured with GoodBoy.AI defaults."""

    configure_root_logger()
    key = name or "goodboy"
    if key in _LOGGER_CACHE:
        return _LOGGER_CACHE[key]
    logger = logging.getLogger(key)
    _LOGGER_CACHE[key] = logger
    return logger
