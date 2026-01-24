# Phase 3: MCP Tool Implementation - Research

**Researched:** 2026-01-24
**Domain:** MCP Protocol Tool Implementation (Python SDK v1.x)
**Confidence:** HIGH

## Summary

Phase 3 implements the MCP tool handlers that expose the semantic search functionality built in Phase 2 to LLM clients. The codebase already has a skeleton MCP server using `mcp.server.Server` with `list_tools` and `call_tool` decorators. The work involves defining two tools (`knowledge_search` and `knowledge_stats`), wiring them to the existing `SemanticSearcher` and vector store, and implementing proper error handling with `isError` responses.

The MCP Python SDK v1.x (pinned to `>=1.25.0,<2` in pyproject.toml) uses a decorator-based pattern for tool registration. The existing server.py file shows the pattern: `@self.server.list_tools()` returns `list[Tool]` and `@self.server.call_tool()` handles invocations returning `list[TextContent]`. The phase requires adding dependency injection for the embedder and store, defining JSON Schema input schemas, and converting SearchResult objects to MCP TextContent responses.

**Primary recommendation:** Use the existing low-level Server API pattern (already in server.py), add dependency injection via constructor parameters or a factory function, and return search results as JSON-formatted TextContent with proper error handling using `isError: true`.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| mcp | >=1.25.0,<2 | MCP protocol implementation | Official Python SDK, already installed |
| mcp.types | (bundled) | Tool, TextContent, CallToolResult types | Standard MCP type definitions |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json | stdlib | JSON serialization for tool responses | Always - convert SearchResult to JSON string for TextContent |
| pydantic | >=2.0.0 | Input validation | Already used in config, optional for tool args validation |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Low-level Server API | FastMCP decorator API | FastMCP auto-generates schemas from type hints, but existing codebase uses low-level API - switching adds churn |
| Manual JSON Schema | Pydantic model_json_schema() | Pydantic cleaner but adds dependency for simple schemas - manual is fine for 2 tools |

**Installation:**
```bash
# Already installed in pyproject.toml
poetry install
```

## Architecture Patterns

### Recommended Project Structure
```
src/knowledge_mcp/
├── server.py             # MCP server with tool handlers (modify existing)
├── search/
│   ├── __init__.py       # SemanticSearcher, SearchResult (Phase 2 - use as-is)
│   └── semantic_search.py
├── store/
│   └── __init__.py       # create_store factory (use as-is)
└── embed/
    └── __init__.py       # OpenAIEmbedder (use as-is)
```

### Pattern 1: Dependency Injection via Constructor

**What:** Pass embedder and store to KnowledgeMCPServer at construction time
**When to use:** When the server lifecycle manages external dependencies
**Example:**
```python
# Source: MCP SDK patterns + existing codebase
from knowledge_mcp.search import SemanticSearcher
from knowledge_mcp.store import create_store
from knowledge_mcp.embed import OpenAIEmbedder
from knowledge_mcp.utils.config import load_config

class KnowledgeMCPServer:
    def __init__(
        self,
        name: str = "knowledge-mcp",
        searcher: SemanticSearcher | None = None,
        store: BaseStore | None = None,
    ) -> None:
        self.name = name
        self.server = Server(name)

        # Lazy initialization - create on first use if not injected
        self._searcher = searcher
        self._store = store
        self._config = None

        self._setup_handlers()

    @property
    def searcher(self) -> SemanticSearcher:
        if self._searcher is None:
            config = self._get_config()
            embedder = OpenAIEmbedder(api_key=config.openai_api_key)
            store = create_store(config)
            self._searcher = SemanticSearcher(embedder, store)
            self._store = store
        return self._searcher

    @property
    def store(self) -> BaseStore:
        if self._store is None:
            # Force searcher creation which creates store
            _ = self.searcher
        assert self._store is not None
        return self._store
```

### Pattern 2: Tool Definition with JSON Schema

**What:** Define tools with `mcp.types.Tool` and JSON Schema inputSchema
**When to use:** All tool definitions in list_tools handler
**Example:**
```python
# Source: MCP SDK documentation + mcpcat.io guides
from mcp.types import Tool

@self.server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="knowledge_search",
            description="""Search the systems engineering knowledge base.

Use this to find:
- Standards requirements (IEEE, ISO, INCOSE)
- Best practices and guidance
- Technical definitions

Returns ranked results with content, score, and source citations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Filter by document type (standard, handbook, guide)",
                        "enum": ["standard", "handbook", "guide"]
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="knowledge_stats",
            description="Get statistics about the knowledge base collection.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]
```

### Pattern 3: Error Handling with isError

