"""Integration tests for database layer.

These tests require a PostgreSQL database.
Set DATABASE_URL environment variable to run.

Example:
    DATABASE_URL=postgresql+asyncpg://user:pass@localhost/test_knowledge_mcp pytest tests/integration/test_database.py
"""

import os
from datetime import datetime

import pytest

# Skip all tests if DATABASE_URL not set
DATABASE_URL = os.getenv("DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL or not DATABASE_URL.startswith("postgresql"),
    reason="DATABASE_URL not set or not PostgreSQL",
)


@pytest.fixture(scope="module")
async def engine_and_session():
    """Create engine and session factory for tests."""
    from knowledge_mcp.db.engine import create_engine_and_session_factory
    from knowledge_mcp.utils.config import KnowledgeConfig

    config = KnowledgeConfig(
        database_url=DATABASE_URL,
        database_pool_size=5,
        database_max_overflow=5,
    )

    engine, session_factory = create_engine_and_session_factory(config)

    yield engine, session_factory

    await engine.dispose()


@pytest.fixture
async def session(engine_and_session):
    """Create a session for each test."""
    _, session_factory = engine_and_session

    async with session_factory() as session:
        yield session
        await session.rollback()  # Rollback after each test


class TestDatabaseConnection:
    """Test database connectivity."""

    @pytest.mark.asyncio
    async def test_connection_works(self, session) -> None:
        """Test basic database connection."""
        from sqlalchemy import text

        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_tables_exist(self, session) -> None:
        """Test that migration tables exist."""
        from sqlalchemy import text

        # Check sources table
        result = await session.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sources')"
            )
        )
        assert result.scalar() is True

        # Check acquisition_requests table
        result = await session.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'acquisition_requests')"
            )
        )
        assert result.scalar() is True


class TestSourceRepositoryIntegration:
    """Integration tests for SourceRepository."""

    @pytest.mark.asyncio
    async def test_create_and_get_source(self, session) -> None:
        """Test creating and retrieving a source."""
        from knowledge_mcp.db.models import AuthorityTier, SourceType
        from knowledge_mcp.db.repositories import SourceRepository

        repo = SourceRepository(session)

        # Create
        source = await repo.create(
            url=f"https://test-{datetime.utcnow().timestamp()}.com",
            source_type=SourceType.WEBSITE,
            title="Test Source",
            authority_tier=AuthorityTier.TIER_2_TRUSTED.value,
        )

        assert source.id is not None
        await session.flush()

        # Get by ID
        retrieved = await repo.get_by_id(source.id)
        assert retrieved is not None
        assert retrieved.title == "Test Source"

    @pytest.mark.asyncio
    async def test_get_by_url(self, session) -> None:
        """Test retrieving source by URL."""
        from knowledge_mcp.db.models import AuthorityTier, SourceType
        from knowledge_mcp.db.repositories import SourceRepository

        repo = SourceRepository(session)
        url = f"https://test-url-{datetime.utcnow().timestamp()}.com"

        # Create
        source = await repo.create(
            url=url,
            source_type=SourceType.DOCUMENTATION,
            title="Test by URL",
            authority_tier=AuthorityTier.TIER_1_CANONICAL.value,
        )
        await session.flush()

        # Get by URL
        retrieved = await repo.get_by_url(url)
        assert retrieved is not None
        assert retrieved.id == source.id
        assert retrieved.title == "Test by URL"

    @pytest.mark.asyncio
    async def test_unique_url_constraint(self, session) -> None:
        """Test that duplicate URLs are rejected."""
        from sqlalchemy.exc import IntegrityError

        from knowledge_mcp.db.models import SourceType
        from knowledge_mcp.db.repositories import SourceRepository

        repo = SourceRepository(session)
        url = f"https://unique-{datetime.utcnow().timestamp()}.com"

        # First create succeeds
        await repo.create(url=url, source_type=SourceType.WEBSITE, title="First", authority_tier="tier_2_trusted")
        await session.flush()

        # Second create should fail
        with pytest.raises(IntegrityError):
            await repo.create(url=url, source_type=SourceType.WEBSITE, title="Second", authority_tier="tier_2_trusted")
            await session.flush()

    @pytest.mark.asyncio
    async def test_list_by_type(self, session) -> None:
        """Test listing sources by type."""
        from knowledge_mcp.db.models import SourceType
        from knowledge_mcp.db.repositories import SourceRepository

        repo = SourceRepository(session)

        # Create sources of different types
        await repo.create(
            url=f"https://blog-{datetime.utcnow().timestamp()}.com",
            source_type=SourceType.BLOG,
            title="Blog",
            authority_tier="tier_3_community",
        )
        await repo.create(
            url=f"https://repo-{datetime.utcnow().timestamp()}.com",
            source_type=SourceType.REPOSITORY,
            title="Repo",
            authority_tier="tier_2_trusted",
        )
        await session.flush()

        # List by type
        blogs = await repo.list_by_type(SourceType.BLOG)
        assert any(s.title == "Blog" for s in blogs)

    @pytest.mark.asyncio
    async def test_list_by_status(self, session) -> None:
        """Test listing sources by status."""
        from knowledge_mcp.db.models import SourceStatus, SourceType
        from knowledge_mcp.db.repositories import SourceRepository

        repo = SourceRepository(session)

        # Create source
        source = await repo.create(
            url=f"https://status-{datetime.utcnow().timestamp()}.com",
            source_type=SourceType.WEBSITE,
            title="Status Test",
            authority_tier="tier_2_trusted",
        )
        await session.flush()

        # List by status
        pending = await repo.list_by_status(SourceStatus.PENDING)
        assert any(s.id == source.id for s in pending)

    @pytest.mark.asyncio
    async def test_update_status(self, session) -> None:
        """Test updating source status."""
        from knowledge_mcp.db.models import SourceStatus, SourceType
        from knowledge_mcp.db.repositories import SourceRepository

        repo = SourceRepository(session)

        # Create source
        source = await repo.create(
            url=f"https://update-{datetime.utcnow().timestamp()}.com",
            source_type=SourceType.WEBSITE,
            title="Update Test",
            authority_tier="tier_2_trusted",
        )
        await session.flush()

        # Update status
        crawl_time = datetime.utcnow()
        updated = await repo.update_status(
            source_id=source.id,
            status=SourceStatus.ACTIVE,
            last_crawled_at=crawl_time,
        )

        assert updated is not None
        assert updated.status == SourceStatus.ACTIVE
        assert updated.last_crawled_at is not None


