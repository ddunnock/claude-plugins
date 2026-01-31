# tests/integration/test_mcp_tools.py
"""
Integration tests for MCP tool handlers with real dependencies.

Tests the full call chain: MCP handler -> SemanticSearcher -> ChromaDBStore.
Uses real ChromaDB but mocks OpenAI embedder to avoid API calls.

Key difference from unit tests (test_server.py):
- Unit tests mock everything (embedder, store, searcher)
- These tests use real ChromaDBStore with actual data
- Only the embedder is mocked (to avoid OpenAI API costs)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock

import pytest
from mcp.types import CallToolRequest

from knowledge_mcp.models.chunk import KnowledgeChunk
from knowledge_mcp.search import SemanticSearcher
from knowledge_mcp.server import KnowledgeMCPServer
from knowledge_mcp.store.chromadb_store import ChromaDBStore
from knowledge_mcp.utils.config import KnowledgeConfig

if TYPE_CHECKING:
    pass


class TestMCPToolIntegration:
    """Integration tests for MCP tool handlers with real ChromaDB store."""

    @pytest.fixture
    def temp_chromadb_dir(self, tmp_path: Path) -> Path:
        """Create temporary directory for ChromaDB storage."""
        chromadb_dir = tmp_path / "chromadb"
        chromadb_dir.mkdir()
        return chromadb_dir

    @pytest.fixture
    def test_config(self, temp_chromadb_dir: Path) -> KnowledgeConfig:
        """Create test configuration with ChromaDB backend."""
        return KnowledgeConfig(
            openai_api_key="test-api-key-not-real",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
            vector_store="chromadb",
            chromadb_path=temp_chromadb_dir,
            chromadb_collection="test_mcp_integration",
            # Disable cache and token tracking for tests
            cache_enabled=False,
            token_tracking_enabled=False,
        )

    @pytest.fixture
    def real_chromadb_store(self, test_config: KnowledgeConfig) -> ChromaDBStore:
        """Create real ChromaDBStore instance."""
        return ChromaDBStore(test_config)

    @pytest.fixture
    def test_embedding(self) -> list[float]:
        """Create a test embedding vector."""
        # Use a specific pattern for deterministic testing
        return [0.1 * (i % 10) for i in range(1536)]

    @pytest.fixture
    def different_embedding(self) -> list[float]:
        """Create a different embedding vector for filtering tests."""
        # Different pattern to ensure different similarity scores
        return [0.2 * ((i + 5) % 10) for i in range(1536)]

    @pytest.fixture
    def test_chunks(self, test_embedding: list[float]) -> list[KnowledgeChunk]:
        """Create test chunks with known content and embeddings."""
        return [
            KnowledgeChunk(
                id="chunk-001",
                document_id="ieee-15288",
                document_title="IEEE 15288.2-2014",
                document_type="standard",
                content="The System Requirements Review (SRR) shall verify that the system requirements are complete, consistent, and testable.",
                content_hash="hash001",
                token_count=25,
                section_hierarchy=["5", "5.3"],
                section_title="System Requirements Review",
                chunk_type="requirement",
                normative=True,
                page_numbers=[42, 43],
                clause_number="5.3.1",
                embedding=test_embedding,
            ),
            KnowledgeChunk(
                id="chunk-002",
                document_id="ieee-15288",
                document_title="IEEE 15288.2-2014",
                document_type="standard",
                content="Design reviews evaluate the design outputs against requirements and design standards.",
                content_hash="hash002",
                token_count=15,
                section_hierarchy=["5", "5.4"],
                section_title="Design Review",
                chunk_type="guidance",
                normative=False,
                page_numbers=[50],
                clause_number="5.4.1",
                embedding=test_embedding,
            ),
            KnowledgeChunk(
                id="chunk-003",
                document_id="incose-handbook",
                document_title="INCOSE SE Handbook",
                document_type="handbook",
                content="Systems engineering is an interdisciplinary approach to enable the realization of successful systems.",
                content_hash="hash003",
                token_count=18,
                section_hierarchy=["1", "1.1"],
                section_title="Introduction",
                chunk_type="definition",
                normative=None,
                page_numbers=[10],
                clause_number=None,
                embedding=test_embedding,
            ),
        ]

    @pytest.fixture
    def mock_openai_embedder(self, test_embedding: list[float]) -> AsyncMock:
        """Create a mock embedder that returns deterministic embeddings.

        This avoids calling the real OpenAI API while allowing
        the full search flow to execute.
        """
        embedder = AsyncMock()
        embedder.embed.return_value = test_embedding
        embedder.embed_batch.return_value = [test_embedding]
        embedder.dimensions = 1536
        embedder.model_name = "text-embedding-3-small"
        return embedder

    @pytest.fixture
    def populated_chromadb_store(
        self,
        real_chromadb_store: ChromaDBStore,
        test_chunks: list[KnowledgeChunk],
    ) -> ChromaDBStore:
        """ChromaDBStore with test chunks already added."""
        real_chromadb_store.add_chunks(test_chunks)
        return real_chromadb_store

    @pytest.fixture
    def server_with_real_deps(
        self,
        mock_openai_embedder: AsyncMock,
        populated_chromadb_store: ChromaDBStore,
    ) -> KnowledgeMCPServer:
        """Create KnowledgeMCPServer with real store but mocked embedder."""
        return KnowledgeMCPServer(
            name="test-integration-server",
            embedder=mock_openai_embedder,
            store=populated_chromadb_store,
        )

    @pytest.mark.asyncio
    async def test_knowledge_search_returns_real_results(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify search returns actual chunks from ChromaDB.

        This tests the full call chain:
        MCP handler -> SemanticSearcher -> ChromaDBStore -> actual data
        """
        # Arrange
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "system requirements review"}}
        )

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        assert len(response.root.content) == 1
        data = json.loads(response.root.content[0].text)

        assert "results" in data
        assert data["count"] > 0
        assert data["query"] == "system requirements review"

        # Verify we got actual content from ChromaDB
        result = data["results"][0]
        assert "content" in result
        assert "relevance" in result  # Percentage string like "87%"
        assert "citation" in result   # Citation string

        # Verify metadata is populated
        metadata = result["metadata"]
        assert metadata["document_id"] in ["ieee-15288", "incose-handbook"]

    @pytest.mark.asyncio
    async def test_knowledge_search_filter_works(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify filter_dict actually filters results from ChromaDB."""
        # Arrange - filter to only get handbook documents
        request = CallToolRequest(
            params={
                "name": "knowledge_search",
                "arguments": {
                    "query": "systems engineering",
                    "filter_dict": {"document_type": "handbook"},
                },
            }
        )

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        # Should only get handbook documents
        if data["count"] > 0:
            for result in data["results"]:
                assert result["metadata"]["document_id"] == "incose-handbook"

    @pytest.mark.asyncio
    async def test_knowledge_search_normative_filter_works(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify filtering by normative status works."""
        # Arrange - filter to only normative content
        request = CallToolRequest(
            params={
                "name": "knowledge_search",
                "arguments": {
                    "query": "requirements",
                    "filter_dict": {"normative": True},
                },
            }
        )

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        # Should only get normative content
        if data["count"] > 0:
            for result in data["results"]:
                assert result["metadata"]["normative"] is True

    @pytest.mark.asyncio
    async def test_knowledge_search_score_threshold_works(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify low-score results are excluded by score_threshold."""
        # Arrange - set high threshold to filter results
        request = CallToolRequest(
            params={
                "name": "knowledge_search",
                "arguments": {
                    "query": "requirements review",
                    "score_threshold": 0.99,  # Very high threshold
                },
            }
        )

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        # All results should meet threshold (relevance is percentage string like "99%")
        for result in data["results"]:
            relevance_pct = int(result["relevance"].rstrip("%"))
            assert relevance_pct >= 99

    @pytest.mark.asyncio
    async def test_knowledge_stats_returns_real_count(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify stats.total_chunks matches actual count in ChromaDB."""
        # Arrange
        request = CallToolRequest(params={"name": "knowledge_stats", "arguments": {}})

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        assert "total_chunks" in data
        assert data["total_chunks"] == 3  # We added 3 test chunks
        assert "collection_name" in data
        assert "status" in data
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_knowledge_search_empty_collection(
        self,
        mock_openai_embedder: AsyncMock,
        real_chromadb_store: ChromaDBStore,  # Empty store - not populated
    ) -> None:
        """Verify empty results from empty collection."""
        # Arrange - use empty store
        server = KnowledgeMCPServer(
            name="test-empty-server",
            embedder=mock_openai_embedder,
            store=real_chromadb_store,
        )
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "anything"}}
        )

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        assert data["count"] == 0
        assert data["results"] == []

    @pytest.mark.asyncio
    async def test_full_search_flow_with_embedding(
        self,
        mock_openai_embedder: AsyncMock,
        populated_chromadb_store: ChromaDBStore,
    ) -> None:
        """Test embedding -> store search -> format results flow.

        This test verifies the SemanticSearcher properly orchestrates
        the embedder and store to produce SearchResult objects.
        """
        # Arrange - create searcher directly to test intermediate layer
        searcher = SemanticSearcher(mock_openai_embedder, populated_chromadb_store)

        # Act
        results = await searcher.search(
            query="system requirements verification",
            n_results=5,
        )

        # Assert
        # Embedder was called to convert query to vector
        mock_openai_embedder.embed.assert_called_once_with("system requirements verification")

        # Results are SearchResult objects with proper structure
        assert len(results) > 0
        for result in results:
            assert hasattr(result, "id")
            assert hasattr(result, "content")
            assert hasattr(result, "score")
            assert hasattr(result, "document_title")
            assert hasattr(result, "section_title")
            assert hasattr(result, "normative")

    @pytest.mark.asyncio
    async def test_search_n_results_limits_output(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify n_results parameter limits the number of results."""
        # Arrange
        request = CallToolRequest(
            params={
                "name": "knowledge_search",
                "arguments": {"query": "requirements", "n_results": 2},
            }
        )

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        assert data["count"] <= 2

    @pytest.mark.asyncio
    async def test_search_results_ordered_by_relevance(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify results are returned in descending relevance order."""
        # Arrange
        request = CallToolRequest(
            params={
                "name": "knowledge_search",
                "arguments": {"query": "system requirements design", "n_results": 10},
            }
        )

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        if len(data["results"]) > 1:
            # Extract numeric relevance from percentage strings like "87%"
            relevances = [int(r["relevance"].rstrip("%")) for r in data["results"]]
            assert relevances == sorted(relevances, reverse=True), "Results should be in descending relevance order"

    @pytest.mark.asyncio
    async def test_stats_reflects_collection_config(
        self,
        server_with_real_deps: KnowledgeMCPServer,
    ) -> None:
        """Verify stats includes configuration details."""
        # Arrange
        request = CallToolRequest(params={"name": "knowledge_stats", "arguments": {}})

        # Act
        response = await server_with_real_deps.server.request_handlers[CallToolRequest](request)

        # Assert
        data = json.loads(response.root.content[0].text)

        assert "config" in data
        assert data["config"]["vector_size"] == 1536
        assert data["config"]["backend"] == "chromadb"


class TestMCPToolErrorHandling:
    """Integration tests for error handling in MCP tools."""

    @pytest.fixture
    def temp_chromadb_dir(self, tmp_path: Path) -> Path:
        """Create temporary directory for ChromaDB storage."""
        chromadb_dir = tmp_path / "chromadb"
        chromadb_dir.mkdir()
        return chromadb_dir

    @pytest.fixture
    def test_config(self, temp_chromadb_dir: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(
            openai_api_key="test-api-key",
            vector_store="chromadb",
            chromadb_path=temp_chromadb_dir,
            cache_enabled=False,
            token_tracking_enabled=False,
        )

    @pytest.fixture
    def real_chromadb_store(self, test_config: KnowledgeConfig) -> ChromaDBStore:
        """Create real ChromaDBStore instance."""
        return ChromaDBStore(test_config)

    @pytest.mark.asyncio
    async def test_search_handles_embedder_error_gracefully(
        self,
        real_chromadb_store: ChromaDBStore,
    ) -> None:
        """Verify search returns empty results when embedder fails."""
        # Arrange - embedder that raises exception
        failing_embedder = AsyncMock()
        failing_embedder.embed.side_effect = Exception("Embedding API error")

        server = KnowledgeMCPServer(
            name="test-error-server",
            embedder=failing_embedder,
            store=real_chromadb_store,
        )

        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert - graceful degradation: empty results, no crash, no hallucination
        data = json.loads(response.root.content[0].text)
        assert data["count"] == 0  # Empty count
        assert data["results"] == []  # Empty results, no hallucination
