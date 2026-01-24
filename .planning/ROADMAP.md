# Roadmap: Knowledge MCP Integration

## Overview

Migrate the finished knowledge-mcp RAG system from `../knowledge-mcp` into `mcps/knowledge-mcp/`, establishing it as both a standalone marketplace plugin and infrastructure for grounding specification-refiner in engineering standards. The journey progresses from safe migration through document ingestion pipeline to search integration, culminating in production-ready evaluation and monitoring.

## Milestone 1: MVP Integration

**Goal:** Working knowledge-mcp in claude-plugins with standards-grounded spec validation

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (e.g., 2.1): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Migration** - Move code safely, update dependencies, verify nothing breaks
- [ ] **Phase 2: Document Ingestion** - Structure-aware chunking with clause preservation for standards
- [ ] **Phase 3: Search & Integration** - MCP tools exposed, specification-refiner connected
- [x] **Phase 4: Production Readiness** - Evaluation framework, monitoring, quality gates (partial - see gaps)
- [x] **Phase 5: Production Integration** - Wire cache and token tracking into embedder

## Phase Details

### Phase 1: Migration

**Goal**: Working knowledge-mcp code running from new location with updated dependencies
**Depends on**: Nothing (first phase)
**Requirements**: FR-2.1, FR-2.2, FR-2.3, FR-2.4, FR-2.5, NFR-1.1, NFR-1.2, NFR-1.3, NFR-3.1, NFR-3.2, NFR-3.3, NFR-4.1, NFR-4.3
**Risk Callouts**:
- Pitfall #1: Breaking working code during migration - test BEFORE changes
- Pitfall #2: Embedding model lock-in - version collection names from day one
- Pitfall #6: Qdrant single point of failure - implement AND test ChromaDB fallback
- Pitfall #7: Mixing vectors from different models - store embedding_model in metadata

**Success Criteria** (what must be TRUE):
1. All existing tests pass when run from `mcps/knowledge-mcp/`
2. Dependencies updated to MCP SDK 1.25.0, Qdrant 1.16.2 (keep Docling 2.69.0)
3. ChromaDB fallback works when Qdrant connection fails
4. Collection names include embedding model version (e.g., `se_knowledge_base_v1_te3small`)
5. Health checks execute before vector store operations

**Plans**: 4 plans

Plans:
- [x] 01-01-PLAN.md — Git subtree migration and baseline test verification
- [x] 01-02-PLAN.md — Dependency updates (MCP SDK 1.25.x, qdrant-client 1.16.2+)
- [x] 01-03-PLAN.md — Collection versioning, embedding model metadata, validation
- [x] 01-04-PLAN.md — ChromaDB fallback verification and human sign-off

### Phase 2: Document Ingestion

**Goal**: Standards documents ingested with clause structure preserved, tables intact
**Depends on**: Phase 1
**Requirements**: FR-1.1, FR-1.2, FR-1.3, FR-1.4, FR-1.5, FR-1.6, NFR-2.3, NFR-4.2, NFR-4.4
**Risk Callouts**:
- Pitfall #3: Chunking destroys semantic coherence - hierarchical chunking, never split tables
- Pitfall #5: PDF parsing loses critical information - validate on samples FIRST
- Pitfall #12: Large chunks exceed context - enforce 2000 token max

**Success Criteria** (what must be TRUE):
1. PDF documents ingest with clause hierarchy preserved in metadata
2. Tables remain intact (visual comparison shows no mid-row splits)
3. Chunks include source, section, page, and clause metadata
4. Chunks tagged as normative vs informative where identifiable
5. At least 4 standards ingested (INCOSE, IEEE 15288, ISO 15288, ISO 26262)

**Plans**: 5 plans in 4 waves

Plans:
- [ ] 02-01-PLAN.md — Add Docling dependency, create tokenizer/hashing/normative utilities
- [ ] 02-02-PLAN.md — Base ingestor interface and Docling-based PDF ingestor
- [ ] 02-03-PLAN.md — Hierarchical chunker with table integrity and overlap
- [ ] 02-04-PLAN.md — DOCX support and ingestion pipeline orchestrator
- [ ] 02-05-PLAN.md — Integration tests and visual validation (human checkpoint)

