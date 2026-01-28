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

from knowledge_mcp.db.engine import create_engine_and_session_factory, get_session
from knowledge_mcp.embed import BaseEmbedder, OpenAIEmbedder
from knowledge_mcp.embed.cache import EmbeddingCache
from knowledge_mcp.monitoring.token_tracker import TokenTracker
from knowledge_mcp.search import SemanticSearcher
from knowledge_mcp.store import BaseStore, create_store
from knowledge_mcp.tools.acquisition import (
    handle_acquire,
    handle_assess,
    handle_ingest,
    handle_preflight,
    handle_request,
    handle_sources,
)
from knowledge_mcp.tools.workflows import (
    handle_explore,
    handle_plan,
    handle_rcca,
    handle_trade,
)
from knowledge_mcp.utils.config import load_config

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

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
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None

        self._setup_handlers()

    def _ensure_dependencies(self) -> None:
        """Initialize dependencies lazily when server runs (not in tests)."""
        if self._searcher is not None:
            return

        # Load config if not using injected dependencies
        if self._config is None:
            self._config = load_config()

        # Create database engine and session factory if not in offline mode
        if (
            self._engine is None
            and not self._config.offline_mode
            and self._config.database_url
        ):
            self._engine, self._session_factory = create_engine_and_session_factory(
                self._config
            )

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
                Tool(  # noqa: E501
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
                            "query": {  # noqa: E501
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
                            "filter_dict": {  # noqa: E501
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
                Tool(  # noqa: E501
                    name="knowledge_ingest",
                    description="""Trigger ingestion of a document or web URL into the knowledge base.

Use this to add new content sources. For web URLs, content is crawled and ingested immediately.
For documents (PDF, DOCX), creates a source record for CLI ingestion.

Parameters:
- url (required): URL or file path to ingest
- source_type: "document", "web", or "standard" (default: "web")
- authority_tier: "tier1" (standards), "tier2" (handbooks), "tier3" (articles) (default: "tier3")
- title: Optional title override

Returns source_id, status, and ingestion details.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL or file path to ingest"
                            },
                            "source_type": {
                                "type": "string",
                                "description": "Type of source: document, web, or standard",
                                "enum": ["document", "web", "standard"],
                                "default": "web"
                            },
                            "authority_tier": {
                                "type": "string",
                                "description": "Authority tier for ranking",
                                "enum": ["tier1", "tier2", "tier3"],
                                "default": "tier3"
                            },
                            "title": {
                                "type": "string",
                                "description": "Optional title override"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="knowledge_sources",
                    description="""List and filter knowledge sources in the database.

Returns sources with their status, type, and metadata.
Use filters to find specific types of content.

Optional filters:
- source_type: Filter by type (document, web, standard)
- status: Filter by status (pending, ingesting, complete, failed)
- authority_tier: Filter by authority (tier1, tier2, tier3)
- limit: Maximum results (default: 50)""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_type": {
                                "type": "string",
                                "description": "Filter by source type",
                                "enum": ["document", "web", "standard"]
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by status",
                                "enum": ["pending", "ingesting", "complete", "failed"]
                            },
                            "authority_tier": {
                                "type": "string",
                                "description": "Filter by authority tier",
                                "enum": ["tier1", "tier2", "tier3"]
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="knowledge_assess",
                    description="""Assess knowledge coverage for specified topics.

Identifies gaps where the knowledge base has low or no coverage.
Returns priority rankings and suggested queries for acquisition.

Use this to identify areas needing more documentation before starting work.

Parameters:
- areas (required): List of knowledge areas/topics to assess
- threshold: Similarity threshold for coverage (default: 0.5)

Returns coverage report with gaps and covered areas.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "areas": {
                                "type": "array",
                                "description": "Knowledge areas to assess",
                                "items": {"type": "string"},
                                "minItems": 1
                            },
                            "threshold": {
                                "type": "number",
                                "description": "Similarity threshold for coverage",
                                "default": 0.5,
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["areas"]
                    }
                ),
                Tool(
                    name="knowledge_preflight",
                    description="""Check if a URL is accessible before acquisition.

Verifies the URL can be reached and has valid format.
Use before knowledge_acquire to validate URLs.

Parameters:
- url (required): URL to check
- check_robots: Whether to check robots.txt (default: true)

Returns accessibility status and any errors.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to check"
                            },
                            "check_robots": {
                                "type": "boolean",
                                "description": "Whether to check robots.txt compliance",
                                "default": True
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="knowledge_acquire",
                    description="""Acquire web content: preflight, create source, and ingest.

Complete workflow for adding web content. Checks accessibility,
creates source record, and ingests content.

This is a convenience tool that combines preflight + ingest.

Parameters:
- url (required): URL to acquire
- authority_tier: Authority level (default: tier3)
- title: Optional title override
- reason: Why this content is needed

Returns acquisition result with source_id and ingestion details.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to acquire"
                            },
                            "authority_tier": {
                                "type": "string",
                                "description": "Authority tier for ranking",
                                "enum": ["tier1", "tier2", "tier3"],
                                "default": "tier3"
                            },
                            "title": {
                                "type": "string",
                                "description": "Optional title override"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Why this content is needed"
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="knowledge_request",
                    description="""Create an acquisition request for content to be added later.

Use when content cannot be acquired immediately (auth required,
manual review needed, etc.). Tracks pending acquisitions.

Parameters:
- url (required): URL to request
- reason: Why this content is needed
- priority: Priority level (1=highest, 5=lowest, default: 3)

Returns request ID and details.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to request"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Why this content is needed"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Priority level (1=highest, 5=lowest)",
                                "default": 3,
                                "minimum": 1,
                                "maximum": 5
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="knowledge_rcca",
                    description="""Search knowledge base for RCCA (Root Cause Corrective Action) analysis.

Specialized for failure analysis workflows. Retrieves information about:
- Failure symptoms and anomalies
- Root causes and contributing factors
- Investigation methods
- Corrective actions and resolutions

Results are structured with RCCA-specific metadata extraction.

Parameters:
- query (required): Failure symptom or issue description
- n_results: Maximum results (default: 10)
- score_threshold: Minimum similarity score (default: 0.0)
- project_id: Optional project ID for query capture

Returns RCCA-structured results with symptom/cause/resolution categorization.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Failure symptom or issue description"
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "score_threshold": {
                                "type": "number",
                                "description": "Minimum similarity score (0-1)",
                                "default": 0.0,
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Optional project ID for query capture"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="knowledge_trade",
                    description="""Search knowledge base for trade study comparison.

Specialized for decision support workflows. Retrieves information about:
- Alternative approaches and technologies
- Evaluation criteria (performance, cost, risk, etc.)
- Quantitative comparisons
- Evidence for decision making

Results are grouped by alternatives with criteria-specific evidence.

Parameters:
- query (required): Decision context or problem statement
- alternatives: List of alternatives to compare
- criteria: List of evaluation criteria
- n_results: Maximum results (default: 20)
- score_threshold: Minimum similarity score (default: 0.0)
- project_id: Optional project ID for query capture

Returns alternatives grouped by criteria with evidence and quantitative data.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Decision context or problem statement"
                            },
                            "alternatives": {
                                "type": "array",
                                "description": "List of alternatives to compare",
                                "items": {"type": "string"}
                            },
                            "criteria": {
                                "type": "array",
                                "description": "List of evaluation criteria",
                                "items": {"type": "string"}
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "score_threshold": {
                                "type": "number",
                                "description": "Minimum similarity score (0-1)",
                                "default": 0.0,
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Optional project ID for query capture"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="knowledge_explore",
                    description="""Search knowledge base for multi-facet topic exploration.

Specialized for comprehensive understanding workflows. Retrieves information from:
- Definitions and terminology
- Examples and use cases
- Standards and requirements
- Best practices and guidance

Results are organized by facets for diverse perspectives on a topic.

Parameters:
- query (required): Topic or concept to explore
- facets: Specific facets to search (overrides defaults)
- n_results: Maximum results (default: 20)
- score_threshold: Minimum similarity score (default: 0.0)
- project_id: Optional project ID for query capture

Returns results organized by facets (definitions, examples, standards, best_practices).""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Topic or concept to explore"
                            },
                            "facets": {
                                "type": "array",
                                "description": "Specific facets to search (overrides defaults)",
                                "items": {"type": "string"}
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "score_threshold": {
                                "type": "number",
                                "description": "Minimum similarity score (0-1)",
                                "default": 0.0,
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Optional project ID for query capture"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="knowledge_plan",
                    description="""Search knowledge base for project planning support.

Specialized for planning workflows. Retrieves information about:
- Templates and frameworks
- Risk identification and mitigation
- Lessons learned from past projects
- Precedents and case studies

Results are organized by planning categories for structured planning support.

Parameters:
- query (required): Planning question or topic
- categories: Specific categories to search (overrides defaults)
- n_results: Maximum results (default: 20)
- score_threshold: Minimum similarity score (default: 0.0)
- project_id: Optional project ID for query capture

Returns results organized by categories (templates, risks, lessons_learned, precedents).""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Planning question or topic"
                            },
                            "categories": {
                                "type": "array",
                                "description": "Specific categories to search (overrides defaults)",
                                "items": {"type": "string"}
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "score_threshold": {
                                "type": "number",
                                "description": "Minimum similarity score (0-1)",
                                "default": 0.0,
                                "minimum": 0.0,
                                "maximum": 1.0
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Optional project ID for query capture"
                            }
                        },
                        "required": ["query"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(  # noqa: PLR0911  # pyright: ignore[reportUnusedFunction]
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
                elif name == "knowledge_ingest":
                    return await self._handle_knowledge_ingest(arguments)
                elif name == "knowledge_sources":
                    return await self._handle_knowledge_sources(arguments)
                elif name == "knowledge_assess":
                    return await self._handle_knowledge_assess(arguments)
                elif name == "knowledge_preflight":
                    return await self._handle_knowledge_preflight(arguments)
                elif name == "knowledge_acquire":
                    return await self._handle_knowledge_acquire(arguments)
                elif name == "knowledge_request":
                    return await self._handle_knowledge_request(arguments)
                elif name == "knowledge_rcca":
                    return await self._handle_knowledge_rcca(arguments)
                elif name == "knowledge_trade":
                    return await self._handle_knowledge_trade(arguments)
                elif name == "knowledge_explore":
                    return await self._handle_knowledge_explore(arguments)
                elif name == "knowledge_plan":
                    return await self._handle_knowledge_plan(arguments)
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

    async def _handle_knowledge_stats(
        self, arguments: dict[str, Any]  # noqa: ARG002
    ) -> list[TextContent]:
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

    async def _handle_knowledge_ingest(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_ingest tool invocation.

        Args:
            arguments: Tool arguments with url, source_type, authority_tier, title.

        Returns:
            List containing ingestion result as TextContent.
        """
        if self._session_factory is None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Database not available (offline mode or not configured)",
                        "isError": True
                    }, indent=2)
                )
            ]

        async with get_session(self._session_factory) as session:
            result = await handle_ingest(
                session=session,
                url=arguments.get("url", ""),
                source_type=arguments.get("source_type", "web"),
                authority_tier=arguments.get("authority_tier", "tier3"),
                title=arguments.get("title"),
            )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_sources(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_sources tool invocation.

        Args:
            arguments: Tool arguments with optional filters.

        Returns:
            List containing sources list as TextContent.
        """
        if self._session_factory is None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Database not available (offline mode or not configured)",
                        "isError": True
                    }, indent=2)
                )
            ]

        async with get_session(self._session_factory) as session:
            result = await handle_sources(
                session=session,
                source_type=arguments.get("source_type"),
                status=arguments.get("status"),
                authority_tier=arguments.get("authority_tier"),
                limit=arguments.get("limit", 50),
            )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_assess(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_assess tool invocation.

        Args:
            arguments: Tool arguments with areas and threshold.

        Returns:
            List containing coverage report as TextContent.
        """
        assert self._searcher is not None
        result = await handle_assess(
            searcher=self._searcher,
            areas=arguments.get("areas", []),
            threshold=arguments.get("threshold", 0.5),
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_preflight(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_preflight tool invocation.

        Args:
            arguments: Tool arguments with url and check_robots.

        Returns:
            List containing preflight result as TextContent.
        """
        result = await handle_preflight(
            url=arguments.get("url", ""),
            check_robots=arguments.get("check_robots", True),
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_acquire(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_acquire tool invocation.

        Args:
            arguments: Tool arguments with url, authority_tier, title, reason.

        Returns:
            List containing acquisition result as TextContent.
        """
        if self._session_factory is None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Database not available (offline mode or not configured)",
                        "isError": True
                    }, indent=2)
                )
            ]

        async with get_session(self._session_factory) as session:
            result = await handle_acquire(
                session=session,
                url=arguments.get("url", ""),
                authority_tier=arguments.get("authority_tier", "tier3"),
                title=arguments.get("title"),
                reason=arguments.get("reason"),
            )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_request(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_request tool invocation.

        Args:
            arguments: Tool arguments with url, reason, priority.

        Returns:
            List containing request details as TextContent.
        """
        if self._session_factory is None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Database not available (offline mode or not configured)",
                        "isError": True
                    }, indent=2)
                )
            ]

        async with get_session(self._session_factory) as session:
            result = await handle_request(
                session=session,
                url=arguments.get("url", ""),
                reason=arguments.get("reason"),
                priority=arguments.get("priority", 3),
            )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_rcca(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_rcca tool invocation.

        Args:
            arguments: Tool arguments with query, n_results, score_threshold, project_id.

        Returns:
            List containing RCCA-structured results as TextContent.
        """
        assert self._searcher is not None
        result = await handle_rcca(
            searcher=self._searcher,
            query=arguments.get("query", ""),
            n_results=arguments.get("n_results", 10),
            score_threshold=arguments.get("score_threshold", 0.0),
            project_id=arguments.get("project_id"),
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_trade(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_trade tool invocation.

        Args:
            arguments: Tool arguments with query, alternatives, criteria, n_results, etc.

        Returns:
            List containing trade study results as TextContent.
        """
        assert self._searcher is not None
        result = await handle_trade(
            searcher=self._searcher,
            query=arguments.get("query", ""),
            alternatives=arguments.get("alternatives"),
            criteria=arguments.get("criteria"),
            n_results=arguments.get("n_results", 20),
            score_threshold=arguments.get("score_threshold", 0.0),
            project_id=arguments.get("project_id"),
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_explore(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_explore tool invocation.

        Args:
            arguments: Tool arguments with query, facets, n_results, score_threshold, project_id.

        Returns:
            List containing exploration results as TextContent.
        """
        assert self._searcher is not None
        result = await handle_explore(
            searcher=self._searcher,
            query=arguments.get("query", ""),
            facets=arguments.get("facets"),
            n_results=arguments.get("n_results", 20),
            score_threshold=arguments.get("score_threshold", 0.0),
            project_id=arguments.get("project_id"),
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_knowledge_plan(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle knowledge_plan tool invocation.

        Args:
            arguments: Tool arguments with query, categories, n_results, score_threshold, project_id.

        Returns:
            List containing planning results as TextContent.
        """
        assert self._searcher is not None
        result = await handle_plan(
            searcher=self._searcher,
            query=arguments.get("query", ""),
            categories=arguments.get("categories"),
            n_results=arguments.get("n_results", 20),
            score_threshold=arguments.get("score_threshold", 0.0),
            project_id=arguments.get("project_id"),
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

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
