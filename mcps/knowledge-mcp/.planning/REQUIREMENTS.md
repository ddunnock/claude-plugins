# Knowledge MCP v2.0 Requirements

**Version:** 2.0.0
**Created:** 2026-01-27
**Status:** Draft (Pending validation)
**Source:** knowledge-mcp-v2-specification.md, knowledge-mcp-v2-spec-addendum.md

---

## 1. Overview

Transform Knowledge MCP from a semantic search tool into a **Learning Knowledge Management System** that:
1. Ingests documents and web content
2. Assesses coverage and identifies gaps
3. Supports specialized workflows (RCCA, Trade Studies, Exploration, Planning)
4. Captures project outcomes and tracks template usage
5. Learns from feedback to improve recommendations

### 1.1 Core Value Proposition

The system learns from experience — when Claude uses a template and provides feedback on the outcome, future recommendations improve based on what actually worked.

### 1.2 Scope

| In Scope (v2.0) | Out of Scope |
|-----------------|--------------|
| PostgreSQL relational layer | Multi-user access control (v3) |
| Web ingestion via Crawl4AI | Real-time collaboration (v3) |
| Workflow-specific retrieval | Automated standard updates (v3) |
| Three-tier feedback collection | Non-English content (v2.1) |
| Simple effectiveness scoring | External PM tool sync (v2.1) |
| Offline mode with sync | pgvector consolidation (v3) |

---

## 2. Functional Requirements

### 2.1 Core Search (Phase 1)

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-1.1 | Semantic search with score boosting | P1 | Search results include authority-weighted scoring |
| FR-1.2 | Collection statistics | P1 | Return chunk counts, source counts, freshness stats |
| FR-1.3 | Source listing and filtering | P1 | Filter sources by type, authority tier, status |
| FR-1.4 | Multi-collection support | P2 | Query across multiple Qdrant collections |

### 2.2 Content Acquisition (Phase 1)

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-2.1 | Web content ingestion | P1 | Crawl URLs with JavaScript rendering |
| FR-2.2 | Preflight URL checking | P1 | Verify accessibility, robots.txt compliance |
| FR-2.3 | Document ingestion (PDF, DOCX) | P1 | Maintain v1.0 ingestion capabilities |
| FR-2.4 | Coverage assessment | P1 | Identify gaps in knowledge coverage |
| FR-2.5 | Acquisition request tracking | P2 | Track pending content requests |

### 2.3 Workflow Support (Phase 2a)

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-3.1 | RCCA workflow support | P1 | Find similar failures, causal chains |
| FR-3.2 | Trade study support | P1 | Find criteria, alternatives, precedents |
| FR-3.3 | Exploration support | P1 | Anti-pattern matching, gap analysis |
| FR-3.4 | Planning support | P1 | Template retrieval, risk identification |
| FR-3.5 | Project capture | P1 | Create/update projects with outcomes |

### 2.4 Feedback & Learning (Phase 2b)

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-4.1 | Implicit feedback (usage tracking) | P1 | Track retrieval and usage automatically |
| FR-4.2 | Quick feedback (ratings) | P1 | 1-5 star or thumbs up/down |
| FR-4.3 | Detailed feedback (outcomes) | P2 | Project success, lessons learned |
| FR-4.4 | Simple effectiveness scoring | P1 | Calculate chunk effectiveness from feedback |
| FR-4.5 | Score-boosted search | P1 | Apply effectiveness scores to rankings |

### 2.5 Advanced Features (Phase 3)

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-5.1 | Multi-factor scoring | P2 | Combine recency, authority, relevance, effectiveness |
| FR-5.2 | Relationship graph | P2 | Store causal, supporting, contradictory relationships |
| FR-5.3 | Admin health reports | P2 | Source freshness, usage analytics |
| FR-5.4 | Source refresh management | P3 | Re-ingest stale sources |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1.1 | Search latency (p95) | < 500ms | Timer on search endpoint |
| NFR-1.2 | Web ingestion throughput | 3 concurrent URLs | Rate limit config |
| NFR-1.3 | Embedding generation | < 2s per chunk | Timer on embed endpoint |
| NFR-1.4 | Database query latency | < 100ms | PostgreSQL query stats |

