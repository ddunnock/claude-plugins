# Stream Export Command

Export a document to a file in various formats.

## Usage

```
/stream-export [document_id] [--format FORMAT] [--output PATH]
```

## Instructions

When the user invokes this command:

### 1. Identify the document

- If `document_id` provided, use it
- Otherwise, show recent documents and ask which to export:
  ```
  Recent Documents:
  1. doc_xxx - "Security Audit Report" (draft)
  2. doc_yyy - "Sprint Tasks" (finalized)

  Which document would you like to export?
  ```

### 2. Choose export format

Available formats:
- **markdown** (default) - Clean Markdown document
- **html** - Styled HTML with embedded CSS
- **json** - Full structured data
- **text** - Plain text without formatting
- **yaml** - YAML representation
- **csv** - Tabular data (best for tasks/findings)

If not specified, ask:
```
Export format options:
1. markdown - Clean Markdown (recommended)
2. html - Styled HTML page
3. json - Raw structured data
4. text - Plain text
5. yaml - YAML format
6. csv - Spreadsheet format

Which format? [default: markdown]
```

### 3. Determine output path

- If `--output PATH` provided, use it
- Otherwise, suggest a default based on document title:
  ```
  Suggested output: ~/Documents/security-audit-report.md

  Save to this location, or specify a different path?
  ```

### 4. Call stream_export

```json
{
  "document_id": "<doc_id>",
  "format": "markdown",
  "output_path": "~/Documents/report.md"
}
```

### 5. Confirm export

```
Document exported successfully!

File: /Users/name/Documents/security-audit-report.md
Format: markdown
Size: 4.2 KB

The file contains:
- 3 sections (executive_summary, findings, recommendations)
- 5 findings (2 critical, 2 high, 1 medium)
- Full document metadata
```

## Format Details

### Markdown
Best for documentation, READMEs, and sharing. Preserves structure with headers and formatting.

### HTML
Includes embedded CSS for standalone viewing in browsers. Good for sharing with non-technical stakeholders.

### JSON
Full data export including metadata, timestamps, and raw content. Best for programmatic processing or archival.

### Text
Minimal formatting, suitable for terminal output or simple text editors.

### YAML
Human-readable structured format. Good for configuration or data interchange.

### CSV
Tabular format for spreadsheets. Best with task lists or findings that have consistent fields.

## Examples

**User**: `/stream-export`

**Response**:
```
Recent Documents:

1. doc_20260105143052_a1b2c3d4
   "Security Audit Report" - draft (3 blocks)

2. doc_20260104091523_e5f6g7h8
   "Code Review - auth module" - finalized

Which document would you like to export?
```

**User**: `/stream-export doc_20260105143052 --format html --output ~/reports/audit.html`

**Response**:
```
Exporting "Security Audit Report" to HTML...

Export complete!

File: /Users/name/reports/audit.html
Format: HTML (styled)
Size: 8.3 KB

Contents:
- Executive Summary
- 5 Findings (with severity badges)
- Recommendations

Open in browser: file:///Users/name/reports/audit.html
```

**User**: `/stream-export --format csv`

**Response**:
```
Which document would you like to export?

1. "Sprint Tasks Q1" - 12 tasks (ideal for CSV)
2. "Security Audit" - 5 findings (works for CSV)
3. "Architecture Doc" - 4 sections (less suitable)

Note: CSV format works best with documents containing
tasks or findings with consistent fields.
```

## Quick Export Shortcuts

For common workflows:

```
/stream-export --format markdown    # Quick markdown export
/stream-export --format json        # Full data backup
/stream-export --format html        # Shareable report
```

## Notes

- Draft documents can be exported but will be marked as "DRAFT"
- Finalized documents include a completeness indicator
- Large documents may take a moment to render
- CSV exports may flatten nested structures
