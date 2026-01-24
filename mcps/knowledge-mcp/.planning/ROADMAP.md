# Roadmap: Knowledge MCP

## Overview

Knowledge MCP must transform from a partially-implemented codebase (34% coverage, 55 pyright errors, stub MCP tools) into a fully functional MCP server for semantic search over technical documents. The journey starts with fixing broken foundations (tests, types), then builds the missing search layer, wires up MCP tools, achieves quality compliance, and finally adds extended features (hybrid search, reranking, CLI).

## Milestone: v1.0 - Spec Compliance

**Goal:** Complete CLAUDE.md specification compliance - working MCP server with 80% test coverage and zero pyright errors.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Foundation Fixes** - Fix broken tests, eliminate pyright errors, establish quality baseline
- [ ] **Phase 2: Search Layer** - Implement semantic search connecting embedder and store
- [ ] **Phase 3: MCP Tool Implementation** - Wire up functional MCP tools for knowledge search
- [ ] **Phase 4: Test Coverage** - Achieve 80% coverage with comprehensive unit and integration tests
- [ ] **Phase 5: Extended Features** - Add hybrid search, reranking, CLI, and remaining tools

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
**Plans**: TBD

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
**Plans**: TBD

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
**Plans**: TBD

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
**Plans**: TBD

### Phase 5: Extended Features
**Goal**: Add hybrid search, reranking, CLI commands, and remaining MCP tools
**Depends on**: Phase 4
**Requirements**: REQ-02 (local embeddings), REQ-04 (hybrid search), REQ-05 (reranking), REQ-06 (hierarchical chunking), REQ-07 (semantic chunking), REQ-08 (standards chunking), REQ-09 (CLI ingest), REQ-10 (CLI verify)
**Research flag**: needs-research (Cohere API, hybrid search configuration)
**Success Criteria** (what must be TRUE):
  1. `knowledge-ingest` CLI command ingests documents into the knowledge base
  2. `knowledge-mcp --verify` validates embeddings and collection health
  3. Hybrid search combines dense and sparse retrieval (when Qdrant backend)
  4. Reranking improves result quality (Cohere or local cross-encoder)
  5. Local embedding option works without OpenAI API key (sentence-transformers)
  6. `knowledge_keyword_search` and `knowledge_lookup` tools are functional
**Plans**: TBD

## Phase Ordering Rationale

1. **Phase 1 before all others**: Cannot trust test results or CI without fixing foundations. 55 pyright errors indicate potential runtime bugs. Test import failures block accurate coverage measurement.

2. **Phase 2 before Phase 3**: MCP tools depend on search layer. Search layer composes existing embedder + store - straightforward architecture. MCP protocol integration requires more careful testing.

3. **Phase 3 before Phase 4**: Need functional code to test meaningfully. Coverage without functionality is theater. Working tools provide the "what" that tests verify.

4. **Phase 4 before Phase 5**: Establish quality baseline before adding complexity. Extended features (reranking, hybrid search) are optional for core functionality but add test surface area.

5. **Phase 5 is independent features**: CLI, hybrid search, reranking can be implemented in any order within the phase. Local embeddings enable offline operation.

## Requirement Coverage

| Requirement | Description | Phase |
|-------------|-------------|-------|
| REQ-01 | Working MCP tool handlers | Phase 3 |
| REQ-02 | Local embedding support | Phase 5 |
| REQ-03 | Semantic search implementation | Phase 2 |
| REQ-04 | Hybrid search implementation | Phase 5 |
| REQ-05 | Result reranking | Phase 5 |
| REQ-06 | Hierarchical chunking strategy | Phase 5 |
| REQ-07 | Semantic chunking strategy | Phase 5 |
| REQ-08 | Standards-aware chunking strategy | Phase 5 |
| REQ-09 | CLI for document ingestion | Phase 5 |
| REQ-10 | CLI for embedding verification | Phase 5 |
| REQ-11 | 80% test coverage | Phase 1 (types), Phase 4 (coverage) |
| REQ-12 | Zero pyright errors | Phase 1 |
| REQ-13 | Verified Docling integration | Phase 1 |

**Coverage**: 13/13 requirements mapped

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation Fixes | 0/TBD | Not started | - |
| 2. Search Layer | 0/TBD | Not started | - |
| 3. MCP Tool Implementation | 0/TBD | Not started | - |
| 4. Test Coverage | 0/TBD | Not started | - |
| 5. Extended Features | 0/TBD | Not started | - |
