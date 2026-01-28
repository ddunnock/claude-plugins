# Roadmap: Knowledge MCP

## Overview

Knowledge MCP transforms from a semantic search tool (v1.0) into a **Learning Knowledge Management System** (v2.0) that ingests documents and web content, supports specialized workflows, captures project outcomes, and learns from feedback to improve recommendations.

## Current State

**v1.0 Complete** (2026-01-27): Working MCP server with 86% test coverage
- `knowledge_search` and `knowledge_stats` tools
- Typer CLI with `knowledge ingest docs` and `knowledge verify`
- Local embeddings + Cohere/local reranking

---

## Milestone: v2.0 - Learning Knowledge Management

**Goal:** Transform from semantic search into a learning system that improves recommendations based on usage feedback.

**Core Value:** The system learns from experience — when Claude uses a template and provides feedback, future recommendations improve based on what actually worked.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (1.1, 2.1): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Core + Acquisition** - PostgreSQL integration, web ingestion via Crawl4AI, coverage assessment
- [ ] **Phase 2: Workflow Support** - RCCA, trade study, exploration, and planning workflow tools
- [ ] **Phase 3: Feedback + Scoring** - Three-tier feedback collection, effectiveness scoring
- [ ] **Phase 4: Advanced Features** - Multi-factor scoring, relationship graph, admin tools

## Phase Details

### Phase 1: Core + Acquisition
**Goal**: PostgreSQL relational layer, web content ingestion, coverage assessment
**Depends on**: v1.0 complete
**Requirements**: FR-1.x (Core Search), FR-2.x (Content Acquisition)
**Research flag**: needs-research (SQLAlchemy async, Crawl4AI patterns)
**Success Criteria** (what must be TRUE):
  1. PostgreSQL connection with SQLAlchemy 2.0 async works
  2. Alembic migrations create all v2 tables successfully
  3. Crawl4AI ingests web pages with JavaScript rendering
  4. `knowledge_preflight` verifies URL accessibility and robots.txt
  5. `knowledge_assess` identifies coverage gaps
  6. Offline mode with ChromaDB sync functional
  7. Test coverage remains >= 80%
**New Components**:
  - `db/models.py` - SQLAlchemy ORM models
  - `db/repositories.py` - Repository pattern data access
  - `db/migrations/` - Alembic migration scripts
  - `ingest/web_ingestor.py` - Crawl4AI integration
  - `sync/offline.py` - Offline sync manager
**New MCP Tools** (6):
  - `knowledge_ingest` - Trigger document/web ingestion
  - `knowledge_sources` - List/filter sources
  - `knowledge_assess` - Coverage assessment
  - `knowledge_preflight` - URL accessibility check
  - `knowledge_acquire` - Acquire web content
  - `knowledge_request` - Track acquisition requests
**Plans**: 7 plans in 3 waves
  - [ ] 01-01-PLAN.md — PostgreSQL foundation (engine, models, repositories)
  - [ ] 01-02-PLAN.md — Web ingestion via Crawl4AI
  - [ ] 01-03-PLAN.md — Alembic migrations setup
  - [ ] 01-04-PLAN.md — Offline sync manager
  - [ ] 01-05-PLAN.md — Coverage assessment algorithm
  - [ ] 01-06-PLAN.md — MCP tools (6 new tools)
  - [ ] 01-07-PLAN.md — Database tests and coverage

### Phase 2: Workflow Support
**Goal**: Specialized retrieval for RCCA, trade studies, exploration, and planning workflows
**Depends on**: Phase 1 (PostgreSQL models)
**Requirements**: FR-3.x (Workflow Support)
**Research flag**: standard-patterns
**Success Criteria** (what must be TRUE):
  1. `knowledge_rcca` finds similar failures with causal chains
  2. `knowledge_trade` retrieves criteria, alternatives, and precedents
  3. `knowledge_explore` matches anti-patterns and identifies gaps
  4. `knowledge_plan` retrieves templates, risks, and precedents
  5. Project capture creates/updates project records with outcomes
  6. Project state machine enforces valid lifecycle transitions
  7. Test coverage remains >= 80%
**New Components**:
  - `search/workflow_rcca.py` - RCCA-specific retrieval
  - `search/workflow_trade.py` - Trade study retrieval
  - `search/workflow_explore.py` - Exploration retrieval
  - `search/workflow_plan.py` - Planning retrieval
  - `capture/project.py` - Project lifecycle management
  - `capture/template.py` - Template capture and tracking
**New MCP Tools** (4):
  - `knowledge_rcca` - RCCA workflow support
  - `knowledge_trade` - Trade study support
  - `knowledge_explore` - Exploration support
  - `knowledge_plan` - Planning + capture
**Plans**: 7 plans in 4 waves
  - [ ] 02-01-PLAN.md — Database models + migration (Project, QueryHistory, Decision)
  - [ ] 02-02-PLAN.md — Strategy pattern base (SearchStrategy ABC, WorkflowSearcher)
  - [ ] 02-03-PLAN.md — RCCA strategy implementation
  - [ ] 02-04-PLAN.md — Trade study strategy implementation
  - [ ] 02-05-PLAN.md — Explore strategy implementation
  - [ ] 02-06-PLAN.md — Plan strategy + ProjectRepository
  - [ ] 02-07-PLAN.md — MCP tools registration (4 new tools)

### Phase 3: Feedback + Scoring
**Goal**: Three-tier feedback collection, simple effectiveness scoring, score-boosted search
**Depends on**: Phase 2 (project capture)
**Requirements**: FR-4.x (Feedback & Learning)
**Research flag**: standard-patterns
**Success Criteria** (what must be TRUE):
  1. Implicit feedback (usage) tracked automatically
  2. Quick feedback (thumbs/stars) collected via `knowledge_feedback`
  3. Detailed feedback (outcomes) stored with project records
  4. Simple effectiveness scores calculated from feedback
  5. Search results boosted by effectiveness scores
  6. Score formula: combined = (semantic * 0.7) + (effectiveness * 0.3)
  7. Test coverage remains >= 80%
