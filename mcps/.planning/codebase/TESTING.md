# Testing Patterns

**Analysis Date:** 2026-03-08

## Test Framework

**Runner:**
- pytest ^8.0 with pytest-asyncio ^0.23
- Config: `knowledge-mcp/pyproject.toml` `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest built-in assertions (no third-party assertion library)

**Coverage:**
- pytest-cov ^4.1
- Branch coverage enabled

**Run Commands:**
```bash
# Run all tests with coverage (from knowledge-mcp/)
poetry run pytest

# Run all tests (equivalent, addopts in pyproject.toml adds --cov flags)
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run unit tests only
poetry run pytest tests/unit/

# Run integration tests only
poetry run pytest tests/integration/

# Skip integration tests
poetry run pytest -m "not integration"

# Run specific test file
poetry run pytest tests/unit/test_search/test_hybrid.py

# Run with verbose output
poetry run pytest -v

# Generate XML coverage for CI
poetry run pytest --cov=src --cov-report=xml --cov-fail-under=80
```

## Test File Organization

**Location:** Separate `tests/` directory (not co-located with source)

**Naming:** `test_<module_name>.py` matching source structure

**Structure:**
```
knowledge-mcp/tests/
  conftest.py                              # Shared fixtures
  unit/
    test_config.py                         # tests/unit/test_config.py
    test_main.py                           # tests/unit/test_main.py
    test_server.py                         # tests/unit/test_server.py
    test_monitoring.py                     # tests/unit/test_monitoring.py
    test_embed_cache.py                    # tests/unit/test_embed_cache.py
    test_chunk/
      test_hierarchical.py                 # mirrors src/knowledge_mcp/chunk/hierarchical.py
    test_cli/
      test_ingest.py
      test_validate.py
      test_verify.py
    test_db/
      test_engine.py
      test_models.py
      test_repositories.py
    test_embed/
      test_local_embedder.py
      test_openai_embedder.py
    test_ingest/
      test_docx_ingestor.py
      test_pdf_ingestor.py
      test_pipeline.py
      test_web_ingestor.py
    test_models/
      test_chunk.py
    test_search/
      test_bm25.py
      test_citation.py
      test_coverage.py
      test_explore_strategy.py
      test_hybrid.py
      test_models.py
      test_plan_strategy.py
      test_rcca_strategy.py
      test_reranker.py
      test_semantic_search.py
      test_trade_study_strategy.py
      test_workflow_search.py
    test_store/
      test_chromadb_store.py
      test_qdrant_store.py
    test_sync/
      test_offline.py
    test_utils/
      test_hashing.py
      test_logging.py
      test_normative.py
      test_tokenizer.py
    test_validation/
      test_table_validator.py
  integration/
    test_acquisition_tools.py
    test_database.py
    test_embedder_integration.py
    test_end_to_end.py
    test_fallback.py
    test_hybrid_search.py
    test_ingestion.py
    test_mcp_tools.py
    test_workflow_tools.py
  evaluation/
    test_golden_set.py                     # RAG evaluation with golden test data
  fixtures/                                # (empty currently)
```

## Test Structure

**Suite Organization -- use test classes grouped by method/feature:**
```python
"""Unit tests for QdrantStore."""

from unittest.mock import MagicMock, patch

import pytest

from knowledge_mcp.store.qdrant_store import QdrantStore
from knowledge_mcp.utils.config import KnowledgeConfig


class TestQdrantStoreInit:
    """Tests for QdrantStore initialization."""

    @pytest.fixture
    def mock_config(self, tmp_path: Path) -> KnowledgeConfig:
        """Create test configuration."""
        return KnowledgeConfig(...)

    def test_creates_collection_if_not_exists(self, mock_config: KnowledgeConfig) -> None:
        """Verify create_collection called when collection doesn't exist."""
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...


class TestQdrantStoreSearch:
    """Tests for QdrantStore.search method."""
    ...


class TestQdrantStoreStats:
    """Tests for QdrantStore.get_stats method."""
    ...
```

**Key patterns:**
- One test class per method or logical group (e.g., `TestQdrantStoreInit`, `TestQdrantStoreSearch`, `TestQdrantStoreStats`)
- Class docstring describes what's being tested
- Each test method has a docstring describing the specific behavior being verified
- All test methods have `-> None` return type annotation
- Arrange-Act-Assert (AAA) pattern with comment markers

**Arrange-Act-Assert pattern:**
```python
def test_search_returns_formatted_results(self, mock_config, mock_search_results) -> None:
    """Verify result format with content, score, metadata."""
    # Arrange
    mock_client.search.return_value = mock_search_results

    # Act
    results = store.search([0.1] * 1536, n_results=5)

    # Assert
    assert len(results) == 2
    assert results[0]["content"] == "Test content 1"
    assert results[0]["score"] == 0.95
