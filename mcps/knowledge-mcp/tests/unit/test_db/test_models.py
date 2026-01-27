"""Unit tests for database models."""

from datetime import datetime

import pytest

from knowledge_mcp.db.models import (
    AcquisitionRequest,
    AcquisitionRequestStatus,
    AuthorityTier,
    Source,
    SourceStatus,
    SourceType,
)


class TestSourceType:
    """Tests for SourceType enum."""

    def test_values(self) -> None:
        """Test all enum values exist."""
        assert SourceType.WEBSITE == "website"
        assert SourceType.DOCUMENTATION == "documentation"
        assert SourceType.STANDARDS_BODY == "standards_body"
        assert SourceType.BLOG == "blog"
        assert SourceType.REPOSITORY == "repository"

    def test_from_string(self) -> None:
        """Test creating from string."""
        assert SourceType("website") == SourceType.WEBSITE
        assert SourceType("documentation") == SourceType.DOCUMENTATION

    def test_all_values_are_strings(self) -> None:
        """Test that all enum values are strings."""
        for source_type in SourceType:
            assert isinstance(source_type.value, str)


class TestSourceStatus:
    """Tests for SourceStatus enum."""

    def test_values(self) -> None:
        """Test all enum values exist."""
        assert SourceStatus.PENDING == "pending"
        assert SourceStatus.ACTIVE == "active"
        assert SourceStatus.FAILED == "failed"
        assert SourceStatus.ARCHIVED == "archived"

    def test_from_string(self) -> None:
        """Test creating from string."""
        assert SourceStatus("pending") == SourceStatus.PENDING
        assert SourceStatus("active") == SourceStatus.ACTIVE

    def test_all_values_are_strings(self) -> None:
        """Test that all enum values are strings."""
        for status in SourceStatus:
            assert isinstance(status.value, str)


class TestAuthorityTier:
    """Tests for AuthorityTier enum."""

    def test_values(self) -> None:
        """Test all enum values exist."""
        assert AuthorityTier.TIER_1_CANONICAL == "tier_1_canonical"
        assert AuthorityTier.TIER_2_TRUSTED == "tier_2_trusted"
        assert AuthorityTier.TIER_3_COMMUNITY == "tier_3_community"

    def test_from_string(self) -> None:
        """Test creating from string."""
        assert AuthorityTier("tier_1_canonical") == AuthorityTier.TIER_1_CANONICAL
        assert AuthorityTier("tier_2_trusted") == AuthorityTier.TIER_2_TRUSTED

    def test_all_values_are_strings(self) -> None:
        """Test that all enum values are strings."""
        for tier in AuthorityTier:
            assert isinstance(tier.value, str)


class TestAcquisitionRequestStatus:
    """Tests for AcquisitionRequestStatus enum."""

    def test_values(self) -> None:
        """Test all enum values exist."""
        assert AcquisitionRequestStatus.PENDING == "pending"
        assert AcquisitionRequestStatus.APPROVED == "approved"
        assert AcquisitionRequestStatus.REJECTED == "rejected"
        assert AcquisitionRequestStatus.COMPLETED == "completed"

    def test_from_string(self) -> None:
        """Test creating from string."""
        assert AcquisitionRequestStatus("pending") == AcquisitionRequestStatus.PENDING
        assert AcquisitionRequestStatus("completed") == AcquisitionRequestStatus.COMPLETED

    def test_all_values_are_strings(self) -> None:
        """Test that all enum values are strings."""
        for status in AcquisitionRequestStatus:
            assert isinstance(status.value, str)


