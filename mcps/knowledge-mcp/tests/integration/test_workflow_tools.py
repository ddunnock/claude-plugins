"""Integration tests for workflow MCP tools.

Verifies that workflow tools are correctly registered in the server
and have proper input schemas.

These tests verify tool registration without invoking the full MCP protocol.
"""

from __future__ import annotations

import pytest

from knowledge_mcp.server import KnowledgeMCPServer
from knowledge_mcp.tools.workflows import handle_explore, handle_plan, handle_rcca, handle_trade


class TestWorkflowToolsImport:
    """Tests that workflow tool handlers can be imported."""

    def test_workflow_handlers_importable(self) -> None:
        """Test that all workflow handlers can be imported."""
        # If imports succeed, handlers are available
        assert handle_rcca is not None
        assert handle_trade is not None
        assert handle_explore is not None
        assert handle_plan is not None


class TestWorkflowToolsRegistration:
    """Tests for workflow tools registration in MCP server."""

    @pytest.fixture
    def server(self) -> KnowledgeMCPServer:
        """Create a server instance for testing."""
        return KnowledgeMCPServer()

    def test_server_initializes_with_workflow_imports(self, server: KnowledgeMCPServer) -> None:
        """Test that server initializes successfully with workflow tool imports."""
        # If server init succeeds, all imports and registrations worked
        assert server is not None
        assert server.server is not None

    def test_server_has_handler_methods(self, server: KnowledgeMCPServer) -> None:
        """Test that server has workflow tool handler methods."""
        assert hasattr(server, "_handle_knowledge_rcca")
        assert hasattr(server, "_handle_knowledge_trade")
        assert hasattr(server, "_handle_knowledge_explore")
        assert hasattr(server, "_handle_knowledge_plan")

        # Verify methods are callable
        assert callable(server._handle_knowledge_rcca)
        assert callable(server._handle_knowledge_trade)
        assert callable(server._handle_knowledge_explore)
        assert callable(server._handle_knowledge_plan)


class TestWorkflowToolSchemas:
    """Tests for workflow tool input schemas in tool definitions.

    Note: Testing actual MCP protocol interaction is complex and requires
    full MCP client setup. These tests verify the tool definitions are
    present in the source code.
    """

    def test_server_module_has_tool_definitions(self) -> None:
        """Test that server module source contains workflow tool definitions."""
        import knowledge_mcp.server as server_module
        import inspect

        source = inspect.getsource(server_module)

        # Verify tool names appear in source
        assert "knowledge_rcca" in source
        assert "knowledge_trade" in source
        assert "knowledge_explore" in source
        assert "knowledge_plan" in source

    def test_workflow_tools_have_required_schemas(self) -> None:
        """Test that workflow tool schemas include required fields."""
        import knowledge_mcp.server as server_module
        import inspect

        source = inspect.getsource(server_module)

        # Each workflow tool should have inputSchema with query
        assert 'name="knowledge_rcca"' in source
        assert '"query"' in source  # All tools require query parameter
        assert '"project_id"' in source  # All tools accept project_id


class TestToolHandlerCallability:
    """Tests that tool handlers can be called with proper arguments."""

    @pytest.mark.asyncio
    async def test_handle_rcca_signature(self) -> None:
        """Test handle_rcca accepts expected parameters."""
        from unittest.mock import AsyncMock

        # Create mock searcher
        mock_searcher = AsyncMock()
        mock_searcher.search = AsyncMock(return_value=[])

        # Should not raise TypeError for valid parameters
        result = await handle_rcca(
            searcher=mock_searcher,
            query="test failure",
            n_results=10,
            score_threshold=0.0,
            project_id=None,
        )

        # Should return dict (even if empty or error)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_handle_trade_signature(self) -> None:
        """Test handle_trade accepts expected parameters."""
        from unittest.mock import AsyncMock

        mock_searcher = AsyncMock()
        mock_searcher.search = AsyncMock(return_value=[])

        result = await handle_trade(
            searcher=mock_searcher,
            query="compare options",
            alternatives=["A", "B"],
            criteria=["cost", "performance"],
            n_results=20,
            score_threshold=0.0,
            project_id=None,
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_handle_explore_signature(self) -> None:
        """Test handle_explore accepts expected parameters."""
        from unittest.mock import AsyncMock

        mock_searcher = AsyncMock()
        mock_searcher.search = AsyncMock(return_value=[])

        result = await handle_explore(
            searcher=mock_searcher,
            query="explore topic",
            facets=["definitions", "examples"],
            n_results=20,
            score_threshold=0.0,
            project_id=None,
        )

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_handle_plan_signature(self) -> None:
        """Test handle_plan accepts expected parameters."""
        from unittest.mock import AsyncMock

        mock_searcher = AsyncMock()
        mock_searcher.search = AsyncMock(return_value=[])

        result = await handle_plan(
            searcher=mock_searcher,
            query="project planning",
            categories=["templates", "risks"],
            n_results=20,
            score_threshold=0.0,
            project_id=None,
        )

        assert isinstance(result, dict)
