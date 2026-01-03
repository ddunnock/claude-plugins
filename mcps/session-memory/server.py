#!/usr/bin/env python3
"""
Session Memory MCP Server for Claude Desktop.

Provides persistent session memory across conversations with:
- Categorized event recording (JSONL + SQLite indexing)
- Efficient querying by category, time, and keyword
- Auto and manual checkpoints
- Session handoff summaries
- Plugin architecture for skill-specific state

Usage:
    python server.py

Configuration in Claude Desktop:
    {
        "mcpServers": {
            "session-memory": {
                "command": "python3",
                "args": ["~/.claude/session-memory/server.py"]
            }
        }
    }
"""

import asyncio
import json
import os
import sqlite3
import sys
import threading
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add plugins to path
sys.path.insert(0, str(Path(__file__).parent))

from plugins.base import PluginState, ResumptionContext, SessionPlugin
from plugins.generic import GenericPlugin

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP SDK not installed. Running in standalone mode.", file=sys.stderr)


# Default configuration
DEFAULT_CONFIG = {
    "auto_checkpoint_interval_minutes": 5,
    "auto_checkpoint_max_count": 10,
    "events_file": "storage/events.jsonl",
    "index_file": "storage/index.sqlite",
    "checkpoints_dir": "storage/checkpoints",
    "handoffs_dir": "handoffs"
}


class Session:
    """Represents an active session."""

    def __init__(
        self,
        session_id: str,
        skill_name: Optional[str] = None,
        plugin_name: Optional[str] = None,
        started_at: Optional[str] = None
    ):
        self.id = session_id
        self.skill_name = skill_name
        self.plugin_name = plugin_name
        self.started_at = started_at or datetime.utcnow().isoformat() + "Z"
        self.event_count = 0
        self.current_phase: Optional[str] = None
        self.last_checkpoint_id: Optional[str] = None


class SessionMemoryServer:
    """Main session memory server implementation."""

    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            base_path = str(Path(__file__).parent)
        self.base_path = Path(base_path)
        self.config = DEFAULT_CONFIG.copy()
        self._load_config()

        # Initialize storage
        self._init_storage()

        # Load plugins
        self.plugins: Dict[str, SessionPlugin] = {}
        self._register_plugins()

        # Current session state
        self.current_session: Optional[Session] = None
        self.current_plugin: Optional[SessionPlugin] = None
        self.plugin_state: Optional[PluginState] = None

        # Auto-checkpoint timer
        self._checkpoint_timer: Optional[threading.Timer] = None

        # Lock for thread safety
        self._lock = threading.RLock()

    def _load_config(self):
        """Load configuration from config.json if it exists."""
        config_path = self.base_path / "config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    self.config.update(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults

    def _init_storage(self):
        """Initialize storage directories and database."""
        # Create directories
        (self.base_path / "storage/checkpoints/auto").mkdir(parents=True, exist_ok=True)
        (self.base_path / "storage/checkpoints/manual").mkdir(parents=True, exist_ok=True)
        (self.base_path / "handoffs").mkdir(parents=True, exist_ok=True)

        # Initialize SQLite
        self.db_path = self.base_path / self.config["index_file"]
        self._init_database()

        # Events file path
        self.events_path = self.base_path / self.config["events_file"]
        self.events_path.parent.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT,
                session_id TEXT NOT NULL,
                parent_id TEXT,
                jsonl_offset INTEGER NOT NULL,
                jsonl_length INTEGER NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_events_category
                ON events(category, timestamp);
            CREATE INDEX IF NOT EXISTS idx_events_session
                ON events(session_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_events_time
                ON events(timestamp);

            CREATE TABLE IF NOT EXISTS checkpoints (
                id TEXT PRIMARY KEY,
                name TEXT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                session_id TEXT NOT NULL,
                event_count INTEGER,
                state_snapshot TEXT,
                summary TEXT,
                file_path TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                skill_name TEXT,
                plugin_name TEXT,
                current_phase TEXT,
                event_count INTEGER DEFAULT 0,
                last_checkpoint_id TEXT
            );
        """)

        # Create FTS table separately (may already exist)
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(
                    id, category, type, content,
                    tokenize='porter unicode61'
                )
            """)
        except sqlite3.OperationalError:
            pass  # FTS5 may not be available on all systems

        conn.commit()
        conn.close()

    def _register_plugins(self):
        """Register available plugins."""
        plugins = [GenericPlugin()]

        # Try to load skill-specific plugins
        try:
            from plugins.speckit import SpecKitPlugin
            plugins.append(SpecKitPlugin())
        except ImportError:
            pass

        try:
            from plugins.spec_refiner import SpecRefinerPlugin
            plugins.append(SpecRefinerPlugin())
        except ImportError:
            pass

        for plugin in plugins:
            self.plugins[plugin.name] = plugin
            for skill in plugin.supported_skills:
                if skill != "*":  # Don't override with wildcard
                    self.plugins[skill] = plugin

    def _get_plugin(self, skill_name: Optional[str]) -> SessionPlugin:
        """Get appropriate plugin for skill."""
        if skill_name and skill_name in self.plugins:
            return self.plugins[skill_name]
        return self.plugins.get("generic", GenericPlugin())

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}-{timestamp}"

    # =========================================================================
    # Tool Implementations
    # =========================================================================

    def session_init(
        self,
        skill_name: Optional[str] = None,
        session_id: Optional[str] = None,
        resume_from_checkpoint: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Initialize a new session or resume from checkpoint."""
        with self._lock:
            if resume_from_checkpoint:
                return self._resume_from_checkpoint(resume_from_checkpoint)

            # Create new session
            new_id = session_id or self._generate_id("sess")
            plugin = self._get_plugin(skill_name)

            self.current_session = Session(
                session_id=new_id,
                skill_name=skill_name,
                plugin_name=plugin.name
            )
            self.current_plugin = plugin
            self.plugin_state = plugin.create_initial_state()

            # Persist session to database
            self._save_session()

            # Start auto-checkpoint timer
            self._start_auto_checkpoint_timer()

            return {
                "session_id": new_id,
                "status": "new",
                "skill": skill_name,
                "plugin": plugin.name,
                "checkpoint_resumed": None,
                "resumption_context": None,
                "event_count": 0
            }

    def session_record(
        self,
        category: str,
        type: str,
        data: Dict[str, Any],
        parent_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Record a categorized event to the session log."""
        with self._lock:
            if not self.current_session:
                raise ValueError("No active session. Call session_init first.")

            event_id = self._generate_id("evt")
            timestamp = datetime.utcnow().isoformat() + "Z"

            event = {
                "id": event_id,
                "ts": timestamp,
                "category": category,
                "type": type,
                "data": data,
                "session_id": self.current_session.id,
                "parent_id": parent_id,
                "tags": tags or []
            }

            # Append to JSONL
            offset, length = self._append_event(event)

            # Index in SQLite
            self._index_event(event, offset, length)

            # Update plugin state
            if self.current_plugin and self.plugin_state:
                self.plugin_state = self.current_plugin.on_event(event, self.plugin_state)

            # Update session counter
            self.current_session.event_count += 1

            return {
                "event_id": event_id,
                "timestamp": timestamp,
                "indexed": True
            }

    def session_query(
        self,
        category: Optional[str] = None,
        categories: Optional[List[str]] = None,
        type: Optional[str] = None,
        time_range: Optional[Dict[str, str]] = None,
        keyword: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        include_data: bool = True
    ) -> Dict[str, Any]:
        """Query events by various criteria."""
        with self._lock:
            sid = session_id or (self.current_session.id if self.current_session else None)

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Build query
            conditions = []
            params = []

            if sid:
                conditions.append("e.session_id = ?")
                params.append(sid)

            if category:
                conditions.append("e.category = ?")
                params.append(category)
            elif categories:
                placeholders = ",".join("?" * len(categories))
                conditions.append(f"e.category IN ({placeholders})")
                params.extend(categories)

            if type:
                conditions.append("e.type = ?")
                params.append(type)

            if time_range:
                if "after" in time_range:
                    conditions.append("e.timestamp >= ?")
                    params.append(time_range["after"])
                if "before" in time_range:
                    conditions.append("e.timestamp <= ?")
                    params.append(time_range["before"])

            # Full-text search if FTS is available
            if keyword:
                try:
                    conditions.append(
                        "e.id IN (SELECT id FROM events_fts WHERE content MATCH ?)"
                    )
                    params.append(keyword)
                except sqlite3.OperationalError:
                    pass  # FTS not available

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Count total
            count_sql = f"SELECT COUNT(*) FROM events e WHERE {where_clause}"
            total_count = conn.execute(count_sql, params).fetchone()[0]

            # Fetch events
            query_sql = f"""
                SELECT e.id, e.timestamp, e.category, e.type, e.session_id,
                       e.parent_id, e.jsonl_offset, e.jsonl_length
                FROM events e
                WHERE {where_clause}
                ORDER BY e.timestamp DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])

            rows = conn.execute(query_sql, params).fetchall()
            conn.close()

            # Build results
            events = []
            for row in rows:
                event = {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "category": row["category"],
                    "type": row["type"],
                    "session_id": row["session_id"],
                    "parent_id": row["parent_id"]
                }

                if include_data:
                    event["data"] = self._read_event_data(
                        row["jsonl_offset"],
                        row["jsonl_length"]
                    )

                events.append(event)

            return {
                "events": events,
                "total_count": total_count,
                "returned_count": len(events),
                "has_more": total_count > offset + len(events)
            }

    def session_checkpoint(
        self,
        name: Optional[str] = None,
        summary: Optional[str] = None,
        checkpoint_type: str = "manual"
    ) -> Dict[str, Any]:
        """Create a checkpoint of current session state."""
        with self._lock:
            if not self.current_session:
                raise ValueError("No active session.")

            checkpoint_id = self._generate_id("chk")
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Build checkpoint
            checkpoint = {
                "id": checkpoint_id,
                "name": name or f"checkpoint-{self.current_session.event_count}",
                "timestamp": timestamp,
                "type": checkpoint_type,
                "session_id": self.current_session.id,
                "skill": self.current_session.skill_name,
                "plugin_state": self.plugin_state.to_dict() if self.plugin_state else {},
                "event_count": self.current_session.event_count,
                "summary": summary
            }

            # Let plugin add custom data
            if self.current_plugin and self.plugin_state:
                extra = self.current_plugin.on_checkpoint(checkpoint, self.plugin_state)
                checkpoint.update(extra)

            # Save checkpoint file
            subdir = "auto" if checkpoint_type == "auto" else "manual"
            filename = f"{checkpoint['name']}-{int(datetime.utcnow().timestamp())}.json"
            filepath = self.base_path / self.config["checkpoints_dir"] / subdir / filename

            with open(filepath, "w") as f:
                json.dump(checkpoint, f, indent=2)

            checkpoint["file_path"] = str(filepath)

            # Index in database
            self._index_checkpoint(checkpoint)

            # Manage auto-checkpoint rotation
            if checkpoint_type == "auto":
                self._rotate_auto_checkpoints()

            # Update session
            self.current_session.last_checkpoint_id = checkpoint_id

            return {
                "checkpoint_id": checkpoint_id,
                "name": checkpoint["name"],
                "timestamp": timestamp,
                "type": checkpoint_type,
                "event_count": self.current_session.event_count,
                "file_path": str(filepath)
            }

    def session_list_checkpoints(
        self,
        session_id: Optional[str] = None,
        checkpoint_type: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """List available checkpoints."""
        with self._lock:
            sid = session_id or (self.current_session.id if self.current_session else None)

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            conditions = []
            params = []

            if sid:
                conditions.append("session_id = ?")
                params.append(sid)

            if checkpoint_type:
                conditions.append("type = ?")
                params.append(checkpoint_type)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            query = f"""
                SELECT id, name, timestamp, type, session_id, event_count, summary
                FROM checkpoints
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            conn.close()

            checkpoints = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "timestamp": row["timestamp"],
                    "type": row["type"],
                    "session_id": row["session_id"],
                    "event_count": row["event_count"],
                    "summary": row["summary"]
                }
                for row in rows
            ]

            return {
                "checkpoints": checkpoints,
                "total_count": len(checkpoints)
            }

    def session_resume(
        self,
        checkpoint_id: Optional[str] = None,
        checkpoint_name: Optional[str] = None,
        use_latest: bool = False
    ) -> Dict[str, Any]:
        """Resume session from a checkpoint."""
        with self._lock:
            # Find checkpoint
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            if checkpoint_id:
                row = conn.execute(
                    "SELECT * FROM checkpoints WHERE id = ?",
                    (checkpoint_id,)
                ).fetchone()
            elif checkpoint_name:
                row = conn.execute(
                    "SELECT * FROM checkpoints WHERE name = ? ORDER BY timestamp DESC LIMIT 1",
                    (checkpoint_name,)
                ).fetchone()
            elif use_latest:
                row = conn.execute(
                    "SELECT * FROM checkpoints ORDER BY timestamp DESC LIMIT 1"
                ).fetchone()
            else:
                conn.close()
                raise ValueError("Must specify checkpoint_id, checkpoint_name, or use_latest=True")

            conn.close()

            if not row:
                raise ValueError("Checkpoint not found")

            return self._resume_from_checkpoint(row["id"])

    def _resume_from_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Internal method to resume from a checkpoint."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            "SELECT * FROM checkpoints WHERE id = ?",
            (checkpoint_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        # Load checkpoint file for full state
        checkpoint_path = row["file_path"]
        if checkpoint_path and os.path.exists(checkpoint_path):
            with open(checkpoint_path) as f:
                checkpoint_data = json.load(f)
        else:
            checkpoint_data = {}

        # Get skill/plugin info from checkpoint
        skill_name = checkpoint_data.get("skill")
        plugin = self._get_plugin(skill_name)

        # Create new session
        new_id = self._generate_id("sess")
        self.current_session = Session(
            session_id=new_id,
            skill_name=skill_name,
            plugin_name=plugin.name
        )
        self.current_plugin = plugin

        # Restore plugin state
        state_data = checkpoint_data.get("plugin_state", {})
        self.plugin_state = PluginState.from_dict(state_data)

        # Generate resumption context
        context = plugin.generate_resumption_context(
            [],  # No new events yet
            self.plugin_state,
            checkpoint_data
        )

        # Save new session
        self._save_session()

        # Start auto-checkpoint timer
        self._start_auto_checkpoint_timer()

        return {
            "session_id": new_id,
            "status": "resumed",
            "skill": skill_name,
            "plugin": plugin.name,
            "checkpoint_resumed": checkpoint_id,
            "resumption_context": context.to_dict(),
            "event_count": 0
        }

    def session_handoff(
        self,
        include_decisions: bool = True,
        include_findings: bool = True,
        include_open_questions: bool = True,
        include_progress: bool = True,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """Generate a handoff summary for session transfer."""
        with self._lock:
            if not self.current_session:
                raise ValueError("No active session.")

            # Create checkpoint first
            checkpoint_result = self.session_checkpoint(
                name="handoff-checkpoint",
                summary="Auto-created for handoff",
                checkpoint_type="manual"
            )

            # Gather data for handoff
            handoff_data = self._build_handoff_data(
                include_decisions,
                include_findings,
                include_open_questions,
                include_progress
            )

            # Generate content
            if format == "markdown":
                content = self._generate_markdown_handoff(handoff_data)
            else:
                content = json.dumps(handoff_data, indent=2)

            # Save handoff file
            timestamp = datetime.utcnow()
            ext = "md" if format == "markdown" else "json"
            filename = f"handoff-{int(timestamp.timestamp())}.{ext}"
            filepath = self.base_path / self.config["handoffs_dir"] / filename

            with open(filepath, "w") as f:
                f.write(content)

            return {
                "handoff_id": self._generate_id("handoff"),
                "timestamp": timestamp.isoformat() + "Z",
                "file_path": str(filepath),
                "content": content,
                "checkpoint_id": checkpoint_result["checkpoint_id"]
            }

    def session_status(self) -> Dict[str, Any]:
        """Get current session status and statistics."""
        with self._lock:
            if not self.current_session:
                return {
                    "active": False,
                    "message": "No active session"
                }

            # Get event counts by category
            conn = sqlite3.connect(self.db_path)
            rows = conn.execute(
                """
                SELECT category, COUNT(*) as count
                FROM events
                WHERE session_id = ?
                GROUP BY category
                """,
                (self.current_session.id,)
            ).fetchall()
            conn.close()

            events_by_category = {row[0]: row[1] for row in rows}

            # Calculate duration
            started = datetime.fromisoformat(
                self.current_session.started_at.replace("Z", "+00:00")
            )
            duration = (datetime.utcnow().replace(tzinfo=started.tzinfo) - started).total_seconds() / 60

            return {
                "active": True,
                "session_id": self.current_session.id,
                "skill": self.current_session.skill_name,
                "plugin": self.current_session.plugin_name,
                "started_at": self.current_session.started_at,
                "duration_minutes": round(duration, 1),
                "event_count": self.current_session.event_count,
                "events_by_category": events_by_category,
                "last_checkpoint": self.current_session.last_checkpoint_id,
                "plugin_state": self.plugin_state.to_dict() if self.plugin_state else {},
                "progress": self.plugin_state.progress if self.plugin_state else 0
            }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _append_event(self, event: Dict) -> tuple[int, int]:
        """Append event to JSONL file, return (offset, length)."""
        event_json = json.dumps(event)
        with open(self.events_path, "a") as f:
            offset = f.tell()
            f.write(event_json + "\n")
        return offset, len(event_json)

    def _index_event(self, event: Dict, offset: int, length: int):
        """Index event in SQLite."""
        conn = sqlite3.connect(self.db_path)

        # Insert into main table
        conn.execute("""
            INSERT INTO events (id, timestamp, category, type, session_id,
                              parent_id, jsonl_offset, jsonl_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event["id"], event["ts"], event["category"], event.get("type"),
            event["session_id"], event.get("parent_id"), offset, length
        ))

        # Try to insert into FTS (may not be available)
        try:
            conn.execute("""
                INSERT INTO events_fts (id, category, type, content)
                VALUES (?, ?, ?, ?)
            """, (
                event["id"], event["category"], event.get("type"),
                json.dumps(event.get("data", {}))
            ))
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    def _read_event_data(self, offset: int, length: int) -> Dict:
        """Read event data from JSONL at offset."""
        try:
            with open(self.events_path, "r") as f:
                f.seek(offset)
                line = f.read(length)
                event = json.loads(line)
                return event.get("data", {})
        except (IOError, json.JSONDecodeError):
            return {}

    def _index_checkpoint(self, checkpoint: Dict):
        """Index checkpoint in database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO checkpoints
            (id, name, timestamp, type, session_id, event_count, state_snapshot, summary, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            checkpoint["id"],
            checkpoint["name"],
            checkpoint["timestamp"],
            checkpoint["type"],
            checkpoint["session_id"],
            checkpoint.get("event_count"),
            json.dumps(checkpoint.get("plugin_state", {})),
            checkpoint.get("summary"),
            checkpoint.get("file_path")
        ))
        conn.commit()
        conn.close()

    def _save_session(self):
        """Save current session to database."""
        if not self.current_session:
            return

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO sessions
            (id, started_at, skill_name, plugin_name, current_phase, event_count, last_checkpoint_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.current_session.id,
            self.current_session.started_at,
            self.current_session.skill_name,
            self.current_session.plugin_name,
            self.current_session.current_phase,
            self.current_session.event_count,
            self.current_session.last_checkpoint_id
        ))
        conn.commit()
        conn.close()

    def _start_auto_checkpoint_timer(self):
        """Start auto-checkpoint timer."""
        interval = self.config["auto_checkpoint_interval_minutes"] * 60

        def auto_checkpoint():
            with self._lock:
                if self.current_session and self.current_session.event_count > 0:
                    try:
                        self.session_checkpoint(checkpoint_type="auto")
                    except Exception:
                        pass  # Don't crash on auto-checkpoint failure
            # Reschedule
            self._checkpoint_timer = threading.Timer(interval, auto_checkpoint)
            self._checkpoint_timer.daemon = True
            self._checkpoint_timer.start()

        # Cancel existing timer
        if self._checkpoint_timer:
            self._checkpoint_timer.cancel()

        self._checkpoint_timer = threading.Timer(interval, auto_checkpoint)
        self._checkpoint_timer.daemon = True
        self._checkpoint_timer.start()

    def _rotate_auto_checkpoints(self):
        """Keep only the most recent N auto-checkpoints."""
        max_count = self.config["auto_checkpoint_max_count"]
        auto_dir = self.base_path / self.config["checkpoints_dir"] / "auto"

        checkpoints = sorted(
            auto_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime
        )

        while len(checkpoints) > max_count:
            oldest = checkpoints.pop(0)
            try:
                oldest.unlink()
            except IOError:
                pass

    def _build_handoff_data(
        self,
        decisions: bool,
        findings: bool,
        questions: bool,
        progress: bool
    ) -> Dict[str, Any]:
        """Build handoff data from session events."""
        data = {
            "session_id": self.current_session.id,
            "skill": self.current_session.skill_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_count": self.current_session.event_count
        }

        if decisions:
            result = self.session_query(category="decision", limit=100)
            data["decisions"] = result["events"]

        if findings:
            result = self.session_query(category="finding", limit=100)
            data["findings"] = result["events"]

        if questions:
            result = self.session_query(category="question", limit=100)
            data["questions"] = result["events"]

        if progress and self.current_plugin and self.plugin_state:
            ctx = self.current_plugin.generate_resumption_context(
                [], self.plugin_state, {}
            )
            data["progress"] = {
                "value": self.plugin_state.progress,
                "summary": ctx.summary,
                "next_steps": ctx.next_steps,
                "blocking_items": ctx.blocking_items
            }

        return data

    def _generate_markdown_handoff(self, data: Dict) -> str:
        """Generate markdown handoff document."""
        lines = [
            "# Session Handoff",
            "",
            f"**Session ID**: {data['session_id']}",
            f"**Skill**: {data.get('skill', 'generic')}",
            f"**Timestamp**: {data['timestamp']}",
            f"**Events**: {data['event_count']}",
            "",
        ]

        if "progress" in data:
            p = data["progress"]
            lines.extend([
                "## Progress",
                "",
                f"**Completion**: {p['value']*100:.1f}%",
                "",
                f"**Summary**: {p['summary']}",
                "",
                "### Next Steps",
                ""
            ])
            for step in p.get("next_steps", []):
                lines.append(f"- {step}")

            if p.get("blocking_items"):
                lines.extend(["", "### Blocking Items", ""])
                for item in p["blocking_items"]:
                    lines.append(f"- {item}")

        if "decisions" in data and data["decisions"]:
            lines.extend(["", "## Decisions", ""])
            for evt in data["decisions"][:10]:
                d = evt.get("data", {})
                lines.append(f"- **{d.get('title', 'Untitled')}**: {d.get('rationale', '')}")

        if "findings" in data and data["findings"]:
            lines.extend(["", "## Findings", ""])
            for evt in data["findings"][:10]:
                d = evt.get("data", {})
                lines.append(f"- [{d.get('severity', 'INFO')}] {d.get('description', '')}")

        if "questions" in data and data["questions"]:
            lines.extend(["", "## Open Questions", ""])
            for evt in data["questions"]:
                d = evt.get("data", {})
                if d.get("status") != "answered":
                    lines.append(f"- {d.get('question', '')}")

        lines.extend([
            "",
            "---",
            f"*Generated at {data['timestamp']}*"
        ])

        return "\n".join(lines)


# =============================================================================
# MCP Server Setup
# =============================================================================

def create_mcp_server() -> "Server":
    """Create and configure the MCP server."""
    if not MCP_AVAILABLE:
        raise ImportError("MCP SDK not available")

    server = Server("session-memory")
    memory = SessionMemoryServer()

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="session_init",
                description="Initialize a new session or resume from checkpoint",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "skill_name": {"type": "string", "description": "Name of the skill being used"},
                        "session_id": {"type": "string", "description": "Explicit session ID"},
                        "resume_from_checkpoint": {"type": "string", "description": "Checkpoint ID to resume from"}
                    }
                }
            ),
            Tool(
                name="session_record",
                description="Record a categorized event to the session log",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Event category (tool_call, decision, finding, question, phase, custom)"},
                        "type": {"type": "string", "description": "Event type within category"},
                        "data": {"type": "object", "description": "Event payload"},
                        "parent_id": {"type": "string", "description": "Parent event ID for correlation"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags"}
                    },
                    "required": ["category", "type", "data"]
                }
            ),
            Tool(
                name="session_query",
                description="Query events by category, time range, or keyword",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Single category filter"},
                        "categories": {"type": "array", "items": {"type": "string"}, "description": "Multiple categories (OR)"},
                        "type": {"type": "string", "description": "Event type filter"},
                        "time_range": {"type": "object", "properties": {"after": {"type": "string"}, "before": {"type": "string"}}},
                        "keyword": {"type": "string", "description": "Full-text search"},
                        "limit": {"type": "integer", "default": 50},
                        "offset": {"type": "integer", "default": 0},
                        "include_data": {"type": "boolean", "default": True}
                    }
                }
            ),
            Tool(
                name="session_checkpoint",
                description="Create a checkpoint of current session state",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Checkpoint name"},
                        "summary": {"type": "string", "description": "Checkpoint summary/notes"},
                        "checkpoint_type": {"type": "string", "enum": ["auto", "manual"], "default": "manual"}
                    }
                }
            ),
            Tool(
                name="session_list_checkpoints",
                description="List available checkpoints",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "checkpoint_type": {"type": "string", "enum": ["auto", "manual"]},
                        "limit": {"type": "integer", "default": 20}
                    }
                }
            ),
            Tool(
                name="session_resume",
                description="Resume session from a checkpoint",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "checkpoint_id": {"type": "string"},
                        "checkpoint_name": {"type": "string"},
                        "use_latest": {"type": "boolean", "default": False}
                    }
                }
            ),
            Tool(
                name="session_handoff",
                description="Generate a handoff summary for session transfer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_decisions": {"type": "boolean", "default": True},
                        "include_findings": {"type": "boolean", "default": True},
                        "include_open_questions": {"type": "boolean", "default": True},
                        "include_progress": {"type": "boolean", "default": True},
                        "format": {"type": "string", "enum": ["markdown", "json"], "default": "markdown"}
                    }
                }
            ),
            Tool(
                name="session_status",
                description="Get current session status and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "session_init":
                result = memory.session_init(**arguments)
            elif name == "session_record":
                result = memory.session_record(**arguments)
            elif name == "session_query":
                result = memory.session_query(**arguments)
            elif name == "session_checkpoint":
                result = memory.session_checkpoint(**arguments)
            elif name == "session_list_checkpoints":
                result = memory.session_list_checkpoints(**arguments)
            elif name == "session_resume":
                result = memory.session_resume(**arguments)
            elif name == "session_handoff":
                result = memory.session_handoff(**arguments)
            elif name == "session_status":
                result = memory.session_status()
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def main():
    """Main entry point for MCP server."""
    if not MCP_AVAILABLE:
        print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)

    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
