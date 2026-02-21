"""Integration tests for OpenAIEmbedder with cache and token tracking."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.embed.cache import EmbeddingCache
from knowledge_mcp.embed.openai_embedder import OpenAIEmbedder
from knowledge_mcp.monitoring.token_tracker import TokenTracker
from conftest import TEST_OPENAI_API_KEY, TEST_QDRANT_API_KEY, TEST_SK_API_KEY, TEST_COHERE_API_KEY


class TestEmbedderCacheIntegration:
    """Integration tests with real cache and tracker."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path: Path) -> Path:
        """Isolated cache directory."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir

    @pytest.fixture
    def temp_log_file(self, tmp_path: Path) -> Path:
        """Isolated token log file."""
        return tmp_path / "tokens.json"

    @pytest.fixture
    def real_cache(self, temp_cache_dir: Path) -> EmbeddingCache:
        """Real EmbeddingCache with isolated directory."""
        return EmbeddingCache(temp_cache_dir, "text-embedding-3-small")

    @pytest.fixture
    def real_tracker(self, temp_log_file: Path) -> TokenTracker:
        """Real TokenTracker with isolated log file."""
        return TokenTracker(temp_log_file, "text-embedding-3-small")

    @pytest.fixture
    def embedder_with_real_deps(
        self,
        real_cache: EmbeddingCache,
        real_tracker: TokenTracker,
    ) -> OpenAIEmbedder:
        """Embedder with real cache/tracker but mocked API."""
        embedder = OpenAIEmbedder(
            api_key=TEST_SK_API_KEY,
            cache=real_cache,
            token_tracker=real_tracker,
        )
        # Mock the API call
        embedder._client = MagicMock()
        embedder._client.embeddings = MagicMock()
        embedder._client.embeddings.create = AsyncMock(
            return_value=MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
        )
        return embedder

    @pytest.mark.asyncio
    async def test_cache_hit_prevents_api_call(
        self,
        embedder_with_real_deps: OpenAIEmbedder,
    ) -> None:
        """Verify second call with same text does not call API."""
        # First call - cache miss, API called
        await embedder_with_real_deps.embed("test text")
        first_call_count = embedder_with_real_deps._client.embeddings.create.call_count

        # Second call - cache hit, no API call
        await embedder_with_real_deps.embed("test text")
        second_call_count = embedder_with_real_deps._client.embeddings.create.call_count

        assert first_call_count == 1
        assert second_call_count == 1  # No additional call

    @pytest.mark.asyncio
    async def test_cache_returns_same_embedding(
        self,
        embedder_with_real_deps: OpenAIEmbedder,
    ) -> None:
        """Verify cached embedding matches original."""
        embedding1 = await embedder_with_real_deps.embed("test text")
        embedding2 = await embedder_with_real_deps.embed("test text")

        assert embedding1 == embedding2

    @pytest.mark.asyncio
    async def test_tracker_records_cache_hit(
        self,
        embedder_with_real_deps: OpenAIEmbedder,
        real_tracker: TokenTracker,
    ) -> None:
        """Verify tracker records cache hits correctly."""
        await embedder_with_real_deps.embed("test text")  # Cache miss
        await embedder_with_real_deps.embed("test text")  # Cache hit

        summary = real_tracker.get_daily_summary()
        assert summary.get("cache_hits", 0) == 1
        assert summary.get("embedding_requests", 0) == 1

    @pytest.mark.asyncio
    async def test_cache_persists_across_instances(
        self,
        temp_cache_dir: Path,
        temp_log_file: Path,
    ) -> None:
        """Verify cache persists after embedder is recreated."""
        # First embedder instance
        cache1 = EmbeddingCache(temp_cache_dir, "text-embedding-3-small")
        tracker1 = TokenTracker(temp_log_file, "text-embedding-3-small")
        embedder1 = OpenAIEmbedder(
            api_key=TEST_SK_API_KEY,
            cache=cache1,
            token_tracker=tracker1,
        )
        embedder1._client = MagicMock()
        embedder1._client.embeddings = MagicMock()
        embedder1._client.embeddings.create = AsyncMock(
            return_value=MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
        )

        # Store embedding
        await embedder1.embed("persistent text")
        cache1.close()  # Close cache cleanly

        # Second embedder instance with fresh cache
        cache2 = EmbeddingCache(temp_cache_dir, "text-embedding-3-small")
        tracker2 = TokenTracker(temp_log_file, "text-embedding-3-small")
        embedder2 = OpenAIEmbedder(
            api_key=TEST_SK_API_KEY,
            cache=cache2,
            token_tracker=tracker2,
        )
        embedder2._client = MagicMock()
        embedder2._client.embeddings = MagicMock()
        embedder2._client.embeddings.create = AsyncMock(
            return_value=MagicMock(
                data=[MagicMock(embedding=[0.2] * 1536)]  # Different embedding
            )
        )

        # Should return cached value from first instance
        result = await embedder2.embed("persistent text")

        # Result should be from cache (0.1), not new API call (0.2)
        assert result[0] == 0.1
        embedder2._client.embeddings.create.assert_not_called()
        cache2.close()

    @pytest.mark.asyncio
    async def test_different_texts_not_cached(
        self,
        embedder_with_real_deps: OpenAIEmbedder,
    ) -> None:
        """Verify different texts result in separate API calls."""
        await embedder_with_real_deps.embed("text one")
        await embedder_with_real_deps.embed("text two")

        assert embedder_with_real_deps._client.embeddings.create.call_count == 2
