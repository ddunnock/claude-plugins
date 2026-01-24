# Architecture Patterns

**Domain:** MCP Server for RAG/Semantic Search
**Researched:** 2026-01-20
**Confidence:** HIGH (based on existing codebase analysis + established patterns)

## Executive Summary

The search layer and CLI should integrate with the existing pipeline architecture by following the established patterns: abstract base classes for extensibility, Pydantic models for data contracts, and factory methods for instantiation. The search layer sits between the store and MCP server layers, composing embedder + store to provide query-centric operations. The CLI operates as a parallel entry point to the MCP server, using the same underlying pipeline components.

## Recommended Architecture

### Component Boundary Diagram

```
                        Entry Points
                    +------------------+
                    |                  |
              +-----+-----+      +-----+-----+
              |MCP Server |      |    CLI    |
              |(server.py)|      | (cli/*.py)|
              +-----+-----+      +-----+-----+
                    |                  |
                    +--------+---------+
                             |
                    +--------v--------+
                    |   Search Layer  |
                    | (search/*.py)   |
                    +--------+--------+
                             |
          +------------------+------------------+
          |                  |                  |
    +-----v-----+      +-----v-----+      +-----v-----+
    | Embedder  |      |   Store   |      | Reranker  |
    | (embed/)  |      | (store/)  |      | (search/) |
    +-----+-----+      +-----+-----+      +-----------+
          |                  |                  |
          +------------------+------------------+
                             |
                    +--------v--------+
                    |     Models      |
                    |   (models/)     |
                    +-----------------+
```

### Component Boundaries

| Component | Responsibility | Depends On | Used By |
|-----------|---------------|------------|---------|
| `MCP Server` | Expose tools via MCP protocol, handle tool dispatch | Search Layer, Config | AI assistants |
| `CLI` | Command-line operations for ingestion and management | Pipeline components, Config | Operators/developers |
| `Search Layer` | Query embedding, retrieval, optional reranking | Embedder, Store, Reranker | MCP Server, CLI |
| `Embedder` | Text-to-vector conversion | OpenAI/Local API | Search Layer, Pipeline |
| `Store` | Vector persistence and retrieval | Qdrant/ChromaDB | Search Layer |
| `Reranker` | Result quality improvement (optional) | Cohere API | Search Layer |
| `Models` | Data contracts (KnowledgeChunk, SearchResult) | Pydantic | All layers |

## Search Layer Architecture

### Pattern: Facade with Strategy

The search layer should use the **Facade pattern** to simplify the search interface while internally using the **Strategy pattern** for different search modes (semantic, hybrid).

```python
# Recommended structure: src/knowledge_mcp/search/

search/
    __init__.py          # Exports: SemanticSearcher, HybridSearcher, create_searcher
    base.py              # BaseSearcher abstract class
    semantic.py          # SemanticSearcher - dense vector only
    hybrid.py            # HybridSearcher - dense + sparse (Qdrant)
    reranker.py          # CohereReranker, BaseReranker
    models.py            # SearchQuery, SearchResult, SearchConfig
```

### BaseSearcher Interface

Follow the existing `BaseStore` and `BaseEmbedder` patterns:

```python
class BaseSearcher(ABC):
    """Abstract interface for search implementations."""

    @abstractmethod
    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: dict[str, Any] | None = None,
        score_threshold: float = 0.0,
    ) -> list[SearchResult]:
        """Execute search and return ranked results."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify all dependencies are accessible."""
        ...
```

### Data Flow: Search Operation

```
1. Query string received
          |
          v
2. Embedder.embed(query) -> query_embedding
          |
          v
3. Store.search(query_embedding, filters) -> raw_results
          |
          v
4. [Optional] Reranker.rerank(query, raw_results) -> reranked_results
          |
          v
5. Format as SearchResult objects
          |
          v
6. Return to caller
```

### SemanticSearcher Implementation

Composes `BaseEmbedder` + `BaseStore` + optional `BaseReranker`:

```python
class SemanticSearcher(BaseSearcher):
    """Semantic search using dense embeddings only."""

    def __init__(
        self,
        embedder: BaseEmbedder,
        store: BaseStore,
        reranker: BaseReranker | None = None,
    ) -> None:
        self._embedder = embedder
        self._store = store
        self._reranker = reranker

    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: dict[str, Any] | None = None,
        score_threshold: float = 0.0,
    ) -> list[SearchResult]:
        # 1. Embed query
        query_embedding = await self._embedder.embed(query)

        # 2. Search store (retrieve more if reranking)
        retrieve_n = n_results * 3 if self._reranker else n_results
        raw_results = self._store.search(
            query_embedding=query_embedding,
            n_results=retrieve_n,
            filter_dict=filter_dict,
            score_threshold=score_threshold,
        )

        # 3. Optional reranking
        if self._reranker and raw_results:
            raw_results = await self._reranker.rerank(query, raw_results, n_results)

        # 4. Format and return
        return [SearchResult.from_store_result(r) for r in raw_results[:n_results]]
```

