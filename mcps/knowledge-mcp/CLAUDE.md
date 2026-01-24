# Knowledge MCP - Claude Development Standards

> **Version**: 1.0.0
> **Parent Standards**: `docs/reference/claude-standards/constitution.md`
> **Project Type**: Python MCP Server
> **Python Version**: ≥3.11,<3.14

---

## 1. Project Overview

Knowledge MCP is a Model Context Protocol (MCP) server for semantic search over technical reference documents (IEEE standards, INCOSE guides, NASA handbooks). It provides RAG (Retrieval Augmented Generation) capabilities for systems engineering knowledge.

### 1.1 Technology Stack

| Component       | Technology                                  | Standard Reference   |
|-----------------|---------------------------------------------|----------------------|
| Language        | Python ≥3.11,<3.14                          | `python.md` §1       |
| Package Manager | Poetry                                      | `python.md` §2.3     |
| Type Checking   | Pyright (strict mode)                       | `python.md` §4.2     |
| Linting         | Ruff                                        | `python.md` §5.1     |
| Testing         | pytest + pytest-asyncio                     | `testing.md` §2.1    |
| Documentation   | Google-style docstrings                     | `python.md` §3       |
| Vector Store    | Qdrant Cloud (primary), ChromaDB (fallback) | -                    |
| Embeddings      | OpenAI text-embedding-3-small               | -                    |

---

## 2. Project Structure

This project **MUST** follow the standard Python package layout:

```
knowledge-mcp/
├── CLAUDE.md                    # This file
├── pyproject.toml               # Poetry configuration
├── poetry.lock                  # Locked dependencies (committed)
├── README.md                    # Project documentation
├── LICENSE
├── .env.example                 # Environment template
├── .gitignore
│
├── src/
│   └── knowledge_mcp/           # Main package
│       ├── __init__.py          # Package initialization (REQUIRED)
│       ├── __main__.py          # Entry point (REQUIRED)
│       ├── server.py            # MCP server implementation
│       │
│       ├── ingest/              # Document ingestion
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── pdf_ingestor.py
│       │   ├── docx_ingestor.py
│       │   └── markdown_ingestor.py
│       │
│       ├── chunk/               # Chunking strategies
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── hierarchical.py
│       │   ├── semantic.py
│       │   └── standards.py
│       │
│       ├── embed/               # Embedding generation
│       │   ├── __init__.py
│       │   ├── openai_embedder.py
│       │   └── local_embedder.py
│       │
│       ├── store/               # Vector storage
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── qdrant_store.py
│       │   └── chromadb_store.py
│       │
│       ├── search/              # Search and retrieval
│       │   ├── __init__.py
│       │   ├── semantic_search.py
│       │   ├── hybrid_search.py
│       │   └── reranker.py
│       │
│       ├── models/              # Data models
│       │   ├── __init__.py
│       │   ├── chunk.py
│       │   └── document.py
│       │
│       └── utils/               # Utilities
│           ├── __init__.py
│           ├── config.py
│           ├── hashing.py
│           └── tokenizer.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_chunk/
│   │   ├── test_embed/
│   │   └── test_store/
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_server.py
│   └── fixtures/
│       └── sample_documents/
│
├── scripts/
│   ├── ingest_documents.py
│   ├── verify_embeddings.py
│   ├── setup_qdrant.py
│   └── export_collection.py
│
├── data/
│   ├── sources/                 # Place source documents here
│   └── processed/               # Intermediate processing output
│
└── docs/                        # Sphinx documentation
    ├── conf.py
    ├── index.md
    ├── tutorials/
    ├── how-to/
    ├── reference/
    └── explanation/
```

### 2.1 Required Files

Every directory containing Python modules **MUST** have an `__init__.py` file.

Every package **MUST** have a `__main__.py` enabling execution via `python -m knowledge_mcp`.

---

## 3. Code Standards

### 3.1 Type Hints

All code **MUST** use type hints and pass Pyright strict mode with zero errors.

```python
from __future__ import annotations

from typing import Optional
from collections.abc import Sequence


def search(
    query: str,
    n_results: int = 5,
    filter_dict: Optional[dict[str, str]] = None,
) -> list[dict[str, any]]:
    """Search the knowledge base."""
    ...
```

### 3.2 Docstrings

All public APIs **MUST** use Google-style docstrings:

```python
def add_chunks(self, chunks: list[KnowledgeChunk]) -> int:
    """
    Add chunks to the vector store.

    Args:
        chunks: List of KnowledgeChunk objects to store.
            Each chunk must have an embedding.

    Returns:
        Number of chunks successfully added.

    Raises:
        ValueError: When chunks list is empty.
        ConnectionError: When Qdrant Cloud is unreachable.

    Example:
        >>> store = QdrantStore(config)
        >>> chunks = [KnowledgeChunk(...)]
        >>> count = store.add_chunks(chunks)
        >>> print(f"Added {count} chunks")
    """
    ...
```

### 3.3 Error Handling

- Use specific exception types, not bare `except`
- Include context in error messages
- Log errors before re-raising when appropriate

```python
class KnowledgeMCPError(Exception):
    """Base exception for Knowledge MCP errors."""


class ConfigurationError(KnowledgeMCPError):
    """Raised when configuration is invalid."""


class IngestionError(KnowledgeMCPError):
    """Raised when document ingestion fails."""


class EmbeddingError(KnowledgeMCPError):
    """Raised when embedding generation fails."""
```

---

## 4. Testing Requirements

### 4.1 Coverage Thresholds

| Metric            | Minimum   | Target   | Blocking  |
|-------------------|-----------|----------|-----------|
| Line Coverage     | 80%       | 90%      | Yes       |
| Branch Coverage   | 75%       | 85%      | Yes       |
| Function Coverage | 85%       | 95%      | Yes       |

