# Stream Write Command

Write content to a document block with automatic persistence.

## Usage

```
/stream-write <block_key> [--doc DOCUMENT_ID] [--append]
```

## Instructions

When the user invokes this command:

### If block_key is provided:

1. Determine the target document:
   - If `--doc` provided, use that document_id
   - Otherwise, use the most recently active document
   - If no active document, prompt to create one or specify ID

2. Check if the block exists:
   - If block was pre-declared at init, use its configuration
   - If new block, ask what type (section, task, finding, decision, raw)

3. Ask the user what content they want to write to this block.

4. Call `stream_write` with the content:

```json
{
  "document_id": "<doc_id>",
  "block_key": "<block_key>",
  "content": "<the_content>",
  "append": false
}
```

5. Confirm the write:
   ```
   Block "findings" written successfully.
   - Content hash: sha256:a1b2c3...
   - Block status: complete
   - Document progress: 2/4 blocks
   ```

### If no block_key provided:

1. Call `stream_status` to get the current document state.

2. Show available blocks and their status:
   ```
   Document: Security Audit Report

   Available blocks:
   1. executive_summary [complete]
   2. findings [pending] ← suggested
   3. recommendations [pending]

   Which block would you like to write to?
   ```

3. Suggest the first pending block as the natural next step.

## Append Mode

Use `--append` to add content to an existing block instead of replacing:

```
/stream-write findings --append
```

This is useful for:
- Adding items to a list
- Appending sections to a growing analysis
- Building up content iteratively

## Examples

**User**: `/stream-write executive_summary`

**Response**:
```
Writing to block "executive_summary" in document "Security Audit Report".

What content should I write to this block?

Tips:
- For sections, provide the full text content
- Content is automatically persisted with hash verification
- You can use --append later to add more content
```

**User**: `/stream-write`

**Response**:
```
Document: Security Audit Report (doc_20260105143052_a1b2c3d4)

Block Status:
  executive_summary  [complete]
  findings           [pending] ← Next
  recommendations    [pending]

Which block would you like to write to? I suggest "findings" as it's the next pending block.
```

**User**: `/stream-write tasks --doc doc_20260104091523`

**Response**:
```
Writing to block "tasks" in document "Sprint Planning Q1".

This block doesn't exist yet. What type should it be?
1. section - General content section
2. task - Task with status tracking
3. finding - Analysis finding with severity
4. raw - Unstructured content

After you choose, tell me what content to write.
```

## Block Types

Each block type has specific structure:

### Section
General content with optional title:
```json
{
  "title": "Optional Section Title",
  "content": "The main content..."
}
```

### Task
Task with status:
```json
{
  "title": "Task description",
  "status": "pending|in_progress|complete|blocked",
  "notes": "Additional context"
}
```

### Finding
Analysis finding with severity:
```json
{
  "title": "Finding title",
  "severity": "critical|high|medium|low|info",
  "description": "Details...",
  "recommendation": "What to do"
}
```

### Decision
Architectural or design decision:
```json
{
  "title": "Decision title",
  "decision": "What was decided",
  "rationale": "Why",
  "alternatives": ["Other options considered"]
}
```

### Raw
Unstructured content:
```json
{
  "content": "Any content..."
}
```
