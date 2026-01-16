# Testing Standards

> **Applies to**: All automated tests in Knowledge MCP
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
- `__main__.py` entry points

---

## 2. Enforcement Commands

### 2.1 pytest-cov Configuration

Already configured in pyproject.toml:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["**/tests/**", "**/__pycache__/**"]
```

### 2.2 Running Tests

```bash
# Run with coverage (default)
poetry run pytest

# Generate HTML report
poetry run pytest --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_store/

# Run with verbose output
poetry run pytest -v --tb=short
```

---

## 3. Test Organization

### 3.1 Directory Structure

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
│   ├── test_store/
│   │   ├── test_qdrant_store.py
│   │   └── test_chromadb_store.py
│   └── test_config.py
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
# Descriptive snake_case
def test_search_returns_results_for_valid_query():
def test_search_raises_error_for_empty_query():
def test_ingest_handles_malformed_pdf():
```

### 4.2 Test Classes

```python
class TestQdrantStoreSearch:
    """Tests for QdrantStore.search method."""

class TestQdrantStoreAdd:
    """Tests for QdrantStore.add_chunks method."""
```

---

## 5. Test Patterns

### 5.1 Arrange-Act-Assert (AAA)

```python
async def test_search_returns_results(
    self,
    store: QdrantStore,
    mock_client: MagicMock,
) -> None:
    """Test that search returns properly formatted results."""
    # Arrange
    mock_client.search.return_value = [
        MagicMock(
            id="chunk-1",
            score=0.95,
            payload={"content": "Test content", "document_title": "IEEE 15288"},
        )
    ]
    query_embedding = [0.1] * 1536

    # Act
    results = await store.search(query_embedding, n_results=5)

    # Assert
    assert len(results) == 1
    assert results[0]["content"] == "Test content"
    assert results[0]["score"] == 0.95
```

### 5.2 Fixtures

```python
# tests/conftest.py
"""Shared fixtures for Knowledge MCP tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from knowledge_mcp.utils.config import Config


@pytest.fixture
def mock_config() -> Config:
    """Create a test configuration."""
    return Config(
        openai_api_key="test-key",
        qdrant_url="http://localhost:6333",
        qdrant_api_key="test-key",
    )


@pytest.fixture
def mock_qdrant_client() -> MagicMock:
    """Create a mock Qdrant client."""
    client = MagicMock()
    client.search = AsyncMock(return_value=[])
    return client


@pytest.fixture
def sample_chunks() -> list[dict]:
    """Create sample chunks for testing."""
    return [
        {
            "id": "chunk-1",
            "content": "System requirements define...",
            "metadata": {"source": "IEEE 15288", "section": "6.1"},
        },
        {
            "id": "chunk-2",
            "content": "Verification ensures...",
            "metadata": {"source": "IEEE 15288", "section": "6.2"},
        },
    ]
```

---

## 6. Mocking

### 6.1 unittest.mock

```python
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create a mock OpenAI client."""
    client = MagicMock()
    client.embeddings.create = AsyncMock(
        return_value=MagicMock(
            data=[MagicMock(embedding=[0.1] * 1536)]
        )
    )
    return client


# Patching
@patch("knowledge_mcp.embed.openai_embedder.OpenAI")
async def test_embedder_calls_api(mock_openai_class):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.embeddings.create = AsyncMock(...)
    # Test implementation
```

### 6.2 pytest-mock

```python
def test_with_mocker(mocker):
    """Test using pytest-mock."""
    mock_func = mocker.patch("knowledge_mcp.module.function")
    mock_func.return_value = "mocked"
    # Test implementation
```

---

## 7. Async Testing

### 7.1 pytest-asyncio Configuration

Already configured with `asyncio_mode = "auto"`:

```python
# No decorator needed with auto mode
async def test_async_search():
    """Test async search function."""
    result = await search("query")
    assert result is not None
```

### 7.2 Async Fixtures

```python
@pytest.fixture
async def async_client():
    """Create an async client."""
    client = await create_client()
    yield client
    await client.close()
```

---

## 8. Integration Testing

### 8.1 MCP Server Tests

```python
# tests/integration/test_mcp_server.py
"""Integration tests for Knowledge MCP server."""

import pytest
from knowledge_mcp.server import KnowledgeMCPServer


class TestMCPServerIntegration:
    """Integration tests for MCP server."""

    @pytest.fixture
    async def server(self, mock_config):
        """Create a server instance."""
        server = KnowledgeMCPServer(mock_config)
        await server.initialize()
        yield server
        await server.shutdown()

    async def test_search_tool_returns_results(self, server):
        """Test the search tool integration."""
        result = await server.call_tool(
            "knowledge_search",
            {"query": "system requirements"}
        )
        assert "content" in result
```

### 8.2 Pipeline Tests

```python
# tests/integration/test_ingest_pipeline.py
"""Integration tests for document ingestion pipeline."""

import pytest
from pathlib import Path


class TestIngestionPipeline:
    """Test the full ingestion pipeline."""

    @pytest.fixture
    def sample_pdf(self, tmp_path) -> Path:
        """Create a sample PDF for testing."""
        # Create or copy test PDF
        return tmp_path / "sample.pdf"

    async def test_pdf_ingestion_pipeline(self, sample_pdf):
        """Test PDF → chunks → embeddings → store."""
        # Test full pipeline
```

---

## 9. CI Integration

### 9.1 GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run tests
        run: poetry run pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

## 10. Test Quality Checklist

Before committing tests:

- [ ] Tests follow AAA pattern
- [ ] Test names are descriptive
- [ ] Fixtures are in conftest.py or test module
- [ ] Mocks are scoped appropriately
- [ ] Async tests use proper patterns
- [ ] Coverage threshold met (80%+)
- [ ] No flaky tests