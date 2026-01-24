# src/knowledge_mcp/search/semantic_search.py
"""
Semantic search implementation combining embedder and vector store.

This module provides the SemanticSearcher class that orchestrates
text-to-results semantic search by:
1. Converting query text to embeddings
2. Searching the vector store for similar chunks
3. Returning formatted SearchResult objects

Example:
    >>> from knowledge_mcp.embed import OpenAIEmbedder
    >>> from knowledge_mcp.store import QdrantStore
    >>> from knowledge_mcp.search import SemanticSearcher
    >>>
    >>> embedder = OpenAIEmbedder(api_key="...")
    >>> store = QdrantStore(config)
    >>> searcher = SemanticSearcher(embedder, store)
    >>>
    >>> results = await searcher.search("system requirements review")
    >>> for r in results:
    ...     print(f"{r.score:.2f}: {r.document_title}")
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from knowledge_mcp.search.models import SearchResult

if TYPE_CHECKING:
    from knowledge_mcp.embed.base import BaseEmbedder
    from knowledge_mcp.store.base import BaseStore

logger = logging.getLogger(__name__)


class SemanticSearcher:
    """
    Semantic search combining embedder and vector store.

    Provides text-to-results search by:
    1. Converting query text to embedding
    2. Searching vector store for similar chunks
    3. Returning formatted results with metadata

    Attributes:
        embedder: Embedding provider for query vectorization.
        store: Vector store backend for similarity search.

    Example:
        >>> from knowledge_mcp.embed import OpenAIEmbedder
        >>> from knowledge_mcp.store import create_store
        >>>
        >>> embedder = OpenAIEmbedder(api_key="...")
        >>> store = create_store(config)
        >>> searcher = SemanticSearcher(embedder, store)
        >>>
        >>> results = await searcher.search("system requirements review")
        >>> for r in results:
        ...     print(f"{r.score:.2f}: {r.document_title} - {r.section_title}")
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        store: BaseStore,
    ) -> None:
        """
        Initialize semantic searcher.

        Args:
            embedder: Embedding provider (e.g., OpenAIEmbedder).
            store: Vector store implementing BaseStore (QdrantStore or ChromaDBStore).

        Example:
            >>> searcher = SemanticSearcher(
            ...     embedder=OpenAIEmbedder(api_key="..."),
            ...     store=QdrantStore(config),
            ... )
        """
        self._embedder: BaseEmbedder = embedder
        self._store: BaseStore = store

    async def search(
        self,
        query: str,
        n_results: int = 10,
        filter_dict: dict[str, Any] | None = None,
        score_threshold: float = 0.0,
    ) -> list[SearchResult]:
        """
        Search for relevant content by semantic similarity.

        Args:
            query: Natural language search query.
            n_results: Maximum number of results to return. Defaults to 10.
            filter_dict: Metadata filters to apply. Keys are field names.
                Supported fields: document_type, chunk_type, normative, clause_number.
                Example: {"document_type": "standard", "normative": True}
            score_threshold: Minimum similarity score (0-1). Defaults to 0.0.

        Returns:
            List of SearchResult objects ordered by relevance (highest first).
            Empty list if query is empty or no results found.

        Example:
            >>> # Basic search
            >>> results = await searcher.search("SRR requirements")
            >>>
            >>> # Filtered search
            >>> results = await searcher.search(
            ...     query="verification methods",
            ...     filter_dict={"document_type": "standard", "normative": True},
            ...     n_results=5,
            ... )
        """
        # Handle empty query gracefully (Success Criterion #4)
        if not query or not query.strip():
            return []

        try:
            # Generate query embedding
            query_embedding = await self._embedder.embed(query)

            # Search vector store
            raw_results: list[dict[str, Any]] = self._store.search(
                query_embedding=query_embedding,
                n_results=n_results,
                filter_dict=filter_dict,
                score_threshold=score_threshold,
            )

            # Transform to SearchResult objects
            return [self._to_search_result(r) for r in raw_results]

        except Exception as e:
            logger.error("Search failed for query '%s': %s", query[:50], e)
            # Return empty list for graceful degradation
            return []

    def _to_search_result(self, raw: dict[str, Any]) -> SearchResult:
        """
        Transform raw store result to SearchResult dataclass.

        Args:
            raw: Dictionary from vector store search results containing
                id, content, score, and metadata fields.

        Returns:
            SearchResult with flattened citation fields extracted from metadata.
        """
        metadata: dict[str, Any] = raw.get("metadata", {})

        # Extract section_hierarchy with type safety
        section_hierarchy_raw = metadata.get("section_hierarchy")
        section_hierarchy: list[str] = []
        if isinstance(section_hierarchy_raw, list):
            section_hierarchy = [str(item) for item in cast(list[Any], section_hierarchy_raw)]

        # Extract page_numbers with type safety
        page_numbers_raw = metadata.get("page_numbers")
        page_numbers: list[int] = []
        if isinstance(page_numbers_raw, list):
            page_numbers = [int(item) for item in cast(list[Any], page_numbers_raw)]

        return SearchResult(
            id=str(raw["id"]),
            content=str(raw["content"]),
            score=float(raw["score"]),
            metadata=metadata,
            # Flatten citation fields for easy access (FR-3.4)
            document_id=str(metadata.get("document_id", "")),
            document_title=str(metadata.get("document_title", "")),
            document_type=str(metadata.get("document_type", "")),
            section_title=str(metadata.get("section_title", "")),
            section_hierarchy=section_hierarchy,
            chunk_type=str(metadata.get("chunk_type", "")),
            normative=bool(metadata.get("normative", False)),
            clause_number=str(metadata["clause_number"]) if metadata.get("clause_number") else None,
            page_numbers=page_numbers,
        )
