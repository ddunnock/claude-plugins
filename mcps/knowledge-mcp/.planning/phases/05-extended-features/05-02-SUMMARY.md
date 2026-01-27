# Phase 5 Plan 2: LocalEmbedder Implementation Summary

**One-liner:** Local embedding support using sentence-transformers with all-MiniLM-L6-v2 (384d) and create_embedder factory function.

---

## Frontmatter

```yaml
phase: 05-extended-features
plan: 02
subsystem: embed
tags: [embeddings, sentence-transformers, local, offline, factory-pattern]

dependency-graph:
  requires: []
  provides:
    - LocalEmbedder class implementing BaseEmbedder
    - create_embedder(config) factory function
    - EMBEDDING_PROVIDER config option
  affects:
    - Offline operation capability
    - Cost reduction (no OpenAI API calls)
    - CLI ingestion with local embeddings

tech-stack:
  added:
    - sentence-transformers >=3.0.0 (optional local group)
  patterns:
    - asyncio.run_in_executor for non-blocking sync operations
    - ThreadPoolExecutor(max_workers=1) for model inference
    - Factory pattern for embedder selection
    - Conditional imports for optional dependencies

key-files:
  created:
    - src/knowledge_mcp/embed/local_embedder.py
    - tests/unit/test_embed/test_local_embedder.py
  modified:
    - src/knowledge_mcp/embed/__init__.py
    - src/knowledge_mcp/utils/config.py
    - pyproject.toml

decisions:
  - "normalize_embeddings=True default for correct cosine similarity"
  - "ThreadPoolExecutor(max_workers=1) to prevent model contention"
  - "Import SentenceTransformer inside __init__ for lazy loading"
  - "Conditional LocalEmbedder export based on sentence-transformers availability"

metrics:
  tasks: 3
  duration: ~5 min
  completed: 2026-01-27
```

---

## What Was Built

### LocalEmbedder Class
Created `src/knowledge_mcp/embed/local_embedder.py` implementing the `BaseEmbedder` interface:

- **Default model:** all-MiniLM-L6-v2 (384 dimensions, fast)
- **Alternative:** all-mpnet-base-v2 (768 dimensions, higher quality)
- **Async support:** Uses `asyncio.run_in_executor()` to avoid blocking event loop
- **Normalization:** `normalize_embeddings=True` by default (critical for cosine similarity)
- **Device support:** Auto-detects GPU/CPU, configurable via `device` parameter

### Factory Function
Added `create_embedder(config)` to `embed/__init__.py`:

```python
def create_embedder(config: KnowledgeConfig) -> BaseEmbedder:
    if config.embedding_provider == "openai":
        return OpenAIEmbedder(...)
    elif config.embedding_provider == "local":
        return LocalEmbedder(model_name=config.local_embedding_model)
```

### Configuration Support
Extended `KnowledgeConfig` with:

- `embedding_provider: Literal["openai", "local"]` - defaults to "openai"
- `local_embedding_model: str` - defaults to "all-MiniLM-L6-v2"
- Updated `validate()` - only requires `OPENAI_API_KEY` when `embedding_provider="openai"`

### Tests
Created comprehensive test suite with 15 tests:

- Properties: dimensions, model_name
- Async methods: embed(), embed_batch()
- Configuration: normalize_embeddings, device, custom model
- Factory function: local/openai providers, unknown provider

---

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | `1f2e957` | feat(05-02): implement LocalEmbedder with sentence-transformers |
| 2 | (in be285f2) | Config and factory added alongside 05-03 execution |
| 3 | `83c7ace` | test(05-02): add comprehensive LocalEmbedder and create_embedder tests |

---

## Deviations from Plan

None - plan executed exactly as written.

**Note:** Task 2 changes (config.py, embed/__init__.py, pyproject.toml) appear to have been committed as part of the parallel 05-03 execution (commit `be285f2`). All functionality is present and verified.

---

## Verification Results

1. `poetry install --with local` - PASS
2. `from knowledge_mcp.embed import LocalEmbedder, create_embedder` - PASS
3. All 15 tests pass
4. `LocalEmbedder.dimensions` returns 384 - PASS
5. `create_embedder(config)` returns LocalEmbedder when `embedding_provider="local"` - PASS

**Pyright:** 5 errors from sentence-transformers type stubs (known limitation per STATE.md)

---

## Usage Examples

### Direct Usage
```python
from knowledge_mcp.embed import LocalEmbedder

embedder = LocalEmbedder()  # Uses all-MiniLM-L6-v2
vector = await embedder.embed("What is systems engineering?")
# len(vector) == 384
```

### Via Factory (Recommended)
```python
from knowledge_mcp.embed import create_embedder
from knowledge_mcp.utils.config import load_config

config = load_config()  # Reads EMBEDDING_PROVIDER env var
embedder = create_embedder(config)
```

### Environment Configuration
```bash
export EMBEDDING_PROVIDER=local
export LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## Next Phase Readiness

**Ready for:**
- CLI ingest command can use local embeddings
- Offline document ingestion without API keys
- Cost-free embedding generation

**Dependencies provided:**
- LocalEmbedder for search/reranking pipelines
- create_embedder factory for unified embedder creation
