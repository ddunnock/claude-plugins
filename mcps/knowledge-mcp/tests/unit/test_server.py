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
    async def test_list_tools_returns_all_tools(self, server: KnowledgeMCPServer) -> None:
        """Test that list_tools returns all knowledge tools."""
        # Arrange
        request = ListToolsRequest()

        # Act
        response = await server.server.request_handlers[ListToolsRequest](request)

        # Assert - Should have original + Phase 1 + Phase 2 workflow + list_collections
        tool_names = [tool.name for tool in response.root.tools]
        # Original tools (v1.0)
        assert "knowledge_search" in tool_names
        assert "knowledge_stats" in tool_names
        # Phase 1 acquisition tools (v2.0)
        assert "knowledge_ingest" in tool_names
        assert "knowledge_sources" in tool_names
        assert "knowledge_assess" in tool_names
        assert "knowledge_preflight" in tool_names
        assert "knowledge_acquire" in tool_names
        assert "knowledge_request" in tool_names
        # Phase 2 workflow tools (v2.0)
        assert "knowledge_rcca" in tool_names
        assert "knowledge_trade" in tool_names
        assert "knowledge_explore" in tool_names
        assert "knowledge_plan" in tool_names
        # Phase 3 collection discovery (v3.0)
        assert "list_collections" in tool_names

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
        """Test that search returns properly formatted results with citations."""
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
        assert "count" in data
        assert data["count"] == 1
        assert data["query"] == "system requirements review"
        assert data["results"][0]["content"] == "Test content about system requirements review"
        # Check citation field is present (FR-3.4)
        assert "citation" in data["results"][0]
        # Check relevance as percentage (FR-5.4)
        assert data["results"][0]["relevance"] == "95%"

    @pytest.mark.asyncio
    async def test_search_includes_source_citations(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that search results include formatted citations."""
        # Arrange
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Act
        response = await server.server.request_handlers[CallToolRequest](request)

        # Assert
        import json
        data = json.loads(response.root.content[0].text)
        result = data["results"][0]

        # Check citation field is present (FR-3.4)
        assert "citation" in result
        # Citation should be formatted: "DOCUMENT, Clause X.Y.Z, p.N"
        assert "IEEE 15288.2" in result["citation"]
        assert "Clause 5.3.1" in result["citation"]

        # Check metadata still available
        assert result["metadata"]["clause_number"] == "5.3.1"
        assert result["metadata"]["page_numbers"] == [42, 43]
        assert result["metadata"]["normative"] is True

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
        assert data["count"] == 0
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
    async def test_search_connection_error_returns_structured_error(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that ConnectionError returns structured error with empty results."""
        # Arrange
        from unittest.mock import patch

        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Mock searcher to raise ConnectionError
        with patch.object(server, "_searcher") as mock_searcher:
            mock_searcher.search.side_effect = ConnectionError("Vector store unreachable")

            # Act
            response = await server.server.request_handlers[CallToolRequest](request)

        # Assert - FR-4.5: Graceful degradation with explicit empty results
        import json
        data = json.loads(response.root.content[0].text)
        assert "error" in data
        assert data["error"] == "Knowledge base temporarily unavailable"
        assert data["retryable"] is True
        assert data["results"] == []  # Explicit empty results - no hallucination

    @pytest.mark.asyncio
    async def test_search_generic_error_returns_structured_error(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that generic Exception returns structured error with empty results."""
        # Arrange
        from unittest.mock import patch

        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Mock searcher to raise generic Exception
        with patch.object(server, "_searcher") as mock_searcher:
            mock_searcher.search.side_effect = Exception("Unexpected error")

            # Act
            response = await server.server.request_handlers[CallToolRequest](request)

        # Assert - FR-4.5: Graceful degradation with explicit empty results
        import json
        data = json.loads(response.root.content[0].text)
        assert "error" in data
        assert data["error"] == "Search failed"
        assert data["retryable"] is False
        assert data["results"] == []  # Explicit empty results - no hallucination

    @pytest.mark.asyncio
    async def test_search_error_response_has_required_fields(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that error responses have all required fields."""
        # Arrange
        from unittest.mock import patch

        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Mock searcher to raise ConnectionError
        with patch.object(server, "_searcher") as mock_searcher:
            mock_searcher.search.side_effect = ConnectionError("Store down")

            # Act
            response = await server.server.request_handlers[CallToolRequest](request)

        # Assert - Error response structure
        import json
        data = json.loads(response.root.content[0].text)
        assert "error" in data
        assert "message" in data
        assert "retryable" in data
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 0

    @pytest.mark.asyncio
    async def test_search_error_logs_appropriately(
        self,
        server: KnowledgeMCPServer,
    ) -> None:
        """Test that errors are logged before returning."""
        # Arrange
        from unittest.mock import patch
        import logging

        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test query"}}
        )

        # Mock searcher and logger
        with patch.object(server, "_searcher") as mock_searcher:
            mock_searcher.search.side_effect = ConnectionError("Store unreachable")

            with patch("knowledge_mcp.server.logger") as mock_logger:
                # Act
                await server.server.request_handlers[CallToolRequest](request)

                # Assert - Logger was called with error
                mock_logger.error.assert_called_once()
                error_call = mock_logger.error.call_args[0][0]
                assert "Vector store connection failed" in error_call

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


class TestEnsureDependencies:
    """Tests for _ensure_dependencies() method with mocked externals."""

    def test_ensure_dependencies_loads_config(self) -> None:
        """Test that _ensure_dependencies loads config when no dependencies provided."""
        from unittest.mock import patch, MagicMock

        # Don't inject dependencies - force real initialization path
        server = KnowledgeMCPServer(name="test")

        with patch("knowledge_mcp.server.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.cache_enabled = False
            mock_config.token_tracking_enabled = False
            mock_load.return_value = mock_config

            with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                mock_embedder_cls.return_value = MagicMock()
                with patch("knowledge_mcp.server.create_store") as mock_create_store:
                    mock_create_store.return_value = MagicMock()
                    with patch("knowledge_mcp.server.SemanticSearcher"):
                        server._ensure_dependencies()
                        mock_load.assert_called_once()

    def test_ensure_dependencies_creates_embedder_with_cache(self) -> None:
        """Test that cache is created when enabled in config."""
        from unittest.mock import patch, MagicMock

        server = KnowledgeMCPServer(name="test")

        with patch("knowledge_mcp.server.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.cache_enabled = True
            mock_config.cache_dir = "/tmp/cache"
            mock_config.embedding_model = "text-embedding-3-small"
            mock_config.cache_size_limit = 100
            mock_config.token_tracking_enabled = False
            mock_load.return_value = mock_config

            with patch("knowledge_mcp.server.EmbeddingCache") as mock_cache_cls:
                mock_cache_cls.return_value = MagicMock()
                with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                    mock_embedder_cls.return_value = MagicMock()
                    with patch("knowledge_mcp.server.create_store") as mock_create_store:
                        mock_create_store.return_value = MagicMock()
                        with patch("knowledge_mcp.server.SemanticSearcher"):
                            server._ensure_dependencies()

                            mock_cache_cls.assert_called_once_with(
                                "/tmp/cache",
                                "text-embedding-3-small",
                                size_limit=100,
                            )

    def test_ensure_dependencies_creates_embedder_with_tracker(self) -> None:
        """Test that tracker is created when enabled in config."""
        from unittest.mock import patch, MagicMock

        server = KnowledgeMCPServer(name="test")

        with patch("knowledge_mcp.server.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.cache_enabled = False
            mock_config.token_tracking_enabled = True
            mock_config.token_log_file = "/tmp/tokens.log"
            mock_config.embedding_model = "text-embedding-3-small"
            mock_config.daily_token_warning_threshold = 1000
            mock_load.return_value = mock_config

            with patch("knowledge_mcp.server.TokenTracker") as mock_tracker_cls:
                mock_tracker_cls.return_value = MagicMock()
                with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                    mock_embedder_cls.return_value = MagicMock()
                    with patch("knowledge_mcp.server.create_store") as mock_create_store:
                        mock_create_store.return_value = MagicMock()
                        with patch("knowledge_mcp.server.SemanticSearcher"):
                            server._ensure_dependencies()

                            mock_tracker_cls.assert_called_once_with(
                                "/tmp/tokens.log",
                                "text-embedding-3-small",
                                daily_warning_threshold=1000,
                            )

    def test_ensure_dependencies_creates_store(self) -> None:
        """Test that create_store is called when no store provided."""
        from unittest.mock import patch, MagicMock

        server = KnowledgeMCPServer(name="test")

        with patch("knowledge_mcp.server.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.cache_enabled = False
            mock_config.token_tracking_enabled = False
            mock_load.return_value = mock_config

            with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                mock_embedder_cls.return_value = MagicMock()
                with patch("knowledge_mcp.server.create_store") as mock_create_store:
                    mock_store = MagicMock()
                    mock_create_store.return_value = mock_store
                    with patch("knowledge_mcp.server.SemanticSearcher"):
                        server._ensure_dependencies()

                        mock_create_store.assert_called_once_with(mock_config)

    def test_ensure_dependencies_creates_searcher(self) -> None:
        """Test that SemanticSearcher is created with embedder and store."""
        from unittest.mock import patch, MagicMock

        server = KnowledgeMCPServer(name="test")

        with patch("knowledge_mcp.server.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.cache_enabled = False
            mock_config.token_tracking_enabled = False
            mock_load.return_value = mock_config

            with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                mock_embedder = MagicMock()
                mock_embedder_cls.return_value = mock_embedder
                with patch("knowledge_mcp.server.create_store") as mock_create_store:
                    mock_store = MagicMock()
                    mock_create_store.return_value = mock_store
                    with patch("knowledge_mcp.server.SemanticSearcher") as mock_searcher_cls:
                        server._ensure_dependencies()

                        mock_searcher_cls.assert_called_once_with(mock_embedder, mock_store)

    def test_ensure_dependencies_skips_if_already_initialized(self) -> None:
        """Test that _ensure_dependencies is idempotent."""
        from unittest.mock import patch, MagicMock

        mock_embedder = MagicMock()
        mock_store = MagicMock()
        server = KnowledgeMCPServer(
            name="test",
            embedder=mock_embedder,
            store=mock_store,
        )

        # Initialize searcher to simulate already initialized state
        with patch("knowledge_mcp.server.SemanticSearcher") as mock_searcher_cls:
            mock_searcher_cls.return_value = MagicMock()
            server._ensure_dependencies()
            first_call_count = mock_searcher_cls.call_count

            # Call again - should not reinitialize
            server._ensure_dependencies()
            assert mock_searcher_cls.call_count == first_call_count

    def test_ensure_dependencies_uses_injected_embedder(self) -> None:
        """Test that provided embedder is used instead of creating new one."""
        from unittest.mock import patch, MagicMock

        mock_embedder = MagicMock()
        server = KnowledgeMCPServer(name="test", embedder=mock_embedder)

        with patch("knowledge_mcp.server.load_config") as mock_load:
            mock_config = MagicMock()
            mock_load.return_value = mock_config

            with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                with patch("knowledge_mcp.server.create_store") as mock_create_store:
                    mock_create_store.return_value = MagicMock()
                    with patch("knowledge_mcp.server.SemanticSearcher") as mock_searcher_cls:
                        server._ensure_dependencies()

                        # OpenAIEmbedder should not be called since we injected one
                        mock_embedder_cls.assert_not_called()
                        # But SemanticSearcher should use our injected embedder
                        mock_searcher_cls.assert_called_once()
                        call_args = mock_searcher_cls.call_args
                        assert call_args[0][0] is mock_embedder

    def test_ensure_dependencies_uses_injected_store(self) -> None:
        """Test that provided store is used instead of creating new one."""
        from unittest.mock import patch, MagicMock

        mock_store = MagicMock()
        server = KnowledgeMCPServer(name="test", store=mock_store)

        with patch("knowledge_mcp.server.load_config") as mock_load:
            mock_config = MagicMock()
            mock_config.cache_enabled = False
            mock_config.token_tracking_enabled = False
            mock_load.return_value = mock_config

            with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                mock_embedder_cls.return_value = MagicMock()
                with patch("knowledge_mcp.server.create_store") as mock_create_store:
                    with patch("knowledge_mcp.server.SemanticSearcher") as mock_searcher_cls:
                        server._ensure_dependencies()

                        # create_store should not be called since we injected one
                        mock_create_store.assert_not_called()
                        # But SemanticSearcher should use our injected store
                        mock_searcher_cls.assert_called_once()
                        call_args = mock_searcher_cls.call_args
                        assert call_args[0][1] is mock_store


class TestServerRun:
    """Tests for run() method - use asyncio timeout to prevent blocking."""

    @pytest.mark.asyncio
    async def test_run_sets_up_signal_handlers_unix(self) -> None:
        """Test that signal handlers are added on non-Windows platforms."""
        from unittest.mock import patch, MagicMock, AsyncMock
        import asyncio

        mock_embedder = MagicMock()
        mock_store = MagicMock()
        server = KnowledgeMCPServer(
            name="test",
            embedder=mock_embedder,
            store=mock_store,
        )

        # Mock stdio_server context manager
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch("knowledge_mcp.server.stdio_server", return_value=mock_context):
            with patch.object(server.server, "run", new_callable=AsyncMock):
                with patch("sys.platform", "linux"):
                    # Track signal handler calls
                    handler_calls: list[tuple[Any, Any]] = []
                    original_loop = asyncio.get_running_loop()

                    def mock_add_signal_handler(sig: Any, handler: Any) -> None:
                        handler_calls.append((sig, handler))

                    with patch.object(original_loop, "add_signal_handler", side_effect=mock_add_signal_handler):
                        # Run with short timeout
                        try:
                            await asyncio.wait_for(server.run(), timeout=0.1)
                        except asyncio.TimeoutError:
                            pass

                        # Signal handlers should be added for SIGINT and SIGTERM
                        assert len(handler_calls) >= 2
                        signals = [call[0] for call in handler_calls]
                        import signal
                        assert signal.SIGINT in signals
                        assert signal.SIGTERM in signals

    @pytest.mark.asyncio
    async def test_run_skips_signal_handlers_on_windows(self) -> None:
        """Test that signal handlers are not added on Windows."""
        from unittest.mock import patch, MagicMock, AsyncMock
        import asyncio

        mock_embedder = MagicMock()
        mock_store = MagicMock()
        server = KnowledgeMCPServer(
            name="test",
            embedder=mock_embedder,
            store=mock_store,
        )

        # Mock stdio_server context manager
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()

        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=(mock_read_stream, mock_write_stream))
        mock_context.__aexit__ = AsyncMock(return_value=None)

        with patch("knowledge_mcp.server.stdio_server", return_value=mock_context):
            with patch.object(server.server, "run", new_callable=AsyncMock):
                with patch("sys.platform", "win32"):
                    # Track signal handler calls
                    handler_calls: list[tuple[Any, Any]] = []
                    original_loop = asyncio.get_running_loop()

                    def mock_add_signal_handler(sig: Any, handler: Any) -> None:
                        handler_calls.append((sig, handler))

                    with patch.object(original_loop, "add_signal_handler", side_effect=mock_add_signal_handler):
                        # Run with short timeout
                        try:
                            await asyncio.wait_for(server.run(), timeout=0.1)
                        except asyncio.TimeoutError:
                            pass

                        # No signal handlers should be added on Windows
                        assert len(handler_calls) == 0

    def test_handle_shutdown_cancels_tasks(self) -> None:
        """Test that _handle_shutdown cancels all running tasks."""
        from unittest.mock import patch, MagicMock

        mock_embedder = MagicMock()
        mock_store = MagicMock()
        server = KnowledgeMCPServer(
            name="test",
            embedder=mock_embedder,
            store=mock_store,
        )

        mock_task1 = MagicMock()
        mock_task2 = MagicMock()
        mock_loop = MagicMock()

        with patch("asyncio.get_running_loop", return_value=mock_loop):
            with patch("asyncio.all_tasks", return_value={mock_task1, mock_task2}):
                server._handle_shutdown()

                mock_task1.cancel.assert_called_once()
                mock_task2.cancel.assert_called_once()

    def test_handle_shutdown_handles_no_running_loop(self) -> None:
        """Test that _handle_shutdown handles case when no loop is running."""
        from unittest.mock import patch, MagicMock

        mock_embedder = MagicMock()
        mock_store = MagicMock()
        server = KnowledgeMCPServer(
            name="test",
            embedder=mock_embedder,
            store=mock_store,
        )

        # When no loop is running, get_running_loop raises RuntimeError
        with patch("asyncio.get_running_loop", side_effect=RuntimeError("no running loop")):
            # Should not raise - just return silently
            server._handle_shutdown()


class TestMain:
    """Tests for module-level main() function."""

    @pytest.mark.asyncio
    async def test_main_creates_server_and_runs(self) -> None:
        """Test that main() creates a KnowledgeMCPServer and calls run()."""
        from unittest.mock import patch, MagicMock, AsyncMock

        with patch("knowledge_mcp.server.KnowledgeMCPServer") as MockServer:
            mock_instance = MagicMock()
            mock_instance.run = AsyncMock()
            MockServer.return_value = mock_instance

            from knowledge_mcp.server import main
            await main()

            MockServer.assert_called_once()
            mock_instance.run.assert_called_once()
