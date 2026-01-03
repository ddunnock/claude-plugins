Initialize an output file with a section plan for streaming long-form content.

## Usage
`/stream.init <filepath> --sections "<comma-separated-list>" [--template <template-name>]`

## Workflow
1. Create output file (or detect existing)
2. Write header with section plan as YAML frontmatter
3. Generate content hash placeholder for integrity checking
4. Present checklist for tracking

## Templates (optional)
- `bspec` - 15-section B-SPEC structure
- `report` - Standard report structure
- `spec` - Generic specification structure

## Example
```bash
# Standard initialization
/stream.init report.md --sections "introduction,background,analysis,recommendations,conclusion"

# B-SPEC template (pre-defined 15 sections)
/stream.init b-spec-010.md --template bspec
```

## Output file structure
```markdown
---
stream_plan:
  version: "2.0"
  sections:
    - id: introduction
      status: pending
      hash: null
    - id: background
      status: pending
      hash: null
    - id: analysis
      status: pending
      hash: null
  created: 2024-01-15T10:30:00
  last_modified: null
  integrity_check: true
---

# Report

<!-- Content will be streamed below -->
```

## Script
```bash
python scripts/stream_write.py init report.md \
  --sections "introduction,background,analysis,recommendations,conclusion"
```

After initialization, use `/stream.write` to write each section.
