"""Token usage tracking for cost monitoring."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import tiktoken

if TYPE_CHECKING:
    pass


class TokenTracker:
    """
    Track OpenAI API token usage for cost visibility.

    Aggregates daily totals, logs to JSON file.
    Emits warnings when approaching budget threshold.

    Args:
        log_file: Path to JSON file for storing usage stats.
        embedding_model: Model name for tokenizer selection.
        daily_warning_threshold: Token count that triggers warning (default 1M).

    Example:
        >>> tracker = TokenTracker(Path("data/tokens.json"), "text-embedding-3-small")
        >>> tokens = tracker.track_embedding("Hello world", cache_hit=False)
        >>> summary = tracker.get_daily_summary()
        >>> cost = tracker.estimate_cost()
    """

    # OpenAI pricing per 1M tokens (text-embedding-3-small)
    COST_PER_MILLION_TOKENS = 0.020

    def __init__(
        self,
        log_file: Path,
        embedding_model: str = "text-embedding-3-small",
        daily_warning_threshold: int = 1_000_000,
    ) -> None:
        """Initialize tracker with log file and tokenizer."""
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.embedding_model = embedding_model
        self.daily_warning_threshold = daily_warning_threshold

        # Initialize tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(embedding_model)
        except KeyError:
            # Fallback for models not in tiktoken registry
            self.encoding = tiktoken.get_encoding("cl100k_base")

        # Load existing stats
        self.stats: dict[str, dict[str, int]] = self._load_stats()

    def _load_stats(self) -> dict[str, dict[str, int]]:
        """Load existing token stats from JSON."""
        if self.log_file.exists():
            with open(self.log_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_stats(self) -> None:
        """Persist stats to JSON."""
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

    def _get_today(self) -> str:
        """Get today's date as string key."""
        return str(date.today())

    def _ensure_today_entry(self) -> dict[str, int]:
        """Ensure today's entry exists and return it."""
        today = self._get_today()
        if today not in self.stats:
            self.stats[today] = {
                "embedding_tokens": 0,
                "embedding_requests": 0,
                "cache_hits": 0,
            }
        return self.stats[today]

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to tokenize.

        Returns:
            Number of tokens.
        """
        return len(self.encoding.encode(text))

    def track_embedding(self, text: str, cache_hit: bool = False) -> int:
        """
        Track embedding token usage.

        Args:
            text: Text being embedded.
            cache_hit: Whether embedding was served from cache.

        Returns:
            Token count for the text.
        """
        tokens = self.count_tokens(text)
        today_stats = self._ensure_today_entry()

        if cache_hit:
            today_stats["cache_hits"] += 1
        else:
            today_stats["embedding_tokens"] += tokens
            today_stats["embedding_requests"] += 1

        self._save_stats()

        # Check warning threshold
        if today_stats["embedding_tokens"] >= self.daily_warning_threshold:
            self._emit_warning(today_stats["embedding_tokens"])

        return tokens

    def _emit_warning(self, tokens: int) -> None:
        """Emit warning when approaching threshold."""
        import logging
        logger = logging.getLogger("knowledge_mcp.monitoring")
        cost = (tokens / 1_000_000) * self.COST_PER_MILLION_TOKENS
        logger.warning(
            f"Daily token usage high: {tokens:,} tokens (${cost:.4f}). "
            f"Threshold: {self.daily_warning_threshold:,}"
        )

    def get_daily_summary(self, day: str | None = None) -> dict[str, int]:
        """
        Get summary for specific day.

        Args:
            day: Date string (YYYY-MM-DD), defaults to today.

        Returns:
            Dict with embedding_tokens, embedding_requests, cache_hits.
        """
        day = day or self._get_today()
        return self.stats.get(day, {})

    def estimate_cost(self, day: str | None = None) -> float:
        """
        Estimate cost for a day.

        Args:
            day: Date string (YYYY-MM-DD), defaults to today.

        Returns:
            Estimated cost in USD.
        """
        summary = self.get_daily_summary(day)
        tokens = summary.get("embedding_tokens", 0)
        return (tokens / 1_000_000) * self.COST_PER_MILLION_TOKENS

    def get_all_days(self) -> list[str]:
        """Get list of all days with recorded usage."""
        return sorted(self.stats.keys(), reverse=True)
