# Phase 2: Search Layer - Research

**Researched:** 2026-01-23
**Domain:** Python semantic search orchestration
**Confidence:** HIGH

## Summary

Researched implementation patterns for a semantic search layer that orchestrates async embedding generation and vector store querying. The standard approach involves a thin wrapper class that:
1. Validates and sanitizes text queries using Pydantic
2. Embeds queries asynchronously using the embedder interface
3. Searches the vector store with metadata filtering
4. Formats results with scores and metadata

The search layer should be stateless, delegating all storage to the vector store and all embedding to the embedder. Error handling focuses on graceful degradation (return empty list) rather than raising exceptions for user-facing queries.

**Primary recommendation:** Keep the SemanticSearcher simple - validate input with Pydantic, await embedder, call store.search(), format results. Don't hand-roll query preprocessing, score normalization, or caching at this layer.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Pydantic | 2.x | Input validation | Industry standard for FastAPI/ML input sanitization, Rust-backed performance |
| asyncio | stdlib | Async orchestration | Native Python async/await, required for async embedder |
| typing | stdlib | Type hints | Pyright strict mode compliance |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-asyncio | latest | Async test support | Testing async search methods |
| unittest.mock | stdlib | Mocking embedder/store | Unit tests without API calls |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pydantic validation | Manual checks | Pydantic provides automatic type coercion, better errors, and is already in stack |
| Native async | Threading | asyncio matches embedder interface, better for I/O-bound operations |

**Installation:**
```bash
# Already in pyproject.toml from Phase 1
poetry add pydantic  # v2.x
poetry add --group dev pytest-asyncio
```

## Architecture Patterns

### Recommended Project Structure
```
src/knowledge_mcp/search/
├── __init__.py              # Export SemanticSearcher
├── semantic_search.py       # SemanticSearcher class
└── models.py                # Pydantic request/response models
```

### Pattern 1: Async Orchestration with Error Handling
**What:** Coordinate async embedder call with sync store search, handling errors at each stage
**When to use:** Always - this is the core pattern for semantic search layers

**Example:**
```python
# Source: Standard async orchestration pattern
from typing import Any
from knowledge_mcp.embed.base import BaseEmbedder
from knowledge_mcp.store.base import BaseStore

class SemanticSearcher:
    """Orchestrates embedding and vector search."""

    def __init__(self, embedder: BaseEmbedder, store: BaseStore):
        self.embedder = embedder
        self.store = store

    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: dict[str, Any] | None = None,
        score_threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Semantic search with async embedding and sync store search.

        Returns empty list on error rather than raising - graceful degradation.
        """
        # Validate input
        if not query or not query.strip():
            return []

        try:
            # Step 1: Embed query (async)
            query_embedding = await self.embedder.embed(query.strip())

            # Step 2: Search store (sync, but fast)
            results = self.store.search(
                query_embedding=query_embedding,
                n_results=n_results,
                filter_dict=filter_dict,
                score_threshold=score_threshold,
            )

            return results

        except Exception as e:
            # Log error but return empty list for graceful degradation
            # In production, use proper logging
            print(f"Search error: {e}")
            return []
```

### Pattern 2: Pydantic Validation for Request Parameters
**What:** Validate search parameters using Pydantic models before processing
**When to use:** When exposing search through MCP tools or API endpoints

**Example:**
```python
# Source: Pydantic validation best practices
from pydantic import BaseModel, Field, field_validator

class SearchRequest(BaseModel):
    """Validated search request."""

    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(default=10, ge=1, le=100)
    document_type: str | None = Field(default=None, max_length=50)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator('query')
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        """Strip whitespace and normalize."""
        return v.strip()

class SearchResult(BaseModel):
    """Single search result."""

    id: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any]
```

### Pattern 3: Result Formatting with Score Validation
**What:** Ensure search results from store have consistent structure
**When to use:** Always - validate store outputs before returning to caller

