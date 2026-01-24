# Phase 5: Production Integration - Research

**Researched:** 2026-01-24
**Domain:** Python dependency injection and integration testing
**Confidence:** HIGH

## Summary

Phase 5 wires the existing EmbeddingCache (Phase 4.2) and TokenTracker (Phase 4.3) classes into the OpenAIEmbedder embedding pipeline. This research identifies the integration approach using constructor-based dependency injection, the configuration extension pattern, and the testing strategy to verify cache hits, token tracking, and backwards compatibility.

**Current State:**
- `EmbeddingCache` exists in `src/knowledge_mcp/embed/cache.py` with 100% test coverage
- `TokenTracker` exists in `src/knowledge_mcp/monitoring/token_tracker.py` with 97% test coverage
- `OpenAIEmbedder` exists in `src/knowledge_mcp/embed/openai_embedder.py` with comprehensive tests
- Dependencies already in place: `diskcache==5.6.3`, `tiktoken==0.12.0`

**Gap to Close:**
- OpenAIEmbedder needs cache/tracker instances passed via constructor
- Configuration needs `cache_dir` and `token_log_file` fields with sensible defaults
- OpenAIEmbedder.embed() must check cache before API call, set cache after
- OpenAIEmbedder must call tracker.track_embedding() on each request
- Both unit tests (mocked cache/tracker) and integration tests (real instances) required

**Primary recommendation:** Use optional constructor parameters with None defaults for backwards compatibility. Add configuration fields with Path defaults. Verify integration with both unit tests (mocked dependencies) and integration tests (real filesystem).

## Standard Stack

The established libraries/tools for dependency injection and testing in Python:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Constructor Injection | Native | Dependency passing | Pythonic, explicit, testable - recommended over frameworks for simple cases |
| unittest.mock | Python 3.11+ | Test mocking | Standard library, widely understood, pytest-compatible |
| pytest-asyncio | 0.23+ | Async testing | Standard for async/await test support |
| pathlib.Path | Native | Path handling | Type-safe, cross-platform, Pydantic-compatible |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | 2.x | Config validation | Already used in KnowledgeConfig - extend existing pattern |
| tempfile | Native | Test isolation | Unit tests with cache/tracker need isolated directories |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Constructor injection | dependency-injector framework | Framework adds complexity; manual injection sufficient for 2-3 dependencies |
| Optional parameters | Required parameters | Breaks backwards compatibility for existing OpenAIEmbedder users |
| Path type | str type | Path is type-safe and Pydantic supports it natively |

**Installation:**
No new dependencies required - all tools are either native Python or already in `pyproject.toml`.

## Architecture Patterns

### Recommended Integration Structure
```
src/knowledge_mcp/
├── embed/
│   ├── openai_embedder.py    # Modified: accept cache, tracker in __init__
│   ├── cache.py               # Existing: EmbeddingCache (unchanged)
│   └── base.py                # Existing: BaseEmbedder (unchanged)
├── monitoring/
│   └── token_tracker.py       # Existing: TokenTracker (unchanged)
├── utils/
│   └── config.py              # Modified: add cache_dir, token_log_file fields
└── server.py                  # Modified: pass cache/tracker to embedder
```

### Pattern 1: Optional Constructor Injection
**What:** Pass dependencies as optional constructor parameters with None defaults
**When to use:** Extending existing classes without breaking backwards compatibility
**Example:**
```python
# Source: Knowledge MCP codebase analysis + Python best practices
class OpenAIEmbedder(BaseEmbedder):
    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_MODEL,
        dimensions: int = DEFAULT_DIMENSIONS,
        cache: EmbeddingCache | None = None,        # New: optional
        token_tracker: TokenTracker | None = None,  # New: optional
    ) -> None:
        """Initialize with optional cache and token tracker."""
        if not api_key:
            raise ValidationError("OpenAI API key is required")

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._dimensions = dimensions
        self._cache = cache              # None = no caching
        self._token_tracker = token_tracker  # None = no tracking
```

**Why this works:**
- Existing code continues to work (backwards compatible)
- Test code can inject mocks easily
- Production code can pass real instances
- No breaking changes to public API

