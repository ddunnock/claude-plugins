# Python Standards

> **Applies to**: All Python code in this project  
> **Version Constraint**: ≥3.11,<3.14  
> **Parent**: `constitution.md`

---

## 1. Version and Runtime

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Minimum Version | 3.11 | Pattern matching, `tomllib`, performance improvements |
| Maximum Version | <3.14 | 3.14 excluded pending stability assessment |
| Runtime | CPython | PyPy acceptable for performance-critical services with testing |

---

## 2. Dependency Management

### 2.1 Complexity Threshold

Python dependency management **MUST** be selected based on project complexity:

| Complexity Level | Criteria | Tool | Configuration |
|------------------|----------|------|---------------|
| **Simple** | ≤3 standalone scripts, no inter-file imports, no package structure | venv + requirements.txt | `python -m venv .venv` |
| **Standard** | ≥4 files OR any multi-file package OR reusable modules | Poetry | `pyproject.toml` with Poetry backend |

**Decision Flow:**

```
Is this a multi-file Python package?
├─ YES → Use Poetry
└─ NO → Are there ≥4 Python files?
         ├─ YES → Use Poetry
         └─ NO → Do files import from each other?
                  ├─ YES → Use Poetry
                  └─ NO → venv + requirements.txt is acceptable
```

### 2.2 Simple Project Structure

For projects meeting the "Simple" threshold:

```
simple_scripts/
├── requirements.txt            # Pinned dependencies
├── script_one.py               # Standalone script
├── script_two.py               # Standalone script
└── script_three.py             # Standalone script
```

```txt
# requirements.txt
# Generated via: pip freeze > requirements.txt
# Verify latest versions before adding: pip index versions <package>
requests==2.31.0
pyyaml==6.0.1
```

**Setup commands:**

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2.3 Standard Project Structure (Poetry)

All Python packages **MUST** follow proper package structure:

```
project_name/
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Locked dependencies (committed)
├── README.md
├── src/
│   └── package_name/           # Main package directory
│       ├── __init__.py         # Package initialization (REQUIRED)
│       ├── __main__.py         # Entry point (REQUIRED)
│       ├── core/
│       │   ├── __init__.py     # REQUIRED for every directory
│       │   ├── models.py
│       │   └── services.py
│       ├── utils/
│       │   ├── __init__.py     # REQUIRED for every directory
│       │   ├── helpers.py
│       │   └── validators.py
│       └── cli.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_core.py
└── scripts/                    # Standalone scripts (if any)
    └── one_off_task.py
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

    Longer description providing additional context, explaining the
    algorithm, design decisions, or important behavior details.

    Args:
        param1: Description of param1, including valid values.
        param2: Description of param2, including constraints.
        keyword_only: Description of keyword-only parameter.
            Defaults to False.
        optional_param: Description of optional parameter.
            Defaults to None.

    Returns:
        Description of return value structure and semantics.
        For complex returns, use a structured format:
            - key1: Description of key1 value
            - key2: Description of key2 value

    Raises:
        ValueError: When param1 is empty or param2 is negative.
        TypeError: When parameters are of incorrect type.

    Example:
        >>> result = function_name("test", 42, keyword_only=True)
        >>> print(result["status"])
        'success'

    Note:
        Any important caveats or side effects.

    See Also:
        - related_function: For alternative approach
        - OtherClass: For object-oriented usage
    """
    pass
```

### 3.3 Class Docstrings

```python
class ClassName(Generic[T]):
    """
    Brief one-line description of class purpose.

    Longer description of class responsibilities, design rationale,
    and typical usage patterns.

    Attributes:
        instance_attr: Description of instance attribute.
        class_attr: Description of class attribute.

    Example:
        >>> obj = ClassName(value=42)
        >>> obj.method()
        'result'

    Note:
        Thread-safety considerations or other important notes.
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

Pyright **MUST** be configured in strict mode:

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
# src/package_name/__init__.py
"""
Package name - Brief description of package purpose.

This package provides [functionality] for [use case].
"""

from package_name.core.models import Model
from package_name.core.services import Service

__version__ = "0.1.0"
__all__ = ["Model", "Service"]
```