**Example:**
```python
def _format_results(
    self,
    raw_results: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Format and validate results from vector store.

    Ensures all results have required fields with correct types.
    """
    formatted = []
    for result in raw_results:
        # Validate required fields exist
        if not all(k in result for k in ['id', 'content', 'score', 'metadata']):
            continue  # Skip malformed results

        # Ensure score is in valid range (some stores return cosine -1 to 1)
        score = result['score']
        if score < 0:
            score = (score + 1) / 2  # Normalize [-1, 1] to [0, 1]

        formatted.append({
            'id': result['id'],
            'content': result['content'],
            'score': min(max(score, 0.0), 1.0),  # Clamp to [0, 1]
            'metadata': result['metadata'],
        })

    return formatted
```

### Anti-Patterns to Avoid

- **Caching embeddings at search layer:** Caching belongs at the embedder or ingestion layer, not in the search orchestrator. Adds complexity without benefit.
- **Synchronous embedding in async method:** Don't use `embedder.embed()` without await - blocks the event loop
- **Raising exceptions for empty queries:** Return empty list instead - makes MCP tools more robust
- **Complex score transformations:** Vector stores already normalize scores appropriately. Don't add custom normalization unless you have specific requirements and tests.
- **Mixing search logic with business logic:** SemanticSearcher should only orchestrate embedding + search. Metadata filtering decisions belong in the caller.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Input validation | Manual string checks | Pydantic models | Handles type coercion, provides better errors, faster (Rust-backed) |
| Async mocking | Custom async test helpers | pytest-asyncio + unittest.mock | Standard pytest plugin, handles event loop management |
| Empty/whitespace queries | Custom regex validation | `str.strip()` + length check | Simple, readable, handles all whitespace types |
| Score normalization | Custom score scaling | Use store scores as-is | Qdrant/ChromaDB already return 0-1 scores, premature optimization |
| Query preprocessing | Stemming/lemmatization | Rely on embedding model | Modern embeddings (text-embedding-3-small) handle this internally |

**Key insight:** The search layer is an orchestrator, not a processor. Its job is to validate, call the right components, and format results. All the hard work (embedding, vector search, score calculation) happens in specialized components.

## Common Pitfalls

### Pitfall 1: Blocking Async Event Loop
**What goes wrong:** Calling synchronous store.search() in an async method blocks the event loop if it's slow
**Why it happens:** Vector store interfaces are sync, but searches can take 10-100ms
**How to avoid:** Use `asyncio.to_thread()` if store searches become a bottleneck (measure first)
**Warning signs:** MCP tools feel sluggish, async health checks time out

```python
# If needed (measure first!):
results = await asyncio.to_thread(
    self.store.search,
    query_embedding=query_embedding,
    n_results=n_results,
)
```

### Pitfall 2: Not Handling Empty or Whitespace Queries
**What goes wrong:** Embedder receives empty string, raises error, search fails
**Why it happens:** User input from MCP tools can be empty, only whitespace, or accidental
**How to avoid:** Check `if not query.strip()` and return empty list early
**Warning signs:** Cryptic embedding API errors, failed searches with no user feedback

### Pitfall 3: Forgetting to Strip Query Text
**What goes wrong:** Query " kubernetes  " embeds differently than "kubernetes", cache misses, inconsistent results
**Why it happens:** MCP tool calls may have trailing whitespace from user input
**How to avoid:** Always `query.strip()` before embedding
**Warning signs:** Duplicate embeddings for same query, cache inefficiency

### Pitfall 4: Raising Exceptions for User Errors
**What goes wrong:** Empty query raises ValueError, MCP tool shows error to user, bad UX
**Why it happens:** Developer habit to validate early and raise exceptions
**How to avoid:** Distinguish user errors (return empty list) from system errors (raise exception)
**Warning signs:** Users see error messages for natural interactions like empty searches

