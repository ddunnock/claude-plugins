"""SQLAlchemy ORM models for Knowledge MCP v2.0.

Defines database schema for:
- Source: Tracked knowledge sources (websites, documentation sites)
- AcquisitionRequest: User requests to add new sources

Uses SQLAlchemy 2.0 declarative mapping with type hints.
"""

from __future__ import annotations

import enum
from datetime import datetime  # noqa: TCH003

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class SourceType(str, enum.Enum):
    """Type of knowledge source."""

    WEBSITE = "website"
    DOCUMENTATION = "documentation"
    STANDARDS_BODY = "standards_body"
    BLOG = "blog"
    REPOSITORY = "repository"


class SourceStatus(str, enum.Enum):
    """Status of source ingestion."""

    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
    ARCHIVED = "archived"


class AuthorityTier(str, enum.Enum):
    """Authority tier for source prioritization."""

    TIER_1_CANONICAL = "tier_1_canonical"  # IEEE, ISO, INCOSE official docs
    TIER_2_TRUSTED = "tier_2_trusted"  # NASA handbooks, established blogs
    TIER_3_COMMUNITY = "tier_3_community"  # Community content, tutorials


class AcquisitionRequestStatus(str, enum.Enum):
    """Status of acquisition request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class Source(Base):
    """Knowledge source tracked by the system.

    Represents a website or documentation source that has been ingested
    or is scheduled for ingestion. Tracks metadata, status, and authority tier.

    Attributes:
        id: Primary key.
        url: Source URL (unique, indexed).
        title: Display title of the source.
        source_type: Type of source (website, documentation, etc.).
        status: Current ingestion status.
        authority_tier: Authority level for ranking.
        description: Optional description of the source.
        created_at: Timestamp when source was added.
        updated_at: Timestamp of last update.
        last_crawled_at: Timestamp of last successful crawl.
    """

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, native_enum=False), nullable=False
    )
    status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus, native_enum=False), default=SourceStatus.PENDING, nullable=False
    )
    authority_tier: Mapped[AuthorityTier] = mapped_column(
        Enum(AuthorityTier, native_enum=False), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_crawled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        """String representation of Source."""
        return f"<Source(id={self.id}, url='{self.url}', status={self.status.value})>"


class AcquisitionRequest(Base):
    """User request to acquire a new knowledge source.

    Tracks user requests for adding new sources to the knowledge base.
    Used for approval workflow and prioritization.

    Attributes:
        id: Primary key.
        url: Requested source URL (indexed).
        reason: User-provided reason for request.
        priority: Priority level (1=highest, 5=lowest).
        status: Request status (pending, approved, rejected, completed).
        requested_by: Optional identifier of requester.
        created_at: Timestamp when request was created.
        updated_at: Timestamp of last update.
        processed_at: Timestamp when request was processed.
    """

    __tablename__ = "acquisition_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2048), index=True, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    status: Mapped[AcquisitionRequestStatus] = mapped_column(
        Enum(AcquisitionRequestStatus, native_enum=False),
        default=AcquisitionRequestStatus.PENDING,
        nullable=False,
    )
    requested_by: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        """String representation of AcquisitionRequest."""
        return (
            f"<AcquisitionRequest(id={self.id}, url='{self.url}', status={self.status.value})>"
        )
