"""Unit tests for DOCXIngestor."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from docling_core.types.doc.labels import DocItemLabel

from knowledge_mcp.exceptions import IngestionError
from knowledge_mcp.ingest.base import ParsedDocument, ParsedElement
from knowledge_mcp.ingest.docx_ingestor import DOCXIngestor
from knowledge_mcp.models.document import DocumentMetadata


class TestDOCXIngestor:
    """Tests for DOCXIngestor class."""

    def test_supported_extensions(self) -> None:
        """Test that supported_extensions returns correct list."""
        assert DOCXIngestor.supported_extensions() == [".docx"]

    @patch("knowledge_mcp.ingest.docx_ingestor.DocumentConverter")
    def test_ingest_returns_parsed_document(self, mock_converter_class: Mock) -> None:
        """Test that ingest returns ParsedDocument with correct structure."""
        # Arrange
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        # Create mock Docling document
        mock_doc = MagicMock()
        mock_doc.name = "Test Document"

        # Create mock items
        mock_header = MagicMock()
        mock_header.label = DocItemLabel.SECTION_HEADER
        mock_header.text = "Introduction"
        mock_header.prov = []

        mock_paragraph = MagicMock()
        mock_paragraph.label = DocItemLabel.PARAGRAPH
        mock_paragraph.text = "This is a test paragraph."
        mock_paragraph.prov = []

        mock_doc.iterate_items.return_value = [
            (mock_header, 0),
            (mock_paragraph, 1),
        ]

        # Mock converter result
        mock_result = MagicMock()
        mock_result.document = mock_doc
        mock_converter.convert.return_value = mock_result

        # Create ingestor
        ingestor = DOCXIngestor()
        file_path = Path("/tmp/test.docx")

        # Mock file existence
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = ingestor.ingest(file_path)

            # Assert
            assert isinstance(result, ParsedDocument)
            assert isinstance(result.metadata, DocumentMetadata)
            assert result.metadata.document_id == "test"
            assert result.metadata.title == "Introduction"
            assert result.metadata.document_type == "standard"
            assert str(file_path.absolute()) in result.metadata.source_path

            # Check elements
            assert len(result.elements) == 2
            assert result.elements[0].element_type == "heading"
            assert result.elements[0].content == "Introduction"
            assert result.elements[1].element_type == "paragraph"
            assert result.elements[1].content == "This is a test paragraph."

    @patch("knowledge_mcp.ingest.docx_ingestor.DocumentConverter")
    def test_ingest_file_not_found(self, mock_converter_class: Mock) -> None:
        """Test that ingest raises FileNotFoundError when file doesn't exist."""
        # Arrange
        ingestor = DOCXIngestor()
        file_path = Path("/nonexistent/file.docx")

        # Mock file doesn't exist
        with patch.object(Path, "exists", return_value=False):
            # Act & Assert
            with pytest.raises(FileNotFoundError, match="File not found"):
                ingestor.ingest(file_path)

    @patch("knowledge_mcp.ingest.docx_ingestor.DocumentConverter")
    def test_ingest_conversion_error(self, mock_converter_class: Mock) -> None:
        """Test that ingest raises IngestionError when conversion fails."""
        # Arrange
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter
        mock_converter.convert.side_effect = Exception("Conversion failed")

        ingestor = DOCXIngestor()
        file_path = Path("/tmp/test.docx")

        # Mock file exists
        with patch.object(Path, "exists", return_value=True):
            # Act & Assert
            with pytest.raises(IngestionError, match="Failed to parse DOCX"):
                ingestor.ingest(file_path)

    @patch("knowledge_mcp.ingest.docx_ingestor.DocumentConverter")
    def test_extract_table_data(self, mock_converter_class: Mock) -> None:
        """Test that table data is extracted correctly."""
        # Arrange
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        # Create mock Docling document with table
        mock_doc = MagicMock()
        mock_doc.name = "Test Document"

        # Create mock table item
        mock_table = MagicMock()
        mock_table.label = DocItemLabel.TABLE
        mock_table.text = "Table content"
        mock_table.caption = "Table 1: Test table"
        mock_table.prov = []

        # Mock dataframe
        mock_df = MagicMock()
        mock_df.values.tolist.return_value = [
            ["Header1", "Header2"],
            ["Value1", "Value2"],
        ]
        mock_table.export_to_dataframe.return_value = mock_df

        mock_doc.iterate_items.return_value = [(mock_table, 0)]

        # Mock converter result
        mock_result = MagicMock()
        mock_result.document = mock_doc
        mock_converter.convert.return_value = mock_result

        ingestor = DOCXIngestor()
        file_path = Path("/tmp/test.docx")

        # Mock file existence
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = ingestor.ingest(file_path)

            # Assert
            assert len(result.elements) == 1
            table_element = result.elements[0]
            assert table_element.element_type == "table"
            assert table_element.table_data == [
                ["Header1", "Header2"],
                ["Value1", "Value2"],
            ]
            assert table_element.caption == "Table 1: Test table"

    @patch("knowledge_mcp.ingest.docx_ingestor.DocumentConverter")
    def test_extract_page_numbers(self, mock_converter_class: Mock) -> None:
        """Test that page numbers are extracted from provenance."""
        # Arrange
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        # Create mock Docling document
        mock_doc = MagicMock()
        mock_doc.name = "Test Document"

        # Create mock paragraph with page number
        mock_paragraph = MagicMock()
        mock_paragraph.label = DocItemLabel.PARAGRAPH
        mock_paragraph.text = "Content on page 5"

        # Mock provenance with page number
        mock_prov_item = MagicMock()
        mock_prov_item.page_no = 5
        mock_paragraph.prov = [mock_prov_item]

        mock_doc.iterate_items.return_value = [(mock_paragraph, 0)]

        # Mock converter result
        mock_result = MagicMock()
        mock_result.document = mock_doc
        mock_converter.convert.return_value = mock_result

        ingestor = DOCXIngestor()
        file_path = Path("/tmp/test.docx")

        # Mock file existence
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = ingestor.ingest(file_path)

            # Assert
            assert len(result.elements) == 1
            assert result.elements[0].page_number == 5

    @patch("knowledge_mcp.ingest.docx_ingestor.DocumentConverter")
    def test_extract_section_hierarchy(self, mock_converter_class: Mock) -> None:
        """Test that section hierarchy is tracked correctly."""
        # Arrange
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        # Create mock Docling document
        mock_doc = MagicMock()
        mock_doc.name = "Test Document"

        # Create hierarchical headings and paragraph
        mock_h1 = MagicMock()
        mock_h1.label = DocItemLabel.SECTION_HEADER
        mock_h1.text = "1. Introduction"
        mock_h1.prov = []

        mock_h2 = MagicMock()
        mock_h2.label = DocItemLabel.SECTION_HEADER
        mock_h2.text = "1.1 Background"
        mock_h2.prov = []

        mock_para = MagicMock()
        mock_para.label = DocItemLabel.PARAGRAPH
        mock_para.text = "Background paragraph"
        mock_para.prov = []

        mock_doc.iterate_items.return_value = [
            (mock_h1, 0),
            (mock_h2, 1),
            (mock_para, 2),
        ]

        # Mock converter result
        mock_result = MagicMock()
        mock_result.document = mock_doc
        mock_converter.convert.return_value = mock_result

        ingestor = DOCXIngestor()
        file_path = Path("/tmp/test.docx")

        # Mock file existence
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = ingestor.ingest(file_path)

            # Assert
            assert len(result.elements) == 3
            # First heading has empty hierarchy (it's the root)
            assert result.elements[0].section_hierarchy == []
            # Second heading has first heading in hierarchy
            assert result.elements[1].section_hierarchy == ["1. Introduction"]
            # Paragraph has both headings in hierarchy
            assert result.elements[2].section_hierarchy == [
                "1. Introduction",
                "1.1 Background",
            ]

    @patch("knowledge_mcp.ingest.docx_ingestor.DocumentConverter")
    def test_extract_version_from_filename(self, mock_converter_class: Mock) -> None:
        """Test that version is extracted from filename."""
        # Arrange
        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        # Create mock Docling document
        mock_doc = MagicMock()
        mock_doc.name = "IEEE-15288-2014"
        mock_doc.iterate_items.return_value = []

        # Mock converter result
        mock_result = MagicMock()
        mock_result.document = mock_doc
        mock_converter.convert.return_value = mock_result

        ingestor = DOCXIngestor()
        file_path = Path("/tmp/IEEE-15288-2014.docx")

        # Mock file existence
        with patch.object(Path, "exists", return_value=True):
            # Act
            result = ingestor.ingest(file_path)

            # Assert
            assert result.metadata.version == "2014"
            assert result.metadata.document_id == "ieee-15288-2014"
