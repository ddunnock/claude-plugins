# Roadmap: Knowledge MCP

## Overview

Knowledge MCP must transform from a partially-implemented codebase (34% coverage, 55 pyright errors, stub MCP tools) into a fully functional MCP server for semantic search over technical documents. The journey starts with fixing broken foundations (tests, types), then builds the missing search layer, wires up MCP tools, achieves quality compliance, and finally adds extended features (hybrid search, reranking, CLI).

## Milestone: v1.0 - Spec Compliance

**Goal:** Complete CLAUDE.md specification compliance - working MCP server with 80% test coverage and zero pyright errors.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Foundation Fixes** - Fix broken tests, eliminate pyright errors, establish quality baseline
- [x] **Phase 2: Search Layer** - Implement semantic search connecting embedder and store
- [x] **Phase 3: MCP Tool Implementation** - Wire up functional MCP tools for knowledge search
- [x] **Phase 4: Test Coverage** - Achieve 80% coverage with comprehensive unit and integration tests
- [x] **Phase 5: Extended Features** - Add CLI commands, local embeddings, and reranking

## Phase Details

### Phase 1: Foundation Fixes
**Goal**: Clean test collection, zero pyright errors, accurate coverage baseline
**Depends on**: Nothing (first phase)
**Requirements**: REQ-11 (zero pyright errors), REQ-13 (verified Docling integration)
**Research flag**: standard-patterns
**Success Criteria** (what must be TRUE):
  1. `pytest --collect-only` completes with zero errors (all test imports resolve)
  2. `poetry run pyright` reports zero errors in strict mode
  3. Test coverage baseline established (current state measured accurately)
  4. Docling version pinned exactly in pyproject.toml to prevent API breakage
**Plans**: Completed externally (40 tests passing, MCP SDK 1.25.0, qdrant-client 1.16.2)

### Phase 2: Search Layer
**Goal**: Semantic search implementation connecting existing embedder and store components
**Depends on**: Phase 1
**Requirements**: REQ-03 (semantic search)
**Research flag**: standard-patterns
**Success Criteria** (what must be TRUE):
  1. `SemanticSearcher.search(query)` returns relevant results from the vector store
  2. Search results include content, score, and document metadata
  3. Results can be filtered by document_type and other metadata fields
  4. Empty query or no results returns empty list (not error)
**Plans**: 1 plan
Plans:
- [x] 02-01-PLAN.md — Implement SemanticSearcher class and SearchResult dataclass with unit tests

### Phase 3: MCP Tool Implementation
**Goal**: Working MCP tools that actually search the knowledge base
**Depends on**: Phase 2
**Requirements**: REQ-01 (working MCP tool handlers)
**Research flag**: standard-patterns
**Success Criteria** (what must be TRUE):
  1. `knowledge_search` tool returns real search results when called via MCP protocol
  2. `knowledge_stats` tool returns collection statistics (document count, chunk count)
  3. MCP server starts successfully via `python -m knowledge_mcp`
  4. Tool errors return structured error responses with `isError: true`
**Plans**: 1 plan
Plans:
- [x] 03-01-PLAN.md — Implement knowledge_search and knowledge_stats tool handlers with unit tests

### Phase 4: Test Coverage
**Goal**: Achieve 80% line coverage, 75% branch coverage as required by CLAUDE.md
**Depends on**: Phase 3
**Requirements**: REQ-11 (80% test coverage)
**Research flag**: standard-patterns
**Success Criteria** (what must be TRUE):
  1. `pytest --cov` reports >= 80% line coverage
  2. `pytest --cov` reports >= 75% branch coverage
  3. All MCP tool handlers have integration tests
  4. Search layer has comprehensive unit tests (edge cases: empty results, score thresholds)
  5. Store fallback logic tested with categorized exceptions
**Plans**: 5 plans
Plans:
- [x] 04-01-PLAN.md — QdrantStore and ChromaDBStore unit tests with mocked clients, plus categorized exception fallback tests
- [x] 04-02-PLAN.md — Logging utilities and CLI entry point tests
- [x] 04-03-PLAN.md — Server initialization and lifecycle tests
- [x] 04-04-PLAN.md — Coverage verification and gap filling
- [x] 04-05-PLAN.md — MCP tool integration tests with real ChromaDB store

