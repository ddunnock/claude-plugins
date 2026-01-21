# Coding Conventions

**Analysis Date:** 2026-01-20

## Naming Patterns

**Files:**
- Snake_case for all Python files: `openai_embedder.py`, `qdrant_store.py`
- Test files prefixed with `test_`: `test_openai_embedder.py`
- Test directories mirror source: `tests/unit/test_embed/` matches `src/knowledge_mcp/embed/`

**Functions:**
- Snake_case: `add_chunks`, `embed_batch`, `health_check`
- Private methods prefixed with underscore: `_create_knowledge_chunk`, `_convert_filter_to_chromadb`
- Async methods use `async def`: `async def embed(self, text: str)`

**Variables:**
- Snake_case: `query_embedding`, `n_results`, `filter_dict`
- Constants uppercase: `DEFAULT_MODEL`, `MAX_BATCH_SIZE`, `VALID_LOG_LEVELS`
- Private class attributes prefixed: `_client`, `_model`, `_dimensions`

**Classes:**
- PascalCase: `OpenAIEmbedder`, `KnowledgeChunk`, `ConfigurationError`
- Abstract base classes prefixed with `Base`: `BaseStore`, `BaseEmbedder`, `BaseChunker`
- Exception classes suffixed with `Error`: `ConfigurationError`, `ValidationError`

**Types:**
- PascalCase for TypedDict: `ErrorResponse`
- StrEnum values lowercase: `ErrorCode.CONFIG_ERROR = "config_error"`
- Type aliases at module level: `KnowledgeConfig`, `ChunkMetadata`

## Code Style

**Formatting:**
- Tool: Ruff (configured in `pyproject.toml`)
- Line length: 100 characters
- Target Python version: 3.11

**Linting:**
- Tool: Ruff with extensive rule set
- Rules enabled: E, W, F, I, B, C4, UP, ARG, SIM, TCH, PTH, ERA, PL, RUF, D
- Per-file ignores: `tests/**/*.py` ignores PLR2004 (magic values in tests allowed)
- Docstring convention: Google style (`tool.ruff.lint.pydocstyle.convention = "google"`)

**Type Checking:**
- Tool: Pyright in strict mode
- Config location: `pyproject.toml` under `[tool.pyright]`
- Include: `src/`
- Exclude: `**/tests/**`
- All public functions require type hints

## Import Organization

**Order:**
1. `from __future__ import annotations` (always first)
2. Standard library imports
3. Third-party imports
4. Local/first-party imports (knowledge_mcp)

**Path Aliases:**
- First-party known: `knowledge_mcp`
- Configured in: `[tool.ruff.lint.isort]` with `known-first-party = ["knowledge_mcp"]`

**TYPE_CHECKING Pattern:**
```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from knowledge_mcp.models.chunk import KnowledgeChunk
```

## Error Handling

**Exception Hierarchy:**
- All exceptions inherit from `KnowledgeMCPError` at `src/knowledge_mcp/exceptions.py`
- Each exception has: `error_code`, `recoverable`, `default_suggestion`
- Use `to_dict()` method for structured MCP responses

**Patterns:**
```python
# Use specific exceptions, not bare except
try:
    result = await self._call_embedding_api([text])
except APITimeoutError as e:
    raise TimeoutError("OpenAI embedding request timed out") from e
except APIConnectionError as e:
    raise ConnectionError("Failed to connect to OpenAI") from e
except ValidationError:
    raise  # Let validation errors propagate unchanged
except Exception as e:
    # Generic fallback with safe error message
    raise ConnectionError("Embedding generation failed") from e
```

**Error Message Guidelines:**
- Never include API keys or credentials in error messages
- Include actionable suggestions via `default_suggestion`
- Mark recoverable errors (can be retried) vs non-recoverable

**Exception Classes:**
| Exception | Error Code | Recoverable | Use Case |
|-----------|-----------|-------------|----------|
| `ConfigurationError` | `config_error` | No | Missing/invalid config |
| `ConnectionError` | `connection_error` | Yes | Network failures |
| `TimeoutError` | `timeout_error` | Yes | Request timeouts |
| `AuthenticationError` | `auth_error` | No | Invalid credentials |
| `NotFoundError` | `not_found` | No | Missing resources |
| `ValidationError` | `invalid_input` | No | Invalid user input |
| `RateLimitError` | `rate_limited` | Yes | API throttling |
| `InternalError` | `internal_error` | No | Unexpected errors |

## Logging

**Framework:** Python standard `logging` module

**Configuration:**
```python
log_level: str = Field(default="INFO")
log_format: Literal["text", "json"] = Field(default="text")
```

