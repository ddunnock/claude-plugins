# Requirements: Knowledge MCP Integration

**Project:** Migrate knowledge-mcp RAG system into claude-plugins
**Version:** 1.0
**Date:** 2026-01-23

## Functional Requirements

### FR-1: Document Ingestion
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-1.1 | Ingest PDF documents preserving clause structure | MUST | ARCHITECTURE |
| FR-1.2 | Ingest DOCX documents | SHOULD | ARCHITECTURE |
| FR-1.3 | Chunk documents hierarchically (256-512 tokens, 15% overlap) | MUST | FEATURES |
| FR-1.4 | Preserve table integrity (never split tables across chunks) | MUST | PITFALLS #3 |
| FR-1.5 | Extract and store metadata (source, section, page, clause) | MUST | FEATURES |
| FR-1.6 | Tag chunks as normative vs informative | SHOULD | PITFALLS #8 |

### FR-2: Vector Storage
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-2.1 | Store embeddings in Qdrant Cloud (primary) | MUST | STACK |
| FR-2.2 | Support ChromaDB as local fallback | MUST | PITFALLS #6 |
| FR-2.3 | Version collection names with embedding model | MUST | PITFALLS #2, #7 |
| FR-2.4 | Store embedding_model in collection metadata | MUST | PITFALLS #7 |
| FR-2.5 | Validate model match before ingestion | MUST | PITFALLS #7 |

### FR-3: Search & Retrieval
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-3.1 | Semantic search via OpenAI embeddings | MUST | FEATURES |
| FR-3.2 | Hybrid retrieval (semantic + BM25 keyword) | MUST | FEATURES |
| FR-3.3 | Reranking of results | SHOULD | FEATURES |
| FR-3.4 | Return source citation with section references | MUST | FEATURES |
| FR-3.5 | Return relevance/confidence scores | SHOULD | FEATURES |
| FR-3.6 | Support filtering by standard, section, normative status | SHOULD | PITFALLS #8 |

### FR-4: MCP Server
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-4.1 | Expose `search_knowledge` tool via MCP | MUST | ARCHITECTURE |
| FR-4.2 | Expose `ingest_document` tool via MCP | SHOULD | ARCHITECTURE |
| FR-4.3 | Expose `list_collections` tool via MCP | SHOULD | ARCHITECTURE |
| FR-4.4 | Return structured results with provenance | MUST | PITFALLS #15 |
| FR-4.5 | Graceful degradation when vector store unavailable | MUST | PITFALLS #6 |

### FR-5: Integration
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-5.1 | Auto-query during specification-refiner validation | MUST | FEATURES |
| FR-5.2 | Manual lookup via `/lookup-standard` command | MUST | FEATURES |
| FR-5.3 | Check MCP availability before calling | MUST | PITFALLS #11 |
| FR-5.4 | Format citations as "STANDARD Clause X.Y.Z" | MUST | ARCHITECTURE |

## Non-Functional Requirements

### NFR-1: Reliability
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| NFR-1.1 | Health checks before vector store operations | MUST | PITFALLS #6 |
| NFR-1.2 | Retry logic with exponential backoff | SHOULD | STACK |
| NFR-1.3 | Graceful fallback to ChromaDB if Qdrant unavailable | MUST | PITFALLS #6 |

### NFR-2: Quality
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| NFR-2.1 | Evaluation test set (20-50 golden queries) | MUST | PITFALLS #4 |
| NFR-2.2 | Track RAG Triad metrics (context relevance, faithfulness, answer relevance) | SHOULD | PITFALLS #4 |
| NFR-2.3 | Validate PDF extraction on sample docs before bulk ingest | MUST | PITFALLS #5 |

### NFR-3: Migration
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| NFR-3.1 | Test in new location BEFORE any code changes | MUST | PITFALLS #1 |
| NFR-3.2 | Keep git history for rollback capability | MUST | PITFALLS #1 |
| NFR-3.3 | Update all path dependencies atomically | MUST | PITFALLS #1 |

### NFR-4: Maintainability
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| NFR-4.1 | Modular component architecture | MUST | ARCHITECTURE |
| NFR-4.2 | Thin MCP wrappers (logic in components) | MUST | ARCHITECTURE |
| NFR-4.3 | Environment variables for configuration (EMBEDDING_MODEL, etc.) | MUST | PITFALLS #13 |
| NFR-4.4 | Store source document paths in chunk metadata for reingestion | MUST | PITFALLS #2 |