**What:** Return structured error responses using TextContent with isError flag
**When to use:** Any tool execution failure that should be communicated to the LLM
**Example:**
```python
# Source: MCP SDK GitHub issues + error handling guides
from mcp.types import TextContent
import json

@self.server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any],
) -> list[TextContent]:
    try:
        if name == "knowledge_search":
            return await self._handle_search(arguments)
        elif name == "knowledge_stats":
            return await self._handle_stats()
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}),
            )]
    except Exception as e:
        # Return error in structured format with isError indication
        # Note: isError is on CallToolResult, but we return TextContent
        # The caller can detect errors by checking JSON content
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "isError": True,
            }),
        )]
```

### Anti-Patterns to Avoid

- **stdout logging:** Never use print() or write to stdout - it corrupts JSON-RPC messages. Use stderr or Python logging configured for stderr.
- **Bare exception swallowing:** Always log exceptions before returning error responses.
- **Unvalidated arguments:** Validate tool arguments before using them - missing required fields should return clear error messages.
- **Blocking I/O in handlers:** All tool handlers are async - ensure embedder.embed() and store calls are awaited properly.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema for inputs | Manual validation code | JSON Schema in inputSchema + Pydantic | LLM clients validate against schema automatically |
| Store/embedder lifecycle | Global singletons | Dependency injection via constructor | Testable, allows mocking for unit tests |
| Error serialization | Custom error format | Standard `{"error": message, "isError": true}` | LLMs expect consistent error structure |
| Tool result formatting | Custom serializer | `json.dumps()` with SearchResult fields | Simple, predictable, debuggable |

**Key insight:** MCP tools are thin wrappers around existing functionality. The SearchResult dataclass from Phase 2 already has all the fields needed - just serialize it to JSON.

## Common Pitfalls

### Pitfall 1: stdout Pollution

**What goes wrong:** Any print() or stdout write corrupts MCP JSON-RPC protocol
**Why it happens:** Python print() defaults to stdout, developers add debug prints
**How to avoid:**
- Use `logging` module configured for stderr
- Never use print() in server code
- Check all dependencies don't write to stdout
**Warning signs:** MCP client hangs or receives malformed JSON

### Pitfall 2: Exception as Success Response

**What goes wrong:** SDK catches exceptions and sends them as successful response with exception text
**Why it happens:** Known SDK issue - exceptions in call_tool handlers become TextContent with exception message
**How to avoid:**
- Wrap all handler code in try/except
- Catch specific exceptions and return structured error JSON
- Include `"isError": true` in error response JSON
**Warning signs:** LLM receives error text as if it were valid results

### Pitfall 3: Hanging on Embedder/Store Errors

**What goes wrong:** Tool call hangs indefinitely if embedder or store is unavailable
**Why it happens:** No timeout on external service calls, no graceful degradation
**How to avoid:**
- Store and embedder have health_check() methods - use them
- Add timeouts to external calls
- Return clear error message if services unavailable
**Warning signs:** Tool calls never complete

### Pitfall 4: Missing Configuration Validation

**What goes wrong:** Server starts but tools fail with cryptic errors
**Why it happens:** Environment variables not set, config not validated at startup
**How to avoid:**
- Validate config in server constructor
- Fail fast with clear error message if OPENAI_API_KEY or QDRANT_URL missing
- Log configuration state at startup (to stderr)
**Warning signs:** First tool call fails with auth/connection error

### Pitfall 5: Blocking Store.get_stats()

**What goes wrong:** stats tool blocks event loop
**Why it happens:** store.get_stats() is synchronous, but called from async handler
**How to avoid:**
- Run sync store methods in thread pool executor
- Or wrap in asyncio.to_thread()
**Warning signs:** Server becomes unresponsive during stats call

## Code Examples

Verified patterns from official sources and existing codebase:

### Complete Tool Handler Implementation

```python
# Source: MCP SDK patterns + existing server.py structure
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.server import Server
from mcp.types import TextContent, Tool

if TYPE_CHECKING:
    from knowledge_mcp.search import SearchResult, SemanticSearcher
    from knowledge_mcp.store.base import BaseStore

logger = logging.getLogger(__name__)


class KnowledgeMCPServer:
    def __init__(
        self,
        name: str = "knowledge-mcp",
        searcher: SemanticSearcher | None = None,
        store: BaseStore | None = None,
    ) -> None:
        self.name = name
        self.server = Server(name)
        self._searcher = searcher
        self._store = store
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="knowledge_search",
                    description="""Search the systems engineering knowledge base.

Use this to find standards requirements, best practices, and technical definitions
from IEEE, INCOSE, and NASA documents.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query",
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Number of results (1-50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="knowledge_stats",
                    description="Get knowledge base statistics (document count, chunk count).",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: dict[str, Any],
        ) -> list[TextContent]:
            try:
                if name == "knowledge_search":
                    return await self._handle_search(arguments)
                elif name == "knowledge_stats":
                    return await self._handle_stats()
                else:
                    return self._error_response(f"Unknown tool: {name}")
            except Exception as e:
                logger.exception("Tool execution failed: %s", name)
                return self._error_response(str(e))

    async def _handle_search(self, arguments: dict[str, Any]) -> list[TextContent]:
        query = arguments.get("query", "")
        if not query:
            return self._error_response("Query is required")

        n_results = min(max(arguments.get("n_results", 10), 1), 50)

        results = await self.searcher.search(query, n_results=n_results)

        # Convert SearchResult objects to serializable format
        response = {
            "query": query,
            "results": [self._format_result(r) for r in results],
            "total": len(results),
        }
        return [TextContent(type="text", text=json.dumps(response, indent=2))]

    def _format_result(self, result: SearchResult) -> dict[str, Any]:
        return {
            "content": result.content,
            "score": round(result.score, 4),
            "document_title": result.document_title,
            "section_title": result.section_title,
            "document_type": result.document_type,
            "normative": result.normative,
            "clause_number": result.clause_number,
        }

    async def _handle_stats(self) -> list[TextContent]:
        import asyncio
        # Run sync method in thread to avoid blocking
        stats = await asyncio.to_thread(self.store.get_stats)
        return [TextContent(type="text", text=json.dumps(stats, indent=2))]

    def _error_response(self, message: str) -> list[TextContent]:
        return [TextContent(
            type="text",
            text=json.dumps({"error": message, "isError": True}),
        )]
```

