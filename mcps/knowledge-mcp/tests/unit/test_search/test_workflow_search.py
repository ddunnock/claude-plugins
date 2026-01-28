"""Unit tests for workflow search orchestrator and strategy base."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.strategies.base import SearchQuery, SearchStrategy
from knowledge_mcp.search.workflow_search import WorkflowSearcher


class MockStrategy(SearchStrategy):
    """Concrete strategy for testing."""

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any],
    ) -> SearchQuery:
        return SearchQuery(
            original=query,
            expanded_terms=[f"{query} expanded"],
            filters=params.get("filters", {}),
        )

    def adjust_ranking(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        # Boost scores by 10%
        for r in results:
            r.score = min(1.0, r.score * 1.1)
        return sorted(results, key=lambda r: r.score, reverse=True)

    def format_output(
        self,
        results: list[SearchResult],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "results": [{"content": r.content, "score": r.score} for r in results],
            "result_type": "mock",
            "total_results": len(results),
        }


class TestSearchQuery:
    """Tests for SearchQuery dataclass."""

    def test_defaults(self) -> None:
        """SearchQuery has sensible defaults."""
        q = SearchQuery(original="test")
        assert q.original == "test"
        assert q.expanded_terms == []
        assert q.filters == {}
        assert q.facets == []

    def test_with_all_fields(self) -> None:
        """SearchQuery accepts all fields."""
        q = SearchQuery(
            original="test",
            expanded_terms=["test expanded"],
            filters={"type": "standard"},
            facets=["definitions"],
        )
        assert len(q.expanded_terms) == 1
        assert q.filters["type"] == "standard"


class TestWorkflowSearcher:
    """Tests for WorkflowSearcher orchestrator."""

    @pytest.fixture
    def mock_semantic_searcher(self) -> MagicMock:
        """Create mock semantic searcher."""
        searcher = MagicMock()
        searcher.search = AsyncMock(
            return_value=[
                SearchResult(id="1", content="Result 1", score=0.9),
                SearchResult(id="2", content="Result 2", score=0.8),
            ]
        )
        return searcher

    @pytest.fixture
    def mock_strategy(self) -> MockStrategy:
        """Create mock strategy."""
        return MockStrategy()

    @pytest.fixture
    def workflow_searcher(
        self,
        mock_semantic_searcher: MagicMock,
        mock_strategy: MockStrategy,
    ) -> WorkflowSearcher:
        """Create workflow searcher with mocks."""
        return WorkflowSearcher(mock_semantic_searcher, mock_strategy)

    @pytest.mark.asyncio
    async def test_search_calls_strategy_preprocess(
        self,
        workflow_searcher: WorkflowSearcher,
    ) -> None:
        """Search calls strategy preprocess_query."""
        result = await workflow_searcher.search("test query")
        assert result["result_type"] == "mock"

    @pytest.mark.asyncio
    async def test_search_calls_semantic_search(
        self,
        workflow_searcher: WorkflowSearcher,
        mock_semantic_searcher: MagicMock,
    ) -> None:
        """Search calls underlying semantic searcher."""
        await workflow_searcher.search("test query")
        mock_semantic_searcher.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_applies_ranking_adjustment(
        self,
        workflow_searcher: WorkflowSearcher,
    ) -> None:
        """Search applies strategy ranking adjustment."""
        result = await workflow_searcher.search("test query")
        # MockStrategy boosts scores by 10%
        assert result["results"][0]["score"] == pytest.approx(0.99, rel=0.01)

    @pytest.mark.asyncio
    async def test_search_returns_formatted_output(
        self,
        workflow_searcher: WorkflowSearcher,
    ) -> None:
        """Search returns strategy-formatted output."""
        result = await workflow_searcher.search("test query")
        assert "results" in result
        assert "result_type" in result
        assert result["total_results"] == 2

    @pytest.mark.asyncio
    async def test_search_handles_empty_results(
        self,
        mock_strategy: MockStrategy,
    ) -> None:
        """Search handles empty results gracefully."""
        searcher = MagicMock()
        searcher.search = AsyncMock(return_value=[])
        workflow = WorkflowSearcher(searcher, mock_strategy)

        result = await workflow.search("obscure query")
        assert result["total_results"] == 0

    @pytest.mark.asyncio
    async def test_search_passes_params_to_strategy(
        self,
        workflow_searcher: WorkflowSearcher,
        mock_semantic_searcher: MagicMock,
    ) -> None:
        """Search passes params to strategy methods."""
        params = {"filters": {"document_type": "standard"}}
        await workflow_searcher.search("test", params=params)

        # Verify filters were passed to semantic search
        call_kwargs = mock_semantic_searcher.search.call_args.kwargs
        assert call_kwargs.get("filter_dict") == {"document_type": "standard"}

    def test_set_strategy(
        self,
        workflow_searcher: WorkflowSearcher,
    ) -> None:
        """Can change strategy at runtime."""
        new_strategy = MockStrategy()
        workflow_searcher.set_strategy(new_strategy)
        assert workflow_searcher.strategy is new_strategy

    @pytest.mark.asyncio
    async def test_search_handles_errors(
        self,
        mock_strategy: MockStrategy,
    ) -> None:
        """Search returns error dict on exception."""
        searcher = MagicMock()
        searcher.search = AsyncMock(side_effect=Exception("Connection failed"))
        workflow = WorkflowSearcher(searcher, mock_strategy)

        result = await workflow.search("test")
        assert "error" in result
        assert result["result_type"] == "error"
