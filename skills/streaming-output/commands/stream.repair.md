Fix corrupted or partial sections.

## Usage
`/stream.repair <filepath> <section-id> [--strategy <strategy>]`

## Strategies
- `remove` (default): Remove partial content, reset section to pending
- `complete`: Attempt to add missing END marker (use with caution)
- `backup`: Create backup before repair

## Workflow
1. Create backup of current file (if --strategy backup)
2. Locate corrupted section
3. Remove content from `SECTION_START` to end of partial content
4. Update section status to `pending`
5. Report repair results

## Script
```bash
python scripts/stream_repair.py report.md analysis --strategy remove
```

## Output
```
Repair Report: report.md

Section: analysis
Issue: Orphaned SECTION_START (no SECTION_END found)
Strategy: remove
Action: Removed 847 characters of partial content

Before:
  <!-- SECTION_START: analysis | hash:null -->
  ## Analysis

  Partial content here...
  [truncated]

After:
  Section 'analysis' reset to pending status

Backup created: report.md.backup.20240115-103045

Ready to regenerate: /stream.write analysis
```

## When to Use
- `/stream.status --verify` detects orphaned SECTION_START markers
- Hash mismatch between START and END markers
- Empty section content detected
- After context compaction truncated a write operation

## After Repair
Run `/stream.write <section-id>` to regenerate the repaired section.
