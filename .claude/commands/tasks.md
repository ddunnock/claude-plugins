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
- `testing.md` - Test coverage requirements (80% minimum)
- `git-cicd.md` - Git workflow and CI/CD standards

**Project-specific (detected: Python ≥3.11, Poetry, MCP SDK):**
- `python.md` - Python standards, Pyright strict, ruff linting
- `security.md` - API key management, input validation

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

| Level | Behavior | When to Use |
|-------|----------|-------------|
| Strict | Block until criterion rewritten | Critical tasks, security-related |
| Standard | Flag for review, allow with warning | Default for most tasks |
| Relaxed | Log finding only | Exploratory/research tasks |

**Selected for this project:** Standard

### Criterion Format

```markdown
**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/store/qdrant_store.py` exists
      Verification: `ls src/knowledge_mcp/store/qdrant_store.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] QdrantStore class passes type checking
      Verification: `poetry run pyright src/knowledge_mcp/store/`
      SMART: S✓ M✓ A✓ R✓ T✓
```

---

## Constitution Section Mapping

| Task Type | Constitution Sections |
|-----------|----------------------|
| Setup/Init | §2 (Structure), §5 (Configuration) |
| API/Backend | §3 (Code Standards), §10 (MCP Server) |
| Storage | §3.3 (Error Handling), §5 (Configuration) |
| Testing | §4 (Testing), python.md §7 |
| Documentation | §8 (Documentation), documentation.md |

---

## Task Template Level

| Level | Fields Included | When to Use |
|-------|-----------------|-------------|
| Lightweight | Status, Priority, Description, Criteria | Small projects, quick iterations |
| Standard | + Phase, Group, Plan Reference, Dependencies | Default for most projects |
| Detailed | + Constitution Sections, Memory Files, SMART validation | Complex/regulated projects |

**Selected for this project:** Standard

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
prompt: "Map coverage between speckit/spec.md, speckit/plan.md, and speckit/*-tasks.md"
```

The agent will identify:
- Orphan requirements (no task coverage)
- Orphan tasks (no requirement trace)
- Coverage percentage per requirement

**Handle results:**
- Review orphan requirements - add tasks or mark as out-of-scope
- Review orphan tasks - link to requirements or mark as infrastructure

---

## SMART Validation (Agent)

After generating tasks, validate all acceptance criteria.

**Invoke via Task tool:**
```
subagent_type: "speckit-generator:smart-validator"
prompt: "Validate SMART criteria in speckit/*-tasks.md at Standard strictness, suggest fixes for failures"
```

The agent will check each criterion for:
- **S**pecific - No vague adjectives
- **M**easurable - Has verification command/check
- **A**chievable - Single task scope
- **R**elevant - Traces to plan/requirement
- **T**ime-bound - Immediate verification

**Handle results:**
- PASS: Proceed to 8-point validation
- WARN: Review warnings, consider rewording
- FAIL (Strict mode): Must fix before proceeding

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
**Constitution Sections**: §3.1, §3.2
**Memory Files**: python.md, testing.md

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
| Tasks file | `speckit/*-tasks.md` |
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
- §3.1 (Type Hints): 8 tasks
- §3.2 (Docstrings): 5 tasks
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
5. Run `/design TASK-XXX` for detailed implementation designs (optional)

**Awaiting your approval before implementation.**

---

### Design Files (Optional)

For complex tasks, generate detailed implementation designs before implementing:

```
/design TASK-007           # Generate design with algorithms, tests, edge cases
/design TASK-003,TASK-004  # Design multiple tasks
```

Design files provide:
- Data model definitions with validation
- Method signatures with full type annotations
- Algorithm pseudo-code with step-by-step logic
- Test cases covering acceptance criteria
- Edge case handling

Designs are saved to `speckit/designs/design-[TASK-ID].md`
```

---

## Handoffs

### Analyze For Consistency
Run analysis to verify task coverage and find gaps.

Use: `/analyze`

### Implement Project
After tasks are approved, start implementation in phases.

Use: `/implement`