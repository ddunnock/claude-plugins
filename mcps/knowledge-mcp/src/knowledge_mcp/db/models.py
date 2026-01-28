"""SQLAlchemy ORM models for Knowledge MCP v2.0.

Defines database schema for:
- Source: Tracked knowledge sources (websites, documentation sites)
- AcquisitionRequest: User requests to add new sources
- Project: Project tracking for workflow support
- QueryHistory: Query history linked to projects
- Decision: Project decisions with rationale
- DecisionSource: Links decisions to supporting chunks

Uses SQLAlchemy 2.0 declarative mapping with type hints.
"""

from __future__ import annotations

import enum
from datetime import datetime  # noqa: TCH003
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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


class ProjectStatus(str, enum.Enum):
    """Status of project lifecycle."""

    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# Valid state transitions for projects
STATE_TRANSITIONS: dict[ProjectStatus, list[ProjectStatus]] = {
    ProjectStatus.PLANNING: [ProjectStatus.ACTIVE, ProjectStatus.ABANDONED],
    ProjectStatus.ACTIVE: [ProjectStatus.COMPLETED, ProjectStatus.ABANDONED],
    ProjectStatus.COMPLETED: [],  # Terminal state
    ProjectStatus.ABANDONED: [],  # Terminal state
}


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


class Project(Base):
    """Project tracking for workflow support.

    Represents a project context for knowledge capture workflow.
    Tracks project metadata, domain, applicable standards, and lifecycle state.

    Attributes:
        id: Primary key (UUID).
        name: Project name.
        domain: Optional domain (e.g., "aerospace", "medical").
        status: Current project status (planning, active, completed, abandoned).
        applicable_standards: List of applicable standards (e.g., ["IEEE 15288", "DO-178C"]).
        description: Optional project description.
        created_at: Timestamp when project was created.
        updated_at: Timestamp of last update.
        completed_at: Timestamp when project was completed/abandoned.
        query_history: Related query history entries.
        decisions: Related decisions.
    """

    __tablename__ = "projects"

    id: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, native_enum=False),
        insert_default=ProjectStatus.PLANNING,
        server_default="planning",
        nullable=False
    )
    applicable_standards: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    query_history: Mapped[list["QueryHistory"]] = relationship(
        "QueryHistory", back_populates="project"
    )
    decisions: Mapped[list["Decision"]] = relationship(
        "Decision", back_populates="project"
    )

    def __init__(self, **kwargs):
        """Initialize Project with default status if not provided."""
        if "status" not in kwargs:
            kwargs["status"] = ProjectStatus.PLANNING
        super().__init__(**kwargs)

    def can_transition_to(self, new_status: ProjectStatus) -> bool:
        """Check if transition to new status is valid.

        Args:
            new_status: Target status to transition to.

        Returns:
            True if transition is valid, False otherwise.
        """
        return new_status in STATE_TRANSITIONS[self.status]

    def transition_to(self, new_status: ProjectStatus) -> None:
        """Transition to new status.

        Args:
            new_status: Target status to transition to.

        Raises:
            ValueError: If transition is invalid.
        """
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid transition from {self.status.value} to {new_status.value}"
            )
        self.status = new_status
        if new_status in (ProjectStatus.COMPLETED, ProjectStatus.ABANDONED):
            self.completed_at = datetime.now()

    def __repr__(self) -> str:
        """String representation of Project."""
        return f"<Project(id={self.id}, name='{self.name}', status={self.status.value})>"


class QueryHistory(Base):
    """Query history linked to projects.

    Tracks queries made within a project context, including result counts
    and workflow type.

    Attributes:
        id: Primary key (UUID).
        project_id: Foreign key to projects table.
        query: The query text.
        result_count: Number of results returned.
        workflow_type: Optional workflow type (e.g., "rcca", "trade", "explore", "plan").
        created_at: Timestamp when query was executed.
        project: Related project.
    """

    __tablename__ = "query_history"

    id: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    project_id: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, nullable=False)
    workflow_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship
    project: Mapped["Project"] = relationship("Project", back_populates="query_history")

    def __repr__(self) -> str:
        """String representation of QueryHistory."""
        return f"<QueryHistory(id={self.id}, project_id={self.project_id}, query='{self.query[:50]}...')>"


class Decision(Base):
    """Project decision with rationale.

    Stores decisions made during project lifecycle, including alternatives
    considered and rationale.

    Attributes:
        id: Primary key (UUID).
        project_id: Foreign key to projects table.
        decision: The decision made.
        alternatives: List of alternatives considered.
        rationale: Rationale for the decision.
        created_at: Timestamp when decision was made.
        project: Related project.
        sources: Related decision sources.
    """

    __tablename__ = "decisions"

    id: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    project_id: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    alternatives: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="decisions")
    sources: Mapped[list["DecisionSource"]] = relationship(
        "DecisionSource", back_populates="decision"
    )

    def __repr__(self) -> str:
        """String representation of Decision."""
        return f"<Decision(id={self.id}, project_id={self.project_id}, decision='{self.decision[:50]}...')>"


class DecisionSource(Base):
    """Links decisions to supporting chunks.

    Tracks which knowledge chunks support a decision, with relevance scores.

    Attributes:
        id: Primary key (UUID).
        decision_id: Foreign key to decisions table.
        chunk_id: Reference to Qdrant chunk UUID.
        relevance: Relevance score (0.0-1.0).
        decision: Related decision.
    """

    __tablename__ = "decision_sources"

    id: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    decision_id: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("decisions.id"), nullable=False
    )
    chunk_id: Mapped[str] = mapped_column(String(255), nullable=False)
    relevance: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationship
    decision: Mapped["Decision"] = relationship("Decision", back_populates="sources")

    def __repr__(self) -> str:
        """String representation of DecisionSource."""
        return f"<DecisionSource(id={self.id}, decision_id={self.decision_id}, chunk_id='{self.chunk_id}')>"
