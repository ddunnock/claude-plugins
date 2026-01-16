Execute tasks from *-tasks.md with batch+gates execution model and mandatory hooks.

## Usage
- `/speckit.implement TASK-001` - Single task
- `/speckit.implement TASK-001..TASK-005` - Range of tasks
- `/speckit.implement "Phase 1"` - All tasks in phase
- `/speckit.implement @foundation` - All tasks with @foundation group
- `/speckit.implement` - No argument: shows status and prompts for selection

## Task Selection

| Selector | Meaning |
|----------|---------|
| `TASK-001` | Single task |
| `TASK-001..TASK-005` | Range of tasks |
| `"Phase 1"` | All tasks in phase |
| `@foundation` | All tasks with @foundation group |
| `--all` | All pending tasks |
| `--continue` | Resume from last position |
| *(no argument)* | Show status, prompt for selection |

## Execution Model: Pre-Hooks → Checkpoint → Tasks → Gates → Post-Hooks

```
═══════════════════════════════════════════
MANDATORY: Pre-Implementation Hooks
═══════════════════════════════════════════
    ↓
GIT CHECKPOINT (revertable state)
    ↓
Execute Phase 1 tasks
    ↓
GATE: "Phase 1 complete. Review outputs?"
    ↓
[User confirms]
    ↓
Execute Phase 2 tasks
    ↓
GATE: "Phase 2 complete. Review outputs?"
    ...
    ↓
═══════════════════════════════════════════
MANDATORY: Post-Implementation Hooks
═══════════════════════════════════════════
```

---

## MANDATORY: Pre-Implementation Hooks

**CRITICAL**: These hooks MUST execute BEFORE any task work begins.

### Pre-Hook 1: Load Project Status

**ALWAYS** read `.claude/memory/project-status.md` first:
- Current phase and overall progress
- What was completed in previous sessions
- Any blockers or failed criteria from last run
- Recommended next actions

### Pre-Hook 2: Validate Argument / Show Status

**IF no argument provided OR invalid argument**, output:

```markdown
## Current Project Status

| Metric | Value |
|--------|-------|
| Project | [PROJECT_NAME] |
| Current Phase | Phase [N]: [Name] |
| Progress | [X]/[Y] tasks ([Z]%) |

### Recommended Next Action
Based on current state, run:
/speckit.implement "Phase [N]"

### Available Selectors
| Selector | Example |
|----------|---------|
| Single task | `TASK-001` |
| Range | `TASK-001..TASK-005` |
| Phase | `"Phase 2"` |
| Group | `@foundation` |
| Continue | `--continue` |

**Please specify which tasks to implement.**
```

**STOP HERE** - Do not proceed without valid selection.

### Pre-Hook 3: Validate Task Selection

Verify tasks are actionable:
- Tasks exist in *-tasks.md
- Tasks are PENDING or FAILED (not COMPLETED)
- Dependencies are met

**IF no actionable tasks**, show status and suggest next phase.

### Pre-Hook 4: Present Execution Plan

Show what will be executed and get confirmation.

### Pre-Hook 5: Create Git Checkpoint

**CRITICAL**: Before ANY implementation work, create a revertable checkpoint.

```bash
# 1. Check for uncommitted changes
git status --porcelain

# 2. If changes exist, stash or commit them
git stash push -m "speckit-pre-implement-stash-$(date +%Y%m%d_%H%M%S)"
# OR
git add -A && git commit -m "speckit: Pre-implementation checkpoint"

# 3. Create checkpoint tag
git tag -a "speckit-checkpoint-$(date +%Y%m%d_%H%M%S)" -m "Pre-implementation checkpoint for [TASK_SELECTION]"

# 4. Record checkpoint in project-status.md
```

### Git Checkpoint Output

```markdown
## Git Checkpoint Created

| Property | Value |
|----------|-------|
| Checkpoint Tag | `speckit-checkpoint-20240115_143500` |
| Working Tree | Clean (stashed N changes) |
| Revert Command | `/speckit.revert speckit-checkpoint-20240115_143500` |

⚠️ **Safe to proceed** - All changes can be reverted if implementation fails.
```

---

## Workflow (After Pre-Hooks Pass)

For each task:
1. **Load context** - Read referenced constitution sections + memory files
2. **Present context** - Show agent the relevant guidelines
3. **Execute** - Perform the task
4. **Update status** - PENDING → IN_PROGRESS → COMPLETED
5. **Verify** - Check acceptance criteria

## Gate Behavior

At phase/group boundaries:
```
Phase [N] complete.

Tasks completed: [count]
Tasks failed: [count]

Options:
1. Continue to Phase [N+1]
2. Review completed work
3. Re-run failed tasks
4. Stop execution
5. Revert to checkpoint (/speckit.revert)
```

## Context Loading

```markdown
## Execution Context for TASK-001

### Constitution Requirements (§4.1, §4.2)
[Extracted sections from constitution.md]

### Memory File Guidelines
From typescript.md:
[Relevant sections]

From git-cicd.md:
[Relevant sections]

### Task Details
[Full task content]
```

---

## MANDATORY: Post-Implementation Hooks

**CRITICAL**: These hooks MUST execute after ANY `/speckit.implement` completion. The command is NOT complete without them.

