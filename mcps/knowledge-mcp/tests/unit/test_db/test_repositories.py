"""Unit tests for database repositories."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from knowledge_mcp.db.models import (
    AcquisitionRequest,
    AcquisitionRequestStatus,
    AuthorityTier,
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


class TestSourceRepository:
    """Tests for SourceRepository."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Create mock async session."""
        session = MagicMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.execute = AsyncMock()
        session.get = AsyncMock()
        return session

    @pytest.fixture
    def repo(self, mock_session: MagicMock) -> SourceRepository:
        """Create repository with mock session."""
        return SourceRepository(mock_session)

    @pytest.mark.asyncio
    async def test_create_source(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test creating a new source."""
        source = await repo.create(
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Test",
            authority_tier=AuthorityTier.TIER_2_TRUSTED.value,
        )

        assert source.url == "https://example.com"
        assert source.title == "Test"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_source_with_description(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test creating source with optional description."""
        source = await repo.create(
            url="https://example.com",
            source_type=SourceType.DOCUMENTATION,
            title="Test Docs",
            authority_tier=AuthorityTier.TIER_1_CANONICAL.value,
            description="Test description",
        )

        assert source.description == "Test description"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test getting source by ID when it exists."""
        mock_source = Source(
            id=1,
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Test",
            authority_tier=AuthorityTier.TIER_2_TRUSTED,
        )
        mock_session.get.return_value = mock_source

        source = await repo.get_by_id(1)

        assert source is not None
        assert source.id == 1
        mock_session.get.assert_awaited_once_with(Source, 1)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test getting source by ID when it doesn't exist."""
        mock_session.get.return_value = None

        source = await repo.get_by_id(999)

        assert source is None
        mock_session.get.assert_awaited_once_with(Source, 999)

    @pytest.mark.asyncio
    async def test_get_by_url(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test getting source by URL."""
        mock_source = Source(
            id=1,
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Test",
            authority_tier=AuthorityTier.TIER_2_TRUSTED,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_source
        mock_session.execute.return_value = mock_result

        source = await repo.get_by_url("https://example.com")

        assert source is not None
        assert source.url == "https://example.com"
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_by_url_not_found(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test getting source by URL when it doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        source = await repo.get_by_url("https://nonexistent.com")

        assert source is None

    @pytest.mark.asyncio
    async def test_list_by_type(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test listing sources by type."""
        mock_sources = [
            Source(
                id=1,
                url="https://a.com",
                source_type=SourceType.WEBSITE,
                title="A",
                authority_tier=AuthorityTier.TIER_2_TRUSTED,
            ),
            Source(
                id=2,
                url="https://b.com",
                source_type=SourceType.WEBSITE,
                title="B",
                authority_tier=AuthorityTier.TIER_2_TRUSTED,
            ),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_sources
        mock_session.execute.return_value = mock_result

        sources = await repo.list_by_type(SourceType.WEBSITE)

        assert len(sources) == 2
        assert all(s.source_type == SourceType.WEBSITE for s in sources)
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_list_by_status(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test listing sources by status."""
        mock_sources = [
            Source(
                id=1,
                url="https://a.com",
                source_type=SourceType.WEBSITE,
                title="A",
                authority_tier=AuthorityTier.TIER_2_TRUSTED,
                status=SourceStatus.ACTIVE,
            ),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_sources
        mock_session.execute.return_value = mock_result

        sources = await repo.list_by_status(SourceStatus.ACTIVE)

        assert len(sources) == 1
        assert sources[0].status == SourceStatus.ACTIVE
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_status(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test updating source status."""
        mock_source = Source(
            id=1,
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Test",
            authority_tier=AuthorityTier.TIER_2_TRUSTED,
            status=SourceStatus.PENDING,
        )
        mock_session.get.return_value = mock_source

        result = await repo.update_status(
            source_id=1,
            status=SourceStatus.ACTIVE,
        )

        assert result is not None
        assert result.status == SourceStatus.ACTIVE
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_status_with_crawl_timestamp(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test updating source status with last_crawled_at."""
        mock_source = Source(
            id=1,
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Test",
            authority_tier=AuthorityTier.TIER_2_TRUSTED,
        )
        mock_session.get.return_value = mock_source
        crawl_time = datetime(2024, 1, 1, 12, 0, 0)

        result = await repo.update_status(
            source_id=1,
            status=SourceStatus.ACTIVE,
            last_crawled_at=crawl_time,
        )

        assert result is not None
        assert result.last_crawled_at == crawl_time
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_status_not_found(
        self, repo: SourceRepository, mock_session: MagicMock
    ) -> None:
        """Test updating status for non-existent source."""
        mock_session.get.return_value = None

        result = await repo.update_status(
            source_id=999,
            status=SourceStatus.ACTIVE,
        )

        assert result is None


class TestAcquisitionRequestRepository:
    """Tests for AcquisitionRequestRepository."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Create mock async session."""
        session = MagicMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.execute = AsyncMock()
        session.get = AsyncMock()
        return session

    @pytest.fixture
    def repo(self, mock_session: MagicMock) -> AcquisitionRequestRepository:
        """Create repository with mock session."""
        return AcquisitionRequestRepository(mock_session)

    @pytest.mark.asyncio
    async def test_create_request(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test creating acquisition request."""
        request = await repo.create(
            url="https://example.com",
            reason="Need documentation",
            priority=5,
        )

        assert request.url == "https://example.com"
        assert request.reason == "Need documentation"
        assert request.priority == 5
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_request_with_requester(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test creating request with requester identifier."""
        request = await repo.create(
            url="https://example.com",
            reason="Need docs",
            priority=1,
            requested_by="user@example.com",
        )

        assert request.requested_by == "user@example.com"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_request_default_priority(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test creating request with default priority."""
        request = await repo.create(
            url="https://example.com",
            reason="Need docs",
        )

        assert request.priority == 3  # Default priority
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test getting request by ID."""
        mock_request = AcquisitionRequest(
            id=1,
            url="https://example.com",
            reason="Test",
        )
        mock_session.get.return_value = mock_request

        request = await repo.get_by_id(1)

        assert request is not None
        assert request.id == 1
        mock_session.get.assert_awaited_once_with(AcquisitionRequest, 1)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test getting non-existent request."""
        mock_session.get.return_value = None

        request = await repo.get_by_id(999)

        assert request is None

    @pytest.mark.asyncio
    async def test_list_pending(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test listing pending requests."""
        mock_requests = [
            AcquisitionRequest(id=1, url="https://a.com", reason="A", priority=10),
            AcquisitionRequest(id=2, url="https://b.com", reason="B", priority=5),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_requests
        mock_session.execute.return_value = mock_result

        requests = await repo.list_pending()

        assert len(requests) == 2
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_status_completed(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test marking request as completed."""
        mock_request = AcquisitionRequest(
            id=1,
            url="https://example.com",
            reason="Test",
            status=AcquisitionRequestStatus.PENDING,
        )
        mock_session.get.return_value = mock_request
        processed_time = datetime(2024, 1, 1, 12, 0, 0)

        result = await repo.update_status(
            request_id=1,
            status=AcquisitionRequestStatus.COMPLETED,
            processed_at=processed_time,
        )

        assert result is not None
        assert result.status == AcquisitionRequestStatus.COMPLETED
        assert result.processed_at == processed_time
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_status_rejected(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test marking request as rejected."""
        mock_request = AcquisitionRequest(
            id=1,
            url="https://example.com",
            reason="Test",
        )
        mock_session.get.return_value = mock_request

        result = await repo.update_status(
            request_id=1,
            status=AcquisitionRequestStatus.REJECTED,
        )

        assert result is not None
        assert result.status == AcquisitionRequestStatus.REJECTED
        mock_session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_status_not_found(
        self, repo: AcquisitionRequestRepository, mock_session: MagicMock
    ) -> None:
        """Test updating non-existent request."""
        mock_session.get.return_value = None

        result = await repo.update_status(
            request_id=999,
            status=AcquisitionRequestStatus.COMPLETED,
        )

        assert result is None
