# tests/unit/test_ingest/test_pdf_ingestor.py
"""Unit tests for PDF ingestor."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from knowledge_mcp.exceptions import IngestionError
from knowledge_mcp.ingest.base import ParsedDocument, ParsedElement
from knowledge_mcp.ingest.pdf_ingestor import PDFIngestor
from knowledge_mcp.models.document import DocumentMetadata


class TestPDFIngestorBasics:
    """Tests for PDFIngestor basic functionality."""

    def test_supported_extensions(self) -> None:
        """Test that supported_extensions returns correct list."""
        extensions = PDFIngestor.supported_extensions()

        assert extensions == [".pdf"]

    def test_ingestor_initialization(self) -> None:
        """Test that PDFIngestor can be initialized."""
        ingestor = PDFIngestor()

        assert ingestor.converter is not None


class TestPDFIngestorFileHandling:
    """Tests for file handling behavior."""

    def test_ingest_file_not_found(self) -> None:
        """Test that ingest raises FileNotFoundError for missing file."""
        ingestor = PDFIngestor()
        nonexistent_path = Path("/nonexistent/file.pdf")

        with pytest.raises(FileNotFoundError):
            ingestor.ingest(nonexistent_path)


class TestPDFIngestorParsing:
    """Tests for PDF parsing with mocked Docling."""

    @pytest.fixture
    def mock_docling_result(self) -> MagicMock:
        """Create a mock Docling conversion result."""
        # Mock the conversion result
        result = MagicMock()

        # Mock the document
        mock_doc = MagicMock()
        mock_doc.name = "Test Document"

        # Mock iterate_items to return test elements
        mock_heading = MagicMock()
        mock_heading.label = MagicMock()
        mock_heading.label.__eq__ = lambda self, other: True  # Match SECTION_HEADER
        mock_heading.text = "Introduction"
        mock_heading.prov = []

        mock_para = MagicMock()
        mock_para.label = MagicMock()
        # Configure label to match PARAGRAPH but not others
        mock_para.label.__eq__ = lambda self, other: str(other) == "paragraph"
        mock_para.text = "This is a test paragraph."
        mock_para.prov = []

        # iterate_items returns tuples of (item, level)
        mock_doc.iterate_items = MagicMock(
            return_value=[
                (mock_heading, 0),
                (mock_para, 0),
            ]
        )

        result.document = mock_doc
        return result

    def test_ingest_returns_parsed_document(
        self, mock_docling_result: MagicMock, tmp_path: Path
    ) -> None:
        """Test that ingest returns ParsedDocument with correct structure."""
        # Create a temporary PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("dummy content")

        ingestor = PDFIngestor()

        # Mock the DocumentConverter
        with patch.object(
            ingestor.converter, "convert", return_value=mock_docling_result
        ):
            result = ingestor.ingest(test_pdf)

        # Verify result structure
        assert isinstance(result, ParsedDocument)
        assert isinstance(result.metadata, DocumentMetadata)
        assert isinstance(result.elements, list)
        assert result.metadata.source_path == str(test_pdf.absolute())

    def test_ingest_extracts_metadata(
        self, mock_docling_result: MagicMock, tmp_path: Path
    ) -> None:
        """Test that metadata is correctly extracted."""
        # Create a temporary PDF file with structured name
        test_pdf = tmp_path / "ieee-15288-2014.pdf"
        test_pdf.write_text("dummy content")

        ingestor = PDFIngestor()

        with patch.object(
            ingestor.converter, "convert", return_value=mock_docling_result
        ):
            result = ingestor.ingest(test_pdf)

        metadata = result.metadata
        assert metadata.document_id == "ieee-15288-2014"
        assert metadata.document_type == "standard"
        assert metadata.version == "2014"  # Extracted from filename
        assert metadata.source_path == str(test_pdf.absolute())

    def test_ingest_populates_section_hierarchy(
        self, mock_docling_result: MagicMock, tmp_path: Path
    ) -> None:
        """Test that section hierarchy is tracked for elements."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("dummy content")

        ingestor = PDFIngestor()

        with patch.object(
            ingestor.converter, "convert", return_value=mock_docling_result
        ):
            result = ingestor.ingest(test_pdf)

        # Verify elements have section_hierarchy attribute
        for element in result.elements:
            assert isinstance(element, ParsedElement)
            assert hasattr(element, "section_hierarchy")
            assert isinstance(element.section_hierarchy, list)

    def test_ingest_handles_parse_errors(self, tmp_path: Path) -> None:
        """Test that parse errors raise IngestionError."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("dummy content")

        ingestor = PDFIngestor()

        # Mock converter to raise an exception
        with patch.object(
            ingestor.converter,
            "convert",
            side_effect=Exception("Docling parse error"),
        ):
            with pytest.raises(IngestionError) as exc_info:
                ingestor.ingest(test_pdf)

            assert "Failed to parse PDF" in str(exc_info.value)


class TestPDFIngestorTableExtraction:
    """Tests for table extraction functionality."""

    @pytest.fixture
    def mock_table_item(self) -> MagicMock:
        """Create a mock table item."""
        table = MagicMock()
        table.label = MagicMock()
        # Configure to match TABLE label
        table.label.__eq__ = lambda self, other: str(other) == "table"
        table.text = "Table content"
        table.prov = []

        # Mock export_to_dataframe
        mock_df = MagicMock()
        mock_df.values.tolist.return_value = [
            ["Header1", "Header2"],
            ["Value1", "Value2"],
        ]
        table.export_to_dataframe = MagicMock(return_value=mock_df)
        table.caption = "Table 1: Test Table"

        return table

    def test_extract_table_data(self, mock_table_item: MagicMock) -> None:
        """Test that table data is extracted as structured data."""
        ingestor = PDFIngestor()

        table_data, caption = ingestor._extract_table_data(mock_table_item)

        assert table_data is not None
        assert len(table_data) == 2
        assert table_data[0] == ["Header1", "Header2"]
        assert table_data[1] == ["Value1", "Value2"]
        assert caption == "Table 1: Test Table"

    def test_extract_table_data_handles_missing_caption(self) -> None:
        """Test table extraction when caption is missing."""
        ingestor = PDFIngestor()

        # Create table without caption
        table = MagicMock()
        table.caption = None
        mock_df = MagicMock()
        mock_df.values.tolist.return_value = [["Data"]]
        table.export_to_dataframe = MagicMock(return_value=mock_df)

        table_data, caption = ingestor._extract_table_data(table)

        assert table_data == [["Data"]]
        assert caption is None


class TestSectionHierarchyTracking:
    """Tests for section hierarchy tracking."""

    def test_update_section_stack_adds_section(self) -> None:
        """Test that update_section_stack correctly adds sections."""
        ingestor = PDFIngestor()
        section_stack: list[str] = []

        ingestor._update_section_stack(section_stack, 1, "Introduction")

        assert section_stack == ["Introduction"]

    def test_update_section_stack_nesting(self) -> None:
        """Test that nested sections are tracked correctly."""
        ingestor = PDFIngestor()
        section_stack: list[str] = ["Introduction"]

        ingestor._update_section_stack(section_stack, 2, "Background")

        assert section_stack == ["Introduction", "Background"]

    def test_update_section_stack_sibling_section(self) -> None:
        """Test that sibling sections replace at same level."""
        ingestor = PDFIngestor()
        section_stack: list[str] = ["Introduction", "Background"]

        # Add sibling at level 2
        ingestor._update_section_stack(section_stack, 2, "Motivation")

        assert section_stack == ["Introduction", "Motivation"]

    def test_update_section_stack_parent_level(self) -> None:
        """Test that returning to parent level trims stack."""
        ingestor = PDFIngestor()
        section_stack: list[str] = ["Introduction", "Background", "Details"]

        # Return to level 1
        ingestor._update_section_stack(section_stack, 1, "Methods")

        assert section_stack == ["Methods"]
