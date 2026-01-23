# Testing Patterns

**Analysis Date:** 2026-01-23

## Test Framework

**Runner:**
- pytest (Python testing framework)
- Version: 8.3.3+ (from reference pyproject.toml)
- Config: `pytest.ini_options` in `pyproject.toml`

**Assertion Library:**
- Python built-in `assert` statements
- pytest assertions (no external assertion library like `should.py`)

**Run Commands:**
```bash
pytest tests/                          # Run all tests
pytest tests/ -v                       # Verbose output
pytest tests/test_*.py --tb=short      # Specific test pattern with short traceback
pytest -m slow                         # Run marked tests
pytest --cov=src                       # Coverage reporting
```

## Test File Organization

**Location:**
- Tests placed in `tests/` directory at project root (co-located at directory level, not file-level)
- Example structure from reference: `/Users/dunnock/projects/claude-plugins/_references/claude-cookbooks/tests/`

**Naming:**
- Test files: `test_*.py` (e.g., `test_memory_tool.py`, `test_employee_count.py`)
- Test directories: Optional `tests/` subdirectories for organization
- Test functions/methods: `test_*` prefix (e.g., `test_validation_passes()`, `test_error_handling()`)
- Test classes: `Test*` prefix (e.g., `TestValidation`, `TestMemoryServer`)

**Structure from reference project:**
```
tests/
├── conftest.py                     # pytest configuration and fixtures
├── test_memory_tool.py
├── notebook_tests/
│   ├── conftest.py
│   └── test_*.py
└── evaluation/
    └── tests/
        └── test_*.py
```

## Test Structure

**Suite Organization:**
All tests in this codebase use pytest standard patterns:

```python
import pytest

def test_basic_validation():
    """Test basic validation pass case."""
    result = validate_plan("test_plan.md")
    assert result.valid == True
    assert len(result.issues) == 0

def test_missing_section():
    """Test validation fails when required section missing."""
    result = validate_plan("incomplete_plan.md")
    assert result.valid == False
    assert any(i["severity"] == "ERROR" for i in result.issues)

class TestValidation:
    """Group related validation tests."""

    def test_detects_broken_links(self):
        """Test broken internal reference detection."""
        pass

    def test_requirement_mapping(self):
        """Test requirement (REQ-XXX) parsing."""
        pass
```

**Patterns:**
- Setup: Use pytest fixtures in `conftest.py` or inline with `@pytest.fixture`
- Teardown: Context managers for cleanup (e.g., tempfile contexts)
- Assertion: Direct assert statements: `assert condition`, `assert obj == expected`

## Mocking

**Framework:** Not observed in main codebase; reference uses unittest.mock

**Patterns:**
From reference project (`_references/claude-cookbooks`):
```python
from unittest.mock import Mock, patch, MagicMock

@patch('module.external_function')
def test_with_mock(mock_func):
    mock_func.return_value = "mocked value"
    result = my_function()
    assert result == "mocked value"
    mock_func.assert_called_once()
```

**What to Mock:**
- External API calls (Anthropic API, cloud services)
- Database operations in unit tests
- File system operations for unit tests (use tempfile for integration)
- Time-dependent operations (use `freezegun` or mock `datetime`)

**What NOT to Mock:**
- Core business logic of functions under test
- Dictionary/JSON operations
- Data structures and dataclasses
- Standard library functions (Path, etc.)

## Fixtures and Factories

**Test Data:**
Use pytest fixtures for setup:

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_plan():
    """Provide a valid plan for testing."""
    return """
## Overview
[content]

## Architecture Decisions
### AD-001: Use SQLite
[content]
"""

@pytest.fixture
def temp_plan_file(tmp_path, sample_plan):
    """Create temporary plan file."""
    plan_file = tmp_path / "plan.md"
    plan_file.write_text(sample_plan)
    return plan_file

def test_validate_plan(temp_plan_file):
    result = validate_plan(temp_plan_file)
    assert result.valid == True
```

**Location:**
- Global fixtures in `tests/conftest.py`
- File-specific fixtures at top of test file
- Scope indicators: `@pytest.fixture(scope="session")`, `@pytest.fixture(scope="function")`

## Coverage

**Requirements:** Target 80%+ coverage on core modules (see reference pyproject.toml)

**View Coverage:**
```bash
pytest --cov=src --cov-report=html     # HTML coverage report
pytest --cov=src --cov-report=term     # Terminal report
pytest --cov-report=xml                 # XML for CI tools
```

## Test Types

**Unit Tests:**
- Scope: Single function or method
- Example: `test_validate_plan()` tests `validate_plan()` function in isolation
- Approach: Small, focused tests with clear setup/assertion
- Location: `tests/test_*.py` files
- Dependencies mocked or minimal

**Integration Tests:**
- Scope: Multiple components interacting
- Example: `test_session_record_and_query()` tests event recording plus query in one test
- Approach: Use real databases (SQLite test database), real files (temp directory)
- Location: `tests/integration/test_*.py` (if separated)
- Marked with `@pytest.mark.integration` if needed

**E2E Tests:**
- Framework: Not currently in use; could use pytest with markers
- Example: Full workflow from session creation through checkpoint and resume
- Would use `@pytest.mark.e2e` decorator

## Common Patterns

**Async Testing:**
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

**Error Testing:**
```python
import pytest

def test_invalid_plan_raises_error():
    """Test that invalid input raises ValueError."""
    with pytest.raises(ValueError, match="Plan file not found"):
        validate_plan("nonexistent.md")

def test_catches_validation_error():
    """Test validation error handling."""
    result = validate_plan("invalid.md")
    assert result.valid == False
    assert len(result.issues) > 0
```

**Parametrized Tests:**
```python
import pytest

@pytest.mark.parametrize("plan_type,expected", [
    ("simple", "simple"),
    ("master", "master"),
    ("domain", "domain"),
])
def test_plan_type_detection(plan_type, expected):
    """Test different plan type detection."""
    result = detect_plan_type(f"resources/{plan_type}_plan.md")
    assert result == expected
```

**Markers and Skip:**
```python
@pytest.mark.slow
def test_expensive_operation():
    """Mark as slow - skip with -m 'not slow'."""
    pass

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+")
def test_requires_python_311():
    pass
```

## pytest Configuration

From `/Users/dunnock/projects/claude-plugins/_references/claude-cookbooks/pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",                              # Verbose
    "--tb=short",                      # Short tracebacks
]
markers = [
    "slow: marks tests as slow (requires notebook execution)",
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
```

## Current State

**Testing in Main Codebase:**
- No test files found in `skills/`, `mcps/`, or `tools/` directories
- Tests exist in `_references/claude-cookbooks/` (reference material)
- Reference setup uses pytest with ~8.3.3+ version
- Notebooks tested with `nbval` (Jupyter notebook validation)

**Opportunity:**
Implement pytest tests for:
- `validate_plugin.py` - Plugin validation logic
- `validate_plan.py` - Plan file validation
- `detect_stack.py` - Stack detection algorithms
- Session memory server - Core session/checkpoint operations

---

*Testing analysis: 2026-01-23*
