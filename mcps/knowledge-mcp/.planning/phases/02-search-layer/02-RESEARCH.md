# Phase 2: Search Layer - Research

**Researched:** 2026-01-23
**Domain:** Semantic search implementation with existing embedder and vector store
**Confidence:** HIGH

## Summary

Phase 2 implements a semantic search layer connecting the existing `OpenAIEmbedder` and `QdrantStore`/`ChromaDBStore` components. The existing codebase already has:
- `OpenAIEmbedder` with `embed()` and `embed_batch()` methods (async)
- `QdrantStore.search()` and `ChromaDBStore.search()` methods accepting query embeddings
- Well-defined result format with `id`, `content`, `metadata`, and `score` fields

The search layer needs to:
1. Accept a text query from the user
2. Generate an embedding using the embedder
3. Execute search against the vector store
4. Return formatted results with content, scores, and metadata

This is a thin orchestration layer rather than a complex component. The stores already implement filtering, scoring, and result formatting.

**Primary recommendation:** Create a `SemanticSearcher` class that composes the embedder and store, providing a simple `search(query: str) -> list[SearchResult]` interface. Use a dataclass for `SearchResult` to provide clean typing.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| qdrant-client | >=1.16.2 | Vector store | Already integrated, proven API |
| openai | >=1.0.0 | Embeddings | Already integrated via OpenAIEmbedder |
| pydantic | >=2.0.0 | Data validation | Used for config, can use for result models |

### Supporting (Already in Project)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tenacity | >=8.0.0 | Retry logic | Already in embedder, reuse pattern |
| dataclasses | stdlib | Result types | SearchResult dataclass |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| dataclass SearchResult | dict | Dataclass provides better typing, IDE support, and validation |
| Thin wrapper | LangChain | Adds dependency, abstracts too much when we have direct control |
| Sync search | Async search | Embedder is async; keep consistency. Can add sync wrapper if needed |

**Installation:** No new packages needed - all dependencies already present.

## Architecture Patterns

### Recommended Project Structure
```
src/knowledge_mcp/
├── search/
│   ├── __init__.py           # Exports SemanticSearcher, SearchResult
│   ├── semantic_search.py    # SemanticSearcher class
│   └── models.py             # SearchResult dataclass (or in models/search.py)
```

### Pattern 1: Composition Over Inheritance

**What:** SemanticSearcher composes embedder and store instances rather than inheriting from them.

**When to use:** Always - this is the standard pattern for search orchestration.

**Example:**
```python
# Source: Standard composition pattern
from dataclasses import dataclass, field
from typing import Optional, Union

from knowledge_mcp.embed import BaseEmbedder
from knowledge_mcp.store import BaseStore


@dataclass
class SearchResult:
    """A single search result with content, score, and metadata."""

    id: str
    content: str
    score: float
    metadata: dict[str, object] = field(default_factory=dict)

    # Source citation fields (FR-3.4)
    document_id: str = ""
    document_title: str = ""
    section_title: str = ""
    section_hierarchy: list[str] = field(default_factory=list)
    clause_number: Optional[str] = None
    page_numbers: list[int] = field(default_factory=list)


class SemanticSearcher:
    """Semantic search combining embedder and vector store."""

    def __init__(
        self,
        embedder: BaseEmbedder,
        store: Union[QdrantStore, ChromaDBStore],
    ) -> None:
        self._embedder = embedder
        self._store = store

    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: Optional[dict[str, object]] = None,
        score_threshold: float = 0.0,
    ) -> list[SearchResult]:
        """Search for relevant content."""
        # Handle empty query gracefully (Success Criterion #4)
        if not query or not query.strip():
            return []

        # Generate embedding
        query_embedding = await self._embedder.embed(query)

        # Search store
        raw_results = self._store.search(
            query_embedding=query_embedding,
            n_results=n_results,
            filter_dict=filter_dict,
            score_threshold=score_threshold,
        )

        # Transform to SearchResult objects
        return [self._to_search_result(r) for r in raw_results]
```

### Pattern 2: Graceful Empty Handling

**What:** Return empty list for edge cases instead of raising exceptions.

**When to use:** For empty queries, no results found, or overly-restrictive filters.

**Example:**
```python
# Source: Success Criterion #4 requirement
async def search(self, query: str, ...) -> list[SearchResult]:
    # Empty query returns empty list
    if not query or not query.strip():
        return []

    try:
        query_embedding = await self._embedder.embed(query)
        results = self._store.search(query_embedding=query_embedding, ...)
        # Empty results is valid - just return empty list
        return [self._to_search_result(r) for r in results]
    except Exception:
        # Log error, but don't propagate for search
        # Could also raise specific SearchError if preferred
        return []
```

### Pattern 3: Result Transformation with Metadata Flattening

