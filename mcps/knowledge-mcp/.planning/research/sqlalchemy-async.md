# SQLAlchemy 2.0 Async Patterns for Knowledge MCP v2.0

**Researched:** 2026-01-27
**Confidence:** HIGH (official documentation verified)
**Domain:** PostgreSQL integration with async SQLAlchemy

---

## Executive Summary

SQLAlchemy 2.0 provides mature async support via the `sqlalchemy.ext.asyncio` extension. For Knowledge MCP v2.0's PostgreSQL integration, use `asyncpg` as the database driver, `async_sessionmaker` for session management, and the new `Mapped[]`/`mapped_column()` type-safe model declarations. The async architecture requires careful attention to lazy loading (which is not supported) and session concurrency (one session per task).

**Key Recommendations:**
- Use `create_async_engine()` with `pool_pre_ping=True` for connection health
- Configure `expire_on_commit=False` to prevent detached object issues
- Use eager loading strategies (`selectinload`, `joinedload`) instead of lazy loading
- Initialize Alembic with `alembic init -t async` for async migration support
- Implement repository pattern with `AsyncSession` dependency injection

---

## 1. Async Architecture Overview

### 1.1 Core Components

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
```

| Component | Purpose |
|-----------|---------|
| `create_async_engine()` | Creates async engine with `AsyncAdaptedQueuePool` |
| `AsyncSession` | Async session for ORM operations |
| `async_sessionmaker` | Factory for creating `AsyncSession` instances |
| `AsyncAttrs` | Mixin enabling async attribute access |

### 1.2 Driver Selection

**Recommended: asyncpg**

```
postgresql+asyncpg://user:password@host:5432/database
```

asyncpg is purpose-built for asyncio with superior performance compared to other PostgreSQL drivers. It is the recommended driver for SQLAlchemy's async PostgreSQL backend.

**Note:** As of late 2024, asyncpg versions 0.29.0+ may have compatibility issues with `create_async_engine`. Pin to `asyncpg>=0.27.0,<0.29.0` if issues arise, though this may be resolved in newer SQLAlchemy versions.

---

## 2. Engine and Session Configuration

### 2.1 Engine Creation

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Production configuration
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost:5432/knowledge_mcp",
    pool_size=10,           # Base connections in pool
    max_overflow=5,         # Extra connections when pool exhausted
    pool_recycle=300,       # Recycle connections after 5 minutes
    pool_pre_ping=True,     # Test connections before checkout
    echo=False,             # Set True for SQL debugging
)

# Session factory - note expire_on_commit=False
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL for async
)
```

### 2.2 Why `expire_on_commit=False`

In async contexts, SQLAlchemy cannot perform implicit I/O when accessing attributes after commit. Without this setting, accessing any attribute on a committed object raises:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
```

Setting `expire_on_commit=False` keeps objects usable after commit without triggering lazy loads.

### 2.3 Connection Pool Recommendations

| Parameter | Recommended | Rationale |
|-----------|-------------|-----------|
| `pool_size` | 10 | Base concurrent connections; adjust per workload |
| `max_overflow` | 5 | Temporary connections for burst traffic |
| `pool_recycle` | 300 | Prevent stale connections (5 min) |
| `pool_pre_ping` | True | Detect disconnected connections before use |

**Important:** SQLAlchemy's async pool uses `AsyncAdaptedQueuePool`, not the standard `QueuePool`. Connection pooling is handled entirely by SQLAlchemy; do not use asyncpg's pool directly.

---

## 3. Session Context Manager Patterns

### 3.1 Basic Pattern

```python
async def get_project(project_id: str) -> dict:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if project:
            # Return data, not ORM object (detaches after context)
            return {"id": project.id, "name": project.name}
        return None
```

### 3.2 Transaction Pattern with Auto-Commit

```python
async def create_project(name: str) -> str:
    async with async_session_factory() as session:
        async with session.begin():  # Auto-commits on success
            project = Project(name=name)
            session.add(project)
            # Flush to get generated ID before commit
            await session.flush()
            return project.id
        # Auto-commits here if no exception
```

### 3.3 Dependency Injection Pattern (FastAPI-style)

```python
from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# Usage in route/handler
async def create_project_handler(
    name: str,
    session: AsyncSession = Depends(get_session)
) -> Project:
    project = Project(name=name)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project
