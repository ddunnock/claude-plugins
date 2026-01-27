# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** The MCP server must actually work - when Claude calls the search tool, it gets real results from the knowledge base.
**Current focus:** Milestone v1.0 Complete ✓

## Current Position

Phase: 5 of 5 (Extended Features) - COMPLETE
Plan: 4 of 4 (All plans complete)
Status: **Milestone v1.0 - Spec Compliance COMPLETE**
Last activity: 2026-01-27 - All Phase 5 plans executed

Progress: [##########] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 12
- Average duration: 4.8 min
- Total execution time: ~58 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | - | - | External |
| 2 | 1/1 | 5 min | 5 min |
| 3 | 1/1 | 10 min | 10 min |
| Doc Ingest | 5/5 | ~60 min | 12 min |
| 4 | 5/5 | 15 min | 3 min |
| 5 | 4/4 | ~15 min | ~4 min |

**Recent Trend:**
- Last 5 plans: 05-04, 05-03, 05-02, 05-01, 04-05
- Trend: Phase 5 plans executed in parallel (Wave 1: 05-01, 05-02, 05-03; Wave 2: 05-04)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Docling for unified document parsing (PDF, DOCX, PPTX, XLSX, HTML, images)
- [Init]: Qdrant primary, ChromaDB fallback for vector storage
- [Init]: OpenAI embeddings (text-embedding-3-small) as default
- [Phase 1]: MCP SDK 1.25.0, qdrant-client 1.16.2 dependencies confirmed
- [Phase 1]: 40 tests passing, zero pyright errors
- [Phase 2]: Use BaseStore interface instead of Union for type safety
- [Phase 2]: Return empty list on errors for graceful degradation
- [Phase 2]: Use cast() for list conversions to satisfy pyright strict mode
- [Phase 3]: Lazy dependency initialization via _ensure_dependencies() for test mocking
- [Phase 3]: MCP request handlers accessed via request type classes as dict keys
- [Phase 3]: Two-layer error handling (SemanticSearcher + MCP handler)
- [Phase 3]: Fix print() to sys.stderr.write() for JSON-RPC compatibility
- [Doc Ingest]: Docling 2.70.0 for PDF parsing with table extraction
- [Doc Ingest]: Hierarchical chunking with 500 token target, 1000 max, 100 overlap
- [Doc Ingest]: Small chunks (<100 tokens) merged with adjacent chunks
- [Doc Ingest]: Three-state normative: True (SHALL/MUST), False (MAY/NOTE), None (unknown)
- [Doc Ingest]: Section markers "(normative)"/"(informative)" take priority over keywords
- [Phase 4]: Test run() with asyncio.wait_for timeout to avoid blocking
- [Phase 4]: Test signal handlers by patching loop.add_signal_handler
- [Phase 4]: Mock only embedder (not store) for MCP tool integration tests
- [Phase 4]: Patch asyncio.run directly for CLI tests (import inside function)
- [Phase 4]: 86% line coverage verified, exceeds 80% threshold
- [Phase 5]: Hybrid search deferred to v2 (multi-collection design)
- [Phase 5]: CLI uses subcommand pattern (`knowledge ingest docs`) for v2 extensibility
- [Phase 5]: New MCP tools deferred to v2 (15-tool consolidated design)
- [Phase 5]: Local embeddings only - offline sync deferred to v2 OfflineManager
- [Phase 5]: Reranking included (not in v2 spec, no conflict)
- [05-01]: CLI uses Typer subcommand groups for extensibility
- [05-01]: Entry point: `knowledge = "knowledge_mcp.cli.main:cli"`
- [05-02]: normalize_embeddings=True default for correct cosine similarity
- [05-02]: ThreadPoolExecutor(max_workers=1) to prevent model contention
- [05-02]: Conditional LocalEmbedder export based on sentence-transformers availability
- [05-03]: dataclasses.replace() for immutable SearchResult updates
- [05-03]: cast() for pyright strict mode with Cohere API response
- [05-04]: Verify command uses existing store.get_stats() API
- [05-04]: Verify defaults to versioned_collection_name from config

### Pending Todos

None - Milestone v1.0 complete.

### Blockers/Concerns

None. All Phase 5 work is v2-compatible.

### Known Limitations (non-blocking)

- Docling GLYPH encoding issues with some PDF fonts
- Section hierarchy accumulates all headings (very long)
- Docling deprecation warning for TableItem.export_to_dataframe()
- Pre-existing pyright errors (113) from missing type stubs for external libraries
- Pre-existing ruff errors (468) primarily docstring formatting (D212)

## Session Continuity

Last session: 2026-01-27
Stopped at: Milestone v1.0 Complete
Resume file: .planning/ROADMAP.md
Next: Consider v2 migration or new milestone
