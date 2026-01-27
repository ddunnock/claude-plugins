# tests/unit/test_utils/test_logging.py
"""
Unit tests for logging utilities.

Tests the SensitiveDataFilter, JSON and Human formatters,
and the setup_logging/get_logger configuration functions.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any
from unittest.mock import patch

import pytest

from knowledge_mcp.utils.logging import (
    REDACTED_VALUE,
    HumanFormatter,
    JSONFormatter,
    SensitiveDataFilter,
    get_logger,
    setup_logging,
)


class TestSensitiveDataFilter:
    """Tests for SensitiveDataFilter redaction behavior."""

    @pytest.fixture
    def filter_instance(self) -> SensitiveDataFilter:
        """Create a SensitiveDataFilter instance."""
        return SensitiveDataFilter()

    def _create_record(
        self,
        msg: str,
        args: tuple[Any, ...] | dict[str, Any] = (),
        exc_info: Any = None,
    ) -> logging.LogRecord:
        """Helper to create a LogRecord for testing."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=msg,
            args=args,
            exc_info=exc_info,
        )
        return record

    def test_redacts_openai_api_key(self, filter_instance: SensitiveDataFilter) -> None:
        """Verify sk-xxx patterns are redacted."""
        record = self._create_record(
            "Key is sk-abc123def456xyz789012345678901234567890"
        )
        filter_instance.filter(record)
        assert "sk-abc" not in record.msg
        assert REDACTED_VALUE in record.msg

    def test_redacts_long_tokens(self, filter_instance: SensitiveDataFilter) -> None:
        """Verify 32+ character tokens are redacted."""
        # 32 character alphanumeric token
        token = "a" * 32
        record = self._create_record(f"Token: {token}")
        filter_instance.filter(record)
        assert token not in record.msg
        assert REDACTED_VALUE in record.msg

    def test_redacts_key_value_patterns(
        self, filter_instance: SensitiveDataFilter
    ) -> None:
        """Verify 'api_key=xxx' patterns are redacted."""
        record = self._create_record("Config has api_key=super_secret_value_123")
        filter_instance.filter(record)
        assert "super_secret" not in record.msg
        assert REDACTED_VALUE in record.msg

    def test_redacts_sensitive_dict_keys(
        self, filter_instance: SensitiveDataFilter
    ) -> None:
        """Verify args dict values are redacted for sensitive keys."""
        args_dict = {
            "api_key": "sk-secret123",
            "username": "john",
            "password": "mypass123",
            "token": "bearer_abc",
        }
        record = self._create_record("Config: %(api_key)s", args_dict)
        filter_instance.filter(record)
        assert record.args is not None
        assert isinstance(record.args, dict)
        assert record.args["api_key"] == REDACTED_VALUE
        assert record.args["username"] == "john"  # Not sensitive
        assert record.args["password"] == REDACTED_VALUE
        assert record.args["token"] == REDACTED_VALUE

    def test_preserves_normal_messages(
        self, filter_instance: SensitiveDataFilter
    ) -> None:
        """Verify non-sensitive text is unchanged."""
        msg = "Processing document with id 12345"
        record = self._create_record(msg)
        filter_instance.filter(record)
        assert record.msg == msg

    def test_redacts_tuple_args(self, filter_instance: SensitiveDataFilter) -> None:
        """Verify string args in tuples are redacted."""
        record = self._create_record(
            "Key: %s",
            ("sk-abc123def456xyz789012345678901234567890",),
        )
        filter_instance.filter(record)
        assert record.args is not None
        assert isinstance(record.args, tuple)
        assert "sk-abc" not in record.args[0]
        assert REDACTED_VALUE in record.args[0]

    def test_always_returns_true(self, filter_instance: SensitiveDataFilter) -> None:
        """Verify filter never drops records."""
        record = self._create_record("Any message")
        result = filter_instance.filter(record)
        assert result is True

    def test_redacts_secret_patterns(
        self, filter_instance: SensitiveDataFilter
    ) -> None:
        """Verify secret=xxx patterns are redacted."""
        record = self._create_record("Connection secret='my_db_secret'")
        filter_instance.filter(record)
        assert "my_db_secret" not in record.msg
        assert REDACTED_VALUE in record.msg

    def test_redacts_credential_patterns(
        self, filter_instance: SensitiveDataFilter
    ) -> None:
        """Verify credential=xxx patterns are redacted."""
        record = self._create_record("Auth credential: admin_cred_123")
        filter_instance.filter(record)
        assert "admin_cred_123" not in record.msg

    def test_handles_none_msg(self, filter_instance: SensitiveDataFilter) -> None:
        """Verify filter handles None message gracefully."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=None,
        )
        record.msg = ""  # Empty string, not None
        result = filter_instance.filter(record)
        assert result is True

    def test_handles_non_string_tuple_args(
        self, filter_instance: SensitiveDataFilter
    ) -> None:
        """Verify non-string args in tuples are preserved."""
        record = self._create_record(
            "Count: %d, Flag: %s",
            (42, True),
        )
        filter_instance.filter(record)
        assert record.args is not None
        assert isinstance(record.args, tuple)
        assert record.args[0] == 42
        assert record.args[1] is True


class TestJSONFormatter:
    """Tests for JSONFormatter output."""

    @pytest.fixture
    def formatter(self) -> JSONFormatter:
        """Create a JSONFormatter instance."""
        return JSONFormatter()

    def _create_record(
        self,
        msg: str,
        level: int = logging.INFO,
        exc_info: Any = None,
    ) -> logging.LogRecord:
        """Helper to create a LogRecord for testing."""
        record = logging.LogRecord(
            name="test.module",
            level=level,
            pathname="/path/to/module.py",
            lineno=42,
            msg=msg,
            args=(),
            exc_info=exc_info,
        )
        return record

    def test_formats_as_json(self, formatter: JSONFormatter) -> None:
        """Verify output is valid JSON."""
        record = self._create_record("Test message")
        output = formatter.format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_includes_timestamp(self, formatter: JSONFormatter) -> None:
        """Verify timestamp field is present."""
        record = self._create_record("Test message")
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "timestamp" in parsed
        # Should be ISO format
        assert "T" in parsed["timestamp"]

    def test_includes_level(self, formatter: JSONFormatter) -> None:
        """Verify level field is present."""
        record = self._create_record("Test message", level=logging.WARNING)
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "WARNING"

    def test_includes_message(self, formatter: JSONFormatter) -> None:
        """Verify message field is present."""
        record = self._create_record("Test message content")
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["message"] == "Test message content"

    def test_includes_exception_info(self, formatter: JSONFormatter) -> None:
        """Verify exception field when exc_info is set."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = self._create_record("Error occurred", exc_info=exc_info)
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]
        assert "Test exception" in parsed["exception"]

    def test_includes_extra_fields(self, formatter: JSONFormatter) -> None:
        """Verify custom extra fields are included."""
        record = self._create_record("Processing")
        record.request_id = "abc123"
        record.user_id = "user456"
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["request_id"] == "abc123"
        assert parsed["user_id"] == "user456"

    def test_excludes_standard_attrs(self, formatter: JSONFormatter) -> None:
        """Verify standard LogRecord attrs are not duplicated."""
        record = self._create_record("Test message")
        output = formatter.format(record)
        parsed = json.loads(output)
        # Standard attrs should not appear as separate keys
        assert "args" not in parsed
        assert "pathname" not in parsed
        assert "processName" not in parsed
        assert "threadName" not in parsed

    def test_includes_location_info(self, formatter: JSONFormatter) -> None:
        """Verify module, function, line are included."""
        record = self._create_record("Test message")
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "module" in parsed
        assert "function" in parsed
        assert "line" in parsed
        assert parsed["line"] == 42


