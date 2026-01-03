Show current progress, identify resume point, and check integrity.

## Usage
`/stream.status <filepath> [--verify]`

## Script
```bash
python scripts/stream_status.py report.md
python scripts/stream_status.py report.md --verify  # Full integrity check
```

## Standard Output
```
Stream Status: report.md

Sections:
  [x] introduction (completed) ✓
  [x] background (completed) ✓
  [ ] analysis (pending) <- RESUME HERE
  [ ] recommendations (pending)
  [ ] conclusion (pending)

Progress: 2/5 sections (40%)
Next section: analysis
```

## With --verify flag (integrity check)
```
Stream Status: report.md

Integrity Check:
  [x] introduction - hash:a1b2c3d4 ✓ valid
  [x] background - hash:e5f6g7h8 ✓ valid
  [!] analysis - CORRUPTED (START without END)
  [ ] recommendations - pending
  [ ] conclusion - pending

⚠️  CORRUPTION DETECTED in section: analysis
    Run `/stream.repair analysis` to fix

Progress: 2/5 sections (40%)
Next section: analysis (requires repair)
```

## Corruption Detection
The status command detects:
- **Orphaned START**: `SECTION_START` exists without matching `SECTION_END`
- **Hash mismatch**: START and END marker hashes don't match
- **Empty section**: Markers exist but no content between them
- **Duplicate sections**: Same section ID appears multiple times

## Use Cases
- Check progress after interruption
- Verify all sections completed before finalizing
- Identify which section to resume from
- Detect corruption with `--verify` flag
