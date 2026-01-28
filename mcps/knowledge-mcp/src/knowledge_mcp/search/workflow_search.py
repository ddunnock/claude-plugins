"""Workflow search orchestrator using strategy pattern.

This module provides the WorkflowSearcher class that orchestrates
specialized searches by delegating to strategy objects.

The template method pattern defines the search algorithm structure:
1. Preprocess query (strategy)
2. Execute semantic search (shared)
3. Adjust ranking (strategy)
4. Format output (strategy)

Example:
    >>> from knowledge_mcp.search import SemanticSearcher
    >>> from knowledge_mcp.search.workflow_search import WorkflowSearcher
    >>> from knowledge_mcp.search.strategies.rcca import RCCAStrategy
    >>>
    >>> searcher = WorkflowSearcher(semantic_searcher, RCCAStrategy())
    >>> results = await searcher.search("power supply failure")
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from knowledge_mcp.search.semantic_search import SemanticSearcher
    from knowledge_mcp.search.strategies.base import SearchStrategy

logger = logging.getLogger(__name__)


class WorkflowSearcher:
    """Orchestrates workflow-specific searches using strategy pattern.

    Combines a shared SemanticSearcher with interchangeable strategies
    to provide specialized retrieval for different workflows.

    Attributes:
        searcher: The underlying semantic search implementation.
        strategy: The workflow-specific search strategy.

    Example:
        >>> from knowledge_mcp.search.strategies.trade import TradeStudyStrategy
        >>>
        >>> workflow = WorkflowSearcher(semantic_searcher, TradeStudyStrategy())
        >>> results = await workflow.search(
        ...     query="database comparison",
        ...     params={"alternatives": ["PostgreSQL", "MongoDB"]}
        ... )
    """

    def __init__(
        self,
        searcher: SemanticSearcher,
        strategy: SearchStrategy,
    ) -> None:
        """Initialize workflow searcher.

        Args:
            searcher: Semantic search implementation for vector similarity.
            strategy: Workflow-specific strategy for customization.
        """
        self._searcher = searcher
        self._strategy = strategy

    @property
    def strategy(self) -> SearchStrategy:
        """Get the current search strategy."""
        return self._strategy

    def set_strategy(self, strategy: SearchStrategy) -> None:
        """Change the search strategy at runtime.

        Args:
            strategy: New workflow strategy to use.

        Example:
            >>> workflow.set_strategy(ExploreStrategy())
        """
        self._strategy = strategy

    async def search(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        n_results: int = 10,
        score_threshold: float = 0.0,
    ) -> dict[str, Any]:
        """Execute workflow-specific search.

        Template method that defines the search algorithm:
        1. Preprocess query using strategy
        2. Execute semantic search
        3. Adjust ranking using strategy
        4. Format output using strategy

        Args:
            query: Natural language search query.
            params: Strategy-specific parameters (varies by workflow).
            n_results: Maximum results to return. Defaults to 10.
            score_threshold: Minimum similarity score. Defaults to 0.0.

        Returns:
            Formatted dict from strategy.format_output().
            Always includes "result_type" and "total_results" fields.

        Example:
            >>> results = await workflow.search(
            ...     query="requirements traceability",
            ...     params={"facets": ["definitions", "examples"]},
            ...     n_results=20,
            ... )
        """
        params = params or {}

        try:
            # 1. Preprocess query (strategy-specific)
            search_query = await self._strategy.preprocess_query(query, params)
            logger.debug(
                "Preprocessed query: original=%s, expanded=%d terms, filters=%s",
                search_query.original[:50],
                len(search_query.expanded_terms),
                list(search_query.filters.keys()),
            )

            # 2. Execute semantic search (shared core)
            results = await self._searcher.search(
                query=search_query.original,
                n_results=n_results,
                filter_dict=search_query.filters if search_query.filters else None,
                score_threshold=score_threshold,
            )
            logger.debug("Semantic search returned %d results", len(results))

            # 3. Adjust ranking (strategy-specific)
            ranked_results = self._strategy.adjust_ranking(results)

            # 4. Format output (strategy-specific)
            output = self._strategy.format_output(ranked_results, params)

            # Ensure standard fields
            if "total_results" not in output:
                output["total_results"] = len(ranked_results)

            return output

        except Exception as e:
            logger.error("Workflow search failed: %s", e)
            return {
                "error": str(e),
                "result_type": "error",
                "total_results": 0,
            }