### Phase 3: Search & Integration

**Goal**: MCP tools callable from Claude Desktop, specification-refiner grounded in standards
**Depends on**: Phase 2
**Requirements**: FR-3.1, FR-3.2, FR-3.3, FR-3.4, FR-3.5, FR-3.6, FR-4.1, FR-4.2, FR-4.3, FR-4.4, FR-4.5, FR-5.1, FR-5.2, FR-5.3, FR-5.4
**Risk Callouts**:
- Pitfall #11: Skill assumes MCP availability - check before calling, graceful degradation
- Pitfall #15: Search results lack provenance - return source, clause, page

**Success Criteria** (what must be TRUE):
1. `search_knowledge` tool returns relevant results with "STANDARD Clause X.Y.Z" citations
2. Hybrid retrieval (semantic + BM25) demonstrably improves keyword query results
3. specification-refiner auto-queries knowledge-mcp during validation
4. `/lookup-standard` command works for manual deep dives
5. Graceful degradation message appears when MCP unavailable (not hallucination)

**Plans**: TBD

### Phase 4: Production Readiness (Partial)

**Goal**: Quality gates and monitoring ensure sustained performance
**Depends on**: Phase 3
**Requirements**: NFR-2.1, NFR-2.2 (NFR-5.1, NFR-5.2 moved to Phase 5)
**Risk Callouts**:
- Pitfall #4: No systematic evaluation - build golden test set, run on every PR
- Pitfall #10: No cost monitoring - log token counts, cache by hash
- Pitfall #14: No document update strategy - version tracking for future audits

**Success Criteria** (what must be TRUE):
1. Golden test set exists (20-50 queries) with expected results - 34 queries
2. RAG Triad metrics tracked (context relevance, faithfulness, answer relevance)
3. Token counts logged for cost visibility - **Infrastructure built, not wired (-> Phase 5)**
4. Embedding cache prevents duplicate embedding of unchanged content - **Infrastructure built, not wired (-> Phase 5)**
5. Plugin packaged for marketplace distribution

**Plans**: 5/5 complete

Plans:
- [x] 04-01-PLAN.md — Add production dependencies (ragas, diskcache) and create package structure
- [x] 04-02-PLAN.md — Implement embedding cache with content hashing
- [x] 04-03-PLAN.md — Implement token tracking and cost monitoring with CLI
- [x] 04-04-PLAN.md — Create golden test set and RAG evaluation framework
- [x] 04-05-PLAN.md — MCPB packaging and documentation (checkpoint)

**Gaps (moved to Phase 5):**
- EmbeddingCache class exists (100% coverage) but not wired to OpenAIEmbedder
- TokenTracker class exists (97% coverage) but not wired to OpenAIEmbedder

### Phase 5: Production Integration

**Goal**: Wire cache and token tracking into embedding pipeline for actual cost savings and visibility
**Depends on**: Phase 4
**Requirements**: NFR-5.1, NFR-5.2
**Risk Callouts**:
- Avoid over-engineering - simple integration, no new abstractions
- Maintain backwards compatibility - cache/tracking should be optional

**Success Criteria** (what must be TRUE):
1. OpenAIEmbedder checks EmbeddingCache before calling OpenAI API
2. Cache hits return immediately without API call (measurable cost savings)
3. OpenAIEmbedder logs token counts via TokenTracker on each request
4. Token data visible in CLI token_summary command after embedding operations
5. All existing tests pass, new integration tests verify wiring

**Plans**: 2/2 complete

Plans:
- [x] 05-01-PLAN.md — Extend KnowledgeConfig and integrate cache/tracker into OpenAIEmbedder
- [x] 05-02-PLAN.md — Wire dependencies in server, add unit and integration tests

## Progress

