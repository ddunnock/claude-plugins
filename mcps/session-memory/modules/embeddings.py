"""Semantic search using OpenAI embeddings.

This module provides:
- Embedding generation using OpenAI's text-embedding-3-small model
- Cosine similarity search for finding related events
- Hybrid search combining embeddings with FTS5
"""

import hashlib
import json
import math
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Optional dependency
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class EmbeddingService:
    """Generate and search embeddings using OpenAI API."""

    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536

    def __init__(
        self,
        db_path: str,
        api_key: Optional[str] = None
    ):
        self.db_path = db_path
        self.available = OPENAI_AVAILABLE

        if self.available:
            key = api_key or os.environ.get("OPENAI_API_KEY")
            if key:
                self.client = openai.OpenAI(api_key=key)
            else:
                self.available = False
                self.client = None
        else:
            self.client = None

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not self.available:
            raise RuntimeError("OpenAI SDK not available or API key not set")

        if not texts:
            return []

        # OpenAI has a limit on batch size
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.MODEL,
                input=batch
            )
            all_embeddings.extend([d.embedding for d in response.data])

        return all_embeddings

    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def content_hash(self, content: str) -> str:
        """Generate a hash for deduplication."""
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def store_embedding(
        self,
        event_id: str,
        content: str,
        embedding: Optional[List[float]] = None
    ) -> str:
        """Store an embedding for an event."""
        conn = self._get_conn()
        try:
            content_hash = self.content_hash(content)

            # Check if already embedded
            existing = conn.execute(
                "SELECT id FROM embeddings WHERE event_id = ?",
                (event_id,)
            ).fetchone()

            if existing:
                return existing["id"]

            # Generate embedding if not provided
            if embedding is None:
                embedding = self.embed_single(content)

            embedding_id = f"emb-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

            conn.execute("""
                INSERT INTO embeddings
                (id, event_id, model, embedding, content_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                embedding_id,
                event_id,
                self.MODEL,
                json.dumps(embedding),
                content_hash,
                datetime.utcnow().isoformat() + "Z"
            ))

            conn.commit()
            return embedding_id
        finally:
            conn.close()

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        categories: Optional[List[str]] = None,
        top_k: int = 10,
        threshold: float = 0.7,
        hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar events using embeddings.

        Args:
            query: Natural language search query
            session_id: Limit to specific session (None for all)
            categories: Filter by event categories
            top_k: Number of results to return
            threshold: Minimum similarity score (0.0 to 1.0)
            hybrid: Combine with FTS5 results

        Returns:
            List of matching events with similarity scores
        """
        if not self.available:
            raise RuntimeError("Embedding search not available")

        # Generate query embedding
        query_embedding = self.embed_single(query)

        conn = self._get_conn()
        try:
            # Build query conditions
            conditions = []
            params: List[Any] = []

            if session_id:
                conditions.append("e.session_id = ?")
                params.append(session_id)

            if categories:
                placeholders = ",".join("?" * len(categories))
                conditions.append(f"e.category IN ({placeholders})")
                params.extend(categories)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Get all embeddings that match filters
            sql = f"""
                SELECT emb.event_id, emb.embedding, e.category, e.type, e.timestamp,
                       e.jsonl_offset, e.jsonl_length
                FROM embeddings emb
                JOIN events e ON emb.event_id = e.id
                WHERE {where_clause}
            """

            rows = conn.execute(sql, params).fetchall()

            # Calculate similarities
            results = []
            for row in rows:
                stored_embedding = json.loads(row["embedding"])
                similarity = self.cosine_similarity(query_embedding, stored_embedding)

                if similarity >= threshold:
                    results.append({
                        "event_id": row["event_id"],
                        "similarity": round(similarity, 4),
                        "category": row["category"],
                        "type": row["type"],
                        "timestamp": row["timestamp"],
                        "jsonl_offset": row["jsonl_offset"],
                        "jsonl_length": row["jsonl_length"]
                    })

            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)

            # Hybrid search: combine with FTS results
            if hybrid:
                results = self._hybrid_search(conn, query, results, where_clause, params, top_k)

            return results[:top_k]
        finally:
            conn.close()

    def _hybrid_search(
        self,
        conn: sqlite3.Connection,
        query: str,
        embedding_results: List[Dict],
        where_clause: str,
        params: List[Any],
        top_k: int
    ) -> List[Dict]:
        """Combine embedding results with FTS5 results."""
        try:
            # Get FTS results
            fts_sql = f"""
                SELECT e.id as event_id, e.category, e.type, e.timestamp,
                       e.jsonl_offset, e.jsonl_length
                FROM events e
                JOIN events_fts fts ON e.id = fts.id
                WHERE events_fts MATCH ? AND {where_clause}
                ORDER BY rank
                LIMIT ?
            """
            fts_rows = conn.execute(fts_sql, [query] + params + [top_k]).fetchall()

            # Merge results
            seen_ids = {r["event_id"] for r in embedding_results}
            fts_boost = 0.1  # Small boost for FTS matches

            for row in fts_rows:
                event_id = row["event_id"]
                if event_id in seen_ids:
                    # Boost existing result
                    for result in embedding_results:
                        if result["event_id"] == event_id:
                            result["similarity"] = min(1.0, result["similarity"] + fts_boost)
                            result["fts_match"] = True
                            break
                else:
                    # Add FTS-only result with lower base score
                    embedding_results.append({
                        "event_id": event_id,
                        "similarity": 0.5 + fts_boost,  # Base score for FTS match
                        "category": row["category"],
                        "type": row["type"],
                        "timestamp": row["timestamp"],
                        "jsonl_offset": row["jsonl_offset"],
                        "jsonl_length": row["jsonl_length"],
                        "fts_match": True,
                        "embedding_match": False
                    })
                    seen_ids.add(event_id)

            # Re-sort
            embedding_results.sort(key=lambda x: x["similarity"], reverse=True)

        except sqlite3.OperationalError:
            pass  # FTS not available

        return embedding_results

    def embed_event(
        self,
        event: Dict[str, Any],
        auto_categories: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Embed an event if it matches auto-embed criteria.

        Args:
            event: The event to potentially embed
            auto_categories: Categories to auto-embed (default: decision, finding, question)

        Returns:
            Embedding ID if created, None otherwise
        """
        if not self.available:
            return None

        auto_categories = auto_categories or ["decision", "finding", "question"]

        if event.get("category") not in auto_categories:
            return None

        # Build content from event data
        data = event.get("data", {})
        content_parts = []

        # Extract key fields
        for key in ["title", "description", "question", "rationale", "summary"]:
            if key in data:
                content_parts.append(str(data[key]))

        # Fallback to full data serialization
        if not content_parts:
            content_parts.append(json.dumps(data))

        content = " ".join(content_parts)

        if len(content) < 10:  # Skip very short content
            return None

        try:
            return self.store_embedding(event["id"], content)
        except Exception:
            return None

    def get_similar_events(
        self,
        event_id: str,
        top_k: int = 5,
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Find events similar to a given event."""
        conn = self._get_conn()
        try:
            # Get the event's embedding
            row = conn.execute(
                "SELECT embedding FROM embeddings WHERE event_id = ?",
                (event_id,)
            ).fetchone()

            if not row:
                return []

            query_embedding = json.loads(row["embedding"])

            # Get all other embeddings
            rows = conn.execute("""
                SELECT emb.event_id, emb.embedding, e.category, e.type
                FROM embeddings emb
                JOIN events e ON emb.event_id = e.id
                WHERE emb.event_id != ?
            """, (event_id,)).fetchall()

            results = []
            for r in rows:
                stored_embedding = json.loads(r["embedding"])
                similarity = self.cosine_similarity(query_embedding, stored_embedding)

                if similarity >= threshold:
                    results.append({
                        "event_id": r["event_id"],
                        "similarity": round(similarity, 4),
                        "category": r["category"],
                        "type": r["type"]
                    })

            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
        finally:
            conn.close()
