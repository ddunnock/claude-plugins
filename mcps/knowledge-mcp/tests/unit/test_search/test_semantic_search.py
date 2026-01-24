# tests/unit/test_search/test_semantic_search.py
"""
Unit tests for SemanticSearcher.

Tests cover:
- Basic search returning results
- Empty/whitespace query handling
- Filter forwarding to store
- Parameter forwarding (n_results, score_threshold)
- Error handling (embedder/store failures)
- Metadata transformation to SearchResult

Uses AAA pattern (Arrange-Act-Assert) per testing.md.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.search import SearchResult, SemanticSearcher


class TestSemanticSearcherSearch:
    """Tests for SemanticSearcher.search method."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create mock embedder returning sample embedding."""
        embedder = AsyncMock()
        embedder.embed.return_value = [0.1] * 1536
        return embedder

    @pytest.fixture
    def sample_store_result(self) -> dict[str, Any]:
        """Create sample result dict matching store.search() output format."""
        return {
            "id": "chunk-1",
            "content": "Test content about SRR",
            "score": 0.92,
            "metadata": {
                "document_id": "ieee-15288",
                "document_title": "IEEE 15288.2",
                "document_type": "standard",
                "section_title": "System Requirements Review",
                "section_hierarchy": ["5", "5.3", "5.3.1"],
                "chunk_type": "requirement",
                "normative": True,
                "clause_number": "5.3.1",
                "page_numbers": [42, 43],
            },
        }

    @pytest.fixture
    def mock_store(self, sample_store_result: dict[str, Any]) -> MagicMock:
        """Create mock store returning sample results."""
        store = MagicMock()
        store.search.return_value = [sample_store_result]
        return store

    @pytest.fixture
    def searcher(self, mock_embedder: AsyncMock, mock_store: MagicMock) -> SemanticSearcher:
        """Create SemanticSearcher with mocked dependencies."""
        return SemanticSearcher(mock_embedder, mock_store)

    @pytest.mark.asyncio
    async def test_search_returns_results(
        self,
        searcher: SemanticSearcher,
        mock_embedder: AsyncMock,
        mock_store: MagicMock,
    ) -> None:
        """Test that search returns properly formatted SearchResult objects."""
        # Act
        results = await searcher.search("SRR requirements")

        # Assert
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].content == "Test content about SRR"
        assert results[0].score == 0.92
        assert results[0].document_title == "IEEE 15288.2"
        assert results[0].normative is True

    @pytest.mark.asyncio
    async def test_search_calls_embedder_with_query(
        self,
        searcher: SemanticSearcher,
        mock_embedder: AsyncMock,
    ) -> None:
        """Test that search calls embedder.embed() with the query string."""
        # Act
        await searcher.search("SRR requirements")

        # Assert
        mock_embedder.embed.assert_called_once_with("SRR requirements")

    @pytest.mark.asyncio
    async def test_search_calls_store_with_embedding(
        self,
        searcher: SemanticSearcher,
        mock_embedder: AsyncMock,
        mock_store: MagicMock,
    ) -> None:
        """Test that search calls store.search() with embedding and parameters."""
        # Arrange
        expected_embedding = [0.1] * 1536

        # Act
        await searcher.search("SRR requirements", n_results=5)

        # Assert
        mock_store.search.assert_called_once()
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["query_embedding"] == expected_embedding
        assert call_kwargs["n_results"] == 5

    @pytest.mark.asyncio
    async def test_search_transforms_metadata_to_search_result(
        self,
        searcher: SemanticSearcher,
    ) -> None:
        """Test that metadata fields are correctly mapped to SearchResult."""
        # Act
        results = await searcher.search("test query")

        # Assert
        result = results[0]
        assert result.id == "chunk-1"
        assert result.document_id == "ieee-15288"
        assert result.document_title == "IEEE 15288.2"
        assert result.document_type == "standard"
        assert result.section_title == "System Requirements Review"
        assert result.section_hierarchy == ["5", "5.3", "5.3.1"]
        assert result.chunk_type == "requirement"
        assert result.normative is True
        assert result.clause_number == "5.3.1"
        assert result.page_numbers == [42, 43]


class TestSemanticSearcherEmptyHandling:
    """Tests for empty query and no results handling."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create mock embedder."""
        embedder = AsyncMock()
        embedder.embed.return_value = [0.1] * 1536
        return embedder

    @pytest.fixture
    def mock_store(self) -> MagicMock:
        """Create mock store returning empty results."""
        store = MagicMock()
        store.search.return_value = []
        return store

    @pytest.fixture
    def searcher(self, mock_embedder: AsyncMock, mock_store: MagicMock) -> SemanticSearcher:
        """Create SemanticSearcher with mocked dependencies."""
        return SemanticSearcher(mock_embedder, mock_store)

    @pytest.mark.asyncio
    async def test_empty_query_returns_empty_list(
        self,
        searcher: SemanticSearcher,
        mock_embedder: AsyncMock,
    ) -> None:
        """Test that empty string query returns empty list without calling embedder."""
        # Act
        results = await searcher.search("")

        # Assert
        assert results == []
        mock_embedder.embed.assert_not_called()

    @pytest.mark.asyncio
    async def test_whitespace_query_returns_empty_list(
        self,
        searcher: SemanticSearcher,
        mock_embedder: AsyncMock,
    ) -> None:
        """Test that whitespace-only query returns empty list."""
        # Act
        results = await searcher.search("   ")

        # Assert
        assert results == []
        mock_embedder.embed.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_results_returns_empty_list(
        self,
        searcher: SemanticSearcher,
        mock_store: MagicMock,
    ) -> None:
        """Test that no matches returns empty list (not error)."""
        # Arrange
        mock_store.search.return_value = []

        # Act
        results = await searcher.search("nonexistent topic xyz")

        # Assert
        assert results == []


