---
name: streaming-output-mcp
description: >
  Stream structured content to persistent SQLite storage with automatic session break recovery.
  Core principle: The content IS the state. Every stream_write is automatically persistent.
  Supports multi-format export (Markdown, HTML, JSON, YAML, CSV, Text) and 7 document templates.
  Commands: /stream-init, /stream-status, /stream-read, /stream-write, /stream-export.
  ALWAYS call stream_status after session breaks to check for resume_from and preserved_context.
---

# Streaming Output MCP Skill

Agent instructions for using the streaming-output MCP to produce persistent, recoverable output.

## Overview

This skill enables you to stream structured content to persistent SQLite storage with automatic session break recovery. Use it when producing reports, analysis results, task lists, or any structured output that needs to survive session interruptions.

**Core Principle**: The content IS the state. Every `stream_write` is automatically persistent.

**Version 2.0 Features**:
- 7 pre-built document templates (security-audit, code-review, sprint-retrospective, etc.)
- 6 export formats (Markdown, HTML, JSON, YAML, CSV, Plain Text)
- Document finalization with completion verification
- File export with path expansion

## First Action Protocol

**CRITICAL**: Always follow this protocol at the start of any streaming task.

```
IF you have a document_id (from previous session or user):
    1. Call stream_status(document_id) FIRST
    2. Check for resume_from field
    3. If preserved_context exists, READ IT and CONTINUE from that point
    4. Do NOT restart blocks from scratch

IF you don't have a document_id:
    1. Call stream_start() to create new document
    2. Optionally use a template for structure
    3. Begin writing blocks in sequence
```

### Why This Matters

Session breaks happen. When they do:
- The MCP knows which blocks are incomplete
- Partial content may be preserved in `preserved_context`
- You should CONTINUE from the interruption point, not restart

## Document Templates

Use templates for common document types with pre-defined structure:

| Template | Use Case | Pre-declared Blocks |
|----------|----------|---------------------|
| `security-audit` | Security assessments | executive_summary, scope, findings, recommendations |
| `code-review` | PR/code reviews | summary, critical_issues, suggestions, approval_status |
| `sprint-retrospective` | Sprint retros | what_went_well, improvements, action_items |
| `technical-spec` | Technical specs | overview, requirements, architecture, implementation_plan |
| `adr` | Architecture decisions | context, decision, consequences, alternatives |
| `research-report` | Research docs | abstract, methodology, findings, conclusions |
| `task-list` | Task tracking | No pre-declared blocks (dynamic) |

**To use a template:**
```json
{
  "title": "Q4 Security Audit",
  "template": "security-audit"
}
```

**List available templates:**
```json
stream_templates({})
```

## Tool Reference

### stream_start

Initialize a new document.

```json
// Minimal
{"title": "Code Review Report"}

// With template
{
  "title": "Security Assessment",
  "template": "security-audit"
}

// Custom structure
{
  "title": "Custom Report",
  "schema_type": "report",
  "blocks": [
    {"key": "summary", "type": "section"},
    {"key": "findings", "type": "finding"}
  ]
}
```

### stream_write

Write content to a block. Each write is atomic and SHA-256 verified.

```json
{
  "document_id": "doc_...",
  "block_key": "summary",
  "content": {
    "title": "Executive Summary",
    "body": "This audit identified 3 critical vulnerabilities..."
  },
  "block_type": "section"
}
```

**Block Types:**

| Type | When to Use | Required Fields |
|------|-------------|-----------------|
| `section` | Narrative content | title, body |
| `task` | Actionable items | id, title, status |
| `finding` | Analysis results | id, severity, description |
| `decision` | ADR-style decisions | id, title, decision, rationale |
| `raw` | Arbitrary JSON | content |

**Content Schemas:**

```json
// section
{"title": "...", "body": "..."}

// task
{"id": "T-001", "title": "...", "status": "pending|in_progress|complete", "assignee": "...", "notes": "..."}

// finding
{"id": "F-001", "severity": "critical|high|medium|low|info", "description": "...", "evidence": "...", "recommendation": "..."}

// decision
{"id": "ADR-001", "title": "...", "context": "...", "decision": "...", "rationale": "...", "alternatives": [...]}
```

### stream_status

Check document state. **Always call after session breaks.**

```json
// List recent documents
{}

// Check specific document with verification
{"document_id": "doc_...", "verify": true}
```

**Response Fields:**
```json
{
  "resume_from": "findings",           // ← Start here
  "preserved_context": {
    "block_key": "findings",
    "partial_content": "Found 3 SQL injection..."
  },
  "summary": {
    "total": 5,
    "complete": 2,
    "pending": 3
  }
}
```

