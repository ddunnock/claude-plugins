# Stream Read Command

Read document content as JSON or render to Markdown.

## Usage

```
/stream-read [document_id] [--format json|markdown] [--blocks block1,block2,...]
```

## Instructions

When the user invokes this command:

### If no document_id provided:

1. Call `stream_status()` to list recent documents.
2. Ask which document to read.

### Reading the document:

1. Determine format preference:
   - `markdown` (default) - Human-readable rendered output
   - `json` - Structured data for programmatic use

2. Call `stream_read(document_id, format, blocks)`:
   ```json
   {
     "document_id": "doc_xxx",
     "format": "markdown",
     "blocks": ["summary", "recommendations"]  // optional
   }
   ```

3. Display the content appropriately:

   **For Markdown:**
   - Display the rendered content directly
   - Note any pending/incomplete blocks

   **For JSON:**
   - Show the structured output
   - Can be used for export or further processing

### Selective Reading

If user wants specific blocks:
```
/stream-read doc_xxx --blocks summary,recommendations
```

Only those blocks will be included in the output.

## Examples

**User**: `/stream-read doc_20260105143052_a1b2c3d4`

**Response**:
```markdown
# Security Audit Report

> **Document ID**: doc_20260105143052_a1b2c3d4
> **Type**: report
> **Status**: draft
> **Updated**: 2026-01-05T16:30:00Z

## Executive Summary

This security audit was conducted on the authentication module
of the web application. We identified 3 critical vulnerabilities
that require immediate attention.

## Findings _(pending)_

## Recommendations _(pending)_
```

**User**: `/stream-read doc_xxx --format json`

**Response**:
```json
{
  "document": {
    "id": "doc_xxx",
    "title": "Security Audit Report",
    "schema_type": "report",
    "status": "draft"
  },
  "blocks": [
    {
      "key": "executive_summary",
      "type": "section",
      "status": "complete",
      "content": {
        "title": "Executive Summary",
        "body": "This security audit was conducted..."
      }
    },
    {
      "key": "findings",
      "type": "finding",
      "status": "pending",
      "content": null
    }
  ]
}
```

**User**: `/stream-read doc_xxx --blocks executive_summary`

**Response**:
```markdown
# Security Audit Report

> **Document ID**: doc_xxx

## Executive Summary

This security audit was conducted on the authentication module
of the web application. We identified 3 critical vulnerabilities
that require immediate attention.

---
(Showing 1 of 3 blocks)
```