**Patterns:**
- Use module-level logger: `logger = logging.getLogger(__name__)`
- Log at appropriate levels: DEBUG for verbose, INFO for operations, WARNING for fallbacks, ERROR for failures
- Integration tests use `caplog` fixture to verify log messages

## Comments

**When to Comment:**
- Module docstrings explaining purpose and usage example
- Class docstrings with attributes and example
- Public method docstrings with Args, Returns, Raises, Example sections

**Docstring Format (Google style):**
```python
def add_chunks(self, chunks: list[KnowledgeChunk]) -> int:
    """Add chunks to the vector store.

    Args:
        chunks: List of KnowledgeChunk objects to store.
            Each chunk must have an embedding.

    Returns:
        Number of chunks successfully added.

    Raises:
        ValueError: When chunks list is empty.
        ConnectionError: When the vector store is unreachable.

    Example:
        >>> store = QdrantStore(config)
        >>> chunks = [KnowledgeChunk(...)]
        >>> count = store.add_chunks(chunks)
        >>> print(f"Added {count} chunks")
    """
```

**Inline Comments:**
- Use `# noqa: RULE` for intentional rule suppression with reason
- Use `# type: ignore[reason]` for type checker exceptions
- Example: `# noqa: PLC0415` for delayed imports, `# noqa: ARG001` for unused args in callbacks

## Function Design

**Size:** Methods are typically 20-50 lines; extract private methods for complex logic

**Parameters:**
- Use keyword-only for optional parameters: `*, batch_size: int = 100`
- Use dataclasses or Pydantic models for related config: `DoclingChunkerConfig`, `ChunkMetadata`
- Validate at entry point, not deep in call stack

**Return Values:**
- Return empty list `[]` for "no results" (not None)
- Use Pydantic models for structured returns: `IngestResult`, `ChunkingResult`
- Use immutable frozen models where appropriate: `model_config = ConfigDict(frozen=True)`

## Module Design

**Exports:**
- Define `__all__` in package `__init__.py` files
- Export public API explicitly, keep internals private

**Barrel Files:**
- `src/knowledge_mcp/__init__.py` exports main server and all exceptions
- Subpackages export key classes: `from knowledge_mcp.embed import OpenAIEmbedder`

**Abstract Base Classes:**
- All ABC modules at `{package}/base.py`: `store/base.py`, `embed/base.py`, `chunk/base.py`
- Define interface with abstract methods
- Provide default implementations where sensible (e.g., `health_check`)

## Pydantic Models

**Configuration:**
```python
class KnowledgeChunk(BaseModel):
    model_config = ConfigDict(frozen=True)  # Immutable
```

**Field Patterns:**
```python
# Required field with validation
document_id: str = Field(..., min_length=1, description="Source document identifier")

# Optional field with default
embedding: list[float] | None = Field(default=None, description="Vector embedding")

# Field with factory default
section_hierarchy: list[str] = Field(
    default_factory=lambda: list[str](),
    description="Path through document structure",
)
```

**Validators:**
```python
@field_validator("content")
@classmethod
def validate_content_not_empty(cls, v: str) -> str:
    """Validate that content is not empty or whitespace-only."""
    if not v or not v.strip():
        raise ValueError("content must not be empty or whitespace-only")
    return v
```

## Async Patterns

**Async Methods:**
- External API calls are async: `async def embed()`, `async def embed_batch()`
- Use `AsyncOpenAI` client for OpenAI operations
- Mark test methods with `@pytest.mark.asyncio`

**Retry Logic (using tenacity):**
```python
@retry(
    retry=retry_if_exception_type((APIConnectionError, APITimeoutError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
async def _call_embedding_api(self, texts: list[str]) -> list[list[float]]:
    ...
```

## Immutability Patterns

**Use frozen dataclasses and Pydantic models:**
```python
@dataclass(frozen=True)
class ChunkMetadata:
    document_id: str
    document_title: str
    ...

class KnowledgeChunk(BaseModel):
    model_config = ConfigDict(frozen=True)
```

**Copy-on-update pattern for modifications:**
```python
def with_embedding(self, embedding: list[float], model: str) -> KnowledgeChunk:
    """Return a new chunk with embedding populated."""
    return self.model_copy(update={
        "embedding": embedding,
        "embedding_model": model,
    })
```

## Constants and Configuration

**Module-level constants:**
```python
DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_DIMENSIONS = 1536
MAX_BATCH_SIZE = 100
_MAX_HIERARCHY_DEPTH = 6  # Private constants with underscore prefix
```

**Configuration validation:**
- Use Pydantic Field constraints: `ge=`, `le=`, `min_length=`
- Implement `check_config()` method that returns ALL errors (not just first)
- Validate at startup, fail fast with clear messages

---

*Convention analysis: 2026-01-20*
