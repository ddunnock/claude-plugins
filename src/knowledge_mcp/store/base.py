# src/knowledge_mcp/store/base.py
"""
Abstract base class for vector store backends.

This module defines the interface that all vector store implementations
(Qdrant, ChromaDB, etc.) must follow, enabling backend switching.

Example:
    >>> class MyStore(BaseStore):
    ...     def add_chunks(self, chunks): ...
    ...     def search(self, query_embedding, ...): ...
    ...     def get_stats(self): ...
    ...     def health_check(self): ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk


class BaseStore(ABC):
    """
    Abstract base class for vector store implementations.

    All vector store backends (Qdrant, ChromaDB, etc.) must inherit
    from this class and implement all abstract methods.

    This enables the application to switch between backends without
    changing the search and ingestion code.

    Attributes:
        None defined at base level - implementations add their own.

    Example:
        >>> class QdrantStore(BaseStore):
        ...     def __init__(self, config):
        ...         self.client = QdrantClient(...)
        ...
        ...     def add_chunks(self, chunks):
        ...         # Implementation
        ...         pass
    """

    @abstractmethod
    def add_chunks(self, chunks: list[KnowledgeChunk]) -> int:
        """
        Add knowledge chunks to the vector store.

        Args:
            chunks: List of KnowledgeChunk objects to store.
                Each chunk must have a valid embedding.

        Returns:
            Number of chunks successfully added.

        Raises:
            ValueError: When chunks list is empty or contains
                chunks without embeddings.
            ConnectionError: When the vector store is unreachable.

        Example:
            >>> chunks = [KnowledgeChunk(...), KnowledgeChunk(...)]
            >>> added = store.add_chunks(chunks)
            >>> print(f"Added {added} chunks")
        """

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        filter_dict: dict[str, Any] | None = None,
        score_threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_embedding: Dense vector embedding of the query.
                Must match the dimensionality of stored embeddings.
            n_results: Maximum number of results to return.
                Defaults to 10.
            filter_dict: Optional metadata filters to apply.
                Keys are field names, values are match conditions.
                Example: {"chunk_type": "requirement", "normative": True}
            score_threshold: Minimum similarity score (0-1) for results.
                Results below this threshold are excluded.

        Returns:
            List of matching chunks as dictionaries with:
                - id: Chunk identifier
                - content: Text content
                - metadata: Metadata dictionary
                - score: Similarity score (0-1)

        Raises:
            ConnectionError: When the vector store is unreachable.
            ValueError: When query_embedding has wrong dimensions.

        Example:
            >>> results = store.search(
            ...     query_embedding=embedder.embed("SRR"),
            ...     n_results=5,
            ...     filter_dict={"normative": True},
            ... )
            >>> for r in results:
            ...     print(f"{r['score']:.2f}: {r['content'][:50]}...")
        """

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the vector store collection.

        Returns:
            Dictionary containing:
                - collection_name: Name of the collection
                - total_chunks: Total number of stored chunks
                - vectors_count: Number of vectors (may differ if batching)
                - config: Store configuration summary

        Raises:
            ConnectionError: When the vector store is unreachable.

        Example:
            >>> stats = store.get_stats()
            >>> print(f"Collection has {stats['total_chunks']} chunks")
        """

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the vector store is healthy and accessible.

        Performs a lightweight connectivity check to verify
        the store is reachable and responsive.

        Returns:
            True if the store is healthy, False otherwise.

        Example:
            >>> if not store.health_check():
            ...     raise RuntimeError("Vector store unavailable")
        """