### 3.2 Reliability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-2.1 | Web ingestion success rate | > 95% | Success/failure ratio |
| NFR-2.2 | Offline mode availability | 100% | ChromaDB fallback works |
| NFR-2.3 | Data integrity | Zero corruption | Foreign key constraints |
| NFR-2.4 | Graceful degradation | Required | Fallback when services unavailable |

### 3.3 Quality

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-3.1 | Test coverage | >= 80% | pytest-cov |
| NFR-3.2 | Type safety | Zero pyright errors | pyright --strict |
| NFR-3.3 | Code style | Zero ruff errors | ruff check |
| NFR-3.4 | API compatibility | v1.0 tools unchanged | Integration tests |

### 3.4 Security (v2.0 Foundation, v3 Full Implementation)

| ID | Requirement | Target | Phase |
|----|-------------|--------|-------|
| NFR-4.1 | PostgreSQL RLS enabled | Ready for v3 | v2.0 |
| NFR-4.2 | Tenant context management | Session-based | v2.0 |
| NFR-4.3 | Multi-tenant isolation | Database-enforced | v3.0 |

---

## 4. MCP Tool Requirements

### 4.1 Tool Inventory

| Tool | Category | Phase | Operations |
|------|----------|-------|------------|
| `knowledge_search` | Core | v1.0 DONE | Semantic search with filters |
| `knowledge_stats` | Core | v1.0 DONE | Collection statistics |
| `knowledge_ingest` | Core | P1 | Trigger document/web ingestion |
| `knowledge_sources` | Core | P1 | List/filter sources |
| `knowledge_assess` | Acquisition | P1 | Coverage assessment |
| `knowledge_preflight` | Acquisition | P1 | URL accessibility check |
| `knowledge_acquire` | Acquisition | P1 | Acquire web content |
| `knowledge_request` | Acquisition | P1 | Track acquisition requests |
| `knowledge_rcca` | Workflow | P2a | RCCA workflow support |
| `knowledge_trade` | Workflow | P2a | Trade study support |
| `knowledge_explore` | Workflow | P2a | Exploration support |
| `knowledge_plan` | Workflow | P2a | Planning + capture |
| `knowledge_feedback` | Feedback | P2b | Collect effectiveness feedback |
| `knowledge_relationships` | Graph | P3 | Relationship queries |
| `knowledge_admin` | Admin | P3 | Health reports, refresh |

### 4.2 Tool Schemas

All tools must provide:
- Complete JSON Schema with `inputSchema`
- Comprehensive `description` for agent guidance
- Structured error responses with `isError: true`

---

## 5. Data Model Requirements

### 5.1 PostgreSQL Tables (New)

| Table | Purpose | Key Relationships |
|-------|---------|-------------------|
| `organizations` | Tenant isolation | Parent of users |
| `users` | User identity | Belongs to org |
| `sources` | Document/web metadata | References chunks |
| `projects` | Project records | Has template, feedback |
| `templates` | Project templates | Abstracted from projects |
| `feedback` | Three-tier feedback | Links artifact + project |
| `scores` | Effectiveness scores | Per-chunk scoring |
| `relationships` | Knowledge graph | Chunk-to-chunk links |
| `acquisition_requests` | Pending acquisitions | Workflow tracking |

### 5.2 Qdrant Collections (Existing + Extended)

| Collection | Content | New Fields |
|------------|---------|------------|
| `chunks` | Document vectors | `source_url`, `authority_score`, `freshness_date` |
| `patterns` | Anti-pattern vectors | (existing) |
| `templates` | Template vectors | (existing) |

### 5.3 Data Integrity

- PostgreSQL foreign keys enforce referential integrity
- Chunk IDs in PostgreSQL reference Qdrant UUIDs
- Transactions span PostgreSQL only (hybrid limitation)
- ChromaDB sync maintains offline copy of chunks

---

## 6. Integration Requirements

