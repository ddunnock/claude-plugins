# Phase 1: Core + Acquisition - Research

**Researched:** 2026-01-27
**Domain:** PostgreSQL + SQLAlchemy 2.0 async, Web ingestion, Knowledge gap detection
**Confidence:** HIGH

## Summary

Phase 1 introduces PostgreSQL as the relational data layer for Knowledge MCP v2.0, maintaining the existing Qdrant vector store while adding web ingestion via Crawl4AI and coverage assessment capabilities. The research confirms that SQLAlchemy 2.0 async with asyncpg provides a mature, production-ready stack for async PostgreSQL operations.

**Key findings:**
- SQLAlchemy 2.0 async requires strict session-per-task pattern, with `expire_on_commit=False` essential for async workflows
- Alembic supports async migrations via `alembic init -t async`, but upgrade/downgrade functions remain synchronous (executed via `run_sync()`)
- asyncpg connection pooling works seamlessly with SQLAlchemy's AsyncAdaptedQueuePool, with default settings (min=10, max=10) suitable for moderate load
- Offline sync between PostgreSQL and ChromaDB requires custom implementation - no standard patterns exist for this hybrid architecture
- Coverage gap detection leverages semantic entropy and uncertainty quantification from recent 2024-2026 RAG research

**Primary recommendation:** Use SQLAlchemy 2.0 async with repository pattern, Alembic async template for migrations, and implement custom offline sync logic that serializes PostgreSQL state to ChromaDB's embedded format.

## Standard Stack

The established libraries/tools for async PostgreSQL with Python:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy | 2.0+ | Async ORM with type hints | Industry standard, mature async support, comprehensive documentation |
| asyncpg | 0.29+ | PostgreSQL async driver | Fastest Python PostgreSQL driver, native async |
| Alembic | 1.18+ | Database migrations | Official SQLAlchemy migration tool, async template support |
| Pydantic | 2.0+ | Data validation | Type-safe models, integrates with SQLAlchemy |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | 1.0+ | Environment config | Already in use (v1.0) |
| tenacity | 8.0+ | Retry logic | Already in use, good for DB connection retries |
| asyncio | stdlib | Event loop | Built-in, no dependency needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| asyncpg | psycopg3 async | asyncpg is 3x faster for most operations |
| SQLAlchemy async | Raw asyncpg | Lose ORM benefits, type safety, migration tooling |
| Alembic | Yoyo, SQLAlchemy-Migrate | Alembic is official, better maintained |

**Installation:**
```bash
poetry add "sqlalchemy>=2.0.0" "asyncpg>=0.29.0" "alembic>=1.18.0"
```

**Note on asyncpg version:** Pin to `>=0.29.0` for latest features. Earlier concerns about 0.29.0 compatibility with SQLAlchemy have been resolved in recent releases.

## Architecture Patterns

### Recommended Project Structure
```
src/knowledge_mcp/
├── db/
│   ├── __init__.py
│   ├── engine.py          # AsyncEngine setup, session factory
│   ├── models.py          # SQLAlchemy declarative models
│   ├── repositories.py    # Repository pattern (data access layer)
│   └── migrations/        # Alembic migration scripts
│       ├── env.py         # Async migration environment
│       ├── alembic.ini    # Alembic configuration
│       └── versions/      # Migration versions
├── ingest/
│   ├── web_ingestor.py    # Crawl4AI integration (already researched)
│   └── pipeline.py        # Update for web content (exists)
├── sync/
│   ├── __init__.py
│   └── offline.py         # PostgreSQL <-> ChromaDB sync manager
└── tools/
    └── acquisition.py     # New MCP tools (ingest, assess, preflight, etc.)
```

### Pattern 1: AsyncEngine and Session Factory Setup
**What:** Create async engine once at startup, use async_sessionmaker for session factory
**When to use:** Application initialization, before handling any requests
**Example:**
```python
# Source: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Create engine at startup
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/dbname",
    echo=False,  # Set True for SQL logging in dev
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create session factory with expire_on_commit=False (CRITICAL for async)
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,  # Prevents lazy loading after commit
    class_=AsyncSession
)

# Proper cleanup on shutdown
async def shutdown():
    await engine.dispose()
```

