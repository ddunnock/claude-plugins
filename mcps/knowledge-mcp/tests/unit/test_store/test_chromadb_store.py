# tests/unit/test_store/test_chromadb_store.py
"""
Unit tests for ChromaDBStore.

Tests all methods with mocked chromadb to exercise code paths
without requiring a real ChromaDB instance.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

from knowledge_mcp.models.chunk import KnowledgeChunk
from knowledge_mcp.utils.config import KnowledgeConfig

if TYPE_CHECKING:
    pass


class TestChromaDBStoreInit:
    """Tests for ChromaDBStore initialization."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="chromadb",
            chromadb_path=tmp_path / "chromadb",
            chromadb_collection="test_collection",
        )

    def test_creates_directory_if_not_exists(self, mock_config: KnowledgeConfig) -> None:
        """Verify mkdir called for chromadb path."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            # Need to reimport to get the patched module
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            # Directory should be created
            assert mock_config.chromadb_path.exists()

    def test_gets_or_creates_collection(self, mock_config: KnowledgeConfig) -> None:
        """Verify get_or_create_collection called."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            mock_client.get_or_create_collection.assert_called_once()
            call_kwargs = mock_client.get_or_create_collection.call_args[1]
            assert call_kwargs["name"] == mock_config.versioned_chromadb_collection_name
            assert call_kwargs["metadata"] == {"hnsw:space": "cosine"}

    def test_raises_import_error_when_chromadb_missing(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify helpful ImportError when chromadb not installed."""
        # Remove chromadb from sys.modules if present
        chromadb_modules = [k for k in sys.modules if k.startswith("chromadb")]
        saved_modules = {k: sys.modules.pop(k) for k in chromadb_modules if k in sys.modules}

        try:
            # Also need to remove the store module so it reimports
            if "knowledge_mcp.store.chromadb_store" in sys.modules:
                del sys.modules["knowledge_mcp.store.chromadb_store"]

            # Patch the import to raise ImportError
            import builtins
            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "chromadb":
                    raise ImportError("No module named 'chromadb'")
                return original_import(name, *args, **kwargs)

            with patch.object(builtins, "__import__", side_effect=mock_import):
                from knowledge_mcp.store.chromadb_store import ChromaDBStore

                with pytest.raises(ImportError, match="chromadb is required"):
                    ChromaDBStore(mock_config)
        finally:
            # Restore modules
            sys.modules.update(saved_modules)


class TestChromaDBStoreAddChunks:
    """Tests for ChromaDBStore.add_chunks method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="chromadb",
            chromadb_path=tmp_path / "chromadb",
            chromadb_collection="test_collection",
        )

    @pytest.fixture
    def mock_store(self, mock_config: KnowledgeConfig) -> Any:
        """Create ChromaDBStore with mocked client."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)
            store._mock_collection = mock_collection
            return store

    @pytest.fixture
    def sample_chunks(self) -> list[KnowledgeChunk]:
        """Create sample chunks for testing."""
        return [
            KnowledgeChunk(
                id="chunk-1",
                document_id="doc-1",
                document_title="Test Doc",
                document_type="standard",
                content="Test content 1",
                content_hash="hash1",
                token_count=10,
                embedding=[0.1] * 1536,
            ),
            KnowledgeChunk(
                id="chunk-2",
                document_id="doc-1",
                document_title="Test Doc",
                document_type="standard",
                content="Test content 2",
                content_hash="hash2",
                token_count=10,
                embedding=[0.2] * 1536,
            ),
        ]

    def test_add_chunks_upserts_data(
        self, mock_store: Any, sample_chunks: list[KnowledgeChunk]
    ) -> None:
        """Verify collection.upsert called with correct data."""
        result = mock_store.add_chunks(sample_chunks)

        mock_store._mock_collection.upsert.assert_called_once()
        call_kwargs = mock_store._mock_collection.upsert.call_args[1]
        assert len(call_kwargs["ids"]) == 2
        assert len(call_kwargs["embeddings"]) == 2
        assert len(call_kwargs["documents"]) == 2
        assert len(call_kwargs["metadatas"]) == 2

    def test_add_chunks_returns_count(
        self, mock_store: Any, sample_chunks: list[KnowledgeChunk]
    ) -> None:
        """Verify correct count is returned."""
        result = mock_store.add_chunks(sample_chunks)
        assert result == 2

    def test_add_empty_chunks_returns_zero(self, mock_store: Any) -> None:
        """Verify 0 returned for empty list."""
        result = mock_store.add_chunks([])
        assert result == 0
        mock_store._mock_collection.upsert.assert_not_called()

    def test_add_chunks_raises_on_missing_embedding(self, mock_store: Any) -> None:
        """Verify ValueError for chunk with None embedding."""
        chunk_without_embedding = KnowledgeChunk(
            id="chunk-no-embed",
            document_id="doc-1",
            document_title="Test Doc",
            document_type="standard",
            content="Test content",
            content_hash="hash",
            token_count=10,
            embedding=None,
        )

        with pytest.raises(ValueError, match="missing embedding"):
            mock_store.add_chunks([chunk_without_embedding])

    def test_add_chunks_includes_all_metadata(
        self, mock_store: Any, sample_chunks: list[KnowledgeChunk]
    ) -> None:
        """Verify all metadata fields are included."""
        mock_store.add_chunks(sample_chunks)

        call_kwargs = mock_store._mock_collection.upsert.call_args[1]
        metadata = call_kwargs["metadatas"][0]

        # Check all expected fields
        assert "document_id" in metadata
        assert "document_title" in metadata
        assert "document_type" in metadata
        assert "section_title" in metadata
        assert "chunk_type" in metadata
        assert "normative" in metadata
        assert "token_count" in metadata
        assert "content_hash" in metadata
        assert "embedding_model" in metadata
        assert "embedding_dimensions" in metadata
        assert "created_at" in metadata


class TestChromaDBStoreSearch:
    """Tests for ChromaDBStore.search method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="chromadb",
            chromadb_path=tmp_path / "chromadb",
            chromadb_collection="test_collection",
        )

    @pytest.fixture
    def mock_store_with_results(self, mock_config: KnowledgeConfig) -> Any:
        """Create ChromaDBStore with mocked query results."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        # Mock query results
        mock_collection.query.return_value = {
            "ids": [["chunk-1", "chunk-2"]],
            "documents": [["Content 1", "Content 2"]],
            "metadatas": [[
                {"document_id": "doc-1", "document_title": "Test Doc"},
                {"document_id": "doc-2", "document_title": "Test Doc 2"},
            ]],
            "distances": [[0.1, 0.3]],  # Lower distance = higher similarity
        }

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)
            store._mock_collection = mock_collection
            return store

    def test_search_returns_formatted_results(self, mock_store_with_results: Any) -> None:
        """Verify result format."""
        results = mock_store_with_results.search([0.1] * 1536, n_results=5)

        assert len(results) == 2
        assert results[0]["id"] == "chunk-1"
        assert results[0]["content"] == "Content 1"
        assert results[0]["metadata"]["document_id"] == "doc-1"
        assert "score" in results[0]

    def test_search_converts_distance_to_score(
        self, mock_store_with_results: Any
    ) -> None:
        """Verify 1 - distance conversion."""
        results = mock_store_with_results.search([0.1] * 1536, n_results=5)

        # Distance 0.1 should become score 0.9
        assert results[0]["score"] == pytest.approx(0.9)
        # Distance 0.3 should become score 0.7
        assert results[1]["score"] == pytest.approx(0.7)

    def test_search_with_filter_dict(self, mock_store_with_results: Any) -> None:
        """Verify where filter built from filter_dict."""
        mock_store_with_results.search(
            [0.1] * 1536,
            n_results=5,
            filter_dict={"chunk_type": "requirement"},
        )

        call_kwargs = mock_store_with_results._mock_collection.query.call_args[1]
        assert call_kwargs["where"] is not None
        assert "$and" in call_kwargs["where"]

    def test_search_respects_score_threshold(self, mock_config: KnowledgeConfig) -> None:
        """Verify low scores are filtered out."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        # Mock query results with one low score
        mock_collection.query.return_value = {
            "ids": [["chunk-1", "chunk-2"]],
            "documents": [["Content 1", "Content 2"]],
            "metadatas": [[
                {"document_id": "doc-1"},
                {"document_id": "doc-2"},
            ]],
            "distances": [[0.1, 0.9]],  # Second has score 0.1 (below threshold)
        }

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            results = store.search([0.1] * 1536, n_results=5, score_threshold=0.5)

            # Only first result should be returned (score 0.9 > 0.5)
            assert len(results) == 1
            assert results[0]["id"] == "chunk-1"

    def test_search_empty_collection(self, mock_config: KnowledgeConfig) -> None:
        """Verify empty list returned for empty collection."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        # Mock empty results
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            results = store.search([0.1] * 1536, n_results=5)

            assert results == []


class TestChromaDBStoreStats:
    """Tests for ChromaDBStore.get_stats method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="chromadb",
            chromadb_path=tmp_path / "chromadb",
            chromadb_collection="test_collection",
        )

    def test_get_stats_returns_info(self, mock_config: KnowledgeConfig) -> None:
        """Verify stats format."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_collection.count.return_value = 500

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            stats = store.get_stats()

            assert "collection_name" in stats
            assert stats["total_chunks"] == 500
            assert stats["vectors_count"] == 500
            assert stats["status"] == "active"
            assert stats["config"]["backend"] == "chromadb"

    def test_get_stats_includes_count(self, mock_config: KnowledgeConfig) -> None:
        """Verify total_chunks from count()."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_collection.count.return_value = 1234

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            stats = store.get_stats()

            assert stats["total_chunks"] == 1234
            mock_collection.count.assert_called()


