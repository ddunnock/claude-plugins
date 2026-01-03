---
name: streaming-output
description: >
  Stream long-form content to markdown files with resume capability. Writes content incrementally
  with section markers, enabling recovery if context limits are hit. Use when generating long
  documents, reports, specifications, or any content that may exceed output limits.
  Commands: init, write, status, resume, finalize, repair.
triggers:
  - Long document generation (>1000 lines expected)
  - B-SPEC or specification writing
  - Multi-section reports
  - Any task where context compaction may occur mid-generation
  - User explicitly requests streaming output
---

# Streaming Output

Write long-form content incrementally to markdown files with automatic resume capability. If context limits are hit mid-generation, work persists and can be continued.

## ⚠️ MANDATORY USE CASES

**ALWAYS use this skill when:**
- Generating B-SPEC documents (typically 1,500-4,000 lines)
- Writing any document expected to exceed 1,000 lines
- Creating multi-section specifications or reports
- Context compaction has already occurred in the conversation
- The continuation prompt mentions streaming-output

**DO NOT use manual heredoc appends (`cat >> file << 'EOF'`) for long documents.** This pattern fails silently when context compaction occurs mid-write, causing content corruption that is difficult to detect and repair.

---

## Commands

| Command | Purpose |
|---------|---------|
| `/stream.init` | Initialize output file with section plan |
| `/stream.write` | Write next section to file |
| `/stream.status` | Show progress, detect resume point, check integrity |
| `/stream.resume` | Continue from last completed section |
| `/stream.repair` | Fix corrupted/partial sections |
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

**Usage**: `/stream.init <filepath> --sections "<comma-separated-list>" [--template <template-name>]`

**Workflow**:
1. Create output file (or detect existing)
2. Write header with section plan as YAML frontmatter
3. Generate content hash placeholder for integrity checking
4. Present checklist for tracking

**Templates** (optional):
- `bspec` - 15-section B-SPEC structure
- `report` - Standard report structure
- `spec` - Generic specification structure

**Example**:
```bash
# Standard initialization
python scripts/stream_write.py init report.md \
  --sections "introduction,background,analysis,recommendations,conclusion"

# B-SPEC template (pre-defined 15 sections)
python scripts/stream_write.py init b-spec-010.md --template bspec
```

**Output file structure**:
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

---

## /stream.write

Write a single section to the file with markers and integrity verification.

**Usage**: `/stream.write <section-id>`

**Workflow**:
1. Check section exists in plan and is pending
2. Generate content for section
3. Compute content hash
4. Write to temporary location first
5. Validate write completed (check for SECTION_END marker)
6. Append to main file with `SECTION_START` and `SECTION_END` markers
7. Update section status to `completed` with hash

**Script**:
```bash
python scripts/stream_write.py write report.md introduction "Your content here..."
```

**Markers in file**:
```markdown
<!-- SECTION_START: introduction | hash:a1b2c3d4 -->
## Introduction

Your introduction content here...

<!-- SECTION_END: introduction | hash:a1b2c3d4 -->
```

**Important**: 
- Write ONE section at a time
- Verify success before proceeding
- Hash in START and END markers must match (integrity check)

### Write Verification

After each write, the skill automatically verifies:
1. `SECTION_START` marker exists
2. `SECTION_END` marker exists
3. Hashes in both markers match
4. Content between markers is non-empty

If verification fails, the write is flagged and `/stream.repair` is recommended.

---

## /stream.status

Show current progress, identify resume point, and check integrity.

**Usage**: `/stream.status <filepath> [--verify]`

**Script**:
```bash
python scripts/stream_status.py report.md
python scripts/stream_status.py report.md --verify  # Full integrity check
```

**Standard Output**:
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

**With --verify flag (integrity check)**:
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

### Corruption Detection

The status command detects:
- **Orphaned START**: `SECTION_START` exists without matching `SECTION_END`
- **Hash mismatch**: START and END marker hashes don't match
- **Empty section**: Markers exist but no content between them
- **Duplicate sections**: Same section ID appears multiple times

---

## /stream.resume

Continue writing from the last incomplete section.

