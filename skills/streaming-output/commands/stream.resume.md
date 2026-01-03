Continue writing from the last incomplete section.

## Usage
`/stream.resume <filepath>`

## Workflow
1. Run status with verification to find resume point
2. Check for corrupted sections (repair if needed)
3. Read existing content for context
4. Continue with `/stream.write` for next pending section

## Script
```bash
python scripts/stream_status.py report.md --resume
```

## Output
```
Resume Point: report.md

Last completed: background
Next pending: analysis

Context from previous sections loaded (2,450 tokens)
Ready to write: analysis

Command: /stream.write analysis
```

## If Corruption Detected
```
Resume Point: report.md

⚠️  CORRUPTION DETECTED
Section 'analysis' has incomplete markers.

Recommended action:
1. Run `/stream.repair analysis` to remove partial content
2. Then run `/stream.write analysis` to regenerate

Command: /stream.repair analysis
```

## Recovery Scenarios

### Scenario 1: Context limit hit mid-section
The section has `SECTION_START` but no `SECTION_END`:

**Recovery**:
1. `/stream.status --verify` detects incomplete section
2. `/stream.repair analysis` removes partial content
3. `/stream.write analysis` regenerates the section

### Scenario 2: Session ended between sections
All written sections have both markers.

**Recovery**:
1. `/stream.resume` finds next pending section
2. Continue with `/stream.write`
