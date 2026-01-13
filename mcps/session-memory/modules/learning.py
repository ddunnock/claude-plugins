"""Cross-session learning and pattern discovery.

This module enables learning from past sessions by:
- Storing reusable patterns, decisions, and anti-patterns
- Searching learnings by keyword and semantic similarity
- Tracking learning effectiveness via usage/outcome metrics
"""

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .embeddings import EmbeddingService


@dataclass
class Learning:
    """A reusable insight learned from past sessions."""

    id: str
    category: str  # 'pattern', 'decision', 'anti-pattern'
    title: str
    description: str
    context_hash: str
    source_session_ids: List[str]
    confidence: float = 0.7
    usage_count: int = 0
    last_applied: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "context_hash": self.context_hash,
            "source_session_ids": self.source_session_ids,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
            "last_applied": self.last_applied,
            "metadata": self.metadata
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Learning":
        return cls(
            id=row["id"],
            category=row["category"],
            title=row["title"],
            description=row["description"] or "",
            context_hash=row["context_hash"] or "",
            source_session_ids=json.loads(row["source_session_ids"] or "[]"),
            confidence=row["confidence"] or 0.7,
            usage_count=row["usage_count"] or 0,
            last_applied=row["last_applied"],
            metadata=json.loads(row["metadata"] or "{}")
        )


