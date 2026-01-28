"""Plan workflow search strategy.

Implements SearchStrategy for planning workflows, with support for
templates, risk analysis, lessons learned, and precedent retrieval.

Example:
    >>> from knowledge_mcp.search.strategies.plan import PlanStrategy
    >>> strategy = PlanStrategy()
    >>> query = await strategy.preprocess_query("project planning", {})
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from knowledge_mcp.search.strategies.base import SearchQuery, SearchStrategy

if TYPE_CHECKING:
    from knowledge_mcp.search.models import SearchResult


class PlanStrategy(SearchStrategy):
    """Search strategy for planning workflows.

    Optimizes search for:
    - Planning templates and frameworks
    - Risk identification and mitigation
    - Lessons learned from past projects
    - Precedents and best practices

    Supports categorization by:
    - templates: Planning templates, frameworks, methodologies
    - risks: Risk analysis, mitigation strategies
    - lessons_learned: Post-project reviews, retrospectives
    - precedents: Similar past projects, case studies
    """

    # Keywords to boost for planning-related content
    PLANNING_KEYWORDS = [
        "planning",
        "template",
        "framework",
        "methodology",
        "approach",
        "strategy",
        "roadmap",
        "schedule",
        "timeline",
    ]

    # Category-specific keywords
    CATEGORY_KEYWORDS = {
        "templates": ["template", "framework", "methodology", "pattern", "structure"],
        "risks": ["risk", "hazard", "threat", "mitigation", "contingency", "failure"],
        "lessons_learned": [
            "lesson",
            "retrospective",
            "post-mortem",
            "learned",
            "experience",
        ],
        "precedents": [
            "precedent",
            "case study",
            "example",
            "similar",
            "previous",
            "past project",
        ],
    }

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any],
    ) -> SearchQuery:
        """Transform user query into internal search representation.

        Adds planning-specific keyword expansions and category filters.

        Args:
            query: Natural language query from user.
            params: Tool-specific parameters (may include "category" key).

        Returns:
            SearchQuery with expanded terms and category facets.
        """
        expanded_terms: list[str] = []
        facets: list[str] = []

        # Check if a specific category is requested
        category = params.get("category")
        if category and category in self.CATEGORY_KEYWORDS:
            # Add category-specific keywords
            expanded_terms.extend(self.CATEGORY_KEYWORDS[category])
            facets.append(category)
        else:
            # Add general planning keywords
            expanded_terms.extend(self.PLANNING_KEYWORDS)
            # Include all categories as facets
            facets.extend(list(self.CATEGORY_KEYWORDS.keys()))

        return SearchQuery(
            original=query,
            expanded_terms=expanded_terms,
            filters=params.get("filters", {}),
            facets=facets,
        )

    def adjust_ranking(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """Apply planning-specific ranking adjustments.

        Boosts results containing planning keywords or matching categories.

        Args:
            results: Raw semantic search results.

        Returns:
            Reranked results with adjusted scores.
        """
        for result in results:
            content_lower = result.content.lower()

            # Boost for planning keywords
            planning_matches = sum(
                1 for keyword in self.PLANNING_KEYWORDS if keyword in content_lower
            )
            if planning_matches > 0:
                # Boost by up to 10% based on keyword density
                boost = min(0.1, planning_matches * 0.02)
                result.score = min(1.0, result.score * (1.0 + boost))

            # Additional boost for templates/frameworks in metadata
            doc_type = result.metadata.get("document_type", "").lower()
            if "template" in doc_type or "framework" in doc_type:
                result.score = min(1.0, result.score * 1.05)

        # Re-sort by adjusted scores
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def format_output(
        self,
        results: list[SearchResult],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Structure output for planning workflow.

        Organizes results by category (templates, risks, lessons_learned, precedents)
        if multiple categories are present, otherwise returns flat list.

        Args:
            results: Ranked search results.
            params: Original tool parameters.

        Returns:
            Formatted dict with categorized results and metadata.
        """
        category = params.get("category")

        # If specific category requested, return flat structure
        if category:
            return {
                "result_type": "plan_analysis",
                "category": category,
                "results": [
                    {
                        "content": r.content,
                        "score": r.score,
                        "document_title": r.document_title,
                        "section_title": r.section_title,
                        "chunk_type": r.chunk_type,
                    }
                    for r in results
                ],
                "count": len(results),
            }

        # Otherwise, categorize results by content
        categorized: dict[str, list[dict[str, Any]]] = {
            "templates": [],
            "risks": [],
            "lessons_learned": [],
            "precedents": [],
        }

        for result in results:
            content_lower = result.content.lower()
            result_dict = {
                "content": result.content,
                "score": result.score,
                "document_title": result.document_title,
                "section_title": result.section_title,
                "chunk_type": result.chunk_type,
            }

            # Categorize based on keyword matching
            categorized_flag = False
            for cat, keywords in self.CATEGORY_KEYWORDS.items():
                if any(keyword in content_lower for keyword in keywords):
                    categorized[cat].append(result_dict)
                    categorized_flag = True
                    break

            # If no category match, add to templates as default
            if not categorized_flag:
                categorized["templates"].append(result_dict)

        return {
            "result_type": "plan_analysis",
            "categories": categorized,
            "total_results": len(results),
        }