### Hook 1: Update tasks.md - Status & Acceptance Criteria

For EACH task that was worked on:

```markdown
### TASK-XXX: [Title]

**Status**: COMPLETED
**Completed**: 2024-01-15T14:35:00Z
**Verified By**: Claude
**Checkpoint**: speckit-checkpoint-20240115_143500

**Acceptance Criteria**:
- [x] Criterion 1 - Verified: [evidence/command output]
- [x] Criterion 2 - Verified: [evidence/command output]
- [ ] Criterion 3 - FAILED: [specific reason]
```

**Verification Process**:
1. Read each acceptance criterion
2. Execute appropriate verification:
   - File exists? → `ls` or glob
   - Tests pass? → Run test command
   - Code compiles? → Run build
   - Lint clean? → Run linter
3. Document evidence in the criterion
4. Mark checkbox accordingly

### Hook 2: Update project-status.md

Location: `.claude/memory/project-status.md`

MUST update with:

```markdown
# Project Status

## Current State
| Metric | Value |
|--------|-------|
| Current Phase | Phase 2: Core Features |
| Total Tasks | 25 |
| Completed | 12 |
| In Progress | 0 |
| Pending | 13 |
| Progress | 48% |
| Last Updated | 2024-01-15T14:35:00Z |
| Last Checkpoint | speckit-checkpoint-20240115_143500 |

## Phase Progress
| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| Phase 1: Foundation | ✓ COMPLETE | 6 | 6 |
| Phase 2: Core Features | IN PROGRESS | 8 | 4 |
| Phase 3: Integration | PENDING | 6 | 0 |
| Phase 4: Polish | PENDING | 5 | 0 |

## Recent Activity
| Date | Tasks | Action | Checkpoint |
|------|-------|--------|------------|
| 2024-01-15 | TASK-007..TASK-010 | Completed Phase 2a | speckit-checkpoint-20240115_143500 |
| 2024-01-14 | TASK-001..TASK-006 | Completed Phase 1 | speckit-checkpoint-20240114_091000 |

## Next Actions
- [ ] Continue with Phase 2: TASK-011..TASK-014
- [ ] Address failed criterion in TASK-008
```

### Hook 3: Generate Completion Summary (MUST Output to User)

```markdown
## Implementation Complete

### Git Checkpoint
- **Created**: speckit-checkpoint-20240115_143500
- **Revert**: `/speckit.revert` to undo all changes from this session

### Tasks Completed This Session
| Task ID | Title | Status | Criteria Met |
|---------|-------|--------|--------------|
| TASK-007 | Implement user auth | ✓ COMPLETED | 4/4 |
| TASK-008 | Add session handling | ✓ COMPLETED | 3/3 |
| TASK-009 | Create middleware | ✓ COMPLETED | 2/2 |
| TASK-010 | Set up routes | ⚠ PARTIAL | 2/3 |

### Acceptance Criteria Verification
**Total Criteria**: 12
**Verified**: 11 (92%)
**Failed**: 1

#### Failed Criteria Requiring Attention
- TASK-010, Criterion 3: Route tests failing - TypeError in auth middleware

### Project Status Updated
- **Phase Progress**: Phase 2 in-progress (4/8 tasks)
- **Overall Progress**: 10/25 tasks (40%)
- **project-status.md**: Updated ✓
- **tasks.md**: Updated ✓

### Recommended Next Steps
1. Fix failing test in TASK-010 route middleware
2. Re-run: `/speckit.implement TASK-010`
3. Continue: `/speckit.implement "Phase 2"` (remaining 4 tasks)
4. When Phase 2 complete: `/speckit.implement "Phase 3"`
5. If issues persist: `/speckit.revert` to return to checkpoint

**Files Updated**:
- `speckit/core-tasks.md`
- `.claude/memory/project-status.md`
```

---

## Hook Enforcement Checklist

The implement command is **NOT COMPLETE** until ALL boxes are checked:

### Pre-Execution (before any task work)
- [ ] project-status.md read and understood
- [ ] Argument validated (or status shown if missing/invalid)
- [ ] Task selection verified as actionable
- [ ] Execution plan presented and confirmed
- [ ] Git checkpoint created with tag

### Post-Execution (after tasks complete)
- [ ] All executed task statuses updated in *-tasks.md
- [ ] Each acceptance criterion systematically verified with evidence
- [ ] Checkboxes marked `[x]` or `[ ]` with verification notes
- [ ] `.claude/memory/project-status.md` exists and is current
- [ ] Progress metrics accurate in project-status.md
- [ ] Checkpoint tag recorded in status
- [ ] Completion summary output to user
- [ ] Next steps clearly stated based on current state

---

## Idempotency
- Skips COMPLETED tasks
- Resumes from last position with `--continue`
- Re-runnable for failed tasks
- Never removes existing completion evidence
- Each run creates new checkpoint (does not overwrite previous)

---

## Revert Capability

If implementation goes wrong, use `/speckit.revert`:

```bash
/speckit.revert                    # Revert to most recent checkpoint
/speckit.revert speckit-checkpoint-20240115_143500  # Specific checkpoint
```

See `commands/speckit.revert.md` for full revert workflow with failure analysis.