### Pitfall 5: Testing with Real Embeddings API
**What goes wrong:** Unit tests are slow, cost money, fail when API is down, hit rate limits
**Why it happens:** Not mocking the embedder in tests
**How to avoid:** Use unittest.mock for embedder in unit tests, reserve real API for integration tests
**Warning signs:** Test suite takes minutes, CI fails intermittently, rising OpenAI bills

### Pitfall 6: Not Validating n_results Range
**What goes wrong:** User requests 10,000 results, query is slow, returns too much data
**Why it happens:** No upper bound on n_results parameter
**How to avoid:** Use Pydantic `Field(ge=1, le=100)` to enforce sensible limits
**Warning signs:** Occasional very slow queries, large response payloads

## Code Examples

Verified patterns from research and standard practices:

### Complete SemanticSearcher Implementation
```python
# Source: Standard async orchestration + Pydantic validation patterns
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from knowledge_mcp.embed.base import BaseEmbedder
    from knowledge_mcp.store.base import BaseStore


class SearchRequest(BaseModel):
    """Validated search request parameters."""

    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(default=10, ge=1, le=100)
    filter_dict: dict[str, Any] | None = Field(default=None)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator('query')
    @classmethod
    def strip_query(cls, v: str) -> str:
        """Strip whitespace from query."""
        return v.strip()


class SemanticSearcher:
    """
    Semantic search orchestrator.

    Coordinates async embedding generation with vector store search.
    Stateless - delegates all storage to vector store, all embedding to embedder.

    Example:
        >>> searcher = SemanticSearcher(embedder, store)
        >>> results = await searcher.search("system requirements", n_results=5)
        >>> len(results) <= 5
        True
    """

    def __init__(self, embedder: BaseEmbedder, store: BaseStore):
        """
        Initialize semantic searcher.

        Args:
            embedder: Async embedder for generating query embeddings
            store: Vector store for similarity search
        """
        self.embedder = embedder
        self.store = store

    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: dict[str, Any] | None = None,
        score_threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Search for semantically similar content.

        Args:
            query: Natural language search query
            n_results: Maximum results to return (1-100)
            filter_dict: Optional metadata filters (e.g., {"document_type": "standard"})
            score_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of search results, each containing:
                - id: Chunk identifier
                - content: Text content
                - score: Similarity score (0-1, higher is better)
                - metadata: Chunk metadata dict

        Returns empty list on error or empty query (graceful degradation).

        Example:
            >>> results = await searcher.search(
            ...     query="functional requirements",
            ...     n_results=5,
            ...     filter_dict={"normative": True},
            ...     score_threshold=0.7,
            ... )
            >>> all(r['score'] >= 0.7 for r in results)
            True
        """
        # Validate and sanitize input
        try:
            request = SearchRequest(
                query=query,
                n_results=n_results,
                filter_dict=filter_dict,
                score_threshold=score_threshold,
            )
        except Exception:
            # Invalid input - return empty list
            return []

        # Empty query after stripping - return empty list
        if not request.query:
            return []

        try:
            # Step 1: Generate query embedding (async)
            query_embedding = await self.embedder.embed(request.query)

            # Step 2: Search vector store (sync but fast)
            results = self.store.search(
                query_embedding=query_embedding,
                n_results=request.n_results,
                filter_dict=request.filter_dict,
                score_threshold=request.score_threshold,
            )

            return results

        except Exception as e:
            # System error - log and return empty list for graceful degradation
            # In production, use proper logging with context
            import logging
            logging.error(f"Search failed: {e}", exc_info=True)
            return []

    async def health_check(self) -> bool:
        """
        Check if search layer components are healthy.

        Returns:
            True if both embedder and store are accessible, False otherwise.
        """
        try:
            # Check embedder
            embedder_healthy = await self.embedder.health_check()
            if not embedder_healthy:
                return False

            # Check store
            store_healthy = self.store.health_check()
            return store_healthy

        except Exception:
            return False
```

