"""Database module for Knowledge MCP v2.0.

Provides PostgreSQL async database layer with SQLAlchemy 2.0:
- AsyncEngine and session factory (engine.py)
- ORM models for sources and acquisition requests (models.py)
- Repository pattern for data access (repositories.py)

Example:
    >>> from knowledge_mcp.db import (
    ...     create_engine_and_session_factory,
    ...     get_session,
    ...     Source,
    ...     SourceRepository,
    ... )
    >>> from knowledge_mcp.utils.config import load_config
    >>>
    >>> config = load_config()
    >>> engine, session_factory = create_engine_and_session_factory(config)
    >>>
    >>> async with get_session(session_factory) as session:
    ...     repo = SourceRepository(session)
    ...     source = await repo.get_by_url("https://example.com")
"""

from __future__ import annotations

from knowledge_mcp.db.engine import create_engine_and_session_factory, get_session
from knowledge_mcp.db.models import (
    AcquisitionRequest,
    AcquisitionRequestStatus,
    AuthorityTier,
    Base,
    Project,
    ProjectStatus,
    Source,
    SourceStatus,
    SourceType,
)
from knowledge_mcp.db.repositories import (
    AcquisitionRequestRepository,
    ProjectRepository,
    SourceRepository,
)

__all__ = [
    "create_engine_and_session_factory",
    "get_session",
    "Base",
    "Source",
    "AcquisitionRequest",
    "Project",
    "SourceType",
    "SourceStatus",
    "AuthorityTier",
    "AcquisitionRequestStatus",
    "ProjectStatus",
    "SourceRepository",
    "AcquisitionRequestRepository",
    "ProjectRepository",
]
