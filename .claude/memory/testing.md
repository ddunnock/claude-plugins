# Testing Standards

> **Applies to**: All automated tests
> **Parent**: `constitution.md`

---

## 1. Coverage Requirements

All code **MUST** meet or exceed these thresholds:

| Metric             | Minimum  | Target  | Blocking  |
|--------------------|----------|---------|-----------|
| Line Coverage      | 80%      | 90%     | Yes       |
| Branch Coverage    | 75%      | 85%     | Yes       |
| Function Coverage  | 85%      | 95%     | Yes       |
| Statement Coverage | 80%      | 90%     | Yes       |

### 1.1 Exclusions

These **MAY** be excluded (with documented rationale):

- Generated code
- Configuration files
- Test fixtures and mocks

---

## 2. Enforcement Commands

### 2.1 Python (pytest-cov)

```bash
# Run with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Generate HTML report
pytest --cov=src --cov-report=html

# Configuration in pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["**/tests/**", "**/__pycache__/**"]
```

---

## 3. Test Organization

### 3.1 Knowledge MCP Test Structure

```
tests/
├── __init__.py
├── conftest.py             # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_chunk/
│   │   ├── __init__.py
│   │   ├── test_hierarchical.py
│   │   └── test_semantic.py
│   ├── test_embed/
│   │   └── test_openai_embedder.py
│   └── test_store/
│       ├── test_qdrant_store.py
│       └── test_chromadb_store.py
├── integration/
│   ├── __init__.py
│   ├── test_ingest_pipeline.py
│   └── test_mcp_server.py
└── fixtures/
    ├── sample_pdf.pdf
    ├── sample_docx.docx
    └── expected_chunks.json
```

---

## 4. Test Naming Conventions

### 4.1 Test Functions

```python
# Python - descriptive snake_case
def test_search_returns_results_for_valid_query():
def test_search_raises_error_for_empty_query():
def test_ingest_handles_malformed_pdf():
```

### 4.2 Test Classes

```python
# Python - Group by method/feature
class TestQdrantStoreSearch:
    """Tests for QdrantStore.search method."""

class TestSemanticChunkerProcess:
    """Tests for SemanticChunker.process method."""
```

---

## 5. Test Patterns

### 5.1 Arrange-Act-Assert (AAA)

```python
def test_search_returns_results(self, service, mock_store):
    # Arrange
    query = "systems engineering process"
    mock_store.search.return_value = [
        {"content": "SE process overview", "score": 0.95}
    ]

    # Act
    results = service.search(query, n_results=5)

    # Assert
    assert len(results) == 1
    assert results[0]["score"] == 0.95
    mock_store.search.assert_called_once()
```

### 5.2 Fixtures

```python
# Python - pytest fixtures
@pytest.fixture
def mock_embedder() -> AsyncMock:
    """Create a mock embedder for testing."""
    embedder = AsyncMock(spec=OpenAIEmbedder)
    embedder.embed.return_value = [0.1] * 1536
    return embedder


@pytest.fixture
def mock_store() -> MagicMock:
    """Create a mock vector store for testing."""
    return MagicMock(spec=QdrantStore)


@pytest.fixture
def search_service(mock_embedder: AsyncMock, mock_store: MagicMock) -> SemanticSearch:
    """Create a search service with mocked dependencies."""
    return SemanticSearch(embedder=mock_embedder, store=mock_store)
```

---

## 6. Mocking

### 6.1 Python (unittest.mock)

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Mock OpenAI client for testing."""
    client = MagicMock()
    client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1] * 1536)]
    )
    return client


# Patching
@patch("knowledge_mcp.embed.openai_embedder.OpenAI")
async def test_embed_with_patched_client(mock_openai):
    mock_openai.return_value.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1] * 1536)]
    )
    # ... test code
```

---

## 7. Async Testing

### 7.1 pytest-asyncio Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### 7.2 Async Test Examples

```python
import pytest


class TestAsyncOperations:
    """Tests for async operations."""

    async def test_async_search(
        self,
        search_service: SemanticSearch,
    ) -> None:
        """Test async search operation."""
        # Arrange
        query = "test query"

        # Act
        results = await search_service.search_async(query)

        # Assert
        assert results is not None


    async def test_async_embed_batch(
        self,
        embedder: OpenAIEmbedder,
    ) -> None:
        """Test batch embedding operation."""
        # Arrange
        texts = ["text 1", "text 2", "text 3"]

        # Act
        embeddings = await embedder.embed_batch(texts)

        # Assert
        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)
```

---

## 8. CI Integration

### 8.1 GitHub Actions

```yaml
test-python:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - run: pip install poetry
    - run: poetry install
    - name: Run tests with coverage
      run: poetry run pytest --cov --cov-report=xml --cov-fail-under=80
    - uses: codecov/codecov-action@v4
```

---

## 9. Test Data Management

### 9.1 Fixtures Directory

Store test data in `tests/fixtures/`:

```
tests/fixtures/
├── sample_documents/
│   ├── ieee_15288_excerpt.pdf
│   └── incose_handbook_section.docx
├── expected_chunks/
│   └── ieee_15288_chunks.json
└── embeddings/
    └── cached_embeddings.json
```

### 9.2 Loading Fixtures

```python
from pathlib import Path
import json


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_pdf(fixtures_dir: Path) -> Path:
    """Return path to sample PDF."""
    return fixtures_dir / "sample_documents" / "ieee_15288_excerpt.pdf"


@pytest.fixture
def expected_chunks(fixtures_dir: Path) -> list[dict]:
    """Load expected chunks from fixture."""
    chunks_file = fixtures_dir / "expected_chunks" / "ieee_15288_chunks.json"
    return json.loads(chunks_file.read_text())
```