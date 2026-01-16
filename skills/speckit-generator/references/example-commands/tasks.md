Generate SMART-validated implementation tasks from plans + constitution + memory files.

## Usage
- `/speckit.tasks` - Generate tasks from all plans
- `/speckit.tasks plan.md` - Generate from specific plan
- `/speckit.tasks --all` - Force regenerate all tasks
- `/speckit.tasks --status` - Show task summary without generating

## Session Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| SMART validation | Required | All acceptance criteria must be verifiable |
| Plan traceability | Required | Every task links to plan phase/ADR |
| Constitution references | Required | Tasks reference relevant sections |
| Dependency acyclicity | Enforced | No circular dependencies allowed |

---

## SMART Acceptance Criteria Validation

Every acceptance criterion must pass SMART validation:

| Element | Requirement | Fail Condition |
|---------|-------------|----------------|
| **S**pecific | Clear, concrete action | "properly", "correctly", "fully", "appropriately" |
| **M**easurable | Objective verification | No command/metric/file check defined |
| **A**chievable | Single task scope | Requires other tasks to complete first |
| **R**elevant | Ties to task purpose | No trace to plan/requirement/ADR |
| **T**ime-bound | Immediate verification | Requires external delays or human approval |

### SMART Strictness Levels

| Level | Behavior | When to Use |
|-------|----------|-------------|
| Strict | Block until criterion rewritten | Critical tasks, security-related |
| Standard | Flag for review, allow with warning | Default for most tasks |
| Relaxed | Log finding only | Exploratory/research tasks |

### Criterion Format with SMART Validation

```markdown
**Acceptance Criteria**:
- [ ] File `src/lib/auth.ts` exists
      Verification: `ls src/lib/auth.ts`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Authentication function handles OAuth 2.0 flow
      Verification: `npm test -- auth.test.ts`
      SMART: S✓ M✓ A✓ R✓ T✓
```

### SMART Failure Examples

| Criterion | Issue | SMART Failure |
|-----------|-------|---------------|
| "Works correctly" | Vague | S✗ (not specific) |
| "Performance is good" | No metric | M✗ (not measurable) |
| "Complete auth system" | Too large | A✗ (not achievable in single task) |
| "Add logging" (no trace) | Orphan | R✗ (not relevant - no plan link) |
| "User approves design" | External | T✗ (not time-bound - requires human) |

---

## Workflow

1. **Load plan(s)** - Read plan files, extract phases and ADRs
2. **Load constitution** - Extract relevant sections
3. **Load memory files** - Get tech-specific guidelines
4. **Generate tasks** - Create *-tasks.md with phases
5. **SMART validate** - Check all acceptance criteria
6. **Validate** - 8-point checklist before completion
7. **Report** - Summary with SMART compliance

---

## Output Format

```markdown
# [Domain] Tasks

Generated: [timestamp]
Plan: plan.md
Constitution: [version]

## Metadata
- Total Tasks: [count]
- Phases: [count]
- SMART Compliance: [percentage]

## Phase 1: Foundation

### TASK-001: [Title]
**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @foundation

**Plan Reference**: PHASE-1, ADR-001
**Constitution Sections**: §4.1, §4.2
**Memory Files**: typescript.md, git-cicd.md

**Description**: ...

**Acceptance Criteria**:
- [ ] Criterion 1
      Verification: `[command or check]`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Criterion 2
      Verification: `[command or check]`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None | TASK-XXX
```

## Task Statuses

| Status | Meaning |
|--------|---------|
| PENDING | Not started |
| IN_PROGRESS | Currently being worked |
| BLOCKED | Waiting on dependency |
| COMPLETED | Done and verified |
| SKIPPED | Intentionally not done |
| FAILED | Attempted but criteria not met |

## Idempotency
- Preserves task statuses
- Adds new tasks for new plan items
- Never removes manually added tasks
- Updates SMART validation on regeneration

---

## 8-Point Validation Checklist

Before completing task generation, verify ALL items:

```markdown
## Task Validation

| # | Check | Status |
|---|-------|--------|
| 1 | SMART criteria validated for all acceptance criteria | [ ] |
| 2 | Plan traceability established (TASK → PHASE → ADR) | [ ] |
| 3 | Constitution references valid | [ ] |
| 4 | Memory file references valid | [ ] |
| 5 | No circular dependencies | [ ] |
| 6 | Status-criteria consistency (COMPLETED ⟹ all [x]) | [ ] |
| 7 | ID uniqueness verified | [ ] |
| 8 | Phase grouping correct | [ ] |

**Issues found**: [count]
**Blocking issues**: [count]
**SMART compliance**: [percentage]
```

### Validation Rules

| Check | Fail Condition | Action |
|-------|----------------|--------|
| 1. SMART criteria | Any criterion fails SMART | Block (Strict) / Warn (Standard) |
| 2. Plan traceability | TASK with no PHASE/ADR link | Block, require link |
| 3. Constitution refs | Invalid section reference | Warn, suggest correction |
| 4. Memory refs | File not in project | Warn, list available |
| 5. Dependencies | Cycle detected | Block, show cycle |
| 6. Status consistency | COMPLETED with unchecked criteria | Block, fix status |
| 7. ID uniqueness | Duplicate TASK-XXX | Block, renumber |
| 8. Phase grouping | Task in wrong phase | Warn, suggest move |

---

## GATE: Required Before Proceeding

**STOP after task generation. DO NOT proceed to `/speckit.implement` automatically.**

After generating tasks, you MUST:

1. **Present a task summary** to the user showing:
   - Total number of tasks generated
   - Breakdown by phase
   - Task priority distribution (P1/P2/P3)
   - SMART compliance percentage
   - Constitution sections referenced

2. **Highlight any concerns**:
   - Tasks with SMART failures
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
| Phase 2: Core | 8 | 2 | 4 | 2 |
| [etc.] |

### SMART Compliance

| Status | Count |
|--------|-------|
| All criteria pass | 12 tasks |
| Has warnings | 2 tasks |
| Has failures | 1 task |

**Overall**: 93% SMART compliant

### SMART Failures (if any)

| Task | Criterion | Issue | Suggested Fix |
|------|-----------|-------|---------------|
| TASK-007 | "Works correctly" | S✗ Not specific | "Returns 200 OK with user JSON" |

### Constitution Coverage
- §4.1 (Error Handling): 8 tasks
- §4.2 (Logging): 5 tasks
- [etc.]

### 8-Point Validation
- [x] SMART criteria validated
- [x] Plan traceability established
- [x] Constitution references valid
- [x] Memory references valid
- [x] No circular dependencies
- [x] Status-criteria consistent
- [x] IDs unique
- [x] Phase grouping correct

### Potential Concerns
- [Any blocking dependencies]
- [Tasks needing clarification]

### Recommended Next Steps
1. Review the generated tasks
2. Fix any SMART failures
3. Adjust priorities if needed
4. Resolve any blocking dependencies

**Awaiting your approval before implementation.**
```