### 6.1 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| SQLAlchemy | ^2.0.25 | Async ORM |
| asyncpg | ^0.29.0 | PostgreSQL driver |
| Alembic | ^1.13.1 | Migrations |
| Crawl4AI | ^0.7.8 | Web ingestion |
| networkx | ^3.2.1 | Graph analysis (optional) |

### 6.2 External Services

| Service | Required | Fallback |
|---------|----------|----------|
| PostgreSQL 16+ | Yes (v2.0) | None |
| Qdrant Cloud | Yes | ChromaDB |
| OpenAI API | Yes | Local embeddings |
| Cohere API | Optional | Local cross-encoder |

### 6.3 Configuration

All new configuration via environment variables:
- `POSTGRES_URL` - PostgreSQL connection string
- `CRAWL4AI_MAX_CONCURRENT` - Web crawl concurrency
- `CRAWL4AI_RESPECT_ROBOTS` - robots.txt compliance
- `SCORING_ENABLED` - Enable effectiveness scoring
- `OFFLINE_MODE` - Force ChromaDB fallback

---

## 7. Success Criteria

| Criterion | Target | Phase | Measurement |
|-----------|--------|-------|-------------|
| Web ingestion reliability | > 95% | P1 | Success ratio |
| Coverage assessment correlation | > 0.75 | P1 | Gap prediction accuracy |
| Offline mode functional | 100% | P1 | All tools work offline |
| Similar failure recall@5 | > 0.70 | P2a | Retrieval evaluation |
| Project capture adoption | > 5/month | P2a | Usage metrics |
| Feedback collection rate | > 60% | P2b | Feedback per project |
| Score prediction accuracy | > 0.6 | P3 | Correlation coefficient |
| Test coverage | >= 80% | All | pytest-cov |

---

## 8. Constraints

### 8.1 Technical Constraints

- Python >=3.11, <3.14
- Pyright strict mode with zero errors
- MCP Protocol v1.x compatibility
- v1.0 API backward compatibility (no breaking changes)

### 8.2 Operational Constraints

- PostgreSQL required for v2.0 (new dependency)
- Playwright browsers required for Crawl4AI (~500MB)
- Memory requirements increase for parallel web crawling

### 8.3 Phase Boundaries

- Phase 1 delivers standalone value (search + acquisition)
- Phase 2a depends on Phase 1 PostgreSQL models
- Phase 2b depends on Phase 2a project capture
- Phase 3 depends on Phase 2b scoring data

---

## 9. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| PostgreSQL connection issues | High | Medium | Connection pooling, health checks |
| Crawl4AI reliability | Medium | Medium | Retry logic, preflight checks |
| Score accuracy with sparse data | Medium | High | Start simple, require min samples |
| Tool count overwhelming agents | Medium | Medium | Consolidate tools, usage guidance |
| Test coverage regression | Medium | Low | Maintain 80% throughout |

---

## 10. v1.0 Requirements (Complete)

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-01 | Working MCP tool handlers | DONE |
| REQ-02 | Local embedding support | DONE |
| REQ-03 | Semantic search implementation | DONE |
| REQ-05 | Result reranking | DONE |
| REQ-06 | Hierarchical chunking | DONE |
| REQ-08 | Standards-aware chunking | DONE |
| REQ-09 | CLI for document ingestion | DONE |
| REQ-10 | CLI for embedding verification | DONE |
| REQ-11 | 80% test coverage | DONE (86%) |
| REQ-12 | Zero pyright errors | DONE |
| REQ-13 | Verified Docling integration | DONE |

---

## 11. Traceability

| Requirement Source | Location |
|-------------------|----------|
| v2 Main Specification | `mcps/tmp/unified-knowledge-upgrade/knowledge-mcp-v2-specification.md` |
| v2 Addendum | `mcps/tmp/unified-knowledge-upgrade/knowledge-mcp-v2-spec-addendum.md` |
| Gap Analysis | `.planning/research/gap-analysis.md` |
| Crawl4AI Research | `.planning/research/crawl4ai.md` |
| v1.0 Research Summary | `.planning/research/SUMMARY.md` |

---

*Requirements validated against v2 specifications. Ready for roadmap creation.*
