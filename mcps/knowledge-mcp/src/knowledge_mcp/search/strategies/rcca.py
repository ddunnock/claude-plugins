"""RCCA (Root Cause Corrective Action) search strategy.

Provides specialized retrieval for failure analysis workflows. Boosts
keywords related to symptoms, failures, root causes, and resolutions.

Example:
    >>> from knowledge_mcp.search.strategies.rcca import RCCAStrategy
    >>> from knowledge_mcp.search import SemanticSearcher
    >>> from knowledge_mcp.search.workflow_search import WorkflowSearcher
    >>>
    >>> strategy = RCCAStrategy()
    >>> workflow = WorkflowSearcher(semantic_searcher, strategy)
    >>> results = await workflow.search("power supply failure")
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from knowledge_mcp.search.strategies.base import SearchQuery, SearchStrategy

if TYPE_CHECKING:
    from knowledge_mcp.search.models import SearchResult


class RCCAStrategy(SearchStrategy):
    """Strategy for RCCA (Root Cause Corrective Action) workflow.

    Specializes search for failure analysis by:
    1. Expanding queries with failure-related terminology
    2. Boosting results containing symptoms, causes, and resolutions
    3. Extracting structured RCCA metadata from results

    RCCA-specific keywords include:
    - Symptoms: failure, error, symptom, anomaly, malfunction
    - Root causes: root cause, underlying cause, contributing factor
    - Analysis: investigation, diagnosis, analysis
    - Resolution: corrective action, mitigation, resolution, fix

    Example:
        >>> strategy = RCCAStrategy()
        >>> query = await strategy.preprocess_query(
        ...     "intermittent reboot",
        ...     {}
        ... )
        >>> print(query.expanded_terms)
        ['failure', 'symptom', 'root cause', 'resolution']
    """

    # RCCA-related keywords for query expansion
    SYMPTOM_KEYWORDS = [
        "failure",
        "error",
        "symptom",
        "anomaly",
        "malfunction",
        "issue",
        "problem",
    ]

    CAUSE_KEYWORDS = [
        "root cause",
        "underlying cause",
        "contributing factor",
        "causal factor",
    ]

    ANALYSIS_KEYWORDS = [
        "investigation",
        "diagnosis",
        "analysis",
        "troubleshooting",
    ]

    RESOLUTION_KEYWORDS = [
        "corrective action",
        "mitigation",
        "resolution",
        "fix",
        "remedy",
        "workaround",
    ]

    async def preprocess_query(
        self,
        query: str,
        params: dict[str, Any],
    ) -> SearchQuery:
        """Expand query with RCCA-specific terminology.

        Args:
            query: Original user query (e.g., "power supply failure").
            params: Optional parameters (currently unused).

        Returns:
            SearchQuery with expanded RCCA-related terms.

        Example:
            >>> query = await strategy.preprocess_query("reboot issue", {})
            >>> len(query.expanded_terms) > 0
            True
        """
        # Add RCCA domain terms to broaden search
        expanded_terms = [
            "failure",
            "symptom",
            "root cause",
            "corrective action",
            "resolution",
        ]

        return SearchQuery(
            original=query,
            expanded_terms=expanded_terms,
            filters={},
            facets=["symptoms", "causes", "resolutions"],
        )

    def adjust_ranking(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """Boost results containing RCCA-specific content.

        Applies score multipliers based on presence of:
        - Multiple RCCA keywords (10% boost)
        - Explicit root cause language (15% boost)
        - Resolution/corrective action content (10% boost)

        Args:
            results: Raw semantic search results.

        Returns:
            Reranked results with RCCA relevance boosts applied.

        Example:
            >>> results = strategy.adjust_ranking(search_results)
            >>> # Results with "root cause" will rank higher
        """
        for result in results:
            content_lower = result.content.lower()
            boost = 1.0

            # Count RCCA keyword categories present
            has_symptom = any(kw in content_lower for kw in self.SYMPTOM_KEYWORDS)
            has_cause = any(kw in content_lower for kw in self.CAUSE_KEYWORDS)
            has_resolution = any(kw in content_lower for kw in self.RESOLUTION_KEYWORDS)

            # Boost if multiple RCCA aspects present
            rcca_aspects = sum([has_symptom, has_cause, has_resolution])
            if rcca_aspects >= 2:
                boost *= 1.10

            # Extra boost for explicit root cause language
            if has_cause:
                boost *= 1.15

            # Boost for resolution/corrective action content
            if has_resolution:
                boost *= 1.10

            # Apply boost while keeping score in 0-1 range
            result.score = min(1.0, result.score * boost)

        # Re-sort by adjusted scores
        return sorted(results, key=lambda r: r.score, reverse=True)

    def format_output(
        self,
        results: list[SearchResult],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Format results with extracted RCCA metadata.

        Extracts structured fields from result content:
        - symptoms: Observable behaviors, error messages
        - root_cause: Underlying cause if mentioned
        - contributing_factors: Secondary causes
        - resolution: How issue was resolved

        Args:
            results: Ranked search results.
            params: Original tool parameters (unused).

        Returns:
            Dict with 'result_type': 'rcca_analysis' and structured results.

        Example:
            >>> output = strategy.format_output(results, {})
            >>> output['result_type']
            'rcca_analysis'
            >>> 'results' in output
            True
        """
        formatted_results: list[dict[str, Any]] = []

        for result in results:
            # Extract RCCA-specific metadata
            rcca_data = self._extract_rcca_metadata(result)

            formatted_results.append({
                "id": result.id,
                "content": result.content,
                "score": round(result.score, 3),
                "document_title": result.document_title,
                "section_title": result.section_title,
                "rcca_metadata": rcca_data,
            })

        return {
            "result_type": "rcca_analysis",
            "total_results": len(formatted_results),
            "results": formatted_results,
        }

    def _extract_rcca_metadata(self, result: SearchResult) -> dict[str, Any]:
        """Extract RCCA-specific fields from result content.

        Attempts to identify and extract:
        - symptoms: Sentences with symptom keywords
        - root_cause: Sentences with cause keywords
        - contributing_factors: Additional causal mentions
        - resolution: Sentences with resolution keywords

        Args:
            result: Search result to analyze.

        Returns:
            Dict with extracted RCCA fields (may be empty strings if not found).
        """
        content = result.content
        symptoms: list[str] = []
        contributing_factors: list[str] = []
        metadata: dict[str, Any] = {
            "symptoms": symptoms,
            "root_cause": "",
            "contributing_factors": contributing_factors,
            "resolution": "",
        }

        # Split content into sentences for extraction
        sentences = self._split_sentences(content)

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Extract symptoms
            if any(kw in sentence_lower for kw in self.SYMPTOM_KEYWORDS):
                if sentence not in metadata["symptoms"]:
                    metadata["symptoms"].append(sentence.strip())

            # Extract root cause (take first match)
            if not metadata["root_cause"]:
                if any(kw in sentence_lower for kw in self.CAUSE_KEYWORDS):
                    metadata["root_cause"] = sentence.strip()
                elif "contributing" in sentence_lower:
                    # Contributing factors if no root cause yet
                    if sentence.strip() not in metadata["contributing_factors"]:
                        metadata["contributing_factors"].append(sentence.strip())

            # Extract resolution (take first match)
            if not metadata["resolution"]:
                if any(kw in sentence_lower for kw in self.RESOLUTION_KEYWORDS):
                    metadata["resolution"] = sentence.strip()

        # Limit symptoms and factors to top 3 to avoid overwhelming output
        metadata["symptoms"] = metadata["symptoms"][:3]
        metadata["contributing_factors"] = metadata["contributing_factors"][:3]

        return metadata

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences.

        Simple sentence splitter using periods, question marks, and exclamation
        points. Does not handle abbreviations perfectly but sufficient for
        extracting RCCA content.

        Args:
            text: Text to split.

        Returns:
            List of sentences.
        """
        # Split on period, question mark, or exclamation followed by space/newline
        sentences = re.split(r'[.!?]+\s+', text)
        return [s for s in sentences if s.strip()]
