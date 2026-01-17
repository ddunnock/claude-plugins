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

## 1.1 Design Philosophy (PEP 20)

Python code **MUST** embody [The Zen of Python (PEP 20)](https://peps.python.org/pep-0020/) as actionable rules:

| Principle | Rule Level | Actionable Directive |
|-----------|------------|---------------------|
| Readability counts | **MUST** | Prefer clear variable names over terse abbreviations; prioritize understandability over cleverness |
| Explicit is better than implicit | **MUST** | Avoid magic methods, hidden state, or implicit type coercion; make behavior obvious |
| Simple is better than complex | **MUST** | Resist premature optimization; solve the immediate problem without speculative generalization |
| Flat is better than nested | **SHOULD** | Limit nesting to 3 levels; extract nested logic into named functions |
| Sparse is better than dense | **SHOULD** | One statement per line; avoid compound one-liners that sacrifice clarity |
| Errors should never pass silently | **MUST** | Never use bare `except:`; catch specific exceptions and handle or re-raise |
| In the face of ambiguity, refuse to guess | **MUST** | Require explicit configuration over convention-based defaults |
| There should be one obvious way | **SHOULD** | Follow established patterns from this memory file rather than inventing alternatives |
| Practicality beats purity | **SHOULD** | Trade-off purity for pragmatism when justified with inline comments |

### Anti-Patterns (MUST NOT)

```python
# ❌ MUST NOT: Clever one-liner that sacrifices readability
result = [x for x in (y for y in data if y > 0) if x < 100 and x % 2 == 0]

# ✓ MUST: Readable multi-step filtering
positives = (y for y in data if y > 0)
result = [x for x in positives if x < 100 and x % 2 == 0]

# ❌ MUST NOT: Implicit behavior via __getattr__ magic
class Config:
    def __getattr__(self, name): return os.environ.get(name)

# ✓ MUST: Explicit configuration
class Config:
    def __init__(self, api_key: str, timeout: int):
        self.api_key = api_key
        self.timeout = timeout

# ❌ MUST NOT: Bare except that silences errors
try:
    process_data()
except:
    pass

# ✓ MUST: Specific exception handling
try:
    process_data()
except ValidationError as e:
    logger.warning(f"Invalid data: {e}")
    raise
except IOError as e:
    logger.error(f"IO failure: {e}")
    raise ProcessingError(f"Failed to process: {e}") from e
```

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

---

## 10. Security Practices (OWASP)

Python code **MUST** follow security best practices from [OWASP](https://owasp.org/www-project-python-security/) and [Bandit](https://bandit.readthedocs.io/).

### 10.1 Prohibited Functions (MUST NOT)

| Function | Risk | Alternative |
|----------|------|-------------|
| `eval()` / `exec()` | Code injection | Use `ast.literal_eval()` for safe parsing, or structured data formats |
| `pickle.load()` from untrusted sources | Arbitrary code execution | Use JSON or MessagePack for serialization |
| `shell=True` in subprocess | Command injection | Use `subprocess.run([cmd, arg1], shell=False)` |
| `os.system()` | Command injection | Use `subprocess.run()` with argument list |
| `__import__()` with user input | Code injection | Use allowlist of permitted modules |
| `yaml.load()` without Loader | Code execution | Use `yaml.safe_load()` |
| `requests.get(verify=False)` | MitM attacks | Always verify SSL certificates |

### 10.2 Secret Management (MUST)

```python
# ❌ MUST NOT: Hardcoded secrets
API_KEY = "sk-abc123secret"
DATABASE_URL = "postgresql://user:password@localhost/db"

# ✓ MUST: Environment variables or secrets manager
import os
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    """Load settings from environment with validation."""
    return Settings(
        api_key=os.environ["API_KEY"],  # Fails fast if missing
        database_url=os.environ["DATABASE_URL"],
    )

# ✓ For local development, use .env with python-dotenv
# .env files MUST be in .gitignore
```

### 10.3 Input Validation (MUST)

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserInput(BaseModel):
    """Validated user input with security constraints."""

    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    @field_validator('username')
    @classmethod
    def no_sql_injection(cls, v: str) -> str:
        """Reject common SQL injection patterns."""
        dangerous = ["'", '"', ';', '--', '/*', '*/']
        if any(char in v for char in dangerous):
            raise ValueError('Invalid characters in username')
        return v
```

### 10.4 Path Traversal Prevention (MUST)

```python
from pathlib import Path

def safe_read_file(base_dir: Path, user_filename: str) -> str:
    """Read file safely, preventing directory traversal.

    Args:
        base_dir: Allowed directory (must be absolute)
        user_filename: User-provided filename

    Returns:
        File contents

    Raises:
        ValueError: If path would escape base_dir
    """
    # Resolve to absolute path
    target = (base_dir / user_filename).resolve()

    # MUST verify path is within base_dir
    if not target.is_relative_to(base_dir.resolve()):
        raise ValueError(f"Path traversal attempt: {user_filename}")

    return target.read_text()
```

---

## 11. Architecture Principles

### 11.1 Single Responsibility Principle (MUST)

Each module, class, and function **MUST** have a single, well-defined responsibility:

```python
# ❌ MUST NOT: God module doing everything
# file: service.py (500+ lines)
class UserService:
    def create_user(self): ...
    def send_email(self): ...          # Email is separate concern
    def generate_pdf_report(self): ... # Reporting is separate concern
    def sync_to_crm(self): ...         # Integration is separate concern

# ✓ MUST: Focused modules with single responsibility
# file: services/user.py
class UserService:
    def __init__(self, repository: UserRepository, event_bus: EventBus):
        self._repository = repository
        self._event_bus = event_bus

    def create_user(self, data: UserCreate) -> User:
        user = self._repository.create(data)
        self._event_bus.publish(UserCreated(user_id=user.id))
        return user

# file: services/email.py
class EmailService:
    def send_welcome_email(self, user: User) -> None: ...

# file: handlers/user_events.py
class UserEventHandlers:
    def on_user_created(self, event: UserCreated) -> None:
        self._email_service.send_welcome_email(event.user_id)
```

### 11.2 Anti-Patterns (MUST NOT)

| Anti-Pattern | Symptom | Remedy |
|--------------|---------|--------|
| **God Module** | File >500 lines, >10 public functions | Split by responsibility |
| **Circular Imports** | `ImportError` at runtime | Extract shared types to separate module |
| **Deep Nesting** | >3 levels of indentation | Extract to named functions |
| **Magic Numbers** | Unexplained literals in code | Define named constants with docstrings |
| **Catch-All Exception** | `except Exception:` | Catch specific exceptions |
| **Mutable Default Args** | `def f(items=[]):` | Use `def f(items=None):` |

### 11.3 Module Size Guidelines

| Metric | SHOULD | MUST NOT Exceed |
|--------|--------|-----------------|
| Lines per module | ≤300 | 500 |
| Public functions per module | ≤7 | 15 |
| Parameters per function | ≤5 | 8 |
| Cyclomatic complexity | ≤10 | 15 |

### 11.4 Dependency Direction (MUST)

```
Domain Models ← Services ← API/CLI ← Infrastructure
     ↑             ↑           ↑
   (pure)      (business)  (I/O boundary)
```

- **Domain models** MUST NOT import from services or infrastructure
- **Services** MUST NOT import from API handlers
- **Use dependency injection** for infrastructure dependencies (database, external APIs)

---

## 12. Agent Enforcement Rules

This section defines rule levels for automated agents (Claude Code, linters, CI checks).

### 12.1 Rule Levels

| Level | Meaning | Agent Behavior |
|-------|---------|----------------|
| **MUST** | Mandatory requirement | Agent MUST comply; failure blocks completion |
| **MUST NOT** | Prohibited action | Agent MUST NOT perform; violation is error |
| **SHOULD** | Recommended practice | Agent SHOULD comply; deviation requires comment |
| **MAY** | Optional guidance | Agent MAY choose based on context |

### 12.2 Pre-Completion Checklist (MUST)

Before marking any Python task as complete, agents **MUST** verify:

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| Type checking | `pyright --outputjson` | Zero errors |
| Linting | `ruff check .` | Zero errors |
| Formatting | `ruff format --check .` | No changes needed |
| Tests pass | `pytest` | All tests pass |
| Coverage | `pytest --cov --cov-fail-under=80` | ≥80% coverage |

### 12.3 Code Quality Rules

| Rule | Level | Verification |
|------|-------|--------------|
| Type hints on public functions | **MUST** | Pyright strict mode |
| Google-style docstrings on public API | **MUST** | Ruff D rules |
| No unused imports | **MUST** | Ruff F401 |
| No hardcoded secrets | **MUST** | Manual review + Bandit |
| Tests for new functionality | **MUST** | Coverage delta |
| Single responsibility per function | **SHOULD** | Function ≤50 lines |
| Flat module structure | **SHOULD** | Nesting ≤3 levels |

### 12.4 Deviation Handling (MUST)

When deviating from a **SHOULD** rule, agents **MUST**:

1. Add inline comment explaining the deviation
2. Reference the rule being deviated from
3. Justify why deviation is appropriate

```python
# Deviation from §11.3: Function exceeds 50 lines because
# splitting would break the transaction boundary. The atomic
# operation requires all steps in sequence.
def complex_but_atomic_operation(data: Input) -> Output:
    ...
```

### 12.5 Authoritative Sources

All Python code **MUST** align with these authoritative references:

| Source | URL | Scope |
|--------|-----|-------|
| PEP 8 | https://peps.python.org/pep-0008/ | Style guide |
| PEP 20 | https://peps.python.org/pep-0020/ | Design philosophy |
| PEP 257 | https://peps.python.org/pep-0257/ | Docstring conventions |
| PEP 484 | https://peps.python.org/pep-0484/ | Type hints |
| Google Style Guide | https://google.github.io/styleguide/pyguide.html | Docstrings, naming |
| OWASP Python Security | https://owasp.org/www-project-python-security/ | Security practices |

---

## 13. Anti-Patterns to Avoid

These patterns indicate inexperience and **MUST NOT** appear in code:

### 13.1 Mutable Default Arguments

```python
# ❌ MUST NOT: Mutable default is shared across calls
def append_to_list(item, target=[]):
    target.append(item)
    return target

# ✅ MUST: Use None sentinel
def append_to_list(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

### 13.2 Bare Except Clauses

```python
# ❌ MUST NOT: Catches SystemExit, KeyboardInterrupt
try:
    process_data()
except:
    pass

# ✅ MUST: Catch specific exceptions
try:
    process_data()
except (ValueError, TypeError) as e:
    logger.warning(f"Invalid data: {e}")
    raise
```

### 13.3 Using `type()` for Type Checking

```python
# ❌ SHOULD NOT: Doesn't handle inheritance
if type(obj) == dict:
    process_dict(obj)

# ✅ SHOULD: Use isinstance for type checks
if isinstance(obj, dict):
    process_dict(obj)
```

### 13.4 String Concatenation in Loops

```python
# ❌ SHOULD NOT: O(n²) complexity
result = ""
for item in items:
    result += str(item)

# ✅ SHOULD: Use join for O(n) complexity
result = "".join(str(item) for item in items)
```

### 13.5 Not Using Context Managers

```python
# ❌ MUST NOT: Resource leak on exception
f = open("file.txt")
data = f.read()
f.close()

# ✅ MUST: Context manager ensures cleanup
with open("file.txt") as f:
    data = f.read()
```

### 13.6 Wildcard Imports

```python
# ❌ MUST NOT: Pollutes namespace, hides dependencies
from module import *

# ✅ MUST: Explicit imports
from module import specific_function, SpecificClass
```

### 13.7 Global State Mutation

```python
# ❌ MUST NOT: Hidden side effects
_cache = {}
def get_data(key):
    if key not in _cache:
        _cache[key] = fetch(key)  # Mutates global
    return _cache[key]

# ✅ MUST: Explicit dependency injection
def get_data(key, cache: dict | None = None):
    if cache is None:
        return fetch(key)
    if key not in cache:
        cache[key] = fetch(key)
    return cache[key]
```

### 13.8 Dynamic Code Evaluation

**MUST NOT** use `eval()` or similar dynamic execution on untrusted input. Use `ast.literal_eval()` for safe literal parsing.

### 13.9 Ignoring Return Values

```python
# ❌ SHOULD NOT: Silently ignores errors
list.sort()  # Returns None, sorts in place
sorted_list = list.sort()  # Bug: sorted_list is None

# ✅ SHOULD: Understand mutating vs returning methods
list.sort()  # Mutates in place
sorted_list = sorted(list)  # Returns new sorted list
```

### 13.10 Deep Nesting

```python
# ❌ SHOULD NOT: Hard to follow logic
def process(data):
    if data:
        if data.valid:
            if data.items:
                for item in data.items:
                    if item.active:
                        handle(item)

# ✅ SHOULD: Early returns and extraction
def process(data):
    if not data or not data.valid or not data.items:
        return
    active_items = (item for item in data.items if item.active)
    for item in active_items:
        handle(item)
```

> **Reference**: See `python-antipatterns.md` for detailed explanations and detection patterns.
