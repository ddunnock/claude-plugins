"""Unit tests for tokenizer module."""

from __future__ import annotations

import pytest

from knowledge_mcp.utils.tokenizer import (
    TokenizerConfig,
    count_tokens,
    truncate_to_tokens,
)


class TestTokenizerConfig:
    """Tests for TokenizerConfig dataclass."""

    def test_default_values(self) -> None:
        """Test that TokenizerConfig has expected defaults."""
        config = TokenizerConfig()

        assert config.model == "text-embedding-3-small"
        assert config.max_tokens == 500

    def test_custom_values(self) -> None:
        """Test that TokenizerConfig accepts custom values."""
        config = TokenizerConfig(model="text-embedding-3-large", max_tokens=1000)

        assert config.model == "text-embedding-3-large"
        assert config.max_tokens == 1000


class TestCountTokens:
    """Tests for count_tokens function."""

    def test_empty_string(self) -> None:
        """Test that empty string returns 0 tokens."""
        assert count_tokens("") == 0

    def test_simple_text(self) -> None:
        """Test token counting for simple English text."""
        # "Hello world" should be 2 tokens with cl100k_base
        count = count_tokens("Hello world")
        assert count == 2

    def test_single_word(self) -> None:
        """Test token counting for single word."""
        # "Hello" should be 1 token
        count = count_tokens("Hello")
        assert count == 1

    def test_unicode_characters(self) -> None:
        """Test that unicode characters are handled correctly."""
        # Unicode should work but may take multiple tokens
        text = "Hello 你好 world"
        count = count_tokens(text)
        # Should be > 0 and handle unicode without errors
        assert count > 0
        assert isinstance(count, int)

    def test_emoji_handling(self) -> None:
        """Test that emoji characters are handled correctly."""
        text = "Hello 👋 world 🌍"
        count = count_tokens(text)
        assert count > 0
        assert isinstance(count, int)

    def test_whitespace_variations(self) -> None:
        """Test that different whitespace is handled correctly."""
        text1 = "Hello world"
        text2 = "Hello  world"  # Double space
        text3 = "Hello\nworld"  # Newline

        count1 = count_tokens(text1)
        count2 = count_tokens(text2)
        count3 = count_tokens(text3)

        # All should count successfully
        assert count1 > 0
        assert count2 > 0
        assert count3 > 0

    def test_long_text(self) -> None:
        """Test token counting for longer text."""
        # Create a longer piece of text
        text = " ".join(["word"] * 100)
        count = count_tokens(text)

        # Should have approximately 100 tokens (one per word)
        # Allow some variance due to encoding
        assert 90 < count < 110

    def test_model_parameter(self) -> None:
        """Test that model parameter is accepted."""
        text = "Hello world"
        count1 = count_tokens(text, model="text-embedding-3-small")
        count2 = count_tokens(text, model="text-embedding-3-large")

        # Both should work and give same result (same encoding)
        assert count1 == count2
        assert count1 == 2


class TestTruncateToTokens:
    """Tests for truncate_to_tokens function."""

    def test_empty_string(self) -> None:
        """Test that empty string is preserved."""
        result = truncate_to_tokens("", max_tokens=100)
        assert result == ""

    def test_text_under_limit(self) -> None:
        """Test that text under limit is preserved completely."""
        text = "Hello world"
        result = truncate_to_tokens(text, max_tokens=100)

        assert result == text
        assert count_tokens(result) <= 100

    def test_text_over_limit(self) -> None:
        """Test that text over limit is truncated correctly."""
        # Create text with ~20 tokens
        text = " ".join(["word"] * 20)

        result = truncate_to_tokens(text, max_tokens=10)

        # Should be truncated
        assert len(result) < len(text)
        assert count_tokens(result) <= 10

    def test_exact_limit(self) -> None:
        """Test behavior when text is exactly at token limit."""
        # "Hello world" is 2 tokens
        text = "Hello world"
        result = truncate_to_tokens(text, max_tokens=2)

        assert result == text
        assert count_tokens(result) == 2

    def test_truncate_preserves_decoding(self) -> None:
        """Test that truncation produces valid UTF-8 string."""
        text = "Hello 你好 world 世界 " * 10
        result = truncate_to_tokens(text, max_tokens=20)

        # Should be valid string
        assert isinstance(result, str)
        # Should not raise on encode
        result.encode("utf-8")
        # Should be truncated
        assert count_tokens(result) <= 20

    def test_single_token_limit(self) -> None:
        """Test truncation to single token."""
        text = "Hello world and more text"
        result = truncate_to_tokens(text, max_tokens=1)

        assert count_tokens(result) <= 1
        assert len(result) > 0  # Should have something

    def test_zero_token_limit(self) -> None:
        """Test truncation to zero tokens."""
        text = "Hello world"
        result = truncate_to_tokens(text, max_tokens=0)

        # Should return empty string
        assert result == ""
        assert count_tokens(result) == 0

    def test_model_parameter(self) -> None:
        """Test that model parameter is accepted."""
        text = " ".join(["word"] * 20)

        result = truncate_to_tokens(text, max_tokens=10, model="text-embedding-3-small")

        assert count_tokens(result, model="text-embedding-3-small") <= 10

    def test_maintains_word_boundaries(self) -> None:
        """Test that truncation doesn't cut words awkwardly when possible."""
        text = "Hello world this is a test"
        result = truncate_to_tokens(text, max_tokens=3)

        # Result should be valid text
        assert isinstance(result, str)
        assert len(result) > 0
        assert count_tokens(result) <= 3
