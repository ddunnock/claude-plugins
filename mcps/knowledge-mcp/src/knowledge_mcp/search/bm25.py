# src/knowledge_mcp/search/bm25.py
"""
BM25S-based lexical search implementation.

This module provides the BM25Searcher class for keyword-based retrieval
using the BM25S algorithm. It complements semantic search by finding
documents with exact keyword matches.

Example:
    >>> from knowledge_mcp.search import BM25Searcher
    >>>
    >>> searcher = BM25Searcher()
    >>> documents = [
    ...     {"id": "doc1", "content": "System requirements review"},
    ...     {"id": "doc2", "content": "Software verification methods"},
    ... ]
    >>> searcher.build_index(documents)
    >>>
    >>> results = searcher.search("requirements", n_results=5)
    >>> for r in results:
    ...     print(f"{r['score']:.2f}: {r['content']}")
"""

from __future__ import annotations

import logging
from typing import Any

import bm25s  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class BM25Searcher:
    """
    BM25S-based lexical search for keyword matching.

    Provides fast keyword-based retrieval to complement semantic search.
    Uses simple whitespace tokenization with lowercasing (per 03-RESEARCH.md).

    Attributes:
        is_indexed: Whether the index has been built.
        document_count: Number of indexed documents.

    Example:
        >>> searcher = BM25Searcher()
        >>> documents = [
        ...     {"id": "ieee-15288-1", "content": "The SRR shall verify requirements"},
        ...     {"id": "ieee-15288-2", "content": "Verification methods include test"},
        ... ]
        >>> searcher.build_index(documents)
        >>> results = searcher.search("verification requirements")
        >>> print(f"Found {len(results)} results")
    """

    def __init__(self) -> None:
        """
        Initialize BM25 searcher with empty index.

        The index must be built using build_index() before searching.
        """
        self._index: bm25s.BM25 | None = None
        self._doc_ids: list[str] = []
        self._doc_contents: list[str] = []

    def build_index(self, documents: list[dict[str, Any]]) -> None:
        """
        Build BM25 index from document corpus.

        Args:
            documents: List of dicts with 'id' and 'content' fields.
                Each document must have both fields.

        Raises:
            ValueError: If documents list is empty or missing required fields.

        Example:
            >>> documents = [
            ...     {"id": "doc1", "content": "System requirements review"},
            ...     {"id": "doc2", "content": "Software verification"},
            ... ]
            >>> searcher.build_index(documents)
            >>> assert searcher.is_indexed
        """
        if not documents:
            msg = "Cannot build index from empty document list"
            raise ValueError(msg)

        # Validate required fields
        for i, doc in enumerate(documents):
            if "id" not in doc or "content" not in doc:
                msg = f"Document at index {i} missing 'id' or 'content' field"
                raise ValueError(msg)

        # Extract IDs and content
        self._doc_ids = [str(doc["id"]) for doc in documents]
        self._doc_contents = [str(doc["content"]) for doc in documents]

        # Tokenize using simple whitespace split + lowercase (per research)
        corpus_tokens = [content.lower().split() for content in self._doc_contents]

        # Build BM25 index
        self._index = bm25s.BM25()
        self._index.index(corpus_tokens)  # type: ignore[reportUnknownMemberType]

        logger.info("BM25 index built with %d documents", len(documents))

    def search(self, query: str, n_results: int = 10) -> list[dict[str, Any]]:
        """
        Search for documents matching query keywords.

        Args:
            query: Search query text. Tokenized using whitespace split + lowercase.
            n_results: Maximum number of results to return. Defaults to 10.

        Returns:
            List of result dicts ordered by BM25 score (highest first).
            Each dict contains: id, content, score.
            Returns empty list if query is empty or index not built.

        Example:
            >>> results = searcher.search("system requirements", n_results=5)
            >>> for r in results:
            ...     print(f"{r['id']}: {r['score']:.3f}")
        """
        # Handle empty query gracefully
        if not query or not query.strip():
            return []

        # Check if index is built
        if not self.is_indexed:
            logger.warning("BM25 search called before index built, returning empty results")
            return []

        # Tokenize query
        query_tokens = query.lower().split()

        # Retrieve top-k results
        # bm25s.retrieve expects a list of tokenized queries (batch)
        # Returns (scores, indices) as numpy arrays with shape (batch_size, k)
        assert self._index is not None  # Already checked via is_indexed
        scores, indices = self._index.retrieve([query_tokens], k=n_results)

        # Convert to result dicts
        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            # Convert numpy types to Python types
            score_float = float(score)

            # Skip if score is 0 (no match)
            if score_float == 0:
                continue

            idx_int = int(idx)
            results.append({
                "id": self._doc_ids[idx_int],
                "content": self._doc_contents[idx_int],
                "score": score_float,
            })

        # Sort by score descending (bm25s returns sorted by index, not score)
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    @property
    def is_indexed(self) -> bool:
        """
        Check if index has been built.

        Returns:
            True if build_index() has been called, False otherwise.
        """
        return self._index is not None

    @property
    def document_count(self) -> int:
        """
        Get number of indexed documents.

        Returns:
            Number of documents in the index. 0 if not built.
        """
        return len(self._doc_ids)