### Testing Tool Handlers

```python
# Source: pytest-asyncio patterns + MCP SDK testing
import pytest
from unittest.mock import AsyncMock, MagicMock

from knowledge_mcp.server import KnowledgeMCPServer
from knowledge_mcp.search.models import SearchResult


@pytest.fixture
def mock_searcher():
    searcher = MagicMock()
    searcher.search = AsyncMock(return_value=[
        SearchResult(
            id="chunk-1",
            content="Test content",
            score=0.95,
            document_title="IEEE 15288",
            section_title="Requirements",
        )
    ])
    return searcher


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.get_stats.return_value = {"total_chunks": 100}
    return store


@pytest.fixture
def server(mock_searcher, mock_store):
    return KnowledgeMCPServer(
        searcher=mock_searcher,
        store=mock_store,
    )


class TestKnowledgeSearch:
    async def test_search_returns_results(self, server, mock_searcher):
        # Get the call_tool handler
        handlers = server.server._tool_handlers
        result = await handlers["call_tool"]("knowledge_search", {"query": "test"})

        assert len(result) == 1
        assert result[0].type == "text"
        # Parse JSON response
        import json
        data = json.loads(result[0].text)
        assert "results" in data
        assert len(data["results"]) == 1

    async def test_search_empty_query_returns_error(self, server):
        result = await server._handle_search({"query": ""})
        import json
        data = json.loads(result[0].text)
        assert data.get("isError") is True
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| mcp 0.x with different API | mcp 1.x with Server.list_tools/call_tool | Nov 2024 | Stable decorator-based API |
| FastMCP only | Both FastMCP and low-level Server | Dec 2024 | Choice of abstraction level |
| No outputSchema | Optional outputSchema for structured responses | v1.20+ | Better LLM integration |

**Deprecated/outdated:**
- mcp 0.x API: Completely different, do not reference old examples
- v2.0 pre-alpha: In development, not for production - stick with v1.x

## Open Questions

Things that couldn't be fully resolved:

1. **CallToolResult vs list[TextContent] return type**
   - What we know: call_tool handler returns list[TextContent], but isError is on CallToolResult
   - What's unclear: How to properly signal isError at protocol level with current API
   - Recommendation: Include `"isError": true` in JSON text content as workaround; monitor SDK updates

2. **Async store.get_stats()**
   - What we know: BaseStore.get_stats() is sync, call_tool handlers are async
   - What's unclear: Whether asyncio.to_thread() is appropriate for Qdrant client
   - Recommendation: Use asyncio.to_thread() for now, profile if performance issues arise

## Sources

### Primary (HIGH confidence)
- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk) - Low-level Server API patterns
- [MCP Official Docs - Build Server](https://modelcontextprotocol.io/docs/develop/build-server) - Tool implementation patterns
- [PyPI mcp package](https://pypi.org/project/mcp/) - Version 1.25.0 documentation

### Secondary (MEDIUM confidence)
- [MCP SDK GitHub Issues #396](https://github.com/modelcontextprotocol/python-sdk/issues/396) - Exception handling behavior
- [DeepWiki MCP Python SDK](https://deepwiki.com/modelcontextprotocol/python-sdk) - Low-level Server documentation
- [MCPcat Error Handling Guide](https://mcpcat.io/guides/error-handling-custom-mcp-servers/) - Error handling patterns

### Tertiary (LOW confidence)
- Various Medium articles on MCP patterns (verified against official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using official MCP SDK already installed
- Architecture: HIGH - Patterns verified against official examples and existing codebase
- Pitfalls: MEDIUM - Based on GitHub issues and community reports, not direct testing

**Research date:** 2026-01-24
**Valid until:** 2026-02-24 (30 days - SDK stable at v1.x)
