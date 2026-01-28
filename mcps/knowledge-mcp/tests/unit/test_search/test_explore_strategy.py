"""Unit tests for ExploreStrategy."""

from __future__ import annotations

from typing import Any

import pytest

from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.strategies.explore import ExploreStrategy


class TestExploreStrategy:
    """Tests for ExploreStrategy implementation."""

    @pytest.fixture
    def strategy(self) -> ExploreStrategy:
        """Create ExploreStrategy instance."""
        return ExploreStrategy()

    @pytest.mark.asyncio
    async def test_preprocess_query_uses_default_facets(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """preprocess_query applies default facets when none provided."""
        query = await strategy.preprocess_query("test query", {})

        assert query.original == "test query"
        assert len(query.facets) == 4
        assert "definitions" in query.facets
        assert "examples" in query.facets
        assert "standards" in query.facets
        assert "best_practices" in query.facets

    @pytest.mark.asyncio
    async def test_preprocess_query_accepts_custom_facets(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """preprocess_query accepts custom facets from params."""
        params = {"facets": ["definitions", "examples"]}
        query = await strategy.preprocess_query("test query", params)

        assert len(query.facets) == 2
        assert "definitions" in query.facets
        assert "examples" in query.facets
        assert "standards" not in query.facets

    @pytest.mark.asyncio
    async def test_preprocess_query_handles_invalid_facets(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """preprocess_query falls back to defaults for invalid facets."""
        # Non-list facets
        params: dict[str, Any] = {"facets": "not a list"}
        query = await strategy.preprocess_query("test query", params)
        assert query.facets == strategy.default_facets

        # Empty list
        params = {"facets": []}
        query = await strategy.preprocess_query("test query", params)
        assert query.facets == strategy.default_facets

        # Mixed types
        params = {"facets": ["valid", 123, None]}
        query = await strategy.preprocess_query("test query", params)
        assert query.facets == strategy.default_facets

    @pytest.mark.asyncio
    async def test_preprocess_query_preserves_filters(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """preprocess_query preserves filter params."""
        params = {"filters": {"document_type": "standard"}}
        query = await strategy.preprocess_query("test query", params)

        assert query.filters["document_type"] == "standard"

    def test_adjust_ranking_boosts_definitions(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """adjust_ranking boosts definition chunks by 20%."""
        results = [
            SearchResult(
                id="1",
                content="Definition content",
                score=0.8,
                chunk_type="definition",
            ),
            SearchResult(
                id="2",
                content="Other content",
                score=0.85,
                chunk_type="guidance",
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Definition should be boosted: 0.8 * 1.20 = 0.96
        definition_result = next(r for r in adjusted if r.id == "1")
        assert definition_result.score == pytest.approx(0.96, rel=0.01)

        # Results should be re-sorted by score
        assert adjusted[0].id == "1"  # Boosted definition now highest

    def test_adjust_ranking_boosts_examples(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """adjust_ranking boosts example chunks by 15%."""
        results = [
            SearchResult(
                id="1",
                content="Example content",
                score=0.8,
                chunk_type="example",
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Example should be boosted: 0.8 * 1.15 = 0.92
        assert adjusted[0].score == pytest.approx(0.92, rel=0.01)

    def test_adjust_ranking_boosts_normative_content(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """adjust_ranking boosts normative content by 10%."""
        results = [
            SearchResult(
                id="1",
                content="Normative requirement",
                score=0.8,
                normative=True,
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Normative should be boosted: 0.8 * 1.10 = 0.88
        assert adjusted[0].score == pytest.approx(0.88, rel=0.01)

    def test_adjust_ranking_boosts_guidance(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """adjust_ranking boosts guidance chunks by 10%."""
        results = [
            SearchResult(
                id="1",
                content="Guidance content",
                score=0.8,
                chunk_type="guidance",
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Guidance should be boosted: 0.8 * 1.10 = 0.88
        assert adjusted[0].score == pytest.approx(0.88, rel=0.01)

    def test_adjust_ranking_caps_score_at_one(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """adjust_ranking caps boosted scores at 1.0."""
        results = [
            SearchResult(
                id="1",
                content="High score definition",
                score=0.95,
                chunk_type="definition",
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # 0.95 * 1.20 = 1.14, should be capped at 1.0
        assert adjusted[0].score == 1.0

    def test_adjust_ranking_handles_case_insensitive_chunk_types(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """adjust_ranking handles mixed case chunk_type values."""
        results = [
            SearchResult(
                id="1",
                content="Upper case",
                score=0.8,
                chunk_type="DEFINITION",
            ),
            SearchResult(
                id="2",
                content="Mixed case",
                score=0.8,
                chunk_type="Example",
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Both should be boosted
        assert adjusted[0].score > 0.8
        assert adjusted[1].score > 0.8

    def test_format_output_organizes_by_facet(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """format_output organizes results by facet."""
        results = [
            SearchResult(
                id="1",
                content="Definition text",
                score=0.9,
                chunk_type="definition",
                document_title="IEEE 15288",
                section_title="Terminology",
            ),
            SearchResult(
                id="2",
                content="Example text",
                score=0.85,
                chunk_type="example",
                document_title="INCOSE Guide",
                section_title="Case Studies",
            ),
            SearchResult(
                id="3",
                content="Requirement text",
                score=0.8,
                normative=True,
                document_title="ISO 29148",
                section_title="Requirements",
            ),
        ]

        output = strategy.format_output(results, {})

        assert output["result_type"] == "explore_analysis"
        assert output["total_results"] == 3
        assert len(output["results_by_facet"]["definitions"]) == 1
        assert len(output["results_by_facet"]["examples"]) == 1
        assert len(output["results_by_facet"]["standards"]) == 1

    def test_format_output_includes_facet_coverage(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """format_output includes coverage metrics for each facet."""
        results = [
            SearchResult(
                id="1",
                content="Definition 1",
                score=0.9,
                chunk_type="definition",
            ),
            SearchResult(
                id="2",
                content="Definition 2",
                score=0.85,
                chunk_type="definition",
            ),
            SearchResult(
                id="3",
                content="Example 1",
                score=0.8,
                chunk_type="example",
            ),
        ]

        output = strategy.format_output(results, {})

        assert output["facet_coverage"]["definitions"] == 2
        assert output["facet_coverage"]["examples"] == 1
        assert output["facet_coverage"]["standards"] == 0
        assert output["facet_coverage"]["best_practices"] == 0

    def test_format_output_categorizes_uncategorized_as_best_practices(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """format_output puts uncategorized content in best_practices."""
        results = [
            SearchResult(
                id="1",
                content="Generic content",
                score=0.8,
                chunk_type="other",
            ),
            SearchResult(
                id="2",
                content="No chunk type",
                score=0.75,
                chunk_type="",
            ),
        ]

        output = strategy.format_output(results, {})

        assert len(output["results_by_facet"]["best_practices"]) == 2

    def test_format_output_includes_facets_explored(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """format_output includes list of facets explored."""
        params = {"facets": ["definitions", "examples"]}
        results = [
            SearchResult(id="1", content="Test", score=0.8, chunk_type="definition"),
        ]

        output = strategy.format_output(results, params)

        assert output["facets_explored"] == ["definitions", "examples"]

    def test_format_output_includes_result_metadata(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """format_output includes all relevant result metadata."""
        results = [
            SearchResult(
                id="1",
                content="Test content",
                score=0.9,
                chunk_type="definition",
                document_title="IEEE 15288",
                section_title="Terminology",
                normative=True,
            ),
        ]

        output = strategy.format_output(results, {})

        result = output["results_by_facet"]["definitions"][0]
        assert result["content"] == "Test content"
        assert result["score"] == 0.9
        assert result["document_title"] == "IEEE 15288"
        assert result["section_title"] == "Terminology"
        assert result["chunk_type"] == "definition"
        assert result["normative"] is True

    def test_format_output_handles_empty_results(
        self,
        strategy: ExploreStrategy,
    ) -> None:
        """format_output handles empty result list gracefully."""
        output = strategy.format_output([], {})

        assert output["total_results"] == 0
        assert output["facet_coverage"]["definitions"] == 0
        assert output["result_type"] == "explore_analysis"
