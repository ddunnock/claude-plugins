# src/knowledge_mcp/server.py
"""
MCP server implementation for Knowledge MCP.

This module provides the main MCP server that exposes knowledge search
tools to AI assistants via the Model Context Protocol.

The server supports:
    - Semantic search over technical documents
    - Definition lookup
    - Requirements search
    - Keyword search
    - Health checks and statistics

Example:
    >>> server = KnowledgeMCPServer()
    >>> await server.run()

    # Or via CLI:
    $ python -m knowledge_mcp
"""

from __future__ import annotations

import signal
import sys
from typing import TYPE_CHECKING, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

if TYPE_CHECKING:
    from mcp.types import TextContent, Tool


class KnowledgeMCPServer:
    """
    MCP server for semantic search over technical reference documents.

    Provides MCP tools for searching IEEE standards, INCOSE guides,
    NASA handbooks, and other systems engineering reference materials.

    Attributes:
        server: The underlying MCP Server instance.
        name: Server name for identification.

    Example:
        >>> server = KnowledgeMCPServer()
        >>> await server.run()
    """

    def __init__(self, name: str = "knowledge-mcp") -> None:
        """
        Initialize the Knowledge MCP server.

        Args:
            name: Server name for identification in MCP protocol.
        """
        self.name = name
        self.server = Server(name)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """
        Register MCP protocol handlers.

        Sets up handlers for:
            - list_tools: Returns available tool definitions
            - call_tool: Dispatches tool invocations
        """

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:  # pyright: ignore[reportUnusedFunction]
            """Return list of available tools."""
            # Tools will be registered in TASK-024
            return []

        @self.server.call_tool()
        async def handle_call_tool(  # pyright: ignore[reportUnusedFunction]
            name: str,
            arguments: dict[str, Any],
        ) -> list[TextContent]:
            """
            Handle tool invocations.

            Args:
                name: Name of the tool to invoke.
                arguments: Tool arguments as a dictionary.

            Returns:
                List of content items (TextContent, etc.)
            """
            # Tool implementations will be added in Phase 5
            from mcp.types import TextContent

            return [
                TextContent(
                    type="text",
                    text=f"Tool '{name}' not yet implemented",
                )
            ]

    async def run(self) -> None:
        """
        Run the MCP server on stdio transport.

        This method blocks until the server is shut down via
        SIGINT (Ctrl+C) or SIGTERM.

        Raises:
            RuntimeError: If server fails to start.

        Example:
            >>> import asyncio
            >>> server = KnowledgeMCPServer()
            >>> asyncio.run(server.run())
        """
        # Set up graceful shutdown handlers
        loop = None
        try:
            import asyncio

            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if loop and sys.platform != "win32":
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._handle_shutdown)

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

    def _handle_shutdown(self) -> None:
        """Handle graceful shutdown on SIGINT/SIGTERM."""
        import asyncio

        # Get the current task and cancel it gracefully
        try:
            loop = asyncio.get_running_loop()
            for task in asyncio.all_tasks(loop):
                task.cancel()
        except RuntimeError:
            pass


async def main() -> None:
    """
    Entry point for running the MCP server.

    This function is called from __main__.py when running
    the package as a module.

    Example:
        >>> import asyncio
        >>> asyncio.run(main())
    """
    server = KnowledgeMCPServer()
    await server.run()
