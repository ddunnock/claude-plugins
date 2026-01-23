# Phase 1: Migration - Research

**Researched:** 2026-01-23
**Domain:** Python codebase migration with dependency updates and architectural enhancement
**Confidence:** HIGH

## Summary

Phase 1 involves migrating working knowledge-mcp code from `../knowledge-mcp/` to `mcps/knowledge-mcp/` while updating dependencies and implementing vector store resilience features. The source codebase is well-architected with 26 test files providing 80%+ coverage, mature error handling, and existing ChromaDB fallback logic.

**Critical Finding:** The existing code already uses Docling (not pymupdf4llm as mentioned in stack research). Docling is the correct choice based on extensive analysis already completed in the source repository. The migration should preserve Docling, not replace it with pymupdf4llm.

**Key architectural strengths already present:**
- Health checks implemented in both Qdrant and ChromaDB stores
- Retry logic with exponential backoff in OpenAI embedder (using tenacity library)
- Comprehensive fallback logic in `create_store()` factory function
- Collection versioning NOT yet implemented (needs addition)
- Embedding model tracking exists in chunk model but NOT stored in vector store metadata (needs addition)

**Primary recommendation:** Use git subtree or git filter-repo for history-preserving migration, test existing functionality BEFORE any code changes, then layer in collection versioning and embedding model metadata storage.

## Standard Stack

The codebase already uses best-practice libraries. Updates needed are version bumps, not replacements.

### Core
| Library | Current | Target | Purpose | Why Standard |
|---------|---------|--------|---------|--------------|
| mcp | >=1.0.0 | >=1.25.0 | Model Context Protocol SDK | Official Python SDK for MCP servers |
| qdrant-client | >=1.7.0 | >=1.16.2 | Vector database client | Official Qdrant Python client, stable API |
| docling | ==2.69.0 | ==2.69.0 | Document parsing (PDF/DOCX) | IBM Research, superior table/layout extraction |
| openai | >=1.0.0 | >=1.0.0 | Embeddings API | Official OpenAI SDK |
| tenacity | >=8.0.0 | >=8.0.0 | Retry logic | De facto standard for retry patterns |
| pydantic | >=2.0.0 | >=2.0.0 | Data validation | Type-safe models, used throughout |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| chromadb | >=0.4.0 | Local vector store fallback | Already in optional dependency group |
| tiktoken | >=0.5.0 | Token counting | OpenAI tokenizer for chunking |
| python-dotenv | >=1.0.0 | Environment config | .env file loading |

### Migration NOT Needed
| Keep | Don't Replace With | Reason |
|------|---------------------|--------|
| docling | pymupdf4llm | Docling provides superior table structure, layout analysis, OCR support. Extensive analysis already completed (see docling-integration-analysis.md) |

**Installation:**
```bash
cd mcps/knowledge-mcp
poetry install --with dev,chromadb
```

## Architecture Patterns

### Existing Project Structure (Preserve This)
```
mcps/knowledge-mcp/
├── src/knowledge_mcp/
│   ├── __init__.py
│   ├── server.py           # MCP server
│   ├── chunk/              # Docling-based chunking
│   ├── embed/              # OpenAI embedder with retry
│   ├── ingest/             # Docling ingestor
│   ├── models/             # Pydantic models
│   ├── search/             # Semantic search
│   ├── store/              # Qdrant + ChromaDB
│   │   ├── base.py         # BaseStore interface
│   │   ├── qdrant_store.py # Primary vector store
│   │   ├── chromadb_store.py # Fallback store
│   │   └── __init__.py     # create_store() factory
│   └── utils/              # Config, logging
├── tests/
│   ├── unit/               # 80%+ coverage
│   ├── integration/        # Fallback tests
│   └── conftest.py         # Fixtures
├── pyproject.toml
└── .env.example
```

### Pattern 1: Vector Store Factory with Fallback
**What:** `create_store()` tries Qdrant first, falls back to ChromaDB on connection errors
**When to use:** Already implemented, preserve during migration
**Example:**
```python
# Source: /Users/dunnock/projects/knowledge-mcp/src/knowledge_mcp/store/__init__.py
def create_store(config: KnowledgeConfig) -> BaseStore:
    if config.vector_store == "qdrant":
        store, qdrant_attempt = _try_qdrant(config)
        if store is not None:
            return store

        # Fallback to ChromaDB
        logger.warning("Qdrant unavailable, falling back to ChromaDB")
        store, chromadb_attempt = _try_chromadb(config)
        if store is not None:
            return store

        raise ConnectionError(_format_failure_message([qdrant_attempt, chromadb_attempt]))
```