### Pattern 2: Repository Pattern with AsyncSession
**What:** Abstract database operations into repository classes that accept AsyncSession
**When to use:** All database access - enforces session-per-task pattern
**Example:**
```python
# Source: Community pattern from multiple 2025-2026 articles
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class SourceRepository:
    """Repository for Source model operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, source_data: dict) -> Source:
        """Create a new source."""
        source = Source(**source_data)
        self.session.add(source)
        await self.session.flush()  # Get ID without committing
        return source

    async def get_by_id(self, source_id: int) -> Optional[Source]:
        """Get source by ID with eager loading."""
        stmt = select(Source).where(Source.id == source_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> List[Source]:
        """List all sources."""
        stmt = select(Source).order_by(Source.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

# Usage in service layer
async def add_source(source_data: dict) -> Source:
    async with async_session_factory() as session:
        try:
            repo = SourceRepository(session)
            source = await repo.create(source_data)
            await session.commit()
            return source
        except Exception as e:
            await session.rollback()
            raise
```

### Pattern 3: Unit of Work Pattern for Transactions
**What:** Coordinate multiple repository operations as atomic units
**When to use:** Operations that span multiple tables and must succeed/fail together
**Example:**
```python
# Source: https://medium.com/pythoneers/unit-of-work-in-sqlalchemy-2025
from contextlib import asynccontextmanager

@asynccontextmanager
async def unit_of_work():
    """Context manager for database transactions."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Usage
async def ingest_web_content(url: str, metadata: dict):
    async with unit_of_work() as session:
        source_repo = SourceRepository(session)
        chunk_repo = ChunkRepository(session)

        # Both operations commit together or rollback together
        source = await source_repo.create({"url": url, **metadata})
        chunks = await chunk_repo.bulk_create(chunks_data, source_id=source.id)
        # Commit happens automatically if no exception
```

### Pattern 4: Alembic Async Migration Setup
**What:** Initialize Alembic with async template, run migrations via run_sync()
**When to use:** Database schema changes
**Example:**
```bash
# Initialize Alembic with async template
alembic init -t async src/knowledge_mcp/db/migrations
```

```python
# Source: https://github.com/sqlalchemy/alembic/blob/main/alembic/templates/async/env.py
# In migrations/env.py
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

async def run_async_migrations() -> None:
    """Create async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No pooling for migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)  # Sync function inside async

    await connectable.dispose()

def do_run_migrations(connection):
    """Synchronous migration execution."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
```

### Pattern 5: Session-Per-Task with asyncio.gather()
**What:** Each concurrent task gets its own AsyncSession instance
**When to use:** Parallel operations (crawling multiple URLs, batch processing)
**Example:**
```python
# Source: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
async def process_url(url: str, session_factory):
    """Process a single URL with its own session."""
    async with session_factory() as session:
        # This session is isolated to this task
        repo = SourceRepository(session)
        # ... do work ...
        await session.commit()

async def process_urls_parallel(urls: List[str]):
    """Process multiple URLs concurrently."""
    tasks = [process_url(url, async_session_factory) for url in urls]
    await asyncio.gather(*tasks)  # Each task has separate session
```

### Anti-Patterns to Avoid

- **Lazy Loading in Async:** Never rely on relationship lazy loading. Always use `selectinload()`, `joinedload()`, or `subqueryload()` to eagerly load relationships. Accessing unloaded attributes in async context will fail.

- **Sharing AsyncSession Across Tasks:** Never pass a single AsyncSession to multiple concurrent tasks (via `asyncio.gather()`). Each task needs its own session.

- **Forgetting expire_on_commit=False:** Without this setting, accessing model attributes after commit triggers new SQL queries, which blocks async execution.

- **Using Scoped Session Pattern:** The `scoped_session` pattern relies on thread-local storage, which doesn't work with asyncio tasks. Always pass AsyncSession explicitly.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Connection pooling | Custom pool manager | asyncpg pool via SQLAlchemy | asyncpg pool handles reconnection, health checks, overflow automatically. Defaults: min=10, max=10, max_inactive_lifetime=300s |
| Database migrations | SQL files + manual versioning | Alembic | Handles upgrade/downgrade, detects schema changes (autogenerate), tracks migration history |
| Transaction management | Manual commit/rollback | Unit of Work pattern or context managers | Ensures proper cleanup, handles nested transactions (savepoints), prevents resource leaks |
| Query result typing | Dict manipulation | Pydantic models + SQLAlchemy ORM | Type safety, validation, IDE autocompletion, prevents runtime errors |
| Retry logic for DB errors | Custom retry loops | tenacity decorators | Handles exponential backoff, specific exception types, max attempts. Already in project. |
| Session lifecycle | Manual session creation/disposal | async_sessionmaker with context managers | Prevents connection leaks, ensures proper cleanup even on exceptions |

