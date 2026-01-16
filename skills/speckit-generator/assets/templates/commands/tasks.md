---
description: "Generate actionable, dependency-ordered tasks from plans"
handoffs:
  - label: Analyze For Consistency
    agent: analyze
    prompt: Run project analysis for consistency
  - label: Implement Project
    agent: implement
    prompt: Start implementation in phases
---

# Tasks

Generate implementation tasks from plans + constitution + memory files.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Usage

```
/tasks                  # Generate tasks from all plans
/tasks plan.md          # Generate from specific plan
/tasks --all            # Force regenerate all tasks
```

---

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

---

## Outputs

| Output | Location |
|--------|----------|
| Tasks file | `.claude/resources/*-tasks.md` |
| Updated status | `.claude/memory/project-status.md` |

---

## GATE: Required Before Proceeding

**STOP after task generation. DO NOT proceed to `/implement` automatically.**

After generating tasks, you MUST:

1. **Present a task summary** to the user showing:
   - Total number of tasks generated
   - Breakdown by phase
   - Task priority distribution (P1/P2/P3)
   - Constitution sections referenced

2. **Highlight any concerns**:
   - Tasks with unclear acceptance criteria
   - Dependencies that may cause blocking
   - Tasks that may need clarification

3. **Wait for explicit user approval** before implementation

### Gate Response Template

```markdown
## Task Generation Complete

Generated [N] tasks across [M] phases:

| Phase | Tasks | P1 | P2 | P3 |
|-------|-------|----|----|----|
| Phase 1: Foundation | 5 | 3 | 2 | 0 |
| [etc.] |

### Constitution Coverage
- §4.1 (Error Handling): 8 tasks
- §4.2 (Logging): 5 tasks
- [etc.]

### Potential Concerns
- [Any blocking dependencies]
- [Tasks needing clarification]

### Recommended Next Steps
1. Review the generated tasks
2. Adjust priorities if needed
3. Resolve any blocking dependencies

**Awaiting your approval before implementation.**
```

---

## Handoffs

### Analyze For Consistency
Run analysis to verify task coverage and find gaps.

Use: `/analyze`

### Implement Project
After tasks are approved, start implementation in phases.

Use: `/implement`
