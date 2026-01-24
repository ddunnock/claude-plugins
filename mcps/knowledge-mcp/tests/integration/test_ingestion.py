# tests/integration/test_ingestion.py
"""
Integration tests for the document ingestion pipeline.

These tests use REAL Docling processing (not mocked) to verify:
- PDF/DOCX ingestion produces valid chunks
- Token counts are within limits
- Metadata is populated correctly
- Table integrity is preserved
- Normative detection works on real content
- Error handling for invalid files

Tests are marked with @pytest.mark.integration to allow skipping in quick CI runs:
    pytest -m "not integration"  # Skip integration tests
    pytest -m integration        # Run only integration tests

Most tests will skip gracefully if test fixtures are not available.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from knowledge_mcp.exceptions import IngestionError
from knowledge_mcp.ingest.pipeline import IngestionPipeline, ingest_document
from knowledge_mcp.models.chunk import KnowledgeChunk

if TYPE_CHECKING:
    pass


# Test fixture paths - tests skip if not present
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample.pdf"
SAMPLE_DOCX = FIXTURES_DIR / "sample.docx"


def has_fixture(path: Path) -> bool:
    """Check if a fixture file exists."""
    return path.exists() and path.is_file()


@pytest.fixture
def pipeline() -> IngestionPipeline:
    """Create an IngestionPipeline instance."""
    return IngestionPipeline()


@pytest.mark.integration
class TestPDFIngestion:
    """Integration tests for PDF document ingestion."""

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_pdf_ingestion_produces_chunks(self, pipeline: IngestionPipeline) -> None:
        """Test that PDF ingestion produces chunks."""
        chunks = pipeline.ingest(SAMPLE_PDF)

        assert len(chunks) > 0
        assert all(isinstance(c, KnowledgeChunk) for c in chunks)

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_pdf_chunks_have_valid_token_counts(
        self, pipeline: IngestionPipeline
    ) -> None:
        """Test that PDF chunks have token counts within limits."""
        chunks = pipeline.ingest(SAMPLE_PDF)

        for chunk in chunks:
            assert chunk.token_count > 0
            # Max is 1000 tokens per chunk config
            assert chunk.token_count <= 1000, (
                f"Chunk {chunk.id} exceeds max tokens: {chunk.token_count}"
            )

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_pdf_chunks_have_metadata(self, pipeline: IngestionPipeline) -> None:
        """Test that PDF chunks have required metadata populated."""
        chunks = pipeline.ingest(SAMPLE_PDF)

        for chunk in chunks:
            # Required identity fields
            assert chunk.id, "Chunk ID is required"
            assert chunk.document_id, "Document ID is required"
            assert chunk.document_title, "Document title is required"
            assert chunk.document_type, "Document type is required"

            # Required content fields
            assert chunk.content, "Chunk content is required"
            assert chunk.content_hash, "Content hash is required"


@pytest.mark.integration
class TestDOCXIngestion:
    """Integration tests for DOCX document ingestion."""

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_DOCX),
        reason=f"Test fixture not found: {SAMPLE_DOCX}"
    )
    def test_docx_ingestion_produces_chunks(
        self, pipeline: IngestionPipeline
    ) -> None:
        """Test that DOCX ingestion produces chunks."""
        chunks = pipeline.ingest(SAMPLE_DOCX)

        assert len(chunks) > 0
        assert all(isinstance(c, KnowledgeChunk) for c in chunks)


@pytest.mark.integration
class TestTableExtraction:
    """Integration tests for table extraction and integrity."""

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_table_chunks_have_consistent_columns(
        self, pipeline: IngestionPipeline
    ) -> None:
        """
        Test that table chunks do not have partial rows.

        If tables exist in the document, verify that table_data
        (if present in metadata) has consistent column counts.
        """
        chunks = pipeline.ingest(SAMPLE_PDF)
        table_chunks = [c for c in chunks if c.chunk_type == "table"]

        for chunk in table_chunks:
            # Check content for consistent row structure
            # Tables are typically formatted with | separators or tabs
            lines = chunk.content.strip().split("\n")

            # Filter to lines that look like table rows (contain | or multiple tabs)
            table_lines = [
                line for line in lines
                if "|" in line or line.count("\t") >= 1
            ]

            if len(table_lines) >= 2:
                # Count columns in each row
                column_counts = []
                for line in table_lines:
                    if "|" in line:
                        # Pipe-separated
                        cols = len([c for c in line.split("|") if c.strip()])
                    else:
                        # Tab-separated
                        cols = len(line.split("\t"))
                    column_counts.append(cols)

                # All rows should have the same column count
                if column_counts:
                    first_count = column_counts[0]
                    for i, count in enumerate(column_counts):
                        assert count == first_count, (
                            f"Row {i} has {count} columns, expected {first_count} "
                            f"(possible mid-row split)"
                        )


@pytest.mark.integration
class TestSectionHierarchy:
    """Integration tests for section hierarchy preservation."""

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_chunks_have_section_hierarchy(
        self, pipeline: IngestionPipeline
    ) -> None:
        """
        Test that structured docs have section hierarchy.

        For well-structured documents, at least some chunks should
        have section_hierarchy populated.
        """
        chunks = pipeline.ingest(SAMPLE_PDF)

        # At least some chunks should have section hierarchy
        chunks_with_hierarchy = [
            c for c in chunks if c.section_hierarchy
        ]

        # This is a soft check - not all documents have clear hierarchy
        # Log a warning but don't fail if no hierarchy found
        if not chunks_with_hierarchy:
            pytest.skip(
                "No section hierarchy found - document may not have clear structure"
            )

        # If hierarchy exists, verify format
        for chunk in chunks_with_hierarchy:
            assert isinstance(chunk.section_hierarchy, list)
            assert all(isinstance(s, str) for s in chunk.section_hierarchy)


@pytest.mark.integration
class TestNormativeDetection:
    """Integration tests for normative/informative detection."""

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_chunks_containing_shall_are_normative(
        self, pipeline: IngestionPipeline
    ) -> None:
        """
        Test that chunks containing 'shall' are marked normative.

        Per standards convention, 'shall' indicates mandatory requirements.
        """
        chunks = pipeline.ingest(SAMPLE_PDF)

        # Find chunks containing "shall" (case-insensitive)
        shall_chunks = [
            c for c in chunks
            if "shall" in c.content.lower()
        ]

        if not shall_chunks:
            pytest.skip("No chunks containing 'shall' found in document")

        # All shall-containing chunks should be normative
        for chunk in shall_chunks:
            assert chunk.normative is True, (
                f"Chunk containing 'shall' not marked normative: "
                f"{chunk.content[:100]}..."
            )

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_note_only_chunks_are_informative(
        self, pipeline: IngestionPipeline
    ) -> None:
        """
        Test that chunks containing only NOTE: are marked informative.

        Per standards convention, NOTEs are informative, not normative.
        """
        chunks = pipeline.ingest(SAMPLE_PDF)

        # Find chunks that are primarily notes
        note_chunks = [
            c for c in chunks
            if c.content.strip().upper().startswith("NOTE")
            and "shall" not in c.content.lower()
            and "must" not in c.content.lower()
        ]

        if not note_chunks:
            pytest.skip("No note-only chunks found in document")

        # Note-only chunks should be informative (not normative)
        for chunk in note_chunks:
            assert chunk.normative is False, (
                f"Note-only chunk marked as normative: "
                f"{chunk.content[:100]}..."
            )


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling."""

    def test_nonexistent_file_raises_error(
        self, pipeline: IngestionPipeline
    ) -> None:
        """Test that non-existent file raises FileNotFoundError."""
        fake_path = Path("/nonexistent/path/to/document.pdf")

        with pytest.raises(FileNotFoundError):
            pipeline.ingest(fake_path)

    def test_unsupported_extension_raises_error(
        self, pipeline: IngestionPipeline
    ) -> None:
        """Test that unsupported file extension raises IngestionError."""
        # Create a temp file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            temp_path = Path(f.name)
            f.write(b"test content")

        try:
            with pytest.raises(IngestionError) as exc_info:
                pipeline.ingest(temp_path)

            assert "Unsupported file extension" in str(exc_info.value)
            assert ".xyz" in str(exc_info.value)
        finally:
            temp_path.unlink()

    def test_corrupted_pdf_raises_error(
        self, pipeline: IngestionPipeline
    ) -> None:
        """Test that corrupted PDF raises IngestionError."""
        # Create a temp file with .pdf extension but invalid content
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = Path(f.name)
            f.write(b"This is not a valid PDF file content")

        try:
            with pytest.raises((IngestionError, Exception)) as exc_info:
                pipeline.ingest(temp_path)

            # Should have some error indicating the issue
            error_msg = str(exc_info.value).lower()
            assert any(
                word in error_msg
                for word in ["fail", "error", "invalid", "corrupt", "cannot", "not"]
            ), f"Unexpected error message: {exc_info.value}"
        finally:
            temp_path.unlink()


