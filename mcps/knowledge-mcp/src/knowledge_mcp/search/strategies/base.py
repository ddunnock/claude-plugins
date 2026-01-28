"""Base classes for workflow search strategies.

Defines the SearchStrategy abstract base class and SearchQuery dataclass
used by all workflow-specific search implementations.

The strategy pattern allows customizing:
1. Query preprocessing (expansion, faceting)
2. Ranking adjustments (boost domain-specific fields)
3. Output formatting (structured metadata)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from knowledge_mcp.search.models import SearchResult


@dataclass
class SearchQuery:
    """Internal representation of a processed query.

    Holds the original query along with any expansions, filters,
    and facets added by strategy preprocessing.

    Attributes:
        original: The original query string from the user.
        expanded_terms: Additional query terms for broader search.
        filters: Metadata filters to apply (e.g., document_type).
        facets: Named facets for multi-aspect search (e.g., "definitions").
    """

    original: str
    expanded_terms: list[str] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    facets: list[str] = field(default_factory=list)


class SearchStrategy(ABC):
    """Abstract base class for workflow-specific search strategies.

    Strategies customize three phases of the search process:
    1. Query preprocessing - expand terms, add filters, define facets
    2. Ranking adjustments - boost results matching domain criteria
    3. Output formatting - structure results for specific workflow needs

    Subclasses must implement all three abstract methods.

    Example:
        >>> class MyStrategy(SearchStrategy):
        ...     async def preprocess_query(self, query, params):
        ...         return SearchQuery(original=query)
        ...
        ...     def adjust_ranking(self, results):
        ...         return results
        ...
        ...     def format_output(self, results, params):
        ...         return {"results": [r.content for r in results]}
    """

    @abstractmethod
    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any],
    ) -> SearchQuery:
        """Transform user query into internal search representation.

        Args:
            query: Natural language query from user.
            params: Tool-specific parameters (filters, options, alternatives).

        Returns:
            SearchQuery with expanded terms, filters, and facets.

        Note:
            This method is async to allow for LLM-based query expansion
            in future implementations.
        """
        pass

    @abstractmethod
    def adjust_ranking(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """Apply strategy-specific ranking adjustments.

        Args:
            results: Raw semantic search results from SemanticSearcher.

        Returns:
            Reranked results with strategy-specific score adjustments.

        Note:
            Implementations should modify result.score and re-sort.
            Scores should remain in 0-1 range.
        """
        pass

    @abstractmethod
    def format_output(
        self,
        results: list[SearchResult],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Structure output according to strategy requirements.

        Args:
            results: Ranked search results.
            params: Original tool parameters (for context like alternatives list).

        Returns:
            Formatted dict suitable for MCP tool response.

        Note:
            Output must be JSON-serializable. Include result_type field
            to identify the workflow (e.g., "rcca_analysis", "trade_study").
        """
        pass