### Pattern 2: Cache-Aware Embedding Flow
**What:** Check cache before API call, update cache after response
**When to use:** Wrapping expensive API calls with caching layer
**Example:**
```python
# Source: Diskcache best practices + knowledge_mcp.embed.cache analysis
async def embed(self, text: str) -> list[float]:
    """Generate embedding with optional caching."""
    if not text or not text.strip():
        raise ValidationError("Text cannot be empty")

    # Check cache first (if configured)
    if self._cache is not None:
        cached = self._cache.get(text)
        if cached is not None:
            # Track cache hit (if tracker configured)
            if self._token_tracker is not None:
                self._token_tracker.track_embedding(text, cache_hit=True)
            return cached

    # Cache miss - call OpenAI API
    try:
        result = await self._call_embedding_api([text])
        embedding = result[0]

        # Validate dimensions
        if len(embedding) != self._dimensions:
            raise ValidationError(
                f"Embedding dimension mismatch: expected {self._dimensions}, "
                f"got {len(embedding)}"
            )

        # Store in cache (if configured)
        if self._cache is not None:
            self._cache.set(text, embedding)

        # Track API usage (if tracker configured)
        if self._token_tracker is not None:
            self._token_tracker.track_embedding(text, cache_hit=False)

        return embedding

    except APITimeoutError as e:
        raise TimeoutError("OpenAI embedding request timed out") from e
    # ... (existing error handlers)
```

**Critical details:**
- Cache check BEFORE API call (cost savings)
- Cache set AFTER successful response (consistency)
- Token tracking distinguishes cache_hit=True/False
- Graceful degradation when cache/tracker are None

### Pattern 3: Configuration Extension
**What:** Add new fields to existing Pydantic config with sensible defaults
**When to use:** Extending application configuration without breaking existing deployments
**Example:**
```python
# Source: knowledge_mcp.utils.config analysis + Pydantic patterns
class KnowledgeConfig(BaseModel):
    # ... existing fields ...

    # Embedding Cache Configuration (Phase 4.2)
    cache_dir: Path = Field(
        default=Path("./data/embeddings/cache"),
        description="Directory for embedding cache storage",
    )
    cache_enabled: bool = Field(
        default=True,
        description="Enable embedding cache",
    )
    cache_size_limit: int = Field(
        default=10 * 1024 * 1024 * 1024,  # 10GB
        ge=100 * 1024 * 1024,  # Min 100MB
        description="Cache size limit in bytes",
    )

    # Token Tracking Configuration (Phase 4.3)
    token_log_file: Path = Field(
        default=Path("./data/token_usage.json"),
        description="Token usage log file path",
    )
    token_tracking_enabled: bool = Field(
        default=True,
        description="Enable token usage tracking",
    )
    daily_token_warning_threshold: int = Field(
        default=1_000_000,
        ge=0,
        description="Daily token warning threshold",
    )
```

**Why these defaults:**
- `./data/` prefix matches existing `chromadb_path` pattern
- 10GB cache matches Phase 4.2 decision
- 1M token threshold matches Phase 4.3 decision
- Enabled by default (production use case)
- Can be disabled via environment variables

### Pattern 4: Integration Test Structure
**What:** Test with real filesystem dependencies, isolated per test
**When to use:** Verifying cache/tracker work correctly with real I/O
**Example:**
```python
# Source: tests/integration/test_fallback.py analysis + pytest best practices
class TestOpenAIEmbedderIntegration:
    """Integration tests with real cache and token tracker."""

    @pytest.fixture
    def temp_dirs(self, tmp_path: Path) -> dict[str, Path]:
        """Create isolated temporary directories."""
        return {
            "cache": tmp_path / "cache",
            "logs": tmp_path / "logs",
        }

    @pytest.fixture
    def embedder_with_cache(
        self, temp_dirs: dict[str, Path]
    ) -> OpenAIEmbedder:
        """Create embedder with real cache and tracker."""
        cache = EmbeddingCache(
            temp_dirs["cache"],
            "text-embedding-3-small",
        )
        tracker = TokenTracker(
            temp_dirs["logs"] / "tokens.json",
            "text-embedding-3-small",
        )
        return OpenAIEmbedder(
            api_key="sk-test-key",
            cache=cache,
            token_tracker=tracker,
        )

    @pytest.mark.asyncio
    async def test_cache_hit_reduces_api_calls(
        self, embedder_with_cache: OpenAIEmbedder
    ) -> None:
        """Verify cache prevents duplicate API calls."""
        # First call - cache miss, API call
        embedding1 = await embedder_with_cache.embed("test text")

        # Second call - cache hit, no API call
        embedding2 = await embedder_with_cache.embed("test text")

        # Same result
        assert embedding1 == embedding2

        # Verify only one API call made (via mock tracking)
```

