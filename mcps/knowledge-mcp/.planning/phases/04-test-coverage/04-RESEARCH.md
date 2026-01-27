# Phase 4: Test Coverage - Research

**Researched:** 2026-01-27
**Domain:** Python pytest testing, coverage analysis, security testing
**Confidence:** HIGH

## Summary

This phase requires increasing test coverage from the current 71% line coverage to 80% line coverage and achieving 75% branch coverage. The codebase already has a solid testing foundation using pytest 8.4, pytest-cov 4.1, and pytest-asyncio 0.23, with established patterns in the existing test suite.

The primary coverage gaps are in:
1. **Store backends** (QdrantStore: 17%, ChromaDBStore: 33%) - core CRUD operations need testing
2. **Server module** (64%) - MCP handler coverage is good but entry points and initialization paths missing
3. **CLI/utility modules** (`__main__.py`: 0%, `token_summary.py`: 0%, `logging.py`: 20%) - command-line tools untested
4. **Evaluation modules** (`metrics.py`: 14%, `reporter.py`: 9%) - RAG evaluation reporting untested

The existing test patterns use dependency injection with mocked embedders and stores, AAA (Arrange-Act-Assert) structure, and pytest fixtures in `conftest.py`. These patterns should be extended to cover the remaining modules.

**Primary recommendation:** Focus on the critical path first (Search -> Store -> MCP server), then add comprehensive error/fallback path tests to hit branch coverage targets.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | ^8.0 | Test framework | Installed, pytest-asyncio integration, AAA pattern support |
| pytest-cov | ^4.1 | Coverage measurement | Installed, branch coverage support, pyproject.toml config |
| pytest-asyncio | ^0.23 | Async test support | Installed, `asyncio_mode = "auto"` configured |
| coverage.py | (via pytest-cov) | Coverage engine | Branch coverage, exclude patterns configured |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-golden | ^1.0 | Golden test pattern | Snapshot testing for complex outputs |
| unittest.mock | (stdlib) | Mocking | AsyncMock for async methods, MagicMock for sync |
| tracemalloc | (stdlib) | Memory leak detection | Stress testing with memory monitoring |
| ruff | ^0.4 | Security linting | S-rules for security, C901 for complexity |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| unittest.mock | pytest-mock | pytest-mock adds `mocker` fixture, but unittest.mock is already used throughout |
| tracemalloc | psutil.Process().memory_full_info().uss | psutil works with all libraries but less granular |
| pytest-golden | inline assertions | Golden tests better for complex JSON output comparison |

**Installation:**
All required packages are already installed via `poetry install`.

## Architecture Patterns

### Recommended Test File Organization
```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures (mock_config, sample_chunk, mock_embedder)
├── unit/
│   ├── __init__.py
│   ├── test_config.py             # Exists - config validation
│   ├── test_server.py             # Exists - MCP handlers (needs expansion)
│   ├── test_embed_cache.py        # Exists - embedding cache
│   ├── test_monitoring.py         # Exists - token tracking
│   ├── test_logging.py            # NEW - logging module tests
│   ├── test_cli/                  # NEW - CLI command tests
│   │   ├── __init__.py
│   │   └── test_token_summary.py
│   ├── test_chunk/                # Exists
│   ├── test_embed/                # Exists
│   ├── test_ingest/               # Exists
│   ├── test_search/               # Exists
│   ├── test_store/                # Exists (needs QdrantStore/ChromaDB unit tests)
│   │   ├── __init__.py
│   │   ├── test_qdrant_store.py   # NEW - mocked Qdrant client tests
│   │   └── test_chromadb_store.py # NEW - mocked ChromaDB tests
│   └── test_utils/                # Exists
├── integration/
│   ├── __init__.py
│   ├── test_fallback.py           # Exists - store fallback
│   ├── test_ingestion.py          # Exists - ingestion pipeline
│   ├── test_embedder_integration.py # Exists
│   └── test_mcp_protocol.py       # NEW - full E2E MCP JSON-RPC tests
├── evaluation/                    # Exists
│   └── test_golden_set.py
└── fixtures/
    ├── sample_documents/          # NEW - small test PDFs/DOCXs
    │   ├── small_test.pdf
    │   ├── small_test.docx
    │   └── sample_markdown.md
    └── sample_data.py             # NEW - deterministic test vectors
```

### Pattern 1: Mocked Vector Store Testing
**What:** Test store methods using mocked Qdrant/ChromaDB clients
**When to use:** Unit testing store CRUD operations without network/database dependencies