### Phase 5: Extended Features
**Goal**: Add CLI commands, local embeddings, and reranking (v2-compatible scope)
**Depends on**: Phase 4
**Requirements**: REQ-02 (local embeddings), REQ-05 (reranking), REQ-09 (CLI ingest), REQ-10 (CLI verify)
**Research flag**: standard-patterns (Cohere API documented, sentence-transformers well-known)
**Success Criteria** (what must be TRUE):
  1. `knowledge ingest docs <path>` CLI command ingests documents into the knowledge base
  2. `knowledge verify` validates embeddings and collection health
  3. Reranking improves result quality (Cohere or local cross-encoder)
  4. Local embedding option works without OpenAI API key (sentence-transformers)
  5. All Phase 5 code compatible with v2 architecture (no blocking changes)
**Deferred to v2** (per 05-CONTEXT.md decisions):
  - REQ-04: Hybrid search (v2 has multi-collection design)
  - `knowledge_keyword_search` and `knowledge_lookup` tools (v2 tool consolidation)
  - REQ-06/07/08: Chunking strategies (already complete or v2)
**Plans**: 4 plans
Plans:
- [x] 05-01-PLAN.md — Typer CLI framework with `knowledge ingest docs` command
- [x] 05-02-PLAN.md — LocalEmbedder with sentence-transformers
- [x] 05-03-PLAN.md — Reranker (Cohere + local cross-encoder)
- [x] 05-04-PLAN.md — `knowledge verify` CLI command

## Phase Ordering Rationale

1. **Phase 1 before all others**: Cannot trust test results or CI without fixing foundations. 55 pyright errors indicate potential runtime bugs. Test import failures block accurate coverage measurement.

2. **Phase 2 before Phase 3**: MCP tools depend on search layer. Search layer composes existing embedder + store - straightforward architecture. MCP protocol integration requires more careful testing.

3. **Phase 3 before Phase 4**: Need functional code to test meaningfully. Coverage without functionality is theater. Working tools provide the "what" that tests verify.

4. **Phase 4 before Phase 5**: Establish quality baseline before adding complexity. Extended features (reranking, hybrid search) are optional for core functionality but add test surface area.

5. **Phase 5 is independent features**: CLI, hybrid search, reranking can be implemented in any order within the phase. Local embeddings enable offline operation.

## Requirement Coverage

| Requirement | Description | Phase | Status |
|-------------|-------------|-------|--------|
| REQ-01 | Working MCP tool handlers | Phase 3 | Complete |
| REQ-02 | Local embedding support | Phase 5 | Complete |
| REQ-03 | Semantic search implementation | Phase 2 | Complete |
| REQ-04 | Hybrid search implementation | v2 | Deferred |
| REQ-05 | Result reranking | Phase 5 | Complete |
| REQ-06 | Hierarchical chunking strategy | Doc Ingest | Complete |
| REQ-07 | Semantic chunking strategy | v2+ | Deferred |
| REQ-08 | Standards-aware chunking strategy | Doc Ingest | Complete |
| REQ-09 | CLI for document ingestion | Phase 5 | Complete |
| REQ-10 | CLI for embedding verification | Phase 5 | Complete |
| REQ-11 | 80% test coverage | Phase 4 | Complete |
| REQ-12 | Zero pyright errors | Phase 1 | Complete |
| REQ-13 | Verified Docling integration | Phase 1 | Complete |

**Coverage**: 13/13 requirements mapped (2 deferred to v2, 11 complete)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation Fixes | - | Complete (external) | 2026-01-23 |
| 2. Search Layer | 1/1 | Complete | 2026-01-24 |
| 3. MCP Tool Implementation | 1/1 | Complete | 2026-01-24 |
| 4. Test Coverage | 5/5 | Complete | 2026-01-27 |
| 5. Extended Features | 4/4 | Complete | 2026-01-27 |

## Milestone Complete: v1.0 - Spec Compliance ✓

All 5 phases complete. Knowledge MCP now has:
- Working MCP server with `knowledge_search` and `knowledge_stats` tools
- 86% test coverage (exceeds 80% threshold)
- Typer CLI with `knowledge ingest docs` and `knowledge verify` commands
- Local embeddings via sentence-transformers (no OpenAI API key required)
- Result reranking (Cohere API + local cross-encoder fallback)
