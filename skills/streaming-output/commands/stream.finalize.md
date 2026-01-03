Strip markers and validate completeness.

## Usage
`/stream.finalize <filepath> [--output <output-filepath>]`

## Workflow
1. Run full integrity check
2. Verify all sections completed
3. Verify all hashes valid
4. Remove `SECTION_START` and `SECTION_END` markers
5. Remove YAML frontmatter stream metadata
6. Validate no incomplete markers remain
7. Write to output file (or overwrite in place)

## Script
```bash
python scripts/stream_cleanup.py report.md --output final_report.md
```

## Pre-finalize Validation
```
Finalize Check: report.md

Sections:
  [x] introduction ✓
  [x] background ✓
  [x] analysis ✓
  [x] recommendations ✓
  [x] conclusion ✓

All sections complete: YES
All hashes valid: YES
Ready to finalize: YES

Finalizing...
Output written to: final_report.md
Markers removed: 10
Lines in final document: 1,247
```

## If Validation Fails
```
Finalize Check: report.md

⚠️  CANNOT FINALIZE - Issues detected:

  [ ] recommendations - PENDING (not written)
  [!] conclusion - CORRUPTED (hash mismatch)

Fix required before finalization:
1. /stream.write recommendations
2. /stream.repair conclusion
```

## Before/After
**Before**:
```markdown
---
stream_plan:
  sections: [...]
---
<!-- SECTION_START: intro | hash:a1b2c3d4 -->
## Introduction
Content...
<!-- SECTION_END: intro | hash:a1b2c3d4 -->
```

**After**:
```markdown
## Introduction
Content...
```

## Pre-finalize Checklist
- Run `/stream.status --verify` to confirm all sections complete
- Check for any sections with hash mismatches
- Address any corrupted sections with `/stream.repair` before finalizing