### Anti-Patterns to Avoid
- **Global singleton cache:** Makes testing impossible, couples components
- **Modifying BaseEmbedder interface:** Forces all embedders to support caching (violates YAGNI)
- **Required cache/tracker parameters:** Breaks backwards compatibility
- **String paths instead of Path objects:** Loses type safety, platform compatibility

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cache key generation | Custom hash function | EmbeddingCache._hash_content() | Already implements SHA-256 + normalization (Phase 4.2) |
| Token counting | Regex/split | tiktoken.encoding_for_model() | Matches OpenAI billing exactly, handles edge cases |
| Cache eviction | Manual size checking | diskcache.Cache(size_limit=...) | Built-in LRU eviction, process-safe |
| Test isolation | Manual cleanup | pytest tmp_path fixture | Automatic cleanup, pytest standard |
| Dependency injection framework | dependency-injector | Constructor parameters | Overkill for 2-3 dependencies, adds complexity |

**Key insight:** The infrastructure (cache, tracker) already exists with 97-100% test coverage. Integration is straightforward dependency wiring, not new implementations.

## Common Pitfalls

### Pitfall 1: Breaking Backwards Compatibility
**What goes wrong:** Adding required parameters to OpenAIEmbedder.__init__() breaks existing code that creates embedders without cache/tracker
**Why it happens:** Desire for "clean" API without optional parameters
**How to avoid:**
- Use `cache: EmbeddingCache | None = None` pattern
- Default to None (no caching/tracking)
- Update server.py to pass instances, but leave direct OpenAIEmbedder usage unchanged
**Warning signs:**
- Existing tests fail after integration
- Server initialization requires cache/tracker before they're configured

### Pitfall 2: Cache/Tracker Lifecycle Mismanagement
**What goes wrong:** Cache not closed properly, leaving SQLite locks; log file corruption from concurrent writes
**Why it happens:** No explicit cleanup in async code
**How to avoid:**
- EmbeddingCache.close() already exists - call in cleanup
- TokenTracker saves on each track_embedding() - no cleanup needed
- For server: cache/tracker live for server lifetime (OK to not close)
- For tests: tmp_path auto-cleanup handles it
**Warning signs:**
- "database is locked" errors in tests
- JSON corruption in token log

### Pitfall 3: Testing Only with Mocks
**What goes wrong:** Unit tests pass but real cache/tracker integration fails with I/O errors
**Why it happens:** Mocks don't verify filesystem behavior
**How to avoid:**
- Require BOTH unit tests (mocked) AND integration tests (real filesystem)
- Integration tests verify cache persistence across instances
- Integration tests verify token log JSON format
**Warning signs:**
- Tests pass but manual testing fails
- Coverage high but bugs in production

### Pitfall 4: Not Verifying Cache Hit Metrics
**What goes wrong:** Cache wired but never actually hits, costing full API usage
**Why it happens:** Text normalization differences, cache key bugs
**How to avoid:**
- Integration test must verify second call with same text returns cached value
- Integration test must verify tracker shows cache_hits > 0
- CLI token_summary command shows cache efficiency
**Warning signs:**
- tracker.get_daily_summary()["cache_hits"] always 0
- No cost reduction despite caching enabled

### Pitfall 5: Configuration Field Type Mismatches
**What goes wrong:** Pydantic validation fails when loading config from environment
**Why it happens:** Path vs str confusion, bool parsing errors
**How to avoid:**
- Use `Path = Field(default=Path("..."))` not `str`
- Pydantic handles environment variable conversion automatically
- load_config() uses `Path(os.getenv(...))` for path fields
**Warning signs:**
- ValidationError on config load
- Path concatenation fails (str + Path)

## Code Examples

Verified patterns from official sources:

