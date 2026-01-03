Execute tasks from *-tasks.md with batch+gates execution model.

## Usage
- `/speckit.implement TASK-001` - Single task
- `/speckit.implement TASK-001..TASK-005` - Range of tasks
- `/speckit.implement "Phase 1"` - All tasks in phase
- `/speckit.implement @foundation` - All tasks with @foundation group

## Task Selection

| Selector | Meaning |
|----------|---------|
| `TASK-001` | Single task |
| `TASK-001..TASK-005` | Range of tasks |
| `"Phase 1"` | All tasks in phase |
| `@foundation` | All tasks with @foundation group |

## Execution Model: Batch + Gates

```
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
```

## Workflow

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

## Idempotency
- Skips COMPLETED tasks
- Resumes from last position
- Re-runnable for failed tasks
