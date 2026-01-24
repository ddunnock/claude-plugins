# Testing Patterns

**Analysis Date:** 2026-01-20

## Test Framework

**Runner:**
- pytest ^8.0
- Config: `pyproject.toml` under `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest (built-in assertions)
- `pytest.approx()` for floating point comparisons

**Async Support:**
- pytest-asyncio ^0.23
- Mode: `asyncio_mode = "auto"` (auto-detects async tests)

**Run Commands:**
```bash
poetry run pytest                                    # Run all tests with coverage
poetry run pytest tests/unit                         # Run unit tests only
poetry run pytest tests/integration                  # Run integration tests only
poetry run pytest -v                                 # Verbose output
poetry run pytest -x                                 # Stop on first failure
poetry run pytest --cov-report=html                  # Generate HTML coverage report
poetry run pytest tests/unit/test_embed             # Run specific test directory
```

## Test File Organization

**Location:**
- Separate `tests/` directory, mirroring `src/knowledge_mcp/` structure
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Shared fixtures: `tests/conftest.py`

**Naming:**
- Test files: `test_{module_name}.py`
- Test classes: `Test{ClassName}` or `Test{ClassName}{Method}`
- Test methods: `test_{description_of_behavior}`

**Structure:**
```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_chunk/
│   │   ├── __init__.py
│   │   └── test_docling_chunker.py
│   ├── test_embed/
│   │   ├── __init__.py
│   │   └── test_openai_embedder.py
│   ├── test_ingest/
│   │   ├── __init__.py
│   │   └── test_base.py
│   ├── test_models/
│   │   ├── __init__.py
│   │   ├── test_chunk.py
│   │   └── test_enums.py
│   └── test_store/
│       ├── __init__.py
│       └── test_chromadb_store.py
└── integration/
    ├── __init__.py
    └── test_store_fallback.py
```

## Test Structure

**Suite Organization:**
```python
"""Unit tests for OpenAIEmbedder.

Tests cover:
- Single text embedding
- Batch embedding (within limit)
- Batch embedding (exceeds limit, splits)
- Retry on transient error
- Failure after max retries
- Dimension validation

Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestOpenAIEmbedderInit:
    """Tests for OpenAIEmbedder initialization."""

    def test_init_with_valid_api_key(self) -> None:
        """Test successful initialization with valid API key."""
        # Arrange & Act
        embedder = OpenAIEmbedder(api_key="sk-test-key")

        # Assert
        assert embedder.dimensions == 1536
        assert embedder.model_name == "text-embedding-3-small"


class TestOpenAIEmbedderEmbed:
    """Tests for single text embedding."""

    @pytest.fixture
    def mock_embedder(self) -> OpenAIEmbedder:
        """Create an embedder with mocked OpenAI client."""
        with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
            return OpenAIEmbedder(api_key="sk-test-key")

    @pytest.mark.asyncio
    async def test_embed_single_text_success(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test successful embedding of a single text."""
        # Arrange
        expected_embedding = [0.1] * 1536
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=expected_embedding)]
        mock_embedder._client.embeddings.create = AsyncMock(
            return_value=mock_response
        )

        # Act
        result = await mock_embedder.embed("What is systems engineering?")

        # Assert
        assert result == expected_embedding
        assert len(result) == 1536
```

**Patterns:**
- Group related tests in classes: `TestOpenAIEmbedderInit`, `TestOpenAIEmbedderEmbed`
- Use class docstrings to describe test scope
- Use method docstrings for single-line test description
- Always include return type hint `-> None` on test methods

## Mocking

**Framework:** `unittest.mock` (built-in)

**Patterns:**
```python
from unittest.mock import AsyncMock, MagicMock, patch

# Patching a module-level import
@patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI")
def test_something(self, mock_async_openai: MagicMock) -> None:
    ...

# Patching with context manager (for fixtures)
@pytest.fixture
def mock_embedder(self) -> OpenAIEmbedder:
    with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
        return OpenAIEmbedder(api_key="sk-test-key")

# AsyncMock for async methods
mock_embedder._client.embeddings.create = AsyncMock(return_value=mock_response)