**What:** Extract commonly-used metadata fields to top-level SearchResult properties for easier access.

**When to use:** When metadata contains structured fields that consumers need direct access to.

**Example:**
```python
def _to_search_result(self, raw: dict) -> SearchResult:
    """Transform store result to SearchResult."""
    metadata = raw.get("metadata", {})

    return SearchResult(
        id=raw["id"],
        content=raw["content"],
        score=raw["score"],
        metadata=metadata,
        # Flatten citation fields (FR-3.4)
        document_id=metadata.get("document_id", ""),
        document_title=metadata.get("document_title", ""),
        section_title=metadata.get("section_title", ""),
        section_hierarchy=metadata.get("section_hierarchy", []),
        clause_number=metadata.get("clause_number"),
        page_numbers=metadata.get("page_numbers", []),
    )
```

### Anti-Patterns to Avoid

- **Don't re-implement store filtering:** The store already handles filtering well. Don't filter results after retrieval.
- **Don't embed in constructor:** Embedding requires async; keep it in the search method.
- **Don't catch all exceptions silently:** Log errors even if returning empty list.
- **Don't mix sync/async:** Keep the search async since embedder is async.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Filter construction | Custom filter builder | Qdrant's Filter/FieldCondition | Store already handles filter translation |
| Result scoring | Custom ranking | Store's score field | HNSW index provides optimized cosine similarity |
| Embedding caching | Manual cache dict | None (embeddings are cheap for queries) | Query embeddings are small, API calls fast |
| Type validation | Manual isinstance checks | Pydantic/dataclass | Already using pydantic in project |

**Key insight:** The vector stores already implement the complex parts (HNSW search, filtering, scoring). The search layer is just orchestration glue.

## Common Pitfalls

### Pitfall 1: Blocking on Async Embedder

**What goes wrong:** Calling async embed() from sync context causes runtime errors or deadlocks.

**Why it happens:** OpenAIEmbedder.embed() is async, but developer tries to use it synchronously.

**How to avoid:** Keep SemanticSearcher.search() async. If sync interface needed, create separate sync wrapper using `asyncio.run()`.

**Warning signs:** `RuntimeWarning: coroutine was never awaited`

### Pitfall 2: Type Mismatches Between Stores

**What goes wrong:** Assuming identical return formats from QdrantStore and ChromaDBStore.

**Why it happens:** Minor differences in how stores format metadata.

**How to avoid:** Both stores follow the same result format (verified in code review). Use `.get()` with defaults when accessing metadata to be safe.

**Warning signs:** KeyError on metadata access

### Pitfall 3: Not Handling Empty Embeddings

**What goes wrong:** Passing empty string to embedder raises ValidationError.

**Why it happens:** User submits empty search query.

**How to avoid:** Check for empty/whitespace query before calling embedder. Return empty list.

**Warning signs:** `ValidationError: Text cannot be empty`

### Pitfall 4: Score Threshold Confusion

**What goes wrong:** Setting score_threshold too high returns no results; too low returns noise.

**Why it happens:** Cosine similarity scores vary by domain and query type.

**How to avoid:** Default to 0.0 (no threshold). Let consumers set threshold based on their needs. Document that scores are 0-1 for cosine similarity.

**Warning signs:** Zero results for known-good queries, or irrelevant results at bottom

### Pitfall 5: Filter Type Mismatch

**What goes wrong:** Passing wrong type in filter_dict (e.g., string "true" instead of bool True).

**Why it happens:** JSON serialization or user input handling.

**How to avoid:** Document expected filter types. Store already handles type-appropriate matching. For booleans, ensure actual bool values.

**Warning signs:** Filters not working, all or no results returned

## Code Examples

Verified patterns from existing codebase and official sources:

### Complete SemanticSearcher Implementation

