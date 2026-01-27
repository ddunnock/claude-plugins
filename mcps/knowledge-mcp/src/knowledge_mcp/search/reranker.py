# src/knowledge_mcp/search/reranker.py
"""Result reranking using Cohere API or local cross-encoder.

Provides relevance-based reranking to improve search result quality.
Uses Cohere Rerank API when available, falls back to local cross-encoder.

Example:
    >>> reranker = Reranker(provider="cohere", api_key="...")
    >>> reranked = await reranker.rerank(query, results, top_n=5)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import replace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from knowledge_mcp.search.models import SearchResult

logger = logging.getLogger(__name__)


class Reranker:
    """Rerank search results using Cohere or local cross-encoder.

    This class provides two reranking backends:
    - Cohere: Cloud-based reranking using Cohere's rerank-english-v3.0 model
    - Local: Local cross-encoder using sentence-transformers

    The reranker takes semantic search results and reorders them based on
    query-document relevance scores computed by the backend model.

    Example:
        >>> # Using Cohere (requires API key)
        >>> reranker = Reranker(provider="cohere", api_key="your-key")
        >>> reranked = await reranker.rerank("query", results, top_n=5)
        >>>
        >>> # Using local cross-encoder (no API key needed)
        >>> reranker = Reranker(provider="local")
        >>> reranked = await reranker.rerank("query", results)
    """

    def __init__(
        self,
        provider: str = "cohere",
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize reranker.

        Args:
            provider: Backend provider, either "cohere" or "local".
            api_key: Cohere API key (required if provider="cohere").
            model: Model name. Defaults to rerank-english-v3.0 for Cohere,
                   cross-encoder/ms-marco-MiniLM-L6-v2 for local.

        Raises:
            ValueError: When provider="cohere" but no api_key provided.
        """
        self._provider = provider
        self._client: Any = None
        self._model: Any = None
        self._model_name: str = ""

        if provider == "cohere":
            import cohere

            if not api_key:
                raise ValueError("api_key required for Cohere provider")
            self._client = cohere.ClientV2(api_key=api_key)
            self._model_name = model or "rerank-english-v3.0"
        else:  # local
            from sentence_transformers import CrossEncoder

            self._model_name = model or "cross-encoder/ms-marco-MiniLM-L6-v2"
            self._model = CrossEncoder(self._model_name)

    async def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_n: int | None = None,
    ) -> list[SearchResult]:
        """Rerank results by relevance.

        Takes a list of search results and reorders them based on
        query-document relevance scores computed by the backend model.

        Args:
            query: Search query to score documents against.
            results: Results from semantic search to rerank.
            top_n: Return only top N results after reranking.
                   If None, returns all results reranked.

        Returns:
            Reranked results with updated scores, sorted by relevance.
            Original SearchResult fields are preserved except for score.
        """
        if not results:
            return results

        if self._provider == "cohere":
            return await self._rerank_cohere(query, results, top_n)
        else:
            return await self._rerank_local(query, results, top_n)

    async def _rerank_cohere(
        self,
        query: str,
        results: list[SearchResult],
        top_n: int | None,
    ) -> list[SearchResult]:
        """Rerank using Cohere API.

        Args:
            query: Search query.
            results: Results to rerank.
            top_n: Number of results to return.

        Returns:
            Reranked results with Cohere relevance scores.
        """
        documents = [r.content for r in results]

        # Cohere client is sync, run in executor
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.rerank(
                model=self._model_name,
                query=query,
                documents=documents,
                top_n=top_n or len(documents),
            ),
        )

        # Map back to SearchResult objects with updated scores using dataclasses.replace
        reranked: list[SearchResult] = []
        for item in response.results:
            original = results[item.index]
            # Use dataclasses.replace for immutable update - only change score
            reranked.append(replace(original, score=item.relevance_score))

        return reranked

    async def _rerank_local(
        self,
        query: str,
        results: list[SearchResult],
        top_n: int | None,
    ) -> list[SearchResult]:
        """Rerank using local cross-encoder.

        Args:
            query: Search query.
            results: Results to rerank.
            top_n: Number of results to return.

        Returns:
            Reranked results with cross-encoder scores.
        """
        pairs = [(query, r.content) for r in results]

        # CrossEncoder.predict is sync, run in executor
        loop = asyncio.get_running_loop()
        scores = await loop.run_in_executor(
            None,
            self._model.predict,
            pairs,
        )

        # Create new results with updated scores using dataclasses.replace and sort
        scored_results = [
            replace(result, score=float(score)) for result, score in zip(results, scores)
        ]

        # Sort by score descending
        scored_results.sort(key=lambda r: r.score, reverse=True)

        if top_n:
            return scored_results[:top_n]
        return scored_results
