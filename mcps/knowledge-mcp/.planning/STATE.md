# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-27)

**Core value:** The system learns from experience — when Claude uses a template and provides feedback, future recommendations improve based on what actually worked.
**Current focus:** Milestone v2.0 - Phase 1 Planning

## Current Position

Phase: 2 of 4 (Workflow Support)
Plan: 6 of 7 in phase
Status: **In Progress - Executing Phase 2 Plans**
Last activity: 2026-01-28 - Completed 02-06-PLAN.md (Plan Strategy + ProjectRepository)

Progress: [█████████░] 92% (11/12 plans complete total)

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
| Session per invocation | 01-06 | Create session for each tool call | Ensures proper lifecycle and prevents connection leaks |
| Offline mode errors | 01-06 | Return JSON errors when DB unavailable | Tools fail gracefully with clear error messages |
| check_robots parameter | 01-06 | Keep for API compatibility | Future enhancement, currently only URL validation |

**Phase 2 Execution Decisions:**

| Decision | Plan | Choice | Rationale |
|----------|------|--------|-----------|
| State machine pattern | 02-01 | STATE_TRANSITIONS dict + methods | Explicit valid transitions, prevents invalid state changes |
| Default status handling | 02-01 | insert_default + __init__ | Both SQLAlchemy INSERT and Python object creation need defaults |
| UUID primary keys | 02-01 | UUID for all project tables | Distributed system design, prevents ID collision |
| Cascade delete | 02-01 | ON DELETE CASCADE | Automatic cleanup of related records when project deleted |
| Strategy customization | 02-02 | Three methods: preprocess/rank/format | Separates concerns, enables focused workflow customization |
| Async preprocess | 02-02 | preprocess_query is async | Future-proofs for LLM-based query expansion |
| Composition pattern | 02-02 | WorkflowSearcher composes SemanticSearcher | Better separation, easier testing than inheritance |
| Error dict structure | 02-02 | {"error", "result_type": "error"} | MCP tools need JSON-serializable error responses |
| Default facets | 02-05 | 4 facets: definitions/examples/standards/best_practices | Comprehensive multi-perspective topic exploration |
| Facet ranking boosts | 02-05 | Type-specific (20%/15%/10%/10%) | Prioritize diverse content for exploration workflows |
| Uncategorized default | 02-05 | Default to best_practices facet | Ensures all results categorized in output |
| Type-safe facets | 02-05 | isinstance() + cast() pattern | Pass pyright strict mode with runtime validation |

### Completed This Session

- [x] Executed 02-01-PLAN.md (Project Capture Models)
  - Added Project, QueryHistory, Decision, DecisionSource models
  - Created migration 002 with CASCADE delete
  - 9 unit tests covering state machine behavior
- [x] Executed 02-02-PLAN.md (Strategy Pattern Foundation)
  - Created SearchStrategy ABC with three abstract methods
  - Built WorkflowSearcher orchestrator with template method pattern
  - 10 unit tests verifying strategy execution order
- [x] Executed 02-05-PLAN.md (Explore Strategy Implementation)
  - Implemented ExploreStrategy with 4 default facets
  - Facet-aware ranking with type-specific boosts
  - 16 unit tests covering all functionality
- [x] Executed 02-03-PLAN.md (RCCA Strategy Implementation)
  - Implemented RCCAStrategy for failure analysis workflow
  - RCCA metadata extraction (symptoms, root_cause, contributing_factors, resolution)
  - 18 unit and integration tests, 98% coverage for rcca.py

### Pending Todos

- [ ] Execute remaining Phase 2 plans (02-04 through 02-07)
- [ ] Phase 3-4 execution

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

Last session: 2026-01-28 13:37 UTC
Stopped at: Completed 02-05-PLAN.md (Explore Strategy Implementation)
Resume file: .planning/phases/02-workflow-support/02-05-SUMMARY.md
Next: Execute remaining Phase 2 plans
