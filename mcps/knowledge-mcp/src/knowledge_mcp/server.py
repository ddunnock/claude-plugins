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

import asyncio
import json
import signal
import sys
from typing import TYPE_CHECKING, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from knowledge_mcp.embed import BaseEmbedder, OpenAIEmbedder
from knowledge_mcp.embed.cache import EmbeddingCache
from knowledge_mcp.monitoring.token_tracker import TokenTracker
from knowledge_mcp.search import SemanticSearcher
from knowledge_mcp.store import BaseStore, create_store
from knowledge_mcp.utils.config import load_config

if TYPE_CHECKING:
    from knowledge_mcp.utils.config import KnowledgeConfig


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

    def __init__(
        self,
        name: str = "knowledge-mcp",
        embedder: BaseEmbedder | None = None,
        store: BaseStore | None = None,
    ) -> None:
        """
        Initialize the Knowledge MCP server.

        Args:
            name: Server name for identification in MCP protocol.
            embedder: Optional embedder instance. If None, creates from config.
            store: Optional store instance. If None, creates from config.
        """
        self.name = name
        self.server = Server(name)

        # Lazy initialization: only create dependencies if not provided
        self._config: KnowledgeConfig | None = None
        self._embedder = embedder
        self._store = store
        self._searcher: SemanticSearcher | None = None

        self._setup_handlers()

    def _ensure_dependencies(self) -> None:
        """Initialize dependencies lazily when server runs (not in tests)."""
        if self._searcher is not None:
            return

        # Load config if not using injected dependencies
        if self._config is None:
            self._config = load_config()

        # Create embedder if not provided
        if self._embedder is None:
            # Create cache if enabled
            cache: EmbeddingCache | None = None
            if self._config.cache_enabled:
                cache = EmbeddingCache(
                    self._config.cache_dir,
                    self._config.embedding_model,
                    size_limit=self._config.cache_size_limit,
                )

            # Create tracker if enabled
            tracker: TokenTracker | None = None
            if self._config.token_tracking_enabled:
                tracker = TokenTracker(
                    self._config.token_log_file,
                    self._config.embedding_model,
                    daily_warning_threshold=self._config.daily_token_warning_threshold,
                )

            # Create embedder with cache and tracker
            self._embedder = OpenAIEmbedder(
                api_key=self._config.openai_api_key,
                model=self._config.embedding_model,
                dimensions=self._config.embedding_dimensions,
                cache=cache,
                token_tracker=tracker,
            )

        # Create store if not provided
        if self._store is None:
            self._store = create_store(self._config)

        # Create searcher
        self._searcher = SemanticSearcher(self._embedder, self._store)

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
            return [
                Tool(
                    name="knowledge_search",
                    description="""Search the systems engineering knowledge base for relevant information.

Use this to find:
- Standards requirements (IEEE, ISO, INCOSE)
- Best practices and guidance
- Technical definitions
- Process descriptions

The search uses semantic similarity to find relevant content even when exact keywords don't match.

Backend: Vector search with OpenAI embeddings (text-embedding-3-small).""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query (e.g., 'system requirements review')"
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (1-100)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "filter_dict": {
                                "type": "object",
                                "description": "Optional metadata filters (e.g., {'document_type': 'standard', 'normative': true})",
                                "additionalProperties": True
                            },
                            "score_threshold": {
                                "type": "number",
                                "description": "Minimum similarity score (0-1) for results",
                                "default": 0.0,
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="knowledge_stats",
                    description="""Get statistics about the knowledge base collection.

Returns information about:
- Total number of chunks stored
- Collection name
- Vector store configuration
- Document count (if available)

Use this to verify the knowledge base is populated and accessible.""",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
            ]

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
            try:
                # Ensure dependencies are initialized
                self._ensure_dependencies()

                if name == "knowledge_search":
                    return await self._handle_knowledge_search(arguments)
                elif name == "knowledge_stats":
                    return await self._handle_knowledge_stats(arguments)
                else:
                    # Unknown tool - return error response
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "error": f"Unknown tool: {name}",
                                "isError": True
                            }, indent=2)
                        )
                    ]
            except Exception as e:
                # Catch all exceptions and return structured error
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "error": str(e),
                            "isError": True
                        }, indent=2)
                    )
                ]

    async def _handle_knowledge_search(self, arguments: dict[str, Any]) -> list[TextContent]:
        """
        Handle knowledge_search tool invocation.

        Args:
            arguments: Tool arguments with query, n_results, filter_dict, score_threshold.

        Returns:
            List containing formatted search results as TextContent.
        """
        # Extract arguments with defaults
        query: str = arguments.get("query", "")
        n_results: int = arguments.get("n_results", 10)
        filter_dict: dict[str, Any] | None = arguments.get("filter_dict")
        score_threshold: float = arguments.get("score_threshold", 0.0)

        # Perform search
        assert self._searcher is not None
        results = await self._searcher.search(
            query=query,
            n_results=n_results,
            filter_dict=filter_dict,
            score_threshold=score_threshold,
        )

        # Format results for LLM consumption
        formatted_results: list[dict[str, Any]] = []
        for result in results:
            result_dict: dict[str, Any] = {
                "content": result.content,
                "score": result.score,
                "source": {
                    "document_title": result.document_title,
                    "document_type": result.document_type,
                    "section_title": result.section_title,
                    "section_hierarchy": result.section_hierarchy,
                    "clause_number": result.clause_number,
                    "page_numbers": result.page_numbers,
                },
                "metadata": {
                    "chunk_type": result.chunk_type,
                    "normative": result.normative,
                }
            }
            formatted_results.append(result_dict)

        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "results": formatted_results,
                    "query": query,
                    "total_results": len(formatted_results),
                }, indent=2)
            )
        ]

    async def _handle_knowledge_stats(self, arguments: dict[str, Any]) -> list[TextContent]:
        """
        Handle knowledge_stats tool invocation.

        Args:
            arguments: Tool arguments (currently none required).

        Returns:
            List containing collection statistics as TextContent.
        """
        # Call store.get_stats() in thread pool (sync method)
        assert self._store is not None
        stats = await asyncio.to_thread(self._store.get_stats)

        return [
            TextContent(
                type="text",
                text=json.dumps(stats, indent=2)
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
