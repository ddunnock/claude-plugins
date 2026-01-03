Write a single section to the file with markers and integrity verification.

## Usage
`/stream.write <section-id>`

## Workflow
1. Check section exists in plan and is pending
2. Generate content for section
3. Compute content hash
4. Write to temporary location first
5. Validate write completed (check for SECTION_END marker)
6. Append to main file with `SECTION_START` and `SECTION_END` markers
7. Update section status to `completed` with hash

## Script
```bash
python scripts/stream_write.py write report.md introduction "Your content here..."
```

## Markers in file
```markdown
<!-- SECTION_START: introduction | hash:a1b2c3d4 -->
## Introduction

Your introduction content here...

<!-- SECTION_END: introduction | hash:a1b2c3d4 -->
```

## Write Verification
After each write, the skill automatically verifies:
1. `SECTION_START` marker exists
2. `SECTION_END` marker exists
3. Hashes in both markers match
4. Content between markers is non-empty

If verification fails, the write is flagged and `/stream.repair` is recommended.

## Important
- Write ONE section at a time
- Verify success before proceeding to next section
- Hash in START and END markers must match (integrity check)
- If interrupted mid-section, run `/stream.status --verify` to detect corruption