**Usage**: `/stream.resume <filepath>`

**Workflow**:
1. Run status with verification to find resume point
2. Check for corrupted sections (repair if needed)
3. Read existing content for context
4. Continue with `/stream.write` for next pending section

**Script**:
```bash
python scripts/stream_status.py report.md --resume
```

**Output**:
```
Resume Point: report.md

Last completed: background
Next pending: analysis

Context from previous sections loaded (2,450 tokens)
Ready to write: analysis

Command: /stream.write analysis
```

If corruption is detected:
```
Resume Point: report.md

⚠️  CORRUPTION DETECTED
Section 'analysis' has incomplete markers.

Recommended action:
1. Run `/stream.repair analysis` to remove partial content
2. Then run `/stream.write analysis` to regenerate

Command: /stream.repair analysis
```

---

## /stream.repair

Fix corrupted or partial sections.

**Usage**: `/stream.repair <filepath> <section-id> [--strategy <strategy>]`

**Strategies**:
- `remove` (default): Remove partial content, reset section to pending
- `complete`: Attempt to add missing END marker (use with caution)
- `backup`: Create backup before repair

**Workflow**:
1. Create backup of current file (if --strategy backup)
2. Locate corrupted section
3. Remove content from `SECTION_START` to end of partial content
4. Update section status to `pending`
5. Report repair results

**Script**:
```bash
python scripts/stream_repair.py report.md analysis --strategy remove
```

**Output**:
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

---

## /stream.finalize

Strip markers and validate completeness.

**Usage**: `/stream.finalize <filepath> [--output <output-filepath>]`

**Workflow**:
1. Run full integrity check
2. Verify all sections completed
3. Verify all hashes valid
4. Remove `SECTION_START` and `SECTION_END` markers
5. Remove YAML frontmatter stream metadata
6. Validate no incomplete markers remain
7. Write to output file (or overwrite in place)

**Script**:
```bash
python scripts/stream_cleanup.py report.md --output final_report.md
```

**Pre-finalize validation**:
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

**If validation fails**:
```
Finalize Check: report.md

⚠️  CANNOT FINALIZE - Issues detected:

  [ ] recommendations - PENDING (not written)
  [!] conclusion - CORRUPTED (hash mismatch)

Fix required before finalization:
1. /stream.write recommendations
2. /stream.repair conclusion
```

---

## Recovery Scenarios

### Scenario 1: Context limit hit mid-section

The section has `SECTION_START` but no `SECTION_END`:
```markdown
<!-- SECTION_START: analysis | hash:null -->
## Analysis

Partial content here...
[truncated - no SECTION_END]
```

**Recovery**:
1. `/stream.status --verify` detects incomplete section
2. `/stream.repair analysis` removes partial content
3. `/stream.write analysis` regenerates the section

### Scenario 2: Session ended between sections

All written sections have both markers:
```markdown
<!-- SECTION_END: background | hash:e5f6g7h8 -->
```

**Recovery**:
1. `/stream.resume` finds next pending section
2. Continue with `/stream.write`

### Scenario 3: Hash mismatch detected

START and END hashes don't match (content corrupted during write):
```markdown
<!-- SECTION_START: analysis | hash:a1b2c3d4 -->
...
<!-- SECTION_END: analysis | hash:x9y8z7w6 -->
```

**Recovery**:
1. `/stream.status --verify` flags hash mismatch
2. `/stream.repair analysis --strategy remove`
3. `/stream.write analysis` regenerates

### Scenario 4: Context compaction during heredoc append (what to avoid)

**Problem**: Using `cat >> file << 'EOF'` without streaming-output markers:
```bash
# DON'T DO THIS for long documents
cat >> spec.md << 'EOF'
## Section 12
Content...
EOF
```

If context compaction occurs, the heredoc may be split, causing:
- Partial content written
- No markers to detect corruption
- No way to identify resume point

**Prevention**: Always use streaming-output for documents >1000 lines.

---

## B-SPEC Template

For B-SPEC documents, use the built-in template:

```bash
/stream.init b-spec-010-llm-integration.md --template bspec
```

