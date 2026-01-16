# Streaming Output MCP

A simple, reliable MCP for streaming structured content to persistent SQLite storage with automatic session break recovery.

## Core Insight

**The content IS the state.** Don't track metadata about work—store the actual work. Every `stream_write` is automatically persistent. No sessions, no checkpoints, no events—just documents and blocks.

## Tools

### stream_start

Initialize a new document for streaming content.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Document title |
| `schema_type` | string | No | Type: `generic`, `report`, `tasks`, `findings`, `custom` |
| `blocks` | array | No | Pre-declared blocks: `[{key, type}]` |
| `metadata` | object | No | Optional metadata JSON |

**Example:**
```json
{
  "title": "Security Audit Report",
  "schema_type": "findings",
  "blocks": [
    {"key": "summary", "type": "section"},
    {"key": "critical_findings", "type": "finding"},
    {"key": "recommendations", "type": "section"}
  ]
}
```

**Returns:**
```json
{
  "document_id": "doc_20260105143052_a1b2c3d4",
  "title": "Security Audit Report",
  "schema_type": "findings",
  "status": "draft",
  "blocks": [
    {"id": "blk_...", "key": "summary", "type": "section", "status": "pending"}
  ]
}
```

---

### stream_write

Write content to a block. Atomic and verified.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | string | Yes | Document ID from stream_start |
| `block_key` | string | Yes | Block identifier (e.g., "intro") |
| `content` | object | Yes | JSON content for the block |
| `block_type` | string | No | `section`, `task`, `finding`, `decision`, `raw` |
| `repair` | boolean | No | Allow overwriting completed blocks |

**Block Type Schemas:**

**section:**
```json
{"title": "Introduction", "body": "Content text..."}
```

**task:**
```json
{"id": "T-001", "title": "Implement auth", "status": "pending", "assignee": "Alice", "notes": "..."}
```

**finding:**
```json
{"id": "F-001", "severity": "ERROR", "description": "SQL injection", "evidence": "...", "recommendation": "..."}
```

**decision:**
```json
{"id": "ADR-001", "title": "Use PostgreSQL", "context": "...", "decision": "...", "rationale": "...", "alternatives": ["MySQL", "SQLite"]}
```

**Returns:**
```json
{
  "block_id": "blk_20260105143055_e5f6g7h8",
  "block_key": "summary",
  "hash": "abc123def456...",
  "status": "complete",
  "action": "created"
}
```

---

### stream_status

Get document status, find resume point after interruption, verify integrity.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | string | No | Document ID, or omit to list recent documents |
| `verify` | boolean | No | Verify content hashes |

**Example (list documents):**
```json
{}
```

**Example (check specific document):**
```json
{"document_id": "doc_20260105143052_a1b2c3d4", "verify": true}
```

**Returns (with resume info):**
```json
{
  "document_id": "doc_...",
  "title": "Security Audit Report",
  "status": "draft",
  "blocks": [
    {"key": "summary", "status": "complete", "hash": "..."},
    {"key": "critical_findings", "status": "pending"}
  ],
  "summary": {"total": 3, "complete": 1, "pending": 2},
  "resume_from": "critical_findings",
  "preserved_context": {
    "block_key": "critical_findings",
    "partial_content": "Found 3 SQL injection vulnerabilities in...",
    "captured_at": "2026-01-05T14:35:00Z"
  }
}
```

---

### stream_read

Read document content as JSON or render to Markdown.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | string | Yes | Document ID |
| `format` | string | No | `json` or `markdown` (default: json) |
| `blocks` | array | No | Block keys to include (default: all) |

**Example:**
```json
{"document_id": "doc_...", "format": "markdown"}
```

**Returns (markdown):**
```json
{
  "format": "markdown",
  "content": "# Security Audit Report\n\n> **Document ID**: doc_...\n...",
  "block_count": 3
}
```

---

## Session Break Recovery

The MCP automatically tracks incomplete writes and preserves partial content.

### Recovery Flow

```
Session 1 (interrupted):
  stream_write("analysis", content) → interrupted mid-write

Session 2 (recovery):
  stream_status(doc_id)
    → returns: {resume_from: "analysis", preserved_context: "partial content..."}

  Agent reads preserved_context, continues from that point
  stream_write("analysis", continued_content, repair=true)
```

### Block States

| State | Meaning |
|-------|---------|
| `pending` | Declared but not yet written |
| `writing` | Write started but interrupted |
| `complete` | Successfully written with verified hash |

---

## Database Schema

Location: `~/.claude/streaming-output/streams.db`

```sql
-- Documents: containers for streamed content
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    schema_type TEXT DEFAULT 'generic',
    status TEXT NOT NULL DEFAULT 'draft',  -- draft, complete, finalized
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT
);

-- Blocks: atomic content units
CREATE TABLE blocks (
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
    UNIQUE (document_id, block_key)
);

-- Context preservation for interrupted writes
CREATE TABLE recovery_context (
    id TEXT PRIMARY KEY,
    block_id TEXT NOT NULL,
    partial_content TEXT,
    captured_at TEXT NOT NULL
);
```

---

## Installation

### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "streaming-output": {
      "command": "python3",
      "args": ["/path/to/streaming-output/server.py"]
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "streaming-output": {
      "command": "python3",
      "args": ["/path/to/streaming-output/server.py"]
    }
  }
}
```

---

## Dependencies

- Python 3.10+
- `mcp` package (`pip install mcp`)
- SQLite (built-in)
