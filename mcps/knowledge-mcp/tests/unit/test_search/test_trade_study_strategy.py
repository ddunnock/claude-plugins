"""Unit tests for TradeStudyStrategy.

Tests cover:
- Query preprocessing with trade study keyword boosting
- Result ranking with criteria keyword detection
- Output formatting with alternative grouping
- Criterion extraction with quantitative values
"""

from __future__ import annotations

import pytest

from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.strategies.base import SearchQuery
from knowledge_mcp.search.strategies.trade_study import TradeStudyStrategy


class TestTradeStudyStrategyPreprocessQuery:
    """Tests for TradeStudyStrategy.preprocess_query method."""

    @pytest.fixture
    def strategy(self) -> TradeStudyStrategy:
        """Create strategy instance."""
        return TradeStudyStrategy()

    @pytest.mark.asyncio
    async def test_preprocess_query_adds_trade_study_keywords(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that preprocess_query adds trade study keywords as expanded terms."""
        # Arrange
        query = "Compare Architecture A vs Architecture B"
        params: dict[str, list[str]] = {}

        # Act
        result = await strategy.preprocess_query(query, params)

        # Assert
        assert isinstance(result, SearchQuery)
        assert result.original == query
        assert len(result.expanded_terms) > 0
        assert "alternative" in result.expanded_terms
        assert "criteria" in result.expanded_terms
        assert "trade-off" in result.expanded_terms
        assert "evaluation" in result.expanded_terms

    @pytest.mark.asyncio
    async def test_preprocess_query_includes_alternatives_as_facets(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that alternatives parameter is added as facets."""
        # Arrange
        query = "Compare options"
        params = {"alternatives": ["Option A", "Option B", "Option C"]}

        # Act
        result = await strategy.preprocess_query(query, params)

        # Assert
        assert result.facets == ["Option A", "Option B", "Option C"]

    @pytest.mark.asyncio
    async def test_preprocess_query_without_alternatives(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test preprocessing when no alternatives provided."""
        # Arrange
        query = "Find trade study information"
        params: dict[str, list[str]] = {}

        # Act
        result = await strategy.preprocess_query(query, params)

        # Assert
        assert result.facets == []
        assert len(result.expanded_terms) > 0


class TestTradeStudyStrategyAdjustRanking:
    """Tests for TradeStudyStrategy.adjust_ranking method."""

    @pytest.fixture
    def strategy(self) -> TradeStudyStrategy:
        """Create strategy instance."""
        return TradeStudyStrategy()

    def test_adjust_ranking_boosts_results_with_criteria_keywords(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that results with criteria keywords get score boost."""
        # Arrange
        results = [
            SearchResult(
                id="chunk-1",
                content="This discusses evaluation criteria and trade-offs between alternatives.",
                score=0.5,
            ),
            SearchResult(
                id="chunk-2",
                content="This is generic content without decision keywords.",
                score=0.6,
            ),
        ]

        # Act
        adjusted = strategy.adjust_ranking(results)

        # Assert - chunk-1 should be boosted above chunk-2
        assert adjusted[0].id == "chunk-1"
        assert adjusted[0].score > 0.5  # Original was 0.5, should be boosted
        assert adjusted[1].id == "chunk-2"
        assert adjusted[1].score == 0.6  # No boost

    def test_adjust_ranking_caps_boost_at_30_percent(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that boost is capped at 0.3."""
        # Arrange - content with many keywords
        results = [
            SearchResult(
                id="chunk-1",
                content="alternative option criteria trade-off evaluation comparison assessment advantage disadvantage benefit drawback versus compare",
                score=0.5,
            ),
        ]

        # Act
        adjusted = strategy.adjust_ranking(results)

        # Assert - should be boosted by max 0.3
        assert adjusted[0].score == 0.8  # 0.5 + 0.3 cap

    def test_adjust_ranking_does_not_exceed_1_0(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that boosted score never exceeds 1.0."""
        # Arrange
        results = [
            SearchResult(
                id="chunk-1",
                content="alternative criteria trade-off evaluation comparison",
                score=0.95,
            ),
        ]

        # Act
        adjusted = strategy.adjust_ranking(results)

        # Assert - should cap at 1.0
        assert adjusted[0].score == 1.0

    def test_adjust_ranking_preserves_order_when_no_boost_needed(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that results without keywords maintain order."""
        # Arrange
        results = [
            SearchResult(id="chunk-1", content="First result", score=0.9),
            SearchResult(id="chunk-2", content="Second result", score=0.8),
            SearchResult(id="chunk-3", content="Third result", score=0.7),
        ]

        # Act
        adjusted = strategy.adjust_ranking(results)

        # Assert - order unchanged
        assert [r.id for r in adjusted] == ["chunk-1", "chunk-2", "chunk-3"]


class TestTradeStudyStrategyFormatOutput:
    """Tests for TradeStudyStrategy.format_output method."""

    @pytest.fixture
    def strategy(self) -> TradeStudyStrategy:
        """Create strategy instance."""
        return TradeStudyStrategy()

    def test_format_output_groups_by_specified_alternatives(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test grouping results by alternatives when provided."""
        # Arrange
        results = [
            SearchResult(
                id="chunk-1",
                content="Option A provides performance of 99.9% uptime",
                score=0.9,
                document_title="System Design Doc",
                section_title="Performance Analysis",
            ),
            SearchResult(
                id="chunk-2",
                content="Option B achieves 95% uptime at lower cost",
                score=0.85,
                document_title="Cost Analysis",
                section_title="Budget Comparison",
            ),
        ]
        params = {"alternatives": ["Option A", "Option B"]}

        # Act
        output = strategy.format_output(results, params)

        # Assert
        assert output["result_type"] == "trade_study"
        assert len(output["alternatives"]) == 2
        assert output["alternatives"][0]["name"] == "Option A"
        assert output["alternatives"][1]["name"] == "Option B"
        assert output["total_sources"] == 2

    def test_format_output_includes_criteria_with_evidence(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that each alternative includes criteria with evidence."""
        # Arrange
        results = [
            SearchResult(
                id="chunk-1",
                content="Option A reliability is 99.9% uptime with excellent performance",
                score=0.9,
                document_title="Tech Spec",
                section_title="Reliability",
            ),
        ]
        params = {"alternatives": ["Option A"]}

        # Act
        output = strategy.format_output(results, params)

        # Assert
        alt_a = output["alternatives"][0]
        assert len(alt_a["criteria"]) > 0
        criterion = alt_a["criteria"][0]
        assert "name" in criterion
        assert "evidence" in criterion
        assert "value" in criterion
        assert "source" in criterion
        assert criterion["source"]["chunk_id"] == "chunk-1"
        assert criterion["source"]["document_title"] == "Tech Spec"

    def test_format_output_extracts_quantitative_values(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test extraction of quantitative values from content."""
        # Arrange
        results = [
            SearchResult(
                id="chunk-1",
                content="System achieves 99.9% uptime with 50ms latency",
                score=0.9,
                document_title="Performance Report",
            ),
        ]
        params = {"alternatives": ["System"]}

        # Act
        output = strategy.format_output(results, params)

        # Assert
        criterion = output["alternatives"][0]["criteria"][0]
        # Should extract either percentage or time unit
        assert criterion["value"] in ["99.9%", "99.9 %", "50ms", "50 ms"]

    def test_format_output_identifies_criterion_types(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test identification of criterion types from content."""
        # Arrange
        results = [
            SearchResult(
                id="chunk-1",
                content="Solution A provides excellent performance with benchmark throughput",
                score=0.9,
            ),
            SearchResult(
                id="chunk-2",
                content="The solution cost analysis indicates budget of $50,000",
                score=0.85,
            ),
        ]
        params = {"alternatives": ["Solution", "Solution A"]}

        # Act
        output = strategy.format_output(results, params)

        # Assert - should identify criterion types from at least one alternative
        all_criteria_names = []
        for alt in output["alternatives"]:
            all_criteria_names.extend([c["name"] for c in alt["criteria"]])

        # At least one should be identified
        assert any(
            name
            in [
                "Performance",
                "Cost",
                "Reliability",
                "Security",
                "Scalability",
                "Maintainability",
                "Usability",
            ]
            for name in all_criteria_names
        )

    def test_format_output_without_alternatives_parameter(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test output when alternatives not specified - should extract from content."""
        # Arrange
        results = [
            SearchResult(
                id="chunk-1",
                content="Consider option X for better performance",
                score=0.9,
            ),
            SearchResult(
                id="chunk-2",
                content="Alternative Y provides lower cost",
                score=0.85,
            ),
        ]
        params: dict[str, list[str]] = {}

        # Act
        output = strategy.format_output(results, params)

        # Assert - should create alternatives from content
        assert output["result_type"] == "trade_study"
        assert len(output["alternatives"]) > 0

    def test_format_output_truncates_long_evidence(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test that long evidence text is truncated."""
        # Arrange
        long_content = "Solution: " + ("A" * 300)  # Content longer than 200 chars with alternative name
        results = [
            SearchResult(
                id="chunk-1",
                content=long_content,
                score=0.9,
            ),
        ]
        params = {"alternatives": ["Solution"]}

        # Act
        output = strategy.format_output(results, params)

        # Assert
        alt = output["alternatives"][0]
        assert len(alt["criteria"]) > 0, "Should have at least one criterion"
        evidence = alt["criteria"][0]["evidence"]
        assert len(evidence) <= 203  # 200 chars + "..."
        assert evidence.endswith("...")


class TestTradeStudyStrategyIntegration:
    """Integration tests for complete workflow."""

    @pytest.fixture
    def strategy(self) -> TradeStudyStrategy:
        """Create strategy instance."""
        return TradeStudyStrategy()

    @pytest.mark.asyncio
    async def test_full_workflow_with_trade_study(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test complete workflow from query to formatted output."""
        # Arrange
        query = "Compare Database A vs Database B"
        params = {"alternatives": ["Database A", "Database B"]}

        results = [
            SearchResult(
                id="chunk-1",
                content="Database A provides 99.9% uptime and excellent performance with criteria evaluation showing strong reliability",
                score=0.7,
                document_title="DB Comparison Report",
                section_title="Reliability Analysis",
            ),
            SearchResult(
                id="chunk-2",
                content="Database B has lower cost at $10,000 per year",
                score=0.65,
                document_title="Cost Analysis",
                section_title="Budget Review",
            ),
            SearchResult(
                id="chunk-3",
                content="General information about databases",
                score=0.8,
            ),
        ]

        # Act - preprocess
        search_query = await strategy.preprocess_query(query, params)
        assert len(search_query.expanded_terms) > 0

        # Act - adjust ranking
        ranked = strategy.adjust_ranking(results)
        # chunk-1 should be boosted due to keywords
        assert ranked[0].id == "chunk-1"

        # Act - format output
        output = strategy.format_output(ranked, params)

        # Assert
        assert output["result_type"] == "trade_study"
        assert len(output["alternatives"]) == 2

        db_a = next(a for a in output["alternatives"] if a["name"] == "Database A")
        db_b = next(a for a in output["alternatives"] if a["name"] == "Database B")

        assert len(db_a["criteria"]) > 0
        assert len(db_b["criteria"]) > 0
        assert db_a["criteria"][0]["value"] in ["99.9%", "99.9 %"]

    @pytest.mark.asyncio
    async def test_handles_empty_results(
        self,
        strategy: TradeStudyStrategy,
    ) -> None:
        """Test handling of empty result set."""
        # Arrange
        query = "No results expected"
        params = {"alternatives": ["Option A"]}
        results: list[SearchResult] = []

        # Act
        search_query = await strategy.preprocess_query(query, params)
        ranked = strategy.adjust_ranking(results)
        output = strategy.format_output(ranked, params)

        # Assert - should not crash
        assert output["result_type"] == "trade_study"
        assert output["total_sources"] == 0