class TestSourceModel:
    """Tests for Source model."""

    def test_create_source(self) -> None:
        """Test Source model creation."""
        source = Source(
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Example",
            authority_tier=AuthorityTier.TIER_2_TRUSTED,
        )
        assert source.url == "https://example.com"
        assert source.source_type == SourceType.WEBSITE
        assert source.title == "Example"
        assert source.authority_tier == AuthorityTier.TIER_2_TRUSTED

    def test_default_values(self) -> None:
        """Test default values are set."""
        source = Source(
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Test",
            authority_tier=AuthorityTier.TIER_2_TRUSTED,
        )
        # Note: SQLAlchemy defaults only apply when inserted to database
        # In Python object creation, we need to check if field is optional
        assert source.description is None
        assert source.last_crawled_at is None

    def test_optional_description(self) -> None:
        """Test optional description field."""
        source = Source(
            url="https://example.com",
            source_type=SourceType.DOCUMENTATION,
            title="Docs",
            authority_tier=AuthorityTier.TIER_1_CANONICAL,
            description="Important documentation",
        )
        assert source.description == "Important documentation"

    def test_repr(self) -> None:
        """Test string representation."""
        source = Source(
            id=42,
            url="https://example.com",
            source_type=SourceType.WEBSITE,
            title="Test",
            authority_tier=AuthorityTier.TIER_2_TRUSTED,
            status=SourceStatus.ACTIVE,
        )
        repr_str = repr(source)
        assert "Source" in repr_str
        assert "42" in repr_str
        assert "example.com" in repr_str
        assert "active" in repr_str

    def test_all_source_types(self) -> None:
        """Test creating source with all source types."""
        for source_type in SourceType:
            source = Source(
                url=f"https://{source_type.value}.com",
                source_type=source_type,
                title=f"Test {source_type.value}",
                authority_tier=AuthorityTier.TIER_2_TRUSTED,
            )
            assert source.source_type == source_type

    def test_all_authority_tiers(self) -> None:
        """Test creating source with all authority tiers."""
        for tier in AuthorityTier:
            source = Source(
                url=f"https://{tier.value}.com",
                source_type=SourceType.WEBSITE,
                title=f"Test {tier.value}",
                authority_tier=tier,
            )
            assert source.authority_tier == tier

    def test_all_statuses(self) -> None:
        """Test creating source with all statuses."""
        for status in SourceStatus:
            source = Source(
                url=f"https://{status.value}.com",
                source_type=SourceType.WEBSITE,
                title=f"Test {status.value}",
                authority_tier=AuthorityTier.TIER_2_TRUSTED,
                status=status,
            )
            assert source.status == status


class TestAcquisitionRequestModel:
    """Tests for AcquisitionRequest model."""

    def test_create_request(self) -> None:
        """Test AcquisitionRequest model creation."""
        request = AcquisitionRequest(
            url="https://example.com",
            reason="Need this content",
            priority=5,
        )
        assert request.url == "https://example.com"
        assert request.reason == "Need this content"
        assert request.priority == 5

    def test_default_values(self) -> None:
        """Test default values are set."""
        request = AcquisitionRequest(
            url="https://example.com",
            reason="Test",
        )
        # Note: SQLAlchemy defaults only apply when inserted to database
        # In Python object creation, we need to check if field is optional
        assert request.requested_by is None
        assert request.processed_at is None

    def test_with_requester(self) -> None:
        """Test creating request with requester."""
        request = AcquisitionRequest(
            url="https://example.com",
            reason="Need docs",
            requested_by="user@example.com",
        )
        assert request.requested_by == "user@example.com"

    def test_repr(self) -> None:
        """Test string representation."""
        request = AcquisitionRequest(
            id=123,
            url="https://example.com",
            reason="Test",
            status=AcquisitionRequestStatus.COMPLETED,
        )
        repr_str = repr(request)
        assert "AcquisitionRequest" in repr_str
        assert "123" in repr_str
        assert "example.com" in repr_str
        assert "completed" in repr_str

    def test_all_statuses(self) -> None:
        """Test creating request with all statuses."""
        for status in AcquisitionRequestStatus:
            request = AcquisitionRequest(
                url=f"https://{status.value}.com",
                reason=f"Test {status.value}",
                status=status,
            )
            assert request.status == status

    def test_priority_range(self) -> None:
        """Test different priority values."""
        for priority in [1, 3, 5, 10]:
            request = AcquisitionRequest(
                url=f"https://priority-{priority}.com",
                reason="Test",
                priority=priority,
            )
            assert request.priority == priority
