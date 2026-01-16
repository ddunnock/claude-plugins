# Python Standards

> **Applies to**: All Python code in Knowledge MCP
> **Version Constraint**: ≥3.11,<3.14
> **Parent**: `constitution.md`

---

## 1. Version and Runtime

| Constraint      | Value   | Rationale                                             |
|-----------------|---------|-------------------------------------------------------|
| Minimum Version | 3.11    | Pattern matching, `tomllib`, performance improvements |
| Maximum Version | <3.14   | 3.14 excluded pending stability assessment            |
| Runtime         | CPython | Standard runtime                                      |

---

## 2. Dependency Management

### 2.1 Poetry Configuration

This project uses Poetry for dependency management with the src layout.

**Package structure:**
```
src/
└── knowledge_mcp/
    ├── __init__.py
    ├── __main__.py
    └── ...
```

**pyproject.toml key settings:**
```toml
[tool.poetry]
packages = [{include = "knowledge_mcp", from = "src"}]
```

### 2.2 Development Commands

```bash
# Install dependencies
poetry install

# Add production dependency
poetry add <package>

# Add development dependency
poetry add --group dev <package>

# Update dependencies
poetry update

# Check outdated
poetry show --outdated
```

---

## 3. Documentation Standards

### 3.1 Module Docstrings

Every module **MUST** have a module-level docstring:

```python
"""
Document ingestion module for Knowledge MCP.

This module provides PDF, DOCX, and Markdown ingestion
for the Knowledge MCP semantic search system.

Example:
    >>> from knowledge_mcp.ingest import PDFIngestor
    >>> ingestor = PDFIngestor()
    >>> chunks = await ingestor.ingest("document.pdf")

Attributes:
    DEFAULT_CHUNK_SIZE: Default chunk size in tokens (512).
"""
```

### 3.2 Function Docstrings

All functions **MUST** use Google-style docstrings:

```python
async def search(
    query: str,
    n_results: int = 5,
    filter_dict: dict[str, str] | None = None,
) -> list[SearchResult]:
    """
    Search the knowledge base for relevant content.

    Performs semantic search using the configured vector store
    and returns the most relevant chunks.

    Args:
        query: Natural language search query.
        n_results: Maximum number of results to return.
            Defaults to 5.
        filter_dict: Optional metadata filters to apply.
            Keys are field names, values are exact matches.

    Returns:
        List of SearchResult objects ordered by relevance.
        Each result contains content, score, and metadata.

    Raises:
        ConnectionError: When vector store is unreachable.
        ValueError: When query is empty.

    Example:
        >>> results = await search("system requirements")
        >>> for r in results:
        ...     print(f"{r.score:.2f}: {r.content[:50]}...")
    """
```

### 3.3 Class Docstrings

```python
class QdrantStore:
    """
    Qdrant Cloud vector store implementation.

    Provides storage and retrieval of document chunks with
    semantic search capabilities via Qdrant Cloud.

    Attributes:
        collection: Name of the Qdrant collection.
        client: Qdrant client instance.
        hybrid_enabled: Whether hybrid search is active.

    Example:
        >>> store = QdrantStore(config)
        >>> await store.add_chunks(chunks)
        >>> results = await store.search(embedding)
    """

    def __init__(self, config: StoreConfig) -> None:
        """
        Initialize QdrantStore with configuration.

        Args:
            config: Store configuration with connection details.

        Raises:
            ConnectionError: When Qdrant Cloud is unreachable.
        """
```

---

## 4. Type Safety

### 4.1 Type Hint Requirements

- All function parameters **MUST** have type hints
- All function return types **MUST** be annotated
- Use `from __future__ import annotations` for forward references
- Prefer `collections.abc` types over `typing` equivalents
- Use `TypeVar` and `Generic` for generic types

### 4.2 Pyright Configuration

Pyright **MUST** be configured in strict mode (already in pyproject.toml):

```toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
include = ["src"]
exclude = ["**/tests/**"]
reportMissingTypeStubs = "warning"
reportUnusedImport = "error"
reportUnusedVariable = "error"
```

### 4.3 Running Type Checks

```bash
# Run type checking
poetry run pyright

# Or directly
pyright src/
```

---

## 5. Linting and Formatting

### 5.1 Ruff Configuration

Already configured in pyproject.toml:

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "B", "C4", "UP",
    "ARG", "SIM", "TCH", "PTH", "ERA",
    "PL", "RUF", "D"
]
ignore = ["D100", "D104"]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

### 5.2 Running Linting

```bash
# Check for issues
poetry run ruff check src tests

# Format code
poetry run ruff format src tests

# Auto-fix issues
poetry run ruff check --fix src tests
```

---

## 6. Required Package Files

### 6.1 `__init__.py`