```

### 3.4 Manual Transaction Control

```python
async def complex_operation(data: dict) -> bool:
    async with async_session_factory() as session:
        try:
            # Start transaction explicitly
            async with session.begin():
                # Multiple operations in single transaction
                project = Project(name=data["name"])
                session.add(project)
                await session.flush()

                feedback = Feedback(project_id=project.id, content=data["feedback"])
                session.add(feedback)

                # Commit happens automatically if no exception
            return True
        except Exception as e:
            # Transaction already rolled back
            logger.error(f"Operation failed: {e}")
            return False
```

---

## 4. Type-Safe Models with Mapped[] and mapped_column()

### 4.1 Base Class Setup

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models with async attribute support."""
    pass
```

### 4.2 Model Definitions

```python
from sqlalchemy import Enum as SQLEnum
import enum


class ProjectStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    # Primary key with UUID default
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Required string with max length
    name: Mapped[str] = mapped_column(String(255))

    # Optional field (nullable)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Enum field with default
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.DRAFT
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=datetime.utcnow,
        nullable=True
    )

    # Relationships with eager loading strategy
    feedback_items: Mapped[list["Feedback"]] = relationship(
        back_populates="project",
        lazy="selectin"  # Eager load by default
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name})>"


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    content: Mapped[str] = mapped_column(Text)
    score: Mapped[Optional[float]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Back-reference
    project: Mapped["Project"] = relationship(back_populates="feedback_items")
```

### 4.3 Type Annotation Rules

| Python Type | SQLAlchemy Behavior |
|-------------|---------------------|
| `Mapped[str]` | Required, NOT NULL |
| `Mapped[Optional[str]]` | Nullable |
| `Mapped[int]` | Integer, inferred |
| `Mapped[datetime]` | DateTime, inferred |
| `Mapped[UUID]` | UUID type |
| `Mapped[list["Related"]]` | One-to-many relationship |

**Important:** Use `Optional[T]` (or `T | None` in Python 3.10+) for nullable columns. The `Mapped[]` type hint determines nullability.

---

## 5. Repository Pattern Implementation

### 5.1 Generic Base Repository

```python
from typing import TypeVar, Generic, Optional, Sequence
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic async repository for CRUD operations."""

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by primary key."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[T]:
        """Get all entities with pagination."""
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        """Create new entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, id: UUID, **kwargs) -> Optional[T]:
        """Update entity by ID."""
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        return await self.get_by_id(id)

    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0
```

### 5.2 Domain-Specific Repository

```python
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project-specific operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)

    async def get_with_feedback(self, project_id: UUID) -> Optional[Project]:
        """Get project with feedback eagerly loaded."""
        result = await self.session.execute(
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.feedback_items))
        )
        return result.scalar_one_or_none()

    async def get_by_status(self, status: ProjectStatus) -> Sequence[Project]:
        """Get all projects with specific status."""
        result = await self.session.execute(
            select(Project).where(Project.status == status)
        )
        return result.scalars().all()

    async def get_project_with_feedback_count(
        self, project_id: UUID
    ) -> Optional[tuple[Project, int]]:
        """Get project with feedback count (avoiding N+1)."""
        result = await self.session.execute(
            select(Project, func.count(Feedback.id))
            .outerjoin(Feedback)
            .where(Project.id == project_id)
            .group_by(Project.id)
        )
        return result.one_or_none()
```

### 5.3 Unit of Work Pattern

```python
class UnitOfWork:
    """Unit of Work for transactional operations."""

    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        self.projects = ProjectRepository(self.session)
        self.feedback = FeedbackRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


# Usage
async def create_project_with_feedback(name: str, feedback_content: str):
    async with UnitOfWork(async_session_factory) as uow:
        project = await uow.projects.create(Project(name=name))
        feedback = await uow.feedback.create(
            Feedback(project_id=project.id, content=feedback_content)
        )
        await uow.commit()
        return project.id
```

---

## 6. Alembic Async Migration Setup

### 6.1 Initialize with Async Template

```bash
cd knowledge-mcp
alembic init -t async alembic
```

This creates:
```
alembic/
    env.py          # Async-configured environment
    script.py.mako  # Migration template
    versions/       # Migration files
alembic.ini         # Configuration
```

### 6.2 Configure alembic.ini

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