class TestAcquisitionRequestRepositoryIntegration:
    """Integration tests for AcquisitionRequestRepository."""

    @pytest.mark.asyncio
    async def test_create_and_list_pending(self, session) -> None:
        """Test creating requests and listing pending."""
        from knowledge_mcp.db.repositories import AcquisitionRequestRepository

        repo = AcquisitionRequestRepository(session)

        # Create requests with different priorities
        await repo.create(
            url=f"https://low-{datetime.utcnow().timestamp()}.com",
            reason="Low priority",
            priority=1,
        )
        await repo.create(
            url=f"https://high-{datetime.utcnow().timestamp()}.com",
            reason="High priority",
            priority=10,
        )
        await session.flush()

        # List pending (should be ordered by priority desc)
        pending = await repo.list_pending()
        assert len(pending) >= 2

        # Check that we have our requests
        urls = [p.url for p in pending]
        assert any("low-" in url for url in urls)
        assert any("high-" in url for url in urls)

    @pytest.mark.asyncio
    async def test_create_and_get_request(self, session) -> None:
        """Test creating and retrieving request."""
        from knowledge_mcp.db.repositories import AcquisitionRequestRepository

        repo = AcquisitionRequestRepository(session)

        # Create
        request = await repo.create(
            url=f"https://request-{datetime.utcnow().timestamp()}.com",
            reason="Need this",
            priority=5,
            requested_by="test@example.com",
        )
        await session.flush()

        # Get by ID
        retrieved = await repo.get_by_id(request.id)
        assert retrieved is not None
        assert retrieved.reason == "Need this"
        assert retrieved.requested_by == "test@example.com"

    @pytest.mark.asyncio
    async def test_update_request_status(self, session) -> None:
        """Test updating request status."""
        from knowledge_mcp.db.models import AcquisitionRequestStatus
        from knowledge_mcp.db.repositories import AcquisitionRequestRepository

        repo = AcquisitionRequestRepository(session)

        # Create
        request = await repo.create(
            url=f"https://update-req-{datetime.utcnow().timestamp()}.com",
            reason="Update test",
        )
        await session.flush()

        # Update to completed
        processed_time = datetime.utcnow()
        updated = await repo.update_status(
            request_id=request.id,
            status=AcquisitionRequestStatus.COMPLETED,
            processed_at=processed_time,
        )

        assert updated is not None
        assert updated.status == AcquisitionRequestStatus.COMPLETED
        assert updated.processed_at is not None


class TestAlembicMigrations:
    """Test Alembic migrations."""

    @pytest.mark.asyncio
    async def test_current_revision(self, session) -> None:
        """Test that alembic_version table exists and has revision."""
        from sqlalchemy import text

        # Check alembic_version exists
        result = await session.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'alembic_version')"
            )
        )
        assert result.scalar() is True

        # Check version is set
        result = await session.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        assert version is not None
        assert len(version) > 0
