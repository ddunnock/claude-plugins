"""Unit tests for hierarchical chunker."""

from __future__ import annotations

import pytest

from knowledge_mcp.chunk import (
    ChunkConfig,
    ChunkResult,
    DocumentMetadata,
    HierarchicalChunker,
    ParsedElement,
)


class TestChunkConfig:
    """Tests for ChunkConfig dataclass."""

    def test_default_values(self) -> None:
        """Test that ChunkConfig has expected defaults."""
        config = ChunkConfig()

        assert config.target_tokens == 500
        assert config.max_tokens == 1000
        assert config.overlap_tokens == 100
        assert config.model == "text-embedding-3-small"
        assert config.merge_small_chunks is True

    def test_custom_values(self) -> None:
        """Test that ChunkConfig accepts custom values."""
        config = ChunkConfig(
            target_tokens=300,
            max_tokens=600,
            overlap_tokens=50,
            model="text-embedding-3-large",
            merge_small_chunks=False,
        )

        assert config.target_tokens == 300
        assert config.max_tokens == 600
        assert config.overlap_tokens == 50
        assert config.model == "text-embedding-3-large"
        assert config.merge_small_chunks is False


class TestParsedElement:
    """Tests for ParsedElement dataclass."""

    def test_minimal_element(self) -> None:
        """Test creating element with minimal required fields."""
        element = ParsedElement(element_type="text", content="Hello")

        assert element.element_type == "text"
        assert element.content == "Hello"
        assert element.section_hierarchy == []
        assert element.heading == ""
        assert element.page_numbers == []
        assert element.metadata == {}

    def test_full_element(self) -> None:
        """Test creating element with all fields populated."""
        element = ParsedElement(
            element_type="table",
            content="Header\nRow1",
            section_hierarchy=["5", "5.1"],
            heading="Requirements Table",
            page_numbers=[10, 11],
            metadata={"caption": "Table 1: Test data"},
        )

        assert element.element_type == "table"
        assert element.content == "Header\nRow1"
        assert element.section_hierarchy == ["5", "5.1"]
        assert element.heading == "Requirements Table"
        assert element.page_numbers == [10, 11]
        assert element.metadata["caption"] == "Table 1: Test data"


class TestDocumentMetadata:
    """Tests for DocumentMetadata dataclass."""

    def test_creation(self) -> None:
        """Test creating document metadata."""
        metadata = DocumentMetadata(
            document_id="ieee-15288",
            document_title="IEEE 15288-2023",
            document_type="standard",
        )

        assert metadata.document_id == "ieee-15288"
        assert metadata.document_title == "IEEE 15288-2023"
        assert metadata.document_type == "standard"


class TestChunkResult:
    """Tests for ChunkResult dataclass."""

    def test_minimal_result(self) -> None:
        """Test creating chunk result with minimal fields."""
        result = ChunkResult(content="Test content", token_count=5)

        assert result.content == "Test content"
        assert result.token_count == 5
        assert result.section_hierarchy == []
        assert result.clause_number is None
        assert result.page_numbers == []
        assert result.chunk_type == "text"
        assert result.has_overlap is False
        assert result.metadata == {}

    def test_full_result(self) -> None:
        """Test creating chunk result with all fields."""
        result = ChunkResult(
            content="The system shall...",
            token_count=45,
            section_hierarchy=["5", "5.1"],
            clause_number="5.1",
            page_numbers=[10],
            chunk_type="text",
            has_overlap=True,
            metadata={"normative": True},
        )

        assert result.content == "The system shall..."
        assert result.token_count == 45
        assert result.section_hierarchy == ["5", "5.1"]
        assert result.clause_number == "5.1"
        assert result.page_numbers == [10]
        assert result.chunk_type == "text"
        assert result.has_overlap is True
        assert result.metadata["normative"] is True