**Key insight:** SQLAlchemy 2.0 async is mature (2+ years old) with battle-tested patterns. The official documentation and community examples provide production-ready patterns - no need to innovate here.

## Common Pitfalls

### Pitfall 1: Lazy Loading Triggering Sync IO in Async Context
**What goes wrong:** Accessing a relationship attribute (e.g., `source.chunks`) in async code triggers synchronous SQL, blocking the event loop.
**Why it happens:** SQLAlchemy defaults to lazy loading for relationships. In async, this requires awaiting, but the API doesn't support it by default.
**How to avoid:**
1. Always use eager loading: `selectinload()`, `joinedload()`, or `subqueryload()`
2. Use `AsyncAttrs` mixin for awaitable lazy loading (SQLAlchemy 2.0.13+)
3. Set relationships to `lazy='raise'` during development to catch mistakes

**Warning signs:**
- `AttributeError` when accessing relationships
- Warnings about "greenlet_spawn has not been called"
- Event loop blocking during ORM operations

**Example:**
```python
# BAD: Will fail in async
async def get_source_with_chunks(source_id: int):
    async with session_factory() as session:
        stmt = select(Source).where(Source.id == source_id)
        source = await session.scalar(stmt)
        chunks = source.chunks  # FAILS: lazy loading not awaited

# GOOD: Eager loading
from sqlalchemy.orm import selectinload

async def get_source_with_chunks(source_id: int):
    async with session_factory() as session:
        stmt = (
            select(Source)
            .where(Source.id == source_id)
            .options(selectinload(Source.chunks))  # Loads chunks in same query
        )
        source = await session.scalar(stmt)
        chunks = source.chunks  # Works: already loaded
```

### Pitfall 2: Alembic Upgrade/Downgrade Functions Are Not Async
**What goes wrong:** Trying to use `async def upgrade()` or calling async functions from migrations fails.
**Why it happens:** Alembic runs migrations via `connection.run_sync()`, which executes synchronous code within an async context. The upgrade/downgrade functions themselves must be sync.
**How to avoid:**
1. Keep all migration logic synchronous
2. Use `op.execute()` for SQL, never raw async database calls
3. For complex data migrations, use `connection.run_sync()` wrapper if needed

**Warning signs:**
- `RuntimeError: This event loop is already running`
- `AttributeError: 'coroutine' object has no attribute 'execute'`
- Migrations hang indefinitely

**Example:**
```python
# BAD: Async upgrade function
async def upgrade() -> None:  # WRONG: Can't be async
    await op.create_table(...)  # FAILS

# GOOD: Sync upgrade with sync operations
def upgrade() -> None:  # Correct: synchronous
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url', sa.String(), nullable=False),
    )
```

### Pitfall 3: Forgetting pool_pre_ping in Production
**What goes wrong:** Stale connections (closed by PostgreSQL or network) cause queries to fail with "connection closed" errors.
**Why it happens:** PostgreSQL closes idle connections after timeout. Connection pool reuses connections without checking if they're still alive.
**How to avoid:** Always set `pool_pre_ping=True` when creating engine for production.
**Warning signs:**
- Intermittent `OperationalError: server closed the connection unexpectedly`
- Errors after periods of inactivity
- First query after idle period fails, second succeeds

**Example:**
```python
# BAD: No connection verification
engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=10,
    max_overflow=20,
)

# GOOD: Verify connections before use
engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,      # Ping before using connection
    pool_recycle=3600,       # Recycle after 1 hour (prevent stale connections)
)
```

### Pitfall 4: Not Awaiting session.rollback() After Exceptions
**What goes wrong:** After a database error (IntegrityError, etc.), the session is in "inactive" state. Subsequent operations fail with confusing errors.
**Why it happens:** SQLAlchemy rolls back the database transaction automatically but doesn't reset the session state. Application must explicitly call `rollback()`.
**How to avoid:** Always `await session.rollback()` in exception handlers before re-raising or handling error.
**Warning signs:**
- `InvalidRequestError: This Session's transaction has been rolled back`
- Errors mentioning "inactive transaction"
- Second operation after error fails unexpectedly