### HybridSearcher (Qdrant-Specific)

Extends `SemanticSearcher` with sparse vector support:

```python
class HybridSearcher(SemanticSearcher):
    """Hybrid search using dense + sparse vectors (Qdrant only)."""

    def __init__(
        self,
        embedder: BaseEmbedder,
        store: QdrantStore,  # Requires Qdrant for hybrid
        reranker: BaseReranker | None = None,
        sparse_weight: float = 0.3,  # 30% sparse, 70% dense
    ) -> None:
        super().__init__(embedder, store, reranker)
        self._sparse_weight = sparse_weight

        if not store.hybrid_enabled:
            raise ConfigurationError("Hybrid search requires hybrid_enabled=True")
```

### Reranker Interface and Implementation

```python
class BaseReranker(ABC):
    """Abstract interface for result reranking."""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_n: int = 10,
    ) -> list[dict[str, Any]]:
        """Rerank results using cross-encoder or similar."""
        ...


class CohereReranker(BaseReranker):
    """Reranker using Cohere's rerank endpoint."""

    def __init__(self, api_key: str, model: str = "rerank-english-v3.0") -> None:
        self._client = cohere.AsyncClient(api_key)
        self._model = model

    async def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_n: int = 10,
    ) -> list[dict[str, Any]]:
        if not results:
            return []

        response = await self._client.rerank(
            model=self._model,
            query=query,
            documents=[r["content"] for r in results],
            top_n=top_n,
        )

        # Reorder results by rerank score
        reranked = []
        for r in response.results:
            result = results[r.index].copy()
            result["rerank_score"] = r.relevance_score
            reranked.append(result)

        return reranked
```

### Factory Method Pattern

Consistent with `create_store`:

```python
def create_searcher(
    config: KnowledgeConfig,
    embedder: BaseEmbedder | None = None,
    store: BaseStore | None = None,
) -> BaseSearcher:
    """
    Create a searcher instance based on configuration.

    Args:
        config: Application configuration.
        embedder: Optional embedder instance (created if not provided).
        store: Optional store instance (created if not provided).

    Returns:
        Configured searcher instance.
    """
    from knowledge_mcp.embed import OpenAIEmbedder
    from knowledge_mcp.store import create_store

    # Create components if not provided
    if embedder is None:
        embedder = OpenAIEmbedder(api_key=config.openai_api_key)
    if store is None:
        store = create_store(config)

    # Create optional reranker
    reranker = None
    if config.cohere_api_key:
        reranker = CohereReranker(api_key=config.cohere_api_key)

    # Choose searcher type
    if config.vector_store == "qdrant" and config.qdrant_hybrid_search:
        return HybridSearcher(embedder, store, reranker)

    return SemanticSearcher(embedder, store, reranker)
```

## CLI Architecture

### Pattern: Click Application with Subcommands

