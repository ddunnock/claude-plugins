"""Unit tests for monitoring module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from knowledge_mcp.monitoring.token_tracker import TokenTracker
from knowledge_mcp.monitoring.logger import setup_json_logger


class TestTokenTracker:
    """Tests for TokenTracker class."""

    @pytest.fixture
    def log_file(self) -> Path:
        """Create temporary log file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            yield Path(f.name)

    @pytest.fixture
    def tracker(self, log_file: Path) -> TokenTracker:
        """Create tracker instance for testing."""
        return TokenTracker(log_file)

    def test_count_tokens(self, tracker: TokenTracker) -> None:
        """Test token counting with tiktoken."""
        # "Hello world" is typically 2 tokens
        count = tracker.count_tokens("Hello world")
        assert count > 0
        assert isinstance(count, int)

    def test_track_embedding_increments_counters(self, tracker: TokenTracker) -> None:
        """Test that tracking increments daily counters."""
        tracker.track_embedding("First text")
        tracker.track_embedding("Second text")

        summary = tracker.get_daily_summary()
        assert summary["embedding_requests"] == 2
        assert summary["embedding_tokens"] > 0

    def test_track_cache_hit_increments_cache_counter(self, tracker: TokenTracker) -> None:
        """Test that cache hits are tracked separately."""
        tracker.track_embedding("Cached text", cache_hit=True)
        tracker.track_embedding("API text", cache_hit=False)

        summary = tracker.get_daily_summary()
        assert summary["cache_hits"] == 1
        assert summary["embedding_requests"] == 1

    def test_estimate_cost(self, tracker: TokenTracker) -> None:
        """Test cost estimation."""
        # Track enough tokens to have measurable cost
        for _ in range(100):
            tracker.track_embedding("Test text for cost estimation")

        cost = tracker.estimate_cost()
        assert cost > 0
        assert cost < 1.0  # Should be small for test data

    def test_persistence(self, log_file: Path) -> None:
        """Test that stats persist across instances."""
        tracker1 = TokenTracker(log_file)
        tracker1.track_embedding("Persistent text")
        tokens_1 = tracker1.get_daily_summary()["embedding_tokens"]

        tracker2 = TokenTracker(log_file)
        tokens_2 = tracker2.get_daily_summary()["embedding_tokens"]

        assert tokens_2 == tokens_1

    def test_get_all_days(self, tracker: TokenTracker) -> None:
        """Test get_all_days returns tracked days."""
        tracker.track_embedding("Some text")
        days = tracker.get_all_days()

        assert len(days) >= 1
        assert all(isinstance(d, str) for d in days)

    def test_empty_summary_for_missing_day(self, tracker: TokenTracker) -> None:
        """Test that missing day returns empty dict."""
        summary = tracker.get_daily_summary("1900-01-01")
        assert summary == {}

    def test_json_file_created(self, log_file: Path, tracker: TokenTracker) -> None:
        """Test that JSON file is created on first track."""
        tracker.track_embedding("Test")
        assert log_file.exists()

        with open(log_file, encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict)

    def test_warning_threshold_triggers(self, log_file: Path, caplog: pytest.LogCaptureFixture) -> None:
        """Test that warning is emitted when threshold is exceeded."""
        tracker = TokenTracker(log_file, daily_warning_threshold=10)

        # Track enough to exceed threshold
        tracker.track_embedding("This is a longer text to exceed the small threshold")

        # Check if warning was logged
        assert any("Daily token usage high" in record.message for record in caplog.records)

    def test_cache_hit_does_not_increment_tokens(self, tracker: TokenTracker) -> None:
        """Test that cache hits don't increment token count."""
        tracker.track_embedding("Cached", cache_hit=True)

        summary = tracker.get_daily_summary()
        assert summary["embedding_tokens"] == 0
        assert summary["cache_hits"] == 1


class TestSetupJsonLogger:
    """Tests for structured JSON logger."""

    def test_logger_returns_logger_instance(self) -> None:
        """Test that setup returns a logger."""
        import logging
        logger = setup_json_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_logger_name_set(self) -> None:
        """Test that logger has correct name."""
        logger = setup_json_logger("knowledge_mcp.test")
        assert logger.name == "knowledge_mcp.test"

    def test_logger_level_configurable(self) -> None:
        """Test that logging level is configurable."""
        import logging
        logger = setup_json_logger("test.level", level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_no_duplicate_handlers(self) -> None:
        """Test that multiple calls don't add duplicate handlers."""
        logger1 = setup_json_logger("test.duplicate")
        handler_count_1 = len(logger1.handlers)

        logger2 = setup_json_logger("test.duplicate")
        handler_count_2 = len(logger2.handlers)

        assert handler_count_1 == handler_count_2
