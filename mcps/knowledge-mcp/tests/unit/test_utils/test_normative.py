"""Unit tests for normative detection module."""

from __future__ import annotations

import pytest

from knowledge_mcp.utils.normative import NormativeIndicator, detect_normative


class TestNormativeIndicator:
    """Tests for NormativeIndicator enum."""

    def test_enum_values(self) -> None:
        """Test that enum has expected values."""
        assert NormativeIndicator.NORMATIVE.value == "normative"
        assert NormativeIndicator.INFORMATIVE.value == "informative"
        assert NormativeIndicator.UNKNOWN.value == "unknown"


class TestDetectNormative:
    """Tests for detect_normative function."""

    # Normative keyword detection

    def test_shall_keyword(self) -> None:
        """Test that SHALL indicates normative content."""
        text = "The system SHALL verify user credentials."
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_must_keyword(self) -> None:
        """Test that MUST indicates normative content."""
        text = "The component MUST handle errors gracefully."
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_required_keyword(self) -> None:
        """Test that REQUIRED indicates normative content."""
        text = "Authentication is REQUIRED for all API endpoints."
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_should_keyword(self) -> None:
        """Test that SHOULD indicates normative content."""
        text = "The application SHOULD log all security events."
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_recommended_keyword(self) -> None:
        """Test that RECOMMENDED indicates normative content."""
        text = "Using TLS 1.3 is RECOMMENDED for secure connections."
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_normative_keyword_case_insensitive(self) -> None:
        """Test that normative keywords are case-insensitive."""
        texts = [
            "The system shall verify",
            "The system SHALL verify",
            "The system Shall verify",
            "The system ShaLl verify",
        ]
        for text in texts:
            result = detect_normative(text)
            assert result == NormativeIndicator.NORMATIVE

    # Informative keyword detection

    def test_may_keyword(self) -> None:
        """Test that MAY indicates informative content."""
        text = "The user MAY configure additional settings."
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_optional_keyword(self) -> None:
        """Test that OPTIONAL indicates informative content."""
        text = "Additional logging is OPTIONAL."
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_can_keyword(self) -> None:
        """Test that CAN indicates informative content."""
        text = "Users CAN customize the interface."
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_note_keyword(self) -> None:
        """Test that NOTE indicates informative content."""
        text = "NOTE: This section provides additional context."
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_example_keyword(self) -> None:
        """Test that EXAMPLE indicates informative content."""
        text = "EXAMPLE: Consider a web application with multiple users."
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_informative_keyword_case_insensitive(self) -> None:
        """Test that informative keywords are case-insensitive."""
        texts = [
            "note: This is a note",
            "NOTE: This is a note",
            "Note: This is a note",
            "NoTe: This is a note",
        ]
        for text in texts:
            result = detect_normative(text)
            assert result == NormativeIndicator.INFORMATIVE

    # Section marker detection

    def test_normative_section_marker_in_text(self) -> None:
        """Test that (normative) marker in text indicates normative."""
        text = "Annex A (normative): Security Requirements"
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_informative_section_marker_in_text(self) -> None:
        """Test that (informative) marker in text indicates informative."""
        text = "Annex B (informative): Examples and Use Cases"
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_normative_section_marker_in_path(self) -> None:
        """Test that (normative) marker in section path indicates normative."""
        text = "This section contains requirements."
        section_path = "Annex A (normative)"
        result = detect_normative(text, section_path)
        assert result == NormativeIndicator.NORMATIVE

    def test_informative_section_marker_in_path(self) -> None:
        """Test that (informative) marker in section path indicates informative."""
        text = "This section provides examples."
        section_path = "Annex B (informative)"
        result = detect_normative(text, section_path)
        assert result == NormativeIndicator.INFORMATIVE

    def test_section_marker_case_insensitive(self) -> None:
        """Test that section markers are case-insensitive."""
        texts = [
            "Annex (Normative)",
            "Annex (NORMATIVE)",
            "Annex (normative)",
        ]
        for text in texts:
            result = detect_normative(text)
            assert result == NormativeIndicator.NORMATIVE

    # Priority and edge cases

    def test_section_marker_overrides_keywords(self) -> None:
        """Test that section markers have priority over keywords."""
        # (informative) marker should override SHALL keyword
        text = "Annex (informative): The system SHALL do X."
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_normative_keyword_overrides_informative_keyword(self) -> None:
        """Test that normative keywords take priority."""
        text = "The system SHALL do X. NOTE: This is important."
        result = detect_normative(text)
        # SHALL appears first and is normative
        assert result == NormativeIndicator.NORMATIVE

    def test_empty_string(self) -> None:
        """Test that empty string returns UNKNOWN."""
        result = detect_normative("")
        assert result == NormativeIndicator.UNKNOWN

    def test_whitespace_only(self) -> None:
        """Test that whitespace-only returns UNKNOWN."""
        result = detect_normative("   \n\t  ")
        assert result == NormativeIndicator.UNKNOWN

    def test_no_indicators_body_content(self) -> None:
        """Test that body content without indicators is UNKNOWN."""
        text = "This section describes the authentication process."
        result = detect_normative(text)
        # Default for body content without markers is UNKNOWN
        assert result == NormativeIndicator.UNKNOWN

    def test_keyword_as_part_of_word(self) -> None:
        """Test that keywords must be whole words."""
        # "shall" as part of "marshall" should not match
        text = "The marshall handles the data."
        result = detect_normative(text)
        # Should be UNKNOWN (not matched as SHALL keyword, no explicit markers)
        assert result == NormativeIndicator.UNKNOWN

    def test_multiple_keywords_same_type(self) -> None:
        """Test text with multiple keywords of same type."""
        text = "The system SHALL verify and MUST authenticate."
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_mixed_case_in_sentence(self) -> None:
        """Test that keywords work in natural sentences."""
        text = "Users shall provide credentials and must accept terms."
        result = detect_normative(text)
        assert result == NormativeIndicator.NORMATIVE

    def test_note_at_start_of_paragraph(self) -> None:
        """Test NOTE at start of paragraph."""
        text = """NOTE: This is informative.

        Additional details follow."""
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE

    def test_example_with_colon(self) -> None:
        """Test EXAMPLE with colon separator."""
        text = "EXAMPLE: A user logs in with username and password."
        result = detect_normative(text)
        assert result == NormativeIndicator.INFORMATIVE
