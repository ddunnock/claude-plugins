# src/knowledge_mcp/search/citation.py
"""
Citation formatting utilities for standards-compliant references.

This module provides utilities for formatting search results into
academic-style citations that follow standards documentation conventions.

Example:
    >>> from knowledge_mcp.search.citation import format_citation
    >>> citation = format_citation(
    ...     document_title="ISO/IEC/IEEE 12207:2017",
    ...     clause_number="6.4.2",
    ...     page_numbers=[23],
    ... )
    >>> print(citation)
    ISO/IEC/IEEE 12207:2017, Clause 6.4.2, p.23
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from knowledge_mcp.search.models import SearchResult


def format_citation(
    document_title: str,
    clause_number: str | None = None,
    page_numbers: list[int] | None = None,
    section_title: str | None = None,
) -> str:
    """
    Format a citation in standards-compliant format.

    Creates academic-style citations for standards, handbooks, and technical
    documents following the pattern:
    "DOCUMENT, Clause/Section X.Y.Z (Title), p.N" or "pp.N-M"

    Args:
        document_title: Full document title (required).
            Examples: "ISO/IEC/IEEE 12207:2017", "INCOSE SE Handbook v5"
        clause_number: Clause or section identifier if applicable.
            Examples: "6.4.2", "5.3.1", "Section 4.2"
        page_numbers: List of page numbers. Single page or range.
            Examples: [23], [45, 46, 47]
        section_title: Section or clause title for additional context.
            Only included in output if clause_number is also provided.

    Returns:
        Formatted citation string with components separated by ", ".
        Missing components are gracefully omitted.

    Examples:
        >>> # Full citation
        >>> format_citation(
        ...     "ISO/IEC/IEEE 12207:2017",
        ...     clause_number="6.4.2",
        ...     page_numbers=[23],
        ...     section_title="Verification",
        ... )
        'ISO/IEC/IEEE 12207:2017, Clause 6.4.2 (Verification), p.23'

        >>> # No clause
        >>> format_citation("INCOSE SE Handbook", page_numbers=[45])
        'INCOSE SE Handbook, p.45'

        >>> # No page numbers
        >>> format_citation("IEEE 15288:2023", clause_number="5.1")
        'IEEE 15288:2023, Clause 5.1'

        >>> # Title only
        >>> format_citation("NASA SE Handbook")
        'NASA SE Handbook'

        >>> # Page range
        >>> format_citation(
        ...     "INCOSE SE Handbook",
        ...     clause_number="Section 4.2",
        ...     page_numbers=[45, 46, 47],
        ...     section_title="Requirements Definition",
        ... )
        'INCOSE SE Handbook, Section 4.2 (Requirements Definition), pp.45-47'
    """
    components: list[str] = [document_title]

    # Add clause/section number with optional title
    if clause_number:
        if clause_number.lower().startswith("section"):
            clause_part = clause_number
        elif clause_number.lower().startswith("clause"):
            clause_part = clause_number
        else:
            # Auto-prefix with "Clause" if not already prefixed
            clause_part = f"Clause {clause_number}"

        # Add section title in parentheses if provided
        if section_title:
            clause_part = f"{clause_part} ({section_title})"

        components.append(clause_part)

    # Add page numbers
    if page_numbers:
        if len(page_numbers) == 1:
            page_part = f"p.{page_numbers[0]}"
        else:
            # Format as range: pp.45-47
            page_part = f"pp.{min(page_numbers)}-{max(page_numbers)}"
        components.append(page_part)

    return ", ".join(components)


class CitationFormatter:
    """
    Advanced citation formatter with configurable output options.

    Provides formatted citations for SearchResult objects with optional
    relevance score display.

    Attributes:
        include_relevance: Whether to include relevance percentage by default.

    Example:
        >>> from knowledge_mcp.search.citation import CitationFormatter
        >>> from knowledge_mcp.search.models import SearchResult
        >>>
        >>> formatter = CitationFormatter(include_relevance=True)
        >>> result = SearchResult(
        ...     id="chunk-1",
        ...     content="...",
        ...     score=0.87,
        ...     document_title="ISO 12207:2017",
        ...     clause_number="6.4.2",
        ...     page_numbers=[23],
        ... )
        >>> print(formatter.format(result))
        ISO 12207:2017, Clause 6.4.2, p.23 (87% relevant)
    """

    def __init__(self, include_relevance: bool = True) -> None:
        """
        Initialize the citation formatter.

        Args:
            include_relevance: If True, include relevance percentage in output
                when using format() method. Default is True.
        """
        self.include_relevance = include_relevance

    def format(self, result: SearchResult) -> str:
        """
        Format a search result into a citation.

        Respects the include_relevance setting from __init__.

        Args:
            result: SearchResult object to format.

        Returns:
            Formatted citation string, with optional relevance percentage.

        Example:
            >>> formatter = CitationFormatter(include_relevance=False)
            >>> citation = formatter.format(result)
            >>> print(citation)
            ISO 12207:2017, Clause 6.4.2, p.23
        """
        if self.include_relevance:
            return self.format_with_relevance(result)
        else:
            return self._format_base(result)

    def format_with_relevance(self, result: SearchResult) -> str:
        """
        Format a search result with relevance score.

        Always includes relevance percentage regardless of include_relevance setting.

        Args:
            result: SearchResult object to format.

        Returns:
            Citation with relevance percentage appended.

        Example:
            >>> formatter = CitationFormatter()
            >>> citation = formatter.format_with_relevance(result)
            >>> print(citation)
            ISO 12207:2017, Clause 6.4.2, p.23 (87% relevant)
        """
        base_citation = self._format_base(result)
        relevance_pct = int(result.score * 100)
        return f"{base_citation} ({relevance_pct}% relevant)"

    def _format_base(self, result: SearchResult) -> str:
        """
        Format base citation without relevance score.

        Args:
            result: SearchResult object to format.

        Returns:
            Formatted citation string without relevance.
        """
        return format_citation(
            document_title=result.document_title,
            clause_number=result.clause_number,
            page_numbers=result.page_numbers if result.page_numbers else None,
            section_title=result.section_title if result.section_title else None,
        )
