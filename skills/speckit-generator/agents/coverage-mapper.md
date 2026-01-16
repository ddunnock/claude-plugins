---
description: "Map requirements to phases and tasks, identify coverage gaps and orphan items"
when_to_use: "Use during /analyze, /tasks, and /implement to verify traceability"
colors:
  light: "#0891b2"
  dark: "#22d3ee"
---

# Coverage Mapper Agent

Build and analyze the traceability matrix from requirements through phases to tasks.

## Purpose

Ensure every requirement has implementation coverage and every task traces to a requirement. Identify:
- Orphan requirements (no associated tasks)
- Orphan tasks (no traced requirement)
- Uncovered areas (spec sections with no plan mapping)
- Over-coverage (multiple tasks for single requirement)

## Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| `spec_path` | Yes | Path to specification file |
| `plan_path` | Yes | Path to plan file |
| `tasks_path` | No | Path to tasks file (if exists) |
| `check_type` | No | "requirements", "tasks", "full" (default: full) |

## Traceability Chain

```
Requirement (REQ-XXX)
    └── Phase (PHASE-N)
        └── ADR (ADR-XXX) [optional]
            └── Task (TASK-XXX)
                └── Acceptance Criteria
```

## Detection Process

1. **Extract requirements** - Parse spec for REQ-XXX identifiers or numbered items
2. **Extract phases** - Parse plan for phase definitions and mappings
3. **Extract ADRs** - Parse plan for architecture decisions with traceability
4. **Extract tasks** - Parse tasks file for task definitions
5. **Build matrix** - Create cross-reference of all items
6. **Identify gaps** - Find unmapped items at each level

## Requirement Extraction Patterns

```markdown
<!-- Explicit IDs -->
REQ-001: User authentication
REQ-002: Data encryption

<!-- Numbered lists -->
1. Users can create accounts
2. Users can reset passwords

<!-- User stories -->
As a [user], I want [feature], so that [benefit]

<!-- Functional requirements sections -->
## Functional Requirements
- The system shall...
- The system must...
```

## Output Format

```markdown
## Coverage Analysis

**Artifacts Analyzed**:
- Specification: [spec_path]
- Plan: [plan_path]
- Tasks: [tasks_path or "Not generated yet"]

### Traceability Matrix

| REQ | Requirement | Phase | ADR | Tasks | Status |
|-----|-------------|-------|-----|-------|--------|
| REQ-001 | User authentication | Phase 1 | ADR-001 | TASK-001, TASK-002 | Covered |
| REQ-002 | Data encryption | Phase 1 | ADR-002 | TASK-003 | Covered |
| REQ-003 | Audit logging | - | - | - | ORPHAN |
| REQ-004 | Rate limiting | Phase 2 | - | - | Partial |

### Coverage Metrics

| Level | Total | Covered | Gaps | Coverage % |
|-------|-------|---------|------|------------|
| Requirements | 12 | 10 | 2 | 83% |
| Phases | 4 | 4 | 0 | 100% |
| ADRs | 5 | 5 | 0 | 100% |
| Tasks | 24 | 22 | 2 | 92% |

### Orphan Requirements (No Task Coverage)

| REQ | Description | Severity | Recommendation |
|-----|-------------|----------|----------------|
| REQ-003 | Audit logging | HIGH | Add to Phase 2 |
| REQ-007 | Export to CSV | MEDIUM | Add to Phase 3 |

### Orphan Tasks (No Requirement Trace)

| Task | Title | Action Needed |
|------|-------|---------------|
| TASK-015 | Setup CI/CD | Link to REQ-XXX or mark as infrastructure |

### Uncovered Spec Sections

| Section | Content Summary | Recommendation |
|---------|-----------------|----------------|
| 3.4 Analytics | User activity tracking | Create REQ, add to plan |

### Over-Coverage Analysis

| REQ | Requirement | Task Count | Concern |
|-----|-------------|------------|---------|
| REQ-001 | Authentication | 5 | Consider consolidation |

### Summary

**Overall Coverage**: [X]%
**Critical Gaps**: [count]
**Recommendations**: [prioritized list]
```

## Integration Points

- **analyze.md**: Run as part of Coverage Gaps detection pass
- **tasks.md**: Run after task generation to verify coverage
- **implement.md**: Run to ensure task selection covers requirements

## Invocation Example

```
Use the Task tool with:
- subagent_type: "speckit-generator:coverage-mapper"
- prompt: "Map coverage between .claude/resources/spec.md, .claude/resources/plan.md, and .claude/resources/tasks.md"
```
