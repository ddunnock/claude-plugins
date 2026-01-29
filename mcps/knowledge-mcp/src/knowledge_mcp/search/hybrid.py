# src/knowledge_mcp/search/hybrid.py
"""
Hybrid search combining semantic and BM25 retrieval with RRF fusion.

This module provides hybrid retrieval (FR-3.2) by merging results from
semantic search and BM25 lexical search using Reciprocal Rank Fusion (RRF).

Example:
    >>> from knowledge_mcp.search import HybridSearcher, SemanticSearcher, BM25Searcher
    >>> from knowledge_mcp.embed import OpenAIEmbedder
    >>> from knowledge_mcp.store import QdrantStore
    >>>
    >>> embedder = OpenAIEmbedder(api_key="...")
    >>> store = QdrantStore(config)
    >>> semantic = SemanticSearcher(embedder, store)
    >>> bm25 = BM25Searcher()
    >>> bm25.build_index(documents)
    >>>
    >>> hybrid = HybridSearcher(semantic, bm25)
    >>> results = await hybrid.search("system requirements", n_results=5)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any

from knowledge_mcp.search.models import SearchResult

if TYPE_CHECKING:
    from knowledge_mcp.search.bm25 import BM25Searcher
    from knowledge_mcp.search.semantic_search import SemanticSearcher

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    results_list: list[list[dict[str, Any]]],
    k: int = 60,
) -> list[dict[str, Any]]:
    """
    Merge multiple ranked result lists using Reciprocal Rank Fusion.

    RRF is a simple and effective method for combining results from different
    retrieval systems. It uses the formula: score = 1 / (k + rank) for each
    result in each list, then sums scores across lists.

    Args:
        results_list: List of ranked result lists from different retrievers.
            Each result dict must have an 'id' field for deduplication.
        k: Constant for RRF formula. Default 60 is standard (per research).
            Higher k gives more weight to lower-ranked results.

    Returns:
        Merged results sorted by fused RRF score descending.
        Each result has 'rrf_score' field added.

    Example:
        >>> semantic_results = [{"id": "doc1", "score": 0.9}, {"id": "doc2", "score": 0.7}]
        >>> bm25_results = [{"id": "doc2", "score": 5.0}, {"id": "doc3", "score": 3.0}]
        >>> merged = reciprocal_rank_fusion([semantic_results, bm25_results], k=60)
        >>> # doc2 appears in both lists so gets highest RRF score
        >>> assert merged[0]["id"] == "doc2"
    """
    # Score each document by summing RRF scores across all result lists
    fused_scores: dict[str, float] = defaultdict(float)
    doc_map: dict[str, dict[str, Any]] = {}

    for results in results_list:
        for rank, doc in enumerate(results, start=1):
            doc_id = str(doc["id"])
            # RRF formula: 1 / (k + rank)
            fused_scores[doc_id] += 1.0 / (k + rank)
            # Store document (last occurrence wins for metadata)
            doc_map[doc_id] = doc

    # Sort by fused score descending
    sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

    # Return merged results with RRF scores
    return [
        {**doc_map[doc_id], "rrf_score": fused_scores[doc_id]}
        for doc_id in sorted_ids
    ]


class HybridSearcher:
    """
    Hybrid search combining semantic and BM25 retrieval via RRF fusion.

    Implements FR-3.2 hybrid retrieval by:
    1. Running semantic search (embedding similarity)
    2. Running BM25 search (keyword matching)
    3. Merging results with Reciprocal Rank Fusion (k=60)
    4. Converting to SearchResult objects

    Falls back gracefully to semantic-only search if BM25 index not built.

    Attributes:
        semantic_searcher: SemanticSearcher instance for vector search.
        bm25_searcher: BM25Searcher instance for keyword search.

    Example:
        >>> hybrid = HybridSearcher(semantic_searcher, bm25_searcher)
        >>> results = await hybrid.search("traceability matrix", n_results=5)
        >>> for r in results:
        ...     print(f"{r.score:.2f}: {r.document_title}")
    """

    def __init__(
        self,
        semantic_searcher: SemanticSearcher,
        bm25_searcher: BM25Searcher,
    ) -> None:
        """
        Initialize hybrid searcher.

        Args:
            semantic_searcher: SemanticSearcher for vector-based retrieval.
            bm25_searcher: BM25Searcher for keyword-based retrieval.

        Example:
            >>> from knowledge_mcp.search import SemanticSearcher, BM25Searcher
            >>> hybrid = HybridSearcher(
            ...     semantic_searcher=SemanticSearcher(embedder, store),
            ...     bm25_searcher=BM25Searcher(),
            ... )
        """
        self._semantic = semantic_searcher
        self._bm25 = bm25_searcher

    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """
        Perform hybrid search combining semantic and BM25 results.

        Retrieves 2x n_results from each searcher, merges via RRF, and returns
        top n_results. If BM25 index not built, falls back to semantic only.

        Args:
            query: Natural language search query.
            n_results: Number of results to return. Defaults to 10.
            filter_dict: Metadata filters to apply to semantic search.
                Not applied to BM25 search (keyword-only matching).

        Returns:
            List of SearchResult objects ordered by RRF score (highest first).
            Empty list if query is empty or no results found.

        Example:
            >>> results = await hybrid.search(
            ...     query="system requirements review",
            ...     n_results=5,
            ...     filter_dict={"document_type": "standard"},
            ... )
            >>> print(f"Found {len(results)} results")
        """
        # Handle empty query gracefully
        if not query or not query.strip():
            return []

        # Check if BM25 index is built
        if not self._bm25.is_indexed:
            logger.warning(
                "BM25 index not built, falling back to semantic search only. "
                "Build BM25 index for hybrid retrieval improvements."
            )
            return await self._semantic.search(
                query=query,
                n_results=n_results,
                filter_dict=filter_dict,
            )

        # Run both searches with 2x n_results for better fusion
        retrieval_count = n_results * 2

        # Semantic search (async)
        semantic_results = await self._semantic.search(
            query=query,
            n_results=retrieval_count,
            filter_dict=filter_dict,
        )

        # BM25 search (sync)
        bm25_results = self._bm25.search(query, n_results=retrieval_count)

        # Convert SearchResult objects to dicts for RRF
        semantic_dicts = [
            {
                "id": r.id,
                "content": r.content,
                "score": r.score,
                "metadata": r.metadata,
                "document_id": r.document_id,
                "document_title": r.document_title,
                "document_type": r.document_type,
                "section_title": r.section_title,
                "section_hierarchy": r.section_hierarchy,
                "chunk_type": r.chunk_type,
                "normative": r.normative,
                "clause_number": r.clause_number,
                "page_numbers": r.page_numbers,
            }
            for r in semantic_results
        ]

        # Merge with RRF (k=60 per research)
        fused_results = reciprocal_rank_fusion(
            [semantic_dicts, bm25_results],
            k=60,
        )

        # Convert to SearchResult objects and return top n_results
        search_results = [self._to_search_result(r) for r in fused_results[:n_results]]

        logger.info(
            "Hybrid search completed: %d semantic + %d BM25 -> %d fused results",
            len(semantic_results),
            len(bm25_results),
            len(search_results),
        )

        return search_results

    def _to_search_result(self, result: dict[str, Any]) -> SearchResult:
        """
        Convert fused result dict to SearchResult object.

        Args:
            result: Result dict from RRF fusion with rrf_score.

        Returns:
            SearchResult with RRF score as main score.
        """
        return SearchResult(
            id=str(result["id"]),
            content=str(result.get("content", "")),
            score=float(result["rrf_score"]),  # Use RRF score as main score
            metadata=result.get("metadata", {}),
            document_id=str(result.get("document_id", "")),
            document_title=str(result.get("document_title", "")),
            document_type=str(result.get("document_type", "")),
            section_title=str(result.get("section_title", "")),
            section_hierarchy=result.get("section_hierarchy", []),
            chunk_type=str(result.get("chunk_type", "")),
            normative=bool(result.get("normative", False)),
            clause_number=result.get("clause_number"),
            page_numbers=result.get("page_numbers", []),
        )
