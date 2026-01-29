# tests/unit/test_search/test_models.py
"""Unit tests for search result models."""

from __future__ import annotations

import pytest

from knowledge_mcp.search.models import SearchResult


class TestSearchResultCitation:
    """Tests for SearchResult.citation property."""

    def test_citation_with_full_metadata(self) -> None:
        """Test citation property with all metadata fields."""
        result = SearchResult(
            id="chunk-1",
            content="Test content",
            score=0.95,
            document_title="ISO/IEC/IEEE 12207:2017",
            clause_number="6.4.2",
            page_numbers=[23],
            section_title="Verification",
        )
        expected = "ISO/IEC/IEEE 12207:2017, Clause 6.4.2 (Verification), p.23"
        assert result.citation == expected

    def test_citation_with_minimal_metadata(self) -> None:
        """Test citation property with only document title."""
        result = SearchResult(
            id="chunk-2",
            content="Test content",
            score=0.80,
            document_title="NASA SE Handbook",
        )
        assert result.citation == "NASA SE Handbook"

    def test_citation_without_clause(self) -> None:
        """Test citation when clause_number is missing."""
        result = SearchResult(
            id="chunk-3",
            content="Test content",
            score=0.85,
            document_title="INCOSE SE Handbook",
            page_numbers=[45],
        )
        assert result.citation == "INCOSE SE Handbook, p.45"

    def test_citation_without_pages(self) -> None:
        """Test citation when page_numbers is missing."""
        result = SearchResult(
            id="chunk-4",
            content="Test content",
            score=0.90,
            document_title="IEEE 15288:2023",
            clause_number="5.1",
        )
        assert result.citation == "IEEE 15288:2023, Clause 5.1"

    def test_citation_with_page_range(self) -> None:
        """Test citation with multiple pages."""
        result = SearchResult(
            id="chunk-5",
            content="Test content",
            score=0.92,
            document_title="INCOSE Handbook",
            clause_number="Section 4.2",
            page_numbers=[45, 46, 47],
            section_title="Requirements",
        )
        expected = "INCOSE Handbook, Section 4.2 (Requirements), pp.45-47"
        assert result.citation == expected

    def test_citation_with_empty_page_list(self) -> None:
        """Test that empty page_numbers list is treated as None."""
        result = SearchResult(
            id="chunk-6",
            content="Test content",
            score=0.75,
            document_title="Test Document",
            clause_number="3.1",
            page_numbers=[],  # Empty list
        )
        assert result.citation == "Test Document, Clause 3.1"

    def test_citation_with_section_but_no_clause(self) -> None:
        """Test that section_title is omitted if clause_number is not provided."""
        result = SearchResult(
            id="chunk-7",
            content="Test content",
            score=0.70,
            document_title="Test Document",
            section_title="Some Section",  # Should be ignored
            page_numbers=[10],
        )
        # Section title should not appear without clause
        assert result.citation == "Test Document, p.10"
        assert "Some Section" not in result.citation


class TestSearchResultCitationWithRelevance:
    """Tests for SearchResult.citation_with_relevance property."""

    def test_citation_with_relevance_includes_percentage(self) -> None:
        """Test that citation_with_relevance includes relevance score."""
        result = SearchResult(
            id="chunk-1",
            content="Test content",
            score=0.87,
            document_title="ISO/IEC/IEEE 12207:2017",
            clause_number="6.4.2",
            page_numbers=[23],
            section_title="Verification",
        )
        expected = "ISO/IEC/IEEE 12207:2017, Clause 6.4.2 (Verification), p.23 (87% relevant)"
        assert result.citation_with_relevance == expected

    def test_citation_with_relevance_minimal_metadata(self) -> None:
        """Test citation_with_relevance with minimal metadata."""
        result = SearchResult(
            id="chunk-2",
            content="Test content",
            score=0.50,
            document_title="NASA SE Handbook",
        )
        assert result.citation_with_relevance == "NASA SE Handbook (50% relevant)"

    def test_citation_with_relevance_rounds_percentage(self) -> None:
        """Test that relevance percentage is properly rounded."""
        result = SearchResult(
            id="chunk-3",
            content="Test content",
            score=0.876,
            document_title="Test Document",
        )
        # int(0.876 * 100) = 87
        assert result.citation_with_relevance == "Test Document (87% relevant)"

    def test_citation_with_relevance_high_score(self) -> None:
        """Test citation_with_relevance with high relevance score."""
        result = SearchResult(
            id="chunk-4",
            content="Test content",
            score=0.99,
            document_title="IEEE Standard",
            clause_number="Section 5",
        )
        assert result.citation_with_relevance == "IEEE Standard, Section 5 (99% relevant)"

    def test_citation_with_relevance_low_score(self) -> None:
        """Test citation_with_relevance with low relevance score."""
        result = SearchResult(
            id="chunk-5",
            content="Test content",
            score=0.15,
            document_title="Test Doc",
        )
        assert result.citation_with_relevance == "Test Doc (15% relevant)"

    def test_citation_with_relevance_perfect_score(self) -> None:
        """Test citation_with_relevance with perfect score."""
        result = SearchResult(
            id="chunk-6",
            content="Test content",
            score=1.0,
            document_title="Perfect Match",
        )
        assert result.citation_with_relevance == "Perfect Match (100% relevant)"

    def test_citation_with_relevance_zero_score(self) -> None:
        """Test citation_with_relevance with zero score."""
        result = SearchResult(
            id="chunk-7",
            content="Test content",
            score=0.0,
            document_title="No Match",
        )
        assert result.citation_with_relevance == "No Match (0% relevant)"


class TestSearchResultBasics:
    """Tests for basic SearchResult functionality."""

    def test_search_result_creation(self) -> None:
        """Test creating a basic SearchResult."""
        result = SearchResult(
            id="test-id",
            content="Test content",
            score=0.95,
        )
        assert result.id == "test-id"
        assert result.content == "Test content"
        assert result.score == 0.95
        assert result.document_title == ""
        assert result.clause_number is None
        assert result.page_numbers == []

    def test_search_result_with_metadata(self) -> None:
        """Test SearchResult with metadata dict."""
        metadata = {
            "custom_field": "value",
            "another_field": 123,
        }
        result = SearchResult(
            id="test-id",
            content="Test content",
            score=0.90,
            metadata=metadata,
        )
        assert result.metadata == metadata
        assert result.metadata["custom_field"] == "value"

    def test_search_result_defaults(self) -> None:
        """Test SearchResult default values."""
        result = SearchResult(
            id="test-id",
            content="Test content",
            score=0.85,
        )
        assert result.metadata == {}
        assert result.document_id == ""
        assert result.document_type == ""
        assert result.section_title == ""
        assert result.section_hierarchy == []
        assert result.chunk_type == ""
        assert result.normative is False
        assert result.clause_number is None
        assert result.page_numbers == []
