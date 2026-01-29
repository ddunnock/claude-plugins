# tests/unit/test_search/test_citation.py
"""Unit tests for citation formatting utilities."""

from __future__ import annotations

import pytest

from knowledge_mcp.search.citation import CitationFormatter, format_citation
from knowledge_mcp.search.models import SearchResult


class TestFormatCitation:
    """Tests for format_citation function."""

    def test_full_citation_with_all_fields(self) -> None:
        """Test citation with all fields provided."""
        citation = format_citation(
            document_title="ISO/IEC/IEEE 12207:2017",
            clause_number="6.4.2",
            page_numbers=[23],
            section_title="Verification",
        )
        assert citation == "ISO/IEC/IEEE 12207:2017, Clause 6.4.2 (Verification), p.23"

    def test_citation_without_clause_number(self) -> None:
        """Test citation when clause_number is missing."""
        citation = format_citation(
            document_title="INCOSE SE Handbook",
            page_numbers=[45],
        )
        assert citation == "INCOSE SE Handbook, p.45"

    def test_citation_without_page_numbers(self) -> None:
        """Test citation when page_numbers is missing."""
        citation = format_citation(
            document_title="IEEE 15288:2023",
            clause_number="5.1",
        )
        assert citation == "IEEE 15288:2023, Clause 5.1"

    def test_citation_title_only(self) -> None:
        """Test citation with only document title."""
        citation = format_citation(document_title="NASA SE Handbook")
        assert citation == "NASA SE Handbook"

    def test_citation_with_page_range(self) -> None:
        """Test citation with multiple page numbers formatted as range."""
        citation = format_citation(
            document_title="INCOSE SE Handbook",
            clause_number="Section 4.2",
            page_numbers=[45, 46, 47],
            section_title="Requirements Definition",
        )
        assert citation == "INCOSE SE Handbook, Section 4.2 (Requirements Definition), pp.45-47"

    def test_citation_with_non_contiguous_pages(self) -> None:
        """Test that non-contiguous pages still format as min-max range."""
        citation = format_citation(
            document_title="Test Document",
            page_numbers=[10, 15, 20],
        )
        assert citation == "Test Document, pp.10-20"

    def test_citation_auto_prefixes_clause(self) -> None:
        """Test that clause numbers without prefix get 'Clause' added."""
        citation = format_citation(
            document_title="ISO 12207:2017",
            clause_number="6.4.2",
        )
        assert citation == "ISO 12207:2017, Clause 6.4.2"

    def test_citation_preserves_section_prefix(self) -> None:
        """Test that 'Section' prefix is preserved."""
        citation = format_citation(
            document_title="INCOSE Handbook",
            clause_number="Section 4.2",
        )
        assert citation == "INCOSE Handbook, Section 4.2"

    def test_citation_preserves_clause_prefix(self) -> None:
        """Test that 'Clause' prefix is preserved if already present."""
        citation = format_citation(
            document_title="ISO Standard",
            clause_number="Clause 3.1",
        )
        assert citation == "ISO Standard, Clause 3.1"

    def test_section_title_without_clause_omitted(self) -> None:
        """Test that section_title is omitted if clause_number is not provided."""
        citation = format_citation(
            document_title="Test Document",
            section_title="Some Section",
            page_numbers=[10],
        )
        # Section title should not appear without clause
        assert citation == "Test Document, p.10"

    def test_citation_with_empty_page_list(self) -> None:
        """Test that empty page_numbers list is treated as None."""
        citation = format_citation(
            document_title="Test Document",
            page_numbers=[],
        )
        assert citation == "Test Document"

    def test_citation_case_insensitive_prefix_detection(self) -> None:
        """Test that prefix detection works regardless of case."""
        citation1 = format_citation(
            document_title="Test",
            clause_number="clause 5",
        )
        citation2 = format_citation(
            document_title="Test",
            clause_number="SECTION 3",
        )
        assert citation1 == "Test, clause 5"
        assert citation2 == "Test, SECTION 3"


