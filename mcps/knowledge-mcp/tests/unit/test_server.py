# tests/unit/test_server.py
"""
Unit tests for MCP server tool handlers.

Tests the knowledge_search and knowledge_stats tools using
mocked dependencies (embedder and store).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.types import CallToolRequest, ListToolsRequest

from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.server import KnowledgeMCPServer


class TestListTools:
    """Tests for list_tools handler."""

    @pytest.fixture
    def server(self) -> KnowledgeMCPServer:
        """Create server instance with mocked dependencies."""
        mock_embedder = MagicMock()
        mock_store = MagicMock()
        return KnowledgeMCPServer(
            name="test-server",
            embedder=mock_embedder,
            store=mock_store,
        )

    @pytest.mark.asyncio
    async def test_list_tools_returns_two_tools(self, server: KnowledgeMCPServer) -> None:
        """Test that list_tools returns knowledge_search and knowledge_stats."""
        # Arrange
        request = ListToolsRequest()

        # Act
        response = await server.server.request_handlers[ListToolsRequest](request)

        # Assert
        assert len(response.root.tools) == 2
        tool_names = [tool.name for tool in response.root.tools]
        assert "knowledge_search" in tool_names
        assert "knowledge_stats" in tool_names

    @pytest.mark.asyncio
    async def test_knowledge_search_tool_has_required_schema(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that knowledge_search tool has correct input schema."""
        # Arrange
        request = ListToolsRequest()

        # Act
        response = await server.server.request_handlers[ListToolsRequest](request)
        search_tool = next(t for t in response.root.tools if t.name == "knowledge_search")

        # Assert
        assert "query" in search_tool.inputSchema["required"]
        assert "query" in search_tool.inputSchema["properties"]
        assert "n_results" in search_tool.inputSchema["properties"]
        assert "filter_dict" in search_tool.inputSchema["properties"]
        assert "score_threshold" in search_tool.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_knowledge_stats_tool_has_empty_schema(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that knowledge_stats tool has no required parameters."""
        # Arrange
        request = ListToolsRequest()

        # Act
        response = await server.server.request_handlers[ListToolsRequest](request)
        stats_tool = next(t for t in response.root.tools if t.name == "knowledge_stats")

        # Assert
        assert stats_tool.inputSchema["required"] == []
        assert stats_tool.inputSchema["properties"] == {}


class TestKnowledgeSearch:
    """Tests for knowledge_search tool handler."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create a mock embedder."""
        embedder = AsyncMock()
        embedder.embed.return_value = [0.1] * 1536
        return embedder

    @pytest.fixture
    def mock_store(self) -> MagicMock:
        """Create a mock store."""
        store = MagicMock()
        store.search.return_value = [
            {
                "id": "chunk-1",
                "content": "Test content about system requirements review",
                "score": 0.95,
                "metadata": {
                    "document_id": "ieee-15288",
                    "document_title": "IEEE 15288.2",
                    "document_type": "standard",
                    "section_title": "System Requirements Review",
                    "section_hierarchy": ["5", "5.3"],
                    "chunk_type": "requirement",
                    "normative": True,
                    "clause_number": "5.3.1",
                    "page_numbers": [42, 43],
                },
            }
        ]
        return store

    @pytest.fixture
    def server(
        self,
        mock_embedder: AsyncMock,
        mock_store: MagicMock,
    ) -> KnowledgeMCPServer:
        """Create server instance with mocked dependencies."""
        return KnowledgeMCPServer(
            name="test-server",
            embedder=mock_embedder,
            store=mock_store,
        )

    @pytest.mark.asyncio
    async def test_search_returns_formatted_results(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that search returns properly formatted results."""
        # Arrange
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "system requirements review"}}
        )

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        assert len(response.root.content) == 1
        assert response.root.content[0].type == "text"

        import json
        data = json.loads(response.root.content[0].text)
        assert "results" in data
        assert data["total_results"] == 1
        assert data["query"] == "system requirements review"
        assert data["results"][0]["content"] == "Test content about system requirements review"
        assert data["results"][0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_search_includes_source_citations(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that search results include source citations."""
        # Arrange
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        import json
        data = json.loads(response.root.content[0].text)
        source = data["results"][0]["source"]

        assert source["document_title"] == "IEEE 15288.2"
        assert source["section_title"] == "System Requirements Review"
        assert source["section_hierarchy"] == ["5", "5.3"]
        assert source["clause_number"] == "5.3.1"
        assert source["page_numbers"] == [42, 43]

    @pytest.mark.asyncio
    async def test_search_passes_all_arguments(
        self,
        server: KnowledgeMCPServer,
        mock_embedder: AsyncMock,
    ) -> None:
        """Test that all search arguments are passed through correctly."""
        # Arrange
        request = CallToolRequest(
            params={
                "name": "knowledge_search",
                "arguments": {
                    "query": "test query",
                    "n_results": 5,
                    "filter_dict": {"document_type": "standard"},
                    "score_threshold": 0.7,
                },
            }
        )

        # Act
        await server.server.request_handlers[CallToolRequest](request)

        # Assert
        mock_embedder.embed.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_search_handles_empty_results(
        self,
        server: KnowledgeMCPServer,
        mock_embedder: AsyncMock,
        mock_store: MagicMock,
    ) -> None:
        """Test that search handles empty results gracefully."""
        # Arrange
        mock_embedder.embed.return_value = [0.1] * 1536
        mock_store.search.return_value = []
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "nonexistent query"}}
        )

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        import json
        data = json.loads(response.root.content[0].text)
        assert data["total_results"] == 0
        assert data["results"] == []


