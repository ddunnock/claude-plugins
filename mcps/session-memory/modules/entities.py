"""Entity extraction and knowledge graph.

This module provides:
- Auto-extraction of entities from events (files, functions, decisions, etc.)
- A lightweight knowledge graph with entities and relations
- Querying capabilities for finding related entities
"""

import json
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Entity:
    """A node in the knowledge graph."""

    id: str
    type: str  # 'file', 'function', 'class', 'decision', 'person', 'concept', 'module'
    name: str
    qualified_name: Optional[str] = None
    first_seen_session: Optional[str] = None
    first_seen_event: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "first_seen_session": self.first_seen_session,
            "first_seen_event": self.first_seen_event,
            "metadata": self.metadata
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Entity":
        return cls(
            id=row["id"],
            type=row["type"],
            name=row["name"],
            qualified_name=row["qualified_name"],
            first_seen_session=row["first_seen_session"],
            first_seen_event=row.get("first_seen_event"),
            metadata=json.loads(row["metadata"] or "{}")
        )


@dataclass
class Relation:
    """An edge in the knowledge graph."""

    id: str
    source_id: str
    target_id: str
    relation_type: str  # 'calls', 'imports', 'depends_on', 'modifies', 'decided_by', 'implements', 'tests'
    session_id: Optional[str] = None
    event_id: Optional[str] = None
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "session_id": self.session_id,
            "event_id": self.event_id,
            "weight": self.weight,
            "metadata": self.metadata
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Relation":
        return cls(
            id=row["id"],
            source_id=row["source_entity_id"],
            target_id=row["target_entity_id"],
            relation_type=row["relation_type"],
            session_id=row.get("session_id"),
            event_id=row.get("event_id"),
            weight=row["weight"] or 1.0,
            metadata=json.loads(row["metadata"] or "{}")
        )


class EntityExtractor:
    """Extract entities from event data automatically."""

    ENTITY_TYPES = ["file", "function", "class", "decision", "person", "concept", "module"]
    RELATION_TYPES = ["calls", "imports", "depends_on", "modifies", "decided_by", "implements", "tests"]

    # Regex patterns for auto-extraction
    FILE_PATTERN = re.compile(r'[\'"]?(/[\w./\-]+\.\w+)[\'"]?')
    QUALIFIED_NAME_PATTERN = re.compile(r'\b(\w+(?:\.\w+)+)\b')
    FUNCTION_CALL_PATTERN = re.compile(r'\b(\w+)\s*\(')
    CLASS_DEF_PATTERN = re.compile(r'\bclass\s+(\w+)')
    FUNCTION_DEF_PATTERN = re.compile(r'\bdef\s+(\w+)')

    def extract_from_event(
        self,
        event: Dict[str, Any],
        session_id: str
    ) -> Tuple[List[Entity], List[Tuple[str, str, str]]]:
        """
        Extract entities from an event.

        Returns:
            Tuple of (entities, relations) where relations are (source_name, target_name, relation_type)
        """
        entities: List[Entity] = []
        relations: List[Tuple[str, str, str]] = []

        category = event.get("category", "")
        event_type = event.get("type", "")
        data = event.get("data", {})
        event_id = event.get("id", "")

        # Serialize data for pattern matching
        content = json.dumps(data)

        # Extract file paths
        for match in self.FILE_PATTERN.findall(content):
            if self._is_valid_file_path(match):
                entity = Entity(
                    id=f"file:{match}",
                    type="file",
                    name=match.split("/")[-1],
                    qualified_name=match,
                    first_seen_session=session_id,
                    first_seen_event=event_id,
                    metadata={"path": match}
                )
                entities.append(entity)

        # Extract from tool_call events (Read, Write, Edit)
        if category == "tool_call":
            tool_name = data.get("tool")

            if tool_name in ("Read", "Write", "Edit", "Glob", "Grep"):
                path = data.get("file_path") or data.get("path")
                if path and self._is_valid_file_path(path):
                    entities.append(Entity(
                        id=f"file:{path}",
                        type="file",
                        name=path.split("/")[-1],
                        qualified_name=path,
                        first_seen_session=session_id,
                        first_seen_event=event_id,
                        metadata={"path": path, "tool": tool_name}
                    ))

        # Extract from decision events
        if category == "decision":
            title = data.get("title", "")
            if title:
                entities.append(Entity(
                    id=f"decision:{event_id}",
                    type="decision",
                    name=title,
                    first_seen_session=session_id,
                    first_seen_event=event_id,
                    metadata={
                        "rationale": data.get("rationale"),
                        "alternatives": data.get("alternatives", [])
                    }
                ))

        # Extract from finding events
        if category == "finding":
            description = data.get("description", "")
            if description:
                # Check if finding references a file
                file_matches = self.FILE_PATTERN.findall(description)
                for path in file_matches:
                    if self._is_valid_file_path(path):
                        relations.append((
                            f"finding:{event_id}",
                            f"file:{path}",
                            "modifies"
                        ))

        return entities, relations

    def _is_valid_file_path(self, path: str) -> bool:
        """Check if a string looks like a valid file path."""
        if not path or len(path) < 3:
            return False
        if not path.startswith("/"):
            return False
        # Check for common file extensions
        valid_extensions = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
            ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".xml",
            ".html", ".css", ".scss", ".sql", ".sh", ".bash"
        }
        ext = "." + path.split(".")[-1] if "." in path else ""
        return ext.lower() in valid_extensions or "/" in path[1:]

    def extract_code_entities(self, code: str) -> List[Entity]:
        """Extract entities from code content."""
        entities = []

        # Classes
        for match in self.CLASS_DEF_PATTERN.findall(code):
            entities.append(Entity(
                id=f"class:{match}",
                type="class",
                name=match
            ))

        # Functions
        for match in self.FUNCTION_DEF_PATTERN.findall(code):
            entities.append(Entity(
                id=f"function:{match}",
                type="function",
                name=match
            ))

        return entities


