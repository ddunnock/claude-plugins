# Generate Workflow

Detailed workflow for `/docs.generate` command.

## Table of Contents
- [Purpose](#purpose)
- [Trigger Conditions](#trigger-conditions)
- [Workflow Steps](#workflow-steps)
- [Selection Options](#selection-options)
- [Document Review Loop](#document-review-loop)
- [Outputs](#outputs)
- [Idempotency](#idempotency)

---

## Purpose

Execute the documentation plan to create actual documentation:
1. Load WBS items from plan
2. Process items by priority and dependencies
3. Generate documents following Diátaxis guidelines
4. Apply document review loop (from GUARDRAILS)
5. Track progress and cascade changes
6. Update memory files with terminology and sources

---

## Trigger Conditions

**Explicit**:
- User runs `/docs.generate`
- User runs `/docs.generate WBS-001` (specific item)
- User runs `/docs.generate "Phase 1"` (phase)

**Selection modes**:
- `/docs.generate` - All pending items
- `/docs.generate WBS-001` - Specific item
- `/docs.generate "Phase 1"` - Items in phase
- `/docs.generate --user` - User-facing docs only
- `/docs.generate --dev` - Developer docs only

---

## Workflow Steps

### Step 1: Load Plan

Read from `docs/_meta/plan.md`:

```
Loading documentation plan...
├─ Total WBS items: 7
├─ Completed: 2
├─ In Progress: 0
└─ Pending: 5

Selection: [all pending / specific / phase]
```

If no plan exists:
```
No documentation plan found.

Options:
1. Run /docs.plan to create plan
2. Generate ad-hoc (specify sources directly)
```

### Step 2: Resolve Dependencies

Build execution order respecting dependencies:

```
Dependency Resolution:

WBS-001 (quickstart.md)      → No deps, ready
WBS-002 (installation.md)    → No deps, ready
WBS-003 (authentication.md)  → Depends on WBS-001, queue after
WBS-004 (api-usage.md)       → Depends on WBS-003, queue after
WBS-005 (configuration.md)   → No deps, ready
WBS-006 (overview.md)        → No deps, ready
WBS-007 (endpoints.md)       → No deps, ready

Execution Order:
1. WBS-001, WBS-002, WBS-005, WBS-006, WBS-007 (parallel eligible)
2. WBS-003 (after WBS-001)
3. WBS-004 (after WBS-003)
```

### Step 3: Load Sources

For each WBS item, load relevant sources:

```
WBS-003: authentication.md
├─ Loading: SRC-001 (requirements.md) - 2,400 tokens
├─ Loading: SRC-003 (auth-spec.md) - 1,800 tokens
└─ Total context: 4,200 tokens
```

Apply chunking if needed:
```
WBS-007: endpoints.md
├─ Source: SRC-002 (api-design.md) - 5,200 tokens
├─ Chunking: 2 chunks required
└─ Processing chunk 1 of 2...
```

### Step 4: Generate Document

Apply Diátaxis quadrant guidelines:

**For Tutorial (Getting Started)**:
```markdown
## Generation Guidelines: Tutorial

Focus on:
- Learning-oriented content
- Step-by-step progression
- Concrete examples user follows
- Achievable goals at each step

Structure:
1. What you'll learn
2. Prerequisites
3. Step 1, 2, 3...
4. What you've accomplished
```

**For How-To (Guides)**:
```markdown
## Generation Guidelines: How-To

Focus on:
- Task-oriented content
- Specific problem solving
- Assume basic knowledge
- Direct, actionable steps

Structure:
1. Goal statement
2. Prerequisites
3. Steps to accomplish
4. Troubleshooting
```

**For Reference**:
```markdown
## Generation Guidelines: Reference

Focus on:
- Information-oriented content
- Complete, accurate details
- Technical precision
- Consistent structure

Structure:
1. Overview
2. Syntax/Usage
3. Parameters/Options
4. Examples
5. See Also
```

**For Explanation**:
```markdown
## Generation Guidelines: Explanation

Focus on:
- Understanding-oriented content
- Why things work as they do
- Context and background
- Connections between concepts

Structure:
1. Introduction
2. Background
3. How it works
4. Design decisions
5. Implications
```

### Step 5: Document Review Loop

Apply the review loop from GUARDRAILS:

```
Document Review Loop for: authentication.md

1. Generate Draft
   └─ [Draft content generated]

2. Self-Audit
   ├─ Accuracy: ✓ Claims match sources
   ├─ Completeness: ✓ Key topics covered
   ├─ Clarity: ⚠ Section 3 could be clearer
   └─ Consistency: ✓ Terms match registry

3. Address Issues
   └─ Revising Section 3 for clarity...

4. User Review
   └─ Present draft for approval

[A]pprove  [R]evise  [S]kip
```

### Step 6: Write Document

On approval, write to target location:

```
Writing: docs/user/guides/authentication.md

├─ Created directory: docs/user/guides/
├─ Wrote file: 1,847 characters
└─ Updated progress tracker
```

### Step 7: Update Tracking

Update `docs/_meta/progress.md`:

```markdown
## Session: [timestamp]

| WBS ID | Document | Action | Status |
|--------|----------|--------|--------|
| WBS-003 | authentication.md | Generated | Complete |
```

Update memory files:
- `docs-terminology.md` - New terms defined
- `docs-sources.md` - Source usage logged
- `docs/_meta/change-log.md` - Change recorded

### Step 8: Cascade Analysis

Check if changes affect other documents:

```
Cascade Analysis for: authentication.md

Potentially affected:
├─ docs/user/guides/api-usage.md (references auth)
├─ docs/developer/reference/api/endpoints.md (auth endpoints)
└─ README.md (quick start section)

Actions:
1. Queue api-usage.md for review
2. Mark endpoints.md for auth section update
3. Suggest README update
```

### Step 9: Phase Gate Check

At phase boundaries:

```
Phase 1 Complete: Foundation

All items generated:
├─ ✓ WBS-001: quickstart.md
└─ ✓ WBS-002: installation.md

Gate Check: User can complete basic setup
├─ Prerequisites documented: ✓
├─ Installation steps: ✓
├─ First-run example: ✓
└─ Gate PASSED

Proceed to Phase 2? [Y/n]
```

---

## Selection Options

### By WBS ID

```bash
/docs.generate WBS-003
/docs.generate WBS-003,WBS-004,WBS-005
```

### By Phase

```bash
/docs.generate "Phase 1"
/docs.generate "Phase 2"
```

### By Audience

```bash
/docs.generate --user      # docs/user/** only
/docs.generate --dev       # docs/developer/** only
```

### By Quadrant

```bash
/docs.generate --tutorials  # Tutorial quadrant
/docs.generate --howto      # How-To quadrant
/docs.generate --reference  # Reference quadrant
/docs.generate --explain    # Explanation quadrant
```

### By Priority

```bash
/docs.generate --high       # HIGH priority only
/docs.generate --high,medium
```

---

## Document Review Loop

From GUARDRAILS - applied to each generated document:

### 1. Generate Draft

Create initial content from sources following quadrant guidelines.

### 2. Self-Audit Checklist

| Check | Question |
|-------|----------|
| Accuracy | Do all claims have source citations? |
| Completeness | Are all required topics covered? |
| Clarity | Is language clear and scannable? |
| Consistency | Do terms match the terminology registry? |
| Structure | Does structure follow quadrant template? |

### 3. Address Issues

Revise draft to address any failed checks.

### 4. User Review

Present for approval with options:
- **Approve**: Accept and write
- **Revise**: Request specific changes
- **Skip**: Move to next item

---

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| Generated docs | `docs/user/`, `docs/developer/` | Documentation files |
| Progress log | `docs/_meta/progress.md` | Session tracking |
| Change log | `docs/_meta/change-log.md` | Change history |
| Updated terminology | `.claude/memory/docs-terminology.md` | New terms |
| Updated sources | `.claude/memory/docs-sources.md` | Source usage |

---

## Idempotency

**Safe behaviors**:
- Skips completed WBS items (unless `--force`)
- Preserves manual edits to existing docs
- Offers merge options for conflicts
- Never deletes existing documentation
- Logs all actions for recovery

**Re-generation scenarios**:

```
WBS-003 already complete.

Options:
1. Skip - Keep existing document
2. Regenerate - Create fresh (backup existing)
3. Merge - Generate new, merge with existing
```

**Conflict detection**:

```
Existing file has manual edits:

docs/user/guides/authentication.md
├─ Generated: 2024-01-15
├─ Modified: 2024-01-16 (manual edits detected)
└─ Regenerating would overwrite edits

Options:
1. Skip - Preserve manual edits
2. Backup & Regenerate - Save existing, create new
3. Show Diff - Compare before deciding
```

**Status tracking**:

| Status | Meaning |
|--------|---------|
| Pending | Not yet generated |
| In Progress | Currently generating |
| Complete | Generated and approved |
| Skipped | Explicitly skipped by user |
| Needs Update | Cascade detected, needs review |
