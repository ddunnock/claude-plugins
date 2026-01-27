# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-27)

**Core value:** The system learns from experience — when Claude uses a template and provides feedback, future recommendations improve based on what actually worked.
**Current focus:** Milestone v2.0 - Phase 1 Planning

## Current Position

Phase: 1 of 4 (Core + Acquisition)
Plan: 6 of 7 in phase
Status: **In Progress - Executing Phase 1 Plans**
Last activity: 2026-01-27 - Completed 01-04-PLAN.md (Offline Sync Manager)

Progress: [████████░░] 86% (6/7 plans complete in phase)

## Performance Metrics

**v1.0 Velocity (for reference):**
- Total plans completed: 12
- Average duration: 4.8 min
- Total execution time: ~58 min

**v2.0 Estimated Scope:**
- Phase 1: Core + Acquisition (~6 new MCP tools, PostgreSQL, Crawl4AI)
- Phase 2: Workflow Support (~4 workflow tools, project capture)
- Phase 3: Feedback + Scoring (~1 tool, scoring system)
- Phase 4: Advanced Features (~2 tools, relationship graph)
- Total: 13 new MCP tools across 4 phases

*Updated after roadmap creation*

## Accumulated Context

### Decisions

Decisions logged in PROJECT.md Key Decisions table.
Decisions from v2 specification validated by research:

- [Validated]: PostgreSQL for relational data (ACID, RLS path to multi-tenancy)
- [Validated]: SQLAlchemy 2.0 async with type hints
- [Validated]: Hybrid architecture (PostgreSQL + Qdrant) for v2
- [Validated]: 15 consolidated MCP tools (13 new + 2 existing)
- [Validated]: Three-tier feedback collection
- [Validated]: Project state machine for lifecycle
- [Validated]: Score-boosted ranking (semantic * 0.7 + effectiveness * 0.3)
- [Validated]: Crawl4AI for web ingestion (v0.7.8+, async native)

**Phase 1 Execution Decisions:**

| Decision | Plan | Choice | Rationale |
|----------|------|--------|-----------|
| expire_on_commit | 01-01 | False (async safety) | Prevents lazy loading errors after commit in async context |
| pool_pre_ping | 01-01 | True (connection verification) | Prevents stale connection errors (Pitfall #3 from research) |
| Data access pattern | 01-01 | Repository pattern | Encapsulates queries, enforces session-per-operation |
| Crawl4AI version | 01-02 | Pin to ^0.7.8 instead of 0.8.0 | 0.7.8 is proven stable; 0.8.0 too new |
| Rate limiting | 01-02 | Sequential crawling in batch | Simple; Crawl4AI handles internal limits |
| Title extraction | 01-02 | Regex-based vs BeautifulSoup | Reduces dependencies; sufficient for <title> |
| Enum implementation | 01-03 | VARCHAR with CHECK constraints | Matches models.py native_enum=False; easier to modify |
| Initial migration | 01-03 | Manual creation vs autogenerate | Better control, explicit indexes, cleaner for review |
| Migration pooling | 01-03 | pool.NullPool | No pooling needed for one-off operations |
| Entropy weighting | 01-05 | 30% entropy in confidence | Balances similarity (50%), entropy (30%), count (20%) |
| Priority thresholds | 01-05 | HIGH: <0.3 sim OR >0.7 conf | Empirical thresholds for gap urgency classification |
| Type factory functions | 01-05 | _default_gaps()/_default_covered() | Resolve pyright type inference for dataclass fields |
| Offline sync scope | 01-04 | Metadata-only to ChromaDB | ChromaDB optimized for vectors, not relational data |
| Sync collection | 01-04 | Separate sources_metadata collection | Isolated from vector chunk storage |
| Client initialization | 01-04 | Lazy-load ChromaDB client | Avoids cost when PostgreSQL is online |
| Timestamp handling | 01-04 | datetime.now(UTC) vs utcnow() | Use timezone-aware timestamps (utcnow deprecated) |

### Completed This Session

- [x] Read v2 specification files (main + addendum)
- [x] Gap analysis: v1.0 codebase vs v2.0 requirements
- [x] Crawl4AI research: API patterns, rate limiting, robots.txt
- [x] Created REQUIREMENTS.md with 22 functional requirements
- [x] Created ROADMAP.md with 4 phases and success criteria
- [x] Executed 01-01-PLAN.md (PostgreSQL Async Foundation)
- [x] Executed 01-02-PLAN.md (Web Content Ingestion)
- [x] Executed 01-03-PLAN.md (Alembic Async Migrations)
- [x] Executed 01-04-PLAN.md (Offline Sync Manager)
- [x] Executed 01-05-PLAN.md (Coverage Assessment Algorithm)

### Pending Todos

- [ ] Execute remaining Phase 1 plans (01-06, 01-07)
- [ ] Phase 2-4 execution

### Blockers/Concerns

- **Resolved**: Crawl4AI integration patterns documented
- **Resolved**: SQLAlchemy 2.0 async session management (01-01 complete)
- **Resolved**: Alembic async migration patterns (01-03 complete)
- **Resolved**: PostgreSQL connection complexity (mitigated with pool_pre_ping and pool_recycle)

### Known Limitations (from v1.0)

- Docling GLYPH encoding issues with some PDF fonts
- Section hierarchy accumulates all headings (very long)
- Docling deprecation warning for TableItem.export_to_dataframe()
- Pre-existing pyright errors (113) from missing type stubs for external libraries
- Pre-existing ruff errors (468) primarily docstring formatting (D212)
- **New**: Crawl4AI lacks type stubs (causes pyright warnings, not errors)

## Session Continuity

Last session: 2026-01-27 21:01 UTC
Stopped at: Completed 01-04-PLAN.md (Offline Sync Manager)
Resume file: .planning/phases/01-core-acquisition/01-04-SUMMARY.md
Next: Execute remaining Phase 1 plans (01-06 through 01-07)
