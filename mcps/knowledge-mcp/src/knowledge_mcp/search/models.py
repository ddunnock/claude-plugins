# src/knowledge_mcp/search/models.py
"""
Data models for search results.

This module defines the SearchResult dataclass used to represent
search results with flattened citation fields for easy access.

Example:
    >>> result = SearchResult(
    ...     id="chunk-1",
    ...     content="Systems engineering is...",
    ...     score=0.95,
    ...     document_title="IEEE 15288",
    ... )
    >>> print(f"{result.score:.2f}: {result.document_title}")
    0.95: IEEE 15288
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    """
    A single search result with content, score, and metadata.

    Contains both the core search result data and flattened citation
    fields for easy access when generating citations (FR-3.4).

    Attributes:
        id: Unique chunk identifier.
        content: The text content of the chunk.
        score: Similarity score (0-1, higher is more similar).
        metadata: Full metadata dictionary from vector store.
        document_id: Source document identifier.
        document_title: Human-readable document title.
        document_type: Type of document (standard, handbook, guide, etc.).
        section_title: Title of containing section.
        section_hierarchy: Path through document structure (e.g., ["5", "5.3"]).
        chunk_type: Type of chunk (requirement, definition, guidance, etc.).
        normative: Whether the chunk contains normative (mandatory) content.
        clause_number: Clause identifier if applicable (e.g., "5.3.1").
        page_numbers: Source page references.

    Example:
        >>> result = SearchResult(
        ...     id="ieee-15288-chunk-42",
        ...     content="The SRR shall verify requirements...",
        ...     score=0.92,
        ...     document_title="IEEE 15288.2",
        ...     section_title="System Requirements Review",
        ...     normative=True,
        ... )
        >>> print(f"[{result.document_title}] {result.section_title}")
        [IEEE 15288.2] System Requirements Review
    """

    # Core fields (required)
    id: str
    content: str
    score: float

    # Full metadata dict for extensibility
    metadata: dict[str, Any] = field(default_factory=lambda: {})

    # Flattened citation fields (FR-3.4: Return source citation with section references)
    document_id: str = ""
    document_title: str = ""
    document_type: str = ""
    section_title: str = ""
    section_hierarchy: list[str] = field(default_factory=lambda: [])
    chunk_type: str = ""
    normative: bool = False
    clause_number: str | None = None
    page_numbers: list[int] = field(default_factory=lambda: [])

    @property
    def citation(self) -> str:
        """
        Get formatted citation for this result.

        Returns standards-compliant citation in the format:
        "DOCUMENT, Clause X.Y.Z, p.N"

        Missing metadata is gracefully omitted. Uses format_citation
        utility to generate consistent academic-style citations.

        Returns:
            Formatted citation string.

        Example:
            >>> result = SearchResult(
            ...     id="chunk-1",
            ...     content="...",
            ...     score=0.95,
            ...     document_title="ISO/IEC/IEEE 12207:2017",
            ...     clause_number="6.4.2",
            ...     page_numbers=[23],
            ... )
            >>> print(result.citation)
            ISO/IEC/IEEE 12207:2017, Clause 6.4.2, p.23
        """
        from knowledge_mcp.search.citation import format_citation

        return format_citation(
            document_title=self.document_title,
            clause_number=self.clause_number,
            page_numbers=self.page_numbers if self.page_numbers else None,
            section_title=self.section_title if self.section_title else None,
        )

    @property
    def citation_with_relevance(self) -> str:
        """
        Get formatted citation with relevance score.

        Appends relevance percentage to the base citation for displaying
        search result quality to users (FR-3.5).

        Returns:
            Citation with relevance percentage appended.

        Example:
            >>> result = SearchResult(
            ...     id="chunk-1",
            ...     content="...",
            ...     score=0.87,
            ...     document_title="ISO 12207:2017",
            ... )
            >>> print(result.citation_with_relevance)
            ISO 12207:2017 (87% relevant)
        """
        relevance_pct = int(self.score * 100)
        return f"{self.citation} ({relevance_pct}% relevant)"
