"""Unit tests for coverage assessment."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.search.coverage import (
    CoverageAssessor,
    CoverageConfig,
    CoverageGap,
    CoveredArea,
    CoveragePriority,
    CoverageReport,
    assess_knowledge_coverage,
)
from knowledge_mcp.search.models import SearchResult


class TestCoveragePriority:
    """Tests for CoveragePriority enum."""

    def test_enum_values(self) -> None:
        """Test priority values."""
        assert CoveragePriority.HIGH == "high"
        assert CoveragePriority.MEDIUM == "medium"
        assert CoveragePriority.LOW == "low"
        assert CoveragePriority.SUFFICIENT == "sufficient"


class TestCoverageGap:
    """Tests for CoverageGap dataclass."""

    def test_creation(self) -> None:
        """Test gap creation."""
        gap = CoverageGap(
            area="test area",
            priority=CoveragePriority.HIGH,
            confidence=0.9,
            reason="No content",
            max_similarity=0.1,
            result_count=0,
        )
        assert gap.area == "test area"
        assert gap.priority == CoveragePriority.HIGH
        assert gap.confidence == 0.9


class TestCoverageReport:
    """Tests for CoverageReport dataclass."""

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        report = CoverageReport(
            gaps=[
                CoverageGap(
                    area="gap1",
                    priority=CoveragePriority.HIGH,
                    confidence=0.8,
                    reason="No content",
                    max_similarity=0.0,
                    result_count=0,
                )
            ],
            covered=[
                CoveredArea(
                    area="covered1",
                    chunk_count=5,
                    avg_similarity=0.75,
                )
            ],
            total_areas=2,
            coverage_ratio=0.5,
        )

        d = report.to_dict()
        assert d["summary"]["total_areas"] == 2
        assert d["summary"]["coverage_ratio"] == 0.5
        assert len(d["gaps"]) == 1
        assert len(d["covered"]) == 1


class TestCoverageConfig:
    """Tests for CoverageConfig."""

    def test_default_values(self) -> None:
        """Test default configuration."""
        config = CoverageConfig()
        assert config.similarity_threshold == 0.5
        assert config.n_results == 10

    def test_custom_values(self) -> None:
        """Test custom configuration."""
        config = CoverageConfig(similarity_threshold=0.7, n_results=20)
        assert config.similarity_threshold == 0.7
        assert config.n_results == 20


class TestCoverageAssessor:
    """Tests for CoverageAssessor class."""

    @pytest.fixture
    def mock_searcher(self) -> MagicMock:
        """Create mock searcher."""
        searcher = MagicMock()
        searcher.search = AsyncMock()
        return searcher

    @pytest.fixture
    def assessor(self, mock_searcher: MagicMock) -> CoverageAssessor:
        """Create assessor with mock searcher."""
        return CoverageAssessor(mock_searcher)

    @pytest.mark.asyncio
    async def test_assess_empty_areas(self, assessor: CoverageAssessor) -> None:
        """Test assessment with no areas."""
        report = await assessor.assess([])
        assert report.total_areas == 0
        assert report.coverage_ratio == 0.0
        assert len(report.gaps) == 0

    @pytest.mark.asyncio
    async def test_assess_no_results_is_gap(
        self, assessor: CoverageAssessor, mock_searcher: MagicMock
    ) -> None:
        """Test that no results means gap."""
        mock_searcher.search.return_value = []

        report = await assessor.assess(["nonexistent topic"])

        assert len(report.gaps) == 1
        assert report.gaps[0].area == "nonexistent topic"
        assert report.gaps[0].priority == CoveragePriority.HIGH
        assert report.gaps[0].confidence == 1.0
        assert "No content found" in report.gaps[0].reason

    @pytest.mark.asyncio
    async def test_assess_high_similarity_is_covered(
        self, assessor: CoverageAssessor, mock_searcher: MagicMock
    ) -> None:
        """Test that high similarity means covered."""
        mock_searcher.search.return_value = [
            SearchResult(
                id="test-1",
                content="Relevant content",
                score=0.85,
                document_title="Good Doc",
                document_type="standard",
                section_title="Section",
                chunk_type="paragraph",
                section_hierarchy=[],
                clause_number="",
                page_numbers=[],
                normative=True,
            )
        ]

        report = await assessor.assess(["well covered topic"])

        assert len(report.covered) == 1
        assert len(report.gaps) == 0
        assert report.covered[0].area == "well covered topic"
        assert report.covered[0].avg_similarity == 0.85

    @pytest.mark.asyncio
    async def test_assess_low_similarity_is_gap(
        self, assessor: CoverageAssessor, mock_searcher: MagicMock
    ) -> None:
        """Test that low similarity means gap."""
        mock_searcher.search.return_value = [
            SearchResult(
                id="test-1",
                content="Vaguely related",
                score=0.2,
                document_title="Some Doc",
                document_type="article",
                section_title="Section",
                chunk_type="paragraph",
                section_hierarchy=[],
                clause_number="",
                page_numbers=[],
                normative=False,
            )
        ]

        report = await assessor.assess(["poorly covered topic"])

        assert len(report.gaps) == 1
        assert report.gaps[0].area == "poorly covered topic"
        assert "Low relevance" in report.gaps[0].reason

    def test_calculate_entropy_empty(self, assessor: CoverageAssessor) -> None:
        """Test entropy with empty list."""
        entropy = assessor._calculate_entropy([])
        assert entropy == 0.0

    def test_calculate_entropy_single(self, assessor: CoverageAssessor) -> None:
        """Test entropy with single value."""
        entropy = assessor._calculate_entropy([0.5])
        assert entropy == 0.0

    def test_calculate_entropy_uniform(self, assessor: CoverageAssessor) -> None:
        """Test entropy with uniform distribution."""
        # Uniform distribution has max entropy
        entropy = assessor._calculate_entropy([0.25, 0.25, 0.25, 0.25])
        assert entropy > 0.9  # Should be close to 1.0

    def test_calculate_entropy_concentrated(self, assessor: CoverageAssessor) -> None:
        """Test entropy with concentrated distribution."""
        # One dominant value has low entropy
        entropy = assessor._calculate_entropy([0.9, 0.05, 0.03, 0.02])
        assert entropy < 0.5

    def test_determine_priority_very_low_similarity(
        self, assessor: CoverageAssessor
    ) -> None:
        """Test HIGH priority for very low similarity."""
        priority = assessor._determine_priority(0.1, 0.5)
        assert priority == CoveragePriority.HIGH

    def test_determine_priority_high_confidence(
        self, assessor: CoverageAssessor
    ) -> None:
        """Test HIGH priority for high confidence gap."""
        priority = assessor._determine_priority(0.4, 0.8)
        assert priority == CoveragePriority.HIGH

    def test_determine_priority_medium(self, assessor: CoverageAssessor) -> None:
        """Test MEDIUM priority."""
        priority = assessor._determine_priority(0.4, 0.5)
        assert priority == CoveragePriority.MEDIUM

    def test_determine_priority_low(self, assessor: CoverageAssessor) -> None:
        """Test LOW priority."""
        priority = assessor._determine_priority(0.45, 0.3)
        assert priority == CoveragePriority.LOW

    def test_calculate_gap_confidence_low_sim(self, assessor: CoverageAssessor) -> None:
        """Test confidence calculation with low similarity."""
        confidence = assessor._calculate_gap_confidence(0.1, 0.5, 3)
        assert confidence > 0.5  # Low similarity should give high confidence

    def test_calculate_gap_confidence_high_entropy(
        self, assessor: CoverageAssessor
    ) -> None:
        """Test confidence calculation with high entropy."""
        confidence = assessor._calculate_gap_confidence(0.4, 0.9, 5)
        assert confidence > 0.3  # High entropy contributes to gap confidence

    @pytest.mark.asyncio
    async def test_assess_multiple_areas(
        self, assessor: CoverageAssessor, mock_searcher: MagicMock
    ) -> None:
        """Test assessment with multiple areas."""

        async def mock_search(query: str, n_results: int) -> list[SearchResult]:
            """Mock search that returns different results based on query."""
            if query == "covered":
                return [
                    SearchResult(
                        id="test-1",
                        content="Good content",
                        score=0.8,
                        document_title="Doc",
                        document_type="standard",
                        section_title="Section",
                        chunk_type="paragraph",
                        section_hierarchy=[],
                        clause_number="",
                        page_numbers=[],
                        normative=True,
                    )
                ]
            else:
                return []

        mock_searcher.search.side_effect = mock_search

        report = await assessor.assess(["covered", "gap"])

        assert report.total_areas == 2
        assert len(report.covered) == 1
        assert len(report.gaps) == 1
        assert report.coverage_ratio == 0.5

    @pytest.mark.asyncio
    async def test_assess_overall_priority_high(
        self, assessor: CoverageAssessor, mock_searcher: MagicMock
    ) -> None:
        """Test overall priority when many high priority gaps."""
        mock_searcher.search.return_value = []

        report = await assessor.assess(["gap1", "gap2"])

        assert report.overall_priority == CoveragePriority.HIGH

    @pytest.mark.asyncio
    async def test_assess_overall_priority_sufficient(
        self, assessor: CoverageAssessor, mock_searcher: MagicMock
    ) -> None:
        """Test overall priority when all covered."""
        mock_searcher.search.return_value = [
            SearchResult(
                id="test-1",
                content="Good content",
                score=0.8,
                document_title="Doc",
                document_type="standard",
                section_title="Section",
                chunk_type="paragraph",
                section_hierarchy=[],
                clause_number="",
                page_numbers=[],
                normative=True,
            )
        ]

        report = await assessor.assess(["area1", "area2"])

        assert report.overall_priority == CoveragePriority.SUFFICIENT


class TestAssessKnowledgeCoverage:
    """Tests for convenience function."""

    @pytest.mark.asyncio
    async def test_function_creates_assessor(self) -> None:
        """Test function creates assessor and runs."""
        mock_searcher = MagicMock()
        mock_searcher.search = AsyncMock(return_value=[])

        report = await assess_knowledge_coverage(mock_searcher, ["test area"])

        assert isinstance(report, CoverageReport)
        assert report.total_areas == 1

    @pytest.mark.asyncio
    async def test_function_with_config(self) -> None:
        """Test function with custom config."""
        mock_searcher = MagicMock()
        mock_searcher.search = AsyncMock(return_value=[])
        config = CoverageConfig(similarity_threshold=0.7)

        report = await assess_knowledge_coverage(mock_searcher, ["test"], config)

        assert isinstance(report, CoverageReport)