```

## Async Testing

**Configuration:** `asyncio_mode = "auto"` in pyproject.toml (no need for `@pytest.mark.asyncio` on every test, but the codebase still uses it explicitly)

**Pattern:**
```python
@pytest.mark.asyncio
async def test_search_combines_both_methods(
    self,
    hybrid_searcher: HybridSearcher,
    mock_semantic_searcher: AsyncMock,
    mock_bm25_searcher: MagicMock,
) -> None:
    """Test that hybrid search calls both semantic and BM25."""
    # Arrange
    mock_semantic_searcher.search.return_value = [
        SearchResult(id="doc1", content="test1", score=0.9)
    ]
    mock_bm25_searcher.search.return_value = [
        {"id": "doc2", "content": "test2", "score": 5.0}
    ]

    # Act
    results = await hybrid_searcher.search("test query", n_results=5)

    # Assert
    mock_semantic_searcher.search.assert_called_once()
    assert isinstance(results, list)
```

## Mocking

**Framework:** `unittest.mock` (stdlib) -- `MagicMock`, `AsyncMock`, `patch`

**Patterns:**

1. **Fixture-based mocks (preferred for class-level dependencies):**
```python
@pytest.fixture
def mock_semantic_searcher(self) -> AsyncMock:
    """Create a mock SemanticSearcher."""
    searcher = AsyncMock(spec=SemanticSearcher)
    return searcher

@pytest.fixture
def hybrid_searcher(
    self,
    mock_semantic_searcher: AsyncMock,
    mock_bm25_searcher: MagicMock,
) -> HybridSearcher:
    """Create a HybridSearcher with mocked dependencies."""
    return HybridSearcher(mock_semantic_searcher, mock_bm25_searcher)
```

2. **Context manager `patch` (for module-level patching):**
```python
def test_creates_collection_if_not_exists(self, mock_config) -> None:
    with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        mock_client.get_collections.return_value.collections = []

        from knowledge_mcp.store.qdrant_store import QdrantStore
        QdrantStore(mock_config)

        mock_client.create_collection.assert_called_once()
```

3. **Deeply nested patch (for initialization chains):**
```python
def test_ensure_dependencies_creates_embedder_with_cache(self) -> None:
    server = KnowledgeMCPServer(name="test")
    with patch("knowledge_mcp.server.load_config") as mock_load:
        mock_config = MagicMock()
        mock_config.cache_enabled = True
        mock_load.return_value = mock_config
        with patch("knowledge_mcp.server.EmbeddingCache") as mock_cache_cls:
            with patch("knowledge_mcp.server.OpenAIEmbedder") as mock_embedder_cls:
                with patch("knowledge_mcp.server.create_store") as mock_create_store:
                    with patch("knowledge_mcp.server.SemanticSearcher"):
                        server._ensure_dependencies()
                        mock_cache_cls.assert_called_once_with(...)
```

**What to mock:**
- External API clients (OpenAI, Qdrant, Cohere)
- Database connections and sessions
- File system operations in ingestors
- Network calls (HTTP clients)

**What NOT to mock:**
- Data models (`KnowledgeChunk`, `SearchResult`, `KnowledgeConfig`) -- use real instances
- Pure functions (`reciprocal_rank_fusion`) -- test directly
- Configuration objects -- create real `KnowledgeConfig` with test values

**Use `spec=` parameter** when mocking classes to catch attribute errors:
```python
searcher = AsyncMock(spec=SemanticSearcher)  # Will error if non-existent methods called
```

## Fixtures

**Shared fixtures in `knowledge-mcp/tests/conftest.py`:**
```python
# Test constants -- not real credentials
TEST_OPENAI_API_KEY = os.environ.get("TEST_OPENAI_API_KEY", "test-api-key-not-real")
TEST_QDRANT_API_KEY = os.environ.get("TEST_QDRANT_API_KEY", "test-qdrant-key-not-real")

@pytest.fixture
def mock_config() -> KnowledgeConfig:
    """Create a test configuration."""
    return KnowledgeConfig(
        openai_api_key=TEST_OPENAI_API_KEY,
        embedding_model="text-embedding-3-small",
        embedding_dimensions=1536,
        vector_store="chromadb",
        chromadb_path=Path("/tmp/test-chromadb"),
    )

@pytest.fixture
def sample_chunk() -> KnowledgeChunk:
    """Create a sample knowledge chunk for testing."""
    return KnowledgeChunk(
        id="test-chunk-001",
        document_id="ieee-15288.2",
        content="The System Requirements Review (SRR) shall verify...",
        content_hash="abc123def456",
        token_count=150,
        embedding=[0.1] * 1536,
    )