**Execution Order:** 1 -> 4 -> 5 -> 2 -> 3 (Phase 4-5 jumped ahead for foundation work)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Migration | 4/4 | ✓ Complete | 2026-01-23 |
| 4. Production Readiness | 5/5 | ✓ Complete | 2026-01-24 |
| 5. Production Integration | 2/2 | ✓ Complete | 2026-01-24 |
| 2. Document Ingestion | 0/5 | Planned | - |
| 3. Search & Integration | 0/TBD | Not started | - |

## Requirement Coverage

All requirements mapped to exactly one phase:

| Requirement | Phase | Description |
|-------------|-------|-------------|
| FR-1.1 | 2 | Ingest PDF documents preserving clause structure |
| FR-1.2 | 2 | Ingest DOCX documents |
| FR-1.3 | 2 | Chunk documents hierarchically (256-512 tokens, 15% overlap) |
| FR-1.4 | 2 | Preserve table integrity |
| FR-1.5 | 2 | Extract and store metadata |
| FR-1.6 | 2 | Tag chunks as normative vs informative |
| FR-2.1 | 1 | Store embeddings in Qdrant Cloud |
| FR-2.2 | 1 | Support ChromaDB as local fallback |
| FR-2.3 | 1 | Version collection names with embedding model |
| FR-2.4 | 1 | Store embedding_model in collection metadata |
| FR-2.5 | 1 | Validate model match before ingestion |
| FR-3.1 | 3 | Semantic search via OpenAI embeddings |
| FR-3.2 | 3 | Hybrid retrieval (semantic + BM25) |
| FR-3.3 | 3 | Reranking of results |
| FR-3.4 | 3 | Return source citation with section references |
| FR-3.5 | 3 | Return relevance/confidence scores |
| FR-3.6 | 3 | Support filtering by standard, section, normative status |
| FR-4.1 | 3 | Expose search_knowledge tool via MCP |
| FR-4.2 | 3 | Expose ingest_document tool via MCP |
| FR-4.3 | 3 | Expose list_collections tool via MCP |
| FR-4.4 | 3 | Return structured results with provenance |
| FR-4.5 | 3 | Graceful degradation when vector store unavailable |
| FR-5.1 | 3 | Auto-query during specification-refiner validation |
| FR-5.2 | 3 | Manual lookup via /lookup-standard command |
| FR-5.3 | 3 | Check MCP availability before calling |
| FR-5.4 | 3 | Format citations as "STANDARD Clause X.Y.Z" |
| NFR-1.1 | 1 | Health checks before vector store operations |
| NFR-1.2 | 1 | Retry logic with exponential backoff |
| NFR-1.3 | 1 | Graceful fallback to ChromaDB |
| NFR-2.1 | 4 | Evaluation test set (20-50 golden queries) |
| NFR-2.2 | 4 | Track RAG Triad metrics |
| NFR-2.3 | 2 | Validate PDF extraction on sample docs |
| NFR-3.1 | 1 | Test in new location BEFORE any code changes |
| NFR-3.2 | 1 | Keep git history for rollback |
| NFR-3.3 | 1 | Update all path dependencies atomically |
| NFR-4.1 | 1 | Modular component architecture |
| NFR-4.2 | 2 | Thin MCP wrappers (logic in components) |
| NFR-4.3 | 1 | Environment variables for configuration |
| NFR-4.4 | 2 | Store source document paths in chunk metadata |
| NFR-5.1 | 5 | Log token counts for cost monitoring (integration) |
| NFR-5.2 | 5 | Cache embeddings by content hash (integration) |

**Coverage:** 41/41 requirements mapped

---
*Roadmap created: 2026-01-23*
*Phase 1 completed: 2026-01-23*
*Phase 4 partial: 2026-01-24 (infrastructure built, integration gaps moved to Phase 5)*
*Phase 5 added: 2026-01-24*
*Phase 5 planned: 2026-01-24 (2 plans in 2 waves)*
*Phase 5 completed: 2026-01-24 (cache and token tracking fully integrated)*
*Phase 2 planned: 2026-01-24 (5 plans in 4 waves)*
