"""Unit tests for PlanStrategy."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.strategies.plan import PlanStrategy


class TestPlanStrategy:
    """Tests for PlanStrategy."""

    @pytest.fixture
    def strategy(self) -> PlanStrategy:
        """Create PlanStrategy instance."""
        return PlanStrategy()

    @pytest.mark.asyncio
    async def test_preprocess_query_no_category(
        self, strategy: PlanStrategy
    ) -> None:
        """Test preprocessing query without specific category."""
        query = await strategy.preprocess_query("project planning", {})

        assert query.original == "project planning"
        assert len(query.expanded_terms) > 0
        assert "planning" in query.expanded_terms
        assert len(query.facets) == 4  # All categories
        assert "templates" in query.facets
        assert "risks" in query.facets
        assert "lessons_learned" in query.facets
        assert "precedents" in query.facets

    @pytest.mark.asyncio
    async def test_preprocess_query_with_templates_category(
        self, strategy: PlanStrategy
    ) -> None:
        """Test preprocessing with templates category."""
        query = await strategy.preprocess_query(
            "planning template", {"category": "templates"}
        )

        assert query.original == "planning template"
        assert "template" in query.expanded_terms
        assert "framework" in query.expanded_terms
        assert query.facets == ["templates"]

    @pytest.mark.asyncio
    async def test_preprocess_query_with_risks_category(
        self, strategy: PlanStrategy
    ) -> None:
        """Test preprocessing with risks category."""
        query = await strategy.preprocess_query(
            "risk analysis", {"category": "risks"}
        )

        assert query.original == "risk analysis"
        assert "risk" in query.expanded_terms
        assert "mitigation" in query.expanded_terms
        assert query.facets == ["risks"]

    @pytest.mark.asyncio
    async def test_preprocess_query_with_lessons_learned_category(
        self, strategy: PlanStrategy
    ) -> None:
        """Test preprocessing with lessons_learned category."""
        query = await strategy.preprocess_query(
            "lessons from project", {"category": "lessons_learned"}
        )

        assert query.original == "lessons from project"
        assert "lesson" in query.expanded_terms
        assert "retrospective" in query.expanded_terms
        assert query.facets == ["lessons_learned"]

    @pytest.mark.asyncio
    async def test_preprocess_query_with_precedents_category(
        self, strategy: PlanStrategy
    ) -> None:
        """Test preprocessing with precedents category."""
        query = await strategy.preprocess_query(
            "similar projects", {"category": "precedents"}
        )

        assert query.original == "similar projects"
        assert "precedent" in query.expanded_terms
        assert "case study" in query.expanded_terms
        assert query.facets == ["precedents"]

    @pytest.mark.asyncio
    async def test_preprocess_query_with_filters(
        self, strategy: PlanStrategy
    ) -> None:
        """Test preprocessing preserves filters from params."""
        query = await strategy.preprocess_query(
            "planning", {"filters": {"document_type": "template"}}
        )

        assert query.filters == {"document_type": "template"}

    def test_adjust_ranking_boosts_planning_keywords(
        self, strategy: PlanStrategy
    ) -> None:
        """Test ranking adjustment boosts planning keywords."""
        results = [
            SearchResult(
                id="1",
                content="This is about planning and templates",
                score=0.8,
            ),
            SearchResult(
                id="2",
                content="This is generic content",
                score=0.85,
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Result 1 should be boosted and possibly re-ranked
        result_1 = next(r for r in adjusted if r.id == "1")
        assert result_1.score > 0.8  # Should be boosted

    def test_adjust_ranking_boosts_template_document_type(
        self, strategy: PlanStrategy
    ) -> None:
        """Test ranking adjustment boosts template document types."""
        results = [
            SearchResult(
                id="1",
                content="Some content",
                score=0.8,
                metadata={"document_type": "template"},
            ),
            SearchResult(
                id="2",
                content="Some content",
                score=0.85,
                metadata={"document_type": "standard"},
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Result 1 should be boosted
        result_1 = next(r for r in adjusted if r.id == "1")
        assert result_1.score > 0.8

    def test_adjust_ranking_maintains_sort_order(
        self, strategy: PlanStrategy
    ) -> None:
        """Test that adjusted results are sorted by score."""
        results = [
            SearchResult(id="1", content="test", score=0.7),
            SearchResult(id="2", content="test", score=0.9),
            SearchResult(id="3", content="test", score=0.8),
        ]

        adjusted = strategy.adjust_ranking(results)

        # Verify descending order
        scores = [r.score for r in adjusted]
        assert scores == sorted(scores, reverse=True)

    def test_format_output_with_category_returns_flat_structure(
        self, strategy: PlanStrategy
    ) -> None:
        """Test format_output with category returns flat list."""
        results = [
            SearchResult(
                id="1",
                content="Template content",
                score=0.9,
                document_title="Planning Guide",
                section_title="Templates",
                chunk_type="guidance",
            ),
        ]

        output = strategy.format_output(results, {"category": "templates"})

        assert output["result_type"] == "plan_analysis"
        assert output["category"] == "templates"
        assert output["count"] == 1
        assert len(output["results"]) == 1
        assert output["results"][0]["content"] == "Template content"
        assert output["results"][0]["score"] == 0.9

    def test_format_output_without_category_categorizes_results(
        self, strategy: PlanStrategy
    ) -> None:
        """Test format_output without category categorizes by content."""
        results = [
            SearchResult(
                id="1",
                content="This is a planning template for projects",
                score=0.9,
                document_title="Guide",
                section_title="Templates",
                chunk_type="guidance",
            ),
            SearchResult(
                id="2",
                content="Risk mitigation strategies for projects",
                score=0.85,
                document_title="Risk Guide",
                section_title="Risks",
                chunk_type="guidance",
            ),
            SearchResult(
                id="3",
                content="Lessons learned from past projects",
                score=0.8,
                document_title="Retrospective",
                section_title="Lessons",
                chunk_type="guidance",
            ),
            SearchResult(
                id="4",
                content="Case study of similar precedent project",
                score=0.75,
                document_title="Case Studies",
                section_title="Precedents",
                chunk_type="example",
            ),
        ]

        output = strategy.format_output(results, {})

        assert output["result_type"] == "plan_analysis"
        assert "categories" in output
        assert output["total_results"] == 4

        # Verify categorization
        categories = output["categories"]
        assert len(categories["templates"]) == 1
        assert len(categories["risks"]) == 1
        assert len(categories["lessons_learned"]) == 1
        assert len(categories["precedents"]) == 1

    def test_format_output_uncategorized_goes_to_templates(
        self, strategy: PlanStrategy
    ) -> None:
        """Test that uncategorized results default to templates."""
        results = [
            SearchResult(
                id="1",
                content="Generic planning content without keywords",
                score=0.8,
                document_title="Guide",
                section_title="General",
                chunk_type="guidance",
            ),
        ]

        output = strategy.format_output(results, {})

        categories = output["categories"]
        assert len(categories["templates"]) == 1
        assert categories["templates"][0]["content"] == "Generic planning content without keywords"

    def test_format_output_includes_all_fields(
        self, strategy: PlanStrategy
    ) -> None:
        """Test that formatted output includes all expected fields."""
        results = [
            SearchResult(
                id="1",
                content="Template content",
                score=0.9,
                document_title="Planning Guide",
                section_title="Templates Section",
                chunk_type="guidance",
            ),
        ]

        output = strategy.format_output(results, {"category": "templates"})

        result = output["results"][0]
        assert "content" in result
        assert "score" in result
        assert "document_title" in result
        assert "section_title" in result
        assert "chunk_type" in result
        assert result["document_title"] == "Planning Guide"
        assert result["section_title"] == "Templates Section"
        assert result["chunk_type"] == "guidance"

    def test_adjust_ranking_caps_score_at_one(
        self, strategy: PlanStrategy
    ) -> None:
        """Test that score boosting doesn't exceed 1.0."""
        results = [
            SearchResult(
                id="1",
                content="planning template framework methodology approach strategy roadmap",
                score=0.95,
            ),
        ]

        adjusted = strategy.adjust_ranking(results)

        assert adjusted[0].score <= 1.0
