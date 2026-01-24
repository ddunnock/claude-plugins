---
description: "Revert to checkpoint with intelligent failure analysis"
handoffs:
  - label: Clarify Requirements
    agent: clarify
    prompt: Resolve spec gaps that caused failure
  - label: Revise Plan
    agent: plan
    prompt: Update plan with different approach
  - label: Retry Implementation
    agent: implement
    prompt: Retry implementation after fixes
---

# Revert

Revert to a previous git checkpoint with failure analysis and artifact recommendations.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Usage

```
/revert                    # Revert to most recent checkpoint
/revert [checkpoint-tag]   # Revert to specific checkpoint
/revert --list             # List available checkpoints
/revert --dry-run          # Preview without executing
```

---

## MANDATORY: Pre-Revert Hooks

### Pre-Hook 1: List and Validate Checkpoints

```bash
# List speckit checkpoints
git tag -l "speckit-checkpoint-*" --sort=-creatordate
```

**IF no checkpoints exist**: Stop and inform user.

### Pre-Hook 2: Show Revert Preview

Before reverting, show:
- Files that will be reverted
- Tasks that will be reset
- Changes that will be lost

**Get explicit confirmation before proceeding.**

---

## Revert Process

### Step 1: Save Current State for Analysis

```bash
# Save diff for analysis
git diff HEAD [checkpoint] > .claude/.cache/failed-changes.diff

# Save commit log
git log --oneline [checkpoint]..HEAD > .claude/.cache/failed-commits.log
```

### Step 2: Execute Revert

```bash
# Stash uncommitted changes
git stash push -m "speckit-pre-revert-$(date +%Y%m%d_%H%M%S)"

# Reset to checkpoint
git reset --hard [checkpoint]
```

---

## MANDATORY: Post-Revert Failure Analysis

**CRITICAL**: Always analyze what went wrong after reverting.

### Analysis Steps

1. **Examine the diff** - What was changed?
2. **Identify failure category**:
   - SPEC_GAP - Requirements unclear
   - APPROACH_WRONG - Need different architecture
   - DEPENDENCY_ISSUE - External problem
   - TEST_MISMATCH - Tests don't match reality
   - SCOPE_CREEP - Too much at once
   - KNOWLEDGE_GAP - Need more research

3. **Generate recommendations**:
   - Spec clarifications needed?
   - Plan revisions required?
   - Task decomposition suggested?

### Update Artifacts

1. **project-status.md** - Log revert, add blocker
2. **tasks.md** - Reset status, add failure notes
3. **Create failure report** - speckit/failure-analysis-[date].md

---

## Output Template

```markdown
## Revert Complete

### Summary
| Property | Value |
|----------|-------|
| Checkpoint | [TAG] |
| Tasks Reverted | [TASK_RANGE] |
| Failure Category | [CATEGORY] |

### Root Cause
[Brief explanation]

### Recommendations
1. [First action]
2. [Second action]
3. [Third action]

### Next Command
Based on analysis:
```
[recommended command]
```
```

---

## Flags

| Flag | Effect |
|------|--------|
| `--list` | Show checkpoints only |
| `--dry-run` | Preview without reverting |
| `--no-analysis` | Skip analysis (not recommended) |
| `--force` | Skip confirmations |