# src/knowledge_mcp/store/chromadb_store.py
"""
ChromaDB local vector store implementation.

Provides a local fallback vector store using ChromaDB when
Qdrant Cloud is unavailable. Supports the same interface as QdrantStore.

Features:
    - Local persistent storage
    - Dense vector search
    - Metadata filtering
    - Automatic fallback support
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk
    from knowledge_mcp.utils.config import KnowledgeConfig

logger = logging.getLogger(__name__)


class ChromaDBStore:
    """
    Vector store using local ChromaDB.

    Provides local storage and retrieval of knowledge chunks using
    ChromaDB's persistent client as a fallback when Qdrant is unavailable.

    Attributes:
        config: Knowledge MCP configuration.
        client: ChromaDB PersistentClient instance.
        collection: ChromaDB collection.

    Example:
        >>> config = load_config()
        >>> store = ChromaDBStore(config)
        >>> store.add_chunks(chunks)
        >>> results = store.search(query_embedding, n_results=5)
    """

    def __init__(self, config: KnowledgeConfig) -> None:
        """
        Initialize ChromaDB store.

        Args:
            config: Knowledge MCP configuration with ChromaDB settings.

        Raises:
            ImportError: When chromadb is not installed.
            ConnectionError: When unable to initialize ChromaDB.
        """
        try:
            import chromadb
        except ImportError as e:
            raise ImportError(
                "chromadb is required for local fallback. "
                "Install with: poetry install --with chromadb"
            ) from e

        self.config = config

        # Ensure path exists
        config.chromadb_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(config.chromadb_path))

        # Use versioned collection name for consistency with Qdrant
        collection_name = config.versioned_chromadb_collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._collection_name = collection_name

    def add_chunks(self, chunks: list[KnowledgeChunk]) -> int:
        """
        Add chunks to the collection.

        Args:
            chunks: List of KnowledgeChunk objects with embeddings.

        Returns:
            Number of chunks successfully added.

        Raises:
            ValueError: When chunks list is empty or missing embeddings.
        """
        if not chunks:
            return 0

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            if chunk.embedding is None:
                msg = f"Chunk {chunk.id} missing embedding"
                raise ValueError(msg)

            ids.append(chunk.id)
            embeddings.append(chunk.embedding)
            documents.append(chunk.content)
            metadatas.append({
                "document_id": chunk.document_id,
                "document_title": chunk.document_title,
                "document_type": chunk.document_type,
                "section_title": chunk.section_title,
                "chunk_type": chunk.chunk_type,
                "normative": chunk.normative,
                "clause_number": chunk.clause_number or "",
                "token_count": chunk.token_count,
                "content_hash": chunk.content_hash,
                "embedding_model": chunk.embedding_model,
                "embedding_dimensions": len(chunk.embedding),
                "created_at": chunk.created_at,
            })

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        return len(ids)

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        filter_dict: Optional[dict[str, Any]] = None,
        score_threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Search for similar chunks.

        Args:
            query_embedding: Dense vector embedding of the query.
            n_results: Number of results to return.
            filter_dict: Metadata filters.
            score_threshold: Minimum similarity score (0-1).

        Returns:
            List of matching chunks with scores and metadata.
        """
        where_filter = None
        if filter_dict:
            # ChromaDB uses $eq for equality
            where_filter = {
                "$and": [
                    {key: {"$eq": value}}
                    for key, value in filter_dict.items()
                ]
            }

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                # ChromaDB returns distance, convert to similarity score
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 - distance  # Cosine distance to similarity

                if score < score_threshold:
                    continue

                formatted_results.append({
                    "id": chunk_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": score,
                })

        return formatted_results

    def get_stats(self) -> dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection metadata and counts.
        """
        return {
            "collection_name": self._collection_name,
            "total_chunks": self.collection.count(),
            "vectors_count": self.collection.count(),
            "indexed_vectors": self.collection.count(),
            "status": "active",
            "config": {
                "vector_size": self.config.embedding_dimensions,
                "hybrid_enabled": False,
                "backend": "chromadb",
            },
        }

    def health_check(self) -> bool:
        """Check if the ChromaDB store is healthy and accessible.

        Returns:
            True if the store is accessible, False otherwise.
        """
        try:
            # Try to count items to verify collection is accessible
            self.collection.count()
            return True
        except Exception as e:
            logger.warning("Health check failed for ChromaDB: %s", e)
            return False

    def validate_embedding_model(self, expected_model: str) -> bool:
        """Verify collection uses expected embedding model.

        Args:
            expected_model: The embedding model name to validate against.

        Returns:
            True if model matches or collection is empty.

        Raises:
            ValueError: If collection has data with different embedding model.
        """
        try:
            # Sample one item to check metadata
            results = self.collection.peek(limit=1)
            if not results["ids"]:  # Empty collection
                return True

            metadatas = results.get("metadatas", [])
            if metadatas and metadatas[0]:
                stored_model = metadatas[0].get("embedding_model")
                if stored_model and stored_model != expected_model:
                    raise ValueError(
                        f"Collection '{self._collection_name}' uses {stored_model}, "
                        f"but config specifies {expected_model}. "
                        f"Use different collection name or recreate collection."
                    )
            return True
        except ValueError:
            raise
        except Exception as e:
            logger.warning("Model validation failed: %s", e)
            return False
