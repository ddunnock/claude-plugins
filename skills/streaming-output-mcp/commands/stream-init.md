# Stream Init Command

Initialize a new streaming document for persistent output.

## Usage

```
/stream-init [title] [--type TYPE] [--blocks BLOCKS]
```

## Instructions

When the user invokes this command:

1. If a title is provided, use it. Otherwise, ask what document they want to create.

2. Determine the appropriate schema_type:
   - `report` - For structured reports with sections
   - `tasks` - For task tracking
   - `findings` - For analysis results
   - `generic` - For freeform content

3. Ask if they want to pre-declare blocks (recommended for structured documents):
   - For reports: summary, analysis, recommendations
   - For findings: overview, critical, warnings, info
   - For tasks: typically no pre-declaration needed

4. Call `stream_start` with the configuration:

```json
{
  "title": "<document_title>",
  "schema_type": "<type>",
  "blocks": [
    {"key": "section_name", "type": "section|task|finding|decision|raw"}
  ]
}
```

5. Store the returned `document_id` for subsequent operations.

6. Inform the user:
   - Document ID (they may need this for recovery)
   - Pre-declared blocks (if any)
   - Next steps (start writing with stream_write)

## Examples

**User**: `/stream-init Security Audit Report`

**Response**:
```
Created document: Security Audit Report
Document ID: doc_20260105143052_a1b2c3d4
Type: report

Pre-declared blocks:
- executive_summary (section) - pending
- findings (finding) - pending
- recommendations (section) - pending

Ready to write. Use stream_write to add content to each block.
```

**User**: `/stream-init`

**Response**:
```
What document would you like to create?

Options:
1. Report (structured sections)
2. Task list
3. Findings/Analysis
4. Custom document

What title should I use?
```
