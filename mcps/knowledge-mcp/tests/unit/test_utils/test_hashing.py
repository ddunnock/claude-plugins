"""Unit tests for hashing module."""

from __future__ import annotations

from knowledge_mcp.utils.hashing import compute_content_hash


class TestComputeContentHash:
    """Tests for compute_content_hash function."""

    def test_deterministic_output(self) -> None:
        """Test that same input produces same hash."""
        text = "Hello world"
        hash1 = compute_content_hash(text)
        hash2 = compute_content_hash(text)

        assert hash1 == hash2

    def test_different_text_different_hash(self) -> None:
        """Test that different text produces different hashes."""
        hash1 = compute_content_hash("Hello world")
        hash2 = compute_content_hash("Goodbye world")

        assert hash1 != hash2

    def test_whitespace_normalization_leading_trailing(self) -> None:
        """Test that leading/trailing whitespace is normalized."""
        hash1 = compute_content_hash("Hello world")
        hash2 = compute_content_hash("  Hello world  ")
        hash3 = compute_content_hash("\tHello world\n")

        assert hash1 == hash2
        assert hash1 == hash3

    def test_line_ending_normalization(self) -> None:
        """Test that \\r\\n is normalized to \\n."""
        hash1 = compute_content_hash("Hello\nworld")
        hash2 = compute_content_hash("Hello\r\nworld")

        assert hash1 == hash2

    def test_empty_string(self) -> None:
        """Test that empty string produces consistent hash."""
        hash1 = compute_content_hash("")
        hash2 = compute_content_hash("")

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex is 64 chars

    def test_whitespace_only_normalized(self) -> None:
        """Test that whitespace-only strings are normalized to empty."""
        hash1 = compute_content_hash("")
        hash2 = compute_content_hash("   ")
        hash3 = compute_content_hash("\n\n\n")
        hash4 = compute_content_hash("\t\t")

        assert hash1 == hash2
        assert hash1 == hash3
        assert hash1 == hash4

    def test_unicode_handling(self) -> None:
        """Test that unicode text is handled correctly."""
        text = "Hello 你好 world 世界"
        hash1 = compute_content_hash(text)
        hash2 = compute_content_hash(text)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_emoji_handling(self) -> None:
        """Test that emoji characters are handled correctly."""
        text = "Hello 👋 world 🌍"
        hash1 = compute_content_hash(text)
        hash2 = compute_content_hash(text)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_multiline_text(self) -> None:
        """Test hashing multiline text."""
        text = """Line 1
Line 2
Line 3"""
        hash1 = compute_content_hash(text)
        hash2 = compute_content_hash(text)

        assert hash1 == hash2

    def test_internal_whitespace_preserved(self) -> None:
        """Test that internal whitespace differences affect hash."""
        hash1 = compute_content_hash("Hello world")
        hash2 = compute_content_hash("Hello  world")  # Double space

        # Internal whitespace is NOT normalized, should produce different hashes
        assert hash1 != hash2

    def test_case_sensitive(self) -> None:
        """Test that hashing is case-sensitive."""
        hash1 = compute_content_hash("Hello World")
        hash2 = compute_content_hash("hello world")

        assert hash1 != hash2

    def test_hash_format(self) -> None:
        """Test that hash is valid SHA-256 hex format."""
        text = "Test content"
        hash_result = compute_content_hash(text)

        # SHA-256 produces 64 hex characters
        assert len(hash_result) == 64
        # Should only contain hex characters
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_long_text(self) -> None:
        """Test hashing long text."""
        text = "word " * 1000  # ~5000 characters
        hash1 = compute_content_hash(text)
        hash2 = compute_content_hash(text)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_special_characters(self) -> None:
        """Test hashing text with special characters."""
        text = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        hash1 = compute_content_hash(text)
        hash2 = compute_content_hash(text)

        assert hash1 == hash2
