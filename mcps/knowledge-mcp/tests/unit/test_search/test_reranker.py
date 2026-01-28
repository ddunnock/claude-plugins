# tests/unit/test_search/test_reranker.py
"""Unit tests for Reranker."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from knowledge_mcp.search.models import SearchResult


def make_result(id: str, content: str, score: float) -> SearchResult:
    """Create a SearchResult for testing.

    Args:
        id: Chunk identifier.
        content: Text content.
        score: Similarity score.

    Returns:
        SearchResult with the given values.
    """
    return SearchResult(id=id, content=content, score=score)


class TestRerankerInit:
    """Tests for Reranker initialization."""

    def test_cohere_init_requires_api_key(self) -> None:
        """Test Cohere provider requires API key."""
        mock_cohere = MagicMock()
        with patch.dict(sys.modules, {"cohere": mock_cohere}):
            # Need to reimport after patching
            from knowledge_mcp.search import reranker

            # Clear any cached import
            if "knowledge_mcp.search.reranker" in sys.modules:
                del sys.modules["knowledge_mcp.search.reranker"]

            # Re-import the module
            from knowledge_mcp.search.reranker import Reranker

            with pytest.raises(ValueError, match="api_key required"):
                Reranker(provider="cohere")

    def test_cohere_init_with_api_key(self) -> None:
        """Test Cohere provider initializes with API key."""
        mock_cohere = MagicMock()
        with patch.dict(sys.modules, {"cohere": mock_cohere}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(provider="cohere", api_key="test-key")
            assert reranker._provider == "cohere"
            mock_cohere.ClientV2.assert_called_once_with(api_key="test-key")

    def test_cohere_init_custom_model(self) -> None:
        """Test Cohere provider accepts custom model name."""
        mock_cohere = MagicMock()
        with patch.dict(sys.modules, {"cohere": mock_cohere}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(
                provider="cohere", api_key="test-key", model="rerank-multilingual-v3.0"
            )
            assert reranker._model_name == "rerank-multilingual-v3.0"

    def test_local_init(self) -> None:
        """Test local provider initializes cross-encoder."""
        mock_st = MagicMock()
        with patch.dict(sys.modules, {"sentence_transformers": mock_st}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(provider="local")
            assert reranker._provider == "local"
            mock_st.CrossEncoder.assert_called_once_with("cross-encoder/ms-marco-MiniLM-L6-v2")

    def test_local_init_custom_model(self) -> None:
        """Test local provider accepts custom model name."""
        mock_st = MagicMock()
        with patch.dict(sys.modules, {"sentence_transformers": mock_st}):
            from knowledge_mcp.search.reranker import Reranker

            Reranker(provider="local", model="cross-encoder/ms-marco-TinyBERT-L2-v2")
            mock_st.CrossEncoder.assert_called_once_with("cross-encoder/ms-marco-TinyBERT-L2-v2")


class TestRerankerRerank:
    """Tests for Reranker.rerank method."""

    @pytest.mark.asyncio
    async def test_rerank_empty_results(self) -> None:
        """Test rerank returns empty list for empty input."""
        mock_st = MagicMock()
        with patch.dict(sys.modules, {"sentence_transformers": mock_st}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(provider="local")
            result = await reranker.rerank("query", [])
            assert result == []

    @pytest.mark.asyncio
    async def test_rerank_local_reorders_by_score(self) -> None:
        """Test local reranking actually reorders results by new scores.

        This test verifies that reranking changes the order of results
        based on cross-encoder scores, not just that it returns results.
        """
        mock_st = MagicMock()
        mock_model = MagicMock()
        # Scores that reverse the original order: [0.3, 0.6, 0.9]
        # Original order: id=1, id=2, id=3
        # After reranking: id=3 (0.9), id=2 (0.6), id=1 (0.3)
        mock_model.predict.return_value = [0.3, 0.6, 0.9]
        mock_st.CrossEncoder.return_value = mock_model

        with patch.dict(sys.modules, {"sentence_transformers": mock_st}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(provider="local")
            # Original results with semantic search scores (different from rerank scores)
            results = [
                make_result("1", "content 1", 0.95),  # Highest semantic score
                make_result("2", "content 2", 0.85),
                make_result("3", "content 3", 0.75),  # Lowest semantic score
            ]

            reranked = await reranker.rerank("query", results)

            # Verify order changed: id=3 should now be first (score 0.9)
            assert reranked[0].id == "3", "Highest rerank score should be first"
            assert reranked[1].id == "2", "Middle rerank score should be second"
            assert reranked[2].id == "1", "Lowest rerank score should be last"

            # Verify scores were updated
            assert reranked[0].score == 0.9
            assert reranked[1].score == 0.6
            assert reranked[2].score == 0.3

    @pytest.mark.asyncio
    async def test_rerank_preserves_all_fields(self) -> None:
        """Test that reranking preserves all SearchResult fields except score."""
        mock_st = MagicMock()
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.99]
        mock_st.CrossEncoder.return_value = mock_model

        with patch.dict(sys.modules, {"sentence_transformers": mock_st}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(provider="local")

            # Create result with all fields populated
            original = SearchResult(
                id="chunk-42",
                content="Test content",
                score=0.5,
                metadata={"key": "value"},
                document_id="doc-1",
                document_title="IEEE 15288",
                document_type="standard",
                section_title="Requirements",
                section_hierarchy=["5", "5.3"],
                chunk_type="requirement",
                normative=True,
                clause_number="5.3.1",
                page_numbers=[42, 43],
            )

            reranked = await reranker.rerank("query", [original])

            # Score should be updated
            assert reranked[0].score == 0.99

            # All other fields should be preserved
            assert reranked[0].id == original.id
            assert reranked[0].content == original.content
            assert reranked[0].metadata == original.metadata
            assert reranked[0].document_id == original.document_id
            assert reranked[0].document_title == original.document_title
            assert reranked[0].document_type == original.document_type
            assert reranked[0].section_title == original.section_title
            assert reranked[0].section_hierarchy == original.section_hierarchy
            assert reranked[0].chunk_type == original.chunk_type
            assert reranked[0].normative == original.normative
            assert reranked[0].clause_number == original.clause_number
            assert reranked[0].page_numbers == original.page_numbers

    @pytest.mark.asyncio
    async def test_rerank_top_n(self) -> None:
        """Test top_n limits returned results."""
        mock_st = MagicMock()
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.8, 0.3, 0.9]
        mock_st.CrossEncoder.return_value = mock_model

        with patch.dict(sys.modules, {"sentence_transformers": mock_st}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(provider="local")
            results = [
                make_result("1", "content 1", 0.5),
                make_result("2", "content 2", 0.6),
                make_result("3", "content 3", 0.4),
            ]

            reranked = await reranker.rerank("query", results, top_n=2)

            assert len(reranked) == 2
            # Should be top 2 by rerank score: id=3 (0.9), id=1 (0.8)
            assert reranked[0].id == "3"
            assert reranked[1].id == "1"

    @pytest.mark.asyncio
    async def test_rerank_cohere_reorders_by_relevance(self) -> None:
        """Test Cohere reranking reorders results by relevance score."""
        mock_cohere = MagicMock()

        # Mock the rerank response
        mock_client = MagicMock()
        mock_cohere.ClientV2.return_value = mock_client

        # Cohere returns results sorted by relevance with original indices
        mock_result_1 = MagicMock()
        mock_result_1.index = 2  # Original index of id=3
        mock_result_1.relevance_score = 0.95

        mock_result_2 = MagicMock()
        mock_result_2.index = 0  # Original index of id=1
        mock_result_2.relevance_score = 0.85

        mock_result_3 = MagicMock()
        mock_result_3.index = 1  # Original index of id=2
        mock_result_3.relevance_score = 0.70

        mock_response = MagicMock()
        mock_response.results = [mock_result_1, mock_result_2, mock_result_3]
        mock_client.rerank.return_value = mock_response

        with patch.dict(sys.modules, {"cohere": mock_cohere}):
            from knowledge_mcp.search.reranker import Reranker

            reranker = Reranker(provider="cohere", api_key="test-key")

            results = [
                make_result("1", "content 1", 0.9),
                make_result("2", "content 2", 0.8),
                make_result("3", "content 3", 0.7),
            ]

            reranked = await reranker.rerank("query", results)

            # Verify Cohere reordered results
            assert reranked[0].id == "3"  # Was index 2, now first
            assert reranked[1].id == "1"  # Was index 0, now second
            assert reranked[2].id == "2"  # Was index 1, now third

            # Verify scores updated to Cohere relevance scores
            assert reranked[0].score == 0.95
            assert reranked[1].score == 0.85
            assert reranked[2].score == 0.70