Use Click (already in Rich's dependencies) for CLI structure. Each command is a thin wrapper around pipeline components.

```python
# Recommended structure: src/knowledge_mcp/cli/

cli/
    __init__.py          # Main CLI entry point
    ingest.py            # Document ingestion commands
    verify.py            # Verification and diagnostic commands
    search.py            # CLI search interface (for testing)
```

### CLI Entry Point Structure

```python
# src/knowledge_mcp/cli/__init__.py
import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
def cli() -> None:
    """Knowledge MCP - Semantic search over technical documents."""
    pass


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--recursive/--no-recursive", default=True)
@click.option("--dry-run", is_flag=True, help="Preview without processing")
def ingest(source: str, recursive: bool, dry_run: bool) -> None:
    """Ingest documents from SOURCE directory."""
    from knowledge_mcp.cli.ingest import run_ingest
    run_ingest(source, recursive, dry_run)


@cli.command()
@click.option("--collection", default=None, help="Collection to verify")
def verify(collection: str | None) -> None:
    """Verify embeddings and store health."""
    from knowledge_mcp.cli.verify import run_verify
    run_verify(collection)


@cli.command()
@click.argument("query")
@click.option("-n", "--results", default=5, help="Number of results")
def search(query: str, results: int) -> None:
    """Search the knowledge base (for testing)."""
    from knowledge_mcp.cli.search import run_search
    run_search(query, results)
```

### Ingest Command Data Flow

```
1. Parse CLI arguments
          |
          v
2. Discover files (glob, filter by extension)
          |
          v
3. For each file:
   a. get_ingestor(path) -> ingestor
   b. ingestor.ingest(path) -> IngestResult[]
   c. chunker.chunk_batch(results) -> KnowledgeChunk[]
   d. embedder.embed_batch(chunks) -> embedded_chunks
   e. store.add_chunks(embedded_chunks)
          |
          v
4. Report summary (files processed, chunks created, errors)
```

### Pipeline Orchestrator

The CLI should use a `Pipeline` class that composes all components:

```python
# src/knowledge_mcp/pipeline.py
class IngestionPipeline:
    """Orchestrates the full ingestion pipeline."""

    def __init__(
        self,
        ingestors: dict[str, BaseIngestor] | None = None,
        chunker: BaseChunker | None = None,
        embedder: BaseEmbedder | None = None,
        store: BaseStore | None = None,
    ) -> None:
        self._ingestors = ingestors or self._default_ingestors()
        self._chunker = chunker
        self._embedder = embedder
        self._store = store

    async def process_file(self, path: Path) -> PipelineResult:
        """Process a single file through the full pipeline."""
        # 1. Ingest
        ingestor = get_ingestor(path)
        results = ingestor.ingest(path)

        # 2. Chunk
        chunk_metadata = ChunkMetadata(...)
        chunks = self._chunker.chunk_batch([(r.content, chunk_metadata) for r in results])

        # 3. Embed
        texts = [c.content for c in chunks.chunks]
        embeddings = await self._embedder.embed_batch(texts)
        embedded_chunks = [
            c.with_embedding(e, self._embedder.model_name)
            for c, e in zip(chunks.chunks, embeddings)
        ]

        # 4. Store
        count = self._store.add_chunks(embedded_chunks)

        return PipelineResult(
            file_path=path,
            chunks_created=count,
            tokens_total=chunks.total_tokens,
        )
```

## Testing Architecture

### Pattern: Layered Testing with Mocks

The existing test structure follows AAA (Arrange-Act-Assert) with fixtures. Extend this pattern to achieve 80% coverage.

### Test Organization

```
tests/
    conftest.py                    # Shared fixtures, mock factories
    unit/
        test_search/
            __init__.py
            test_semantic_search.py
            test_hybrid_search.py
            test_reranker.py
        test_cli/
            __init__.py
            test_ingest_command.py
            test_verify_command.py
        test_pipeline.py
    integration/
        test_search_integration.py  # Real embedder + mock store
        test_pipeline_integration.py
    e2e/
        test_mcp_server.py         # Full MCP protocol test
```

### Mock Strategy

| Component     | Mock Approach                                   |
|---------------|-------------------------------------------------|
| Embedder      | `AsyncMock` returning fixed-dimension vectors    |
| Store         | `MagicMock` with configurable `search()` returns |
| Reranker      | `AsyncMock` returning reordered input           |
| Qdrant Client | `MagicMock` (as existing tests do)              |
| OpenAI Client | `AsyncMock` with embedding response structure   |

### Fixture Patterns (from existing codebase)

```python
# Reuse existing fixture patterns

@pytest.fixture
def mock_embedder() -> BaseEmbedder:
    """Create a mock embedder with predictable outputs."""
    embedder = MagicMock(spec=BaseEmbedder)
    embedder.dimensions = 1536
    embedder.model_name = "test-model"
    embedder.embed = AsyncMock(return_value=[0.1] * 1536)
    embedder.embed_batch = AsyncMock(
        side_effect=lambda texts: [[0.1] * 1536 for _ in texts]
    )
    return embedder


@pytest.fixture
def mock_store() -> BaseStore:
    """Create a mock store with search results."""
    store = MagicMock(spec=BaseStore)
    store.search.return_value = [
        {
            "id": "chunk-1",
            "content": "Test content",
            "metadata": {"document_title": "Test Doc"},
            "score": 0.95,
        }
    ]
    store.health_check.return_value = True
    return store


@pytest.fixture
def searcher(mock_embedder: BaseEmbedder, mock_store: BaseStore) -> SemanticSearcher:
    """Create a searcher with mocked dependencies."""
    return SemanticSearcher(embedder=mock_embedder, store=mock_store)
```

### Coverage Strategy

To achieve 80% coverage, focus on:

1. **Unit tests for search layer** (~20 tests)
   - SemanticSearcher.search() with various inputs
   - HybridSearcher sparse weight handling
   - Reranker integration
   - Error handling for each exception type

2. **Unit tests for CLI commands** (~15 tests)
   - Argument parsing
   - Dry-run mode
   - Error handling and reporting
   - Progress output

3. **Integration tests** (~10 tests)
   - Full search flow with mock store
   - Pipeline execution with mock components
   - MCP tool handler dispatch

4. **Edge case tests** (~10 tests)
   - Empty results
   - Score threshold filtering
   - Large batch handling
   - Network error recovery

### MCP Server Testing

Test MCP tools using the `mcp` library's test utilities:

```python
@pytest.mark.asyncio
async def test_knowledge_search_tool(
    searcher: SemanticSearcher,
    mock_store: BaseStore,
) -> None:
    """Test MCP knowledge_search tool returns formatted results."""
    # Arrange
    server = KnowledgeMCPServer()
    server._searcher = searcher  # Inject mock

    # Act
    result = await server._handle_search_tool({"query": "SRR", "n_results": 5})

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].type == "text"
    content = json.loads(result[0].text)
    assert "results" in content
```

## Build Order Implications

### Phase Ordering Rationale

Based on dependencies, the build order should be:

1. **Search Layer Models** (`search/models.py`)
   - No dependencies on new code
   - Defines `SearchResult`, `SearchQuery` data contracts
   - Enables parallel work on searcher implementations

2. **BaseSearcher Interface** (`search/base.py`)
   - Depends only on models
   - Enables parallel implementation of SemanticSearcher and tests

3. **SemanticSearcher** (`search/semantic.py`)
   - Depends on BaseSearcher, existing Embedder, existing Store
   - Core search functionality

4. **Reranker** (`search/reranker.py`)
   - Independent of searchers
   - Can be developed in parallel with SemanticSearcher

5. **HybridSearcher** (`search/hybrid.py`)
   - Extends SemanticSearcher
   - Requires QdrantStore hybrid mode verification

6. **Search Factory** (`search/__init__.py`)
   - Depends on all searcher implementations
   - Wires configuration to searcher selection

7. **MCP Tool Handlers** (update `server.py`)
   - Depends on search factory
   - Connects search layer to MCP protocol

8. **CLI Framework** (`cli/__init__.py`)
   - Independent of search, depends on Click
   - Sets up command structure

9. **Ingest Command** (`cli/ingest.py`)
   - Depends on existing ingest/chunk/embed/store layers
   - Uses Pipeline orchestrator

10. **Verify Command** (`cli/verify.py`)
    - Depends on store health checks
    - Can run after ingest

### Dependency Graph

```
search/models.py
        |
        v
search/base.py -----> search/reranker.py (parallel)
        |
        v
search/semantic.py
        |
        +-----------+
        |           |
        v           v
search/hybrid.py  search/__init__.py (factory)
        |           |
        +-----------+
                |
                v
          server.py (MCP tools)

cli/__init__.py
        |
        +-------------+
        |             |
        v             v
cli/ingest.py    cli/verify.py
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: God Searcher

**What:** Single searcher class with all search modes via flags
**Why bad:** Violates single responsibility, hard to test, complex branching
**Instead:** Separate SemanticSearcher, HybridSearcher with common base

### Anti-Pattern 2: Direct Store Access from MCP Server

**What:** MCP tool handlers directly calling `store.search()`
**Why bad:** Bypasses embedding, loses reranking, couples server to store
**Instead:** MCP tools call search layer, which composes components

### Anti-Pattern 3: CLI Business Logic

**What:** Complex processing logic in CLI command functions
**Why bad:** Hard to test, duplicates logic with programmatic use
**Instead:** CLI is thin wrapper around Pipeline class

### Anti-Pattern 4: Synchronous Embedding in Search

**What:** Blocking on embedding during search request
**Why bad:** Poor latency for MCP tool calls
**Instead:** Use `async def search()` throughout, await embedding

## Scalability Considerations

| Concern           | At 100 docs        | At 10K docs    | At 1M docs                  |
|-------------------|--------------------|----------------|-----------------------------|
| Search latency    | <100ms             | <200ms         | Consider query caching      |
| Embedding cost    | Negligible         | $2-5/ingest    | Pre-compute, batch          |
| Store size        | Local ChromaDB OK  | Qdrant Cloud   | Qdrant Cloud with sharding  |
| Reranking         | Always             | Top 30         | Top 100, then rerank top 30 |

## Sources

| Source                 | Confidence | Notes                                       |
|------------------------|-----------|---------------------------------------------|
| Existing codebase      | HIGH      | Direct analysis of `src/knowledge_mcp/`     |
| CLAUDE.md specification | HIGH      | Project standards document                  |
| Existing test patterns | HIGH      | `tests/` directory analysis                 |
| MCP protocol           | MEDIUM    | Based on training data + existing server.py |
| Cohere reranking       | MEDIUM    | Based on training data, verify current API  |
| Click CLI              | MEDIUM    | Standard Python CLI library                 |

---

*Architecture research: 2026-01-20*
