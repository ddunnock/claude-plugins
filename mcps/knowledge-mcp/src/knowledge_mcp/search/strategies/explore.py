"""Exploration strategy for multi-facet knowledge discovery.

Implements ExploreStrategy for broad exploration workflows across
multiple facets like definitions, examples, standards, and best practices.

Example:
    >>> from knowledge_mcp.search.strategies.explore import ExploreStrategy
    >>> strategy = ExploreStrategy()
    >>> query = await strategy.preprocess_query("requirements analysis")
    >>> print(query.facets)
    ['definitions', 'examples', 'standards', 'best_practices']
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from knowledge_mcp.search.strategies.base import SearchQuery, SearchStrategy

if TYPE_CHECKING:
    from knowledge_mcp.search.models import SearchResult


class ExploreStrategy(SearchStrategy):
    """Strategy for multi-facet exploration of knowledge base.

    Supports broad exploration across 4 default facets:
    1. Definitions - Terminology and conceptual definitions
    2. Examples - Concrete examples and case studies
    3. Standards - Normative requirements and standards
    4. Best Practices - Guidance and recommended approaches

    The strategy organizes results by facet to provide comprehensive
    coverage of a topic from multiple perspectives.

    Attributes:
        default_facets: List of default facet names to explore.

    Example:
        >>> strategy = ExploreStrategy()
        >>> query = await strategy.preprocess_query("verification")
        >>> print(query.facets)
        ['definitions', 'examples', 'standards', 'best_practices']
    """

    default_facets: list[str] = [
        "definitions",
        "examples",
        "standards",
        "best_practices",
    ]

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any],
    ) -> SearchQuery:
        """Transform query into multi-facet search.

        Adds default facets unless custom facets provided in params.
        Each facet represents a different perspective on the topic.

        Args:
            query: Natural language query from user.
            params: Optional facets override via params["facets"].

        Returns:
            SearchQuery with facets populated for multi-aspect search.

        Example:
            >>> strategy = ExploreStrategy()
            >>> query = await strategy.preprocess_query("risk management")
            >>> len(query.facets)
            4
        """
        # Extract facets with type safety
        facets_param = params.get("facets")
        if isinstance(facets_param, list) and facets_param:
            # Runtime validation that all items are strings
            if all(isinstance(f, str) for f in cast(list[Any], facets_param)):
                facets = cast(list[str], facets_param)
            else:
                facets = self.default_facets
        else:
            facets = self.default_facets

        return SearchQuery(
            original=query,
            filters=params.get("filters", {}),
            facets=facets,
        )

    def adjust_ranking(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """Apply facet-aware ranking adjustments.

        For exploration, we prioritize diverse content types:
        - Definitions: +20% boost if chunk_type="definition"
        - Examples: +15% boost if chunk_type="example"
        - Standards: +10% boost if normative=True
        - Best practices: +10% boost if chunk_type="guidance"

        Args:
            results: Raw semantic search results.

        Returns:
            Reranked results with facet-aware score adjustments.
        """
        for result in results:
            chunk_type = result.chunk_type.lower() if result.chunk_type else ""

            # Apply facet-specific boosts
            if chunk_type == "definition":
                result.score = min(1.0, result.score * 1.20)
            elif chunk_type == "example":
                result.score = min(1.0, result.score * 1.15)
            elif result.normative:
                result.score = min(1.0, result.score * 1.10)
            elif chunk_type == "guidance":
                result.score = min(1.0, result.score * 1.10)

        return sorted(results, key=lambda r: r.score, reverse=True)

    def format_output(
        self,
        results: list[SearchResult],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Structure results by facet for comprehensive exploration.

        Organizes results into facet categories and calculates coverage
        metrics to show which perspectives are well-represented.

        Args:
            results: Ranked search results.
            params: Original parameters (contains facets list).

        Returns:
            Dict with results organized by facet plus coverage metadata.

        Example:
            >>> output = strategy.format_output(results, params)
            >>> print(output.keys())
            dict_keys(['results_by_facet', 'facet_coverage', 'result_type'])
        """
        facets = params.get("facets", self.default_facets)

        # Organize results by facet
        results_by_facet: dict[str, list[dict[str, Any]]] = {
            facet: [] for facet in facets
        }

        for result in results:
            # Determine which facet this result belongs to
            chunk_type = result.chunk_type.lower() if result.chunk_type else ""

            if chunk_type == "definition":
                facet = "definitions"
            elif chunk_type == "example":
                facet = "examples"
            elif result.normative:
                facet = "standards"
            elif chunk_type == "guidance":
                facet = "best_practices"
            else:
                # Default to best_practices for uncategorized content
                facet = "best_practices"

            if facet in results_by_facet:
                results_by_facet[facet].append({
                    "content": result.content,
                    "score": result.score,
                    "document_title": result.document_title,
                    "section_title": result.section_title,
                    "chunk_type": result.chunk_type,
                    "normative": result.normative,
                })

        # Calculate facet coverage
        facet_coverage = {
            facet: len(results_by_facet[facet]) for facet in facets
        }

        return {
            "results_by_facet": results_by_facet,
            "facet_coverage": facet_coverage,
            "total_results": len(results),
            "facets_explored": facets,
            "result_type": "explore_analysis",
        }
