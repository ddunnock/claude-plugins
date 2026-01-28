# Knowledge MCP - v2.0 Learning Knowledge Management System

## What This Is

An MCP server that transforms from a semantic search tool into a **learning knowledge management system**. It provides:
1. Unified document and web content ingestion
2. Coverage assessment and knowledge acquisition
3. Workflow-specific retrieval (RCCA, Trade Studies, Exploration, Planning)
4. Project capture and outcome tracking
5. Feedback-driven learning that improves recommendations over time

## Core Value

The system learns from experience — when Claude uses a template and provides feedback on the outcome, future recommendations improve based on what actually worked.

## Milestone: v2.0 - Learning Knowledge Management

### Phase 1: Core + Acquisition
- Unified ingestion (PDF, DOCX, Web via Crawl4AI)
- Coverage assessment and gap detection
- Web content acquisition with relevance scoring
- Offline mode with ChromaDB sync

### Phase 2a: Workflow + Capture
- RCCA workflow support (similar failures, causal chains)
- Trade study support (criteria, alternatives, precedents)
- Exploration support (anti-patterns, gap analysis)
- Planning support (templates, precedents, risks)
- Project capture and outcome tracking

### Phase 2b: Feedback + Basic Scoring
- Three-tier feedback collection (implicit, quick, detailed)
- Simple effectiveness scoring
- Score-boosted search rankings

### Phase 3: Advanced + Admin
- Multi-factor scoring with propagation
- Relationship graph (causal, contradictory, supporting)
- Admin tools (health reports, analytics, refresh)

## Requirements

### From v1.0 (Complete)
- ✓ MCP server infrastructure (stdio transport, handlers)
- ✓ Docling document ingestion (PDF, DOCX, PPTX, XLSX, HTML)
- ✓ Hierarchical chunking with section awareness
- ✓ OpenAI embedding generation (text-embedding-3-small)
- ✓ Local embeddings (sentence-transformers)
- ✓ Qdrant vector storage with Qdrant Cloud
- ✓ ChromaDB fallback storage
- ✓ Semantic search with reranking
- ✓ CLI for document ingestion and verification
- ✓ 86% test coverage
- ✓ Pyright strict mode compliance

### v2.0 Active

**Phase 1 - Core + Acquisition**
- [ ] PostgreSQL integration (SQLAlchemy 2.0 async)
- [ ] Web ingestion via Crawl4AI
- [ ] Coverage assessment with gap detection
- [ ] Knowledge acquisition workflow
- [ ] Offline sync manager
- [ ] 8 MCP tools (search, stats, ingest, sources, assess, preflight, acquire, request)

**Phase 2a - Workflow + Capture**
- [ ] Project/Template data models with lifecycle
- [ ] RCCA workflow support tool
- [ ] Trade study support tool
- [ ] Exploration support tool
- [ ] Planning support tool (with capture operations)
- [ ] Pattern library for anti-pattern matching

**Phase 2b - Feedback + Scoring**
- [ ] Feedback collection (3-tier system)
- [ ] Simple effectiveness scoring
- [ ] Score-boosted search ranking
- [ ] Feedback MCP tool

**Phase 3 - Advanced + Admin**
- [ ] Multi-factor scoring with confidence
- [ ] Score propagation to templates
- [ ] Relationship graph storage
- [ ] Admin MCP tool
- [ ] Relationship MCP tool

### Out of Scope (v2.0)
- Multi-user access control — v3
- Real-time collaboration — v3
- Automated standard updates — v3
- Non-English content — v2.1
- External PM tool sync — v2.1

## Context

**v1.0 Complete:** Milestone v1.0 (Spec Compliance) completed 2026-01-27 with:
- Working MCP server with `knowledge_search` and `knowledge_stats` tools
- 86% test coverage (exceeds 80% threshold)
- Typer CLI with `knowledge ingest docs` and `knowledge verify` commands
- Local embeddings via sentence-transformers
- Result reranking (Cohere API + local cross-encoder)

**v2.0 Architecture Evolution:**
- v1: Qdrant/ChromaDB only (vectors)
- v2: Hybrid PostgreSQL + Qdrant (relational + vectors)
- v3 (future): Consolidated pgvector

**New Dependencies for v2:**
- PostgreSQL 16+
- SQLAlchemy 2.0 with asyncpg
- Alembic for migrations
- Crawl4AI for web ingestion

## Constraints

- **Python version**: ≥3.11,<3.14 — per CLAUDE.md specification
- **Type safety**: Pyright strict mode with zero errors
- **Test coverage**: ≥80% line coverage
- **API compatibility**: v1.0 tools must continue working
- **MCP Protocol**: v1.x compatibility

## Key Decisions

| Decision | Rationale | Status |
|----------|-----------|--------|
| PostgreSQL for relational data | ACID compliance, RLS for multi-tenancy path | Pending |
| SQLAlchemy 2.0 async | Modern async ORM with type hints | Pending |
| Hybrid architecture (v2) | Incremental migration, proven components | Pending |
| 15 consolidated tools | Balance capability vs. agent complexity | Pending |
| Three-tier feedback | Maximize collection, minimize friction | Pending |
| Project state machine | Prevent invalid lifecycle states | Pending |
| Score-boosted ranking | Combined semantic + effectiveness scoring | Pending |

## Success Criteria

| Criterion | Target | Phase |
|-----------|--------|-------|
| Web ingestion reliability | 100% | 1 |
| Coverage assessment accuracy | >0.75 correlation | 1 |
| Offline mode functional | 100% | 1 |
| Similar failure recall@5 | >0.70 | 2a |
| Project capture adoption | >5/month | 2a |
| Feedback collection rate | >60% per project | 2b |
| Score prediction accuracy | >0.6 correlation | 3 |
| Test coverage | ≥80% | All |

---
*Last updated: 2026-01-27 - Milestone v2.0 initiated*
