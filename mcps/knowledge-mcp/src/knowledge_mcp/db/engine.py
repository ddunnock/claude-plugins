"""Database engine and session management for Knowledge MCP.

Provides async SQLAlchemy engine creation and session factory with proper
connection pooling and session lifecycle management.

Example:
    >>> from knowledge_mcp.utils.config import load_config
    >>> from knowledge_mcp.db.engine import create_engine_and_session_factory, get_session
    >>>
    >>> config = load_config()
    >>> engine, session_factory = create_engine_and_session_factory(config)
    >>>
    >>> async with get_session(session_factory) as session:
    ...     result = await session.execute(select(Source))
    ...     sources = result.scalars().all()
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncEngine

    from knowledge_mcp.utils.config import KnowledgeConfig


def create_engine_and_session_factory(
    config: KnowledgeConfig,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Create async engine and session factory.

    Call once at application startup to initialize the database connection pool.
    The engine manages a pool of connections that are reused across requests.

    Args:
        config: KnowledgeConfig with database_url and pool settings.

    Returns:
        Tuple of (AsyncEngine, async_sessionmaker) for creating sessions.

    Raises:
        ValueError: When database_url is invalid or missing.

    Example:
        >>> config = load_config()
        >>> engine, session_factory = create_engine_and_session_factory(config)
    """
    if not config.database_url:
        msg = "database_url is required in config"
        raise ValueError(msg)

    # Create async engine with connection pooling
    # pool_pre_ping=True verifies connections before use (Pitfall #3)
    # pool_recycle=3600 closes connections after 1 hour to avoid stale connections
    engine = create_async_engine(
        config.database_url,
        echo=config.database_echo,
        pool_size=config.database_pool_size,
        max_overflow=config.database_max_overflow,
        pool_pre_ping=True,  # Verify connections are alive
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    # Create session factory
    # expire_on_commit=False is CRITICAL for async (Pitfall #1)
    # Without this, accessing attributes after commit requires new queries
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    return engine, session_factory


@asynccontextmanager
async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions with proper cleanup.

    Automatically commits on success and rolls back on exceptions.
    Ensures sessions are properly closed to return connections to the pool.

    Args:
        session_factory: async_sessionmaker created by create_engine_and_session_factory.

    Yields:
        AsyncSession for database operations.

    Example:
        >>> async with get_session(session_factory) as session:
        ...     source = Source(url="https://example.com", title="Example")
        ...     session.add(source)
        ...     # Automatically committed when context exits successfully
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