class TestChromaDBStoreValidation:
    """Tests for ChromaDBStore.validate_embedding_model method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="chromadb",
            chromadb_path=tmp_path / "chromadb",
            chromadb_collection="test_collection",
        )

    def test_validate_embedding_model_empty(self, mock_config: KnowledgeConfig) -> None:
        """Verify True for empty collection."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        # Empty peek result
        mock_collection.peek.return_value = {"ids": [], "metadatas": []}

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            result = store.validate_embedding_model("text-embedding-3-small")

            assert result is True

    def test_validate_embedding_model_matching(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify True when models match."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        # Peek returns matching model
        mock_collection.peek.return_value = {
            "ids": ["chunk-1"],
            "metadatas": [{"embedding_model": "text-embedding-3-small"}],
        }

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            result = store.validate_embedding_model("text-embedding-3-small")

            assert result is True

    def test_validate_embedding_model_mismatch(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify ValueError when different model."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        # Peek returns different model
        mock_collection.peek.return_value = {
            "ids": ["chunk-1"],
            "metadatas": [{"embedding_model": "text-embedding-ada-002"}],
        }

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            with pytest.raises(ValueError, match="uses text-embedding-ada-002"):
                store.validate_embedding_model("text-embedding-3-small")

    def test_validate_embedding_model_handles_exceptions(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify False on errors."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        # Peek raises exception
        mock_collection.peek.side_effect = Exception("Database error")

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            result = store.validate_embedding_model("text-embedding-3-small")

            assert result is False


class TestChromaDBStoreHealthCheck:
    """Tests for ChromaDBStore.health_check method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="chromadb",
            chromadb_path=tmp_path / "chromadb",
            chromadb_collection="test_collection",
        )

    def test_health_check_returns_true(self, mock_config: KnowledgeConfig) -> None:
        """Verify True when count() succeeds."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_collection.count.return_value = 100

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            result = store.health_check()

            assert result is True

    def test_health_check_returns_false_on_error(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify False on exception."""
        mock_chromadb = MagicMock()
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection

        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            from importlib import reload
            import knowledge_mcp.store.chromadb_store as chromadb_module
            reload(chromadb_module)

            store = chromadb_module.ChromaDBStore(mock_config)

            # Now make count() fail
            store.collection.count.side_effect = Exception("Connection lost")

            result = store.health_check()

            assert result is False