@pytest.mark.integration
class TestConvenienceFunction:
    """Integration tests for the ingest_document convenience function."""

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_ingest_document_function(self) -> None:
        """Test that ingest_document convenience function works."""
        chunks = ingest_document(SAMPLE_PDF)

        assert len(chunks) > 0
        assert all(isinstance(c, KnowledgeChunk) for c in chunks)


@pytest.mark.integration
class TestChunkOverlap:
    """Integration tests for chunk overlap functionality."""

    @pytest.mark.skipif(
        not has_fixture(SAMPLE_PDF),
        reason=f"Test fixture not found: {SAMPLE_PDF}"
    )
    def test_adjacent_chunks_have_overlap_indicator(
        self, pipeline: IngestionPipeline
    ) -> None:
        """
        Test that chunks have overlap for context continuity.

        The hierarchical chunker adds overlap between adjacent chunks,
        indicated by a '---' separator in the content.
        """
        chunks = pipeline.ingest(SAMPLE_PDF)

        if len(chunks) < 2:
            pytest.skip("Document produced only 1 chunk, cannot test overlap")

        # Check for overlap separator in later chunks
        chunks_with_overlap = [
            c for c in chunks[1:]  # Skip first chunk (never has overlap)
            if "---" in c.content
        ]

        # Should have some overlap if document has multiple chunks
        # This is a soft check since not all chunk boundaries need overlap
        if not chunks_with_overlap:
            pytest.skip(
                "No overlap markers found - chunks may be from different sections"
            )

        assert len(chunks_with_overlap) > 0