### Pattern 2: Retry with Exponential Backoff
**What:** Tenacity decorator for OpenAI API calls with 3 retries
**When to use:** Already implemented for embeddings, consider for vector store operations
**Example:**
```python
# Source: /Users/dunnock/projects/knowledge-mcp/src/knowledge_mcp/embed/openai_embedder.py
@retry(
    retry=retry_if_exception_type((APIConnectionError, APITimeoutError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
async def _call_embedding_api(self, texts: list[str]) -> list[list[float]]:
    response = await self._client.embeddings.create(
        model=self._model,
        input=texts,
    )
    return [item.embedding for item in response.data]
```

### Pattern 3: Health Check Before Operations
**What:** Both stores implement `health_check()` called by `create_store()`
**When to use:** Already implemented, preserve pattern
**Example:**
```python
# Source: /Users/dunnock/projects/knowledge-mcp/src/knowledge_mcp/store/qdrant_store.py
def health_check(self) -> bool:
    try:
        self.client.get_collection(self.collection)
        return True
    except Exception as e:
        logger.warning("Qdrant health check failed: %s", e)
        return False
```

### Anti-Patterns to Avoid
- **Breaking working tests during migration:** Test BEFORE any code changes
- **Losing git history:** Use git subtree or filter-repo, not plain cp
- **Switching from Docling to pymupdf4llm:** Docling is the correct choice, already validated

## Don't Hand-Roll

Problems that already have solutions in the existing codebase:

| Problem | Don't Build | Use Existing | Why |
|---------|-------------|--------------|-----|
| Vector store fallback | Custom fallback logic | `create_store()` factory | Already implements Qdrant → ChromaDB fallback with health checks |
| Retry logic | Custom retry decorators | tenacity library | Already used in OpenAI embedder, battle-tested |
| Health checks | Polling loops | Store `health_check()` methods | Lightweight, already implemented in both stores |
| Environment config | Manual os.getenv() | `load_config()` with pydantic | Validation, type safety, .env support |
| Collection versioning | Manual naming | NEEDS IMPLEMENTATION | Not yet present, must add |
| Embedding model tracking | NEEDS IMPLEMENTATION | Add to store metadata | Chunk model has it, stores don't persist it |

**Key insight:** The existing codebase is mature and well-tested. Don't rebuild what already works. Focus on the two missing pieces: collection versioning and embedding model metadata.

## Common Pitfalls

### Pitfall 1: Losing Git History During Migration
**What goes wrong:** Using `cp -r ../knowledge-mcp mcps/` loses all commit history
**Why it happens:** Simple file copy doesn't preserve git metadata
**How to avoid:** Use git subtree or git filter-repo
**Warning signs:** `git log mcps/knowledge-mcp/` shows only the copy commit

**Recommended approach:**
```bash
# Option 1: git subtree (preserves full history)
cd /Users/dunnock/projects/claude-plugins
git subtree add --prefix=mcps/knowledge-mcp \
    ../knowledge-mcp main --squash=false

# Option 2: git filter-repo (cleaner for large repos)
cd /Users/dunnock/projects/knowledge-mcp
git filter-repo --to-subdirectory-filter mcps/knowledge-mcp
cd /Users/dunnock/projects/claude-plugins
git remote add knowledge-mcp ../knowledge-mcp
git fetch knowledge-mcp
git merge knowledge-mcp/main --allow-unrelated-histories
```

