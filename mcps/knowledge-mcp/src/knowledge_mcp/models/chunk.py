# src/knowledge_mcp/models/chunk.py
"""
Data models for knowledge chunks.

This module defines the KnowledgeChunk dataclass used throughout
the ingestion, embedding, and search pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional


@dataclass
class KnowledgeChunk:
    """
    A chunk of knowledge from a technical document.

    Represents a semantically coherent unit of content extracted
    from a source document, enriched with metadata for retrieval.

    Attributes:
        id: Unique identifier (UUID).
        document_id: Source document identifier.
        document_title: Human-readable document title.
        document_type: Document classification (standard, handbook, guide, spec).
        content: The actual text content.
        content_hash: SHA-256 hash for deduplication.
        token_count: Number of tokens for context management.
        section_hierarchy: Path through document structure.
        section_title: Title of containing section.
        parent_chunk_id: Link to parent section chunk.
        chunk_type: Content classification (definition, requirement, guidance, etc.).
        normative: Whether content is mandatory (normative).
        page_numbers: Source page references.
        clause_number: Clause identifier if applicable.
        references: Extracted cross-references.
        embedding: Vector embedding (populated after embed phase).
        embedding_model: Model used for embedding.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    Example:
        >>> chunk = KnowledgeChunk(
        ...     id="550e8400-e29b-41d4-a716-446655440000",
        ...     document_id="ieee-15288.2",
        ...     document_title="IEEE 15288.2-2014",
        ...     document_type="standard",
        ...     content="The SRR shall verify...",
        ...     content_hash="abc123...",
        ...     token_count=150,
        ... )
    """

    # Identity
    id: str
    document_id: str
    document_title: str
    document_type: str

    # Content
    content: str
    content_hash: str
    token_count: int

    # Hierarchy
    section_hierarchy: list[str] = field(default_factory=list)
    section_title: str = ""
    parent_chunk_id: Optional[str] = None

    # Classification
    chunk_type: str = "content"
    normative: Optional[bool] = None  # True=normative, False=informative, None=unknown

    # Location
    page_numbers: list[int] = field(default_factory=list)
    clause_number: Optional[str] = None

    # Cross-references
    references: list[str] = field(default_factory=list)

    # Embeddings
    embedding: Optional[list[float]] = None
    embedding_model: str = "text-embedding-3-small"

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict:
        """
        Convert chunk to dictionary for serialization.

        Returns:
            Dictionary representation of chunk.
        """
        return {
            "id": self.id,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "document_type": self.document_type,
            "content": self.content,
            "content_hash": self.content_hash,
            "token_count": self.token_count,
            "section_hierarchy": self.section_hierarchy,
            "section_title": self.section_title,
            "parent_chunk_id": self.parent_chunk_id,
            "chunk_type": self.chunk_type,
            "normative": self.normative,
            "page_numbers": self.page_numbers,
            "clause_number": self.clause_number,
            "references": self.references,
            "embedding_model": self.embedding_model,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }