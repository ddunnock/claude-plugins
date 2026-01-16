#!/usr/bin/env python3
"""
Streaming Output MCP Server

A simple, reliable MCP for streaming structured content to persistent SQLite storage
with automatic session break recovery.

Core insight: The content IS the state. Store the actual work, not metadata about work.
Store raw structured content → render to ANY format on demand.

Version: 2.0.0
- Added multiple export formats (markdown, html, text, csv, yaml)
- Added file export capability
- Added document templates
- Added finalize and delete tools
- Added tool output schemas (MCP 2025 spec)
- Added HTTP transport support
"""

import asyncio
import hashlib
import html
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool


# Default database location
DEFAULT_DB_DIR = Path.home() / ".claude" / "streaming-output"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "streams.db"

# =============================================================================
# Document Templates - Pre-defined structures for common document types
# =============================================================================

DOCUMENT_TEMPLATES = {
    "security-audit": {
        "schema_type": "findings",
        "blocks": [
            {"key": "executive_summary", "type": "section"},
            {"key": "scope", "type": "section"},
            {"key": "methodology", "type": "section"},
            {"key": "critical_findings", "type": "finding"},
            {"key": "high_findings", "type": "finding"},
            {"key": "medium_findings", "type": "finding"},
            {"key": "low_findings", "type": "finding"},
            {"key": "recommendations", "type": "section"},
            {"key": "conclusion", "type": "section"},
        ]
    },
    "code-review": {
        "schema_type": "findings",
        "blocks": [
            {"key": "overview", "type": "section"},
            {"key": "architecture_review", "type": "section"},
            {"key": "code_quality", "type": "finding"},
            {"key": "security_issues", "type": "finding"},
            {"key": "performance_issues", "type": "finding"},
            {"key": "suggestions", "type": "section"},
        ]
    },
    "sprint-retrospective": {
        "schema_type": "report",
        "blocks": [
            {"key": "sprint_summary", "type": "section"},
            {"key": "what_went_well", "type": "section"},
            {"key": "what_could_improve", "type": "section"},
            {"key": "action_items", "type": "task"},
            {"key": "metrics", "type": "raw"},
        ]
    },
    "technical-spec": {
        "schema_type": "report",
        "blocks": [
            {"key": "overview", "type": "section"},
            {"key": "requirements", "type": "section"},
            {"key": "architecture", "type": "section"},
            {"key": "api_design", "type": "raw"},
            {"key": "data_model", "type": "raw"},
            {"key": "implementation_plan", "type": "task"},
            {"key": "risks", "type": "finding"},
        ]
    },
    "adr": {
        "schema_type": "report",
        "blocks": [
            {"key": "context", "type": "section"},
            {"key": "decision", "type": "decision"},
            {"key": "consequences", "type": "section"},
        ]
    },
    "research-report": {
        "schema_type": "report",
        "blocks": [
            {"key": "abstract", "type": "section"},
            {"key": "introduction", "type": "section"},
            {"key": "methodology", "type": "section"},
            {"key": "findings", "type": "section"},
            {"key": "analysis", "type": "section"},
            {"key": "conclusion", "type": "section"},
            {"key": "references", "type": "raw"},
        ]
    },
    "task-list": {
        "schema_type": "tasks",
        "blocks": []  # Tasks are added dynamically
    },
}


class StreamingOutputServer:
    """Simple streaming output server with SQLite persistence."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Documents: containers for streamed content
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    schema_type TEXT DEFAULT 'generic',
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT,
                    template TEXT
                );

                -- Blocks: atomic content units
                CREATE TABLE IF NOT EXISTS blocks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    block_key TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    block_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                    UNIQUE (document_id, block_key)
                );

                -- Context preservation for interrupted writes
                CREATE TABLE IF NOT EXISTS recovery_context (
                    id TEXT PRIMARY KEY,
                    block_id TEXT NOT NULL,
                    partial_content TEXT,
                    captured_at TEXT NOT NULL,
                    FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_blocks_document ON blocks(document_id, sequence);
                CREATE INDEX IF NOT EXISTS idx_blocks_status ON blocks(document_id, status);

                -- Add template column if not exists (migration)
                -- SQLite doesn't support ADD COLUMN IF NOT EXISTS, so we handle this gracefully
            """)

            # Check if template column exists, add if not
            cursor = conn.execute("PRAGMA table_info(documents)")
            columns = [row[1] for row in cursor.fetchall()]
            if "template" not in columns:
                conn.execute("ALTER TABLE documents ADD COLUMN template TEXT")

            conn.commit()

    def _now(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()

    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID with prefix."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_part = uuid.uuid4().hex[:8]
        return f"{prefix}_{timestamp}_{random_part}"

    def _hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # =========================================================================
    # Tool: stream_start
    # =========================================================================
    def stream_start(
        self,
        title: str,
        schema_type: str = "generic",
        template: Optional[str] = None,
        blocks: Optional[List[Dict[str, str]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize a new document, optionally using a template or pre-declaring blocks.

        Args:
            title: Document title
            schema_type: Type of document (generic, report, tasks, findings, custom)
            template: Optional template name (security-audit, code-review, etc.)
            blocks: Optional list of block declarations [{key, type}]
            metadata: Optional metadata JSON

        Returns:
            Document info including id and declared blocks
        """
        doc_id = self._generate_id("doc")
        now = self._now()

        # If template specified, use it
        if template and template in DOCUMENT_TEMPLATES:
            tpl = DOCUMENT_TEMPLATES[template]
            schema_type = tpl.get("schema_type", schema_type)
            if not blocks:
                blocks = tpl.get("blocks", [])

        with sqlite3.connect(self.db_path) as conn:
            # Create document
            conn.execute(
                """INSERT INTO documents (id, title, schema_type, status, created_at, updated_at, metadata, template)
                   VALUES (?, ?, ?, 'draft', ?, ?, ?, ?)""",
                (doc_id, title, schema_type, now, now, json.dumps(metadata) if metadata else None, template)
            )

            # Pre-declare blocks if provided
            declared_blocks = []
            if blocks:
                for seq, block_decl in enumerate(blocks, 1):
                    block_key = block_decl.get("key", f"block_{seq}")
                    block_type = block_decl.get("type", "section")
                    block_id = self._generate_id("blk")

                    conn.execute(
                        """INSERT INTO blocks (id, document_id, block_key, sequence, block_type, content, hash, status, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, '{}', '', 'pending', ?, ?)""",
                        (block_id, doc_id, block_key, seq, block_type, now, now)
                    )
                    declared_blocks.append({
                        "id": block_id,
                        "key": block_key,
                        "type": block_type,
                        "sequence": seq,
                        "status": "pending"
                    })

            conn.commit()

        result = {
            "document_id": doc_id,
            "title": title,
            "schema_type": schema_type,
            "status": "draft",
            "created_at": now,
            "blocks": declared_blocks,
            "message": f"Document created with {len(declared_blocks)} pre-declared blocks"
        }

        if template:
            result["template"] = template

        return result

    # =========================================================================
    # Tool: stream_write
    # =========================================================================
    def stream_write(
        self,
        document_id: str,
        block_key: str,
        content: Dict[str, Any],
        block_type: str = "section",
        repair: bool = False
    ) -> Dict[str, Any]:
        """
        Write content to a block (atomic, verified).

        Args:
            document_id: Document ID
            block_key: User-defined block key (e.g., "intro", "findings")
            content: JSON content for the block
            block_type: Block type (section, task, finding, decision, raw)
            repair: If true, allow overwriting existing complete block

        Returns:
            Block info including hash for verification
        """
        now = self._now()
        content_str = json.dumps(content, ensure_ascii=False)
        content_hash = self._hash_content(content_str)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Verify document exists
            doc = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
            if not doc:
                raise ValueError(f"Document not found: {document_id}")

            if doc["status"] == "finalized":
                raise ValueError(f"Document is finalized, cannot write: {document_id}")

            # Check if block exists
            existing = conn.execute(
                "SELECT * FROM blocks WHERE document_id = ? AND block_key = ?",
                (document_id, block_key)
            ).fetchone()

            if existing:
                # Block exists - check if we can update
                if existing["status"] == "complete" and not repair:
                    raise ValueError(
                        f"Block '{block_key}' already complete. Use repair=true to overwrite."
                    )

                # Update existing block
                conn.execute(
                    """UPDATE blocks SET content = ?, hash = ?, status = 'complete',
                       block_type = ?, updated_at = ? WHERE id = ?""",
                    (content_str, content_hash, block_type, now, existing["id"])
                )

                # Clear any recovery context
                conn.execute(
                    "DELETE FROM recovery_context WHERE block_id = ?",
                    (existing["id"],)
                )

                block_id = existing["id"]
                sequence = existing["sequence"]
                action = "updated" if repair else "completed"
            else:
                # Create new block
                block_id = self._generate_id("blk")

                # Get next sequence number
                max_seq = conn.execute(
                    "SELECT COALESCE(MAX(sequence), 0) FROM blocks WHERE document_id = ?",
                    (document_id,)
                ).fetchone()[0]
                sequence = max_seq + 1

                conn.execute(
                    """INSERT INTO blocks (id, document_id, block_key, sequence, block_type, content, hash, status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'complete', ?, ?)""",
                    (block_id, document_id, block_key, sequence, block_type, content_str, content_hash, now, now)
                )
                action = "created"

            # Update document timestamp
            conn.execute(
                "UPDATE documents SET updated_at = ? WHERE id = ?",
                (now, document_id)
            )

            conn.commit()

        return {
            "block_id": block_id,
            "block_key": block_key,
            "sequence": sequence,
            "block_type": block_type,
            "hash": content_hash,
            "status": "complete",
            "action": action,
            "message": f"Block '{block_key}' {action} successfully"
        }

    # =========================================================================
    # Tool: stream_status
    # =========================================================================
    def stream_status(
        self,
        document_id: Optional[str] = None,
        verify: bool = False
    ) -> Dict[str, Any]:
        """
        Get document status, find resume point, verify integrity.

        Args:
            document_id: Specific document ID, or None to list recent documents
            verify: If true, verify content hashes

        Returns:
            Status info including resume_from for incomplete documents
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if document_id is None:
                # List recent documents
                docs = conn.execute(
                    """SELECT id, title, schema_type, status, created_at, updated_at, template
                       FROM documents ORDER BY updated_at DESC LIMIT 10"""
                ).fetchall()

                return {
                    "documents": [
                        {
                            "id": d["id"],
                            "title": d["title"],
                            "schema_type": d["schema_type"],
                            "status": d["status"],
                            "template": d["template"],
                            "created_at": d["created_at"],
                            "updated_at": d["updated_at"]
                        }
                        for d in docs
                    ],
                    "available_templates": list(DOCUMENT_TEMPLATES.keys()),
                    "message": f"Found {len(docs)} recent documents"
                }

            # Get specific document
            doc = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
            if not doc:
                raise ValueError(f"Document not found: {document_id}")

            # Get blocks
            blocks = conn.execute(
                """SELECT * FROM blocks WHERE document_id = ? ORDER BY sequence""",
                (document_id,)
            ).fetchall()

            # Analyze block status
            block_info = []
            pending_blocks = []
            writing_blocks = []
            integrity_errors = []

            for b in blocks:
                info = {
                    "id": b["id"],
                    "key": b["block_key"],
                    "type": b["block_type"],
                    "sequence": b["sequence"],
                    "status": b["status"],
                    "hash": b["hash"]
                }

                if b["status"] == "pending":
                    pending_blocks.append(b["block_key"])
                elif b["status"] == "writing":
                    writing_blocks.append(b["block_key"])

                # Verify hash if requested
                if verify and b["status"] == "complete" and b["content"]:
                    computed_hash = self._hash_content(b["content"])
                    if computed_hash != b["hash"]:
                        integrity_errors.append({
                            "block_key": b["block_key"],
                            "stored_hash": b["hash"],
                            "computed_hash": computed_hash
                        })
                        info["integrity"] = "FAILED"
                    else:
                        info["integrity"] = "OK"

                block_info.append(info)

            # Check for recovery context
            preserved_context = None
            if writing_blocks:
                recovery = conn.execute(
                    """SELECT rc.*, b.block_key FROM recovery_context rc
                       JOIN blocks b ON rc.block_id = b.id
                       WHERE b.document_id = ? ORDER BY rc.captured_at DESC LIMIT 1""",
                    (document_id,)
                ).fetchone()
                if recovery:
                    preserved_context = {
                        "block_key": recovery["block_key"],
                        "partial_content": recovery["partial_content"],
                        "captured_at": recovery["captured_at"]
                    }

            # Determine resume point
            resume_from = None
            if pending_blocks:
                resume_from = pending_blocks[0]
            elif writing_blocks:
                resume_from = writing_blocks[0]

            result = {
                "document_id": document_id,
                "title": doc["title"],
                "schema_type": doc["schema_type"],
                "status": doc["status"],
                "template": doc["template"] if "template" in doc.keys() else None,
                "created_at": doc["created_at"],
                "updated_at": doc["updated_at"],
                "blocks": block_info,
                "summary": {
                    "total": len(blocks),
                    "complete": len([b for b in blocks if b["status"] == "complete"]),
                    "pending": len(pending_blocks),
                    "writing": len(writing_blocks)
                }
            }

            if resume_from:
                result["resume_from"] = resume_from
            if preserved_context:
                result["preserved_context"] = preserved_context
            if verify:
                result["integrity"] = {
                    "verified": True,
                    "errors": integrity_errors if integrity_errors else None
                }

            return result

    # =========================================================================
    # Tool: stream_read (enhanced with multiple formats)
    # =========================================================================
    def stream_read(
        self,
        document_id: str,
        format: str = "json",
        blocks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Read document content in any supported format.

        Args:
            document_id: Document ID
            format: Output format (json, markdown, html, text, csv, yaml)
            blocks: Optional list of block keys to include (default: all)

        Returns:
            Document content in requested format
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Get document
            doc = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
            if not doc:
                raise ValueError(f"Document not found: {document_id}")

            # Get blocks
            if blocks:
                placeholders = ",".join("?" * len(blocks))
                block_rows = conn.execute(
                    f"""SELECT * FROM blocks WHERE document_id = ? AND block_key IN ({placeholders})
                        ORDER BY sequence""",
                    [document_id] + blocks
                ).fetchall()
            else:
                block_rows = conn.execute(
                    "SELECT * FROM blocks WHERE document_id = ? ORDER BY sequence",
                    (document_id,)
                ).fetchall()

            # Dispatch to appropriate renderer
            renderers = {
                "json": self._render_json,
                "markdown": self._render_markdown,
                "html": self._render_html,
                "text": self._render_text,
                "csv": self._render_csv,
                "yaml": self._render_yaml,
            }

            if format not in renderers:
                raise ValueError(f"Unknown format: {format}. Supported: {', '.join(renderers.keys())}")

            return renderers[format](doc, block_rows)

    def _render_json(self, doc: sqlite3.Row, blocks: List[sqlite3.Row]) -> Dict[str, Any]:
        """Render document as JSON structure (raw structured content)."""
        return {
            "format": "json",
            "document": {
                "id": doc["id"],
                "title": doc["title"],
                "schema_type": doc["schema_type"],
                "status": doc["status"],
                "metadata": json.loads(doc["metadata"]) if doc["metadata"] else None,
                "created_at": doc["created_at"],
                "updated_at": doc["updated_at"]
            },
            "blocks": [
                {
                    "key": b["block_key"],
                    "type": b["block_type"],
                    "sequence": b["sequence"],
                    "status": b["status"],
                    "content": json.loads(b["content"]) if b["content"] else None
                }
                for b in blocks
            ],
            "block_count": len(blocks)
        }

    def _render_markdown(self, doc: sqlite3.Row, blocks: List[sqlite3.Row]) -> Dict[str, Any]:
        """Render document as Markdown."""
        lines = []

        # Document header
        lines.append(f"# {doc['title']}")
        lines.append("")
        lines.append(f"> **Document ID**: {doc['id']}")
        lines.append(f"> **Type**: {doc['schema_type']}")
        lines.append(f"> **Status**: {doc['status']}")
        lines.append(f"> **Updated**: {doc['updated_at']}")
        lines.append("")

        # Render each block
        for block in blocks:
            if block["status"] != "complete":
                lines.append(f"## {block['block_key']} _(pending)_")
                lines.append("")
                continue

            content = json.loads(block["content"]) if block["content"] else {}
            block_type = block["block_type"]

            # Render based on block type
            if block_type == "section":
                lines.extend(self._render_section_md(block["block_key"], content))
            elif block_type == "task":
                lines.extend(self._render_task_md(content))
            elif block_type == "finding":
                lines.extend(self._render_finding_md(content))
            elif block_type == "decision":
                lines.extend(self._render_decision_md(content))
            else:  # raw or unknown
                lines.extend(self._render_raw_md(block["block_key"], content))

            lines.append("")

        markdown = "\n".join(lines)
        return {
            "format": "markdown",
            "content": markdown,
            "block_count": len(blocks)
        }

    def _render_html(self, doc: sqlite3.Row, blocks: List[sqlite3.Row]) -> Dict[str, Any]:
        """Render document as HTML."""
        lines = []

        lines.append("<!DOCTYPE html>")
        lines.append("<html lang=\"en\">")
        lines.append("<head>")
        lines.append(f"  <meta charset=\"UTF-8\">")
        lines.append(f"  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        lines.append(f"  <title>{html.escape(doc['title'])}</title>")
        lines.append("  <style>")
        lines.append("    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; }")
        lines.append("    h1 { border-bottom: 2px solid #333; padding-bottom: 0.5rem; }")
        lines.append("    h2 { color: #444; margin-top: 2rem; }")
        lines.append("    .meta { background: #f5f5f5; padding: 1rem; border-radius: 4px; margin-bottom: 2rem; font-size: 0.9rem; }")
        lines.append("    .meta span { display: block; }")
        lines.append("    .block { margin-bottom: 2rem; }")
        lines.append("    .pending { color: #999; font-style: italic; }")
        lines.append("    .finding { border-left: 4px solid #666; padding-left: 1rem; margin: 1rem 0; }")
        lines.append("    .finding.error { border-color: #dc3545; }")
        lines.append("    .finding.warn { border-color: #ffc107; }")
        lines.append("    .finding.info { border-color: #17a2b8; }")
        lines.append("    .task { padding: 0.5rem 1rem; background: #f8f9fa; border-radius: 4px; margin: 0.5rem 0; }")
        lines.append("    .task.complete { background: #d4edda; }")
        lines.append("    .decision { background: #e7f3ff; padding: 1rem; border-radius: 4px; }")
        lines.append("    pre { background: #282c34; color: #abb2bf; padding: 1rem; border-radius: 4px; overflow-x: auto; }")
        lines.append("    code { font-family: 'Fira Code', Consolas, monospace; }")
        lines.append("  </style>")
        lines.append("</head>")
        lines.append("<body>")

        # Header
        lines.append(f"  <h1>{html.escape(doc['title'])}</h1>")
        lines.append("  <div class=\"meta\">")
        lines.append(f"    <span><strong>Document ID:</strong> {html.escape(doc['id'])}</span>")
        lines.append(f"    <span><strong>Type:</strong> {html.escape(doc['schema_type'])}</span>")
        lines.append(f"    <span><strong>Status:</strong> {html.escape(doc['status'])}</span>")
        lines.append(f"    <span><strong>Updated:</strong> {html.escape(doc['updated_at'])}</span>")
        lines.append("  </div>")

        # Blocks
        for block in blocks:
            if block["status"] != "complete":
                lines.append(f"  <div class=\"block\">")
                lines.append(f"    <h2>{html.escape(block['block_key'])} <span class=\"pending\">(pending)</span></h2>")
                lines.append(f"  </div>")
                continue

            content = json.loads(block["content"]) if block["content"] else {}
            block_type = block["block_type"]

            if block_type == "section":
                lines.extend(self._render_section_html(block["block_key"], content))
            elif block_type == "task":
                lines.extend(self._render_task_html(content))
            elif block_type == "finding":
                lines.extend(self._render_finding_html(content))
            elif block_type == "decision":
                lines.extend(self._render_decision_html(content))
            else:
                lines.extend(self._render_raw_html(block["block_key"], content))

        lines.append("</body>")
        lines.append("</html>")

        return {
            "format": "html",
            "content": "\n".join(lines),
            "block_count": len(blocks)
        }

    def _render_text(self, doc: sqlite3.Row, blocks: List[sqlite3.Row]) -> Dict[str, Any]:
        """Render document as plain text."""
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append(doc['title'].upper())
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Document ID: {doc['id']}")
        lines.append(f"Type: {doc['schema_type']}")
        lines.append(f"Status: {doc['status']}")
        lines.append(f"Updated: {doc['updated_at']}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

        # Blocks
        for block in blocks:
            if block["status"] != "complete":
                lines.append(f"{block['block_key'].upper()} (pending)")
                lines.append("-" * 40)
                lines.append("")
                continue

            content = json.loads(block["content"]) if block["content"] else {}
            block_type = block["block_type"]

            if block_type == "section":
                title = content.get("title", block["block_key"].replace("_", " ").title())
                lines.append(title.upper())
                lines.append("-" * len(title))
                lines.append("")
                if content.get("body"):
                    lines.append(content["body"])
                    lines.append("")
            elif block_type == "task":
                status_mark = "[X]" if content.get("status") == "complete" else "[ ]"
                task_id = content.get("id", "")
                title = content.get("title", "Untitled Task")
                lines.append(f"{status_mark} {task_id}: {title}")
                if content.get("assignee"):
                    lines.append(f"    Assignee: {content['assignee']}")
                if content.get("notes"):
                    lines.append(f"    Notes: {content['notes']}")
                lines.append("")
            elif block_type == "finding":
                severity = content.get("severity", "INFO")
                finding_id = content.get("id", "")
                lines.append(f"[{severity}] {finding_id}: {content.get('description', 'Finding')}")
                if content.get("evidence"):
                    lines.append(f"    Evidence: {content['evidence']}")
                if content.get("recommendation"):
                    lines.append(f"    Recommendation: {content['recommendation']}")
                lines.append("")
            elif block_type == "decision":
                lines.append(f"DECISION: {content.get('title', 'Decision')}")
                lines.append("-" * 40)
                if content.get("context"):
                    lines.append(f"Context: {content['context']}")
                if content.get("decision"):
                    lines.append(f"Decision: {content['decision']}")
                if content.get("rationale"):
                    lines.append(f"Rationale: {content['rationale']}")
                lines.append("")
            else:
                lines.append(block["block_key"].upper())
                lines.append("-" * 40)
                lines.append(json.dumps(content, indent=2))
                lines.append("")

        return {
            "format": "text",
            "content": "\n".join(lines),
            "block_count": len(blocks)
        }

    def _render_csv(self, doc: sqlite3.Row, blocks: List[sqlite3.Row]) -> Dict[str, Any]:
        """Render document as CSV (best for task lists and findings)."""
        import csv
        import io

        output = io.StringIO()

        # Determine columns based on block types
        block_types = set(b["block_type"] for b in blocks if b["status"] == "complete")

        if "task" in block_types:
            # Task-focused CSV
            writer = csv.writer(output)
            writer.writerow(["ID", "Title", "Status", "Assignee", "Notes"])

            for block in blocks:
                if block["status"] != "complete" or block["block_type"] != "task":
                    continue
                content = json.loads(block["content"]) if block["content"] else {}
                writer.writerow([
                    content.get("id", ""),
                    content.get("title", ""),
                    content.get("status", ""),
                    content.get("assignee", ""),
                    content.get("notes", "")
                ])
        elif "finding" in block_types:
            # Finding-focused CSV
            writer = csv.writer(output)
            writer.writerow(["ID", "Severity", "Description", "Evidence", "Recommendation"])

            for block in blocks:
                if block["status"] != "complete" or block["block_type"] != "finding":
                    continue
                content = json.loads(block["content"]) if block["content"] else {}
                writer.writerow([
                    content.get("id", ""),
                    content.get("severity", ""),
                    content.get("description", ""),
                    content.get("evidence", ""),
                    content.get("recommendation", "")
                ])
        else:
            # Generic CSV - all blocks
            writer = csv.writer(output)
            writer.writerow(["Block Key", "Type", "Status", "Content Summary"])

            for block in blocks:
                content = json.loads(block["content"]) if block["content"] else {}
                summary = content.get("title", content.get("description", str(content)[:100]))
                writer.writerow([
                    block["block_key"],
                    block["block_type"],
                    block["status"],
                    summary
                ])

        return {
            "format": "csv",
            "content": output.getvalue(),
            "block_count": len(blocks)
        }

    def _render_yaml(self, doc: sqlite3.Row, blocks: List[sqlite3.Row]) -> Dict[str, Any]:
        """Render document as YAML."""
        # Manual YAML rendering to avoid dependency
        lines = []

        lines.append("document:")
        lines.append(f"  id: {doc['id']}")
        lines.append(f"  title: \"{doc['title']}\"")
        lines.append(f"  schema_type: {doc['schema_type']}")
        lines.append(f"  status: {doc['status']}")
        lines.append(f"  created_at: {doc['created_at']}")
        lines.append(f"  updated_at: {doc['updated_at']}")

        if doc["metadata"]:
            lines.append("  metadata:")
            metadata = json.loads(doc["metadata"])
            for k, v in metadata.items():
                lines.append(f"    {k}: {json.dumps(v)}")

        lines.append("")
        lines.append("blocks:")

        for block in blocks:
            lines.append(f"  - key: {block['block_key']}")
            lines.append(f"    type: {block['block_type']}")
            lines.append(f"    status: {block['status']}")
            lines.append(f"    sequence: {block['sequence']}")

            if block["status"] == "complete" and block["content"]:
                content = json.loads(block["content"])
                lines.append("    content:")
                for k, v in content.items():
                    if isinstance(v, str) and "\n" in v:
                        lines.append(f"      {k}: |")
                        for line in v.split("\n"):
                            lines.append(f"        {line}")
                    elif isinstance(v, list):
                        lines.append(f"      {k}:")
                        for item in v:
                            lines.append(f"        - {json.dumps(item)}")
                    else:
                        lines.append(f"      {k}: {json.dumps(v)}")

        return {
            "format": "yaml",
            "content": "\n".join(lines),
            "block_count": len(blocks)
        }

    # =========================================================================
    # Markdown block renderers
    # =========================================================================
    def _render_section_md(self, key: str, content: Dict) -> List[str]:
        lines = []
        title = content.get("title", key.replace("_", " ").title())
        lines.append(f"## {title}")
        lines.append("")
        if "body" in content:
            lines.append(content["body"])
        return lines

    def _render_task_md(self, content: Dict) -> List[str]:
        lines = []
        status_icon = "[x]" if content.get("status") == "complete" else "[ ]"
        task_id = content.get("id", "")
        title = content.get("title", "Untitled Task")
        lines.append(f"### {status_icon} {task_id}: {title}")
        lines.append("")
        if content.get("assignee"):
            lines.append(f"**Assignee**: {content['assignee']}")
        if content.get("status"):
            lines.append(f"**Status**: {content['status']}")
        if content.get("notes"):
            lines.append("")
            lines.append(content["notes"])
        return lines

    def _render_finding_md(self, content: Dict) -> List[str]:
        lines = []
        severity = content.get("severity", "INFO")
        finding_id = content.get("id", "")
        severity_icon = {"ERROR": "🔴", "WARN": "🟡", "INFO": "🔵"}.get(severity, "⚪")
        lines.append(f"### {severity_icon} {finding_id}: {content.get('description', 'Finding')}")
        lines.append("")
        if content.get("evidence"):
            lines.append("**Evidence**:")
            lines.append(f"> {content['evidence']}")
            lines.append("")
        if content.get("recommendation"):
            lines.append(f"**Recommendation**: {content['recommendation']}")
        return lines

    def _render_decision_md(self, content: Dict) -> List[str]:
        lines = []
        decision_id = content.get("id", "")
        title = content.get("title", "Decision")
        lines.append(f"### 📋 {decision_id}: {title}")
        lines.append("")
        if content.get("context"):
            lines.append("**Context**:")
            lines.append(content["context"])
            lines.append("")
        if content.get("decision"):
            lines.append("**Decision**:")
            lines.append(content["decision"])
            lines.append("")
        if content.get("rationale"):
            lines.append("**Rationale**:")
            lines.append(content["rationale"])
            lines.append("")
        if content.get("alternatives"):
            lines.append("**Alternatives Considered**:")
            for alt in content["alternatives"]:
                lines.append(f"- {alt}")
        return lines

    def _render_raw_md(self, key: str, content: Dict) -> List[str]:
        lines = []
        lines.append(f"## {key}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(content, indent=2))
        lines.append("```")
        return lines

    # =========================================================================
    # HTML block renderers
    # =========================================================================
    def _render_section_html(self, key: str, content: Dict) -> List[str]:
        lines = []
        title = html.escape(content.get("title", key.replace("_", " ").title()))
        lines.append(f"  <div class=\"block\">")
        lines.append(f"    <h2>{title}</h2>")
        if content.get("body"):
            # Convert newlines to <br> for HTML
            body = html.escape(content["body"]).replace("\n", "<br>")
            lines.append(f"    <p>{body}</p>")
        lines.append(f"  </div>")
        return lines

    def _render_task_html(self, content: Dict) -> List[str]:
        lines = []
        status_class = "complete" if content.get("status") == "complete" else ""
        status_icon = "✅" if content.get("status") == "complete" else "⬜"
        task_id = html.escape(content.get("id", ""))
        title = html.escape(content.get("title", "Untitled Task"))
        lines.append(f"  <div class=\"task {status_class}\">")
        lines.append(f"    <strong>{status_icon} {task_id}: {title}</strong>")
        if content.get("assignee"):
            lines.append(f"    <br><small>Assignee: {html.escape(content['assignee'])}</small>")
        if content.get("notes"):
            lines.append(f"    <br><small>{html.escape(content['notes'])}</small>")
        lines.append(f"  </div>")
        return lines

    def _render_finding_html(self, content: Dict) -> List[str]:
        lines = []
        severity = content.get("severity", "INFO").lower()
        finding_id = html.escape(content.get("id", ""))
        description = html.escape(content.get("description", "Finding"))
        lines.append(f"  <div class=\"finding {severity}\">")
        lines.append(f"    <h3>{finding_id}: {description}</h3>")
        if content.get("evidence"):
            lines.append(f"    <p><strong>Evidence:</strong> {html.escape(content['evidence'])}</p>")
        if content.get("recommendation"):
            lines.append(f"    <p><strong>Recommendation:</strong> {html.escape(content['recommendation'])}</p>")
        lines.append(f"  </div>")
        return lines

    def _render_decision_html(self, content: Dict) -> List[str]:
        lines = []
        decision_id = html.escape(content.get("id", ""))
        title = html.escape(content.get("title", "Decision"))
        lines.append(f"  <div class=\"decision\">")
        lines.append(f"    <h3>📋 {decision_id}: {title}</h3>")
        if content.get("context"):
            lines.append(f"    <p><strong>Context:</strong> {html.escape(content['context'])}</p>")
        if content.get("decision"):
            lines.append(f"    <p><strong>Decision:</strong> {html.escape(content['decision'])}</p>")
        if content.get("rationale"):
            lines.append(f"    <p><strong>Rationale:</strong> {html.escape(content['rationale'])}</p>")
        if content.get("alternatives"):
            lines.append(f"    <p><strong>Alternatives:</strong></p><ul>")
            for alt in content["alternatives"]:
                lines.append(f"      <li>{html.escape(alt)}</li>")
            lines.append(f"    </ul>")
        lines.append(f"  </div>")
        return lines

    def _render_raw_html(self, key: str, content: Dict) -> List[str]:
        lines = []
        lines.append(f"  <div class=\"block\">")
        lines.append(f"    <h2>{html.escape(key)}</h2>")
        lines.append(f"    <pre><code>{html.escape(json.dumps(content, indent=2))}</code></pre>")
        lines.append(f"  </div>")
        return lines

    # =========================================================================
    # Tool: stream_export (NEW)
    # =========================================================================
    def stream_export(
        self,
        document_id: str,
        output_path: str,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Export document to a file in the specified format.

        Args:
            document_id: Document ID
            output_path: Path to save the file (supports ~ expansion)
            format: Output format (json, markdown, html, text, csv, yaml)

        Returns:
            Export result with file path and size
        """
        # Expand path
        expanded_path = Path(os.path.expanduser(output_path))

        # Ensure parent directory exists
        expanded_path.parent.mkdir(parents=True, exist_ok=True)

        # Get rendered content
        result = self.stream_read(document_id, format=format)
        content = result.get("content")

        if not content:
            # JSON format returns structured data
            content = json.dumps(result, indent=2, ensure_ascii=False)

        # Write to file
        with open(expanded_path, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = expanded_path.stat().st_size

        return {
            "document_id": document_id,
            "format": format,
            "output_path": str(expanded_path),
            "file_size": file_size,
            "block_count": result.get("block_count", 0),
            "message": f"Exported to {expanded_path} ({file_size} bytes)"
        }

    # =========================================================================
    # Tool: stream_finalize (expose existing method)
    # =========================================================================
    def stream_finalize(self, document_id: str) -> Dict[str, Any]:
        """
        Mark document as finalized (no more writes allowed).

        Args:
            document_id: Document ID

        Returns:
            Finalization result
        """
        now = self._now()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Verify document exists
            doc = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
            if not doc:
                raise ValueError(f"Document not found: {document_id}")

            if doc["status"] == "finalized":
                return {
                    "document_id": document_id,
                    "status": "finalized",
                    "message": "Document was already finalized"
                }

            # Check all blocks are complete
            incomplete = conn.execute(
                "SELECT COUNT(*) FROM blocks WHERE document_id = ? AND status != 'complete'",
                (document_id,)
            ).fetchone()[0]

            if incomplete > 0:
                raise ValueError(f"Cannot finalize: {incomplete} incomplete blocks")

            conn.execute(
                "UPDATE documents SET status = 'finalized', updated_at = ? WHERE id = ?",
                (now, document_id)
            )
            conn.commit()

        return {
            "document_id": document_id,
            "status": "finalized",
            "finalized_at": now,
            "message": "Document finalized successfully"
        }

    # =========================================================================
    # Tool: stream_delete (NEW)
    # =========================================================================
    def stream_delete(self, document_id: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Delete a document and all its blocks.

        Args:
            document_id: Document ID
            confirm: Must be True to confirm deletion

        Returns:
            Deletion result
        """
        if not confirm:
            raise ValueError("Must set confirm=true to delete a document")

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Get document info before deletion
            doc = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (document_id,)
            ).fetchone()
            if not doc:
                raise ValueError(f"Document not found: {document_id}")

            title = doc["title"]

            # Delete recovery contexts for this document's blocks
            conn.execute(
                """DELETE FROM recovery_context WHERE block_id IN
                   (SELECT id FROM blocks WHERE document_id = ?)""",
                (document_id,)
            )

            # Delete blocks
            block_count = conn.execute(
                "SELECT COUNT(*) FROM blocks WHERE document_id = ?",
                (document_id,)
            ).fetchone()[0]

            conn.execute(
                "DELETE FROM blocks WHERE document_id = ?",
                (document_id,)
            )

            # Delete document
            conn.execute(
                "DELETE FROM documents WHERE id = ?",
                (document_id,)
            )

            conn.commit()

        return {
            "document_id": document_id,
            "title": title,
            "blocks_deleted": block_count,
            "message": f"Document '{title}' and {block_count} blocks deleted"
        }

    # =========================================================================
    # Tool: stream_templates (NEW)
    # =========================================================================
    def stream_templates(self) -> Dict[str, Any]:
        """
        List available document templates.

        Returns:
            Dictionary of available templates with their block structures
        """
        templates_info = {}
        for name, tpl in DOCUMENT_TEMPLATES.items():
            templates_info[name] = {
                "schema_type": tpl.get("schema_type", "generic"),
                "blocks": [
                    {"key": b["key"], "type": b["type"]}
                    for b in tpl.get("blocks", [])
                ],
                "block_count": len(tpl.get("blocks", []))
            }

        return {
            "templates": templates_info,
            "count": len(templates_info),
            "message": f"Found {len(templates_info)} available templates"
        }

    # =========================================================================
    # Utility: Save recovery context
    # =========================================================================
    def save_recovery_context(self, document_id: str, block_key: str, partial_content: str):
        """Save partial content for recovery after interruption."""
        now = self._now()

        with sqlite3.connect(self.db_path) as conn:
            block = conn.execute(
                "SELECT id FROM blocks WHERE document_id = ? AND block_key = ?",
                (document_id, block_key)
            ).fetchone()

            if block:
                conn.execute(
                    "UPDATE blocks SET status = 'writing', updated_at = ? WHERE id = ?",
                    (now, block[0])
                )
                context_id = self._generate_id("ctx")
                conn.execute(
                    """INSERT OR REPLACE INTO recovery_context (id, block_id, partial_content, captured_at)
                       VALUES (?, ?, ?, ?)""",
                    (context_id, block[0], partial_content, now)
                )
                conn.commit()


# =============================================================================
# Tool Output Schemas (MCP 2025 spec compliance)
# =============================================================================

OUTPUT_SCHEMAS = {
    "stream_start": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string", "description": "Unique document identifier"},
            "title": {"type": "string"},
            "schema_type": {"type": "string"},
            "status": {"type": "string", "enum": ["draft", "finalized"]},
            "created_at": {"type": "string", "format": "date-time"},
            "template": {"type": "string"},
            "blocks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "key": {"type": "string"},
                        "type": {"type": "string"},
                        "sequence": {"type": "integer"},
                        "status": {"type": "string"}
                    }
                }
            },
            "message": {"type": "string"}
        },
        "required": ["document_id", "title", "status"]
    },
    "stream_write": {
        "type": "object",
        "properties": {
            "block_id": {"type": "string"},
            "block_key": {"type": "string"},
            "sequence": {"type": "integer"},
            "block_type": {"type": "string"},
            "hash": {"type": "string", "description": "SHA-256 content hash (first 16 chars)"},
            "status": {"type": "string", "enum": ["complete", "pending", "writing"]},
            "action": {"type": "string", "enum": ["created", "updated", "completed"]},
            "message": {"type": "string"}
        },
        "required": ["block_id", "block_key", "hash", "status"]
    },
    "stream_status": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "title": {"type": "string"},
            "status": {"type": "string"},
            "resume_from": {"type": "string", "description": "Block key to resume from"},
            "preserved_context": {
                "type": "object",
                "properties": {
                    "block_key": {"type": "string"},
                    "partial_content": {"type": "string"},
                    "captured_at": {"type": "string"}
                }
            },
            "summary": {
                "type": "object",
                "properties": {
                    "total": {"type": "integer"},
                    "complete": {"type": "integer"},
                    "pending": {"type": "integer"},
                    "writing": {"type": "integer"}
                }
            }
        }
    },
    "stream_read": {
        "type": "object",
        "properties": {
            "format": {"type": "string", "enum": ["json", "markdown", "html", "text", "csv", "yaml"]},
            "content": {"type": "string", "description": "Rendered content in requested format"},
            "block_count": {"type": "integer"},
            "document": {"type": "object", "description": "Document metadata (json format only)"},
            "blocks": {"type": "array", "description": "Block data (json format only)"}
        },
        "required": ["format", "block_count"]
    },
    "stream_export": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "format": {"type": "string"},
            "output_path": {"type": "string"},
            "file_size": {"type": "integer"},
            "block_count": {"type": "integer"},
            "message": {"type": "string"}
        },
        "required": ["document_id", "output_path", "file_size"]
    },
    "stream_finalize": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "status": {"type": "string", "enum": ["finalized"]},
            "finalized_at": {"type": "string", "format": "date-time"},
            "message": {"type": "string"}
        },
        "required": ["document_id", "status"]
    },
    "stream_delete": {
        "type": "object",
        "properties": {
            "document_id": {"type": "string"},
            "title": {"type": "string"},
            "blocks_deleted": {"type": "integer"},
            "message": {"type": "string"}
        },
        "required": ["document_id", "blocks_deleted"]
    },
    "stream_templates": {
        "type": "object",
        "properties": {
            "templates": {"type": "object"},
            "count": {"type": "integer"},
            "message": {"type": "string"}
        },
        "required": ["templates", "count"]
    }
}


# =============================================================================
# MCP Server Setup
# =============================================================================

def create_mcp_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("streaming-output")
    streaming = StreamingOutputServer()

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="stream_start",
                description="Initialize a new document for streaming content. Use templates for common document types, or pre-declare custom blocks.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Document title"
                        },
                        "schema_type": {
                            "type": "string",
                            "enum": ["generic", "report", "tasks", "findings", "custom"],
                            "default": "generic",
                            "description": "Type of document"
                        },
                        "template": {
                            "type": "string",
                            "enum": list(DOCUMENT_TEMPLATES.keys()),
                            "description": "Use a pre-defined template (security-audit, code-review, sprint-retrospective, technical-spec, adr, research-report, task-list)"
                        },
                        "blocks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string"},
                                    "type": {"type": "string", "enum": ["section", "task", "finding", "decision", "raw"]}
                                },
                                "required": ["key"]
                            },
                            "description": "Optional list of block declarations (ignored if template specified)"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata"
                        }
                    },
                    "required": ["title"]
                },
                # outputSchema=OUTPUT_SCHEMAS["stream_start"]  # Uncomment when MCP SDK supports this
            ),
            Tool(
                name="stream_write",
                description="Write raw structured content to a block. Atomic and hash-verified. Content is stored as JSON and can be rendered to any format later.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID from stream_start"
                        },
                        "block_key": {
                            "type": "string",
                            "description": "Block identifier (e.g., 'intro', 'findings')"
                        },
                        "content": {
                            "type": "object",
                            "description": "JSON content for the block. Structure depends on block_type."
                        },
                        "block_type": {
                            "type": "string",
                            "enum": ["section", "task", "finding", "decision", "raw"],
                            "default": "section",
                            "description": "Block type determines rendering behavior"
                        },
                        "repair": {
                            "type": "boolean",
                            "default": False,
                            "description": "Allow overwriting completed blocks"
                        }
                    },
                    "required": ["document_id", "block_key", "content"]
                }
            ),
            Tool(
                name="stream_status",
                description="Get document status, find resume point after interruption, verify integrity. Call without document_id to list recent documents and available templates.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID, or omit to list recent documents"
                        },
                        "verify": {
                            "type": "boolean",
                            "default": False,
                            "description": "Verify content hashes"
                        }
                    }
                }
            ),
            Tool(
                name="stream_read",
                description="Render document content in any supported format. Formats: json (raw), markdown, html, text, csv (tasks/findings), yaml.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown", "html", "text", "csv", "yaml"],
                            "default": "json",
                            "description": "Output format"
                        },
                        "blocks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of block keys to include"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="stream_export",
                description="Export document to a file in any supported format.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "File path to save (supports ~ expansion)"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown", "html", "text", "csv", "yaml"],
                            "default": "markdown",
                            "description": "Output format"
                        }
                    },
                    "required": ["document_id", "output_path"]
                }
            ),
            Tool(
                name="stream_finalize",
                description="Mark document as finalized. No more writes allowed after finalization.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="stream_delete",
                description="Delete a document and all its blocks. Requires confirm=true.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID"
                        },
                        "confirm": {
                            "type": "boolean",
                            "default": False,
                            "description": "Must be true to confirm deletion"
                        }
                    },
                    "required": ["document_id", "confirm"]
                }
            ),
            Tool(
                name="stream_templates",
                description="List available document templates with their block structures.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "stream_start":
                result = streaming.stream_start(
                    title=arguments["title"],
                    schema_type=arguments.get("schema_type", "generic"),
                    template=arguments.get("template"),
                    blocks=arguments.get("blocks"),
                    metadata=arguments.get("metadata")
                )
            elif name == "stream_write":
                result = streaming.stream_write(
                    document_id=arguments["document_id"],
                    block_key=arguments["block_key"],
                    content=arguments["content"],
                    block_type=arguments.get("block_type", "section"),
                    repair=arguments.get("repair", False)
                )
            elif name == "stream_status":
                result = streaming.stream_status(
                    document_id=arguments.get("document_id"),
                    verify=arguments.get("verify", False)
                )
            elif name == "stream_read":
                result = streaming.stream_read(
                    document_id=arguments["document_id"],
                    format=arguments.get("format", "json"),
                    blocks=arguments.get("blocks")
                )
            elif name == "stream_export":
                result = streaming.stream_export(
                    document_id=arguments["document_id"],
                    output_path=arguments["output_path"],
                    format=arguments.get("format", "markdown")
                )
            elif name == "stream_finalize":
                result = streaming.stream_finalize(
                    document_id=arguments["document_id"]
                )
            elif name == "stream_delete":
                result = streaming.stream_delete(
                    document_id=arguments["document_id"],
                    confirm=arguments.get("confirm", False)
                )
            elif name == "stream_templates":
                result = streaming.stream_templates()
            else:
                raise ValueError(f"Unknown tool: {name}")

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]

    return server


# =============================================================================
# Transport: stdio (default) or HTTP (for cloud deployment)
# =============================================================================

async def run_stdio():
    """Run the MCP server with stdio transport."""
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


async def run_http(host: str = "0.0.0.0", port: int = 8080):
    """Run the MCP server with HTTP transport (for cloud deployment)."""
    try:
        from mcp.server.streamable_http import StreamableHTTPServer

        server = create_mcp_server()
        http_server = StreamableHTTPServer(server, host=host, port=port)
        print(f"Starting HTTP server on {host}:{port}")
        await http_server.run()
    except ImportError:
        print("HTTP transport requires mcp>=1.0.0 with streamable_http support")
        print("Falling back to stdio transport")
        await run_stdio()


async def main():
    """Run the MCP server with configured transport."""
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if transport == "http":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8080"))
        await run_http(host, port)
    else:
        await run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
