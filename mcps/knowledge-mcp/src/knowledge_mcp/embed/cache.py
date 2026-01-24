"""Embedding cache with content hashing."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from diskcache import Cache

if TYPE_CHECKING:
    pass


class EmbeddingCache:
    """
    Persistent embedding cache using content hashing.

    Cache key: SHA-256 hash of normalized text content.
    Cache invalidation: Only on embedding model change (model in path).

    Args:
        cache_dir: Base directory for cache storage.
        embedding_model: Model name (used in cache path for auto-invalidation).
        size_limit: Maximum cache size in bytes (default 10GB).

    Example:
        >>> cache = EmbeddingCache(Path("data/cache"), "text-embedding-3-small")
        >>> cache.set("Hello world", [0.1, 0.2, ...])
        >>> embedding = cache.get("Hello world")  # Returns cached embedding
        >>> embedding = cache.get("Unknown text")  # Returns None
    """

    def __init__(
        self,
        cache_dir: Path,
        embedding_model: str,
        size_limit: int = 10 * 1024 * 1024 * 1024,  # 10GB default
    ) -> None:
        """Initialize cache with model-specific namespace."""
        # Model version in cache path ensures auto-invalidation on model change
        model_safe = embedding_model.replace("/", "_").replace(":", "_")
        self.cache_path = cache_dir / model_safe
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.cache = Cache(str(self.cache_path), size_limit=size_limit)
        self.embedding_model = embedding_model

    def _hash_content(self, text: str) -> str:
        """
        Generate SHA-256 hash of normalized text.

        Normalization: strip whitespace, collapse multiple spaces.
        This ensures "Hello  world" and "Hello world" map to same cache key.
        """
        normalized = " ".join(text.split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(self, text: str) -> list[float] | None:
        """
        Retrieve cached embedding by content hash.

        Args:
            text: Original text content.

        Returns:
            Cached embedding vector, or None if not cached.
        """
        key = self._hash_content(text)
        return self.cache.get(key)

    def set(self, text: str, embedding: list[float]) -> None:
        """
        Store embedding with content hash key.

        Args:
            text: Original text content.
            embedding: Embedding vector to cache.
        """
        key = self._hash_content(text)
        self.cache.set(key, embedding)

    def contains(self, text: str) -> bool:
        """Check if text content is cached."""
        key = self._hash_content(text)
        return key in self.cache

    def stats(self) -> dict[str, object]:
        """
        Get cache statistics.

        Returns:
            Dict with size, disk_usage_mb, model, hits, misses.
        """
        return {
            "size": len(self.cache),
            "disk_usage_mb": round(self.cache.volume() / (1024 * 1024), 2),
            "model": self.embedding_model,
        }

    def clear(self) -> None:
        """Clear all cached embeddings."""
        self.cache.clear()

    def close(self) -> None:
        """Close cache connection."""
        self.cache.close()
