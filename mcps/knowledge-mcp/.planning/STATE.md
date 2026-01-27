# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-20)

**Core value:** The MCP server must actually work - when Claude calls the search tool, it gets real results from the knowledge base.
**Current focus:** Phase 5 - Extended Features (In Progress)

## Current Position

Phase: 5 of 5 (Extended Features)
Plan: 1 of 3 (CLI Framework)
Status: In progress
Last activity: 2026-01-27 - Completed 05-01-PLAN.md (Typer CLI)

Progress: [###       ] 33%

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: 5.3 min
- Total execution time: 39 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | - | - | External |
| 2 | 1/1 | 5 min | 5 min |
| 3 | 1/1 | 10 min | 10 min |
| Doc Ingest | 5/5 | ~60 min | 12 min |
| 4 | 5/5 | 15 min | 3 min |

**Recent Trend:**
- Last 5 plans: 05-01, 04-03, 04-05, 04-02, 04-01
- Trend: Phase 5 plans executing smoothly

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

### Pending Todos

- Execute 05-02-PLAN.md (Local Embeddings)
- Execute 05-03-PLAN.md (Reranking)

### Blockers/Concerns

None. Phase 5 scope refined for v2 compatibility.

### Known Limitations (non-blocking)

- Docling GLYPH encoding issues with some PDF fonts
- Section hierarchy accumulates all headings (very long)
- Docling deprecation warning for TableItem.export_to_dataframe()
- Pre-existing pyright errors (113) from missing type stubs for external libraries
- Pre-existing ruff errors (468) primarily docstring formatting (D212)

## Session Continuity

Last session: 2026-01-27
Stopped at: Completed 05-01-PLAN.md
Resume file: .planning/phases/05-extended-features/05-01-SUMMARY.md
Next: Execute 05-02-PLAN.md or 05-03-PLAN.md