### Testing Pattern with Mocks
```python
# Source: pytest-asyncio + unittest.mock standard patterns
import pytest
from unittest.mock import AsyncMock, MagicMock

from knowledge_mcp.search.semantic_search import SemanticSearcher


@pytest.fixture
def mock_embedder():
    """Mock embedder that returns predictable vectors."""
    embedder = AsyncMock()
    embedder.embed.return_value = [0.1] * 1536  # Fixed embedding
    embedder.health_check.return_value = True
    embedder.dimensions = 1536
    return embedder


@pytest.fixture
def mock_store():
    """Mock vector store that returns test results."""
    store = MagicMock()
    store.search.return_value = [
        {
            'id': 'chunk-1',
            'content': 'Test content',
            'score': 0.95,
            'metadata': {'source': 'test.pdf'},
        }
    ]
    store.health_check.return_value = True
    return store


@pytest.fixture
def searcher(mock_embedder, mock_store):
    """SemanticSearcher with mocked dependencies."""
    return SemanticSearcher(embedder=mock_embedder, store=mock_store)


@pytest.mark.asyncio
async def test_search_returns_results(searcher, mock_embedder, mock_store):
    """Test that search orchestrates embedder and store correctly."""
    # Act
    results = await searcher.search("test query", n_results=5)

    # Assert
    assert len(results) == 1
    assert results[0]['content'] == 'Test content'
    assert results[0]['score'] == 0.95

    # Verify calls
    mock_embedder.embed.assert_called_once_with("test query")
    mock_store.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_empty_query_returns_empty_list(searcher, mock_embedder):
    """Test that empty query returns empty list without calling embedder."""
    # Act
    results = await searcher.search("")

    # Assert
    assert results == []
    mock_embedder.embed.assert_not_called()


@pytest.mark.asyncio
async def test_search_whitespace_query_returns_empty_list(searcher, mock_embedder):
    """Test that whitespace-only query returns empty list."""
    # Act
    results = await searcher.search("   ")

    # Assert
    assert results == []
    mock_embedder.embed.assert_not_called()


@pytest.mark.asyncio
async def test_search_strips_whitespace(searcher, mock_embedder, mock_store):
    """Test that query whitespace is stripped before embedding."""
    # Act
    await searcher.search("  test query  ", n_results=5)

    # Assert - embedder receives stripped query
    mock_embedder.embed.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_search_passes_filters(searcher, mock_embedder, mock_store):
    """Test that metadata filters are passed to store."""
    # Act
    filter_dict = {"document_type": "standard"}
    await searcher.search("query", filter_dict=filter_dict)

    # Assert
    call_args = mock_store.search.call_args
    assert call_args.kwargs['filter_dict'] == filter_dict


@pytest.mark.asyncio
async def test_search_handles_embedder_error(searcher, mock_embedder):
    """Test graceful degradation when embedder fails."""
    # Arrange
    mock_embedder.embed.side_effect = Exception("API error")

    # Act
    results = await searcher.search("test query")

    # Assert - returns empty list, doesn't raise
    assert results == []


@pytest.mark.asyncio
async def test_search_handles_store_error(searcher, mock_embedder, mock_store):
    """Test graceful degradation when store fails."""
    # Arrange
    mock_store.search.side_effect = Exception("Connection error")

    # Act
    results = await searcher.search("test query")

    # Assert - returns empty list, doesn't raise
    assert results == []
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| LangChain wrappers | Direct embedder + store | 2024-2025 | Simpler stack, fewer abstractions, easier debugging |
| Manual score normalization | Use store native scores | 2024 | Vector stores (Qdrant, Pinecone) now standardize on 0-1 range |
| Sync-only search | Async/await patterns | 2023-2024 | Better throughput for I/O-bound embedding calls |
| Thread pools for embeddings | Native asyncio | 2024 | Simpler code, better for MCP server event loop |
| Custom validation logic | Pydantic v2 | 2023 | Rust-backed validation 10x faster, better errors |

**Deprecated/outdated:**
- **LangChain VectorStore wrapper:** Adds abstraction layer without value when you control both embedder and store interfaces
- **FAISS for production:** Good for local testing, but Qdrant/Pinecone offer better filtering, metadata, and cloud features
- **Manual async-to-sync wrapping:** Python 3.11+ has better native asyncio support, use `asyncio.to_thread()` if needed
- **Sentence Transformers for cloud deployments:** OpenAI embeddings have better quality and no model management overhead

## Open Questions

Things that couldn't be fully resolved:

1. **Should SemanticSearcher use asyncio.to_thread() for store.search()?**
   - What we know: Vector store search is sync, typically 10-100ms
   - What's unclear: Whether this blocks event loop enough to matter in MCP server context
   - Recommendation: Start without `to_thread()`, measure latency in integration tests, add if needed

2. **Should result formatting validate/transform scores from store?**
   - What we know: Qdrant returns 0-1 scores, ChromaDB returns cosine -1 to 1
   - What's unclear: Whether to normalize at search layer or expect store to handle it
   - Recommendation: Document store interface requirement for 0-1 scores, add runtime assertion

3. **How to handle very long queries (>8K tokens for text-embedding-3-small)?**
   - What we know: OpenAI embedding models have token limits
   - What's unclear: Should search layer truncate, or let embedder raise error?
   - Recommendation: Let embedder handle it (embedder knows its limits), search layer returns empty list on error

## Sources

### Primary (HIGH confidence)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) - Official v2 validation patterns
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html) - Standard async patterns
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/) - Async test patterns

### Secondary (MEDIUM confidence)
- [How to Build a Semantic Search Engine in Python | deepset Blog](https://www.deepset.ai/blog/how-to-build-a-semantic-search-engine-in-python) - General architecture patterns
- [Build a semantic search engine in Python - Vikas Paruchuri](https://www.vikas.sh/post/semantic-search-guide) - Simplicity principles
- [Qdrant Filtering Documentation](https://qdrant.tech/documentation/concepts/filtering/) - Metadata filter patterns
- [Comprehensive Guide to Filtering in Qdrant | Medium](https://medium.com/@vandriichuk/comprehensive-guide-to-filtering-in-qdrant-9fa5e9ad8e7b) - Advanced filtering patterns
- [3 essential async patterns for building a Python service | Elastic Blog](https://www.elastic.co/blog/async-patterns-building-python-service) - Async orchestration
- [Pydantic Validation Layers: Secure Python ML Input Sanitization 2025](https://johal.in/pydantic-validation-layers-secure-python-ml-input-sanitization-2025/) - Input validation for ML
- [OpenSearch vector search performance guide 2026](https://www.instaclustr.com/education/opensearch/opensearch-vector-search-the-basics-and-a-quick-tutorial-2026-guide/) - Query optimization
- [Fake Embeddings | LangChain](https://python.langchain.com/docs/integrations/text_embedding/fake/) - Testing patterns

### Tertiary (LOW confidence)
- [Building effective hybrid search in OpenSearch 2026](https://opensearch.org/blog/building-effective-hybrid-search-in-opensearch-techniques-and-best-practices/) - Score normalization techniques
- [Vector Search Resource Optimization Guide - Qdrant](https://qdrant.tech/articles/vector-search-resource-optimization/) - Performance best practices
- [The Complete Guide to RAG and Vector Databases in 2026](https://solvedbycode.ai/blog/complete-guide-rag-vector-databases-2026) - Architecture overview

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Pydantic, asyncio, and pytest-asyncio are established Python standards
- Architecture: HIGH - Simple orchestrator pattern is well-established for RAG systems
- Pitfalls: HIGH - Based on common async Python mistakes and validation errors observed in production systems

**Research date:** 2026-01-23
**Valid until:** 2026-02-23 (30 days - Python libraries stable, patterns are mature)