### 4.2 Test Organization

```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_config.py           # Configuration tests
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

### 4.3 Test Pattern

Use Arrange-Act-Assert (AAA) pattern:

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
        """Create a store instance with mocked client."""
        store = QdrantStore.__new__(QdrantStore)
        store.client = mock_client
        store.collection = "test_collection"
        store.hybrid_enabled = False
        return store

    def test_search_returns_results(
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
        results = store.search(query_embedding, n_results=5)

        # Assert
        assert len(results) == 1
        assert results[0]["content"] == "Test content"
        assert results[0]["score"] == 0.95
```

---

## 5. Configuration

### 5.1 Environment Variables

All configuration **MUST** use environment variables with `.env` file support.

Required variables:
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `QDRANT_URL` - Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Qdrant Cloud API key

### 5.2 Configuration Validation

Configuration **MUST** be validated at startup with clear error messages:

```python
def validate(self) -> list[str]:
    """
    Validate configuration.

    Returns:
        List of validation error messages. Empty if valid.
    """
    errors = []
    if not self.openai_api_key:
        errors.append("OPENAI_API_KEY is required")
    if self.vector_store == "qdrant":
        if not self.qdrant_url:
            errors.append("QDRANT_URL is required when using Qdrant")
        if not self.qdrant_api_key:
            errors.append("QDRANT_API_KEY is required for Qdrant Cloud")
    return errors
```

---

## 6. Dependency Management

### 6.1 Poetry Configuration

This project uses Poetry for dependency management per `python.md` §2.3.

### 6.2 Version Freshness

All dependencies **MUST** use the latest stable version unless a documented conflict exists.

```bash
# Check for outdated dependencies
poetry show --outdated

# Update all dependencies
poetry update
```

### 6.3 Security Scanning

Dependencies **MUST** be scanned for vulnerabilities:

```bash
# Install pip-audit
pip install pip-audit

# Run security scan
pip-audit --strict
```

---

## 7. Git Workflow

### 7.1 Commit Messages

Follow Conventional Commits specification:

```
feat(store): add hybrid search support for Qdrant
fix(ingest): handle malformed PDF metadata
docs(readme): update installation instructions
test(chunk): add hierarchical chunker tests
refactor(embed): extract base embedder interface
```

### 7.2 Branch Naming

```
feature/ABC-123-add-hybrid-search
fix/ABC-124-pdf-metadata-parsing
chore/ABC-125-update-dependencies
```

---

## 8. Documentation

### 8.1 Diátaxis Framework

Documentation **MUST** follow the Diátaxis framework:

| Quadrant      | Purpose                   | Location            |
|---------------|---------------------------|---------------------|
| Tutorials     | Learning by doing         | `docs/tutorials/`   |
| How-To Guides | Solving specific problems | `docs/how-to/`      |
| Reference     | Looking up information    | `docs/reference/`   |
| Explanation   | Understanding concepts    | `docs/explanation/` |

### 8.2 Required Documents

| Document                            | Purpose               | Update Frequency   |
|-------------------------------------|-----------------------|--------------------|
| `README.md`                         | Quick start, overview | On feature changes |
| `CHANGELOG.md`                      | Version history       | Every release      |
| `docs/tutorials/getting-started.md` | First-time setup      | On major changes   |
| `docs/how-to/ingest-documents.md`   | Document ingestion    | On API changes     |
| `docs/reference/api.md`             | API reference         | On API changes     |

---

## 9. Security

### 9.1 Secrets Management

- **NEVER** commit secrets to version control
- Use `.env` files (gitignored) for local development
- Use environment variables in production

### 9.2 Input Validation

All external input **MUST** be validated:

```python
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Validated search request."""

    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(default=5, ge=1, le=100)
    document_type: str | None = Field(default=None, max_length=50)
```

---

## 10. MCP Server Standards

### 10.1 Tool Definitions

MCP tools **MUST** have comprehensive descriptions:

```python
Tool(
    name="knowledge_search",
    description="""Search the systems engineering knowledge base.

Use this to find:
- Standards requirements (IEEE, ISO, INCOSE)
- Best practices and guidance
- Technical definitions

Backend: Qdrant Cloud with hybrid search support.""",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query"
            },
            # ... more properties
        },
        "required": ["query"]
    }
)
```

### 10.2 Error Handling

MCP tools **MUST** return structured error responses:

```python
try:
    results = await knowledge.search(query)
    return [TextContent(type="text", text=json.dumps(results, indent=2))]
except Exception as e:
    return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
```

---

## 11. Exception Handling (ADRs)

Any deviation from these standards **MUST** be documented in an ADR:

```markdown
# ADR-001: Use Hatchling Instead of Poetry

## Status
Superseded by ADR-002

## Context
Initial development used Hatchling for simplicity.

## Decision
Migrate to Poetry to comply with python.md standards.

## Consequences
- Better dependency resolution
- Lock file for reproducibility
- Consistent with other projects
```

---

## 12. Quick Reference

### 12.1 Development Commands

```bash
# Install dependencies
poetry install

# Run tests with coverage
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run linting
poetry run ruff check src tests
poetry run ruff format src tests

# Run type checking
poetry run pyright

# Run MCP server
poetry run python -m knowledge_mcp

# Ingest documents
poetry run python -m knowledge_mcp.cli.ingest --source ./data/sources
```

### 12.2 Pre-commit Checklist

- [ ] All tests pass
- [ ] Coverage ≥80%
- [ ] Pyright passes (zero errors)
- [ ] Ruff passes (zero errors)
- [ ] Documentation updated
- [ ] Commit message follows Conventional Commits

---

*This document adheres to the standards defined in `docs/reference/claude-standards/`.*
