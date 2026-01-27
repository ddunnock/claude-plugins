# tests/unit/test_store/test_qdrant_store.py
"""
Unit tests for QdrantStore.

Tests all methods with mocked QdrantClient to exercise code paths
without requiring a real Qdrant instance.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    CollectionInfo,
    CollectionStatus,
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    NamedVector,
    OptimizersConfigDiff,
    PayloadSchemaType,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

from knowledge_mcp.models.chunk import KnowledgeChunk
from knowledge_mcp.utils.config import KnowledgeConfig

if TYPE_CHECKING:
    pass


class TestQdrantStoreInit:
    """Tests for QdrantStore initialization."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=False,
            chromadb_path=tmp_path / "chromadb",
        )

    @pytest.fixture
    def mock_config_hybrid(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration with hybrid search enabled."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=True,
            chromadb_path=tmp_path / "chromadb",
        )

    def test_creates_collection_if_not_exists(self, mock_config: KnowledgeConfig) -> None:
        """Verify create_collection called when collection doesn't exist."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client

            # Simulate no existing collections
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            QdrantStore(mock_config)

            # Verify create_collection was called
            mock_client.create_collection.assert_called_once()
            call_kwargs = mock_client.create_collection.call_args[1]
            assert call_kwargs["collection_name"] == mock_config.versioned_collection_name

    def test_skips_collection_creation_if_exists(self, mock_config: KnowledgeConfig) -> None:
        """Verify no create when collection already exists."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client

            # Simulate existing collection
            existing_collection = MagicMock()
            existing_collection.name = mock_config.versioned_collection_name
            mock_client.get_collections.return_value.collections = [existing_collection]

            from knowledge_mcp.store.qdrant_store import QdrantStore
            QdrantStore(mock_config)

            # Verify create_collection was NOT called
            mock_client.create_collection.assert_not_called()

    def test_creates_payload_indexes(self, mock_config: KnowledgeConfig) -> None:
        """Verify _create_payload_indexes called on new collection."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            QdrantStore(mock_config)

            # Should create indexes for known fields
            assert mock_client.create_payload_index.call_count >= 5

    def test_handles_index_already_exists(self, mock_config: KnowledgeConfig) -> None:
        """Verify UnexpectedResponse on index creation is handled gracefully."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            # Simulate index already exists error
            mock_client.create_payload_index.side_effect = UnexpectedResponse(
                status_code=400, reason_phrase="Index already exists", content=b"", headers={}
            )

            from knowledge_mcp.store.qdrant_store import QdrantStore
            # Should not raise - error is handled
            store = QdrantStore(mock_config)
            assert store is not None


class TestQdrantStoreAddChunks:
    """Tests for QdrantStore.add_chunks method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=False,
            chromadb_path=tmp_path / "chromadb",
        )

    @pytest.fixture
    def mock_config_hybrid(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration with hybrid search."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=True,
            chromadb_path=tmp_path / "chromadb",
        )

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

    def test_add_chunks_upserts_points(
        self, mock_config: KnowledgeConfig, sample_chunks: list[KnowledgeChunk]
    ) -> None:
        """Verify client.upsert called with correct points."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            result = store.add_chunks(sample_chunks)

            mock_client.upsert.assert_called_once()
            call_kwargs = mock_client.upsert.call_args[1]
            assert call_kwargs["collection_name"] == mock_config.versioned_collection_name
            assert len(call_kwargs["points"]) == 2

    def test_add_chunks_returns_count(
        self, mock_config: KnowledgeConfig, sample_chunks: list[KnowledgeChunk]
    ) -> None:
        """Verify correct count is returned."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            result = store.add_chunks(sample_chunks)

            assert result == 2

    def test_add_empty_chunks_returns_zero(self, mock_config: KnowledgeConfig) -> None:
        """Verify empty list returns 0 without calling upsert."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            # Reset mock to clear init calls
            mock_client.reset_mock()

            result = store.add_chunks([])

            assert result == 0
            mock_client.upsert.assert_not_called()

    def test_add_chunks_raises_on_missing_embedding(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify ValueError for chunk with None embedding."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            chunk_without_embedding = KnowledgeChunk(
                id="chunk-no-embed",
                document_id="doc-1",
                document_title="Test Doc",
                document_type="standard",
                content="Test content",
                content_hash="hash",
                token_count=10,
                embedding=None,  # Missing embedding
            )

            with pytest.raises(ValueError, match="missing embedding"):
                store.add_chunks([chunk_without_embedding])

    def test_add_chunks_batches_large_lists(self, mock_config: KnowledgeConfig) -> None:
        """Verify batching for >100 chunks."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            # Create 250 chunks
            large_chunks = [
                KnowledgeChunk(
                    id=f"chunk-{i}",
                    document_id="doc-1",
                    document_title="Test Doc",
                    document_type="standard",
                    content=f"Content {i}",
                    content_hash=f"hash{i}",
                    token_count=10,
                    embedding=[0.1] * 1536,
                )
                for i in range(250)
            ]

            result = store.add_chunks(large_chunks)

            # Should batch into 3 calls (100, 100, 50)
            assert mock_client.upsert.call_count == 3
            assert result == 250

    def test_add_chunks_hybrid_mode(
        self, mock_config_hybrid: KnowledgeConfig, sample_chunks: list[KnowledgeChunk]
    ) -> None:
        """Verify NamedVector used when hybrid_enabled."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config_hybrid)

            store.add_chunks(sample_chunks)

            # Check that vector is a dict (NamedVector format)
            call_kwargs = mock_client.upsert.call_args[1]
            point = call_kwargs["points"][0]
            assert isinstance(point.vector, dict)
            assert "dense" in point.vector