**New Components**:
  - `feedback/collector.py` - Three-tier feedback collection
  - `scoring/simple.py` - Simple effectiveness scoring
**New MCP Tools** (1):
  - `knowledge_feedback` - Collect effectiveness feedback
**Plans**: TBD

### Phase 4: Advanced Features
**Goal**: Multi-factor scoring, relationship graph, admin tools
**Depends on**: Phase 3 (feedback data)
**Requirements**: FR-5.x (Advanced Features)
**Research flag**: standard-patterns
**Success Criteria** (what must be TRUE):
  1. Multi-factor scoring combines recency, authority, relevance, effectiveness
  2. Confidence scores reflect sample size and consistency
  3. Relationship graph stores causal, supporting, contradictory links
  4. `knowledge_admin` provides health reports and analytics
  5. Source refresh management re-ingests stale content
  6. Test coverage remains >= 80%
**New Components**:
  - `scoring/advanced.py` - Multi-factor scoring with propagation
  - `graph/relationships.py` - Relationship graph storage
  - `admin/health.py` - Health reports and analytics
  - `admin/refresh.py` - Source refresh management
**New MCP Tools** (2):
  - `knowledge_relationships` - Relationship graph queries
  - `knowledge_admin` - Health reports, refresh
**Plans**: TBD

## Phase Ordering Rationale

1. **Phase 1 first**: PostgreSQL provides the foundation for all relational data (projects, feedback, scores). Web ingestion expands content sources. Both are prerequisites for later phases.

2. **Phase 2 before Phase 3**: Workflow tools create projects that generate feedback. Cannot collect feedback without projects to track.

3. **Phase 3 before Phase 4**: Simple scoring establishes the feedback loop. Advanced scoring and relationship graph build on top of this foundation.

4. **Phase 4 is optional enhancement**: Core learning functionality works after Phase 3. Phase 4 adds sophistication but isn't required for basic operation.

## Requirement Coverage

| Requirement | Description | Phase | Status |
|-------------|-------------|-------|--------|
| FR-1.1 | Semantic search with score boosting | 1 | Complete |
| FR-1.2 | Collection statistics | v1.0 | Complete |
| FR-1.3 | Source listing and filtering | 1 | Complete |
| FR-2.1 | Web content ingestion | 1 | Complete |
| FR-2.2 | Preflight URL checking | 1 | Complete |
| FR-2.3 | Document ingestion | v1.0 | Complete |
| FR-2.4 | Coverage assessment | 1 | Complete |
| FR-2.5 | Acquisition request tracking | 1 | Complete |
| FR-3.1 | RCCA workflow support | 2 | Complete |
| FR-3.2 | Trade study support | 2 | Complete |
| FR-3.3 | Exploration support | 2 | Complete |
| FR-3.4 | Planning support | 2 | Complete |
| FR-3.5 | Project capture | 2 | Complete |
| FR-4.1 | Implicit feedback | 3 | Pending |
| FR-4.2 | Quick feedback | 3 | Pending |
| FR-4.3 | Detailed feedback | 3 | Pending |
| FR-4.4 | Simple effectiveness scoring | 3 | Pending |
| FR-4.5 | Score-boosted search | 3 | Pending |
| FR-5.1 | Multi-factor scoring | 4 | Pending |
| FR-5.2 | Relationship graph | 4 | Pending |
| FR-5.3 | Admin health reports | 4 | Pending |
| FR-5.4 | Source refresh management | 4 | Pending |

**Coverage**: 22 requirements mapped across 4 phases

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core + Acquisition | 7/7 | Complete | 2026-01-28 |
| 2. Workflow Support | 7/7 | Complete | 2026-01-28 |
| 3. Feedback + Scoring | 0/TBD | Not Started | - |
| 4. Advanced Features | 0/TBD | Not Started | - |

---

## Completed: Milestone v1.0 - Spec Compliance

**Completed:** 2026-01-27

All 5 phases complete. Knowledge MCP v1.0 has:
- Working MCP server with `knowledge_search` and `knowledge_stats` tools
- 86% test coverage (exceeds 80% threshold)
- Typer CLI with `knowledge ingest docs` and `knowledge verify` commands
- Local embeddings via sentence-transformers (no OpenAI API key required)
- Result reranking (Cohere API + local cross-encoder fallback)

### v1.0 Phases (Complete)

| Phase | Description | Status |
|-------|-------------|--------|
| 1. Foundation Fixes | Fix tests, pyright errors | Complete |
| 2. Search Layer | Semantic search implementation | Complete |
| 3. MCP Tool Implementation | knowledge_search, knowledge_stats | Complete |
| 4. Test Coverage | Achieve 80% coverage | Complete (86%) |
| 5. Extended Features | CLI, local embeddings, reranking | Complete |

---

## Success Criteria Summary

| Criterion | Target | Phase |
|-----------|--------|-------|
| Web ingestion reliability | > 95% | 1 |
| Coverage assessment correlation | > 0.75 | 1 |
| Offline mode functional | 100% | 1 |
| Similar failure recall@5 | > 0.70 | 2 |
| Project capture adoption | > 5/month | 2 |
| Feedback collection rate | > 60% | 3 |
| Score prediction accuracy | > 0.6 | 4 |
| Test coverage | >= 80% | All |

---

*Roadmap updated 2026-01-27 with Phase 1 and Phase 2 plans.*