```python
# Source: Pattern derived from existing store/embedder APIs
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from knowledge_mcp.embed import BaseEmbedder
    from knowledge_mcp.store.chromadb_store import ChromaDBStore
    from knowledge_mcp.store.qdrant_store import QdrantStore

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """
    A single search result with content, score, and metadata.

    Attributes:
        id: Unique chunk identifier.
        content: The text content of the chunk.
        score: Similarity score (0-1, higher is more similar).
        metadata: Full metadata dictionary from vector store.
        document_id: Source document identifier (FR-3.4).
        document_title: Human-readable document title (FR-3.4).
        section_title: Title of containing section (FR-3.4).
        section_hierarchy: Path through document structure (FR-3.4).
        clause_number: Clause identifier if applicable (FR-3.4).
        page_numbers: Source page references (FR-3.4).
    """

    id: str
    content: str
    score: float
    metadata: dict[str, object] = field(default_factory=dict)

    # Source citation fields (FR-3.4: Return source citation with section references)
    document_id: str = ""
    document_title: str = ""
    document_type: str = ""
    section_title: str = ""
    section_hierarchy: list[str] = field(default_factory=list)
    chunk_type: str = ""
    normative: bool = False
    clause_number: Optional[str] = None
    page_numbers: list[int] = field(default_factory=list)


class SemanticSearcher:
    """
    Semantic search combining embedder and vector store.

    Provides text-to-results search by:
    1. Converting query text to embedding
    2. Searching vector store for similar chunks
    3. Returning formatted results with metadata

    Attributes:
        embedder: Embedding provider for query vectorization.
        store: Vector store backend for similarity search.

    Example:
        >>> from knowledge_mcp.embed import OpenAIEmbedder
        >>> from knowledge_mcp.store import create_store
        >>>
        >>> embedder = OpenAIEmbedder(api_key="...")
        >>> store = create_store(config)
        >>> searcher = SemanticSearcher(embedder, store)
        >>>
        >>> results = await searcher.search("system requirements review")
        >>> for r in results:
        ...     print(f"{r.score:.2f}: {r.document_title} - {r.section_title}")
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        store: Union[QdrantStore, ChromaDBStore],
    ) -> None:
        """
        Initialize semantic searcher.

        Args:
            embedder: Embedding provider (e.g., OpenAIEmbedder).
            store: Vector store (QdrantStore or ChromaDBStore).
        """
        self._embedder = embedder
        self._store = store

    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: Optional[dict[str, object]] = None,
        score_threshold: float = 0.0,
    ) -> list[SearchResult]:
        """
        Search for relevant content by semantic similarity.

        Args:
            query: Natural language search query.
            n_results: Maximum number of results to return. Defaults to 10.
            filter_dict: Metadata filters to apply. Keys are field names.
                Supported fields: document_type, chunk_type, normative, clause_number.
                Example: {"document_type": "standard", "normative": True}
            score_threshold: Minimum similarity score (0-1). Defaults to 0.0.

        Returns:
            List of SearchResult objects ordered by relevance (highest first).
            Empty list if query is empty or no results found.

        Example:
            >>> # Basic search
            >>> results = await searcher.search("SRR requirements")
            >>>
            >>> # Filtered search
            >>> results = await searcher.search(
            ...     query="verification methods",
            ...     filter_dict={"document_type": "standard", "normative": True},
            ...     n_results=5,
            ... )
        """
        # Handle empty query gracefully (Success Criterion #4)
        if not query or not query.strip():
            return []

        try:
            # Generate query embedding
            query_embedding = await self._embedder.embed(query)

            # Search vector store
            raw_results = self._store.search(
                query_embedding=query_embedding,
                n_results=n_results,
                filter_dict=filter_dict,
                score_threshold=score_threshold,
            )

            # Transform to SearchResult objects
            return [self._to_search_result(r) for r in raw_results]

        except Exception as e:
            logger.error("Search failed for query '%s': %s", query[:50], e)
            # Return empty list for graceful degradation
            # Could also raise SearchError if stricter error handling preferred
            return []

    def _to_search_result(self, raw: dict) -> SearchResult:
        """Transform raw store result to SearchResult dataclass."""
        metadata = raw.get("metadata", {})

        return SearchResult(
            id=raw["id"],
            content=raw["content"],
            score=raw["score"],
            metadata=metadata,
            # Flatten citation fields for easy access (FR-3.4)
            document_id=metadata.get("document_id", ""),
            document_title=metadata.get("document_title", ""),
            document_type=metadata.get("document_type", ""),
            section_title=metadata.get("section_title", ""),
            section_hierarchy=metadata.get("section_hierarchy", []),
            chunk_type=metadata.get("chunk_type", ""),
            normative=metadata.get("normative", False),
            clause_number=metadata.get("clause_number"),
            page_numbers=metadata.get("page_numbers", []),
        )
```

### Filter Examples

```python
# Source: Qdrant filtering documentation
# Filter by document type
results = await searcher.search(
    query="verification",
    filter_dict={"document_type": "standard"},
)

# Filter by normative status
results = await searcher.search(
    query="shall requirements",
    filter_dict={"normative": True},
)

# Multiple filters (AND logic applied by stores)
results = await searcher.search(
    query="system requirements",
    filter_dict={
        "document_type": "standard",
        "chunk_type": "requirement",
        "normative": True,
    },
)
```

### Test Pattern

