# Stream Status Command

Check document status, find resume point, verify integrity.

## Usage

```
/stream-status [document_id] [--verify]
```

## Instructions

When the user invokes this command:

### If no document_id provided:

1. Call `stream_status()` with no arguments to list recent documents.

2. Display the document list:
   ```
   Recent Documents:
   1. doc_xxx - "Security Audit Report" (draft, updated 2h ago)
   2. doc_yyy - "Q4 Performance Review" (finalized, updated 1d ago)
   3. doc_zzz - "Sprint Tasks" (draft, updated 3d ago)
   ```

3. Ask which document they want to check.

### If document_id provided:

1. Call `stream_status(document_id, verify=true)` if --verify flag, otherwise `stream_status(document_id)`.

2. Analyze the response:

   **If resume_from exists:**
   - There are incomplete blocks
   - Check for preserved_context (partial content from interrupted write)
   - Offer to continue from the resume point

   **If all blocks complete:**
   - Document is ready for finalization or reading
   - Offer to render as Markdown

3. Display status summary:
   ```
   Document: Security Audit Report
   Status: draft

   Blocks:
   - executive_summary: complete
   - findings: PENDING ← Resume here
   - recommendations: pending

   Progress: 1/3 complete

   [Preserved context found - 450 characters of partial content]
   ```

### Recovery Guidance

If preserved_context exists, guide the user:

```
Found interrupted write for block "findings".

Preserved content (first 200 chars):
> "The security analysis identified 3 critical vulnerabilities in the
> authentication module. First, the password hashing uses MD5 which..."

Would you like me to:
1. Continue from this point
2. Start the block fresh
3. View full preserved content
```

## Examples

**User**: `/stream-status`

**Response**:
```
Recent Documents:

1. doc_20260105143052_a1b2c3d4
   "Security Audit Report" - draft
   Updated: 2 hours ago
   Progress: 1/3 blocks complete

2. doc_20260104091523_e5f6g7h8
   "Code Review - auth module" - finalized
   Updated: 1 day ago

Which document would you like to check? (Enter number or document ID)
```

**User**: `/stream-status doc_20260105143052_a1b2c3d4`

**Response**:
```
Document: Security Audit Report
ID: doc_20260105143052_a1b2c3d4
Type: report
Status: draft

Block Status:
  executive_summary  [complete]
  findings            [PENDING] ← Resume here
  recommendations    [pending]

Summary: 1 of 3 blocks complete

RECOVERY AVAILABLE:
Block "findings" has preserved context from interrupted write.
Partial content: "The security analysis identified 3 critical..."

Ready to continue? I'll pick up where we left off.
```