class LearningService:
    """Manage cross-session learnings."""

    CATEGORIES = ["pattern", "decision", "anti-pattern"]

    def __init__(
        self,
        db_path: str,
        embedding_service: Optional["EmbeddingService"] = None
    ):
        self.db_path = db_path
        self.embeddings = embedding_service

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_context_hash(self, context: str) -> str:
        """Create a hash for context similarity matching."""
        normalized = " ".join(context.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]

    def create_learning(
        self,
        category: str,
        title: str,
        description: str,
        session_id: str,
        source_events: Optional[List[str]] = None,
        confidence: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Learning:
        """Create a new learning from events."""
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Must be one of {self.CATEGORIES}")

        learning_id = f"learn-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        context_hash = self.create_context_hash(f"{title} {description}")
        timestamp = datetime.utcnow().isoformat() + "Z"

        learning = Learning(
            id=learning_id,
            category=category,
            title=title,
            description=description,
            context_hash=context_hash,
            source_session_ids=[session_id],
            confidence=confidence,
            metadata=metadata or {}
        )

        if source_events:
            learning.metadata["source_events"] = source_events

        conn = self._get_conn()
        try:
            # Insert into main table
            conn.execute("""
                INSERT INTO learnings
                (id, timestamp, category, title, description, context_hash,
                 source_session_ids, confidence, usage_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                learning.id, timestamp, learning.category, learning.title,
                learning.description, learning.context_hash,
                json.dumps(learning.source_session_ids), learning.confidence,
                json.dumps(learning.metadata)
            ))

            # Index in FTS for full-text search
            try:
                conn.execute("""
                    INSERT INTO learnings_fts (id, title, description, category)
                    VALUES (?, ?, ?, ?)
                """, (learning.id, learning.title, learning.description, learning.category))
            except sqlite3.OperationalError:
                pass  # FTS may not be available

            conn.commit()
        finally:
            conn.close()

        return learning

    def search_learnings(
        self,
        query: Optional[str] = None,
        context: Optional[str] = None,
        category: Optional[str] = None,
        session_ids: Optional[List[str]] = None,
        min_confidence: float = 0.5,
        limit: int = 10
    ) -> List[Learning]:
        """Search for relevant learnings."""
        conn = self._get_conn()
        results = []

        try:
            conditions = ["confidence >= ?"]
            params: List[Any] = [min_confidence]

            if category and category != "all":
                conditions.append("category = ?")
                params.append(category)

            # FTS search if query provided
            if query:
                try:
                    # Use FTS for better search
                    fts_query = f"""
                        SELECT l.* FROM learnings l
                        JOIN learnings_fts fts ON l.id = fts.id
                        WHERE learnings_fts MATCH ? AND {" AND ".join(conditions)}
                        ORDER BY rank, l.confidence DESC, l.usage_count DESC
                        LIMIT ?
                    """
                    rows = conn.execute(fts_query, [query] + params + [limit]).fetchall()
                    results = [Learning.from_row(row) for row in rows]
                except sqlite3.OperationalError:
                    # Fallback to LIKE search
                    conditions.append("(title LIKE ? OR description LIKE ?)")
                    params.extend([f"%{query}%", f"%{query}%"])

            # If no FTS results or no query, use regular query
            if not results:
                where_clause = " AND ".join(conditions)
                sql = f"""
                    SELECT * FROM learnings
                    WHERE {where_clause}
                    ORDER BY confidence DESC, usage_count DESC
                    LIMIT ?
                """
                params.append(limit)
                rows = conn.execute(sql, params).fetchall()
                results = [Learning.from_row(row) for row in rows]

            # Context similarity with embeddings if available
            if context and self.embeddings and hasattr(self.embeddings, 'available') and self.embeddings.available:
                # Semantic search to rerank results
                # This would use embeddings to find semantically similar learnings
                pass

        finally:
            conn.close()

        return results

    def apply_learning(
        self,
        learning_id: str,
        outcome: str,  # 'success', 'partial', 'failed'
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record that a learning was applied and update confidence."""
        if outcome not in ("success", "partial", "failed"):
            raise ValueError(f"Invalid outcome: {outcome}")

        conn = self._get_conn()
        try:
            now = datetime.utcnow().isoformat() + "Z"

            # Calculate confidence adjustment
            if outcome == "success":
                confidence_delta = 0.05
            elif outcome == "partial":
                confidence_delta = 0.0
            else:  # failed
                confidence_delta = -0.1

            # Update learning
            conn.execute("""
                UPDATE learnings
                SET usage_count = usage_count + 1,
                    last_applied = ?,
                    confidence = MIN(1.0, MAX(0.1, confidence + ?)),
                    metadata = json_set(
                        COALESCE(metadata, '{}'),
                        '$.last_outcome', ?,
                        '$.last_notes', ?
                    )
                WHERE id = ?
            """, (now, confidence_delta, outcome, notes, learning_id))

            if conn.total_changes == 0:
                conn.close()
                raise ValueError(f"Learning not found: {learning_id}")

            conn.commit()

            # Get updated learning
            row = conn.execute(
                "SELECT * FROM learnings WHERE id = ?",
                (learning_id,)
            ).fetchone()

            return {
                "learning_id": learning_id,
                "outcome": outcome,
                "new_confidence": row["confidence"],
                "usage_count": row["usage_count"],
                "applied_at": now
            }
        finally:
            conn.close()

    def get_learning(self, learning_id: str) -> Optional[Learning]:
        """Get a specific learning by ID."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM learnings WHERE id = ?",
                (learning_id,)
            ).fetchone()
            return Learning.from_row(row) if row else None
        finally:
            conn.close()

    def merge_learnings(
        self,
        learning_ids: List[str],
        new_title: Optional[str] = None,
        new_description: Optional[str] = None
    ) -> Learning:
        """Merge multiple related learnings into one."""
        conn = self._get_conn()
        try:
            # Fetch all learnings to merge
            placeholders = ",".join("?" * len(learning_ids))
            rows = conn.execute(
                f"SELECT * FROM learnings WHERE id IN ({placeholders})",
                learning_ids
            ).fetchall()

            if len(rows) < 2:
                raise ValueError("Need at least 2 learnings to merge")

            learnings = [Learning.from_row(row) for row in rows]

            # Aggregate data
            all_sessions = set()
            total_usage = 0
            avg_confidence = 0.0

            for l in learnings:
                all_sessions.update(l.source_session_ids)
                total_usage += l.usage_count
                avg_confidence += l.confidence

            avg_confidence /= len(learnings)

            # Create merged learning
            merged = self.create_learning(
                category=learnings[0].category,
                title=new_title or learnings[0].title,
                description=new_description or "\n\n".join(l.description for l in learnings),
                session_id=list(all_sessions)[0],
                confidence=min(1.0, avg_confidence + 0.1),  # Boost for merged
                metadata={
                    "merged_from": learning_ids,
                    "total_historical_usage": total_usage
                }
            )

            # Update source sessions
            conn.execute("""
                UPDATE learnings
                SET source_session_ids = ?
                WHERE id = ?
            """, (json.dumps(list(all_sessions)), merged.id))

            conn.commit()
            return merged
        finally:
            conn.close()