### 6.2 `__main__.py`

Every package **MUST** have a `__main__.py` enabling execution via `python -m package_name`:

```python
# src/package_name/__main__.py
"""
Entry point for running package as a module.

Usage:
    python -m package_name [options]
    
Examples:
    python -m package_name --help
    python -m package_name run --config config.yaml
"""

import sys

from package_name.cli import main


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

## 7. Poetry Configuration Template

```toml
[tool.poetry]
name = "package-name"
version = "0.1.0"
description = "Brief description of the package"
authors = ["Author Name <author@example.com>"]
readme = "README.md"
packages = [{include = "package_name", from = "src"}]

[tool.poetry.dependencies]
python = ">=3.11,<3.14"
# Add dependencies at @latest, verify via `poetry show --outdated`

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-cov = "^4.1"
pytest-asyncio = "^0.23"
ruff = "^0.4"
pyright = "^1.1"

[tool.poetry.scripts]
package-name = "package_name.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "TCH", "PTH", "ERA", "PL", "RUF", "D"]
ignore = ["D100", "D104"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
include = ["src"]

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

## 8. Testing

### 8.1 Test Structure

```
tests/
├── __init__.py
├── conftest.py             # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── integration/
│   ├── __init__.py
│   └── test_api.py
└── fixtures/
    └── sample_data.json
```

### 8.2 Test Pattern

```python
"""Unit tests for the ResourceService."""

from datetime import datetime, UTC
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.models import Resource, User
from app.services import ResourceService
from app.schemas import ResourceCreate


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Create a mock repository for testing."""
    return AsyncMock(spec=ResourceRepository)


@pytest.fixture
def service(mock_repository: AsyncMock) -> ResourceService:
    """Create a service instance with mocked dependencies."""
    return ResourceService(repository=mock_repository)


class TestResourceServiceCreate:
    """Tests for ResourceService.create method."""

    async def test_create_resource_success(
        self,
        service: ResourceService,
        mock_repository: AsyncMock,
    ) -> None:
        """Test successful resource creation."""
        # Arrange
        create_data = ResourceCreate(name="Test Resource")
        mock_repository.create.return_value = Resource(
            id=uuid4(),
            name=create_data.name,
            created_at=datetime.now(UTC),
        )

        # Act
        result = await service.create(create_data)

        # Assert
        assert result.name == create_data.name
        mock_repository.create.assert_called_once()

    async def test_create_resource_repository_error(
        self,
        service: ResourceService,
        mock_repository: AsyncMock,
    ) -> None:
        """Test that repository errors are propagated correctly."""
        # Arrange
        create_data = ResourceCreate(name="Test Resource")
        mock_repository.create.side_effect = RuntimeError("Database error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Database error"):
            await service.create(create_data)
```

### 8.3 Coverage Enforcement

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Generate HTML report
pytest --cov=src --cov-report=html
```

---

## 9. API Design (FastAPI)

```python
"""API route module following project standards."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.models import User
from app.services import ResourceService

router = APIRouter(prefix="/resources", tags=["resources"])


class ResourceCreate(BaseModel):
    """
    Schema for creating a new resource.

    Attributes:
        name: Display name for the resource (1-100 chars).
        description: Optional detailed description.
    """

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "Example", "description": "A sample"}]
        }
    }


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new resource",
    responses={
        201: {"description": "Resource created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Authentication required"},
    },
)
async def create_resource(
    data: ResourceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ResourceService, Depends()],
) -> ResourceResponse:
    """
    Create a new resource.

    Args:
        data: Resource creation data.
        current_user: Authenticated user from token.
        service: Resource service dependency.

    Returns:
        The created resource.
    """
    result = await service.create(data, owner=current_user)
    return ResourceResponse.model_validate(result)
```
