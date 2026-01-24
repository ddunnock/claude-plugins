"""Unit tests for ingestion pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from knowledge_mcp.chunk.base import ChunkResult
from knowledge_mcp.exceptions import IngestionError
from knowledge_mcp.ingest.base import ParsedDocument, ParsedElement
from knowledge_mcp.ingest.pipeline import IngestionPipeline, ingest_document
from knowledge_mcp.models.chunk import KnowledgeChunk
from knowledge_mcp.models.document import DocumentMetadata


class TestIngestionPipeline:
    """Tests for IngestionPipeline class."""

    def test_initialization(self) -> None:
        """Test that pipeline initializes with correct ingestors."""
        pipeline = IngestionPipeline()

        assert ".pdf" in pipeline.ingestors
        assert ".docx" in pipeline.ingestors
        assert pipeline.chunker is not None

    def test_unsupported_file_extension(self) -> None:
        """Test that unsupported extension raises IngestionError."""
        pipeline = IngestionPipeline()
        file_path = Path("/tmp/document.txt")

        with pytest.raises(IngestionError, match="Unsupported file extension"):
            pipeline.ingest(file_path)

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_pdf_ingestor_selection(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test that .pdf files use PDFIngestor."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor

        # Create mock parsed document
        metadata = DocumentMetadata(
            document_id="test-doc",
            title="Test Document",
            document_type="standard",
            source_path="/tmp/test.pdf",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="paragraph",
                    content="Test content",
                    section_hierarchy=[],
                )
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(
                content="Test content",
                token_count=2,
                section_hierarchy=[],
                chunk_type="text",
            )
        ]

        # Act
        pipeline = IngestionPipeline()
        file_path = Path("/tmp/test.pdf")

        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(file_path)

        # Assert
        assert len(chunks) > 0
        assert isinstance(chunks[0], KnowledgeChunk)

    @patch("knowledge_mcp.ingest.pipeline.DOCXIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_docx_ingestor_selection(
        self,
        mock_chunker_class: Mock,
        mock_docx_ingestor_class: Mock,
    ) -> None:
        """Test that .docx files use DOCXIngestor."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_docx_ingestor_class.return_value = mock_ingestor

        # Create mock parsed document
        metadata = DocumentMetadata(
            document_id="test-doc",
            title="Test Document",
            document_type="standard",
            source_path="/tmp/test.docx",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="paragraph",
                    content="Test content",
                    section_hierarchy=[],
                )
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(
                content="Test content",
                token_count=2,
                section_hierarchy=[],
                chunk_type="text",
            )
        ]

        # Act
        pipeline = IngestionPipeline()
        file_path = Path("/tmp/test.docx")

        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(file_path)

        # Assert
        assert len(chunks) > 0
        assert isinstance(chunks[0], KnowledgeChunk)

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_full_pipeline_flow(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test full pipeline flow from parse to enriched chunks."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor

        # Create mock parsed document with multiple elements
        metadata = DocumentMetadata(
            document_id="ieee-15288-2014",
            title="IEEE 15288.2-2014",
            document_type="standard",
            source_path="/tmp/ieee-15288.pdf",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="heading",
                    content="5. Requirements",
                    section_hierarchy=[],
                    page_number=12,
                ),
                ParsedElement(
                    element_type="paragraph",
                    content="The system SHALL verify all inputs.",
                    section_hierarchy=["5. Requirements"],
                    page_number=12,
                ),
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        # Mock chunker
        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(
                content="5. Requirements",
                token_count=2,
                section_hierarchy=[],
                clause_number="5",
                page_numbers=[12],
                chunk_type="text",
            ),
            ChunkResult(
                content="The system SHALL verify all inputs.",
                token_count=6,
                section_hierarchy=["5. Requirements"],
                clause_number="5",
                page_numbers=[12],
                chunk_type="text",
            ),
        ]

        # Act
        pipeline = IngestionPipeline()
        file_path = Path("/tmp/ieee-15288.pdf")

        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(file_path)

        # Assert
        assert len(chunks) == 2

        # Verify first chunk
        chunk1 = chunks[0]
        assert chunk1.document_id == "ieee-15288-2014"
        assert chunk1.document_title == "IEEE 15288.2-2014"
        assert chunk1.document_type == "standard"
        assert chunk1.content == "5. Requirements"
        assert chunk1.token_count == 2
        assert chunk1.clause_number == "5"
        assert chunk1.page_numbers == [12]
        assert chunk1.id is not None  # UUID generated
        assert chunk1.content_hash is not None  # Hash computed

        # Verify second chunk (normative)
        chunk2 = chunks[1]
        assert chunk2.content == "The system SHALL verify all inputs."
        assert chunk2.normative is True  # Contains "SHALL"
        assert chunk2.section_hierarchy == ["5. Requirements"]
        assert chunk2.section_title == "5. Requirements"

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_content_hash_computed(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test that content_hash is computed for each chunk."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor

        metadata = DocumentMetadata(
            document_id="test-doc",
            title="Test",
            document_type="standard",
            source_path="/tmp/test.pdf",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="paragraph",
                    content="Test content",
                    section_hierarchy=[],
                )
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(
                content="Test content",
                token_count=2,
                section_hierarchy=[],
                chunk_type="text",
            )
        ]

        # Act
        pipeline = IngestionPipeline()
        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(Path("/tmp/test.pdf"))

        # Assert
        assert len(chunks) == 1
        assert chunks[0].content_hash is not None
        assert len(chunks[0].content_hash) == 64  # SHA-256 hex digest length

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_normative_detection_shall(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test normative detection with SHALL keyword."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor

        metadata = DocumentMetadata(
            document_id="test-doc",
            title="Test",
            document_type="standard",
            source_path="/tmp/test.pdf",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="paragraph",
                    content="The system SHALL comply with requirements.",
                    section_hierarchy=[],
                )
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(
                content="The system SHALL comply with requirements.",
                token_count=6,
                section_hierarchy=[],
                chunk_type="text",
            )
        ]

        # Act
        pipeline = IngestionPipeline()
        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(Path("/tmp/test.pdf"))

        # Assert
        assert chunks[0].normative is True

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_normative_detection_note(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test normative detection with NOTE keyword (informative)."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor

        metadata = DocumentMetadata(
            document_id="test-doc",
            title="Test",
            document_type="standard",
            source_path="/tmp/test.pdf",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="paragraph",
                    content="NOTE: This is for guidance only.",
                    section_hierarchy=[],
                )
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(
                content="NOTE: This is for guidance only.",
                token_count=6,
                section_hierarchy=[],
                chunk_type="text",
            )
        ]

        # Act
        pipeline = IngestionPipeline()
        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(Path("/tmp/test.pdf"))

        # Assert
        assert chunks[0].normative is False

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_uuid_generated(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test that UUID is generated for each chunk."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor

        metadata = DocumentMetadata(
            document_id="test-doc",
            title="Test",
            document_type="standard",
            source_path="/tmp/test.pdf",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="paragraph",
                    content="Test 1",
                    section_hierarchy=[],
                ),
                ParsedElement(
                    element_type="paragraph",
                    content="Test 2",
                    section_hierarchy=[],
                ),
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(content="Test 1", token_count=2, chunk_type="text"),
            ChunkResult(content="Test 2", token_count=2, chunk_type="text"),
        ]

        # Act
        pipeline = IngestionPipeline()
        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(Path("/tmp/test.pdf"))

        # Assert
        assert len(chunks) == 2
        assert chunks[0].id != chunks[1].id  # Different UUIDs
        assert len(chunks[0].id) == 36  # UUID format

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_document_metadata_populated(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test that document metadata is populated in chunks."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor

        metadata = DocumentMetadata(
            document_id="ieee-15288-2014",
            title="IEEE 15288.2-2014",
            document_type="standard",
            source_path="/data/sources/ieee-15288.pdf",
        )
        parsed_doc = ParsedDocument(
            metadata=metadata,
            elements=[
                ParsedElement(
                    element_type="paragraph",
                    content="Test content",
                    section_hierarchy=[],
                )
            ],
        )
        mock_ingestor.ingest.return_value = parsed_doc

        mock_chunker = MagicMock()
        mock_chunker_class.return_value = mock_chunker
        mock_chunker.chunk.return_value = [
            ChunkResult(content="Test content", token_count=2, chunk_type="text")
        ]

        # Act
        pipeline = IngestionPipeline()
        with patch.object(Path, "exists", return_value=True):
            chunks = pipeline.ingest(Path("/tmp/test.pdf"))

        # Assert
        assert chunks[0].document_id == "ieee-15288-2014"
        assert chunks[0].document_title == "IEEE 15288.2-2014"
        assert chunks[0].document_type == "standard"

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    def test_file_not_found_propagates(
        self,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test that FileNotFoundError propagates from ingestor."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor
        mock_ingestor.ingest.side_effect = FileNotFoundError("File not found")

        # Act & Assert
        pipeline = IngestionPipeline()
        with pytest.raises(FileNotFoundError):
            pipeline.ingest(Path("/nonexistent/file.pdf"))

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    def test_ingestion_error_propagates(
        self,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test that IngestionError propagates from ingestor."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor
        mock_ingestor.ingest.side_effect = IngestionError("Parse failed")

        # Act & Assert
        pipeline = IngestionPipeline()
        with pytest.raises(IngestionError, match="Parse failed"):
            pipeline.ingest(Path("/tmp/test.pdf"))

    @patch("knowledge_mcp.ingest.pipeline.PDFIngestor")
    @patch("knowledge_mcp.ingest.pipeline.HierarchicalChunker")
    def test_generic_exception_wrapped(
        self,
        mock_chunker_class: Mock,
        mock_pdf_ingestor_class: Mock,
    ) -> None:
        """Test that generic exceptions are wrapped in IngestionError."""
        # Arrange
        mock_ingestor = MagicMock()
        mock_pdf_ingestor_class.return_value = mock_ingestor
        mock_ingestor.ingest.side_effect = ValueError("Unexpected error")

        # Act & Assert
        pipeline = IngestionPipeline()
        with pytest.raises(IngestionError, match="Failed to process document"):
            pipeline.ingest(Path("/tmp/test.pdf"))


class TestIngestDocumentFunction:
    """Tests for ingest_document convenience function."""

    @patch("knowledge_mcp.ingest.pipeline.IngestionPipeline")
    def test_ingest_document_creates_pipeline(
        self,
        mock_pipeline_class: Mock,
    ) -> None:
        """Test that ingest_document creates pipeline and calls ingest."""
        # Arrange
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.ingest.return_value = [
            KnowledgeChunk(
                id="test-id",
                document_id="test-doc",
                document_title="Test",
                document_type="standard",
                content="Test content",
                content_hash="abc123",
                token_count=2,
            )
        ]

        # Act
        chunks = ingest_document(Path("/tmp/test.pdf"))

        # Assert
        mock_pipeline_class.assert_called_once()
        mock_pipeline.ingest.assert_called_once()
        assert len(chunks) == 1