# Leave empty - set programmatically in env.py
sqlalchemy.url =
```

### 6.3 Configure env.py for Async

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your models' Base
from knowledge_mcp.models import Base
from knowledge_mcp.config import get_database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set URL from environment
config.set_main_option("sqlalchemy.url", get_database_url())

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using the provided connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 6.4 Running Migrations

```bash
# Create new migration (autogenerate from models)
alembic revision --autogenerate -m "add projects table"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### 6.5 Migration File Example

```python
"""add projects table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-01-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'completed', 'archived',
                                    name='projectstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_status', 'projects', ['status'])


def downgrade() -> None:
    op.drop_index('ix_projects_status', table_name='projects')
    op.drop_table('projects')
    op.execute("DROP TYPE projectstatus")
```

### 6.6 Data Migrations in Async Context

**Important:** Async `upgrade()` functions do not work. Use synchronous patterns:

```python
from sqlalchemy.orm import Session

def upgrade() -> None:
    # Schema changes
    op.add_column('projects', sa.Column('priority', sa.Integer(), nullable=True))

    # Data migration using sync session (works with async dialect)
    bind = op.get_bind()
    with Session(bind) as session:
        # Update existing rows
        session.execute(
            sa.text("UPDATE projects SET priority = 0 WHERE priority IS NULL")
        )
        session.commit()
```

---

## 7. Common Pitfalls and Solutions

### 7.1 Lazy Loading in Async Context

**Problem:** Accessing unloaded relationships raises `MissingGreenlet` exception.

```python
# BAD - triggers lazy load
project = await session.get(Project, project_id)
for feedback in project.feedback_items:  # FAILS!
    print(feedback.content)
```

**Solutions:**

1. **Use eager loading (recommended):**
```python
result = await session.execute(
    select(Project)
    .where(Project.id == project_id)
    .options(selectinload(Project.feedback_items))
)
project = result.scalar_one()
for feedback in project.feedback_items:  # OK
    print(feedback.content)
```

2. **Set lazy='selectin' on relationship:**
```python
feedback_items: Mapped[list["Feedback"]] = relationship(
    lazy="selectin"  # Always eager load
)
```

3. **Use lazy='raise' for explicit safety:**
```python
feedback_items: Mapped[list["Feedback"]] = relationship(
    lazy="raise"  # Raises exception if accessed without loading
)
```

4. **Use AsyncAttrs mixin for on-demand async loading:**
```python
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Then access with awaitable_attrs
feedback = await project.awaitable_attrs.feedback_items
```

### 7.2 Session Concurrency Issues

**Problem:** Using same `AsyncSession` across multiple tasks.

```python
# BAD - shared session across tasks
session = async_session_factory()

async def task1():
    await session.execute(...)  # Race condition!

async def task2():
    await session.execute(...)  # Race condition!

await asyncio.gather(task1(), task2())  # DANGEROUS
```

**Solution:** Create session per task.

```python
# GOOD - session per task
async def task1():
    async with async_session_factory() as session:
        await session.execute(...)

async def task2():
    async with async_session_factory() as session:
        await session.execute(...)

await asyncio.gather(task1(), task2())  # Safe
```

### 7.3 Detached Objects After Session Close

**Problem:** Accessing ORM objects after session context exits.

```python
# BAD - object detached after context
async def get_project(project_id: UUID) -> Project:
    async with async_session_factory() as session:
        project = await session.get(Project, project_id)
        return project  # Detached!

project = await get_project(uuid)
print(project.name)  # May fail or return stale data
```

**Solution:** Return data, not ORM objects; or keep session open.

```python
# GOOD - return data dict
async def get_project(project_id: UUID) -> dict | None:
    async with async_session_factory() as session:
        project = await session.get(Project, project_id)
        if project:
            return {
                "id": str(project.id),
                "name": project.name,
                "status": project.status.value,
            }
        return None
```

### 7.4 Greenlet Dependency Missing

**Problem:** `ModuleNotFoundError: No module named 'greenlet'`

**Solution:** Install with asyncio extra:
```bash
pip install "sqlalchemy[asyncio]"
# or
poetry add "sqlalchemy[asyncio]"
```

### 7.5 Connection Pool Exhaustion

**Problem:** `TimeoutError: QueuePool limit...` under load.

**Solution:** Increase pool size and ensure proper session cleanup.

```python
engine = create_async_engine(
    url,
    pool_size=20,      # Increase from default 5
    max_overflow=10,   # Allow burst connections
    pool_timeout=30,   # Wait longer before timeout
)

# Always use context managers
async with async_session_factory() as session:
    ...  # Session returned to pool on exit
```