This creates the standard 15-section structure:

```yaml
stream_plan:
  version: "2.0"
  template: bspec
  sections:
    - id: overview
      status: pending
      hash: null
    - id: architecture
      status: pending
      hash: null
    - id: section-03  # Domain-specific
      status: pending
      hash: null
    - id: section-04
      status: pending
      hash: null
    - id: section-05
      status: pending
      hash: null
    - id: section-06
      status: pending
      hash: null
    - id: section-07
      status: pending
      hash: null
    - id: section-08
      status: pending
      hash: null
    - id: section-09
      status: pending
      hash: null
    - id: section-10
      status: pending
      hash: null
    - id: section-11
      status: pending
      hash: null
    - id: database-schema
      status: pending
      hash: null
    - id: api-specification
      status: pending
      hash: null
    - id: implementation-guide
      status: pending
      hash: null
    - id: appendices
      status: pending
      hash: null
```

---

## Workflow Checklist

Copy and track progress:

```
Stream Progress: [document-name]
- [ ] Initialize file with section plan
- [ ] Write each section (one at a time):
  - [ ] Section 1: ___________
  - [ ] Section 2: ___________
  - [ ] Section 3: ___________
  - [ ] ...
- [ ] Run status --verify to check integrity
- [ ] Repair any corrupted sections
- [ ] Finalize to strip markers
```

---

## Best Practices

1. **Plan sections upfront**: Define all sections before starting
2. **One section at a time**: Write, verify, then proceed
3. **Check status often**: Especially after interruptions or compaction
4. **Keep sections reasonable**: 500-2000 words per section works well
5. **Save context**: Don't hold generated content in memory; write immediately
6. **Use --verify flag**: Run `/stream.status --verify` after resuming
7. **Never skip repair**: If corruption is detected, repair before continuing
8. **Use templates**: For known document types like B-SPECs, use built-in templates

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Manual heredoc appends | No corruption detection | Use streaming-output |
| Skipping status checks | Miss corruption | Run status after each write |
| Ignoring hash mismatches | Propagate bad content | Repair immediately |
| Writing multiple sections at once | Can't identify failure point | One section at a time |
| Not using templates | Inconsistent structure | Use bspec template |
| Finalizing without verify | May include corrupted content | Always --verify first |

---

## Integration with Continuation Prompts

When creating continuation prompts for long document generation:

1. **Explicitly state**: "Use streaming-output skill for all document generation"
2. **Include status command**: "Run `/stream.status <file> --verify` to check progress"
3. **Document section plan**: List all sections and their status
4. **Specify resume point**: "Resume from section: X"

Example continuation prompt snippet:
```markdown
## Document Generation Status

Using streaming-output skill for B-SPEC-010.

Current status:
- Sections 1-5: Complete ✓
- Section 6: Pending (resume here)
- Sections 7-15: Pending

Resume command: `/stream.resume b-spec-010.md`
```

---

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `stream_write.py` | Init and write operations | `python scripts/stream_write.py <command> <args>` |
| `stream_status.py` | Progress, verification, and resume detection | `python scripts/stream_status.py <filepath> [--verify] [--resume]` |
| `stream_repair.py` | Fix corrupted sections | `python scripts/stream_repair.py <filepath> <section> [--strategy]` |
| `stream_cleanup.py` | Finalize and strip markers | `python scripts/stream_cleanup.py <filepath> [--output]` |

Run any script with `--help` for detailed options.

---

## Changelog

### v2.0 (2026-01-03)
- Added `/stream.repair` command for fixing corrupted sections
- Added hash-based integrity checking for section markers
- Added `--verify` flag to status command
- Added B-SPEC template (`--template bspec`)
- Added corruption detection (orphaned START, hash mismatch, empty sections)
- Added "Mandatory Use Cases" section
- Added "Anti-Patterns to Avoid" section
- Added "Integration with Continuation Prompts" guidance
- Improved recovery scenarios with specific commands
- Enhanced status output with integrity indicators

### v1.0 (Original)
- Initial streaming output implementation
- Basic section markers
- Status and finalize commands
