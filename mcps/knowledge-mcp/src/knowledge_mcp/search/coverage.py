"""Coverage assessment for knowledge gaps.

Uses semantic search to identify areas where knowledge base
has low coverage, providing actionable gap reports.

Based on semantic entropy approach from research:
- Low similarity scores indicate sparse coverage
- High entropy among results suggests uncertainty
- Combines both signals for confidence scoring

Example:
    >>> assessor = CoverageAssessor(searcher)
    >>> report = await assessor.assess(["system requirements", "trade studies"])
    >>> for gap in report.gaps:
    ...     print(f"{gap.area}: {gap.confidence:.2f}")
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from knowledge_mcp.search.semantic_search import SemanticSearcher

logger = logging.getLogger(__name__)


class CoveragePriority(str, Enum):
    """Priority level for addressing gaps."""

    HIGH = "high"  # No content, urgent
    MEDIUM = "medium"  # Some content, improvement needed
    LOW = "low"  # Adequate, optional enhancement
    SUFFICIENT = "sufficient"  # Good coverage, no action needed


@dataclass
class CoverageGap:
    """A detected knowledge gap."""

    area: str  # Knowledge area queried
    priority: CoveragePriority  # How urgent to address
    confidence: float  # 0-1, how certain we are this is a gap
    reason: str  # Human-readable explanation
    max_similarity: float  # Best match score found
    result_count: int  # How many results returned
    suggested_query: str | None = None  # Suggested search for acquisition


@dataclass
class CoveredArea:
    """An adequately covered knowledge area."""

    area: str
    chunk_count: int
    avg_similarity: float
    best_match_title: str | None = None


def _default_gaps() -> list[CoverageGap]:
    return []


def _default_covered() -> list[CoveredArea]:
    return []


@dataclass
class CoverageReport:
    """Complete coverage assessment report."""

    gaps: list[CoverageGap] = field(default_factory=_default_gaps)
    covered: list[CoveredArea] = field(default_factory=_default_covered)
    total_areas: int = 0
    coverage_ratio: float = 0.0
    overall_priority: CoveragePriority = CoveragePriority.SUFFICIENT

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "gaps": [
                {
                    "area": g.area,
                    "priority": g.priority.value,
                    "confidence": round(g.confidence, 3),
                    "reason": g.reason,
                    "max_similarity": round(g.max_similarity, 3),
                    "result_count": g.result_count,
                    "suggested_query": g.suggested_query,
                }
                for g in self.gaps
            ],
            "covered": [
                {
                    "area": c.area,
                    "chunk_count": c.chunk_count,
                    "avg_similarity": round(c.avg_similarity, 3),
                    "best_match_title": c.best_match_title,
                }
                for c in self.covered
            ],
            "summary": {
                "total_areas": self.total_areas,
                "coverage_ratio": round(self.coverage_ratio, 3),
                "gaps_count": len(self.gaps),
                "covered_count": len(self.covered),
                "overall_priority": self.overall_priority.value,
            },
        }


@dataclass
class CoverageConfig:
    """Configuration for coverage assessment."""

    similarity_threshold: float = 0.5  # Below this = gap
    high_confidence_threshold: float = 0.3  # Below this = high priority
    min_results_for_coverage: int = 3  # Need at least this many results
    n_results: int = 10  # Results to fetch per area
    entropy_weight: float = 0.3  # Weight of entropy in confidence


class CoverageAssessor:
    """Assesses knowledge coverage and identifies gaps.

    Uses semantic search to probe coverage in specified areas.
    Calculates confidence using similarity scores and entropy.

    Example:
        >>> searcher = SemanticSearcher(embedder, store)
        >>> assessor = CoverageAssessor(searcher)
        >>> report = await assessor.assess(["requirements management"])
    """

    def __init__(
        self,
        searcher: SemanticSearcher,
        config: CoverageConfig | None = None,
    ):
        """Initialize coverage assessor.

        Args:
            searcher: SemanticSearcher instance for queries.
            config: Assessment configuration.
        """
        self.searcher = searcher
        self.config = config or CoverageConfig()

    async def assess(self, knowledge_areas: list[str]) -> CoverageReport:
        """Assess coverage for specified knowledge areas.

        Args:
            knowledge_areas: List of topics/areas to check.

        Returns:
            CoverageReport with gaps and covered areas.
        """
        gaps: list[CoverageGap] = []
        covered: list[CoveredArea] = []

        for area in knowledge_areas:
            gap: CoverageGap | None
            covered_area: CoveredArea | None
            gap, covered_area = await self._assess_area(area)
            if gap:
                gaps.append(gap)
            if covered_area:
                covered.append(covered_area)

        # Calculate overall stats
        total = len(knowledge_areas)
        coverage_ratio = len(covered) / total if total > 0 else 0.0

        # Determine overall priority
        high_priority_gaps = sum(1 for g in gaps if g.priority == CoveragePriority.HIGH)
        if high_priority_gaps > total * 0.5:
            overall_priority = CoveragePriority.HIGH
        elif len(gaps) > len(covered):
            overall_priority = CoveragePriority.MEDIUM
        elif gaps:
            overall_priority = CoveragePriority.LOW
        else:
            overall_priority = CoveragePriority.SUFFICIENT

        return CoverageReport(
            gaps=gaps,
            covered=covered,
            total_areas=total,
            coverage_ratio=coverage_ratio,
            overall_priority=overall_priority,
        )

    async def _assess_area(
        self, area: str
    ) -> tuple[CoverageGap | None, CoveredArea | None]:
        """Assess a single knowledge area.

        Returns tuple of (gap, covered_area) - one will be None.
        """
        try:
            # Search for content in this area
            results = await self.searcher.search(
                query=area,
                n_results=self.config.n_results,
            )

            # No results = definite gap
            if not results:
                return (
                    CoverageGap(
                        area=area,
                        priority=CoveragePriority.HIGH,
                        confidence=1.0,
                        reason="No content found",
                        max_similarity=0.0,
                        result_count=0,
                        suggested_query=f"'{area}' documentation OR tutorial OR guide",
                    ),
                    None,
                )

            # Extract similarity scores
            similarities = [r.score for r in results]
            max_sim = max(similarities)
            avg_sim = sum(similarities) / len(similarities)

            # Calculate entropy (uncertainty)
            entropy = self._calculate_entropy(similarities)

            # Determine if this is a gap
            if max_sim < self.config.similarity_threshold:
                # Low similarity = gap
                confidence = self._calculate_gap_confidence(max_sim, entropy, len(results))
                priority = self._determine_priority(max_sim, confidence)

                return (
                    CoverageGap(
                        area=area,
                        priority=priority,
                        confidence=confidence,
                        reason=f"Low relevance scores (max: {max_sim:.2f})",
                        max_similarity=max_sim,
                        result_count=len(results),
                        suggested_query=f"'{area}' best practices OR standards",
                    ),
                    None,
                )

            # Adequate coverage
            best_match = results[0]
            return (
                None,
                CoveredArea(
                    area=area,
                    chunk_count=len(results),
                    avg_similarity=avg_sim,
                    best_match_title=best_match.document_title,
                ),
            )

        except Exception as e:
            logger.warning("Error assessing area '%s': %s", area, e)
            # Return as gap with error reason
            return (
                CoverageGap(
                    area=area,
                    priority=CoveragePriority.MEDIUM,
                    confidence=0.5,
                    reason=f"Assessment error: {e!s}",
                    max_similarity=0.0,
                    result_count=0,
                ),
                None,
            )

    def _calculate_entropy(self, similarities: list[float]) -> float:
        """Calculate Shannon entropy of similarity distribution.

        Higher entropy = more uncertainty = likely gap.
        """
        if not similarities or len(similarities) < 2:
            return 0.0

        # Normalize to probabilities
        total = sum(similarities)
        if total == 0:
            return 1.0  # Max entropy if no signal

        probs = [s / total for s in similarities]

        # Shannon entropy
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)

        # Normalize to 0-1 (max entropy for n items is log2(n))
        max_entropy = math.log2(len(similarities))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _calculate_gap_confidence(
        self, max_sim: float, entropy: float, result_count: int
    ) -> float:
        """Calculate confidence that this is a genuine gap.

        Combines:
        - Low similarity (inverted)
        - High entropy (uncertainty)
        - Low result count
        """
        # Similarity component: lower = more confident it's a gap
        sim_component = 1.0 - (max_sim / self.config.similarity_threshold)
        sim_component = max(0.0, min(1.0, sim_component))

        # Entropy component: higher = more uncertain = more likely gap
        entropy_component = entropy

        # Result count component: fewer results = more confident gap
        count_component = 1.0 - (result_count / self.config.n_results)
        count_component = max(0.0, min(1.0, count_component))

        # Weighted combination
        confidence = (
            sim_component * 0.5
            + entropy_component * self.config.entropy_weight
            + count_component * (0.5 - self.config.entropy_weight)
        )

        return min(1.0, confidence)

    def _determine_priority(self, max_sim: float, confidence: float) -> CoveragePriority:
        """Determine gap priority based on metrics."""
        if max_sim < self.config.high_confidence_threshold or confidence > 0.7:
            return CoveragePriority.HIGH
        elif confidence > 0.4:
            return CoveragePriority.MEDIUM
        else:
            return CoveragePriority.LOW


async def assess_knowledge_coverage(
    searcher: SemanticSearcher,
    areas: list[str],
    config: CoverageConfig | None = None,
) -> CoverageReport:
    """Convenience function for coverage assessment.

    Args:
        searcher: SemanticSearcher instance.
        areas: Knowledge areas to assess.
        config: Optional configuration.

    Returns:
        CoverageReport with results.
    """
    assessor = CoverageAssessor(searcher, config)
    return await assessor.assess(areas)