class TestQdrantStoreSearch:
    """Tests for QdrantStore.search method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=False,
            chromadb_path=tmp_path / "chromadb",
        )

    @pytest.fixture
    def mock_config_hybrid(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration with hybrid search."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=True,
            chromadb_path=tmp_path / "chromadb",
        )

    @pytest.fixture
    def mock_search_results(self) -> list[ScoredPoint]:
        """Create mock search results."""
        return [
            ScoredPoint(
                id="chunk-1",
                version=1,
                score=0.95,
                payload={
                    "content": "Test content 1",
                    "document_id": "doc-1",
                    "document_title": "Test Doc",
                    "document_type": "standard",
                    "section_title": "Section 1",
                    "section_hierarchy": ["1", "1.1"],
                    "chunk_type": "requirement",
                    "normative": True,
                    "clause_number": "1.1",
                    "page_numbers": [10],
                    "references": ["ref1"],
                },
                vector=None,
            ),
            ScoredPoint(
                id="chunk-2",
                version=1,
                score=0.85,
                payload={
                    "content": "Test content 2",
                    "document_id": "doc-1",
                    "document_title": "Test Doc",
                    "document_type": "standard",
                    "section_title": "Section 2",
                    "section_hierarchy": ["2"],
                    "chunk_type": "guidance",
                    "normative": False,
                    "clause_number": "2.0",
                    "page_numbers": [20],
                    "references": [],
                },
                vector=None,
            ),
        ]

    def test_search_returns_formatted_results(
        self, mock_config: KnowledgeConfig, mock_search_results: list[ScoredPoint]
    ) -> None:
        """Verify result format with content, score, metadata."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.search.return_value = mock_search_results

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            results = store.search([0.1] * 1536, n_results=5)

            assert len(results) == 2
            assert results[0]["id"] == "chunk-1"
            assert results[0]["content"] == "Test content 1"
            assert results[0]["score"] == 0.95
            assert results[0]["metadata"]["document_title"] == "Test Doc"
            assert results[0]["metadata"]["normative"] is True

    def test_search_with_filter_dict(
        self, mock_config: KnowledgeConfig, mock_search_results: list[ScoredPoint]
    ) -> None:
        """Verify Filter built from filter_dict."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.search.return_value = mock_search_results

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            store.search(
                [0.1] * 1536,
                n_results=5,
                filter_dict={"chunk_type": "requirement"},
            )

            # Check filter was passed
            call_kwargs = mock_client.search.call_args[1]
            assert call_kwargs["query_filter"] is not None
            assert isinstance(call_kwargs["query_filter"], Filter)

    def test_search_with_bool_filter(
        self, mock_config: KnowledgeConfig, mock_search_results: list[ScoredPoint]
    ) -> None:
        """Verify MatchValue for boolean values."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.search.return_value = mock_search_results

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            store.search(
                [0.1] * 1536,
                n_results=5,
                filter_dict={"normative": True},
            )

            call_kwargs = mock_client.search.call_args[1]
            query_filter = call_kwargs["query_filter"]
            assert query_filter is not None
            # Filter should contain boolean condition
            assert len(query_filter.must) == 1

    def test_search_with_list_filter(
        self, mock_config: KnowledgeConfig, mock_search_results: list[ScoredPoint]
    ) -> None:
        """Verify MatchAny for list values."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.search.return_value = mock_search_results

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            store.search(
                [0.1] * 1536,
                n_results=5,
                filter_dict={"chunk_type": ["requirement", "guidance"]},
            )

            call_kwargs = mock_client.search.call_args[1]
            query_filter = call_kwargs["query_filter"]
            assert query_filter is not None
            # Should use MatchAny for list filter
            condition = query_filter.must[0]
            assert isinstance(condition.match, MatchAny)

    def test_search_with_score_threshold(
        self, mock_config: KnowledgeConfig, mock_search_results: list[ScoredPoint]
    ) -> None:
        """Verify threshold passed to client."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.search.return_value = mock_search_results

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            store.search([0.1] * 1536, n_results=5, score_threshold=0.7)

            call_kwargs = mock_client.search.call_args[1]
            assert call_kwargs["score_threshold"] == 0.7

    def test_search_hybrid_mode_uses_named_vector(
        self, mock_config_hybrid: KnowledgeConfig, mock_search_results: list[ScoredPoint]
    ) -> None:
        """Verify NamedVector in hybrid mode."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.search.return_value = mock_search_results

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config_hybrid)

            store.search([0.1] * 1536, n_results=5)

            call_kwargs = mock_client.search.call_args[1]
            assert isinstance(call_kwargs["query_vector"], NamedVector)
            assert call_kwargs["query_vector"].name == "dense"

    def test_search_non_hybrid_uses_plain_vector(
        self, mock_config: KnowledgeConfig, mock_search_results: list[ScoredPoint]
    ) -> None:
        """Verify plain vector in standard mode."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.search.return_value = mock_search_results

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            store.search([0.1] * 1536, n_results=5)

            call_kwargs = mock_client.search.call_args[1]
            # Should be a plain list, not NamedVector
            assert isinstance(call_kwargs["query_vector"], list)


