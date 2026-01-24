"""Unit tests for EmbeddingCache."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from knowledge_mcp.embed.cache import EmbeddingCache


class TestEmbeddingCache:
    """Tests for EmbeddingCache class."""

    @pytest.fixture
    def cache_dir(self) -> Path:
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def cache(self, cache_dir: Path) -> EmbeddingCache:
        """Create cache instance for testing."""
        return EmbeddingCache(cache_dir, "text-embedding-3-small")

    def test_set_and_get_embedding(self, cache: EmbeddingCache) -> None:
        """Test storing and retrieving embedding."""
        text = "Hello world"
        embedding = [0.1, 0.2, 0.3]

        cache.set(text, embedding)
        result = cache.get(text)

        assert result == embedding

    def test_get_missing_returns_none(self, cache: EmbeddingCache) -> None:
        """Test that missing text returns None."""
        result = cache.get("nonexistent text")
        assert result is None

    def test_normalized_text_matches(self, cache: EmbeddingCache) -> None:
        """Test that whitespace variations map to same cache entry."""
        embedding = [0.1, 0.2, 0.3]

        cache.set("Hello world", embedding)

        # Extra spaces should still hit cache
        assert cache.get("Hello  world") == embedding
        assert cache.get("  Hello world  ") == embedding
        assert cache.get("Hello\n\tworld") == embedding

    def test_different_text_different_keys(self, cache: EmbeddingCache) -> None:
        """Test that different text produces different cache keys."""
        cache.set("Hello world", [0.1])
        cache.set("Hello universe", [0.2])

        assert cache.get("Hello world") == [0.1]
        assert cache.get("Hello universe") == [0.2]

    def test_contains_check(self, cache: EmbeddingCache) -> None:
        """Test contains() method."""
        cache.set("cached text", [0.1])

        assert cache.contains("cached text") is True
        assert cache.contains("uncached text") is False

    def test_stats_returns_metrics(self, cache: EmbeddingCache) -> None:
        """Test stats() returns cache metrics."""
        cache.set("text1", [0.1])
        cache.set("text2", [0.2])

        stats = cache.stats()

        assert stats["size"] == 2
        assert stats["model"] == "text-embedding-3-small"
        assert "disk_usage_mb" in stats

    def test_clear_removes_all(self, cache: EmbeddingCache) -> None:
        """Test clear() removes all cached entries."""
        cache.set("text1", [0.1])
        cache.set("text2", [0.2])

        cache.clear()

        assert cache.get("text1") is None
        assert cache.get("text2") is None
        assert cache.stats()["size"] == 0

    def test_model_isolation(self, cache_dir: Path) -> None:
        """Test that different models have separate caches."""
        cache1 = EmbeddingCache(cache_dir, "model-v1")
        cache2 = EmbeddingCache(cache_dir, "model-v2")

        cache1.set("text", [0.1])

        # Different model should NOT see cache from other model
        assert cache1.get("text") == [0.1]
        assert cache2.get("text") is None

    def test_persistence_across_instances(self, cache_dir: Path) -> None:
        """Test that cache persists across instance recreation."""
        model = "text-embedding-3-small"

        # Create, populate, close
        cache1 = EmbeddingCache(cache_dir, model)
        cache1.set("persistent text", [0.1, 0.2])
        cache1.close()

        # Recreate and verify
        cache2 = EmbeddingCache(cache_dir, model)
        result = cache2.get("persistent text")

        assert result == [0.1, 0.2]
