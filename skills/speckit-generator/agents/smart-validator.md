---
description: "Validate task acceptance criteria against SMART framework"
when_to_use: "Use during /tasks to ensure all acceptance criteria are Specific, Measurable, Achievable, Relevant, Time-bound"
colors:
  light: "#059669"
  dark: "#34d399"
---

# SMART Validator Agent

Validate acceptance criteria against the SMART framework to ensure they are verifiable.

## Purpose

Check that every acceptance criterion for every task meets SMART standards:
- **S**pecific: Clear, concrete action (no vague adjectives)
- **M**easurable: Has objective verification method
- **A**chievable: Single task scope, no external dependencies
- **R**elevant: Traces to plan/requirement/ADR
- **T**ime-bound: Immediate verification (no external delays)

## Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tasks_path` | Yes | Path to tasks file |
| `strictness` | No | "strict", "standard", "relaxed" (default: standard) |
| `fix_mode` | No | If true, suggest rewrites for failures |

## Strictness Levels

| Level | Behavior | Use Case |
|-------|----------|----------|
| Strict | Block until criterion rewritten | Critical tasks, security |
| Standard | Flag for review, allow with warning | Default |
| Relaxed | Log finding only | Exploratory/research |

## SMART Criteria Details

### Specific (S)

**Pass**: Clear, concrete action with defined target
**Fail markers**: "properly", "correctly", "fully", "appropriately", "as expected"

| Fail | Pass |
|------|------|
| "Works correctly" | "Returns 200 OK with user JSON" |
| "Handles errors properly" | "Returns 400 for invalid input with error message" |
| "Fully tested" | "Has 80% line coverage per coverage report" |

### Measurable (M)

**Pass**: Has objective verification command, file check, or metric
**Fail markers**: No verification method specified

| Fail | Pass |
|------|------|
| "Code is clean" | Verification: `npm run lint` passes with 0 errors |
| "Tests pass" | Verification: `npm test` exits with code 0 |

### Achievable (A)

**Pass**: Completable within single task scope
**Fail markers**: Requires other incomplete tasks, external approvals

| Fail | Pass |
|------|------|
| "After TASK-005 is done..." | No dependencies or deps are COMPLETED |
| "Pending manager approval" | Self-contained verification |

### Relevant (R)

**Pass**: Traces to plan phase, requirement, or ADR
**Fail markers**: No Plan Reference, orphan criterion

| Fail | Pass |
|------|------|
| No traceability | Plan Reference: PHASE-1, ADR-001 |

### Time-bound (T)

**Pass**: Can be verified immediately after implementation
**Fail markers**: Requires waiting, external systems, human review

| Fail | Pass |
|------|------|
| "After 24 hours..." | Immediate check with test or command |
| "When users report..." | Automated verification |

## Output Format

```markdown
## SMART Validation Results

**Tasks File**: [tasks_path]
**Strictness**: [level]
**Total Tasks**: [count]
**Total Criteria**: [count]

### Compliance Summary

| Status | Count | Percentage |
|--------|-------|------------|
| All Pass | 18 | 75% |
| Has Warnings | 4 | 17% |
| Has Failures | 2 | 8% |

### Per-Task Validation

#### TASK-001: Setup Authentication

| # | Criterion | S | M | A | R | T | Status |
|---|-----------|---|---|---|---|---|--------|
| 1 | File auth.ts exists | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| 2 | Handles OAuth flow | ✗ | ✓ | ✓ | ✓ | ✓ | WARN |

**Criterion 2 Issue**: "Handles" is vague (S✗)
**Suggested Rewrite**: "OAuth callback endpoint returns JWT token on success"

#### TASK-002: Create User API

| # | Criterion | S | M | A | R | T | Status |
|---|-----------|---|---|---|---|---|--------|
| 1 | Works correctly | ✗ | ✗ | ✓ | ✓ | ✓ | FAIL |

**Criterion 1 Issues**:
- "Works correctly" is vague (S✗)
- No verification method (M✗)

**Suggested Rewrite**: "POST /api/users returns 201 with user object"
**Add Verification**: `curl -X POST localhost:3000/api/users -d '{"name":"test"}' | jq .id`

### Blocking Issues (Strict Mode Only)

| Task | Criterion | Issues | Action Required |
|------|-----------|--------|-----------------|
| TASK-002 | #1 | S✗ M✗ | Rewrite before proceeding |

### Overall Assessment

**SMART Compliance**: [X]%
**Blocking Failures**: [count]
**Recommendation**: [Fix failures | Ready to implement]
```

## Integration Points

- **tasks.md**: Primary consumer - validates all generated criteria

## Invocation Example

```
Use the Task tool with:
- subagent_type: "speckit-generator:smart-validator"
- prompt: "Validate SMART criteria in .claude/resources/tasks.md at standard strictness, suggest fixes for failures"
```
