---
description: "Execute implementation tasks with mandatory status tracking and verification"
agent:
  model: sonnet
---

# Implement

Execute tasks from `.claude/resources/*-tasks.md` with batch execution, gates, and mandatory hooks.

## Usage

```
/implement TASK-001           # Single task
/implement TASK-001..TASK-005 # Range
/implement "Phase 1"          # All in phase
/implement @foundation        # All with group
/implement --continue         # Resume from last
/implement                    # No argument - triggers status check
```

---

## MANDATORY: Pre-Execution Hooks

**CRITICAL**: These hooks MUST execute BEFORE any task implementation begins.

### Pre-Hook 1: Load Project Status

**ALWAYS** read `.claude/memory/project-status.md` first to understand:
- Current phase and progress
- What was completed in previous sessions
- Any blockers or failed criteria from last run
- Recommended next actions

```
Read: .claude/memory/project-status.md

Extract:
- Current Phase: [phase name]
- Progress: [X]/[Y] tasks ([Z]%)
- Last Activity: [date] - [what was done]
- Pending Actions: [list]
```

### Pre-Hook 2: Validate Argument / Show Status

**IF no argument provided OR invalid argument:**

```markdown
## Current Project Status

| Metric | Value |
|--------|-------|
| Project | [PROJECT_NAME] |
| Current Phase | Phase [N]: [Name] |
| Progress | [X]/[Y] tasks ([Z]%) |
| Last Updated | [DATE] |

### Phase Progress
| Phase | Status | Completed/Total |
|-------|--------|-----------------|
| Phase 1 | ✓ COMPLETE | 6/6 |
| Phase 2 | IN PROGRESS | 3/8 |
| Phase 3 | PENDING | 0/5 |

### Recommended Next Action

Based on current state, you should run:

```
/implement "Phase 2"
```

Or to continue from where you left off:

```
/implement --continue
```

### Available Selectors

| Selector | What It Does |
|----------|--------------|
| `TASK-XXX` | Execute single task |
| `TASK-XXX..TASK-YYY` | Execute range |
| `"Phase N"` | Execute all in phase |
| `@group` | Execute all with group tag |
| `--continue` | Resume from last position |
| `--all` | Execute all pending tasks |

**Please specify which tasks to implement.**
```

**STOP HERE** - Do not proceed without valid task selection.

### Pre-Hook 3: Validate Task Selection

For valid arguments, verify:

1. **Tasks exist** - Check *-tasks.md contains specified tasks
2. **Tasks are actionable** - Filter out COMPLETED tasks
3. **Dependencies met** - Check BLOCKED status

**IF no actionable tasks found:**

```markdown
## No Actionable Tasks

The specified selection has no pending tasks:

- `TASK-001`: COMPLETED (2024-01-15)
- `TASK-002`: COMPLETED (2024-01-15)
- `TASK-003`: COMPLETED (2024-01-15)

### Suggestions

1. **Move to next phase:**
   ```
   /implement "Phase [N+1]"
   ```

2. **Re-run a completed task:**
   ```
   /implement TASK-XXX --force
   ```

3. **Check overall status:**
   ```
   cat .claude/memory/project-status.md
   ```
```

### Pre-Hook 4: Present Execution Plan

Before executing, present the plan:

```markdown
## Execution Plan

**Selection**: [what user specified]
**Tasks to execute**: [count]

| Task | Title | Status | Dependencies |
|------|-------|--------|--------------|
| TASK-004 | [Title] | PENDING | None |
| TASK-005 | [Title] | PENDING | TASK-004 |
| TASK-006 | [Title] | FAILED | None (retry) |

**Context to load**:
- Constitution: §3.1, §4.2, §5.1
- Memory: typescript.md, testing.md

**Proceed with execution?**
```

---

## Workflow (After Pre-Hooks Pass)

### Phase 1: Execute Tasks

For each task:

1. **Load context**:
   - Extract referenced constitution sections (§X.Y)
   - Load relevant memory file sections
   - Present context before execution

2. **Execute** the task implementation

3. **Update status**: PENDING → IN_PROGRESS → COMPLETED

### Phase 2: Gate at Boundaries

At phase/group completion:

```
Phase [N] complete.
Tasks completed: [count]
Tasks failed: [count]

Options:
1. Continue to Phase [N+1]
2. Review completed work
3. Re-run failed tasks
4. Stop execution
```

---

## MANDATORY: Post-Implementation Hooks

**CRITICAL**: These hooks MUST execute after ANY implementation run. The command is NOT complete without them.

### Post-Hook 1: Update tasks.md

For EACH task worked on:

```markdown
### TASK-XXX: [Title]

**Status**: COMPLETED
**Completed**: [ISO_TIMESTAMP]
**Verified By**: Claude

**Acceptance Criteria**:
- [x] Criterion 1 - Verified: [evidence/command output]
- [x] Criterion 2 - Verified: [evidence/command output]
- [ ] Criterion 3 - FAILED: [specific reason]
```

**Verification Methods**:

| Criterion Type | Verification |
|----------------|--------------|
| File exists | `ls [path]` or glob |
| Tests pass | Run test command |
| Code compiles | Run build |
| Lint clean | Run linter |
| Type checks | Run type checker |

### Post-Hook 2: Update project-status.md

Location: `.claude/memory/project-status.md`

Update with:
- Current phase and progress metrics
- Phase completion status table
- Recent activity log entry
- Updated next actions

### Post-Hook 3: Output Completion Summary

```markdown
## Implementation Complete

### Tasks Completed This Session
| Task ID | Title | Status | Criteria |
|---------|-------|--------|----------|
| TASK-XXX | [Title] | ✓ COMPLETED | 3/3 ✓ |
| TASK-XXX | [Title] | ⚠ PARTIAL | 2/3 |

### Acceptance Criteria Verification
**Total**: [N] | **Passed**: [M] ([%]) | **Failed**: [F]

[If failed:]
#### Failed Criteria
| Task | Criterion | Reason |
|------|-----------|--------|
| TASK-XXX | [Criterion] | [Reason] |

### Project Status Updated
- Phase: [N] [status]
- Progress: [X]/[Y] tasks ([Z]%)
- project-status.md: Updated ✓

### Next Steps
1. [Based on current state]
2. [Specific command to run]
```

---

## Hook Enforcement Checklist

### Pre-Execution (must complete before tasks)
- [ ] project-status.md read and understood
- [ ] Argument validated (or status shown if missing)
- [ ] Task selection verified as actionable
- [ ] Execution plan presented and confirmed

### Post-Execution (must complete after tasks)
- [ ] All task statuses updated in *-tasks.md
- [ ] Each acceptance criterion verified with evidence
- [ ] `.claude/memory/project-status.md` current
- [ ] Completion summary output to user
- [ ] Next steps clearly stated

---

## Outputs

| Output | Location |
|--------|----------|
| Updated tasks | `.claude/resources/*-tasks.md` |
| Project status | `.claude/memory/project-status.md` |
| Completion summary | Displayed to user |

## Error Handling

| Error | Resolution |
|-------|------------|
| No argument provided | Show status and prompt for selection |
| Invalid task selector | Show valid options and current status |
| No actionable tasks | Suggest next phase or --force |
| Task dependency not met | Skip and mark BLOCKED |
| Criterion verification fails | Document failure, continue |
| project-status.md missing | Create from template |

## Handoffs

### Continue Implementation
```
/implement "Phase [N+1]"
```

### Fix Failed Tasks
```
/implement TASK-XXX
```

### Final Check
```
/analyze
```
