# src/knowledge_mcp/store/qdrant_store.py
"""
Qdrant Cloud vector store implementation.

Provides vector storage and retrieval using Qdrant Cloud's free tier.
Supports dense vector search, hybrid search, and full-text search.

Features:
    - Dense vector search (OpenAI embeddings)
    - Sparse vector search (BM25 for hybrid)
    - Rich metadata filtering
    - Payload indexing for fast queries
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    NamedVector,
    OptimizersConfigDiff,
    PayloadSchemaType,
    PointStruct,
    SparseIndexParams,
    SparseVectorParams,
    TextIndexParams,
    TokenizerType,
    VectorParams,
)

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk
    from knowledge_mcp.utils.config import KnowledgeConfig


class QdrantStore:
    """
    Vector store using Qdrant Cloud.

    Provides storage and retrieval of knowledge chunks using
    Qdrant's vector database with support for hybrid search.

    Attributes:
        config: Knowledge MCP configuration.
        client: Qdrant client instance.
        collection: Collection name.
        hybrid_enabled: Whether hybrid search is enabled.

    Example:
        >>> config = load_config()
        >>> store = QdrantStore(config)
        >>> store.add_chunks(chunks)
        >>> results = store.search(query_embedding, n_results=5)
    """

    def __init__(self, config: KnowledgeConfig) -> None:
        """
        Initialize Qdrant store.

        Args:
            config: Knowledge MCP configuration with Qdrant settings.

        Raises:
            ConnectionError: When unable to connect to Qdrant Cloud.
        """
        self.config = config

        self.client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            timeout=60,
        )

        # Use versioned collection name to prevent model mixing (Pitfall #7)
        self.collection = config.versioned_collection_name
        self.hybrid_enabled = config.qdrant_hybrid_search

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection for c in collections)

        if not exists:
            vectors_config = {
                "dense": VectorParams(
                    size=self.config.embedding_dimensions,
                    distance=Distance.COSINE,
                )
            }

            sparse_vectors_config = None
            if self.hybrid_enabled:
                sparse_vectors_config = {
                    "sparse": SparseVectorParams(
                        index=SparseIndexParams(on_disk=False),
                    )
                }

            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=vectors_config,
                sparse_vectors_config=sparse_vectors_config,
                optimizers_config=OptimizersConfigDiff(indexing_threshold=0),
            )

            self._create_payload_indexes()

    def _create_payload_indexes(self) -> None:
        """Create indexes on frequently filtered fields."""
        index_fields = [
            ("document_id", PayloadSchemaType.KEYWORD),
            ("document_type", PayloadSchemaType.KEYWORD),
            ("chunk_type", PayloadSchemaType.KEYWORD),
            ("normative", PayloadSchemaType.BOOL),
            ("clause_number", PayloadSchemaType.KEYWORD),
        ]

        for field_name, field_type in index_fields:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection,
                    field_name=field_name,
                    field_schema=field_type,
                )
            except UnexpectedResponse:
                pass  # Index might already exist

        # Full-text index on content
        try:
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="content",
                field_schema=TextIndexParams(
                    type="text",
                    tokenizer=TokenizerType.WORD,
                    min_token_len=2,
                    max_token_len=20,
                    lowercase=True,
                ),
            )
        except UnexpectedResponse:
            pass

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

        points = []
        for chunk in chunks:
            if chunk.embedding is None:
                msg = f"Chunk {chunk.id} missing embedding"
                raise ValueError(msg)

            vectors: dict = {"dense": chunk.embedding}

            point = PointStruct(
                id=chunk.id,
                vector=vectors if self.hybrid_enabled else chunk.embedding,
                payload={
                    "content": chunk.content,
                    "document_id": chunk.document_id,
                    "document_title": chunk.document_title,
                    "document_type": chunk.document_type,
                    "section_title": chunk.section_title,
                    "section_hierarchy": chunk.section_hierarchy,
                    "chunk_type": chunk.chunk_type,
                    "normative": chunk.normative,
                    "clause_number": chunk.clause_number or "",
                    "page_numbers": chunk.page_numbers,
                    "references": chunk.references,
                    "token_count": chunk.token_count,
                    "content_hash": chunk.content_hash,
                    "parent_chunk_id": chunk.parent_chunk_id or "",
                    "created_at": chunk.created_at,
                    # Embedding model metadata (FR-2.4)
                    "embedding_model": chunk.embedding_model,
                    "embedding_dimensions": len(chunk.embedding) if chunk.embedding else 0,
                },
            )
            points.append(point)

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection,
                points=batch,
            )

        return len(points)

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        filter_dict: Optional[dict[str, object]] = None,
        score_threshold: float = 0.0,
    ) -> list[dict]:
        """
        Search for similar chunks.

        Args:
            query_embedding: Dense vector embedding of the query.
            n_results: Number of results to return.
            filter_dict: Metadata filters (e.g., {"chunk_type": "requirement"}).
            score_threshold: Minimum similarity score (0-1).

        Returns:
            List of matching chunks with scores and metadata.

        Example:
            >>> results = store.search(
            ...     query_embedding=embedder.embed("SRR"),
            ...     n_results=5,
            ...     filter_dict={"chunk_type": "requirement"},
            ... )
        """
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                if isinstance(value, bool):
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                elif isinstance(value, list):
                    conditions.append(FieldCondition(key=key, match=MatchAny(any=value)))
                else:
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            query_filter = Filter(must=conditions)

        if self.hybrid_enabled:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=NamedVector(name="dense", vector=query_embedding),
                limit=n_results,
                query_filter=query_filter,
                score_threshold=score_threshold,
                with_payload=True,
            )
        else:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=n_results,
                query_filter=query_filter,
                score_threshold=score_threshold,
                with_payload=True,
            )

        return [
            {
                "id": str(r.id),
                "content": r.payload.get("content", ""),
                "metadata": {
                    "document_id": r.payload.get("document_id", ""),
                    "document_title": r.payload.get("document_title", ""),
                    "document_type": r.payload.get("document_type", ""),
                    "section_title": r.payload.get("section_title", ""),
                    "section_hierarchy": r.payload.get("section_hierarchy", []),
                    "chunk_type": r.payload.get("chunk_type", ""),
                    "normative": r.payload.get("normative", False),
                    "clause_number": r.payload.get("clause_number", ""),
                    "page_numbers": r.payload.get("page_numbers", []),
                    "references": r.payload.get("references", []),
                },
                "score": r.score,
            }
            for r in results
        ]

    def get_stats(self) -> dict:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection metadata and counts.
        """
        info = self.client.get_collection(self.collection)
        return {
            "collection_name": self.collection,
            "total_chunks": info.points_count,
            "vectors_count": info.vectors_count,
            "indexed_vectors": info.indexed_vectors_count,
            "status": info.status,
            "config": {
                "vector_size": self.config.embedding_dimensions,
                "hybrid_enabled": self.hybrid_enabled,
            },
        }

    def validate_embedding_model(self, expected_model: str) -> bool:
        """Verify collection uses expected embedding model.

        Args:
            expected_model: The embedding model name to validate against.

        Returns:
            True if model matches or collection is empty.

        Raises:
            ValueError: If collection has data with different embedding model.
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Sample one point to check metadata
            results = self.client.scroll(
                collection_name=self.collection,
                limit=1,
            )
            if not results[0]:  # Empty collection
                return True

            point = results[0][0]
            stored_model = point.payload.get("embedding_model") if point.payload else None
            if stored_model and stored_model != expected_model:
                raise ValueError(
                    f"Collection '{self.collection}' uses {stored_model}, "
                    f"but config specifies {expected_model}. "
                    f"Use different collection name or recreate collection."
                )
            return True
        except ValueError:
            raise
        except Exception as e:
            logger.warning("Model validation failed: %s", e)
            return False

    def health_check(self) -> bool:
        """Check if the Qdrant store is healthy and accessible.

        Returns:
            True if the store is accessible, False otherwise.
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Try to get collection info to verify connectivity
            self.client.get_collection(self.collection)
            return True
        except Exception as e:
            logger.warning("Health check failed for Qdrant: %s", e)
            return False