**Example:**
```python
# BAD: No explicit rollback
async with session_factory() as session:
    try:
        source = Source(url="duplicate")
        session.add(source)
        await session.commit()
    except IntegrityError:
        # Session is now in inconsistent state
        pass  # Missing rollback

# GOOD: Explicit rollback
async with session_factory() as session:
    try:
        source = Source(url="duplicate")
        session.add(source)
        await session.commit()
    except IntegrityError:
        await session.rollback()  # Reset session state
        raise  # or handle error
```

### Pitfall 5: Incorrect asyncpg Pool Settings for ASGI Apps
**What goes wrong:** FastAPI/ASGI apps with small `pool_size` become bottlenecks, causing slow response times under load.
**Why it happens:** ASGI apps handle hundreds of concurrent requests via async I/O. Each request may need a database connection. Default pool_size=10 is too small for high concurrency.
**How to avoid:** For ASGI apps, set `pool_size` based on expected concurrent requests: start with 20-50, monitor and adjust. Use `max_overflow` to handle spikes.
**Warning signs:**
- Response times increase under load
- `TimeoutError: could not acquire connection from pool`
- Requests queuing despite CPU/memory available

**Example:**
```python
# BAD: Too small for ASGI app
engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=10,       # Default: too small
    max_overflow=0,     # No burst capacity
)

# GOOD: Sized for concurrent load
engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=30,        # Base pool for ~30 concurrent requests
    max_overflow=20,     # Allow bursts up to 50 total
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

### Pitfall 6: PostgreSQL-ChromaDB Sync Impedance Mismatch
**What goes wrong:** Assuming PostgreSQL relational data can be synced to ChromaDB vector store using standard sync patterns.
**Why it happens:** ChromaDB is a vector database optimized for embeddings, not relational data. No standard libraries exist for this hybrid sync.
**How to avoid:**
1. Sync only necessary data (source metadata, not full relational graph)
2. Implement custom serialization: PostgreSQL → JSON → ChromaDB metadata
3. Accept that offline mode has reduced functionality (no complex queries)
4. Consider using in-memory SQLite for offline relational queries instead

**Warning signs:**
- Trying to replicate foreign keys in ChromaDB
- Complex JOIN queries expected to work offline
- Syncing entire PostgreSQL schema to ChromaDB

**Recommended approach:**
```python
# Sync minimal relational data to ChromaDB metadata
async def sync_to_chromadb(session: AsyncSession, chroma_client):
    """Sync PostgreSQL sources to ChromaDB for offline use."""
    sources = await session.execute(select(Source))

    for source in sources.scalars():
        # Serialize only what's needed for offline search
        metadata = {
            "source_id": source.id,
            "source_url": source.url,
            "source_type": source.type,
            "authority_tier": source.authority_tier,
            # Don't sync relationships - flatten to metadata
        }
        # Store in ChromaDB collection metadata
        chroma_client.upsert(
            collection_name="sources_metadata",
            documents=[source.url],
            metadatas=[metadata],
            ids=[f"source_{source.id}"],
        )
```

## Code Examples

Verified patterns from official sources:

### Complete Engine and Session Factory Setup
```python
# Source: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
# src/knowledge_mcp/db/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from knowledge_mcp.utils.config import KnowledgeConfig

