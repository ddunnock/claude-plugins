# Coding Conventions

**Analysis Date:** 2026-03-08

## Monorepo Context

This workspace (`mcps/`) contains multiple MCP servers. The primary project is `knowledge-mcp/` (Python, well-structured). Secondary projects `session-memory/` and `streaming-output/` are simpler single-file servers. Conventions below focus on `knowledge-mcp/` as the canonical reference; follow the same patterns when adding new MCP servers.

## Naming Patterns

**Files:**
- Use `snake_case.py` for all Python modules: `pdf_ingestor.py`, `semantic_search.py`, `token_tracker.py`
- Abstract base classes go in `base.py` within their package: `embed/base.py`, `store/base.py`, `ingest/base.py`
- Test files mirror source structure with `test_` prefix: `test_hybrid.py`, `test_qdrant_store.py`

**Functions:**
- Use `snake_case` for all functions and methods: `add_chunks()`, `embed_batch()`, `health_check()`
- Private methods use single underscore prefix: `_ensure_dependencies()`, `_handle_shutdown()`, `_to_search_result()`
- Factory functions use `create_` prefix: `create_store()`, `create_engine_and_session_factory()`
- Handler functions use `handle_` prefix: `handle_acquire()`, `handle_explore()`, `handle_ingest()`

**Variables:**
- Use `snake_case` for all variables: `query_embedding`, `n_results`, `filter_dict`
- Constants use `UPPER_SNAKE_CASE`: `ALL_EXCEPTIONS`, `TEST_OPENAI_API_KEY`
- Private instance attributes use single underscore: `self._semantic`, `self._bm25`, `self._searcher`

**Types/Classes:**
- Use `PascalCase` for all classes: `KnowledgeChunk`, `HybridSearcher`, `BaseStore`, `SearchResult`
- Exception classes end with `Error`: `ConfigurationError`, `IngestionError`, `RateLimitError`
- Base classes use `Base` prefix: `BaseStore`, `BaseEmbedder`, `BaseIngestor`
- Config classes end with `Config`: `KnowledgeConfig`, `CoverageConfig`

**Packages:**
- Use `snake_case` for package directories: `knowledge_mcp`, `search`, `embed`, `ingest`

## Code Style

**Formatting:**
- Tool: Ruff (configured in `knowledge-mcp/pyproject.toml`)
- Line length: 100 characters
- Target version: Python 3.11
- Run: `poetry run ruff format src tests`

**Linting:**
- Tool: Ruff with extensive rule set
- Rules enabled: E, W, F, I, B, C4, UP, ARG, SIM, TCH, PTH, ERA, PL, RUF, D
- Ignored: D100 (module docstrings optional), D104 (package docstrings optional)
- Run: `poetry run ruff check src tests`

**Type Checking:**
- Tool: Pyright in `strict` mode
- Config: `[tool.pyright]` in `knowledge-mcp/pyproject.toml`
- Scope: `src/` only (tests excluded)
- All unused imports and variables are errors
- Run: `poetry run pyright`

## Import Organization

**Order (enforced by Ruff isort):**
1. `from __future__ import annotations` (ALWAYS first line in every file -- 67/67 source files use this)
2. Standard library imports
3. Third-party imports
4. First-party imports (`knowledge_mcp.*`)

**Path Aliases:**
- No path aliases used; all imports are absolute from package root
- Example: `from knowledge_mcp.search.hybrid import HybridSearcher`

**TYPE_CHECKING pattern (used in 38 files):**
```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk
    from knowledge_mcp.utils.config import KnowledgeConfig
```
- Use `TYPE_CHECKING` to avoid circular imports and reduce runtime import costs
- Place type-only imports inside the `if TYPE_CHECKING:` block
- This is the standard pattern for all files that need types for annotations only

## Docstrings

**Style:** Google-style docstrings (enforced by Ruff `pydocstyle` with `convention = "google"`)

**Required on:**
- All public classes (with `Attributes:` section)
- All public methods (with `Args:`, `Returns:`, `Raises:`, `Example:` sections)
- All modules (top-level module docstring)

**Pattern:**
```python
def search(
    self,
    query: str,
    n_results: int = 10,
    filter_dict: dict[str, Any] | None = None,
) -> list[SearchResult]:
    """
    Perform hybrid search combining semantic and BM25 results.

    Retrieves 2x n_results from each searcher, merges via RRF, and returns
    top n_results. If BM25 index not built, falls back to semantic only.

    Args:
        query: Natural language search query.
        n_results: Number of results to return. Defaults to 10.
        filter_dict: Metadata filters to apply to semantic search.

    Returns:
        List of SearchResult objects ordered by RRF score (highest first).
        Empty list if query is empty or no results found.

    Example:
        >>> results = await hybrid.search("system requirements", n_results=5)
    """
```

**Exception docstrings include:**
- When to use the exception
- Example raise statement
- Hierarchy position shown in module docstring (see `knowledge-mcp/src/knowledge_mcp/exceptions.py`)

## Error Handling

