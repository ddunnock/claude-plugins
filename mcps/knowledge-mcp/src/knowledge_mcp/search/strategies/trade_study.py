"""Trade study strategy for decision support workflows.

This strategy helps with trade studies and alternative analysis by:
1. Boosting keywords related to evaluation, criteria, and trade-offs
2. Grouping results by alternative with criteria evidence
3. Extracting quantitative values and comparison data

Example:
    >>> strategy = TradeStudyStrategy()
    >>> query = await strategy.preprocess_query("Compare Architecture A vs B", {})
    >>> results = semantic_search(query)
    >>> formatted = strategy.format_output(results, {})
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from knowledge_mcp.search.strategies.base import SearchQuery, SearchStrategy

if TYPE_CHECKING:
    from knowledge_mcp.search.models import SearchResult


class TradeStudyStrategy(SearchStrategy):
    """Strategy for trade study and decision support workflows.

    Groups results by alternative and extracts criteria evidence with
    quantitative values to support comparative evaluation.

    The strategy synthesizes comparison information from any relevant content,
    not just pre-tagged trade study documents.
    """

    # Keywords to boost for trade study relevance
    TRADE_STUDY_KEYWORDS = [
        "alternative",
        "option",
        "criteria",
        "trade-off",
        "tradeoff",
        "evaluation",
        "comparison",
        "assessment",
        "advantage",
        "disadvantage",
        "benefit",
        "drawback",
        "versus",
        "vs",
        "compare",
    ]

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any],
    ) -> SearchQuery:
        """Transform query to boost trade study and decision-related keywords.

        Args:
            query: Natural language query from user.
            params: Tool parameters, may include "alternatives" list.

        Returns:
            SearchQuery with trade study keywords as expanded terms.

        Example:
            >>> strategy = TradeStudyStrategy()
            >>> q = await strategy.preprocess_query("Compare A vs B", {})
            >>> print(q.expanded_terms[:3])
            ['alternative', 'criteria', 'trade-off']
        """
        # Add trade study keywords as expanded terms for broader matching
        search_query = SearchQuery(
            original=query,
            expanded_terms=self.TRADE_STUDY_KEYWORDS.copy(),
        )

        # If alternatives are provided in params, add them as facets
        alternatives = params.get("alternatives", [])
        if alternatives:
            search_query.facets = [str(alt) for alt in alternatives]

        return search_query

    def adjust_ranking(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """Boost results containing evaluation and criteria keywords.

        Args:
            results: Raw semantic search results.

        Returns:
            Reranked results with score boosts for decision-relevant content.

        Note:
            Boosts scores by 10% for each keyword match (capped at +30%).
        """
        boosted_results: list[SearchResult] = []

        for result in results:
            content_lower = result.content.lower()

            # Count keyword matches
            matches = sum(
                1 for keyword in self.TRADE_STUDY_KEYWORDS if keyword in content_lower
            )

            # Apply boost: 0.1 per match, cap at 0.3
            boost = min(matches * 0.1, 0.3)
            boosted_score = min(result.score + boost, 1.0)

            # Create new result with boosted score
            result.score = boosted_score
            boosted_results.append(result)

        # Re-sort by boosted scores
        boosted_results.sort(key=lambda r: r.score, reverse=True)

        return boosted_results

    def format_output(
        self,
        results: list[SearchResult],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Format results grouped by alternative with criteria evidence.

        Args:
            results: Ranked search results.
            params: Original tool parameters including "alternatives" list.

        Returns:
            Dict with result_type "trade_study" and alternatives list.
            Each alternative includes criteria with evidence and quantitative values.

        Example output structure:
            {
                "result_type": "trade_study",
                "alternatives": [
                    {
                        "name": "Option A",
                        "criteria": [
                            {
                                "name": "Performance",
                                "evidence": "System achieves 99.9% uptime",
                                "value": "99.9%",
                                "source": {
                                    "chunk_id": "...",
                                    "document_title": "...",
                                    "score": 0.95
                                }
                            }
                        ]
                    }
                ]
            }
        """
        alternatives = params.get("alternatives", [])

        # If alternatives provided, group results by alternative
        if alternatives:
            grouped = self._group_by_alternative(results, alternatives)
        else:
            # If no alternatives specified, extract them from results
            grouped = self._extract_alternatives_from_results(results)

        return {
            "result_type": "trade_study",
            "alternatives": grouped,
            "total_sources": len(results),
        }

    def _group_by_alternative(
        self,
        results: list[SearchResult],
        alternatives: list[str],
    ) -> list[dict[str, Any]]:
        """Group results by specified alternatives.

        Args:
            results: Search results to group.
            alternatives: List of alternative names to group by.

        Returns:
            List of alternative dicts with criteria evidence.
        """
        grouped: list[dict[str, Any]] = []

        for alternative in alternatives:
            alt_lower = alternative.lower()

            # Find results mentioning this alternative
            matching_results = [
                r for r in results if alt_lower in r.content.lower()
            ]

            # Extract criteria from matching results
            criteria: list[dict[str, Any]] = []
            for result in matching_results[:5]:  # Top 5 per alternative
                criterion = self._extract_criterion(result, alternative)
                if criterion:
                    criteria.append(criterion)

            grouped.append(
                {
                    "name": alternative,
                    "criteria": criteria,
                    "source_count": len(matching_results),
                }
            )

        return grouped

    def _extract_alternatives_from_results(
        self,
        results: list[SearchResult],
    ) -> list[dict[str, Any]]:
        """Extract alternatives from results when not specified.

        Args:
            results: Search results to analyze.

        Returns:
            List of alternative dicts inferred from content.
        """
        # Simple heuristic: look for "Option X", "Alternative Y" patterns
        alternatives_found: list[dict[str, Any]] = []

        for result in results[:10]:  # Check top 10 results
            content = result.content
            # Look for common patterns
            for keyword in ["option", "alternative", "approach", "solution"]:
                if keyword in content.lower():
                    # Extract a short name from context
                    criterion = self._extract_criterion(result, keyword)
                    if criterion:
                        alternatives_found.append(
                            {
                                "name": f"Found: {keyword}",
                                "criteria": [criterion],
                                "source_count": 1,
                            }
                        )
                    break

        # Fallback: treat all results as general evidence
        if not alternatives_found:
            return [
                {
                    "name": "General Evidence",
                    "criteria": [
                        self._extract_criterion(r, "General") for r in results[:5]
                    ],
                    "source_count": len(results),
                }
            ]

        return alternatives_found

    def _extract_criterion(
        self,
        result: SearchResult,
        alternative: str,
    ) -> dict[str, Any]:
        """Extract a single criterion with evidence from a result.

        Args:
            result: Search result to extract from.
            alternative: Alternative name for context.

        Returns:
            Dict with criterion name, evidence, extracted value, and source.
        """
        # Look for quantitative values (percentages, numbers with units)
        content = result.content
        value = self._extract_quantitative_value(content)

        # Try to identify criterion type from content
        criterion_name = self._identify_criterion_type(content)

        return {
            "name": criterion_name,
            "evidence": content[:200] + ("..." if len(content) > 200 else ""),
            "value": value,
            "source": {
                "chunk_id": result.id,
                "document_title": result.document_title,
                "section_title": result.section_title,
                "score": round(result.score, 3),
            },
        }

    def _extract_quantitative_value(self, content: str) -> str | None:
        """Extract quantitative value from content (percentage, number with unit).

        Args:
            content: Text to extract from.

        Returns:
            Extracted value string or None if not found.
        """
        import re

        # Look for percentages
        pct_match = re.search(r"\d+\.?\d*\s*%", content)
        if pct_match:
            return pct_match.group(0)

        # Look for numbers with common units
        unit_match = re.search(
            r"\d+\.?\d*\s*(ms|seconds?|minutes?|hours?|days?|MB|GB|TB|kg|lbs?|m|ft|km|mi)",
            content,
            re.IGNORECASE,
        )
        if unit_match:
            return unit_match.group(0)

        return None

    def _identify_criterion_type(self, content: str) -> str:
        """Identify evaluation criterion type from content.

        Args:
            content: Text to analyze.

        Returns:
            Criterion type name (e.g., "Performance", "Cost", "Reliability").
        """
        content_lower = content.lower()

        # Map keywords to criterion types
        criterion_keywords = {
            "Performance": [
                "performance",
                "speed",
                "throughput",
                "latency",
                "response time",
            ],
            "Cost": ["cost", "price", "expense", "budget", "affordable"],
            "Reliability": [
                "reliability",
                "availability",
                "uptime",
                "failure",
                "mtbf",
            ],
            "Security": ["security", "secure", "vulnerability", "risk", "threat"],
            "Scalability": ["scalability", "scalable", "scale", "growth", "capacity"],
            "Maintainability": [
                "maintainability",
                "maintenance",
                "maintainable",
                "support",
            ],
            "Usability": ["usability", "usable", "user-friendly", "ease of use"],
        }

        for criterion_type, keywords in criterion_keywords.items():
            if any(kw in content_lower for kw in keywords):
                return criterion_type

        return "General Criterion"
