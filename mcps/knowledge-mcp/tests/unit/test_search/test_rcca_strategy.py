"""Unit tests for RCCAStrategy."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.strategies.rcca import RCCAStrategy
from knowledge_mcp.search.workflow_search import WorkflowSearcher


class TestRCCAStrategy:
    """Tests for RCCAStrategy implementation."""

    @pytest.fixture
    def strategy(self) -> RCCAStrategy:
        """Create RCCAStrategy instance."""
        return RCCAStrategy()

    @pytest.mark.asyncio
    async def test_preprocess_query_expands_terms(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """preprocess_query adds RCCA-specific terms."""
        query = await strategy.preprocess_query("power supply failure", {})

        assert query.original == "power supply failure"
        assert len(query.expanded_terms) > 0
        assert "failure" in query.expanded_terms
        assert "root cause" in query.expanded_terms
        assert "resolution" in query.expanded_terms

    @pytest.mark.asyncio
    async def test_preprocess_query_sets_facets(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """preprocess_query defines RCCA facets."""
        query = await strategy.preprocess_query("issue", {})

        assert "symptoms" in query.facets
        assert "causes" in query.facets
        assert "resolutions" in query.facets

    def test_adjust_ranking_boosts_rcca_content(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """adjust_ranking boosts results with RCCA keywords."""
        results = [
            SearchResult(
                id="1",
                content="Generic content about systems",
                score=0.8,
            ),
            SearchResult(
                id="2",
                content="Failure symptom: intermittent reboot. Root cause: capacitor degradation. Corrective action: replace capacitor.",
                score=0.75,
            ),
        ]

        ranked = strategy.adjust_ranking(results)

        # Result with RCCA content should be boosted above generic result
        assert ranked[0].id == "2"
        assert ranked[0].score > 0.75
        assert ranked[1].id == "1"

    def test_adjust_ranking_multiple_aspects_boost(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """adjust_ranking applies boost when multiple RCCA aspects present."""
        results = [
            SearchResult(
                id="1",
                content="The failure was caused by overheating. The corrective action was to add cooling.",
                score=0.7,
            ),
        ]

        ranked = strategy.adjust_ranking(results)

        # Should have boost for having symptom + resolution
        assert ranked[0].score > 0.7

    def test_adjust_ranking_root_cause_boost(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """adjust_ranking applies extra boost for root cause language."""
        results = [
            SearchResult(
                id="1",
                content="The root cause was identified as insufficient voltage regulation.",
                score=0.6,
            ),
        ]

        ranked = strategy.adjust_ranking(results)

        # Should have extra boost for root cause language
        assert ranked[0].score > 0.6

    def test_adjust_ranking_resolution_boost(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """adjust_ranking boosts results with resolution content."""
        results = [
            SearchResult(
                id="1",
                content="Corrective action: implement voltage regulator with wider tolerance range.",
                score=0.65,
            ),
        ]

        ranked = strategy.adjust_ranking(results)

        # Should have boost for resolution content
        assert ranked[0].score > 0.65

    def test_adjust_ranking_keeps_score_in_range(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """adjust_ranking keeps scores in 0-1 range."""
        results = [
            SearchResult(
                id="1",
                content="Failure root cause corrective action mitigation resolution symptom",
                score=0.95,
            ),
        ]

        ranked = strategy.adjust_ranking(results)

        # Score should not exceed 1.0
        assert ranked[0].score <= 1.0

    def test_format_output_structure(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """format_output returns properly structured dict."""
        results = [
            SearchResult(
                id="test-1",
                content="Test content",
                score=0.9,
                document_title="Test Doc",
                section_title="Test Section",
            ),
        ]

        output = strategy.format_output(results, {})

        assert output["result_type"] == "rcca_analysis"
        assert output["total_results"] == 1
        assert "results" in output
        assert len(output["results"]) == 1

    def test_format_output_includes_metadata(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """format_output includes extracted RCCA metadata."""
        results = [
            SearchResult(
                id="test-1",
                content="The failure symptom was intermittent power loss.",
                score=0.9,
                document_title="Test Doc",
            ),
        ]

        output = strategy.format_output(results, {})

        result = output["results"][0]
        assert "rcca_metadata" in result
        assert "symptoms" in result["rcca_metadata"]
        assert "root_cause" in result["rcca_metadata"]
        assert "contributing_factors" in result["rcca_metadata"]
        assert "resolution" in result["rcca_metadata"]

    def test_extract_symptoms(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """_extract_rcca_metadata extracts symptom sentences."""
        result = SearchResult(
            id="1",
            content="The system exhibited intermittent failures. Error messages indicated timeout. The malfunction occurred under load.",
            score=0.8,
        )

        metadata = strategy._extract_rcca_metadata(result)

        assert len(metadata["symptoms"]) > 0
        assert any("failure" in s.lower() for s in metadata["symptoms"])

    def test_extract_root_cause(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """_extract_rcca_metadata extracts root cause."""
        result = SearchResult(
            id="1",
            content="Investigation revealed the root cause was insufficient buffer size. This led to memory overflow.",
            score=0.8,
        )

        metadata = strategy._extract_rcca_metadata(result)

        assert metadata["root_cause"] != ""
        assert "root cause" in metadata["root_cause"].lower()

    def test_extract_contributing_factors(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """_extract_rcca_metadata extracts contributing factors."""
        result = SearchResult(
            id="1",
            content="The contributing factor was high ambient temperature. Additional contributing factors included dust accumulation.",
            score=0.8,
        )

        metadata = strategy._extract_rcca_metadata(result)

        assert len(metadata["contributing_factors"]) > 0

    def test_extract_resolution(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """_extract_rcca_metadata extracts resolution."""
        result = SearchResult(
            id="1",
            content="The corrective action was to increase buffer size to 4KB. This fix resolved the issue.",
            score=0.8,
        )

        metadata = strategy._extract_rcca_metadata(result)

        assert metadata["resolution"] != ""
        assert "corrective action" in metadata["resolution"].lower() or "fix" in metadata["resolution"].lower()

    def test_extract_limits_symptoms(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """_extract_rcca_metadata limits symptoms to 3."""
        result = SearchResult(
            id="1",
            content="Failure one. Error two. Symptom three. Malfunction four. Issue five.",
            score=0.8,
        )

        metadata = strategy._extract_rcca_metadata(result)

        # Should limit to top 3
        assert len(metadata["symptoms"]) <= 3

    def test_split_sentences(
        self,
        strategy: RCCAStrategy,
    ) -> None:
        """_split_sentences splits text into sentences."""
        text = "First sentence. Second sentence! Third sentence? Fourth."

        sentences = strategy._split_sentences(text)

        assert len(sentences) >= 3
        assert "First sentence" in sentences[0]


class TestRCCAStrategyIntegration:
    """Integration tests for RCCAStrategy with WorkflowSearcher."""

    @pytest.fixture
    def mock_semantic_searcher(self) -> MagicMock:
        """Create mock semantic searcher."""
        searcher = MagicMock()
        searcher.search = AsyncMock(
            return_value=[
                SearchResult(
                    id="1",
                    content="The failure was caused by memory leak. Root cause: improper cleanup. Corrective action: implement destructor.",
                    score=0.9,
                    document_title="RCCA Report 42",
                    section_title="Power System Failure",
                ),
                SearchResult(
                    id="2",
                    content="General information about system architecture.",
                    score=0.7,
                    document_title="System Guide",
                ),
            ]
        )
        return searcher

    @pytest.fixture
    def workflow_searcher(
        self,
        mock_semantic_searcher: MagicMock,
    ) -> WorkflowSearcher:
        """Create WorkflowSearcher with RCCAStrategy."""
        return WorkflowSearcher(mock_semantic_searcher, RCCAStrategy())

    @pytest.mark.asyncio
    async def test_rcca_workflow_search(
        self,
        workflow_searcher: WorkflowSearcher,
    ) -> None:
        """WorkflowSearcher with RCCAStrategy returns RCCA results."""
        result = await workflow_searcher.search("power supply failure")

        assert result["result_type"] == "rcca_analysis"
        assert result["total_results"] >= 1

    @pytest.mark.asyncio
    async def test_rcca_workflow_applies_ranking(
        self,
        workflow_searcher: WorkflowSearcher,
    ) -> None:
        """WorkflowSearcher applies RCCA ranking adjustments."""
        result = await workflow_searcher.search("failure analysis")

        # Result with RCCA content should rank first
        assert result["results"][0]["id"] == "1"
        assert "rcca_metadata" in result["results"][0]

    @pytest.mark.asyncio
    async def test_rcca_workflow_extracts_metadata(
        self,
        workflow_searcher: WorkflowSearcher,
    ) -> None:
        """WorkflowSearcher extracts RCCA metadata."""
        result = await workflow_searcher.search("failure")

        first_result = result["results"][0]
        metadata = first_result["rcca_metadata"]

        # Should have extracted some RCCA fields
        assert "symptoms" in metadata
        assert "root_cause" in metadata
        assert "resolution" in metadata