```python
# Source: Project test conventions (AAA pattern)
import pytest
from unittest.mock import AsyncMock, MagicMock

from knowledge_mcp.search import SemanticSearcher, SearchResult


class TestSemanticSearcher:
    """Tests for SemanticSearcher."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create mock embedder."""
        embedder = AsyncMock()
        embedder.embed.return_value = [0.1] * 1536
        return embedder

    @pytest.fixture
    def mock_store(self) -> MagicMock:
        """Create mock store with sample results."""
        store = MagicMock()
        store.search.return_value = [
            {
                "id": "chunk-1",
                "content": "Test content about SRR",
                "score": 0.92,
                "metadata": {
                    "document_id": "ieee-15288",
                    "document_title": "IEEE 15288.2",
                    "document_type": "standard",
                    "section_title": "System Requirements Review",
                    "normative": True,
                },
            }
        ]
        return store

    @pytest.fixture
    def searcher(self, mock_embedder, mock_store) -> SemanticSearcher:
        """Create searcher with mocks."""
        return SemanticSearcher(mock_embedder, mock_store)

    async def test_search_returns_results(self, searcher, mock_embedder, mock_store):
        """Test that search returns properly formatted SearchResult objects."""
        # Act
        results = await searcher.search("SRR requirements")

        # Assert
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].content == "Test content about SRR"
        assert results[0].score == 0.92
        assert results[0].document_title == "IEEE 15288.2"
        assert results[0].normative is True

        mock_embedder.embed.assert_called_once_with("SRR requirements")
        mock_store.search.assert_called_once()

    async def test_empty_query_returns_empty_list(self, searcher):
        """Test that empty query returns empty list without calling embedder."""
        # Act
        results = await searcher.search("")

        # Assert
        assert results == []

    async def test_whitespace_query_returns_empty_list(self, searcher):
        """Test that whitespace-only query returns empty list."""
        # Act
        results = await searcher.search("   ")

        # Assert
        assert results == []

    async def test_no_results_returns_empty_list(self, searcher, mock_store):
        """Test that no matches returns empty list (not error)."""
        # Arrange
        mock_store.search.return_value = []

        # Act
        results = await searcher.search("nonexistent topic xyz")

        # Assert
        assert results == []

    async def test_filter_passed_to_store(self, searcher, mock_store):
        """Test that filter_dict is passed through to store."""
        # Arrange
        filter_dict = {"document_type": "standard", "normative": True}

        # Act
        await searcher.search("test", filter_dict=filter_dict)

        # Assert
        mock_store.search.assert_called_once()
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["filter_dict"] == filter_dict
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Dense-only search | Hybrid (dense + sparse) | Qdrant 1.7+ | Better keyword recall - Phase 3 will add |
| Custom reranking | Cross-encoder reranking | 2024 | Better precision - Phase 3 will add |
| Single embedding model | Model-specific collections | 2024 | Prevents embedding mismatch - already implemented |

**Deprecated/outdated:**
- Manual FAISS management: Use managed vector stores instead
- Sync embedding calls: OpenAI SDK is async-first now

## Open Questions

Things that couldn't be fully resolved:

1. **Sync vs Async Interface**
   - What we know: Embedder is async, stores are sync
   - What's unclear: Do MCP tools need sync or async?
   - Recommendation: Keep search async, add sync wrapper if MCP requires it

2. **Error Propagation vs Graceful Degradation**
   - What we know: Success Criterion #4 says empty query/no results should return empty list
   - What's unclear: Should embedding errors also return empty list, or raise?
   - Recommendation: Return empty list with logging for now; can add strict mode later

3. **Score Threshold Defaults**
   - What we know: Cosine similarity scores vary by content domain
   - What's unclear: What's a good default threshold for this knowledge base?
   - Recommendation: Default to 0.0 (no threshold), let callers tune

## Sources

### Primary (HIGH confidence)
- Existing codebase: `src/knowledge_mcp/store/qdrant_store.py` - search() method implementation
- Existing codebase: `src/knowledge_mcp/store/chromadb_store.py` - search() method implementation
- Existing codebase: `src/knowledge_mcp/embed/openai_embedder.py` - embed() method implementation
- [Qdrant Search Documentation](https://qdrant.tech/documentation/concepts/search/) - Query API patterns
- [Qdrant Filtering Documentation](https://qdrant.tech/documentation/concepts/filtering/) - Filter construction

### Secondary (MEDIUM confidence)
- [Qdrant Semantic Search Tutorial](https://qdrant.tech/documentation/beginner-tutorials/search-beginners/) - Implementation patterns
- [RAG Architecture Best Practices](https://orq.ai/blog/rag-architecture) - Modular design patterns

### Tertiary (LOW confidence)
- [LanceDB Issue #2425](https://github.com/lancedb/lancedb/issues/2425) - Empty result handling bug (different library but same problem space)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing project dependencies
- Architecture: HIGH - Pattern matches existing codebase conventions
- Pitfalls: MEDIUM - Derived from code review and common patterns

**Research date:** 2026-01-23
**Valid until:** 2026-02-23 (30 days - stable patterns)