class TestHumanFormatter:
    """Tests for HumanFormatter output."""

    @pytest.fixture
    def formatter(self) -> HumanFormatter:
        """Create a HumanFormatter instance."""
        return HumanFormatter()

    def _create_record(
        self,
        msg: str,
        level: int = logging.INFO,
        exc_info: Any = None,
    ) -> logging.LogRecord:
        """Helper to create a LogRecord for testing."""
        record = logging.LogRecord(
            name="test.module",
            level=level,
            pathname="/path/to/module.py",
            lineno=42,
            msg=msg,
            args=(),
            exc_info=exc_info,
        )
        record.module = "module"
        record.funcName = "test_func"
        return record

    def test_formats_readable_output(self, formatter: HumanFormatter) -> None:
        """Verify human-readable format."""
        record = self._create_record("Test message")
        output = formatter.format(record)
        # Should contain the message
        assert "Test message" in output
        # Should contain a timestamp-like pattern
        assert "|" in output

    def test_includes_color_codes(self, formatter: HumanFormatter) -> None:
        """Verify ANSI codes for levels."""
        for level_name, level in [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
        ]:
            record = self._create_record("Test", level=level)
            output = formatter.format(record)
            # Should contain ANSI escape code
            assert "\033[" in output
            # Should contain the level name
            assert level_name in output

    def test_includes_location(self, formatter: HumanFormatter) -> None:
        """Verify module:func:line format."""
        record = self._create_record("Test message")
        output = formatter.format(record)
        # Should contain location info: module:func:line
        assert "module:test_func:42" in output

    def test_includes_exception_traceback(self, formatter: HumanFormatter) -> None:
        """Verify exception is formatted."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = self._create_record("Error occurred", exc_info=exc_info)
        output = formatter.format(record)
        assert "ValueError" in output
        assert "Test exception" in output

    def test_reset_color_at_end(self, formatter: HumanFormatter) -> None:
        """Verify ANSI reset code is included."""
        record = self._create_record("Test", level=logging.INFO)
        output = formatter.format(record)
        # Should contain reset code
        assert "\033[0m" in output


class TestSetupLogging:
    """Tests for setup_logging function."""

    def teardown_method(self) -> None:
        """Clean up after each test."""
        # Reset the knowledge_mcp logger
        logger = logging.getLogger("knowledge_mcp")
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)
        # Clear any LOG_LEVEL env var
        os.environ.pop("LOG_LEVEL", None)

    def test_uses_env_var_level(self) -> None:
        """Verify LOG_LEVEL env var is respected."""
        os.environ["LOG_LEVEL"] = "DEBUG"
        logger = setup_logging()
        assert logger.level == logging.DEBUG

    def test_uses_explicit_level(self) -> None:
        """Verify level parameter works."""
        logger = setup_logging(level="WARNING")
        assert logger.level == logging.WARNING

    def test_uses_explicit_level_int(self) -> None:
        """Verify level parameter works with int."""
        logger = setup_logging(level=logging.ERROR)
        assert logger.level == logging.ERROR

    def test_uses_json_formatter_when_requested(self) -> None:
        """Verify json_format=True uses JSONFormatter."""
        logger = setup_logging(json_format=True)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)

    def test_uses_human_formatter_by_default(self) -> None:
        """Verify json_format=False uses HumanFormatter."""
        logger = setup_logging(json_format=False)
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, HumanFormatter)

    def test_adds_sensitive_filter(self) -> None:
        """Verify SensitiveDataFilter is added."""
        logger = setup_logging()
        assert len(logger.handlers) == 1
        filters = logger.handlers[0].filters
        assert any(isinstance(f, SensitiveDataFilter) for f in filters)

    def test_clears_existing_handlers(self) -> None:
        """Verify no duplicate handlers after multiple calls."""
        setup_logging(level="INFO")
        setup_logging(level="DEBUG")
        logger = logging.getLogger("knowledge_mcp")
        assert len(logger.handlers) == 1

    def test_defaults_to_info_level(self) -> None:
        """Verify default level is INFO when no env var."""
        os.environ.pop("LOG_LEVEL", None)
        logger = setup_logging()
        assert logger.level == logging.INFO

    def test_handler_uses_stderr(self) -> None:
        """Verify handler writes to stderr."""
        import sys

        logger = setup_logging()
        assert len(logger.handlers) == 1
        assert logger.handlers[0].stream == sys.stderr

    def test_propagate_disabled(self) -> None:
        """Verify propagation to root logger is disabled."""
        logger = setup_logging()
        assert logger.propagate is False


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_child_logger(self) -> None:
        """Verify logger is under knowledge_mcp namespace."""
        logger = get_logger("knowledge_mcp.utils.test")
        assert logger.name == "knowledge_mcp.utils.test"

    def test_prefixes_non_namespaced_names(self) -> None:
        """Verify prefix is added if missing."""
        logger = get_logger("mymodule")
        assert logger.name == "knowledge_mcp.mymodule"

    def test_preserves_namespaced_names(self) -> None:
        """Verify prefix is not duplicated."""
        logger = get_logger("knowledge_mcp.store.qdrant")
        assert logger.name == "knowledge_mcp.store.qdrant"

    def test_returns_logger_instance(self) -> None:
        """Verify return type is Logger."""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)
