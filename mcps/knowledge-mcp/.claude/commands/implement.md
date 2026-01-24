---
description: "Execute implementation tasks with mandatory status tracking and verification"
handoffs:
  - label: Design Task First
    agent: design
    prompt: Generate detailed implementation design for task
  - label: Revert Changes
    agent: revert
    prompt: Revert to checkpoint if implementation failed
  - label: Analyze Results
    agent: analyze
    prompt: Verify implementation consistency
---

# Implement

Execute tasks from `speckit/*-tasks.md` with batch execution, gates, and mandatory hooks.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

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
| Project | Knowledge MCP |
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

### Pre-Hook 4: Check Design Files

For each task, check if a design file exists:

```
Check: speckit/designs/design-[TASK-ID].md
```

**IF design file exists:**
- Load design and use as implementation guide
- Follow data models, method signatures, and test cases from design
- Verify implementation matches design specifications

**IF design file does NOT exist:**
- Note task lacks detailed design
- For complex tasks (Scope: L or M), suggest:
  ```
  Consider running `/design [TASK-ID]` first for detailed implementation guidance.
  ```
- For simple tasks (Scope: S), proceed without design

### Pre-Hook 5: Present Execution Plan

Before executing, present the plan:

```markdown
## Execution Plan

**Selection**: [what user specified]
**Tasks to execute**: [count]

| Task | Title | Status | Dependencies | Design |
|------|-------|--------|--------------|--------|
| TASK-004 | [Title] | PENDING | None | ✓ Available |
| TASK-005 | [Title] | PENDING | TASK-004 | ✗ None |
| TASK-006 | [Title] | FAILED | None (retry) | ✓ Available |

**Context to load**:
- Constitution: §3.1, §3.2, §4.1
- Memory: python.md, testing.md
- Designs: design-TASK-004.md, design-TASK-006.md

**Proceed with execution?**
```

---

## Workflow (After Pre-Hooks Pass)

### Phase 1: Execute Tasks

For each task:

1. **Load context**:
   - Extract referenced constitution sections (§X.Y)
   - Load relevant memory file sections
   - Load design file if available (`speckit/designs/design-[TASK-ID].md`)
   - Present context before execution

2. **Execute** the task implementation:
   - If design exists: Follow data models, method signatures, and algorithm from design
   - If no design: Implement based on task description and acceptance criteria
   - Run test cases from design (if provided)

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

### Post-Hook 0: Compliance Check (Agent)

After implementing code, verify compliance with project directives.

**Invoke compliance-checker agent:**
```
subagent_type: "speckit-generator:compliance-checker"
prompt: "Check compliance of [MODIFIED_FILES] against .claude/memory/constitution.md and relevant tech-specific memory files"
```

The agent validates:
- MUST/MUST NOT rules from constitution
- Technology-specific requirements (python.md - Pyright strict, ruff)
- Security requirements

**Handle results:**
- CRITICAL: Must fix before marking task complete
- HIGH: Should fix, warn if proceeding
- MEDIUM/LOW: Document for later review

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
| Tests pass | `poetry run pytest [path]` |
| Code compiles | `poetry run pyright` |
| Lint clean | `poetry run ruff check src tests` |
| Type checks | `poetry run pyright src/` |

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
- [ ] Design files checked for each task
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
| Updated tasks | `speckit/*-tasks.md` |
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

---

## Ralph Loop Mode (Autonomous Execution)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous implementation that iterates until all acceptance criteria are verified:

```
/implement "Phase 1" --ralph
/implement TASK-001..TASK-010 --ralph --max-iterations 30
```

### How It Works

1. Wraps implementation in a ralph-loop with `/ralph-loop`
2. Completion promise: `<promise>ALL_CRITERIA_VERIFIED</promise>`
3. Iterates until ALL acceptance criteria for selected tasks are `[x]` checked
4. Safety limit: 50 iterations (override with `--max-iterations`)

### Exit Criteria

The loop exits ONLY when:
- Every selected task has status: COMPLETED
- Every acceptance criterion is marked `[x]` with verification evidence
- No criteria remain `[ ]` or FAILED

### Ralph Loop Prompt Construction

When `--ralph` is specified, construct the ralph-loop call:

```
/ralph-loop "Execute the following implementation tasks and verify ALL acceptance criteria.

Tasks: [TASK_SELECTION]

For each task:
1. Read task details from tasks.md
2. Implement the task
3. Verify EACH acceptance criterion with evidence
4. Mark criterion [x] with verification notes
5. Update task status to COMPLETED

Exit criteria: ALL acceptance criteria must be [x] verified.

When ALL criteria are verified, output: <promise>ALL_CRITERIA_VERIFIED</promise>

If stuck after multiple attempts, document blockers but do NOT output the promise until genuinely complete." --completion-promise "ALL_CRITERIA_VERIFIED" --max-iterations [N]
```

---

## Handoffs

### Design Complex Tasks First
For tasks lacking designs:
```
/design TASK-XXX
```

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