### Embedding with Cache Check
```python
# Source: knowledge_mcp.embed.openai_embedder + cache.py analysis
async def embed(self, text: str) -> list[float]:
    """Generate embedding with cache support."""
    if not text or not text.strip():
        raise ValidationError("Text cannot be empty")

    # 1. Check cache (if enabled)
    if self._cache is not None:
        cached_embedding = self._cache.get(text)
        if cached_embedding is not None:
            # Track cache hit
            if self._token_tracker is not None:
                self._token_tracker.track_embedding(text, cache_hit=True)
            return cached_embedding

    # 2. Call API (cache miss or no cache)
    try:
        result = await self._call_embedding_api([text])
        embedding = result[0]

        # 3. Validate dimensions
        if len(embedding) != self._dimensions:
            raise ValidationError(
                f"Embedding dimension mismatch: expected {self._dimensions}, "
                f"got {len(embedding)}"
            )

        # 4. Store in cache (if enabled)
        if self._cache is not None:
            self._cache.set(text, embedding)

        # 5. Track token usage (if enabled)
        if self._token_tracker is not None:
            self._token_tracker.track_embedding(text, cache_hit=False)

        return embedding

    except APITimeoutError as e:
        raise TimeoutError(
            "OpenAI embedding request timed out after retries"
        ) from e
    # ... existing error handling ...
```

### Configuration Extension Pattern
```python
# Source: knowledge_mcp.utils.config + Pydantic docs
def load_config() -> KnowledgeConfig:
    """Load configuration from environment variables."""
    import os
    from dotenv import load_dotenv

    # Load .env files
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # Build config with new fields
    return KnowledgeConfig(
        # ... existing fields ...

        # New: cache configuration
        cache_dir=Path(os.getenv("CACHE_DIR", "./data/embeddings/cache")),
        cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
        cache_size_limit=int(os.getenv("CACHE_SIZE_LIMIT", str(10 * 1024**3))),

        # New: token tracking configuration
        token_log_file=Path(os.getenv("TOKEN_LOG_FILE", "./data/token_usage.json")),
        token_tracking_enabled=os.getenv("TOKEN_TRACKING_ENABLED", "true").lower() == "true",
        daily_token_warning_threshold=int(os.getenv("DAILY_TOKEN_WARNING_THRESHOLD", "1000000")),
    )
```

### Server Integration Pattern
```python
# Source: knowledge_mcp.server analysis
def _ensure_dependencies(self) -> None:
    """Initialize dependencies with cache and tracking."""
    if self._searcher is not None:
        return

    if self._config is None:
        self._config = load_config()

    # Create cache if enabled
    cache = None
    if self._config.cache_enabled:
        cache = EmbeddingCache(
            self._config.cache_dir,
            self._config.embedding_model,
            size_limit=self._config.cache_size_limit,
        )

    # Create tracker if enabled
    tracker = None
    if self._config.token_tracking_enabled:
        tracker = TokenTracker(
            self._config.token_log_file,
            self._config.embedding_model,
            daily_warning_threshold=self._config.daily_token_warning_threshold,
        )

    # Create embedder with cache and tracker
    if self._embedder is None:
        self._embedder = OpenAIEmbedder(
            api_key=self._config.openai_api_key,
            model=self._config.embedding_model,
            dimensions=self._config.embedding_dimensions,
            cache=cache,
            token_tracker=tracker,
        )

    # ... create store and searcher ...
```