### NFR-5: Cost
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| NFR-5.1 | Log token counts for cost monitoring | SHOULD | PITFALLS #10 |
| NFR-5.2 | Cache embeddings by content hash | SHOULD | PITFALLS #10 |

## Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| C-1 | Python >=3.11,<3.14 | Type hints, dependency compatibility |
| C-2 | MCP SDK >=1.25.0 | Security, structured output |
| C-3 | Qdrant >=1.16.2 | Compression, hybrid search |
| C-4 | OpenAI text-embedding-3-small | Cost-effective, MTEB competitive |
| C-5 | Max chunk size 2000 tokens | Prevent context overflow |
| C-6 | Single-user context (no multi-tenant) | Claude Desktop use case |

## Out of Scope (Deferred)

| Item | Reason |
|------|--------|
| Custom embedding training | Over-engineering for marginal gains |
| Real-time document sync | Standards are stable; batch is sufficient |
| Multi-tenant isolation | Single-user Claude Desktop context |
| Contextual retrieval | Post-MVP iteration |
| Dual-granularity chunks | Post-MVP iteration |
| Cross-standard linking | Post-MVP iteration |

## Acceptance Criteria

### Migration Phase
- [ ] Code runs from new location `mcps/knowledge-mcp/`
- [ ] All existing tests pass
- [ ] Dependencies updated to required versions
- [ ] ChromaDB fallback tested

### Ingestion Phase
- [ ] PDFs ingest with clause structure preserved
- [ ] Tables remain intact (visual comparison)
- [ ] Metadata includes source, section, page

### Search Phase
- [ ] Semantic search returns relevant results
- [ ] Citations include standard name and clause
- [ ] Hybrid retrieval improves keyword queries

### Integration Phase
- [ ] specification-refiner can auto-query knowledge
- [ ] `/lookup-standard` command works
- [ ] Graceful degradation when MCP unavailable

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FR-1.1 | Phase 2 | Pending |
| FR-1.2 | Phase 2 | Pending |
| FR-1.3 | Phase 2 | Pending |
| FR-1.4 | Phase 2 | Pending |
| FR-1.5 | Phase 2 | Pending |
| FR-1.6 | Phase 2 | Pending |
| FR-2.1 | Phase 1 | Pending |
| FR-2.2 | Phase 1 | Pending |
| FR-2.3 | Phase 1 | Pending |
| FR-2.4 | Phase 1 | Pending |
| FR-2.5 | Phase 1 | Pending |
| FR-3.1 | Phase 3 | Pending |
| FR-3.2 | Phase 3 | Pending |
| FR-3.3 | Phase 3 | Pending |
| FR-3.4 | Phase 3 | Pending |
| FR-3.5 | Phase 3 | Pending |
| FR-3.6 | Phase 3 | Pending |
| FR-4.1 | Phase 3 | Pending |
| FR-4.2 | Phase 3 | Pending |
| FR-4.3 | Phase 3 | Pending |
| FR-4.4 | Phase 3 | Pending |
| FR-4.5 | Phase 3 | Pending |
| FR-5.1 | Phase 3 | Pending |
| FR-5.2 | Phase 3 | Pending |
| FR-5.3 | Phase 3 | Pending |
| FR-5.4 | Phase 3 | Pending |
| NFR-1.1 | Phase 1 | Pending |
| NFR-1.2 | Phase 1 | Pending |
| NFR-1.3 | Phase 1 | Pending |
| NFR-2.1 | Phase 4 | Pending |
| NFR-2.2 | Phase 4 | Pending |
| NFR-2.3 | Phase 2 | Pending |
| NFR-3.1 | Phase 1 | Pending |
| NFR-3.2 | Phase 1 | Pending |
| NFR-3.3 | Phase 1 | Pending |
| NFR-4.1 | Phase 1 | Pending |
| NFR-4.2 | Phase 2 | Pending |
| NFR-4.3 | Phase 1 | Pending |
| NFR-4.4 | Phase 2 | Pending |
| NFR-5.1 | Phase 4 | Pending |
| NFR-5.2 | Phase 4 | Pending |

---
*Requirements derived from research: 2026-01-23*
*Traceability added: 2026-01-23*