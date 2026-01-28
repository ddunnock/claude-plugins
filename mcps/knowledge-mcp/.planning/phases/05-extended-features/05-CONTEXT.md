# Phase 5 Context: Extended Features

## Discussion Summary

**Date:** 2026-01-27
**Phase Goal:** Add CLI, local embeddings, and reranking
**v2 Compatibility:** All decisions made to support v2 without rework

## Decisions Made

### 1. Hybrid Search → DEFERRED TO v2

**Decision:** Do not implement hybrid search in Phase 5.

**Rationale:**
- v2 spec expands from 1 collection to 8 collections
- v2 designs hybrid search with multi-collection support
- Implementing Phase 5 hybrid would be reworked in v2

**Impact:** REQ-04 (Hybrid search) removed from Phase 5 scope.

---

### 2. CLI Design → SUBCOMMAND PATTERN

**Decision:** Use subcommand pattern: `knowledge ingest docs <path>`

**Rationale:**
- Enables clean extension to `knowledge ingest web <url>` in v2
- No breaking changes when v2 adds web acquisition
- Follows modern CLI conventions (git, docker, kubectl)

**Implementation:**
```
knowledge ingest docs <path>     # Phase 5
knowledge ingest web <url>       # v2 extension
knowledge verify                 # Phase 5
```

**Impact:** REQ-09 (CLI ingest) implemented with extensible design.

---

### 3. MCP Tools → DEFERRED TO v2

**Decision:** Do not add `knowledge_keyword_search` or `knowledge_lookup` tools.

**Rationale:**
- v2 spec defines 15 tools with comprehensive design
- `keyword_search` functionality merged into hybrid `knowledge_search`
- `lookup` functionality provided by `knowledge_sources` in v2
- Adding now would create migration burden

**Impact:**
- Remove `knowledge_keyword_search` from Phase 5 scope
- Remove `knowledge_lookup` from Phase 5 scope
- Existing `knowledge_search` and `knowledge_stats` remain

---

### 4. Local Embeddings → EMBEDDINGS ONLY

**Decision:** Implement working `LocalEmbedder` with sentence-transformers. Defer offline mode/sync.

**Rationale:**
- v2 adds `OfflineManager` with bidirectional Qdrant↔ChromaDB sync
- Phase 5 local embeddings enables cost-free operation
- v2 builds offline mode on top without rework

**Implementation:**
- `LocalEmbedder` uses `sentence-transformers` library
- Default model: `all-MiniLM-L6-v2` (384 dimensions, fast)
- Optional model: `all-mpnet-base-v2` (768 dimensions, better quality)
- Config: `EMBEDDING_PROVIDER=local` or `EMBEDDING_MODEL=local:all-MiniLM-L6-v2`

**Impact:** REQ-02 (Local embedding support) implemented.

---

### 5. Reranking → INCLUDE

**Decision:** Implement reranking with Cohere or local cross-encoder.

**Rationale:**
- Not in v2 spec - no conflict
- Improves search quality immediately
- Can be used with both cloud and local embeddings

**Implementation:**
- Cohere Rerank API (when API key available)
- Local cross-encoder fallback (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- Config: `RERANKER=cohere` or `RERANKER=local`

**Impact:** REQ-05 (Result reranking) implemented.

---

## Revised Phase 5 Scope

### IN SCOPE

| Item | Requirement | Notes |
|------|-------------|-------|
| CLI subcommands | REQ-09 | `knowledge ingest docs`, `knowledge verify` |
| Local embeddings | REQ-02 | sentence-transformers, no offline sync |
| Reranking | REQ-05 | Cohere + local cross-encoder |

### DEFERRED TO v2

| Item | Original Req | v2 Coverage |
|------|--------------|-------------|
| Hybrid search | REQ-04 | v2 Phase 1 with multi-collection |
| `knowledge_keyword_search` | - | Merged into hybrid `knowledge_search` |
| `knowledge_lookup` | - | `knowledge_sources` in v2 Phase 1 |
| Offline mode/sync | - | v2 `OfflineManager` |

### ALREADY COMPLETE (not Phase 5)

| Item | Requirement | Status |
|------|-------------|--------|
| Hierarchical chunking | REQ-06 | Implemented in Doc Ingest phase |
| Standards-aware chunking | REQ-08 | Implemented in Doc Ingest phase |

### NOT IN PHASE 5

| Item | Requirement | Notes |
|------|-------------|-------|
| Semantic chunking | REQ-07 | May be v2+ or separate phase |

---

## v2 Compatibility Notes

### What Phase 5 Prepares for v2

1. **CLI extensibility** - Subcommand pattern allows `ingest web` addition
2. **Local embeddings** - v2 OfflineManager can use LocalEmbedder
3. **Reranking** - v2 can integrate reranker into workflow searchers

### What Phase 5 Does NOT Block

1. **Multi-collection architecture** - No assumptions about single collection
2. **Tool proliferation** - No new tools that v2 would deprecate
3. **Offline sync** - No partial implementation that conflicts

### Migration Path

Phase 5 → v2:
- CLI: Add `ingest web` subcommand, no changes to `ingest docs`
- Embeddings: Add OfflineManager, LocalEmbedder unchanged
- Reranking: Integrate into WorkflowSearcher, base Reranker unchanged
- Tools: Add 13 new tools, existing 2 tools unchanged

---

## Success Criteria (Updated)

1. `knowledge ingest docs <path>` successfully ingests documents
2. `knowledge verify` validates collection health
3. Local embeddings work without OpenAI API key
4. Reranking improves result quality (measurable via test)
5. All Phase 5 code compatible with v2 architecture
