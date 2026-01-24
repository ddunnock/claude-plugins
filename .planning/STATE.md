# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-23)

**Core value:** Ground specification refinement in actual engineering standards via RAG
**Current focus:** Phase 2 - Document Ingestion

## Current Position

Phase: 2 of 5 (Document Ingestion)
Plan: 4 of 5 in current phase (complete)
Status: In progress
Last activity: 2026-01-24 - Completed 02-04-PLAN.md

Progress: [###-------] 27%

## Performance Metrics

**Velocity:**
- Total plans completed: 16
- Average duration: ~7.6 min/plan
- Total execution time: ~2 hours 8 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Migration | 4 | ~1 hour | ~15 min |
| 2. Document Ingestion | 4 | ~28 min | ~7 min |
| 2. Search Layer | 1 | ~5 min | ~5 min |
| 4. Production Readiness | 5 | ~25 min | ~5 min |
| 5. Production Integration | 2 | ~9 min | ~4.5 min |

**Recent Trend:**
- Last 5 plans: 05-02, 02-01, 02-03, 02-02, 02-04
- Trend: Consistent fast execution on focused tasks (~6-10 min)

*Updated after each plan completion*

## Phase 4 Completion Summary

Phase 4 executed all 5 plans across 4 waves:
- Wave 1: 04-01 (dependencies - ragas, diskcache, pytest-golden, python-json-logger)
- Wave 2: 04-02 (EmbeddingCache), 04-03 (TokenTracker) - parallel
- Wave 3: 04-04 (Golden tests + RAG evaluation)
- Wave 4: 04-05 (MCPB packaging) - human checkpoint approved

**Verification Result:** 3/5 criteria passed (60%)
- ✓ Golden test set: 34 queries across 6 categories
- ✓ RAG Triad metrics: RAGAS integration complete
- ✗ Token tracking: Infrastructure exists but not wired to embedder
- ✗ Embedding cache: Infrastructure exists but not wired to embedder
- ✓ Plugin packaged: manifest.json + scripts + README

**Gaps moved to Phase 5:**
- EmbeddingCache (100% test coverage) not integrated with OpenAIEmbedder
- TokenTracker (97% test coverage) not integrated with OpenAIEmbedder

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Git subtree chosen over simple copy (preserves history)
- Collection versioning format: `{base}_v1_{model_short}`
- ChromaDB fallback implemented with automatic detection
- Added datasets>=2.14.0 constraint for pyarrow compatibility (04-01)
- Added pillow>=10.0.0 for ragas multimodal prompts (04-01)
- SHA-256 hash with text normalization for embedding cache keys (04-02)
- Model name in cache path for automatic invalidation on model change (04-02)
- 10GB default cache size limit with LRU eviction (04-02)
- tiktoken for accurate OpenAI token counting (matches API billing) (04-03)
- Daily aggregation to JSON file for simple token stats persistence (04-03)
- 1M token warning threshold per day (configurable) (04-03)
- Dual evaluation modes: lightweight recall@k (CI) + RAGAS RAG Triad (periodic) (04-04)
- 34 golden queries across 6 categories with difficulty levels (04-04)
- 80% recall threshold for golden test pass criteria (04-04)
- Constructor injection for cache/tracker in OpenAIEmbedder (05-01)
- Per-text caching in embed_batch for optimal hit rate (05-01)
- Backward compatibility via optional parameters (05-01)
- Only create cache/tracker when embedder not injected (preserves testability) (05-02)
- Mock vs real dependency separation between unit and integration tests (05-02)
- Docling 2.70.0 for unified document parsing (PDF, DOCX, PPTX, XLSX, HTML, images) (02-01)
- tiktoken cl100k_base for OpenAI-compatible token counting (02-01)
- SHA-256 with whitespace/line ending normalization for content hashing (02-01)
- RFC 2119 keyword detection (SHALL/SHOULD/MAY) for normative classification (02-01)
- Base ingestor interface (BaseIngestor, ParsedDocument, ParsedElement) for extensibility (02-02)
- Table extraction via export_to_dataframe() as list[list[str]] for structured data (02-02)
- Section hierarchy as list[str] (e.g., ['4', '4.2', '4.2.3']) for clause-level citations (02-02)
- DocumentMetadata with source_path per NFR-4.4 for provenance tracking (02-02)
- 500 token target, 1000 max, 100 overlap (20%) for chunk configuration (02-03)
- Structure-aware splitting by paragraphs to preserve semantic coherence (02-03)
- Table row-level splitting with header preservation (never split mid-row) (02-03)
- 20% overlap between adjacent chunks for context continuity (02-03)
- Small chunk merging (under 100 tokens) to avoid inefficient micro-chunks (02-03)
- Same DocumentConverter for DOCX as PDF (Docling supports both natively) (02-04)
- Pipeline converts between ingest.base and chunk.base ParsedElement types (02-04)
- Enrichment in pipeline (UUID, hash, normative) not chunker (separation of concerns) (02-04)

### Pending Todos

None - Phase 5 complete

### Blockers/Concerns

Risks mitigated in Phase 1:
- ✅ Pitfall #1: Tests verified in new location BEFORE code changes
- ✅ Pitfall #6: ChromaDB fallback tested (5 integration tests)
- ✅ Pitfall #7: Embedding model stored in metadata, validation added

Remaining risks for future phases:
- Pitfall #3: Chunking destroys semantic coherence - MITIGATED (02-03: structure-aware splitting)
- Pitfall #5: PDF parsing loses critical information - MITIGATED (02-02: Docling table extraction + hierarchy preservation)

## Phase 5 Completion Summary

Phase 5 executed both plans in wave 2:
- Wave 1: 05-01 (Cache and token tracking integration into OpenAIEmbedder)
- Wave 2: 05-02 (Server dependency wiring + comprehensive tests)

**Verification Result:** All success criteria met
- ✓ OpenAIEmbedder checks EmbeddingCache before calling OpenAI API
- ✓ Cache hits return immediately without API call
- ✓ OpenAIEmbedder logs token counts via TokenTracker
- ✓ Token data recorded in daily summary
- ✓ All existing tests pass
- ✓ New unit tests verify cache/tracker integration (9 tests)
- ✓ New integration tests verify end-to-end behavior (5 tests)
- ✓ Zero pyright errors

**Production Ready:**
- Cost optimization via embedding cache (LRU eviction, configurable limits)
- Token usage monitoring with daily warnings
- Comprehensive test coverage (unit + integration)
- Backward compatible (optional cache/tracker parameters)

## Phase 2 Progress

Phase 2 in progress:
- Plan 02-01 (Foundation utilities): Complete - 3 tasks, 3 commits, 4m 40s
- Plan 02-02 (PDF ingestor with Docling): Complete - 3 tasks, 3 commits, 10m 28s
- Plan 02-03 (Hierarchical chunking): Complete - 3 tasks, 3 commits, 6m 59s
- Plan 02-04 (DOCX & pipeline): Complete - 3 tasks, 3 commits, 6m 5s

**Next:**
- Plan 02-05 (Ingestion CLI and verification)

## Session Continuity

Last session: 2026-01-24
Stopped at: Completed 02-04-PLAN.md (DOCX ingestion and pipeline)
Resume file: None

---
*Status: Phase 2 in progress - Foundation, PDF ingestion, and chunking complete*