class TestCitationFormatter:
    """Tests for CitationFormatter class."""

    @pytest.fixture
    def sample_result(self) -> SearchResult:
        """Create a sample SearchResult for testing."""
        return SearchResult(
            id="chunk-1",
            content="Test content",
            score=0.87,
            document_title="ISO/IEC/IEEE 12207:2017",
            clause_number="6.4.2",
            page_numbers=[23],
            section_title="Verification",
        )

    @pytest.fixture
    def minimal_result(self) -> SearchResult:
        """Create a minimal SearchResult with only title."""
        return SearchResult(
            id="chunk-2",
            content="Test content",
            score=0.50,
            document_title="NASA SE Handbook",
        )

    def test_formatter_with_relevance_enabled(self, sample_result: SearchResult) -> None:
        """Test formatter with include_relevance=True."""
        formatter = CitationFormatter(include_relevance=True)
        citation = formatter.format(sample_result)
        assert citation == "ISO/IEC/IEEE 12207:2017, Clause 6.4.2 (Verification), p.23 (87% relevant)"

    def test_formatter_with_relevance_disabled(self, sample_result: SearchResult) -> None:
        """Test formatter with include_relevance=False."""
        formatter = CitationFormatter(include_relevance=False)
        citation = formatter.format(sample_result)
        assert citation == "ISO/IEC/IEEE 12207:2017, Clause 6.4.2 (Verification), p.23"

    def test_formatter_default_includes_relevance(self, sample_result: SearchResult) -> None:
        """Test that default formatter includes relevance."""
        formatter = CitationFormatter()
        citation = formatter.format(sample_result)
        assert "87% relevant" in citation

    def test_format_with_relevance_always_includes_score(self, sample_result: SearchResult) -> None:
        """Test that format_with_relevance always includes score regardless of setting."""
        formatter = CitationFormatter(include_relevance=False)
        citation = formatter.format_with_relevance(sample_result)
        assert "(87% relevant)" in citation

    def test_formatter_with_minimal_metadata(self, minimal_result: SearchResult) -> None:
        """Test formatter with minimal SearchResult (title only)."""
        formatter = CitationFormatter(include_relevance=True)
        citation = formatter.format(minimal_result)
        assert citation == "NASA SE Handbook (50% relevant)"

    def test_formatter_rounds_relevance_percentage(self) -> None:
        """Test that relevance percentage is properly rounded."""
        result = SearchResult(
            id="chunk-3",
            content="Test",
            score=0.876,
            document_title="Test Document",
        )
        formatter = CitationFormatter(include_relevance=True)
        citation = formatter.format(result)
        # int(0.876 * 100) = 87
        assert "(87% relevant)" in citation

    def test_formatter_with_page_range(self) -> None:
        """Test formatter with multiple pages."""
        result = SearchResult(
            id="chunk-4",
            content="Test",
            score=0.92,
            document_title="INCOSE Handbook",
            clause_number="Section 4.2",
            page_numbers=[45, 46, 47],
            section_title="Requirements",
        )
        formatter = CitationFormatter(include_relevance=False)
        citation = formatter.format(result)
        assert citation == "INCOSE Handbook, Section 4.2 (Requirements), pp.45-47"

    def test_formatter_with_empty_page_numbers(self) -> None:
        """Test formatter handles empty page_numbers list."""
        result = SearchResult(
            id="chunk-5",
            content="Test",
            score=0.80,
            document_title="Test Document",
            clause_number="3.1",
            page_numbers=[],  # Empty list
        )
        formatter = CitationFormatter(include_relevance=False)
        citation = formatter.format(result)
        assert citation == "Test Document, Clause 3.1"

    def test_formatter_with_none_clause_number(self) -> None:
        """Test formatter handles None clause_number."""
        result = SearchResult(
            id="chunk-6",
            content="Test",
            score=0.75,
            document_title="Test Document",
            clause_number=None,
            page_numbers=[10],
            section_title="Some Section",  # Should be ignored
        )
        formatter = CitationFormatter(include_relevance=False)
        citation = formatter.format(result)
        assert citation == "Test Document, p.10"
        assert "Some Section" not in citation