```python
# Source: Existing pattern in tests/unit/test_server.py
from unittest.mock import MagicMock, patch

class TestQdrantStoreSearch:
    @pytest.fixture
    def mock_qdrant_client(self) -> MagicMock:
        """Create mock Qdrant client."""
        client = MagicMock()
        client.search.return_value = [
            MagicMock(
                id="chunk-1",
                score=0.95,
                payload={"content": "Test", "document_title": "IEEE 15288"},
            )
        ]
        return client

    @pytest.fixture
    def store(self, mock_qdrant_client: MagicMock) -> QdrantStore:
        """Create store with mocked client."""
        with patch("knowledge_mcp.store.qdrant_store.QdrantClient") as mock_class:
            mock_class.return_value = mock_qdrant_client
            store = QdrantStore.__new__(QdrantStore)
            store.client = mock_qdrant_client
            store.collection = "test_collection"
            store.hybrid_enabled = False
            store.config = MagicMock()
            store.config.embedding_dimensions = 1536
            return store

    def test_search_returns_formatted_results(self, store: QdrantStore) -> None:
        # Arrange
        query_embedding = [0.1] * 1536

        # Act
        results = store.search(query_embedding, n_results=5)

        # Assert
        assert len(results) == 1
        assert results[0]["content"] == "Test"
```

### Pattern 2: MCP Protocol E2E Testing
**What:** Test actual JSON-RPC protocol over server handlers
**When to use:** Integration testing MCP tool invocations

```python
# Source: Adapted from existing tests/unit/test_server.py
from mcp.types import CallToolRequest, ListToolsRequest

class TestMCPProtocolIntegration:
    @pytest.fixture
    def server(self, mock_embedder: AsyncMock, mock_store: MagicMock) -> KnowledgeMCPServer:
        """Create server with mocked dependencies."""
        return KnowledgeMCPServer(
            name="test-server",
            embedder=mock_embedder,
            store=mock_store,
        )

    @pytest.mark.asyncio
    async def test_knowledge_search_via_protocol(self, server: KnowledgeMCPServer) -> None:
        """Test full MCP protocol flow."""
        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test"}}
        )

        response = await server.server.request_handlers[CallToolRequest](request)

        # Verify JSON-RPC response structure
        assert len(response.root.content) == 1
        assert response.root.content[0].type == "text"

        import json
        data = json.loads(response.root.content[0].text)
        assert "results" in data
```

### Pattern 3: Error Path Testing
**What:** Systematically test all exception types and fallback paths
**When to use:** Branch coverage for error handling code

```python
# Source: Existing pattern in tests/unit/test_server.py, tests/integration/test_fallback.py
class TestErrorPaths:
    @pytest.mark.asyncio
    async def test_embedding_failure_returns_empty(
        self, server: KnowledgeMCPServer, mock_embedder: AsyncMock
    ) -> None:
        """Test that embedding failures are handled gracefully."""
        mock_embedder.embed.side_effect = Exception("API rate limit")

        request = CallToolRequest(
            params={"name": "knowledge_search", "arguments": {"query": "test"}}
        )
        response = await server.server.request_handlers[CallToolRequest](request)

        data = json.loads(response.root.content[0].text)
        assert data["total_results"] == 0  # Graceful degradation
```

### Pattern 4: Deterministic Test Data
**What:** Fixed embeddings and mock data for reproducible tests
**When to use:** Any test involving vectors or search results

```python
# Source: Existing pattern in tests/conftest.py
# Add to tests/fixtures/sample_data.py

DETERMINISTIC_EMBEDDING_1536 = [0.1] * 1536  # Fixed 1536-dim vector
DETERMINISTIC_EMBEDDING_3072 = [0.1] * 3072  # For larger models

SAMPLE_SEARCH_RESULT = {
    "id": "chunk-001",
    "content": "The System Requirements Review (SRR) shall verify...",
    "score": 0.95,
    "metadata": {
        "document_id": "ieee-15288",
        "document_title": "IEEE 15288.2",
        "document_type": "standard",
        "section_title": "System Requirements Review",
        "section_hierarchy": ["5", "5.3"],
        "chunk_type": "requirement",
        "normative": True,
        "clause_number": "5.3.1",
        "page_numbers": [42, 43],
    },
}
```