class TestKnowledgeStats:
    """Tests for knowledge_stats tool handler."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create a mock embedder."""
        return AsyncMock()

    @pytest.fixture
    def mock_store(self) -> MagicMock:
        """Create a mock store with stats."""
        store = MagicMock()
        store.get_stats.return_value = {
            "collection_name": "se_knowledge_base_v1_te3small",
            "total_chunks": 1234,
            "vectors_count": 1234,
            "config": {
                "vector_size": 1536,
                "distance": "cosine",
            },
        }
        return store

    @pytest.fixture
    def server(
        self,
        mock_embedder: AsyncMock,
        mock_store: MagicMock,
    ) -> KnowledgeMCPServer:
        """Create server instance with mocked dependencies."""
        return KnowledgeMCPServer(
            name="test-server",
            embedder=mock_embedder,
            store=mock_store,
        )

    @pytest.mark.asyncio
    async def test_stats_returns_collection_info(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that stats returns collection information."""
        # Arrange
        request = CallToolRequest(params={"name": "knowledge_stats", "arguments": {}})

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        assert len(response.root.content) == 1
        assert response.root.content[0].type == "text"

        import json
        data = json.loads(response.root.content[0].text)
        assert data["collection_name"] == "se_knowledge_base_v1_te3small"
        assert data["total_chunks"] == 1234
        assert data["vectors_count"] == 1234

    @pytest.mark.asyncio
    async def test_stats_calls_store_get_stats(
        self,
        server: KnowledgeMCPServer,
        mock_store: MagicMock,
    ) -> None:
        """Test that stats handler calls store.get_stats()."""
        # Arrange
        request = CallToolRequest(params={"name": "knowledge_stats", "arguments": {}})

        # Act
        await server.server.request_handlers[CallToolRequest](request)

        # Assert
        mock_store.get_stats.assert_called_once()


class TestErrorHandling:
    """Tests for error handling in tool handlers."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create a mock embedder."""
        return AsyncMock()

    @pytest.fixture
    def mock_store(self) -> MagicMock:
        """Create a mock store."""
        return MagicMock()

    @pytest.fixture
    def server(
        self,
        mock_embedder: AsyncMock,
        mock_store: MagicMock,
    ) -> KnowledgeMCPServer:
        """Create server instance with mocked dependencies."""
        return KnowledgeMCPServer(
            name="test-server",
            embedder=mock_embedder,
            store=mock_store,
        )

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that unknown tools return structured error response."""
        # Arrange
        request = CallToolRequest(params={"name": "unknown_tool", "arguments": {}})

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        import json
        data = json.loads(response.root.content[0].text)
        assert data["isError"] is True
        assert "Unknown tool: unknown_tool" in data["error"]

    @pytest.mark.asyncio
    async def test_search_error_returns_empty_results_gracefully(
        self,
        server: KnowledgeMCPServer,
        mock_embedder: AsyncMock,
    ) -> None:
        """Test that search errors are handled gracefully by SemanticSearcher."""
        # Arrange
        mock_embedder.embed.side_effect = Exception("Embedding failed")
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert - SemanticSearcher returns empty list on error
        import json
        data = json.loads(response.root.content[0].text)
        assert data["total_results"] == 0
        assert data["results"] == []

    @pytest.mark.asyncio
    async def test_stats_error_returns_structured_error(
        self,
        server: KnowledgeMCPServer,
        mock_store: MagicMock,
    ) -> None:
        """Test that stats errors return structured error response."""
        # Arrange
        mock_store.get_stats.side_effect = ConnectionError("Store unavailable")
        request = CallToolRequest(params={"name": "knowledge_stats", "arguments": {}})

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        import json
        data = json.loads(response.root.content[0].text)
        assert data["isError"] is True
        assert "Store unavailable" in data["error"]