**Exception hierarchy (defined in `knowledge-mcp/src/knowledge_mcp/exceptions.py`):**
```
KnowledgeMCPError (base)
  ConfigurationError (config_error)
  ConnectionError (connection_error)
  TimeoutError (timeout_error)
  AuthenticationError (auth_error)
  NotFoundError (not_found)
  ValidationError (invalid_input)
  RateLimitError (rate_limited)
  InternalError (internal_error)
  IngestionError (ingestion_error)
```

**Patterns:**
- Always use specific exception types from the hierarchy, never bare `except Exception`
- Each exception has an `error_code` class attribute for MCP responses
- Use `to_dict()` for serializing errors in MCP tool responses
- Catch broad exceptions only at boundaries (MCP tool handlers, CLI entry points)
- Use `# noqa: BLE001` annotation when broad exception catch is intentional (see `knowledge-mcp/src/knowledge_mcp/embed/base.py` line 172)

**MCP tool error response pattern (from `knowledge-mcp/src/knowledge_mcp/server.py`):**
```python
try:
    results = await self._searcher.search(query)
    return [TextContent(type="text", text=json.dumps({"results": results}))]
except ConnectionError:
    logger.error("Vector store connection failed: %s", e)
    return [TextContent(type="text", text=json.dumps({
        "error": "Knowledge base temporarily unavailable",
        "message": str(e),
        "retryable": True,
        "results": [],  # Always include empty results to prevent hallucination
    }))]
except Exception:
    return [TextContent(type="text", text=json.dumps({
        "error": "Search failed",
        "retryable": False,
        "results": [],
    }))]
```

## Logging

**Framework:** Python stdlib `logging`

**Pattern (used consistently across 22+ modules):**
```python
import logging

logger = logging.getLogger(__name__)
```

**When to log:**
- `logger.info()`: Successful operations with metrics (e.g., "Hybrid search completed: %d semantic + %d BM25 -> %d fused results")
- `logger.warning()`: Degraded behavior, fallbacks (e.g., "BM25 index not built, falling back to semantic search only")
- `logger.error()`: Failures that return error responses
- Use `%s` string formatting (not f-strings) in logger calls for lazy evaluation

**Structured logging support:**
- `knowledge-mcp/src/knowledge_mcp/monitoring/logger.py` provides JSON logging setup
- `knowledge-mcp/src/knowledge_mcp/utils/logging.py` provides additional utilities

## Data Models

**Two patterns used:**

1. **Dataclasses** for domain models (`knowledge-mcp/src/knowledge_mcp/models/chunk.py`, `knowledge-mcp/src/knowledge_mcp/models/document.py`):
```python
@dataclass
class KnowledgeChunk:
    id: str
    document_id: str
    content: str
    embedding: Optional[list[float]] = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

2. **Pydantic BaseModel** for configuration and validation (`knowledge-mcp/src/knowledge_mcp/utils/config.py`):
```python
class KnowledgeConfig(BaseModel):
    openai_api_key: str = Field(default="", description="OpenAI API key")
    embedding_dimensions: int = Field(default=1536, ge=256, le=3072)
```

**Use dataclasses for:** Domain objects (chunks, documents, parsed elements)
**Use Pydantic for:** Configuration, external input validation

## Abstract Base Classes

**Pattern for extensibility (used in `embed/`, `store/`, `ingest/`, `search/strategies/`):**
```python
from abc import ABC, abstractmethod

class BaseStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: list[KnowledgeChunk]) -> int: ...

    @abstractmethod
    def search(self, query_embedding: list[float], ...) -> list[dict[str, Any]]: ...
```
- Define ABC in `base.py` within each package
- Concrete implementations in separate files: `qdrant_store.py`, `chromadb_store.py`
- Use `__init__.py` for public API exports with `__all__`

## Module Design

**Exports:**
- Every `__init__.py` defines an explicit `__all__` list
- Public API re-exported from package `__init__.py` for convenience imports
- Optional dependencies handled with try/except in `__init__.py` (see `knowledge-mcp/src/knowledge_mcp/search/__init__.py` for Reranker example)

**Factory pattern:**
- `create_store()` in `knowledge-mcp/src/knowledge_mcp/store/__init__.py` creates the right store based on config with automatic fallback
- Constructor dependency injection used for testability (see `KnowledgeMCPServer.__init__()`)

## Session-Memory Conventions

`session-memory/server.py` is a single-file MCP server with different style:
- Uses old-style typing (`Dict`, `List`, `Optional` from `typing`)
- No type checking enforcement
- Plugin pattern via `session-memory/plugins/base.py` with class inheritance
- Direct `sqlite3` usage (no ORM)
- `try/except ImportError` for optional dependencies (`dotenv`, `openai`)

When modifying `session-memory/`, follow its existing style. When creating new MCP servers, follow `knowledge-mcp/` conventions.

## Commit Messages

Follow Conventional Commits:
```
feat(store): add hybrid search support for Qdrant
fix(ingest): handle malformed PDF metadata
docs(readme): update installation instructions
test(chunk): add hierarchical chunker tests
refactor(embed): extract base embedder interface
```

---

*Convention analysis: 2026-03-08*
