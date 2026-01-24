"""Structured JSON logging for production monitoring."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from pythonjsonlogger import jsonlogger

if TYPE_CHECKING:
    pass


def setup_json_logger(
    name: str,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure structured JSON logger.

    Output schema: timestamp (ISO 8601), level, name, message, plus extra fields.

    Args:
        name: Logger name (typically module path).
        level: Logging level (default INFO).

    Returns:
        Configured logger instance.

    Example:
        >>> logger = setup_json_logger("knowledge_mcp.search")
        >>> logger.info("Search completed", extra={"query": "test", "results": 5})
        # Output: {"timestamp":"2026-01-24T10:30:15","level":"INFO","name":"knowledge_mcp.search","message":"Search completed","query":"test","results":5}
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
            timestamp=True,
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