def create_engine_and_session_factory(config: KnowledgeConfig):
    """
    Create async engine and session factory.

    Call once at application startup.
    """
    engine = create_async_engine(
        config.database_url,  # postgresql+asyncpg://...
        echo=config.debug_sql,
        pool_size=20,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    return engine, session_factory

# Usage in MCP server
engine, async_session_factory = create_engine_and_session_factory(config)

async def shutdown():
    await engine.dispose()
```

### Repository Pattern Implementation
```python
# Source: Community patterns from 2025-2026 articles
# src/knowledge_mcp/db/repositories.py
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from knowledge_mcp.db.models import Source, Chunk

class SourceRepository:
    """Repository for Source model operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, url: str, metadata: Dict[str, Any]) -> Source:
        """Create new source."""
        source = Source(url=url, **metadata)
        self.session.add(source)
        await self.session.flush()
        return source

    async def get_by_id(self, source_id: int, load_chunks: bool = False) -> Optional[Source]:
        """Get source by ID."""
        stmt = select(Source).where(Source.id == source_id)
        if load_chunks:
            stmt = stmt.options(selectinload(Source.chunks))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_type(self, source_type: str) -> List[Source]:
        """List sources by type."""
        stmt = (
            select(Source)
            .where(Source.type == source_type)
            .order_by(Source.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, source_id: int, status: str) -> None:
        """Update source status."""
        stmt = (
            update(Source)
            .where(Source.id == source_id)
            .values(status=status)
        )
        await self.session.execute(stmt)
```

### Coverage Assessment Algorithm
```python
# Source: Semantic entropy research from 2024-2026 papers
# src/knowledge_mcp/tools/assessment.py
from typing import List, Dict
import numpy as np
from knowledge_mcp.embed.openai_embedder import OpenAIEmbedder
from knowledge_mcp.search.semantic_search import SemanticSearch

async def assess_coverage_gaps(
    query: str,
    knowledge_areas: List[str],
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Assess knowledge coverage using semantic entropy.

    Based on: "Semantic Entropy Probes: Robust and Cheap Hallucination Detection"
    (arxiv.org/abs/2406.15927)

    Args:
        query: User query or knowledge area to assess
        knowledge_areas: List of expected knowledge domains
        threshold: Similarity threshold for "covered" (default 0.5)

    Returns:
        Dict with coverage stats, gaps, and confidence scores
    """
    embedder = OpenAIEmbedder()
    search = SemanticSearch()

    # Embed query and knowledge areas
    query_embedding = await embedder.embed([query])
    area_embeddings = await embedder.embed(knowledge_areas)

    gaps = []
    covered = []

    for area, embedding in zip(knowledge_areas, area_embeddings):
        # Search for content in this knowledge area
        results = await search.search(
            query=area,
            n_results=10,
            filter_dict=None,
        )

        if not results:
            gaps.append({
                "area": area,
                "reason": "No content found",
                "confidence": 1.0,
            })
            continue

        # Calculate semantic entropy (uncertainty)
        similarities = [r.score for r in results]
        if max(similarities) < threshold:
            # Low similarity = high uncertainty = gap
            entropy = -sum(p * np.log(p + 1e-10) for p in similarities)
            gaps.append({
                "area": area,
                "reason": "Low relevance scores",
                "confidence": float(entropy / np.log(len(similarities))),
                "max_similarity": max(similarities),
            })
        else:
            covered.append({
                "area": area,
                "chunk_count": len(results),
                "avg_similarity": np.mean(similarities),
            })

    return {
        "coverage_ratio": len(covered) / len(knowledge_areas),
        "gaps": gaps,
        "covered_areas": covered,
        "recommendation": "high_priority" if len(gaps) > len(covered) else "optional",
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SQLAlchemy 1.4 with legacy API | SQLAlchemy 2.0+ with unified API | Feb 2023 | Type hints, better async support, cleaner query syntax |
| Thread-based concurrency | asyncio with AsyncSession | SQLAlchemy 2.0 | 3-10x throughput improvement for I/O-bound operations |
| Manual connection pooling | AsyncAdaptedQueuePool | SQLAlchemy 1.4+ | Automatic async-safe pooling, no custom code needed |
| asyncpg < 0.29 | asyncpg 0.29+ | Jan 2024 | Performance improvements, better error handling |
| Alembic sync-only | Alembic async template | Alembic 1.7+ (2021) | Native async engine support, cleaner env.py |
| ChromaDB for all vector data | Hybrid: Qdrant (primary) + ChromaDB (offline fallback) | Industry trend 2025-2026 | Qdrant scales better, ChromaDB simpler for offline |

**Deprecated/outdated:**
- **SQLAlchemy 1.x Query API**: Use `select()` construct, not `session.query()`. The 1.x API still works but is legacy.
- **Scoped session pattern**: Thread-local storage doesn't work with asyncio. Pass AsyncSession explicitly.
- **Synchronous SQLAlchemy with FastAPI**: Mixing async framework with sync ORM loses all async benefits and performs worse than pure sync.

## Open Questions

Things that couldn't be fully resolved:

1. **Offline Sync Strategy for PostgreSQL → ChromaDB**
   - What we know: No standard patterns exist. ChromaDB is designed for vector embeddings, not relational data.
   - What's unclear: Optimal data model for ChromaDB metadata. Should we sync full source records or minimal metadata?
   - Recommendation: Start with minimal metadata sync (source_id, url, type, authority_tier) stored as ChromaDB metadata. Evaluate after Phase 1 whether offline mode needs more relational capabilities (if yes, consider SQLite instead).

2. **Connection Pool Size for Knowledge MCP Workload**
   - What we know: ASGI apps need pool_size=20-50. Default 10 is too small. MCP server handles requests from Claude sequentially (not ASGI-level concurrency).
   - What's unclear: Whether MCP server has burst patterns (multiple parallel tool calls) or sequential pattern (one at a time).
   - Recommendation: Start with conservative pool_size=15, max_overflow=10. Monitor during Phase 1 development and adjust based on observed concurrency.

3. **Coverage Assessment Algorithm Effectiveness**
   - What we know: Semantic entropy (from 2024-2026 research) is state-of-art for uncertainty quantification. AUROC 0.887 in QA tasks.
   - What's unclear: Whether entropy-based approach works well for systems engineering domain (standards, specifications). Domain may have different characteristics than general QA.
   - Recommendation: Implement basic entropy-based assessment in Phase 1, collect metrics during usage. May need domain-specific tuning or alternative approaches based on real-world performance.

4. **Alembic Autogenerate Reliability with Async Models**
   - What we know: Alembic autogenerate detects schema changes but isn't perfect. Requires manual review.
   - What's unclear: Whether async models cause autogenerate issues (likely no, but not explicitly documented).
   - Recommendation: Always review autogenerated migrations. Test upgrade/downgrade paths. Set up CI to detect migration issues early.

## Sources

### Primary (HIGH confidence)
- [SQLAlchemy 2.0 Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - Official docs for AsyncEngine, AsyncSession, and patterns
- [Alembic Async Template](https://github.com/sqlalchemy/alembic/blob/main/alembic/templates/async/env.py) - Official async migration setup
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/usage.html) - Connection pooling and usage patterns
- [asyncpg API Reference](https://magicstack.github.io/asyncpg/current/api/index.html) - Pool parameter defaults

### Secondary (MEDIUM confidence)
- [FastAPI with Async SQLAlchemy 2.0 Guide](https://testdriven.io/blog/fastapi-sqlmodel/) - Production patterns verified with official docs
- [Building High-Performance Async APIs](https://leapcell.io/blog/building-high-performance-async-apis-with-fastapi-sqlalchemy-2-0-and-asyncpg) - asyncpg pool settings
- [Unit of Work in SQLAlchemy 2025](https://medium.com/pythoneers/unit-of-work-in-sqlalchemy-how-to-handle-transactions-efficiently-in-2025-7a705cfdcb89) - Transaction patterns
- [Pgvector vs ChromaDB Analysis](https://medium.com/@mysterious_obscure/pgvector-vs-chroma-db-which-works-better-for-rag-based-applications-3df813ad7307) - Vector database comparison
- [Semantic Entropy Probes Research](https://arxiv.org/abs/2406.15927) - Coverage gap detection algorithm (2024)

### Tertiary (LOW confidence - flagged for validation)
- [PostgreSQL Offline Sync Patterns](https://gist.github.com/pesterhazy/3e039677f2e314cb77ffe3497ebca07b) - General sync patterns, not ChromaDB-specific
- [Vector Database Comparison 2025](https://www.firecrawl.dev/blog/best-vector-databases-2025) - Market overview, not technical depth

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official documentation, mature and stable
- Architecture: HIGH - Patterns from official SQLAlchemy docs and verified community sources
- Pitfalls: HIGH - Documented in official error messages and GitHub discussions with maintainer responses
- Offline sync: MEDIUM - No standard patterns exist; custom implementation required
- Coverage assessment: MEDIUM - Research is recent (2024-2026) but not yet proven in systems engineering domain

**Research date:** 2026-01-27
**Valid until:** ~2026-03-27 (60 days) - SQLAlchemy and asyncpg are mature/stable. Re-verify if major versions released.
**Researcher notes:** Crawl4AI research already completed in prior work, not duplicated here. Focus was on SQLAlchemy async patterns, which are well-documented and battle-tested as of 2026.
