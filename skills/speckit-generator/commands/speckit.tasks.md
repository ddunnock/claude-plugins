Generate implementation tasks from plans + constitution + memory files.

## Usage
- `/speckit.tasks` - Generate tasks from all plans
- `/speckit.tasks plan.md` - Generate from specific plan
- `/speckit.tasks --all` - Force regenerate all tasks

## Workflow

1. **Load plan(s)** - Read plan files
2. **Load constitution** - Extract relevant sections
3. **Load memory files** - Get tech-specific guidelines
4. **Generate tasks** - Create *-tasks.md with phases
5. **Validate** - Check task completeness

## Output Format

```markdown
# [Domain] Tasks

## Phase 1: Foundation

### TASK-001: [Title]
**Status**: PENDING
**Priority**: P1
**Constitution Sections**: §4.1, §4.2
**Memory Files**: typescript.md, git-cicd.md
**Plan Reference**: PLAN-001
**Description**: ...
**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
```

## Task Statuses

| Status | Meaning |
|--------|---------|
| PENDING | Not started |
| IN_PROGRESS | Currently being worked |
| BLOCKED | Waiting on dependency |
| COMPLETED | Done and verified |
| SKIPPED | Intentionally not done |

## Idempotency
- Preserves task statuses
- Adds new tasks for new plan items
- Never removes manually added tasks
