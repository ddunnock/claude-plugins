# tests/integration/test_fallback.py
"""Integration tests for vector store fallback behavior."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

from knowledge_mcp.store import create_store, QdrantStore
from knowledge_mcp.utils.config import KnowledgeConfig


@pytest.fixture(autouse=True)
def ensure_fresh_chromadb_module() -> Generator[None, None, None]:
    """Ensure chromadb_store module is fresh before each test.

    This is needed because the chromadb_store unit tests patch sys.modules
    with mock chromadb, which can pollute the module cache and cause
    isinstance checks to fail when running tests together.
    """
    # Remove the cached module before test to ensure fresh import
    if "knowledge_mcp.store.chromadb_store" in sys.modules:
        del sys.modules["knowledge_mcp.store.chromadb_store"]
    yield
    # Cleanup after test (optional, but keeps things tidy)
    if "knowledge_mcp.store.chromadb_store" in sys.modules:
        del sys.modules["knowledge_mcp.store.chromadb_store"]


def get_chromadb_store_class() -> type:
    """Get ChromaDBStore class with fresh import."""
    from knowledge_mcp.store.chromadb_store import ChromaDBStore
    return ChromaDBStore


class TestQdrantToChromaDBFallback:
    """Test automatic fallback from Qdrant to ChromaDB."""

    @pytest.fixture
    def temp_chromadb_path(self, tmp_path: Path) -> Path:
        """Create temporary directory for ChromaDB."""
        chromadb_dir = tmp_path / "chromadb"
        chromadb_dir.mkdir()
        return chromadb_dir

    @pytest.fixture
    def config_with_bad_qdrant(self, temp_chromadb_path: Path) -> KnowledgeConfig:
        """Create config with unreachable Qdrant URL."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            vector_store="qdrant",
            qdrant_url="http://localhost:9999",  # Unreachable port
            qdrant_api_key="test-api-key",
            chromadb_path=temp_chromadb_path,
        )

    def test_fallback_to_chromadb_on_qdrant_failure(
        self, config_with_bad_qdrant: KnowledgeConfig, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify ChromaDB is returned when Qdrant is unavailable."""
        ChromaDBStore = get_chromadb_store_class()

        with caplog.at_level(logging.WARNING):
            store = create_store(config_with_bad_qdrant)

        # Should be ChromaDB, not Qdrant
        assert isinstance(store, ChromaDBStore)
        assert not isinstance(store, QdrantStore)

        # Should log warning about fallback
        assert any(
            "falling back to chromadb" in record.message.lower()
            or "qdrant unavailable" in record.message.lower()
            for record in caplog.records
        )

    def test_fallback_store_is_functional(
        self, config_with_bad_qdrant: KnowledgeConfig
    ) -> None:
        """Verify fallback ChromaDB store can perform operations."""
        store = create_store(config_with_bad_qdrant)

        # Health check should pass (tests EXISTING health_check() method)
        assert store.health_check()

        # Should be able to search (empty result is fine)
        results = store.search(query_embedding=[0.1] * 1536, n_results=5)
        assert isinstance(results, list)

    def test_no_fallback_when_chromadb_configured(
        self, temp_chromadb_path: Path
    ) -> None:
        """Verify no fallback logic when ChromaDB is primary."""
        ChromaDBStore = get_chromadb_store_class()

        config = KnowledgeConfig(
            openai_api_key="test-key",
            vector_store="chromadb",
            chromadb_path=temp_chromadb_path,
        )

        store = create_store(config)

        assert isinstance(store, ChromaDBStore)


class TestHealthCheckBeforeOperations:
    """Test that health checks execute before store operations.

    Note: health_check() methods already exist in both QdrantStore and ChromaDBStore.
    These tests verify the existing functionality works correctly after migration.
    """

    @pytest.fixture
    def working_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create config with working ChromaDB."""
        chromadb_dir = tmp_path / "chromadb"
        chromadb_dir.mkdir()
        return KnowledgeConfig(
            openai_api_key="test-key",
            vector_store="chromadb",
            chromadb_path=chromadb_dir,
        )

    def test_health_check_called_during_store_creation(
        self, working_config: KnowledgeConfig
    ) -> None:
        """Verify health_check is called when creating store."""
        ChromaDBStore = get_chromadb_store_class()

        with patch.object(
            ChromaDBStore, "health_check", return_value=True
        ) as mock_health:
            store = create_store(working_config)
            mock_health.assert_called_once()


class TestBothStoresUnavailable:
    """Test error handling when no stores are available."""

    def test_connection_error_when_all_stores_fail(self, tmp_path: Path) -> None:
        """Verify ConnectionError is raised when both stores fail."""
        ChromaDBStore = get_chromadb_store_class()

        config = KnowledgeConfig(
            openai_api_key="test-key",
            vector_store="qdrant",
            qdrant_url="http://localhost:9999",  # Unreachable
            qdrant_api_key="test-key",
            chromadb_path=tmp_path / "nonexistent" / "deep" / "path",  # Will fail
        )

        # Make ChromaDB fail by patching health_check
        with patch.object(
            ChromaDBStore, "health_check", return_value=False
        ):
            with pytest.raises(ConnectionError) as exc_info:
                create_store(config)

            # Error message should mention stores
            assert "qdrant" in str(exc_info.value).lower() or "chromadb" in str(exc_info.value).lower()


class TestCategorizedExceptions:
    """Test fallback behavior based on exception type.

    These tests verify that the store factory handles different exception
    categories appropriately (network errors, auth errors, rate limits).
    """

    @pytest.fixture
    def temp_chromadb_path(self, tmp_path: Path) -> Path:
        """Create temporary directory for ChromaDB."""
        chromadb_dir = tmp_path / "chromadb"
        chromadb_dir.mkdir()
        return chromadb_dir

    @pytest.fixture
    def config_with_qdrant(self, temp_chromadb_path: Path) -> KnowledgeConfig:
        """Create config that tries Qdrant first."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            chromadb_path=temp_chromadb_path,
        )

    def test_fallback_on_connection_timeout(
        self,
        config_with_qdrant: KnowledgeConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify fallback when Qdrant connection times out."""
        import requests.exceptions

        with patch(
            "knowledge_mcp.store.qdrant_store.QdrantClient"
        ) as MockClient:
            # Simulate connection timeout
            MockClient.side_effect = requests.exceptions.ConnectTimeout(
                "Connection timed out"
            )

            ChromaDBStore = get_chromadb_store_class()

            with caplog.at_level(logging.WARNING):
                store = create_store(config_with_qdrant)

            # Should fall back to ChromaDB
            assert isinstance(store, ChromaDBStore)
            assert any(
                "qdrant" in record.message.lower()
                for record in caplog.records
            )

    def test_fallback_on_connection_refused(
        self,
        config_with_qdrant: KnowledgeConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify fallback when Qdrant connection is refused."""
        with patch(
            "knowledge_mcp.store.qdrant_store.QdrantClient"
        ) as MockClient:
            # Simulate connection refused
            MockClient.side_effect = ConnectionRefusedError(
                "Connection refused"
            )

            ChromaDBStore = get_chromadb_store_class()

            with caplog.at_level(logging.WARNING):
                store = create_store(config_with_qdrant)

            # Should fall back to ChromaDB
            assert isinstance(store, ChromaDBStore)

    def test_fallback_on_dns_resolution_failure(
        self,
        config_with_qdrant: KnowledgeConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify fallback when DNS resolution fails."""
        import socket

        with patch(
            "knowledge_mcp.store.qdrant_store.QdrantClient"
        ) as MockClient:
            # Simulate DNS resolution failure
            MockClient.side_effect = socket.gaierror(
                8, "nodename nor servname provided, or not known"
            )

            ChromaDBStore = get_chromadb_store_class()

            with caplog.at_level(logging.WARNING):
                store = create_store(config_with_qdrant)

            # Should fall back to ChromaDB
            assert isinstance(store, ChromaDBStore)

    def test_fallback_on_authentication_error(
        self,
        config_with_qdrant: KnowledgeConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify fallback on 401/403 authentication errors."""
        from qdrant_client.http.exceptions import UnexpectedResponse

        with patch(
            "knowledge_mcp.store.qdrant_store.QdrantClient"
        ) as MockClient:
            # Simulate 401 Unauthorized
            MockClient.side_effect = UnexpectedResponse(
                status_code=401,
                reason_phrase="Unauthorized",
                content=b"Invalid API key",
                headers={},
            )

            ChromaDBStore = get_chromadb_store_class()

            with caplog.at_level(logging.WARNING):
                store = create_store(config_with_qdrant)

            # Should fall back to ChromaDB
            assert isinstance(store, ChromaDBStore)

    def test_fallback_on_rate_limit_error(
        self,
        config_with_qdrant: KnowledgeConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify fallback on 429 rate limit errors."""
        from qdrant_client.http.exceptions import UnexpectedResponse

        with patch(
            "knowledge_mcp.store.qdrant_store.QdrantClient"
        ) as MockClient:
            # Simulate 429 Too Many Requests
            MockClient.side_effect = UnexpectedResponse(
                status_code=429,
                reason_phrase="Too Many Requests",
                content=b"Rate limit exceeded",
                headers={},
            )

            ChromaDBStore = get_chromadb_store_class()

            with caplog.at_level(logging.WARNING):
                store = create_store(config_with_qdrant)

            # Should fall back to ChromaDB
            assert isinstance(store, ChromaDBStore)
            # Should log the rate limit
            assert any(
                "qdrant connection failed" in record.message.lower()
                or "falling back" in record.message.lower()
                for record in caplog.records
            )

    def test_no_fallback_on_invalid_config(self, tmp_path: Path) -> None:
        """Verify config errors propagate without fallback.

        Configuration errors (like invalid parameters) should NOT trigger
        fallback - they should be raised to the caller since the config
        itself is wrong.
        """
        ChromaDBStore = get_chromadb_store_class()

        # This tests that ValueError from config validation propagates
        # ChromaDB is configured explicitly, no fallback should occur
        config = KnowledgeConfig(
            openai_api_key="test-key",
            vector_store="chromadb",
            chromadb_path=tmp_path / "chromadb",
        )
        config.chromadb_path.mkdir(parents=True, exist_ok=True)

        with patch.object(
            ChromaDBStore, "__init__", side_effect=ValueError("Invalid collection name")
        ):
            with pytest.raises(ValueError, match="Invalid collection name"):
                create_store(config)

    def test_fallback_on_qdrant_health_check_failure(
        self,
        config_with_qdrant: KnowledgeConfig,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify fallback when Qdrant health check returns False."""
        with patch(
            "knowledge_mcp.store.qdrant_store.QdrantClient"
        ) as MockClient:
            mock_client = MockClient.return_value
            mock_client.get_collections.return_value.collections = []

            # Make health_check fail by having get_collection raise
            mock_client.get_collection.side_effect = Exception("Health check failed")

            ChromaDBStore = get_chromadb_store_class()

            with caplog.at_level(logging.WARNING):
                store = create_store(config_with_qdrant)

            # Should fall back to ChromaDB
            assert isinstance(store, ChromaDBStore)
            assert any(
                "health check failed" in record.message.lower()
                for record in caplog.records
            )