class KnowledgeGraph:
    """Lightweight knowledge graph with SQLite persistence."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.extractor = EntityExtractor()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_entity(
        self,
        entity: Entity,
        session_id: Optional[str] = None,
        event_id: Optional[str] = None
    ) -> str:
        """Add or update an entity. Returns the entity ID."""
        conn = self._get_conn()
        try:
            # Check if entity exists by qualified_name or type+name
            if entity.qualified_name:
                existing = conn.execute(
                    "SELECT id FROM entities WHERE qualified_name = ?",
                    (entity.qualified_name,)
                ).fetchone()
            else:
                existing = conn.execute(
                    "SELECT id FROM entities WHERE type = ? AND name = ?",
                    (entity.type, entity.name)
                ).fetchone()

            if existing:
                # Update existing entity
                entity.id = existing["id"]
                conn.execute("""
                    UPDATE entities
                    SET metadata = json_patch(COALESCE(metadata, '{}'), ?)
                    WHERE id = ?
                """, (json.dumps(entity.metadata), entity.id))
            else:
                # Insert new entity
                conn.execute("""
                    INSERT INTO entities
                    (id, type, name, qualified_name, first_seen_session, first_seen_event, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.id, entity.type, entity.name, entity.qualified_name,
                    session_id or entity.first_seen_session,
                    event_id or entity.first_seen_event,
                    json.dumps(entity.metadata)
                ))

            conn.commit()
            return entity.id
        finally:
            conn.close()

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        session_id: Optional[str] = None,
        event_id: Optional[str] = None,
        weight: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> str:
        """Add a relationship between entities. Returns the relation ID."""
        if relation_type not in EntityExtractor.RELATION_TYPES:
            raise ValueError(f"Invalid relation type: {relation_type}")

        conn = self._get_conn()
        try:
            relation_id = f"rel-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

            # Resolve entity IDs if names provided
            source_entity_id = self._resolve_entity_id(conn, source_id)
            target_entity_id = self._resolve_entity_id(conn, target_id)

            if not source_entity_id or not target_entity_id:
                raise ValueError(f"Entity not found: {source_id if not source_entity_id else target_id}")

            # Check for existing relation
            existing = conn.execute("""
                SELECT id, weight FROM entity_relations
                WHERE source_entity_id = ? AND target_entity_id = ? AND relation_type = ?
            """, (source_entity_id, target_entity_id, relation_type)).fetchone()

            if existing:
                # Increment weight for existing relation
                conn.execute("""
                    UPDATE entity_relations
                    SET weight = weight + ?,
                        metadata = json_patch(COALESCE(metadata, '{}'), ?)
                    WHERE id = ?
                """, (weight, json.dumps(metadata or {}), existing["id"]))
                relation_id = existing["id"]
            else:
                conn.execute("""
                    INSERT INTO entity_relations
                    (id, source_entity_id, target_entity_id, relation_type,
                     session_id, event_id, weight, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    relation_id, source_entity_id, target_entity_id, relation_type,
                    session_id, event_id, weight, json.dumps(metadata or {})
                ))

            conn.commit()
            return relation_id
        finally:
            conn.close()

    def _resolve_entity_id(self, conn: sqlite3.Connection, id_or_name: str) -> Optional[str]:
        """Resolve an entity ID from either ID or name."""
        # Try exact ID match first
        row = conn.execute(
            "SELECT id FROM entities WHERE id = ?", (id_or_name,)
        ).fetchone()
        if row:
            return row["id"]

        # Try qualified name
        row = conn.execute(
            "SELECT id FROM entities WHERE qualified_name = ?", (id_or_name,)
        ).fetchone()
        if row:
            return row["id"]

        # Try name match
        row = conn.execute(
            "SELECT id FROM entities WHERE name = ?", (id_or_name,)
        ).fetchone()
        if row:
            return row["id"]

        return None

    def query(
        self,
        entity_type: Optional[str] = None,
        name_pattern: Optional[str] = None,
        related_to: Optional[str] = None,
        relation_types: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        include_relations: bool = True,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Query entities and their relationships."""
        conn = self._get_conn()
        try:
            conditions = []
            params: List[Any] = []

            if entity_type:
                conditions.append("e.type = ?")
                params.append(entity_type)

            if name_pattern:
                conditions.append("(e.name LIKE ? OR e.qualified_name LIKE ?)")
                params.extend([f"%{name_pattern}%", f"%{name_pattern}%"])

            if session_id:
                conditions.append("e.first_seen_session = ?")
                params.append(session_id)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Handle related_to query
            if related_to:
                related_entity_id = self._resolve_entity_id(conn, related_to)
                if related_entity_id:
                    # Find entities related to the specified entity
                    rel_conditions = ["(r.source_entity_id = ? OR r.target_entity_id = ?)"]
                    rel_params = [related_entity_id, related_entity_id]

                    if relation_types:
                        placeholders = ",".join("?" * len(relation_types))
                        rel_conditions.append(f"r.relation_type IN ({placeholders})")
                        rel_params.extend(relation_types)

                    sql = f"""
                        SELECT DISTINCT e.* FROM entities e
                        JOIN entity_relations r ON (e.id = r.source_entity_id OR e.id = r.target_entity_id)
                        WHERE {" AND ".join(rel_conditions)} AND e.id != ?
                        AND {where_clause}
                        LIMIT ?
                    """
                    params = rel_params + [related_entity_id] + params + [limit]
                else:
                    # No matching entity found
                    return {"entities": [], "relations": [], "total_count": 0}
            else:
                sql = f"""
                    SELECT e.* FROM entities e
                    WHERE {where_clause}
                    ORDER BY e.first_seen_session DESC
                    LIMIT ?
                """
                params.append(limit)

            rows = conn.execute(sql, params).fetchall()
            entities = [Entity.from_row(row).to_dict() for row in rows]

            # Get relations if requested
            relations = []
            if include_relations and entities:
                entity_ids = [e["id"] for e in entities]
                placeholders = ",".join("?" * len(entity_ids))

                rel_sql = f"""
                    SELECT * FROM entity_relations
                    WHERE source_entity_id IN ({placeholders})
                       OR target_entity_id IN ({placeholders})
                """
                rel_rows = conn.execute(rel_sql, entity_ids * 2).fetchall()
                relations = [Relation.from_row(row).to_dict() for row in rel_rows]

            return {
                "entities": entities,
                "relations": relations,
                "total_count": len(entities)
            }
        finally:
            conn.close()

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get a specific entity by ID."""
        conn = self._get_conn()
        try:
            entity_id = self._resolve_entity_id(conn, entity_id)
            if not entity_id:
                return None
            row = conn.execute(
                "SELECT * FROM entities WHERE id = ?", (entity_id,)
            ).fetchone()
            return Entity.from_row(row) if row else None
        finally:
            conn.close()

    def process_event(
        self,
        event: Dict[str, Any],
        session_id: str,
        auto_extract: bool = True
    ) -> Dict[str, Any]:
        """Process an event to extract and store entities."""
        if not auto_extract:
            return {"entities_added": 0, "relations_added": 0}

        entities, relations = self.extractor.extract_from_event(event, session_id)

        entities_added = 0
        relations_added = 0

        for entity in entities:
            try:
                self.add_entity(entity, session_id, event.get("id"))
                entities_added += 1
            except Exception:
                pass  # Skip duplicates or errors

        for source, target, rel_type in relations:
            try:
                self.add_relation(source, target, rel_type, session_id, event.get("id"))
                relations_added += 1
            except Exception:
                pass  # Skip if entities don't exist

        return {
            "entities_added": entities_added,
            "relations_added": relations_added
        }