class TestSemanticSearcherFiltering:
    """Tests for filter and parameter forwarding."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create mock embedder."""
        embedder = AsyncMock()
        embedder.embed.return_value = [0.1] * 1536
        return embedder

    @pytest.fixture
    def mock_store(self) -> MagicMock:
        """Create mock store."""
        store = MagicMock()
        store.search.return_value = []
        return store

    @pytest.fixture
    def searcher(self, mock_embedder: AsyncMock, mock_store: MagicMock) -> SemanticSearcher:
        """Create SemanticSearcher with mocked dependencies."""
        return SemanticSearcher(mock_embedder, mock_store)

    @pytest.mark.asyncio
    async def test_filter_dict_passed_to_store(
        self,
        searcher: SemanticSearcher,
        mock_store: MagicMock,
    ) -> None:
        """Test that filter_dict is forwarded to store.search()."""
        # Arrange
        filter_dict = {"document_type": "standard", "normative": True}

        # Act
        await searcher.search("test", filter_dict=filter_dict)

        # Assert
        mock_store.search.assert_called_once()
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["filter_dict"] == filter_dict

    @pytest.mark.asyncio
    async def test_score_threshold_passed_to_store(
        self,
        searcher: SemanticSearcher,
        mock_store: MagicMock,
    ) -> None:
        """Test that score_threshold is forwarded to store.search()."""
        # Arrange
        score_threshold = 0.75

        # Act
        await searcher.search("test", score_threshold=score_threshold)

        # Assert
        mock_store.search.assert_called_once()
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["score_threshold"] == score_threshold

    @pytest.mark.asyncio
    async def test_n_results_passed_to_store(
        self,
        searcher: SemanticSearcher,
        mock_store: MagicMock,
    ) -> None:
        """Test that n_results is forwarded to store.search()."""
        # Arrange
        n_results = 20

        # Act
        await searcher.search("test", n_results=n_results)

        # Assert
        mock_store.search.assert_called_once()
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["n_results"] == n_results


class TestSemanticSearcherErrorHandling:
    """Tests for error handling and graceful degradation."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create mock embedder."""
        embedder = AsyncMock()
        embedder.embed.return_value = [0.1] * 1536
        return embedder

    @pytest.fixture
    def mock_store(self) -> MagicMock:
        """Create mock store."""
        store = MagicMock()
        store.search.return_value = []
        return store

    @pytest.fixture
    def searcher(self, mock_embedder: AsyncMock, mock_store: MagicMock) -> SemanticSearcher:
        """Create SemanticSearcher with mocked dependencies."""
        return SemanticSearcher(mock_embedder, mock_store)

    @pytest.mark.asyncio
    async def test_embedder_error_returns_empty_list(
        self,
        searcher: SemanticSearcher,
        mock_embedder: AsyncMock,
    ) -> None:
        """Test that embedder error returns empty list (graceful degradation)."""
        # Arrange
        mock_embedder.embed.side_effect = Exception("Embedding API error")

        # Act
        results = await searcher.search("test query")

        # Assert
        assert results == []

    @pytest.mark.asyncio
    async def test_store_error_returns_empty_list(
        self,
        searcher: SemanticSearcher,
        mock_store: MagicMock,
    ) -> None:
        """Test that store error returns empty list (graceful degradation)."""
        # Arrange
        mock_store.search.side_effect = Exception("Vector store connection error")

        # Act
        results = await searcher.search("test query")

        # Assert
        assert results == []


class TestSemanticSearcherMetadataDefaults:
    """Tests for handling missing metadata fields."""

    @pytest.fixture
    def mock_embedder(self) -> AsyncMock:
        """Create mock embedder."""
        embedder = AsyncMock()
        embedder.embed.return_value = [0.1] * 1536
        return embedder

    @pytest.fixture
    def mock_store_minimal(self) -> MagicMock:
        """Create mock store returning minimal result (no metadata)."""
        store = MagicMock()
        store.search.return_value = [
            {
                "id": "chunk-minimal",
                "content": "Minimal content",
                "score": 0.5,
                "metadata": {},
            }
        ]
        return store

    @pytest.fixture
    def searcher_minimal(
        self, mock_embedder: AsyncMock, mock_store_minimal: MagicMock
    ) -> SemanticSearcher:
        """Create SemanticSearcher with minimal metadata store."""
        return SemanticSearcher(mock_embedder, mock_store_minimal)

    @pytest.mark.asyncio
    async def test_missing_metadata_uses_defaults(
        self,
        searcher_minimal: SemanticSearcher,
    ) -> None:
        """Test that missing metadata fields use sensible defaults."""
        # Act
        results = await searcher_minimal.search("test")

        # Assert
        result = results[0]
        assert result.id == "chunk-minimal"
        assert result.content == "Minimal content"
        assert result.score == 0.5
        assert result.document_id == ""
        assert result.document_title == ""
        assert result.document_type == ""
        assert result.section_title == ""
        assert result.section_hierarchy == []
        assert result.chunk_type == ""
        assert result.normative is False
        assert result.clause_number is None
        assert result.page_numbers == []