### Anti-Patterns to Avoid
- **Real API calls in unit tests:** Always mock OpenAI/Qdrant clients
- **Flaky async tests:** Use `asyncio_mode = "auto"` and avoid manual event loop management
- **Shared mutable state:** Each test should create fresh fixtures
- **Testing implementation details:** Test behavior, not internal method calls
- **Ignoring exception context:** Always test the exception message content, not just type

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Coverage measurement | Manual line counting | pytest-cov with `--cov-branch` | Branch coverage, HTML reports, CI integration |
| Async test support | `asyncio.run()` in tests | pytest-asyncio | Fixture support, proper cleanup, event loop handling |
| Mock validation | Manual assertion counting | `mock.assert_called_once_with()` | Built-in call tracking, argument matching |
| Memory leak detection | Manual memory tracking | tracemalloc fixtures | Python stdlib, granular allocation tracking |
| Security scanning | Manual code review | ruff with S-rules | 800+ rules, integrated with existing linting |
| Complex output assertions | Deep dict comparison | pytest-golden | Snapshot testing, easy updates on intentional changes |

**Key insight:** pytest and its plugins handle virtually all testing infrastructure needs. Focus on writing test cases, not test frameworks.

## Common Pitfalls

### Pitfall 1: Incomplete Branch Coverage from Exception Handlers
**What goes wrong:** `except Exception as e:` blocks often don't get tested, missing branch coverage
**Why it happens:** Happy path tests don't trigger exceptions
**How to avoid:** For every try/except block, write tests that trigger each exception type
**Warning signs:** Coverage report shows red lines in except clauses

```python
# Example: Test both success and failure paths
def test_store_search_success(self, store, mock_client):
    mock_client.search.return_value = [...]
    results = store.search([0.1] * 1536)
    assert len(results) > 0

def test_store_search_network_error(self, store, mock_client):
    mock_client.search.side_effect = ConnectionError("timeout")
    with pytest.raises(ConnectionError):
        store.search([0.1] * 1536)
```

### Pitfall 2: Async Test Deadlocks
**What goes wrong:** Tests hang indefinitely on async operations
**Why it happens:** Missing `await`, wrong event loop, or blocking sync calls in async tests
**How to avoid:** Use `asyncio_mode = "auto"`, ensure all async methods are awaited
**Warning signs:** Tests timeout rather than fail, inconsistent test failures

### Pitfall 3: Mock Leakage Between Tests
**What goes wrong:** Mocked state from one test affects another
**Why it happens:** Module-level patching without proper cleanup, shared fixtures
**How to avoid:** Use function-scoped fixtures, context managers for patching
**Warning signs:** Tests pass individually but fail when run together

### Pitfall 4: Testing Internal Implementation
**What goes wrong:** Tests break when refactoring without behavior changes
**Why it happens:** Assertions on internal method calls instead of observable outputs
**How to avoid:** Test public APIs and behaviors, not implementation details
**Warning signs:** Tests need updating when only internal code changes

### Pitfall 5: Ignoring Edge Cases in Coverage
**What goes wrong:** 80% coverage achieved but critical paths untested
**Why it happens:** Focus on line coverage instead of meaningful behavior coverage
**How to avoid:** Prioritize error paths, boundary conditions (n_results=0, empty results)
**Warning signs:** High coverage but production bugs in "covered" code

## Code Examples

Verified patterns from the existing codebase:

### Shared Fixture Pattern (from tests/conftest.py)
```python
# Source: /Users/dunnock/projects/claude-plugins/mcps/knowledge-mcp/tests/conftest.py
@pytest.fixture
def mock_config() -> KnowledgeConfig:
    """Create a test configuration."""
    from knowledge_mcp.utils.config import KnowledgeConfig
    return KnowledgeConfig(
        openai_api_key="test-api-key",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=1536,
        vector_store="chromadb",
        chromadb_path=Path("/tmp/test-chromadb"),
        chromadb_collection="test_collection",
    )

@pytest.fixture
def sample_chunk() -> KnowledgeChunk:
    """Create a sample knowledge chunk for testing."""
    from knowledge_mcp.models.chunk import KnowledgeChunk
    return KnowledgeChunk(
        id="test-chunk-001",
        document_id="ieee-15288.2",
        document_title="IEEE 15288.2-2014",
        # ... full chunk data
        embedding=[0.1] * 1536,
    )
```

### MCP Handler Testing Pattern (from tests/unit/test_server.py)
```python
# Source: /Users/dunnock/projects/claude-plugins/mcps/knowledge-mcp/tests/unit/test_server.py
@pytest.mark.asyncio
async def test_search_returns_formatted_results(self, server: KnowledgeMCPServer) -> None:
    """Test that search returns properly formatted results."""
    # Arrange
    request = CallToolRequest(
        params={"name": "knowledge_search", "arguments": {"query": "system requirements review"}}
    )

    # Act
    response = await server.server.request_handlers[CallToolRequest](request)

    # Assert
    assert len(response.root.content) == 1
    assert response.root.content[0].type == "text"

    import json
    data = json.loads(response.root.content[0].text)
    assert "results" in data
    assert data["total_results"] == 1
```

