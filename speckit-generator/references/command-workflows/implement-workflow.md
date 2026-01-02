# Implement Workflow Reference

Detailed workflow for the `/speckit.implement` command.

## Purpose

Execute tasks from *-tasks.md with batch+gates execution model. Provides structured implementation with checkpoints for review.

## Key Characteristics

- **Context-aware**: Loads constitution sections and memory files per task
- **Batch execution**: Runs related tasks together
- **Gates**: Pauses at phase/group boundaries for review
- **Status tracking**: Updates task statuses in real-time
- **Resumable**: Can stop and continue later

---

## Task Selection

### Selection Syntax

| Selector | Meaning | Example |
|----------|---------|---------|
| `TASK-XXX` | Single task | `TASK-001` |
| `TASK-XXX..TASK-YYY` | Range | `TASK-001..TASK-005` |
| `"Phase N"` | All in phase | `"Phase 1"` |
| `@group` | All with group tag | `@foundation` |
| `--all` | All pending tasks | `--all` |
| `--continue` | Resume from last | `--continue` |

### Selection Examples

```bash
# Single task
/speckit.implement TASK-001

# Range of tasks
/speckit.implement TASK-001..TASK-010

# Entire phase
/speckit.implement "Phase 1"

# All foundation tasks
/speckit.implement @foundation

# All pending tasks
/speckit.implement --all

# Continue from where we left off
/speckit.implement --continue
```

---

## Workflow Steps

### Step 1: Parse Selection

```
Selection: "Phase 1"

Tasks selected:
- TASK-001: Initialize project structure [PENDING]
- TASK-002: Set up configuration [PENDING]
- TASK-003: Create base components [PENDING]
- TASK-004: Implement auth flow [PENDING]

Total: 4 tasks
Status: All PENDING

Proceed with Phase 1 execution?
```

### Step 2: Build Execution Order

Respect dependencies:
```
Dependency analysis:
- TASK-001: No dependencies (start)
- TASK-002: Depends on TASK-001
- TASK-003: Depends on TASK-002
- TASK-004: Depends on TASK-001, TASK-002

Execution order:
1. TASK-001
2. TASK-002
3. TASK-003, TASK-004 (can parallelize)
```

### Step 3: Load Context Per Task

For each task, load referenced materials:

```markdown
## Execution Context for TASK-001

### Task Details
**Title**: Initialize project structure
**Priority**: P1
**Status**: PENDING → IN_PROGRESS

### Constitution Requirements

#### §3.1 Project Structure
> All projects must follow the standard directory layout:
> - src/ for source code
> - tests/ for test files
> - docs/ for documentation
> Projects must include standard config files...

#### §3.2 Configuration
> Configuration must use environment variables for secrets.
> Config files must have schema validation...

### Memory File Guidelines

#### From typescript.md - "Project Setup"
> Use pnpm as package manager.
> Enable strict TypeScript mode.
> Configure path aliases in tsconfig.json...

#### From git-cicd.md - "Initial Setup"
> Initialize with .gitignore from template.
> Set up pre-commit hooks with husky.
> Configure GitHub Actions for CI...

### Acceptance Criteria
- [ ] Project directories created per §3.1
- [ ] Configuration files in place per §3.2
- [ ] TypeScript configured per typescript.md
- [ ] Git initialized per git-cicd.md
```

### Step 4: Execute Task

Present context and execute:

```
Executing TASK-001: Initialize project structure

Context loaded:
- Constitution: §3.1, §3.2
- Memory: typescript.md, git-cicd.md

Acceptance criteria:
- [ ] Project directories created per §3.1
- [ ] Configuration files in place per §3.2
- [ ] TypeScript configured per typescript.md
- [ ] Git initialized per git-cicd.md

Executing...
```

### Step 5: Verify Completion

Check acceptance criteria:

```
TASK-001 Execution Complete

Acceptance criteria check:
✓ Project directories created per §3.1
✓ Configuration files in place per §3.2
✓ TypeScript configured per typescript.md
✓ Git initialized per git-cicd.md

All criteria met. Marking as COMPLETED.

Files modified:
- Created: src/, tests/, docs/
- Created: package.json, tsconfig.json
- Created: .gitignore, .husky/

Continue to TASK-002?
```