Every directory containing Python modules **MUST** have an `__init__.py`:

```python
# src/knowledge_mcp/__init__.py
"""
Knowledge MCP - Semantic search over technical reference documents.

This package provides an MCP server for RAG capabilities
over IEEE standards, INCOSE guides, and NASA handbooks.
"""

from knowledge_mcp.server import KnowledgeMCPServer

__version__ = "0.1.0"
__all__ = ["KnowledgeMCPServer"]
```

### 6.2 `__main__.py`

The package **MUST** have `__main__.py` for `python -m knowledge_mcp`:

```python
# src/knowledge_mcp/__main__.py
"""
Entry point for running Knowledge MCP as a module.

Usage:
    python -m knowledge_mcp [options]
"""

import sys

from knowledge_mcp.cli import main


def cli() -> int:
    """CLI entry point."""
    try:
        main()
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli())
```

---

## 7. Testing

### 7.1 Test Structure

```
tests/
├── __init__.py
├── conftest.py             # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_chunk/
│   │   ├── __init__.py
│   │   └── test_hierarchical.py
│   ├── test_embed/
│   └── test_store/
├── integration/
│   ├── __init__.py
│   └── test_server.py
└── fixtures/
    └── sample_documents/
```

### 7.2 Test Pattern (AAA)

```python
"""Unit tests for QdrantStore."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.store.qdrant_store import QdrantStore
from knowledge_mcp.models.chunk import KnowledgeChunk


class TestQdrantStoreSearch:
    """Tests for QdrantStore.search method."""

    @pytest.fixture
    def mock_client(self) -> MagicMock:
        """Create a mock Qdrant client."""
        return MagicMock()

    @pytest.fixture
    def store(self, mock_client: MagicMock) -> QdrantStore:
        """Create store with mocked client."""
        store = QdrantStore.__new__(QdrantStore)
        store.client = mock_client
        store.collection = "test_collection"
        return store

    def test_search_returns_results(
        self,
        store: QdrantStore,
        mock_client: MagicMock,
    ) -> None:
        """Test that search returns properly formatted results."""
        # Arrange
        mock_client.search.return_value = [
            MagicMock(id="chunk-1", score=0.95, payload={"content": "Test"})
        ]

        # Act
        results = store.search([0.1] * 1536, n_results=5)

        # Assert
        assert len(results) == 1
        assert results[0]["score"] == 0.95
```

### 7.3 Running Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/test_store/

# Run with verbose output
poetry run pytest -v --tb=short
```

---

## 8. Error Handling

### 8.1 Exception Hierarchy

```python
class KnowledgeMCPError(Exception):
    """Base exception for Knowledge MCP errors."""


class ConfigurationError(KnowledgeMCPError):
    """Raised when configuration is invalid."""


class IngestionError(KnowledgeMCPError):
    """Raised when document ingestion fails."""


class EmbeddingError(KnowledgeMCPError):
    """Raised when embedding generation fails."""


class SearchError(KnowledgeMCPError):
    """Raised when search operations fail."""
```

### 8.2 Error Handling Pattern

```python
async def ingest_document(path: Path) -> list[KnowledgeChunk]:
    """Ingest a document with proper error handling."""
    if not path.exists():
        raise IngestionError(f"Document not found: {path}")

    try:
        content = await read_document(path)
    except IOError as e:
        raise IngestionError(f"Failed to read {path}: {e}") from e

    if not content.strip():
        raise IngestionError(f"Document is empty: {path}")

    return await process_content(content)
```

---

## 9. Async Patterns

### 9.1 Async Context Managers

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator


@asynccontextmanager
async def get_qdrant_client() -> AsyncIterator[QdrantClient]:
    """Provide Qdrant client with proper cleanup."""
    client = QdrantClient(url=settings.qdrant_url)
    try:
        yield client
    finally:
        await client.close()
```

### 9.2 Concurrent Operations

```python
import asyncio


async def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed multiple chunks concurrently."""
    tasks = [embed_single(chunk) for chunk in chunks]
    return await asyncio.gather(*tasks)
```

---

## 10. Configuration

### 10.1 Pydantic Settings

```python
from pydantic import BaseModel, Field


class StoreConfig(BaseModel):
    """Configuration for vector store."""

    qdrant_url: str = Field(..., description="Qdrant Cloud URL")
    qdrant_api_key: str = Field(..., description="Qdrant API key")
    collection_name: str = Field(default="knowledge", description="Collection name")

    def validate(self) -> list[str]:
        """Validate configuration."""
        errors = []
        if not self.qdrant_url:
            errors.append("QDRANT_URL is required")
        return errors
```

### 10.2 Environment Variables

Required:
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `QDRANT_URL` - Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Qdrant Cloud API key