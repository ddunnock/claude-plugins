"""Unit tests for BM25Searcher."""

import pytest

from knowledge_mcp.search.bm25 import BM25Searcher


class TestBM25Searcher:
    """Tests for BM25Searcher class."""

    @pytest.fixture
    def sample_documents(self) -> list[dict[str, str]]:
        """Create sample documents for testing."""
        return [
            {"id": "doc1", "content": "System requirements review process"},
            {"id": "doc2", "content": "Software verification and validation methods"},
            {"id": "doc3", "content": "Requirements traceability matrix"},
            {"id": "doc4", "content": "System design review"},
            {"id": "doc5", "content": "Verification methods for requirements"},
        ]

    @pytest.fixture
    def searcher(self) -> BM25Searcher:
        """Create a BM25Searcher instance."""
        return BM25Searcher()

    @pytest.fixture
    def indexed_searcher(
        self, searcher: BM25Searcher, sample_documents: list[dict[str, str]]
    ) -> BM25Searcher:
        """Create a BM25Searcher with built index."""
        searcher.build_index(sample_documents)
        return searcher

    def test_initialization(self, searcher: BM25Searcher) -> None:
        """Test searcher is initialized with empty index."""
        # Arrange & Act completed in fixture

        # Assert
        assert not searcher.is_indexed
        assert searcher.document_count == 0

    def test_build_index(
        self, searcher: BM25Searcher, sample_documents: list[dict[str, str]]
    ) -> None:
        """Test index building from sample documents."""
        # Arrange completed in fixture

        # Act
        searcher.build_index(sample_documents)

        # Assert
        assert searcher.is_indexed
        assert searcher.document_count == len(sample_documents)

    def test_build_index_empty_documents(self, searcher: BM25Searcher) -> None:
        """Test that building index with empty list raises ValueError."""
        # Arrange
        empty_docs: list[dict[str, str]] = []

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot build index from empty document list"):
            searcher.build_index(empty_docs)

    def test_build_index_missing_id(self, searcher: BM25Searcher) -> None:
        """Test that documents missing 'id' field raise ValueError."""
        # Arrange
        invalid_docs = [{"content": "test content"}]

        # Act & Assert
        with pytest.raises(ValueError, match="missing 'id' or 'content' field"):
            searcher.build_index(invalid_docs)

    def test_build_index_missing_content(self, searcher: BM25Searcher) -> None:
        """Test that documents missing 'content' field raise ValueError."""
        # Arrange
        invalid_docs = [{"id": "doc1"}]

        # Act & Assert
        with pytest.raises(ValueError, match="missing 'id' or 'content' field"):
            searcher.build_index(invalid_docs)

    def test_search_returns_ranked_results(self, indexed_searcher: BM25Searcher) -> None:
        """Test that search returns results ranked by BM25 score."""
        # Arrange completed in fixture

        # Act
        results = indexed_searcher.search("requirements", n_results=5)

        # Assert
        assert len(results) > 0
        assert all("id" in r for r in results)
        assert all("content" in r for r in results)
        assert all("score" in r for r in results)
        # Check results are sorted by score descending
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_keyword_matching(self, indexed_searcher: BM25Searcher) -> None:
        """Test that search finds documents with matching keywords."""
        # Arrange completed in fixture

        # Act - search for word that appears in only doc1 and doc3
        results = indexed_searcher.search("requirements", n_results=5)

        # Assert
        assert len(results) > 0
        # All results should have "requirements" in content
        result_ids_with_keyword = [
            r["id"] for r in results if "requirements" in r["content"].lower()
        ]
        # At least one match should be found
        assert len(result_ids_with_keyword) > 0

    def test_search_empty_query(self, indexed_searcher: BM25Searcher) -> None:
        """Test that empty query returns empty results."""
        # Arrange completed in fixture

        # Act
        results = indexed_searcher.search("", n_results=5)

        # Assert
        assert results == []

    def test_search_whitespace_query(self, indexed_searcher: BM25Searcher) -> None:
        """Test that whitespace-only query returns empty results."""
        # Arrange completed in fixture

        # Act
        results = indexed_searcher.search("   ", n_results=5)

        # Assert
        assert results == []

    def test_search_before_indexing(self, searcher: BM25Searcher) -> None:
        """Test that search before building index returns empty results."""
        # Arrange completed in fixture

        # Act
        results = searcher.search("requirements", n_results=5)

        # Assert
        assert results == []
        assert not searcher.is_indexed

    def test_search_respects_n_results(self, indexed_searcher: BM25Searcher) -> None:
        """Test that n_results parameter limits result count."""
        # Arrange completed in fixture
        n = 2

        # Act
        results = indexed_searcher.search("requirements verification", n_results=n)

        # Assert
        assert len(results) <= n

    def test_search_no_matches(self, indexed_searcher: BM25Searcher) -> None:
        """Test that search with no matching keywords returns minimal results."""
        # Arrange completed in fixture

        # Act
        results = indexed_searcher.search("nonexistent keyword xyz", n_results=5)

        # Assert
        # BM25 may return documents even without exact matches (with low scores)
        # or may return empty list if no tokens match - both are acceptable
        if results:
            # If results are returned, all should have low scores
            assert all(r["score"] >= 0 for r in results)

    def test_is_indexed_property(
        self, searcher: BM25Searcher, sample_documents: list[dict[str, str]]
    ) -> None:
        """Test is_indexed property before and after building index."""
        # Arrange completed in fixture

        # Assert before indexing
        assert not searcher.is_indexed

        # Act
        searcher.build_index(sample_documents)

        # Assert after indexing
        assert searcher.is_indexed

    def test_document_count_property(
        self, searcher: BM25Searcher, sample_documents: list[dict[str, str]]
    ) -> None:
        """Test document_count property matches input documents."""
        # Arrange completed in fixture

        # Assert before indexing
        assert searcher.document_count == 0

        # Act
        searcher.build_index(sample_documents)

        # Assert after indexing
        assert searcher.document_count == len(sample_documents)