### stream_read

Read document content in various formats.

```json
// As JSON
{"document_id": "doc_...", "format": "json"}

// As Markdown
{"document_id": "doc_...", "format": "markdown"}

// Specific blocks
{"document_id": "doc_...", "format": "markdown", "blocks": ["summary", "recommendations"]}
```

### stream_export (NEW)

Export document to a file.

```json
{
  "document_id": "doc_...",
  "format": "html",
  "output_path": "~/Documents/report.html"
}
```

**Supported Formats:**
- `markdown` - Clean Markdown with headers
- `html` - Styled HTML with embedded CSS
- `json` - Full structured data
- `text` - Plain text without formatting
- `yaml` - YAML representation
- `csv` - Tabular format (best for tasks/findings)

### stream_finalize (NEW)

Mark document as complete after all blocks are written.

```json
{"document_id": "doc_..."}
```

Returns verification of completion status.

### stream_delete (NEW)

Delete a document and all its blocks.

```json
{"document_id": "doc_..."}
```

### stream_templates (NEW)

List available document templates.

```json
{}  // Returns all 7 templates with their structure
```

## Recovery Workflow

### Scenario 1: Session Break with Preserved Context

```
1. Call stream_status(document_id)
2. Response: resume_from: "analysis", preserved_context: "The security analysis..."
3. Action: Read preserved_context, CONTINUE from that point
4. Call stream_write("analysis", {complete_content}, repair=true)
```

### Scenario 2: Session Break without Preserved Context

```
1. Call stream_status(document_id)
2. Response: resume_from: "analysis", no preserved_context
3. Action: Check complete blocks, re-analyze source, write fresh
```

### Scenario 3: User Wants Previous Work

```
User: "Continue the security report from yesterday"
1. stream_status() - list recent documents
2. Identify by title/date
3. stream_status(document_id) - get details
4. Follow resume_from to continue
```

## Anti-Patterns

**DO NOT:**

1. Skip status check after session break
2. Restart blocks from scratch when preserved_context exists
3. Write multiple blocks without status checks
4. Use wrong content structure for block type
5. Forget `repair=true` when continuing interrupted blocks

## Workflow Examples

### Example 1: Using a Template

```
1. stream_start(title="Q4 Security Audit", template="security-audit")
   → Creates doc with: executive_summary, scope, findings, recommendations

2. stream_write(doc_xxx, "executive_summary", {title: "...", body: "..."})
3. stream_write(doc_xxx, "scope", {title: "...", body: "..."})
4. stream_write(doc_xxx, "findings", {severity: "critical", ...})
5. stream_write(doc_xxx, "recommendations", {title: "...", body: "..."})

6. stream_finalize(doc_xxx)
   → Document finalized

7. stream_export(doc_xxx, format="html", output_path="~/reports/q4-audit.html")
   → Exported to file
```

### Example 2: Resume After Interruption

```
User: "Continue the security report"

1. stream_status()
   → Lists recent docs, find "Security Audit"

2. stream_status("doc_xxx")
   → resume_from: "findings", preserved_context: {partial: "Scanned 45/120..."}

3. Read preserved_context, note endpoint 45

4. Continue from endpoint 46

5. stream_write(doc_xxx, "findings", {complete}, repair=true)
```

### Example 3: Multi-Format Export

```
1. Complete document with stream_write calls

2. stream_read(doc_xxx, format="markdown")
   → Preview in chat

3. stream_export(doc_xxx, format="html", output_path="~/report.html")
   → HTML file for sharing

4. stream_export(doc_xxx, format="json", output_path="~/backup.json")
   → JSON backup for archival
```

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/stream-init` | Initialize a new document |
| `/stream-status` | Check document status and resume point |
| `/stream-read` | Read document content |
| `/stream-write` | Write content to a block |
| `/stream-export` | Export document to file |

## Database Location

Documents are stored in: `~/.claude/streaming-output/streams.db`

This SQLite database persists across sessions.

## Export Format Examples

### Markdown Output
```markdown
# Document Title
*Status: finalized | Created: 2026-01-14*

## Executive Summary
Content here...

## Findings
- **[CRITICAL]** Finding 1
- **[HIGH]** Finding 2
```

### HTML Output
Styled HTML with:
- Embedded CSS (no external dependencies)
- Severity badges for findings
- Status indicators
- Print-friendly formatting

### CSV Output
```csv
block_key,type,title,severity,status
finding_1,finding,SQL Injection,critical,
task_1,task,Fix auth,in_progress,
```
