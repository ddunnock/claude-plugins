# Python Standards

> **Applies to**: All Python code in this project
> **Version Constraint**: >=3.11,<3.14
> **Parent**: `constitution.md`

---

## 1. Version and Runtime

| Constraint      | Value   | Rationale                                                      |
|-----------------|---------|----------------------------------------------------------------|
| Minimum Version | 3.11    | Pattern matching, `tomllib`, performance improvements          |
| Maximum Version | <3.14   | 3.14 excluded pending stability assessment                     |
| Runtime         | CPython | PyPy acceptable for performance-critical services with testing |

---

## 1.1 Design Philosophy (PEP 20)

Python code **MUST** embody [The Zen of Python (PEP 20)](https://peps.python.org/pep-0020/) as actionable rules:

| Principle                                 | Rule Level  | Actionable Directive                                                                               |
|-------------------------------------------|-------------|----------------------------------------------------------------------------------------------------|
| Readability counts                        | **MUST**    | Prefer clear variable names over terse abbreviations; prioritize understandability over cleverness |
| Explicit is better than implicit          | **MUST**    | Avoid magic methods, hidden state, or implicit type coercion; make behavior obvious                |
| Simple is better than complex             | **MUST**    | Resist premature optimization; solve the immediate problem without speculative generalization      |
| Flat is better than nested                | **SHOULD**  | Limit nesting to 3 levels; extract nested logic into named functions                               |
| Sparse is better than dense               | **SHOULD**  | One statement per line; avoid compound one-liners that sacrifice clarity                           |
| Errors should never pass silently         | **MUST**    | Never use bare `except:`; catch specific exceptions and handle or re-raise                         |
| In the face of ambiguity, refuse to guess | **MUST**    | Require explicit configuration over convention-based defaults                                      |
| There should be one obvious way           | **SHOULD**  | Follow established patterns from this memory file rather than inventing alternatives               |
| Practicality beats purity                 | **SHOULD**  | Trade-off purity for pragmatism when justified with inline comments                                |

---

## 2. Dependency Management

### 2.1 Poetry for Knowledge MCP

This project uses Poetry for dependency management:

```
knowledge-mcp/
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Locked dependencies (committed)
├── src/
│   └── knowledge_mcp/          # Main package directory
│       ├── __init__.py         # Package initialization (REQUIRED)
│       ├── __main__.py         # Entry point (REQUIRED)
│       ├── server.py           # MCP server implementation
│       ├── ingest/             # Document ingestion
│       ├── chunk/              # Chunking strategies
│       ├── embed/              # Embedding generation
│       ├── store/              # Vector storage
│       ├── search/             # Search and retrieval
│       ├── models/             # Data models
│       └── utils/              # Utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── unit/
└── scripts/
```

---

## 3. Documentation Standards

### 3.1 Module Docstrings

Every module **MUST** have a module-level docstring:

```python
"""
Module-level docstring describing purpose and usage.

This module provides [functionality] for [use case].

Example:
    >>> from module import function
    >>> result = function(arg)

Attributes:
    MODULE_CONSTANT: Description of module-level constant.

Note:
    Any important usage notes or caveats.
"""
```

### 3.2 Function Docstrings

All functions **MUST** use Google-style docstrings:

```python
def function_name(
    param1: str,
    param2: int,
    *,
    keyword_only: bool = False,
    optional_param: str | None = None,
) -> dict[str, any]:
    """
    Brief one-line description of function purpose.

    Args:
        param1: Description of param1, including valid values.
        param2: Description of param2, including constraints.
        keyword_only: Description of keyword-only parameter.
            Defaults to False.
        optional_param: Description of optional parameter.
            Defaults to None.

    Returns:
        Description of return value structure and semantics.

    Raises:
        ValueError: When param1 is empty or param2 is negative.
        TypeError: When parameters are of incorrect type.

    Example:
        >>> result = function_name("test", 42, keyword_only=True)
        >>> print(result["status"])
        'success'
    """
    pass
```

### 3.3 Class Docstrings

```python
class ClassName(Generic[T]):
    """
    Brief one-line description of class purpose.

    Attributes:
        instance_attr: Description of instance attribute.
        class_attr: Description of class attribute.

    Example:
        >>> obj = ClassName(value=42)
        >>> obj.method()
        'result'
    """

    class_attr: str = "default"

    def __init__(self, value: T) -> None:
        """
        Initialize ClassName instance.

        Args:
            value: Initial value for the instance.

        Raises:
            ValueError: When value is invalid.
        """
        self.instance_attr: T = value
```

---

## 4. Type Safety

### 4.1 Type Hint Requirements

- All function parameters **MUST** have type hints
- All function return types **MUST** be annotated
- Use `from __future__ import annotations` for forward references
- Prefer `collections.abc` types over `typing` equivalents (Python 3.11+)
- Use `TypeVar` and `Generic` for generic types
- Use `Protocol` for structural subtyping
- Use `Literal` for constrained string/int values

### 4.2 Pyright Configuration

Pyright **MUST** be configured in strict mode in `pyproject.toml`:

```toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
include = ["src"]
reportMissingTypeStubs = "warning"
reportUnusedImport = "error"
reportUnusedVariable = "error"
reportUnnecessaryTypeIgnoreComment = "error"
```

---

## 5. Linting and Formatting

### 5.1 Ruff Configuration

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate
    "PL",     # pylint
    "RUF",    # Ruff-specific rules
    "D",      # pydocstyle
]
ignore = ["D100", "D104"]  # Module docstrings optional for __init__.py

