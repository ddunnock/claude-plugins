# Requirements: Knowledge MCP v1.0

## Scope

Achieve full CLAUDE.md specification compliance for the Knowledge MCP server.

## v1 Requirements

### MCP Server (MCP)

| ID | Requirement | Priority | Phase |
|----|-------------|----------|-------|
| REQ-01 | Working MCP tool handlers (currently return "not implemented") | Must | 3 |

### Search (SEARCH)

| ID | Requirement | Priority | Phase |
|----|-------------|----------|-------|
| REQ-03 | Semantic search implementation | Must | 2 |
| REQ-04 | Hybrid search implementation | Should | 5 |
| REQ-05 | Result reranking | Should | 5 |

### Embedding (EMBED)

| ID | Requirement | Priority | Phase |
|----|-------------|----------|-------|
| REQ-02 | Local embedding support (offline/cost-free operation) | Should | 5 |

### Chunking (CHUNK)

| ID | Requirement | Priority | Phase |
|----|-------------|----------|-------|
| REQ-06 | Hierarchical chunking strategy | Should | 5 |
| REQ-07 | Semantic chunking strategy | Should | 5 |
| REQ-08 | Standards-aware chunking strategy | Should | 5 |

### CLI (CLI)

| ID | Requirement | Priority | Phase |
|----|-------------|----------|-------|
| REQ-09 | CLI for document ingestion | Should | 5 |
| REQ-10 | CLI for embedding verification | Should | 5 |

### Quality (QUAL)

| ID | Requirement | Priority | Phase |
|----|-------------|----------|-------|
| REQ-11 | 80% test coverage (currently 34%) | Must | 1, 4 |
| REQ-12 | Zero pyright errors (currently 55) | Must | 1 |
| REQ-13 | Verified Docling integration with real documents | Must | 1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-01 | Phase 3 | Complete |
| REQ-02 | Phase 5 | Pending |
| REQ-03 | Phase 2 | Complete |
| REQ-04 | Phase 5 | Pending |
| REQ-05 | Phase 5 | Pending |
| REQ-06 | Phase 5 | Pending |
| REQ-07 | Phase 5 | Pending |
| REQ-08 | Phase 5 | Pending |
| REQ-09 | Phase 5 | Pending |
| REQ-10 | Phase 5 | Pending |
| REQ-11 | Phase 1, 4 | Complete |
| REQ-12 | Phase 1 | Complete |
| REQ-13 | Phase 1 | Complete |

## Coverage Summary

- Total v1 requirements: 13
- Mapped to phases: 13
- Orphaned: 0

## Out of Scope (v2+)

- GUI/web interface - MCP protocol is the interface
- Multi-tenant support - single knowledge base per deployment
- Real-time document updates - batch ingestion workflow
- Custom training/fine-tuning - uses pre-trained models only
- Cross-reference awareness between documents

---

*Requirements extracted from PROJECT.md on 2026-01-20*