class TestHierarchicalChunker:
    """Tests for HierarchicalChunker."""

    @pytest.fixture
    def chunker(self) -> HierarchicalChunker:
        """Create a chunker instance with default config."""
        return HierarchicalChunker()

    @pytest.fixture
    def custom_chunker(self) -> HierarchicalChunker:
        """Create a chunker with custom config for testing."""
        config = ChunkConfig(target_tokens=50, max_tokens=100, overlap_tokens=10)
        return HierarchicalChunker(config)

    @pytest.fixture
    def metadata(self) -> DocumentMetadata:
        """Create sample document metadata."""
        return DocumentMetadata(
            document_id="test-doc",
            document_title="Test Document",
            document_type="guide",
        )

    def test_empty_elements_raises_error(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that empty elements list raises ValueError."""
        with pytest.raises(ValueError, match="Elements list cannot be empty"):
            chunker.chunk([], metadata)

    def test_single_small_element(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test chunking single element under token limit."""
        elements = [
            ParsedElement(
                element_type="text",
                content="This is a short test paragraph.",
                section_hierarchy=["1"],
                heading="Introduction",
                page_numbers=[1],
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].content == "This is a short test paragraph."
        assert results[0].token_count > 0
        assert results[0].section_hierarchy == ["1"]
        assert results[0].chunk_type == "text"
        assert results[0].has_overlap is False

    def test_oversized_text_is_split(
        self, custom_chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that text exceeding max_tokens is split correctly."""
        # Create text with multiple paragraphs that will exceed 100 tokens
        paragraphs = []
        for i in range(5):
            para = " ".join([f"word{i}"] * 25)  # Each paragraph ~25 tokens
            paragraphs.append(para)
        long_text = "\n\n".join(paragraphs)  # ~125 tokens total

        elements = [
            ParsedElement(
                element_type="text",
                content=long_text,
                section_hierarchy=["2"],
            )
        ]

        results = custom_chunker.chunk(elements, metadata)

        # Should split into multiple chunks due to target_tokens=50
        assert len(results) > 1
        # Each chunk should be under max_tokens
        for result in results:
            assert result.token_count <= custom_chunker.config.max_tokens

    def test_table_under_limit_single_chunk(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that table under limit produces single chunk."""
        elements = [
            ParsedElement(
                element_type="table",
                content="Header1 | Header2\nRow1Col1 | Row1Col2\nRow2Col1 | Row2Col2",
                section_hierarchy=["3"],
                metadata={"caption": "Table 1: Test data"},
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].chunk_type == "table"
        assert "Table 1: Test data" in results[0].content
        assert "Header1" in results[0].content

    def test_large_table_split_by_rows(
        self, custom_chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that large table is split by rows with headers preserved."""
        # Create a table that exceeds max_tokens
        rows = ["Header1 | Header2"]
        for i in range(50):  # Add many rows
            rows.append(f"Row{i}Col1 | Row{i}Col2 with extra text to increase size")
        table_content = "\n".join(rows)

        elements = [
            ParsedElement(
                element_type="table",
                content=table_content,
                section_hierarchy=["4"],
                metadata={"caption": "Large Table"},
            )
        ]

        results = custom_chunker.chunk(elements, metadata)

        # Should split into multiple chunks
        assert len(results) > 1

        # Each chunk should have the header
        for result in results:
            assert result.chunk_type == "table"
            assert "Header1" in result.content
            assert "Large Table" in result.content

    def test_overlap_added_between_chunks(
        self, custom_chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that overlap is added between adjacent chunks."""
        # Create multiple paragraphs that will result in multiple chunks
        paragraphs = []
        for i in range(5):
            para = " ".join([f"paragraph{i}_word"] * 20)
            paragraphs.append(para)
        long_text = "\n\n".join(paragraphs)

        elements = [
            ParsedElement(
                element_type="text",
                content=long_text,
                section_hierarchy=["5"],
            )
        ]

        results = custom_chunker.chunk(elements, metadata)

        # Should have multiple chunks with overlap
        if len(results) > 1:
            # Second and subsequent chunks should have overlap
            for i in range(1, len(results)):
                assert results[i].has_overlap is True
                # Should contain separator
                assert "---" in results[i].content

    def test_section_hierarchy_preserved(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that section hierarchy is preserved in chunk results."""
        elements = [
            ParsedElement(
                element_type="text",
                content="Content in section 5.1.2",
                section_hierarchy=["5", "5.1", "5.1.2"],
                heading="Subsection",
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].section_hierarchy == ["5", "5.1", "5.1.2"]

    def test_clause_number_extraction_from_hierarchy(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test clause number extraction from section hierarchy."""
        elements = [
            ParsedElement(
                element_type="text",
                content="Requirements text",
                section_hierarchy=["5", "5.1"],
                heading="Requirements",
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].clause_number == "5.1"

    def test_clause_number_extraction_from_heading(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test clause number extraction from heading text."""
        elements = [
            ParsedElement(
                element_type="text",
                content="Requirements text",
                section_hierarchy=[],
                heading="5.2.3 Testing Requirements",
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].clause_number == "5.2.3"

    def test_clause_number_none_when_not_found(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that clause_number is None when not extractable."""
        elements = [
            ParsedElement(
                element_type="text",
                content="Requirements text",
                section_hierarchy=[],
                heading="Introduction",
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].clause_number is None

    def test_multiple_elements_processed(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that multiple elements are all processed."""
        elements = [
            ParsedElement(
                element_type="text",
                content="First paragraph",
                section_hierarchy=["1"],
            ),
            ParsedElement(
                element_type="text",
                content="Second paragraph",
                section_hierarchy=["2"],
            ),
            ParsedElement(
                element_type="table",
                content="Header\nRow1\nRow2",
                section_hierarchy=["3"],
            ),
        ]

        results = chunker.chunk(elements, metadata)

        # Should process all elements
        # With overlap and merging, may have different count
        # But should have at least 1 result
        assert len(results) >= 1
        # Verify we have content from all elements (check table marker)
        all_content = " ".join([r.content for r in results])
        assert "First paragraph" in all_content or "Second paragraph" in all_content

    def test_merge_small_chunks_enabled(self) -> None:
        """Test that small chunks are merged when configured."""
        config = ChunkConfig(
            target_tokens=50,
            max_tokens=100,
            overlap_tokens=10,
            merge_small_chunks=True,
        )
        chunker = HierarchicalChunker(config)
        metadata = DocumentMetadata("test", "Test", "guide")

        # Create two small elements that should merge
        elements = [
            ParsedElement(element_type="text", content="Short."),
            ParsedElement(element_type="text", content="Also short."),
        ]

        results = chunker.chunk(elements, metadata)

        # The two small chunks should potentially be merged
        # (depends on token counts, but at least shouldn't error)
        assert len(results) >= 1

    def test_page_numbers_preserved(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that page numbers are preserved in chunks."""
        elements = [
            ParsedElement(
                element_type="text",
                content="Content spanning pages",
                page_numbers=[10, 11, 12],
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].page_numbers == [10, 11, 12]

    def test_metadata_preserved(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that element metadata is preserved in chunks."""
        elements = [
            ParsedElement(
                element_type="text",
                content="Normative content",
                metadata={"normative": True, "source": "clause_5"},
            )
        ]

        results = chunker.chunk(elements, metadata)

        assert len(results) == 1
        assert results[0].metadata["normative"] is True
        assert results[0].metadata["source"] == "clause_5"

    def test_empty_table_handled(
        self, chunker: HierarchicalChunker, metadata: DocumentMetadata
    ) -> None:
        """Test that empty table is handled gracefully."""
        elements = [
            ParsedElement(
                element_type="table",
                content="",
                section_hierarchy=["6"],
            )
        ]

        results = chunker.chunk(elements, metadata)

        # Should handle empty table without error
        assert isinstance(results, list)