class TestQdrantStoreStats:
    """Tests for QdrantStore.get_stats method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=False,
            chromadb_path=tmp_path / "chromadb",
        )

    def test_get_stats_returns_collection_info(self, mock_config: KnowledgeConfig) -> None:
        """Verify stats format."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            # Mock collection info
            mock_info = MagicMock()
            mock_info.points_count = 1000
            mock_info.vectors_count = 1000
            mock_info.indexed_vectors_count = 1000
            mock_info.status = CollectionStatus.GREEN
            mock_client.get_collection.return_value = mock_info

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            stats = store.get_stats()

            assert stats["collection_name"] == mock_config.versioned_collection_name
            assert stats["total_chunks"] == 1000
            assert stats["vectors_count"] == 1000
            assert stats["indexed_vectors"] == 1000
            assert stats["config"]["vector_size"] == 1536


class TestQdrantStoreValidation:
    """Tests for QdrantStore.validate_embedding_model method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=False,
            chromadb_path=tmp_path / "chromadb",
        )

    def test_validate_embedding_model_empty_collection(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify True for empty collection."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            # Empty scroll result
            mock_client.scroll.return_value = ([], None)

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            result = store.validate_embedding_model("text-embedding-3-small")

            assert result is True

    def test_validate_embedding_model_matching(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify True when models match."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            # Scroll returns point with matching model
            mock_point = MagicMock()
            mock_point.payload = {"embedding_model": "text-embedding-3-small"}
            mock_client.scroll.return_value = ([mock_point], None)

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            result = store.validate_embedding_model("text-embedding-3-small")

            assert result is True

    def test_validate_embedding_model_mismatch(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify ValueError when different model."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            # Scroll returns point with different model
            mock_point = MagicMock()
            mock_point.payload = {"embedding_model": "text-embedding-ada-002"}
            mock_client.scroll.return_value = ([mock_point], None)

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            with pytest.raises(ValueError, match="uses text-embedding-ada-002"):
                store.validate_embedding_model("text-embedding-3-small")

    def test_validate_embedding_model_handles_exceptions(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify False on errors."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            # Scroll raises exception
            mock_client.scroll.side_effect = Exception("Connection error")

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            result = store.validate_embedding_model("text-embedding-3-small")

            assert result is False


class TestQdrantStoreHealthCheck:
    """Tests for QdrantStore.health_check method."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-key",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="qdrant",
            qdrant_url="http://localhost:6333",
            qdrant_api_key="test-api-key",
            qdrant_collection="test_collection",
            qdrant_hybrid_search=False,
            chromadb_path=tmp_path / "chromadb",
        )

    def test_health_check_returns_true_when_healthy(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify True on success."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            result = store.health_check()

            assert result is True
            mock_client.get_collection.assert_called_with(mock_config.versioned_collection_name)

    def test_health_check_returns_false_on_error(
        self, mock_config: KnowledgeConfig
    ) -> None:
        """Verify False on exception."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.get_collections.return_value.collections = []
            mock_client.get_collection.side_effect = Exception("Connection refused")

            from knowledge_mcp.store.qdrant_store import QdrantStore
            store = QdrantStore(mock_config)

            result = store.health_check()

            assert result is False
