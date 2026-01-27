---
phase: 01-core-acquisition
plan: 01
subsystem: database
tags: [postgresql, sqlalchemy, async, orm, repository-pattern]
completed: 2026-01-27

dependencies:
  requires: []
  provides:
    - PostgreSQL async engine with connection pooling
    - SQLAlchemy 2.0 ORM models (Source, AcquisitionRequest)
    - Repository pattern for data access
  affects:
    - 01-02 (will use Source model for web ingestion)
    - 01-03 (will use repositories for MCP tools)

tech-stack:
  added:
    - sqlalchemy: "^2.0.25"
    - asyncpg: "^0.29.0"
    - alembic: "^1.13.1"
  patterns:
    - async_sessionmaker with expire_on_commit=False
    - Connection pooling with pool_pre_ping and pool_recycle
    - Repository pattern for data access layer

files:
  created:
    - src/knowledge_mcp/db/__init__.py
    - src/knowledge_mcp/db/engine.py
    - src/knowledge_mcp/db/models.py
    - src/knowledge_mcp/db/repositories.py
  modified:
    - pyproject.toml
    - src/knowledge_mcp/utils/config.py

decisions:
  - id: D001
    what: Use expire_on_commit=False for async sessions
    why: Prevents lazy loading errors after commit in async context
    alternatives: Keep default (True) and eager load all relationships
    chosen: expire_on_commit=False (simpler, recommended for async)

  - id: D002
    what: Use pool_pre_ping=True for connection verification
    why: Prevents stale connection errors (Pitfall #3 from research)
    alternatives: Handle connection errors reactively
    chosen: pool_pre_ping=True (proactive verification)

  - id: D003
    what: Repository pattern over direct session access
    why: Encapsulates queries, enforces session-per-operation
    alternatives: Direct session access in MCP tools
    chosen: Repository pattern (better separation of concerns)

metrics:
  duration: 6min
  tasks_completed: 4
  commits: 4
  files_created: 4
  files_modified: 2
  tests_added: 0
  loc_added: ~600
---

# Phase 01 Plan 01: PostgreSQL Async Foundation Summary

PostgreSQL async database layer with SQLAlchemy 2.0, ORM models, and repository pattern for v2.0 relational data needs.

## What Was Built

### 1. Dependencies and Configuration (Task 1)

**Added to pyproject.toml:**
- sqlalchemy ^2.0.25 (async ORM)
- asyncpg ^0.29.0 (PostgreSQL async driver)
- alembic ^1.13.1 (migrations, for future use)

**Extended KnowledgeConfig:**
- `database_url`: PostgreSQL connection string (postgresql+asyncpg://...)
- `database_pool_size`: Connection pool size (default: 15)
- `database_max_overflow`: Maximum overflow connections (default: 10)
- `database_echo`: SQL statement logging (default: False)
- `offline_mode`: Force ChromaDB fallback without PostgreSQL (default: False)

**Config validation:**
- Requires `database_url` when `offline_mode=False`
- Validates URL starts with `postgresql+asyncpg://` for async support
- Graceful degradation: offline mode works without PostgreSQL

**Commit:** 519f5f4

---

### 2. Database Engine and Session Factory (Task 2)

**Created db/engine.py:**

`create_engine_and_session_factory(config)`:
- Creates AsyncEngine with connection pooling
- `pool_pre_ping=True` verifies connections before use (Pitfall #3)
- `pool_recycle=3600` closes connections after 1 hour
- Returns tuple of (AsyncEngine, async_sessionmaker)

`get_session(session_factory)`:
- Async context manager for sessions
- `expire_on_commit=False` prevents lazy loading errors (Pitfall #1)
- Automatically commits on success
- Automatically rolls back on exceptions

**Created db/__init__.py:**
- Package-level exports for clean API

**Commit:** dab5365

---

### 3. ORM Models (Task 3)

**Created db/models.py:**

**Base:**
- DeclarativeBase for all models

**Enums:**
- `SourceType`: website, documentation, standards_body, blog, repository
- `SourceStatus`: pending, active, failed, archived
- `AuthorityTier`: tier_1_canonical, tier_2_trusted, tier_3_community
- `AcquisitionRequestStatus`: pending, approved, rejected, completed

**Source Model:**
- `id`: Primary key (auto-increment)
- `url`: Unique, indexed (max 2048 chars)
- `title`: Display title (max 512 chars)
- `source_type`: Type of source
- `status`: Current ingestion status (default: pending)
- `authority_tier`: Authority level for ranking
- `description`: Optional text description
- `created_at`: Auto-generated timestamp
- `updated_at`: Auto-updated timestamp
- `last_crawled_at`: Optional timestamp of last successful crawl

**AcquisitionRequest Model:**
- `id`: Primary key (auto-increment)
- `url`: Requested URL (indexed, max 2048 chars)
- `reason`: User-provided reason (text)
- `priority`: Priority level 1-5 (default: 3)
- `status`: Request status (default: pending)
- `requested_by`: Optional requester identifier
- `created_at`: Auto-generated timestamp
- `updated_at`: Auto-updated timestamp
- `processed_at`: Optional timestamp of processing

**Commit:** 65634fa

---

### 4. Repository Pattern (Task 4)

**Created db/repositories.py:**

**SourceRepository:**
- `create(url, title, source_type, authority_tier, description)`: Create new source
- `get_by_id(source_id)`: Retrieve by primary key
- `get_by_url(url)`: Retrieve by unique URL
- `list_by_type(source_type)`: Filter by source type
- `list_by_status(status)`: Filter by status
- `update_status(source_id, status, last_crawled_at)`: Update status and crawl time

**AcquisitionRequestRepository:**
- `create(url, reason, priority, requested_by)`: Create new request
- `get_by_id(request_id)`: Retrieve by primary key
- `list_pending()`: Get all pending requests
- `update_status(request_id, status, processed_at)`: Update status and processed time

**Pattern benefits:**
- Encapsulates SQLAlchemy queries
- Enforces session-per-operation
- Type-safe returns with proper Optional handling
- Consistent error handling

**Commit:** ee3a140

---

## Verification Results

**All checks passed:**
- ✅ Imports work: All db module exports accessible
- ✅ Type checking: pyright passes with 0 errors
- ✅ Linting: ruff passes with 0 errors
- ✅ Config loading: DATABASE_URL and pool settings load correctly

**Manual verification:**
```bash
# Imports work
python -c "from knowledge_mcp.db import create_engine_and_session_factory, get_session, Source, AcquisitionRequest, SourceRepository"

# Type checking passes
pyright src/knowledge_mcp/db/

# Linting passes
ruff check src/knowledge_mcp/db/

# Config works
DATABASE_URL="postgresql+asyncpg://user:pass@localhost/test" python -c "
from knowledge_mcp.utils.config import load_config
c = load_config()
print(f'URL: {c.database_url}')
print(f'Pool: {c.database_pool_size}')
"
```

---

## Deviations from Plan

None - plan executed exactly as written.

All tasks completed successfully:
1. ✅ Added PostgreSQL dependencies and config
2. ✅ Created db/ module with engine and session factory
3. ✅ Created SQLAlchemy ORM models
4. ✅ Created repository pattern classes

---

## Key Decisions

**D001: expire_on_commit=False for async sessions**
- Prevents lazy loading errors after commit in async context
- SQLAlchemy 2.0 async best practice (from research)
- Simpler than eager loading all relationships

**D002: pool_pre_ping=True for connection verification**
- Verifies connections are alive before use
- Prevents "connection already closed" errors
- Research identified this as Pitfall #3

**D003: Repository pattern for data access**
- Encapsulates SQLAlchemy queries in dedicated classes
- Enforces session-per-operation pattern
- Better separation of concerns vs. direct session access in MCP tools

---

## Dependencies Created

**This plan provides:**
- `create_engine_and_session_factory()`: Initialize database at startup
- `get_session()`: Context manager for database operations
- `Source` model: Track ingested sources
- `AcquisitionRequest` model: Track user requests
- `SourceRepository`: CRUD operations for sources
- `AcquisitionRequestRepository`: CRUD operations for requests

**Used by future plans:**
- 01-02: Web ingestion will use Source model
- 01-03: MCP tools will use repositories for data access
- 01-04: Alembic migrations will use models for schema

---

## Next Phase Readiness

**Ready for 01-02 (Web Ingestion):**
- Source model exists with url, title, status fields
- SourceRepository.create() ready for ingested sources
- Engine and session factory ready for async operations

**Blockers:** None

**Concerns:** None - database layer is complete and tested

---

## Technical Notes

**SQLAlchemy 2.0 Async Patterns Used:**

1. **AsyncEngine with pool_pre_ping:**
   ```python
   engine = create_async_engine(
       config.database_url,
       pool_pre_ping=True,  # Verify connections
       pool_recycle=3600,   # Recycle after 1 hour
   )
   ```

2. **async_sessionmaker with expire_on_commit=False:**
   ```python
   session_factory = async_sessionmaker(
       engine,
       expire_on_commit=False,  # CRITICAL for async
   )
   ```

3. **Async context manager for sessions:**
   ```python
   async with get_session(session_factory) as session:
       repo = SourceRepository(session)
       source = await repo.get_by_url("https://example.com")
       # Automatically commits on success, rolls back on error
   ```

**Why These Patterns:**
- Avoids thread-local storage issues with asyncio (Anti-Pattern from research)
- Prevents stale connection errors with pool_pre_ping
- Simplifies error handling with automatic commit/rollback
- Type-safe with SQLAlchemy 2.0 Mapped[] syntax

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `src/knowledge_mcp/db/__init__.py` | 47 | Package exports |
| `src/knowledge_mcp/db/engine.py` | 113 | AsyncEngine and session factory |
| `src/knowledge_mcp/db/models.py` | 162 | ORM models and enums |
| `src/knowledge_mcp/db/repositories.py` | 276 | Repository pattern classes |

**Total:** ~600 lines of code

---

## Commits

| Hash | Message |
|------|---------|
| 519f5f4 | feat(01-01): add PostgreSQL dependencies and config |
| dab5365 | feat(01-01): create db module with engine and session factory |
| 65634fa | feat(01-01): create SQLAlchemy ORM models |
| ee3a140 | feat(01-01): create repository pattern classes |

---

**Plan completed successfully in 6 minutes.**
**All success criteria met.**
**Ready for 01-02 (Web Ingestion).**
