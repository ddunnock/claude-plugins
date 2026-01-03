---
name: streaming-output
description: >
  Stream long-form content to markdown files with resume capability. Writes content incrementally
  with section markers, enabling recovery if context limits are hit. Use when generating long
  documents, reports, or any content that may exceed output limits. Commands: init, write, status,
  resume, finalize.
---

# Streaming Output

Write long-form content incrementally to markdown files with automatic resume capability. If context limits are hit mid-generation, work persists and can be continued.

## Commands

| Command | Purpose |
|---------|---------|
| `/stream.init` | Initialize output file with section plan |
| `/stream.write` | Write next section to file |
| `/stream.status` | Show progress, detect resume point |
| `/stream.resume` | Continue from last completed section |
| `/stream.finalize` | Strip markers, validate completeness |

---

## Quick Start

```bash
# 1. Initialize with a plan
/stream.init report.md --sections "intro,methodology,findings,conclusion"

# 2. Write sections (repeat for each)
/stream.write intro
/stream.write methodology
# ... if interrupted, resume later with:
/stream.resume

# 3. Finalize when complete
/stream.finalize
```

---

## /stream.init

Initialize an output file with a section plan.

**Usage**: `/stream.init <filepath> --sections "<comma-separated-list>"`

**Workflow**:
1. Create output file (or detect existing)
2. Write header with section plan as YAML frontmatter
3. Present checklist for tracking

**Example**:
```bash
python scripts/stream_write.py init report.md \
  --sections "introduction,background,analysis,recommendations,conclusion"
```

**Output file structure**:
```markdown
---
stream_plan:
  sections:
    - id: introduction
      status: pending
    - id: background
      status: pending
    - id: analysis
      status: pending
  created: 2024-01-15T10:30:00
---

# Report

<!-- Content will be streamed below -->
```

---

## /stream.write

Write a single section to the file with markers.

**Usage**: `/stream.write <section-id>`

**Workflow**:
1. Check section exists in plan and is pending
2. Generate content for section
3. Append with `SECTION_START` and `SECTION_END` markers
4. Update section status to `completed`

**Script**:
```bash
python scripts/stream_write.py write report.md introduction "Your content here..."
```

**Markers in file**:
```markdown
<!-- SECTION_START: introduction -->
## Introduction

Your introduction content here...

<!-- SECTION_END: introduction -->
```

**Important**: Write ONE section at a time. Verify success before proceeding.

---

## /stream.status

Show current progress and identify resume point.

**Usage**: `/stream.status <filepath>`

**Script**:
```bash
python scripts/stream_status.py report.md
```

**Output**:
```
Stream Status: report.md

Sections:
  [x] introduction (completed)
  [x] background (completed)
  [ ] analysis (pending) <- RESUME HERE
  [ ] recommendations (pending)
  [ ] conclusion (pending)

Progress: 2/5 sections (40%)
Next section: analysis
```

---

## /stream.resume

Continue writing from the last incomplete section.

**Usage**: `/stream.resume <filepath>`

**Workflow**:
1. Run status to find resume point
2. Read existing content for context
3. Continue with `/stream.write` for next pending section

**Script**:
```bash
python scripts/stream_status.py report.md --resume
```

This outputs the section ID to resume, which you then write.

---

## /stream.finalize

Strip markers and validate completeness.

**Usage**: `/stream.finalize <filepath>`

**Workflow**:
1. Verify all sections completed
2. Remove `SECTION_START` and `SECTION_END` markers
3. Remove YAML frontmatter stream metadata
4. Validate no incomplete markers remain

**Script**:
```bash
python scripts/stream_cleanup.py report.md --output final_report.md
```

**Before**:
```markdown
---
stream_plan:
  sections: [...]
---
<!-- SECTION_START: intro -->
## Introduction
Content...
<!-- SECTION_END: intro -->
```

**After**:
```markdown
## Introduction
Content...
```

---

## Recovery Scenarios

### Scenario 1: Context limit hit mid-section

The section has `SECTION_START` but no `SECTION_END`:
```markdown
<!-- SECTION_START: analysis -->
## Analysis

Partial content here...
[truncated - no SECTION_END]
```

**Recovery**:
1. `/stream.status` detects incomplete section
2. Delete partial content manually or via script
3. `/stream.write analysis` to regenerate

### Scenario 2: Session ended between sections

All written sections have both markers:
```markdown
<!-- SECTION_END: background -->
```

**Recovery**:
1. `/stream.resume` finds next pending section
2. Continue with `/stream.write`

---

## Workflow Checklist

Copy and track progress:

```
Stream Progress:
- [ ] Initialize file with section plan
- [ ] Write each section (one at a time):
  - [ ] Section 1: ___________
  - [ ] Section 2: ___________
  - [ ] Section 3: ___________
  - [ ] ...
- [ ] Run status to verify all complete
- [ ] Finalize to strip markers
```

---

## Best Practices

1. **Plan sections upfront**: Define all sections before starting
2. **One section at a time**: Write, verify, then proceed
3. **Check status often**: Especially after interruptions
4. **Keep sections reasonable**: 500-2000 words per section works well
5. **Save context**: Don't hold generated content in memory; write immediately

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `stream_write.py` | Init and write operations | `python scripts/stream_write.py <command> <args>` |
| `stream_status.py` | Progress and resume detection | `python scripts/stream_status.py <filepath>` |
| `stream_cleanup.py` | Finalize and strip markers | `python scripts/stream_cleanup.py <filepath>` |

Run any script with `--help` for detailed options.