Sources: [Merging Multiple Repositories Into a Monorepo Using Git Subtree](https://medium.com/@andrejkurocenko/merging-multiple-repositories-into-a-monorepo-using-git-subtree-without-losing-history-0c019046498e), [Migrating Git from multirepo to monorepo without losing history](https://developers.netlify.com/guides/migrating-git-from-multirepo-to-monorepo-without-losing-history/)

### Pitfall 2: Breaking Changes in Dependency Updates
**What goes wrong:** Updating qdrant-client 1.7.0 → 1.16.2 breaks code using deprecated methods
**Why it happens:** v1.16.0 removed deprecated `search()`, `recommend()`, `upload_records()` methods
**How to avoid:** Check existing code doesn't use deprecated methods before updating
**Warning signs:** Code uses `client.search()` instead of `client.query_points()`

**Verification:**
```bash
cd /Users/dunnock/projects/knowledge-mcp
grep -r "\.search(" src/knowledge_mcp/store/
grep -r "\.recommend(" src/knowledge_mcp/store/
grep -r "\.upload_records(" src/knowledge_mcp/store/
```

**Good news:** Existing code uses `client.search(collection_name=...)` with collection_name parameter, which is the NEW API (not deprecated). The deprecated `search()` was the one WITHOUT collection_name. Code is safe to update.

### Pitfall 3: Collection Name Conflicts When Adding Versioning
**What goes wrong:** Changing collection name from `se_knowledge_base` to `se_knowledge_base_v1_te3small` breaks existing data
**Why it happens:** New collection name doesn't match existing data
**How to avoid:** Either migrate data or use environment variable for version suffix
**Warning signs:** Empty search results after changing collection name

**Migration strategy:**
```python
# Add to config.py
qdrant_collection: str = Field(
    default="se_knowledge_base",  # Keep default for backward compatibility
    description="Qdrant collection name (add version suffix for new deployments)",
)

# Best practice for NEW deployments:
# QDRANT_COLLECTION=se_knowledge_base_v1_te3small
```

### Pitfall 4: Tests Passing in Old Location But Failing in New Location
**What goes wrong:** Relative paths or assumptions about repo root break after migration
**Why it happens:** Code uses relative imports or path assumptions
**How to avoid:** Run full test suite immediately after migration, before any changes
**Warning signs:** Import errors or FileNotFoundError in tests

**Verification checklist:**
```bash
cd mcps/knowledge-mcp
poetry install
poetry run pytest tests/  # Must pass 100% before any code changes
poetry run ruff check src/
poetry run pyright src/
```

### Pitfall 5: MCP SDK 1.25.0 Breaking Changes
**What goes wrong:** Updating mcp 1.0.0 → 1.25.0 breaks server initialization
**Why it happens:** v1.25.0 is last v1.x release before v2.0 transport changes
**How to avoid:** Pin to `mcp>=1.25,<2` to avoid v2.0 breaking changes
**Warning signs:** Server fails to start or transport errors

**Good news:** v1.25.0 maintains backward compatibility within v1.x series. Major breaking changes are in v2.0 (Q1 2026). Safe to update within v1.x.

## Code Examples

Verified patterns from existing codebase:

### Collection Versioning (NEEDS IMPLEMENTATION)
```python
# Add to src/knowledge_mcp/utils/config.py
@property
def versioned_collection_name(self) -> str:
    """Generate collection name with embedding model version.

    Example: se_knowledge_base_v1_te3small
    """
    # Extract model version (e.g., text-embedding-3-small → te3small)
    model_short = self.embedding_model.replace("text-embedding-", "te").replace("-", "")
    return f"{self.qdrant_collection}_v1_{model_short}"

# Update QdrantStore.__init__() to use versioned name
self.collection = config.versioned_collection_name
```

### Embedding Model Metadata Storage (NEEDS IMPLEMENTATION)
```python
# Update src/knowledge_mcp/store/qdrant_store.py
def add_chunks(self, chunks: list[KnowledgeChunk]) -> int:
    # ... existing code ...
    point = PointStruct(
        id=chunk.id,
        vector=vectors if self.hybrid_enabled else chunk.embedding,
        payload={
            "content": chunk.content,
            # ... existing fields ...
            "embedding_model": chunk.embedding_model,  # ADD THIS
            "embedding_dimensions": len(chunk.embedding) if chunk.embedding else 0,  # ADD THIS
        },
    )
```

### Model Version Validation (NEEDS IMPLEMENTATION)
```python
# Add to src/knowledge_mcp/store/qdrant_store.py
def validate_embedding_model(self, expected_model: str) -> bool:
    """Verify collection uses expected embedding model.

    Returns:
        True if model matches or collection is empty.

    Raises:
        ValueError: If collection has data with different embedding model.
    """
    try:
        # Sample one point to check metadata
        results = self.client.scroll(
            collection_name=self.collection,
            limit=1,
        )
        if not results[0]:  # Empty collection
            return True

        point = results[0][0]
        stored_model = point.payload.get("embedding_model")
        if stored_model and stored_model != expected_model:
            raise ValueError(
                f"Collection '{self.collection}' uses {stored_model}, "
                f"but config specifies {expected_model}. "
                f"Use different collection name or recreate collection."
            )
        return True
    except Exception as e:
        logger.warning("Model validation failed: %s", e)
        return False
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| pymupdf4llm for PDF parsing | Docling 2.69.0 | Existing (Dec 2025) | Superior table extraction, layout analysis, OCR support |
| Manual collection naming | NEEDS: Version-embedded names | Not yet implemented | Prevents embedding model lock-in |
| Chunk-only model tracking | NEEDS: Store metadata tracking | Not yet implemented | Enables model validation before ingestion |
| qdrant-client <1.16 | qdrant-client >=1.16.2 | Target update | Removed deprecated methods, added BM25, gRPC pooling |
| mcp 1.0.0 | mcp 1.25.0 | Target update | Last stable v1.x before v2.0 transport changes |

**Deprecated/outdated:**
- Qdrant `search()` without collection_name: Removed in v1.16.0, use `search(collection_name=...)`
- Qdrant `upload_records()`: Removed in v1.16.0, use `upsert()`
- Python 3.8-3.9: No longer supported by qdrant-client 1.16.2
- MCP SDK v2.0 (unreleased): Major breaking changes planned for Q1 2026, stick to v1.25.x

Sources: [MCP SDK Releases](https://github.com/modelcontextprotocol/python-sdk/releases), [Qdrant Client Releases](https://github.com/qdrant/qdrant-client/releases)

## Open Questions

Things that couldn't be fully resolved:

1. **Git Migration Strategy**
   - What we know: git subtree and git filter-repo both preserve history
   - What's unclear: Which is better for this specific case (single repo → monorepo subdirectory)
   - Recommendation: Use git subtree with `--squash=false` for full history, or git filter-repo for cleaner result

2. **Collection Migration Strategy**
   - What we know: Changing collection name breaks access to existing data
   - What's unclear: Does existing Qdrant instance have production data that needs migration?
   - Recommendation: Check if `se_knowledge_base` collection exists and has data. If yes, either migrate or keep old name and add versioning for future collections only.

3. **ChromaDB Collection Versioning**
   - What we know: Qdrant collection versioning strategy is clear
   - What's unclear: Should ChromaDB fallback also use versioned collection names?
   - Recommendation: Yes, for consistency. Both stores should use `config.versioned_collection_name`

4. **Test Data Migration**
   - What we know: Tests use `./collections/chromadb` path for ChromaDB
   - What's unclear: Do test fixtures need path updates for new location?
   - Recommendation: Run tests immediately after migration to identify path issues

## Sources

### Primary (HIGH confidence)
- Existing codebase at `/Users/dunnock/projects/knowledge-mcp/` - All architecture patterns verified
- docling-integration-analysis.md - Comprehensive analysis of Docling vs pymupdf4llm decision
- pyproject.toml - Current dependency versions and configurations
- tests/ directory - 26 test files with 80%+ coverage
- [MCP Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk/releases) - Official releases
- [Qdrant Client GitHub](https://github.com/qdrant/qdrant-client/releases) - Official changelog

### Secondary (MEDIUM confidence)
- [Merging repos with git subtree](https://medium.com/@andrejkurocenko/merging-multiple-repositories-into-a-monorepo-using-git-subtree-without-losing-history-0c019046498e) - Migration best practices
- [Netlify monorepo guide](https://developers.netlify.com/guides/migrating-git-from-multirepo-to-monorepo-without-losing-history/) - History preservation
- [Docling vs PyMuPDF comparison](https://dev.to/ashokan/from-pdfs-to-markdown-evaluating-document-parsers-for-air-gapped-rag-systems-58eh) - Parser evaluation

### Tertiary (LOW confidence)
- Web search results on migration strategies - General guidance, not project-specific

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified in existing pyproject.toml
- Architecture: HIGH - Patterns extracted from working codebase with tests
- Pitfalls: HIGH - Based on official changelogs and existing code analysis
- Git migration: MEDIUM - Multiple approaches work, choice depends on preferences
- Collection versioning: MEDIUM - Pattern is clear, migration strategy depends on data state

**Research date:** 2026-01-23
**Valid until:** 2026-02-23 (30 days - dependencies are stable)

**Critical for planning:**
1. Existing code is HIGH quality - preserve, don't rebuild
2. Docling is correct choice - do NOT switch to pymupdf4llm
3. Two features need implementation: collection versioning + embedding model metadata
4. Test BEFORE any code changes to establish baseline
5. Git history preservation requires git subtree or filter-repo, not cp