@pytest.fixture
def mock_qdrant_client() -> MagicMock: ...

@pytest.fixture
def mock_openai_client() -> AsyncMock: ...
```

**Local fixtures:**
- Test classes define their own fixtures for class-specific mocks
- Use `tmp_path` (pytest built-in) for temporary file paths in configs
- Lazy imports inside fixtures to avoid import side effects:
```python
@pytest.fixture
def mock_config(self) -> KnowledgeConfig:
    from knowledge_mcp.utils.config import KnowledgeConfig
    return KnowledgeConfig(...)
```

**Test data location:**
- `knowledge-mcp/tests/fixtures/` directory exists but is currently empty
- Inline test data preferred for unit tests
- Integration tests define corpus data as fixtures (see `test_hybrid_search.py` `technical_corpus`)

## Coverage

**Requirements:**
- Line coverage: minimum 80% (CI-blocking via `--cov-fail-under=80`)
- Branch coverage: enabled (`branch = true` in `[tool.coverage.run]`)
- Target: 90% line, 85% branch

**Excluded from coverage (`[tool.coverage.report]`):**
- `pragma: no cover` comments
- `def __repr__` methods
- `raise NotImplementedError` (abstract methods)
- `if TYPE_CHECKING:` blocks
- `if __name__ == "__main__":` blocks

**View coverage:**
```bash
# Terminal report with missing lines
poetry run pytest --cov=src --cov-report=term-missing

# HTML coverage report
poetry run pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

## Test Types

**Unit Tests (`tests/unit/`):**
- Test individual classes and functions in isolation
- All external dependencies mocked
- Fast execution, no network or disk I/O
- ~40 test files covering all source modules

**Integration Tests (`tests/integration/`):**
- Marked with `@pytest.mark.integration`
- Test component interactions (e.g., hybrid search with real BM25 + mocked semantic)
- May use real BM25 indexes but mock external APIs
- 9 test files covering key workflows

**Evaluation Tests (`tests/evaluation/`):**
- RAG quality evaluation using golden test sets
- Uses `ragas` framework for metrics
- `pytest-golden` for snapshot testing

## Integration Test Pattern

```python
@pytest.mark.integration
class TestHybridSearchIntegration:
    """Integration tests demonstrating hybrid search improvements."""

    @pytest.fixture
    def technical_corpus(self) -> list[dict[str, str]]:
        """Create a technical corpus with precise terminology."""
        return [
            {"id": "doc1", "content": "The System Requirements Review (SRR)..."},
            {"id": "doc2", "content": "A requirements traceability matrix (RTM)..."},
        ]

    @pytest.fixture
    def bm25_searcher(self, technical_corpus) -> BM25Searcher:
        """Create a BM25 searcher with indexed corpus."""
        searcher = BM25Searcher()
        searcher.build_index(technical_corpus)
        return searcher

    @pytest.fixture
    def hybrid_searcher(self, mock_semantic_searcher, bm25_searcher) -> HybridSearcher:
        """Create hybrid searcher combining mocked semantic and real BM25."""
        return HybridSearcher(mock_semantic_searcher, bm25_searcher)

    @pytest.mark.asyncio
    async def test_hybrid_improves_keyword_match_ranking(self, hybrid_searcher, ...) -> None:
        """Test FR-3.2: BM25 boosts exact keyword matches."""
        ...
```

## Error Testing

**Pattern for expected exceptions:**
```python
def test_add_chunks_raises_on_missing_embedding(self, mock_config) -> None:
    """Verify ValueError for chunk with None embedding."""
    with pytest.raises(ValueError, match="missing embedding"):
        store.add_chunks([chunk_without_embedding])
```

**Pattern for error responses (MCP tools):**
```python
@pytest.mark.asyncio
async def test_search_connection_error_returns_structured_error(self, server) -> None:
    """Test that ConnectionError returns structured error with empty results."""
    with patch.object(server, "_searcher") as mock_searcher:
        mock_searcher.search.side_effect = ConnectionError("Vector store unreachable")
        response = await server.server.request_handlers[CallToolRequest](request)

    data = json.loads(response.root.content[0].text)
    assert data["error"] == "Knowledge base temporarily unavailable"
    assert data["retryable"] is True
    assert data["results"] == []
```

## CI Integration

**GitHub Actions workflow (`knowledge-mcp/.github/workflows/ci.yml`):**

1. **Lint & Format** job (runs first):
   - `poetry run ruff check src tests`
   - `poetry run pyright`

2. **Test** job (depends on lint):
   - `poetry run pytest --cov=src --cov-report=xml --cov-fail-under=80`
   - Uploads coverage to Codecov

3. **Security** job (parallel):
   - `poetry run pip-audit --strict`

---

*Testing analysis: 2026-03-08*
