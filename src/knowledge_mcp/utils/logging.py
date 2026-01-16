# src/knowledge_mcp/utils/logging.py
"""
Structured logging configuration for Knowledge MCP.

This module provides logging setup with support for both JSON-structured
output (for production log aggregation) and human-readable output
(for development). Includes security filtering to prevent credential leakage.

Example:
    >>> from knowledge_mcp.utils.logging import setup_logging, get_logger
    >>> setup_logging(level="DEBUG", json_format=False)
    >>> logger = get_logger(__name__)
    >>> logger.info("Processing document", extra={"doc_id": "123"})

Environment Variables:
    LOG_LEVEL: Sets the logging level (DEBUG, INFO, WARNING, ERROR).
               Defaults to INFO if not set.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any

# Patterns that indicate sensitive values to redact
_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    # API keys - common formats
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),  # OpenAI keys
    re.compile(r"[a-zA-Z0-9_-]{32,}", re.IGNORECASE),  # Generic long tokens
    # Environment variable values that look like secrets
    re.compile(r"(?:api[_-]?key|secret|token|password|credential)[s]?\s*[:=]\s*['\"]?([^'\"\s]+)", re.IGNORECASE),
)

# Keys to always redact in extra fields
_SENSITIVE_KEYS: frozenset[str] = frozenset({
    "api_key",
    "apikey",
    "api-key",
    "secret",
    "password",
    "token",
    "credential",
    "auth",
    "authorization",
    "openai_api_key",
    "qdrant_api_key",
})

REDACTED_VALUE: str = "***REDACTED***"


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that redacts sensitive data from log messages and extras.

    This filter prevents accidental logging of API keys, tokens, passwords,
    and other sensitive values per security.md §7.2.

    Example:
        >>> filter = SensitiveDataFilter()
        >>> record = logging.LogRecord(...)
        >>> record.msg = "Key is sk-abcd1234..."
        >>> filter.filter(record)
        True
        >>> "REDACTED" in record.msg
        True
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and redact sensitive data from a log record.

        Args:
            record: The log record to filter.

        Returns:
            Always True (never drops records, only redacts content).
        """
        # Redact message content
        if record.msg:
            record.msg = self._redact_string(str(record.msg))

        # Redact args if present
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._redact_value(k, v) for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self._redact_string(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        return True

    def _redact_string(self, text: str) -> str:
        """Redact sensitive patterns from a string."""
        result = text
        for pattern in _SENSITIVE_PATTERNS:
            result = pattern.sub(REDACTED_VALUE, result)
        return result

    def _redact_value(self, key: str, value: Any) -> Any:
        """Redact a value if the key indicates sensitivity."""
        key_lower = key.lower()
        if key_lower in _SENSITIVE_KEYS or any(
            sensitive in key_lower for sensitive in ("key", "secret", "token", "password")
        ):
            return REDACTED_VALUE
        if isinstance(value, str):
            return self._redact_string(value)
        return value


class JSONFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging in production.

    Produces one JSON object per line with timestamp, level, message,
    module, and any extra fields.

    Example Output:
        {"timestamp": "2024-01-15T10:30:00Z", "level": "INFO", ...}
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            JSON string representation of the log record.
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (skip standard LogRecord attributes)
        standard_attrs = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs",
            "pathname", "process", "processName", "relativeCreated",
            "stack_info", "exc_info", "exc_text", "thread", "threadName",
            "taskName", "message",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data, default=str)


class HumanFormatter(logging.Formatter):
    """
    Human-readable log formatter for development.

    Produces colorized, easy-to-read log output for terminal viewing.

    Example Output:
        2024-01-15 10:30:00 | INFO     | module:func:42 - Message here
    """

    # ANSI color codes
    COLORS: dict[str, str] = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record for human readability.

        Args:
            record: The log record to format.

        Returns:
            Formatted string with optional color codes.
        """
        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"] if color else ""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        location = f"{record.module}:{record.funcName}:{record.lineno}"
        message = record.getMessage()

        formatted = f"{timestamp} | {color}{record.levelname:<8}{reset} | {location} - {message}"

        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


def setup_logging(
    level: str | int | None = None,
    json_format: bool = False,
) -> logging.Logger:
    """
    Configure logging for Knowledge MCP.

    Sets up the root logger with appropriate formatter (JSON or human-readable)
    and applies the sensitive data filter to prevent credential leakage.

    Args:
        level: Logging level as string (DEBUG, INFO, WARNING, ERROR) or
               int constant. If None, reads from LOG_LEVEL env var,
               defaulting to INFO.
        json_format: If True, use JSON formatter for production.
                     If False, use human-readable formatter.

    Returns:
        The configured root logger.

    Example:
        >>> # Development mode
        >>> logger = setup_logging(level="DEBUG", json_format=False)
        >>> logger.info("Application started")

        >>> # Production mode
        >>> logger = setup_logging(json_format=True)
        >>> logger.info("Processing", extra={"request_id": "abc123"})
    """
    # Resolve level from parameter or environment
    resolved_level: int
    if level is None:
        level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
        resolved_level = getattr(logging, level_str, logging.INFO)
    elif isinstance(level, str):
        resolved_level = getattr(logging, level.upper(), logging.INFO)
    else:
        resolved_level = level

    # Get root logger for knowledge_mcp package
    logger = logging.getLogger("knowledge_mcp")
    logger.setLevel(resolved_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create handler with appropriate formatter
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(resolved_level)

    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(HumanFormatter())

    # Add sensitive data filter
    handler.addFilter(SensitiveDataFilter())

    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Creates a child logger of the knowledge_mcp logger,
    inheriting its configuration.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger instance.

    Example:
        >>> from knowledge_mcp.utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    # Ensure the name is under the knowledge_mcp namespace
    if not name.startswith("knowledge_mcp"):
        name = f"knowledge_mcp.{name}"
    return logging.getLogger(name)