### Step 6: Gate at Phase Boundary

After completing phase tasks:

```
═══════════════════════════════════════════
GATE: Phase 1 Complete
═══════════════════════════════════════════

Tasks completed: 4
Tasks failed: 0
Tasks skipped: 0

Summary:
- TASK-001: Initialize project structure ✓
- TASK-002: Set up configuration ✓
- TASK-003: Create base components ✓
- TASK-004: Implement auth flow ✓

Files modified: 23
Lines added: 1,247
Lines removed: 0

Options:
1. Continue to Phase 2 (5 tasks)
2. Review completed work in detail
3. Re-run specific tasks
4. Stop execution (can resume later)

Your choice:
```

---

## Status Transitions

```
PENDING → IN_PROGRESS → COMPLETED
                     ↘ FAILED → [fix] → IN_PROGRESS
                     ↘ BLOCKED
                     ↘ SKIPPED
```

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Not started | Ready to execute |
| IN_PROGRESS | Currently executing | Wait for completion |
| COMPLETED | Done and verified | Move to next |
| FAILED | Execution failed | Fix and retry |
| BLOCKED | Waiting on dependency | Resolve blocker |
| SKIPPED | Intentionally skipped | Document reason |

---

## Context Loading

### Constitution Section Extraction

For each referenced section:
1. Find section by ID (§X.Y)
2. Extract section content
3. Include relevant examples
4. Highlight key requirements

```python
def extract_constitution_section(constitution_path, section_id):
    """
    Extract section content from constitution.
    Returns header, content, examples, and key requirements.
    """
    # Parse markdown
    # Find section by heading pattern
    # Extract until next section
    # Identify code blocks as examples
    # Extract "must", "shall", "required" statements
```

### Memory File Section Extraction

For each memory file reference:
1. Find relevant section by title or keyword
2. Extract guidance content
3. Include code examples
4. Highlight patterns and anti-patterns

---

## Failure Handling

### Task Failure

```
TASK-003 Failed

Error: TypeScript compilation errors
Details: 3 type errors in src/components/Button.tsx

Options:
1. View error details
2. Retry task
3. Mark as BLOCKED (add blocker note)
4. Skip task (document reason)
5. Stop execution
```

### Dependency Failure

```
TASK-005 Blocked

Reason: Depends on TASK-003 which FAILED

Options:
1. Fix TASK-003 first
2. Skip TASK-005 (document reason)
3. Override dependency check
4. Stop execution
```

---

## Resumption

After stopping:

```bash
/speckit.implement --continue
```

```
Resuming execution...

Last session: 2024-01-15T14:30:00Z
Progress: Phase 1 complete, Phase 2 in progress

Status:
- COMPLETED: 4 tasks
- IN_PROGRESS: 0 tasks
- PENDING: 11 tasks

Continue from TASK-005?
```

---

## Execution Summary

After completing all selected tasks:

```
═══════════════════════════════════════════
Execution Complete
═══════════════════════════════════════════

Duration: 45 minutes
Tasks executed: 15

By status:
- COMPLETED: 14
- FAILED: 1 (TASK-012)
- SKIPPED: 0

By phase:
- Phase 1: 4/4 ✓
- Phase 2: 6/6 ✓
- Phase 3: 4/5 (1 failed)

Files modified: 67
Lines added: 3,456
Lines removed: 234

Failed tasks require attention:
- TASK-012: API integration test
  Error: External API timeout

Recommendations:
1. Review TASK-012 failure
2. Run /speckit.analyze to check consistency
3. Commit changes with /commit
```

---

## Integration Points

### From /speckit.tasks

Tasks file provides:
- Task definitions
- Constitution references
- Memory file references
- Acceptance criteria
- Dependencies

### To Task File Updates

Status updates written back:
```markdown
### TASK-001: Initialize project structure
**Status**: COMPLETED
**Completed**: 2024-01-15T14:35:00Z
```

### With /speckit.analyze

Post-execution analysis:
```
Execution complete. Run /speckit.analyze to verify consistency?
```

---

## Idempotency

- **Skip COMPLETED**: Already-done tasks skipped
- **Resume IN_PROGRESS**: Interrupted tasks restart
- **Preserve history**: Completion timestamps preserved
- **Re-runnable FAILED**: Failed tasks can retry