[tool.ruff.lint.pydocstyle]
convention = "google"
```

---

## 6. Required Package Files

### 6.1 `__init__.py`

Every directory containing Python modules **MUST** have an `__init__.py`:

```python
# src/knowledge_mcp/__init__.py
"""
Knowledge MCP - Semantic search over technical reference documents.

This package provides MCP server capabilities for searching IEEE standards,
INCOSE guides, NASA handbooks, and other systems engineering knowledge.
"""

from knowledge_mcp.server import serve

__version__ = "0.1.0"
__all__ = ["serve"]
```

### 6.2 `__main__.py`

Every package **MUST** have a `__main__.py` enabling `python -m knowledge_mcp`:

```python
# src/knowledge_mcp/__main__.py
"""
Entry point for running Knowledge MCP as a module.

Usage:
    python -m knowledge_mcp [options]

Examples:
    python -m knowledge_mcp --help
    python -m knowledge_mcp serve
"""

import sys

from knowledge_mcp.cli import main


def cli() -> int:
    """
    Command-line interface entry point.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
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
"""Unit tests for the QdrantStore."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.store.qdrant_store import QdrantStore


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock Qdrant client."""
    return MagicMock()


class TestQdrantStoreSearch:
    """Tests for QdrantStore.search method."""

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

### 7.3 Coverage Enforcement

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

---

## 8. Security Practices

### 8.1 Prohibited Functions (MUST NOT)

| Function                               | Risk                     | Alternative              |
|----------------------------------------|--------------------------|--------------------------|
| `eval()` / `exec()`                    | Code injection           | Use `ast.literal_eval()` |
| `pickle.load()` from untrusted sources | Arbitrary code execution | Use JSON                 |
| `shell=True` in subprocess             | Command injection        | Use argument list        |
| `yaml.load()` without Loader           | Code execution           | Use `yaml.safe_load()`   |

### 8.2 Secret Management (MUST)

```python
# MUST NOT: Hardcoded secrets
API_KEY = "sk-abc123secret"

# MUST: Environment variables
import os

api_key = os.environ["OPENAI_API_KEY"]
```

### 8.3 Input Validation (MUST)

```python
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    """Validated search request."""

    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(default=5, ge=1, le=100)
```

---

## 9. Module Size Guidelines

| Metric                      | SHOULD  | MUST NOT Exceed   |
|-----------------------------|---------|-------------------|
| Lines per module            | <=300   | 500               |
| Public functions per module | <=7     | 15                |
| Parameters per function     | <=5     | 8                 |
| Cyclomatic complexity       | <=10    | 15                |

---

## 10. Pre-Completion Checklist (MUST)

Before marking any Python task as complete, agents **MUST** verify:

| Check         | Command                            | Pass Criteria     |
|---------------|------------------------------------|-------------------|
| Type checking | `pyright --outputjson`             | Zero errors       |
| Linting       | `ruff check src tests`             | Zero errors       |
| Formatting    | `ruff format --check src tests`    | No changes needed |
| Tests pass    | `pytest`                           | All tests pass    |
| Coverage      | `pytest --cov --cov-fail-under=80` | >=80% coverage    |