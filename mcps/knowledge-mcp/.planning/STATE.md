# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** The MCP server must actually work - when Claude calls the search tool, it gets real results from the knowledge base.
**Current focus:** Phase 4 - Test Coverage (In Progress)

## Current Position

Phase: 4 of 5 (Test Coverage) - In Progress
Plan: 03 of 5 complete (04-02, 04-03, 04-05 done)
Status: Plan 04-02 (logging & CLI tests) complete
Last activity: 2026-01-27 - Completed 04-02-PLAN.md (logging & CLI tests)

Progress: [########--] 80%

## Performance Metrics

**Velocity:**
- Total plans completed: 6
- Average duration: 5.7 min
- Total execution time: 36 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | - | - | External |
| 2 | 1/1 | 5 min | 5 min |
| 3 | 1/1 | 10 min | 10 min |
| Doc Ingest | 5/5 | ~60 min | 12 min |
| 4 | 3/5 | 12 min | 4 min |

**Recent Trend:**
- Last 5 plans: Doc-01-05, 04-03, 04-05, 04-02
- Trend: Test coverage plans executing quickly

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

### Pending Todos

- Complete remaining Phase 4 plans (04-01, 04-04)

### Blockers/Concerns

None - All tools working, 44 tests passing for logging/CLI, zero pyright errors.

### Known Limitations (non-blocking)

- Docling GLYPH encoding issues with some PDF fonts
- Section hierarchy accumulates all headings (very long)
- Docling deprecation warning for TableItem.export_to_dataframe()

## Session Continuity

Last session: 2026-01-27
Stopped at: Completed 04-02-PLAN.md (logging & CLI tests)
Resume file: None (plan complete)
Next: Continue Phase 4 (plans 04-01, 04-04)