### Fallback Integration Test Pattern (from tests/integration/test_fallback.py)
```python
# Source: /Users/dunnock/projects/claude-plugins/mcps/knowledge-mcp/tests/integration/test_fallback.py
def test_fallback_to_chromadb_on_qdrant_failure(
    self, config_with_bad_qdrant: KnowledgeConfig, caplog: pytest.LogCaptureFixture
) -> None:
    """Verify ChromaDB is returned when Qdrant is unavailable."""
    with caplog.at_level(logging.WARNING):
        store = create_store(config_with_bad_qdrant)

    # Should be ChromaDB, not Qdrant
    assert isinstance(store, ChromaDBStore)
    assert not isinstance(store, QdrantStore)

    # Should log warning about fallback
    assert any(
        "falling back to chromadb" in record.message.lower()
        for record in caplog.records
    )
```

### Memory Leak Detection Fixture Pattern
```python
# Source: https://pythonspeed.com/articles/identifying-resource-leaks-with-pytest/
# Recommended pattern for stress testing
import gc
import tracemalloc

@pytest.fixture
def check_memory_leaks():
    """Fixture to detect memory leaks in a test."""
    gc.collect()
    tracemalloc.start()
    initial = tracemalloc.get_traced_memory()[0]

    yield

    gc.collect()
    final = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    # Allow 100KB growth for normal variance
    leaked = final - initial
    assert leaked < 100_000, f"Memory leaked: {leaked} bytes"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@pytest.mark.asyncio` on every test | `asyncio_mode = "auto"` in pyproject.toml | pytest-asyncio 0.23+ | No more decorator boilerplate |
| Manual coverage threshold checks | `--cov-fail-under=80` in pytest config | coverage.py 5.0+ | CI fails automatically below threshold |
| grep for security issues | `ruff check --select S` | ruff 0.4+ | 10-100x faster, integrated with linting |
| Separate bandit tool | ruff S-rules (flake8-bandit) | ruff 0.1+ | Single tool for all linting |

**Deprecated/outdated:**
- pytest.mark.asyncio on individual tests (use asyncio_mode = "auto")
- unittest.TestCase subclasses (use plain functions/classes)
- nose test framework (use pytest)
- mock.patch without context manager (prefer `with patch(...)`)

## Open Questions

Things that couldn't be fully resolved:

1. **Fixture sample document sizing**
   - What we know: Need small PDFs and DOCXs for real Docling parsing tests
   - What's unclear: Optimal file size to balance coverage vs speed (< 1MB suggested)
   - Recommendation: Start with minimal 1-page documents, expand if needed

2. **Memory leak threshold**
   - What we know: tracemalloc can detect leaks, need a threshold
   - What's unclear: What's an acceptable memory growth for repeated operations
   - Recommendation: Start with 100KB threshold per stress test, tune based on baseline

3. **MCP E2E test scope**
   - What we know: Can test handlers via `server.request_handlers[RequestType]`
   - What's unclear: Whether to test actual stdio transport or just handler layer
   - Recommendation: Test handler layer (faster, reliable), defer stdio transport testing

## Sources

### Primary (HIGH confidence)
- pyproject.toml - Verified installed versions: pytest 8.4, pytest-cov 4.1, pytest-asyncio 0.23
- tests/ directory - Analyzed existing patterns and fixtures
- Coverage report - Current coverage: 71% line, gaps identified in store/CLI/logging modules

### Secondary (MEDIUM confidence)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/en/latest/config.html) - Branch coverage configuration
- [MCPcat MCP Testing Guide](https://mcpcat.io/guides/writing-unit-tests-mcp-servers/) - In-memory client-server testing pattern
- [Ruff Rules Documentation](https://docs.astral.sh/ruff/rules/) - S-rules for security, C901 for complexity
- [tracemalloc stdlib docs](https://docs.python.org/3/library/tracemalloc.html) - Memory profiling

### Tertiary (LOW confidence)
- [pytest-with-eric coverage guide](https://pytest-with-eric.com/coverage/poetry-test-coverage/) - Coverage best practices
- [pythonspeed memory leaks article](https://pythonspeed.com/articles/identifying-resource-leaks-with-pytest/) - Memory leak fixture pattern

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools already installed and configured in pyproject.toml
- Architecture: HIGH - Based on analysis of existing test patterns in codebase
- Pitfalls: HIGH - Derived from actual coverage gaps and common pytest issues
- Security testing: MEDIUM - Ruff S-rules verified, specific rules to enable TBD

**Research date:** 2026-01-27
**Valid until:** 2026-02-27 (30 days - stable testing practices)