# MagicMock for complex return structures
mock_response = MagicMock()
mock_response.data = [MagicMock(embedding=[0.1] * 1536)]

# Side effect for sequential calls
async def mock_create(*args, **kwargs):  # noqa: ARG001
    nonlocal call_count
    call_count += 1
    if call_count == 1:
        raise APIConnectionError(request=MagicMock())
    response = MagicMock()
    response.data = [MagicMock(embedding=expected_embedding)]
    return response
mock_embedder._client.embeddings.create = mock_create

# Side effect for exception
mock_collection.count.side_effect = Exception("Connection error")
```

**What to Mock:**
- External API clients: OpenAI, Qdrant, ChromaDB clients
- File system operations (use `tmp_path` fixture instead)
- Network calls
- Time-sensitive operations

**What NOT to Mock:**
- Internal business logic
- Pydantic model validation
- Exception handling flow
- Data transformations

## Fixtures and Factories

**Shared Fixtures (`tests/conftest.py`):**
```python
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
        document_type="standard",
        content="The System Requirements Review (SRR) shall verify...",
        token_count=150,
        embedding=[0.1] * 1536,
    )

@pytest.fixture
def mock_qdrant_client() -> MagicMock:
    """Create a mock Qdrant client."""
    client = MagicMock()
    client.get_collections.return_value.collections = []
    return client
```

**Local Fixtures (in test module):**
```python
@pytest.fixture
def valid_metadata(self) -> IngestMetadata:
    """Create valid metadata for tests."""
    return IngestMetadata(
        document_id="test-doc",
        document_title="Test Document",
        document_type="standard",
        source_path="/docs/test.pdf",
    )
```

**Using pytest built-in fixtures:**
```python
def test_init_creates_directory(self, tmp_path: Path) -> None:
    """Test that init creates storage directory."""
    path = tmp_path / "new_chromadb"
    assert not path.exists()
    # ... test implementation
    assert path.exists()