### 7.6 Event Loop Already Running (Alembic)

**Problem:** `RuntimeError: This event loop is already running` when running migrations programmatically.

**Solution:** Handle existing loops in env.py:

```python
def run_migrations_online() -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # Already in async context
        loop.create_task(run_async_migrations())
    else:
        asyncio.run(run_async_migrations())
```

---

## 8. Testing Async SQLAlchemy

### 8.1 Test Configuration

```python
# conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from knowledge_mcp.models import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncSession:
    """Create test session with transaction rollback."""
    session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()
```

### 8.2 Test Examples

```python
import pytest
from uuid import uuid4

from knowledge_mcp.models import Project, ProjectStatus
from knowledge_mcp.repositories import ProjectRepository


@pytest.mark.asyncio
async def test_create_project(async_session):
    """Test project creation."""
    repo = ProjectRepository(async_session)

    project = Project(name="Test Project")
    created = await repo.create(project)

    assert created.id is not None
    assert created.name == "Test Project"
    assert created.status == ProjectStatus.DRAFT


@pytest.mark.asyncio
async def test_get_project_with_feedback(async_session):
    """Test eager loading of relationships."""
    repo = ProjectRepository(async_session)

    project = Project(name="Test")
    await repo.create(project)

    # Add feedback
    feedback = Feedback(project_id=project.id, content="Great!")
    async_session.add(feedback)
    await async_session.flush()

    # Fetch with eager loading
    loaded = await repo.get_with_feedback(project.id)

    assert loaded is not None
    assert len(loaded.feedback_items) == 1
    assert loaded.feedback_items[0].content == "Great!"
```

---

## 9. Recommended Dependencies

Add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
sqlalchemy = {version = "^2.0", extras = ["asyncio"]}
asyncpg = "^0.29"
alembic = "^1.13"
greenlet = "^3.0"  # Required for async

[tool.poetry.group.dev.dependencies]
pytest-asyncio = "^0.23"
```

---

## 10. Implementation Recommendations for Knowledge MCP v2.0

### 10.1 Module Structure

```
src/knowledge_mcp/
    db/
        __init__.py
        engine.py          # Engine and session factory
        base.py            # DeclarativeBase with AsyncAttrs
        models/
            __init__.py
            project.py     # Project model
            feedback.py    # Feedback model
            template.py    # Template model
        repositories/
            __init__.py
            base.py        # BaseRepository[T]
            project.py     # ProjectRepository
            feedback.py    # FeedbackRepository
        migrations/        # Alembic directory
            env.py
            versions/
```

### 10.2 Configuration Pattern

```python
# db/engine.py
from functools import lru_cache
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from knowledge_mcp.utils.config import Settings


@lru_cache
def get_engine():
    settings = Settings()
    return create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        echo=settings.debug,
    )


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )
```

### 10.3 Integration with Existing v1.0 Code

The async database layer should be independent of the existing Qdrant/ChromaDB vector stores. Both can coexist:

- **Vector operations** (search, embeddings): Use existing `VectorStore` interface
- **Relational operations** (projects, feedback, scores): Use new async PostgreSQL layer

This allows incremental adoption without disrupting working v1.0 functionality.

---

## Sources

- [SQLAlchemy 2.0 Asyncio Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [SQLAlchemy 2.0 Declarative Tables](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html)
- [SQLAlchemy 2.0 Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [Alembic 1.18 Cookbook - Async Migrations](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- [Alembic Async Template (GitHub)](https://github.com/sqlalchemy/alembic/blob/main/alembic/templates/async/env.py)
- [SQLAlchemy GitHub Discussions](https://github.com/sqlalchemy/sqlalchemy/discussions)
- [What's New in SQLAlchemy 2.0 - Miguel Grinberg](https://blog.miguelgrinberg.com/post/what-s-new-in-sqlalchemy-2-0)
- [Building High-Performance Async APIs with FastAPI, SQLAlchemy 2.0, and Asyncpg](https://leapcell.io/blog/building-high-performance-async-apis-with-fastapi-sqlalchemy-2-0-and-asyncpg)
- [Setup FastAPI Project with Async SQLAlchemy 2, Alembic, PostgreSQL](https://berkkaraal.com/blog/2024/09/19/setup-fastapi-project-with-async-sqlalchemy-2-alembic-postgresql-and-docker/)
