---
description: "Generate SMART-validated implementation tasks from plans"
handoffs:
  - label: Analyze For Consistency
    agent: analyze
    prompt: Run project analysis for consistency
  - label: Implement Project
    agent: implement
    prompt: Start implementation in phases
---

# Tasks

Generate SMART-validated implementation tasks from plans + constitution + memory files.

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
/tasks --status         # Show task summary without generating
```

---

## Memory Directives

Load these directive files for task generation:

**Always loaded:**
- `constitution.md` - Global principles, section references for tasks
- `testing.md` - Test coverage requirements
- `git-cicd.md` - Git workflow and CI/CD standards

**Project-specific (detected: Python, Poetry, Pyright):**
- `python.md` - Python ≥3.11 standards, type hints, docstrings
- `security.md` - Security requirements

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

### SMART Strictness Level

**Selected for this project:** Standard

| Level | Behavior | When to Use |
|-------|----------|-------------|
| Strict | Block until criterion rewritten | Critical tasks, security-related |
| **Standard** | Flag for review, allow with warning | Default for most tasks |
| Relaxed | Log finding only | Exploratory/research tasks |

### Criterion Format

```markdown
**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/search/hybrid.py` exists
      Verification: `ls src/knowledge_mcp/search/hybrid.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Hybrid search passes all tests
      Verification: `poetry run pytest tests/unit/test_search/`
      SMART: S✓ M✓ A✓ R✓ T✓
```

---

## Constitution Section Mapping

| Task Type | Constitution Sections |
|-----------|----------------------|
| Setup/Init | §3 (Structure), §6 (Performance) |
| API/Backend | §2.3 (Type Safety), §4 (Exception Handling) |
| Testing | §2.1 (Coverage), §7 (Documentation) |
| Documentation | §7 (Documentation Standards) |

---

## Task Template Level

**Selected for this project:** Standard

| Level | Fields Included | When to Use |
|-------|-----------------|-------------|
| Lightweight | Status, Priority, Description, Criteria | Small projects |
| **Standard** | + Phase, Group, Plan Reference, Dependencies | Default |
| Detailed | + Constitution Sections, Memory Files, SMART validation | Complex projects |

---

## Workflow

1. **Load plan(s)** - Read plan files, extract phases and ADRs
2. **Load constitution** - Extract relevant sections
3. **Load memory files** - Get tech-specific guidelines
4. **Generate tasks** - Create *-tasks.md with phases
5. **Validate coverage** - Run coverage mapper agent
6. **SMART validate** - Run SMART validator agent
7. **Validate checklist** - 8-point checklist before completion
8. **Report** - Summary with SMART compliance

---

## Coverage Validation (Agent)

After generating tasks, verify requirement coverage.

**Invoke via Task tool:**
```
subagent_type: "speckit-generator:coverage-mapper"
prompt: "Map coverage between .claude/resources/spec.md, .claude/resources/plan.md, and .claude/resources/*-tasks.md"
```

---

## SMART Validation (Agent)

After generating tasks, validate all acceptance criteria.

**Invoke via Task tool:**
```
subagent_type: "speckit-generator:smart-validator"
prompt: "Validate SMART criteria in .claude/resources/*-tasks.md at Standard strictness, suggest fixes for failures"
```

## Output Format

```markdown
# [Feature] Tasks

Generated: [timestamp]
Plan: plan.md
Constitution: constitution.md

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
**Constitution Sections**: §2.1, §2.3
**Memory Files**: python.md, testing.md

**Description**: ...

**Acceptance Criteria**:
- [ ] Criterion 1
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

---

## 8-Point Validation Checklist

Before completing task generation, verify ALL items:

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

---

## Outputs

| Output | Location |
|--------|----------|
| Tasks file | `.claude/resources/*-tasks.md` |
| Updated status | `.claude/memory/project-status.md` |

---

## Ralph Loop Mode (Autonomous Task Generation)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous task refinement:

```
/tasks --ralph                    # Until 100% SMART compliance
/tasks --ralph --smart-level strict   # Strict SMART validation
```

### Exit Criteria

- All tasks have SMART-compliant acceptance criteria
- 8-point validation passes
- No blocking issues remain
- Hard limit: 15 iterations

---

## GATE: Required Before Proceeding

**STOP after task generation. DO NOT proceed to `/implement` automatically.**

After generating tasks, you MUST:

1. **Present a task summary** showing:
   - Total number of tasks generated
   - Breakdown by phase
   - Task priority distribution (P1/P2/P3)
   - SMART compliance percentage

2. **Highlight any concerns**:
   - Tasks with SMART failures
   - Dependencies that may cause blocking

3. **Wait for explicit user approval** before implementation

### Gate Response Template

```markdown
## Task Generation Complete

Generated [N] tasks across [M] phases:

| Phase | Tasks | P1 | P2 | P3 |
|-------|-------|----|----|----|
| Phase 1: Foundation | 5 | 3 | 2 | 0 |

### SMART Compliance

| Status | Count |
|--------|-------|
| All criteria pass | N tasks |
| Has warnings | N tasks |
| Has failures | N task |

**Overall**: N% SMART compliant

### 8-Point Validation
- [x] SMART criteria validated
- [x] Plan traceability established
- [x] Constitution references valid
- [x] Memory references valid
- [x] No circular dependencies
- [x] Status-criteria consistent
- [x] IDs unique
- [x] Phase grouping correct

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