### Integration Test with Real Dependencies
```python
# Source: tests/integration/test_fallback.py + pytest best practices
class TestEmbedderCacheIntegration:
    """Integration tests with real cache and tracker."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path: Path) -> Path:
        """Isolated cache directory."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir

    @pytest.fixture
    def embedder_with_real_cache(
        self, temp_cache_dir: Path
    ) -> OpenAIEmbedder:
        """Embedder with real cache, mocked API."""
        cache = EmbeddingCache(temp_cache_dir, "text-embedding-3-small")
        embedder = OpenAIEmbedder(
            api_key="sk-test-key",
            cache=cache,
        )

        # Mock the API call
        embedder._client.embeddings.create = AsyncMock(
            return_value=MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
        )

        return embedder

    @pytest.mark.asyncio
    async def test_second_call_hits_cache(
        self, embedder_with_real_cache: OpenAIEmbedder
    ) -> None:
        """Verify cache prevents second API call."""
        # First call - cache miss
        result1 = await embedder_with_real_cache.embed("test text")
        call_count_1 = embedder_with_real_cache._client.embeddings.create.call_count

        # Second call - cache hit
        result2 = await embedder_with_real_cache.embed("test text")
        call_count_2 = embedder_with_real_cache._client.embeddings.create.call_count

        # Same result
        assert result1 == result2

        # Only one API call
        assert call_count_1 == 1
        assert call_count_2 == 1  # No additional calls
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| No caching | diskcache with SHA-256 keys | Phase 4.2 (2026-01) | Reduces duplicate embedding costs |
| Manual token tracking | tiktoken with daily aggregation | Phase 4.3 (2026-01) | Accurate cost visibility |
| Required dependencies | Optional constructor injection | Python 3+ best practice | Backwards compatible integration |
| Decorator pattern | Constructor injection | 2020s Python shift | Simpler testing, explicit dependencies |

**Deprecated/outdated:**
- Global singletons for cache/tracker: Anti-pattern, use constructor injection
- functools.lru_cache for embeddings: In-memory only, doesn't persist across runs
- String-based token estimation: Inaccurate, use tiktoken for OpenAI models

## Open Questions

Things that couldn't be fully resolved:

1. **Should embed_batch() use per-text caching or batch-level caching?**
   - What we know: embed_batch() processes in batches of 100, single API call per batch
   - What's unclear: Whether to check/store cache per-text or per-batch
   - Recommendation: Per-text caching (check each text individually, cache each result separately). Rationale: embed_batch() is called with varying batch contents, per-text cache maximizes hit rate

2. **Should cache/tracker be shared across multiple OpenAIEmbedder instances?**
   - What we know: Server creates one embedder instance, but tests might create multiple
   - What's unclear: Thread-safety expectations
   - Recommendation: diskcache is process-safe, TokenTracker saves on each call (safe). Document that sharing is supported.

3. **Should configuration disable cache/tracker entirely or just skip initialization?**
   - What we know: Boolean flags `cache_enabled` and `token_tracking_enabled` exist
   - What's unclear: Whether to skip creation or create but not use
   - Recommendation: Skip creation entirely (pass None). Simpler, no wasted resources.

## Sources

### Primary (HIGH confidence)
- Knowledge MCP codebase analysis:
  - `src/knowledge_mcp/embed/openai_embedder.py` (current implementation)
  - `src/knowledge_mcp/embed/cache.py` (EmbeddingCache with 100% coverage)
  - `src/knowledge_mcp/monitoring/token_tracker.py` (TokenTracker with 97% coverage)
  - `src/knowledge_mcp/utils/config.py` (configuration pattern)
  - `src/knowledge_mcp/server.py` (dependency injection pattern)
  - `tests/unit/test_embed/test_openai_embedder.py` (test patterns)
  - `tests/integration/test_fallback.py` (integration test patterns)
- Python documentation:
  - pathlib.Path API
  - unittest.mock API
  - pytest fixtures

### Secondary (MEDIUM confidence)
- [Dependency injection in Python](https://python-dependency-injector.ets-labs.org/introduction/di_in_python.html) - Constructor injection is Pythonic standard
- [Python dependency injection guide](https://www.datacamp.com/tutorial/python-dependency-injection) - Best practices for constructor injection
- [Mastering unittest.mock in Python](https://betterstack.com/community/guides/scaling-python/python-unittest-mock/) - Mock best practices
- [Python integration testing guide](https://www.lambdatest.com/learning-hub/python-integration-testing) - When to use mocks vs real dependencies
- [diskcache documentation](https://grantjenks.com/docs/diskcache/) - LRU eviction, process safety
- [tiktoken guide](https://galileo.ai/blog/tiktoken-guide-production-ai) - Accurate OpenAI token counting
- [Python optional arguments](https://realpython.com/python-optional-arguments/) - Backwards compatibility pattern

### Tertiary (LOW confidence)
- None - all findings verified with codebase analysis or official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools are Python standard library or already in dependencies
- Architecture: HIGH - Patterns verified in existing Knowledge MCP codebase
- Pitfalls: HIGH - Derived from pytest best practices and Python dependency injection patterns
- Configuration: HIGH - Extends existing Pydantic pattern in config.py

**Research date:** 2026-01-24
**Valid until:** 2026-03-24 (60 days - stable Python patterns, dependencies already locked)
