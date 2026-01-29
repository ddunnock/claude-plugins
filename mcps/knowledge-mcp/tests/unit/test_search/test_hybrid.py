"""Unit tests for HybridSearcher and RRF fusion."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.search.bm25 import BM25Searcher
from knowledge_mcp.search.hybrid import HybridSearcher, reciprocal_rank_fusion
from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.semantic_search import SemanticSearcher


class TestReciprocalRankFusion:
    """Tests for reciprocal_rank_fusion function."""

    def test_rrf_merges_single_list(self) -> None:
        """Test RRF with single result list returns same order with scores."""
        # Arrange
        results = [
            {"id": "doc1", "score": 0.9, "content": "test1"},
            {"id": "doc2", "score": 0.7, "content": "test2"},
        ]

        # Act
        merged = reciprocal_rank_fusion([results], k=60)

        # Assert
        assert len(merged) == 2
        assert merged[0]["id"] == "doc1"
        assert merged[1]["id"] == "doc2"
        assert "rrf_score" in merged[0]
        assert "rrf_score" in merged[1]

    def test_rrf_merges_two_lists(self) -> None:
        """Test RRF correctly merges two result lists."""
        # Arrange
        semantic_results = [
            {"id": "doc1", "score": 0.9, "content": "test1"},
            {"id": "doc2", "score": 0.7, "content": "test2"},
        ]
        bm25_results = [
            {"id": "doc2", "score": 5.0, "content": "test2"},
            {"id": "doc3", "score": 3.0, "content": "test3"},
        ]

        # Act
        merged = reciprocal_rank_fusion([semantic_results, bm25_results], k=60)

        # Assert
        assert len(merged) == 3
        # doc2 appears in both lists (rank 2 and rank 1) so should rank highest
        assert merged[0]["id"] == "doc2"
        # Check RRF scores are calculated
        assert merged[0]["rrf_score"] > merged[1]["rrf_score"]

    def test_rrf_calculates_correct_scores(self) -> None:
        """Test RRF calculates scores using correct formula."""
        # Arrange
        results1 = [{"id": "doc1", "content": "test1"}]
        results2 = [{"id": "doc1", "content": "test1"}]
        k = 60

        # Act
        merged = reciprocal_rank_fusion([results1, results2], k=k)

        # Assert
        # doc1 is rank 1 in both lists: RRF = 1/(60+1) + 1/(60+1) = 2/61
        expected_score = 2.0 / (k + 1)
        assert abs(merged[0]["rrf_score"] - expected_score) < 1e-6

    def test_rrf_with_custom_k(self) -> None:
        """Test RRF with custom k parameter."""
        # Arrange
        results = [{"id": "doc1", "content": "test1"}]
        k = 20

        # Act
        merged = reciprocal_rank_fusion([results], k=k)

        # Assert
        # RRF score = 1/(20+1) for rank 1
        expected_score = 1.0 / (k + 1)
        assert abs(merged[0]["rrf_score"] - expected_score) < 1e-6

    def test_rrf_with_empty_lists(self) -> None:
        """Test RRF with empty result lists."""
        # Arrange
        results: list[list[dict[str, str]]] = [[], []]

        # Act
        merged = reciprocal_rank_fusion(results, k=60)

        # Assert
        assert merged == []

    def test_rrf_preserves_metadata(self) -> None:
        """Test RRF preserves metadata from source results."""
        # Arrange
        results = [
            {
                "id": "doc1",
                "content": "test1",
                "metadata": {"source": "test"},
                "custom_field": "value",
            }
        ]

        # Act
        merged = reciprocal_rank_fusion([results], k=60)

        # Assert
        assert merged[0]["content"] == "test1"
        assert merged[0]["metadata"] == {"source": "test"}
        assert merged[0]["custom_field"] == "value"


class TestHybridSearcher:
    """Tests for HybridSearcher class."""

    @pytest.fixture
    def mock_semantic_searcher(self) -> AsyncMock:
        """Create a mock SemanticSearcher."""
        searcher = AsyncMock(spec=SemanticSearcher)
        return searcher

    @pytest.fixture
    def mock_bm25_searcher(self) -> MagicMock:
        """Create a mock BM25Searcher."""
        searcher = MagicMock(spec=BM25Searcher)
        searcher.is_indexed = True
        return searcher

    @pytest.fixture
    def hybrid_searcher(
        self,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> HybridSearcher:
        """Create a HybridSearcher with mocked dependencies."""
        return HybridSearcher(mock_semantic_searcher, mock_bm25_searcher)

    @pytest.mark.asyncio
    async def test_search_combines_both_methods(
        self,
        hybrid_searcher: HybridSearcher,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> None:
        """Test that hybrid search calls both semantic and BM25."""
        # Arrange
        mock_semantic_searcher.search.return_value = [
            SearchResult(
                id="doc1",
                content="test1",
                score=0.9,
                document_title="Test Doc 1",
            )
        ]
        mock_bm25_searcher.search.return_value = [
            {"id": "doc2", "content": "test2", "score": 5.0}
        ]

        # Act
        results = await hybrid_searcher.search("test query", n_results=5)

        # Assert
        mock_semantic_searcher.search.assert_called_once()
        mock_bm25_searcher.search.assert_called_once()
        assert isinstance(results, list)
        assert all(isinstance(r, SearchResult) for r in results)

    @pytest.mark.asyncio
    async def test_search_retrieves_2x_n_results(
        self,
        hybrid_searcher: HybridSearcher,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> None:
        """Test that hybrid search retrieves 2x n_results from each searcher."""
        # Arrange
        n_results = 5
        mock_semantic_searcher.search.return_value = []
        mock_bm25_searcher.search.return_value = []

        # Act
        await hybrid_searcher.search("test query", n_results=n_results)

        # Assert
        # Check semantic search called with 2x n_results
        call_args = mock_semantic_searcher.search.call_args
        assert call_args.kwargs["n_results"] == n_results * 2
        # Check BM25 search called with 2x n_results
        bm25_call_args = mock_bm25_searcher.search.call_args
        assert bm25_call_args[1]["n_results"] == n_results * 2

    @pytest.mark.asyncio
    async def test_search_passes_filter_to_semantic(
        self,
        hybrid_searcher: HybridSearcher,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> None:
        """Test that filter_dict is passed through to semantic search."""
        # Arrange
        filter_dict = {"document_type": "standard"}
        mock_semantic_searcher.search.return_value = []
        mock_bm25_searcher.search.return_value = []

        # Act
        await hybrid_searcher.search(
            "test query", n_results=5, filter_dict=filter_dict
        )

        # Assert
        call_args = mock_semantic_searcher.search.call_args
        assert call_args.kwargs["filter_dict"] == filter_dict

    @pytest.mark.asyncio
    async def test_search_respects_n_results(
        self,
        hybrid_searcher: HybridSearcher,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> None:
        """Test that search returns at most n_results."""
        # Arrange
        n_results = 2
        # Return more results than requested (before fusion)
        mock_semantic_searcher.search.return_value = [
            SearchResult(id=f"doc{i}", content=f"test{i}", score=0.9 - i * 0.1)
            for i in range(10)
        ]
        mock_bm25_searcher.search.return_value = [
            {"id": f"bm25-doc{i}", "content": f"test{i}", "score": 5.0 - i}
            for i in range(10)
        ]

        # Act
        results = await hybrid_searcher.search("test query", n_results=n_results)

        # Assert
        assert len(results) <= n_results

    @pytest.mark.asyncio
    async def test_search_empty_query_returns_empty(
        self,
        hybrid_searcher: HybridSearcher,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> None:
        """Test that empty query returns empty results."""
        # Arrange & Act
        results = await hybrid_searcher.search("", n_results=5)

        # Assert
        assert results == []
        mock_semantic_searcher.search.assert_not_called()
        mock_bm25_searcher.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_fallback_when_bm25_not_indexed(
        self,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> None:
        """Test graceful fallback to semantic-only when BM25 not indexed."""
        # Arrange
        mock_bm25_searcher.is_indexed = False
        semantic_results = [
            SearchResult(id="doc1", content="test1", score=0.9)
        ]
        mock_semantic_searcher.search.return_value = semantic_results
        hybrid = HybridSearcher(mock_semantic_searcher, mock_bm25_searcher)

        # Act
        results = await hybrid.search("test query", n_results=5)

        # Assert
        assert results == semantic_results
        mock_semantic_searcher.search.assert_called_once()
        mock_bm25_searcher.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_converts_to_search_results(
        self,
        hybrid_searcher: HybridSearcher,
        mock_semantic_searcher: AsyncMock,
        mock_bm25_searcher: MagicMock,
    ) -> None:
        """Test that hybrid search returns SearchResult objects."""
        # Arrange
        mock_semantic_searcher.search.return_value = [
            SearchResult(
                id="doc1",
                content="test content",
                score=0.9,
                document_title="Test Doc",
                section_title="Section 1",
                normative=True,
            )
        ]
        mock_bm25_searcher.search.return_value = []

        # Act
        results = await hybrid_searcher.search("test query", n_results=5)

        # Assert
        assert len(results) > 0
        result = results[0]
        assert isinstance(result, SearchResult)
        assert result.id == "doc1"
        assert result.content == "test content"
        assert "rrf_score" in str(result.score) or result.score > 0