def test_load_config_custom_values(
    self, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test load_config reads custom values from env vars."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    # ...
```

## Coverage

**Requirements:**
- Minimum: 80% (blocking, configured in pytest.ini_options)
- Target: 90%
- Coverage source: `src/` directory

**Configuration (`pyproject.toml`):**
```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["**/tests/**", "**/__pycache__/**"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
```

**View Coverage:**
```bash
poetry run pytest --cov-report=term-missing      # Terminal with missing lines
poetry run pytest --cov-report=html              # HTML report in htmlcov/
poetry run pytest --cov-report=xml               # XML for CI tools
```

## Test Types

**Unit Tests (`tests/unit/`):**
- Test individual classes/functions in isolation
- Mock all external dependencies
- Fast execution (milliseconds per test)
- High coverage of edge cases

**Integration Tests (`tests/integration/`):**
- Test component interactions (e.g., store fallback logic)
- May use real local services (ChromaDB with tmp_path)
- Mock only external cloud services (Qdrant Cloud)
- Test error handling and logging

## Common Patterns

**Async Testing:**
```python
@pytest.mark.asyncio
async def test_embed_single_text_success(
    self, mock_embedder: OpenAIEmbedder
) -> None:
    """Test successful embedding of a single text."""
    # ... async test body
    result = await mock_embedder.embed("test")
    assert result == expected
```

**Exception Testing:**
```python
def test_empty_content_raises_error(
    self, valid_metadata: IngestMetadata
) -> None:
    """Test that empty content raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        IngestResult(content="", metadata=valid_metadata)

    assert "content" in str(exc_info.value)

# Testing specific error messages
with pytest.raises(ValueError, match="at least 1 character"):
    IngestMetadata(document_id="", ...)

# Testing exception attributes
with pytest.raises(ConnectionError) as exc_info:
    create_store(qdrant_config)
error_msg = str(exc_info.value)
assert "qdrant" in error_msg.lower()
assert "Connection timeout" in error_msg
```

**Parametrized Testing:**
```python
@pytest.mark.parametrize(
    "log_level",
    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
)
def test_valid_log_levels_uppercase(self, log_level: str) -> None:
    """Test all valid log levels are accepted (uppercase)."""
    config = KnowledgeConfig(
        openai_api_key="sk-test",
        log_level=log_level,
    )
    assert config.log_level == log_level

@pytest.mark.parametrize(
    ("log_level", "expected"),
    [
        ("debug", "DEBUG"),
        ("info", "INFO"),
        ("Debug", "DEBUG"),
        ("InFo", "INFO"),
    ],
)
def test_valid_log_levels_case_insensitive(
    self, log_level: str, expected: str
) -> None:
    """Test log levels are normalized to uppercase."""
    config = KnowledgeConfig(openai_api_key="sk-test", log_level=log_level)
    assert config.log_level == expected

@pytest.mark.parametrize(
    ("exc_class", "expected_recoverable"),
    [
        (ConfigurationError, False),
        (ConnectionError, True),
        (TimeoutError, True),
        (AuthenticationError, False),
    ],
)
def test_recoverability_matches_spec(
    self,
    exc_class: type[KnowledgeMCPError],
    expected_recoverable: bool,
) -> None:
    """Test that each exception has correct recoverability."""
    error = exc_class("Test message")
    assert error.recoverable is expected_recoverable
```

**Log Capture Testing:**
```python
def test_logs_warning_on_fallback(
    self,
    qdrant_config: KnowledgeConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that fallback to ChromaDB logs a WARNING."""
    with caplog.at_level(logging.WARNING, logger="knowledge_mcp.store"):
        create_store(qdrant_config)

    assert "Qdrant unavailable" in caplog.text
    assert "falling back to ChromaDB" in caplog.text
```

**Serialization Round-trip Testing:**
```python
def test_serialization_round_trip(
    self, valid_metadata: IngestMetadata
) -> None:
    """Test that result can be serialized and deserialized."""
    result = IngestResult(
        content="Test content",
        metadata=valid_metadata,
        page_numbers=[1, 2, 3],
    )

    # Round-trip: model -> dict -> model
    data = result.model_dump()
    restored = IngestResult.model_validate(data)

    assert restored == result
    assert restored.content == result.content

def test_json_round_trip(self) -> None:
    """Test that model survives JSON round-trip."""
    original = KnowledgeChunk(...)

    json_str = original.model_dump_json()
    restored = KnowledgeChunk.model_validate_json(json_str)

    assert restored.document_id == original.document_id
```

**Immutability Testing:**
```python
def test_model_is_frozen(self) -> None:
    """Test that model attributes cannot be modified."""
    chunk = KnowledgeChunk(...)

    with pytest.raises(ValidationError):
        chunk.content = "New content"  # type: ignore[misc]

def test_with_computed_hash_returns_new_instance(self) -> None:
    """Test that with_computed_hash returns new instance."""
    chunk = KnowledgeChunk(...)

    hashed = chunk.with_computed_hash()

    assert hashed is not chunk  # Different instance
    assert hashed.content_hash != ""
    assert chunk.content_hash == ""  # Original unchanged
```

**Call Count Verification:**
```python
async def test_embed_batch_exceeds_limit_splits(
    self, mock_embedder: OpenAIEmbedder
) -> None:
    """Test that batch exceeding limit is split into multiple calls."""
    texts = [f"text {i}" for i in range(150)]  # Exceeds 100 limit
    call_count = 0

    async def mock_create(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # ... return appropriate response

    mock_embedder._client.embeddings.create = mock_create

    result = await mock_embedder.embed_batch(texts)

    assert len(result) == 150
    assert call_count == 2  # Should split into 2 API calls
```

## Test Naming Guidelines

Follow pattern: `test_{what}_{condition}_{expected_outcome}`

Examples:
- `test_init_with_valid_api_key` - Happy path
- `test_init_with_empty_api_key_raises_validation_error` - Error case
- `test_embed_empty_text_raises_validation_error` - Input validation
- `test_retry_on_connection_error_then_success` - Retry behavior
- `test_failure_after_max_retries_connection_error` - Failure after retries
- `test_health_check_returns_false_on_error` - Failure case

---

*Testing analysis: 2026-01-20*
