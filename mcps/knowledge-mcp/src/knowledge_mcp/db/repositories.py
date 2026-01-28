"""Repository pattern for database access.

Provides repository classes for data access operations with proper
session management and query encapsulation.

Example:
    >>> from knowledge_mcp.db import get_session, SourceRepository
    >>>
    >>> async with get_session(session_factory) as session:
    ...     repo = SourceRepository(session)
    ...     source = await repo.get_by_url("https://example.com")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from knowledge_mcp.db.models import (
    AcquisitionRequest,
    AcquisitionRequestStatus,
    Project,
    ProjectStatus,
    Source,
    SourceStatus,
    SourceType,
)

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession


class SourceRepository:
    """Repository for Source model operations.

    Provides data access methods for Source entities with proper
    session management and type safety.

    Args:
        session: AsyncSession for database operations.

    Example:
        >>> async with get_session(session_factory) as session:
        ...     repo = SourceRepository(session)
        ...     sources = await repo.list_by_type(SourceType.WEBSITE)
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        self.session = session

    async def create(  # noqa: PLR0913
        self,
        url: str,
        title: str,
        source_type: SourceType,
        authority_tier: str,
        description: str | None = None,
    ) -> Source:
        """Create a new source.

        Args:
            url: Source URL (must be unique).
            title: Display title.
            source_type: Type of source.
            authority_tier: Authority tier for ranking.
            description: Optional description.

        Returns:
            Created Source instance.

        Example:
            >>> source = await repo.create(
            ...     url="https://example.com",
            ...     title="Example",
            ...     source_type=SourceType.WEBSITE,
            ...     authority_tier=AuthorityTier.TIER_2_TRUSTED,
            ... )
        """
        from knowledge_mcp.db.models import AuthorityTier

        source = Source(
            url=url,
            title=title,
            source_type=source_type,
            authority_tier=AuthorityTier(authority_tier),
            description=description,
        )
        self.session.add(source)
        await self.session.flush()
        return source

    async def get_by_id(self, source_id: int) -> Source | None:
        """Get source by ID.

        Args:
            source_id: Source ID.

        Returns:
            Source instance or None if not found.
        """
        return await self.session.get(Source, source_id)

    async def get_by_url(self, url: str) -> Source | None:
        """Get source by URL.

        Args:
            url: Source URL.

        Returns:
            Source instance or None if not found.
        """
        stmt = select(Source).where(Source.url == url)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_type(self, source_type: SourceType) -> list[Source]:
        """List sources by type.

        Args:
            source_type: Source type to filter by.

        Returns:
            List of Source instances.
        """
        stmt = select(Source).where(Source.source_type == source_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_status(self, status: SourceStatus) -> list[Source]:
        """List sources by status.

        Args:
            status: Source status to filter by.

        Returns:
            List of Source instances.
        """
        stmt = select(Source).where(Source.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self, source_id: int, status: SourceStatus, last_crawled_at: datetime | None = None
    ) -> Source | None:
        """Update source status.

        Args:
            source_id: Source ID.
            status: New status.
            last_crawled_at: Optional timestamp of last crawl.

        Returns:
            Updated Source instance or None if not found.
        """
        source = await self.get_by_id(source_id)
        if source:
            source.status = status
            if last_crawled_at:
                source.last_crawled_at = last_crawled_at
            await self.session.flush()
        return source


class AcquisitionRequestRepository:
    """Repository for AcquisitionRequest model operations.

    Provides data access methods for AcquisitionRequest entities with
    proper session management and type safety.

    Args:
        session: AsyncSession for database operations.

    Example:
        >>> async with get_session(session_factory) as session:
        ...     repo = AcquisitionRequestRepository(session)
        ...     pending = await repo.list_pending()
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        self.session = session

    async def create(
        self,
        url: str,
        reason: str,
        priority: int = 3,
        requested_by: str | None = None,
    ) -> AcquisitionRequest:
        """Create a new acquisition request.

        Args:
            url: Requested source URL.
            reason: Reason for request.
            priority: Priority level (1=highest, 5=lowest).
            requested_by: Optional identifier of requester.

        Returns:
            Created AcquisitionRequest instance.

        Example:
            >>> request = await repo.create(
            ...     url="https://example.com",
            ...     reason="Need this documentation",
            ...     priority=2,
            ... )
        """
        request = AcquisitionRequest(
            url=url,
            reason=reason,
            priority=priority,
            requested_by=requested_by,
        )
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_by_id(self, request_id: int) -> AcquisitionRequest | None:
        """Get acquisition request by ID.

        Args:
            request_id: Request ID.

        Returns:
            AcquisitionRequest instance or None if not found.
        """
        return await self.session.get(AcquisitionRequest, request_id)

    async def list_pending(self) -> list[AcquisitionRequest]:
        """List pending acquisition requests.

        Returns:
            List of pending AcquisitionRequest instances.
        """
        stmt = select(AcquisitionRequest).where(
            AcquisitionRequest.status == AcquisitionRequestStatus.PENDING
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        request_id: int,
        status: AcquisitionRequestStatus,
        processed_at: datetime | None = None,
    ) -> AcquisitionRequest | None:
        """Update acquisition request status.

        Args:
            request_id: Request ID.
            status: New status.
            processed_at: Optional timestamp of processing.

        Returns:
            Updated AcquisitionRequest instance or None if not found.
        """
        request = await self.get_by_id(request_id)
        if request:
            request.status = status
            if processed_at:
                request.processed_at = processed_at
            await self.session.flush()
        return request


class ProjectRepository:
    """Repository for Project model operations.

    Provides data access methods for Project entities with async CRUD
    and state machine validation.

    Args:
        session: AsyncSession for database operations.

    Example:
        >>> async with get_session(session_factory) as session:
        ...     repo = ProjectRepository(session)
        ...     project = await repo.create(name="My Project", domain="aerospace")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: AsyncSession for database operations.
        """
        self.session = session

    async def create(
        self,
        name: str,
        domain: str | None = None,
        applicable_standards: list[str] | None = None,
        description: str | None = None,
    ) -> Project:
        """Create a new project.

        Args:
            name: Project name.
            domain: Optional domain (e.g., "aerospace", "medical").
            applicable_standards: List of applicable standards.
            description: Optional project description.

        Returns:
            Created Project instance with PLANNING status.

        Example:
            >>> project = await repo.create(
            ...     name="Satellite Comm System",
            ...     domain="aerospace",
            ...     applicable_standards=["IEEE 15288", "DO-178C"],
            ... )
        """
        project = Project(
            name=name,
            domain=domain,
            applicable_standards=applicable_standards,
            description=description,
        )
        self.session.add(project)
        await self.session.flush()
        return project

    async def get_by_id(self, project_id: UUID) -> Project | None:
        """Get project by ID.

        Args:
            project_id: Project UUID.

        Returns:
            Project instance or None if not found.
        """
        return await self.session.get(Project, project_id)

    async def get_by_name(self, name: str) -> Project | None:
        """Get project by name.

        Args:
            name: Project name.

        Returns:
            Project instance or None if not found.
        """
        stmt = select(Project).where(Project.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(self) -> list[Project]:
        """List active projects.

        Returns only projects in PLANNING or ACTIVE status (not completed/abandoned).

        Returns:
            List of active Project instances.
        """
        stmt = select(Project).where(
            Project.status.in_([ProjectStatus.PLANNING, ProjectStatus.ACTIVE])
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, project: Project) -> Project:
        """Update an existing project.

        Args:
            project: Project instance with modified fields.

        Returns:
            Updated Project instance.

        Note:
            Caller must modify the project fields before calling this method.
            The session will track changes automatically.
        """
        await self.session.flush()
        return project

    async def transition_state(
        self,
        project_id: UUID,
        new_state: ProjectStatus,
    ) -> Project:
        """Transition project to a new state with validation.

        Args:
            project_id: Project UUID.
            new_state: Target status to transition to.

        Returns:
            Updated Project instance.

        Raises:
            ValueError: If project not found or transition is invalid.

        Example:
            >>> project = await repo.transition_state(
            ...     project_id=uuid4(),
            ...     new_state=ProjectStatus.ACTIVE,
            ... )
        """
        project = await self.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Use model's state machine validation
        project.transition_to(new_state)
        await self.session.flush()
        return project
