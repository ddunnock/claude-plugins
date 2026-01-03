# Specification Analysis State

## Document Under Analysis
- **Title**: [DOCUMENT_TITLE]
- **Version**: [VERSION_OR_DATE]
- **Hash**: [CONTENT_HASH_FOR_CHANGE_DETECTION]
- **Type**: [Concept | Draft Spec | Detailed Design | Implementation Plan | Review]

## Mode Selection
- **Selected Mode**: [SIMPLE | COMPLEX]
- **Override**: [Yes/No - if Yes, original recommendation was X]
- **Rationale**: [Why this mode was selected or overridden]

## Analysis Iterations

| Iteration | Date | Phase | Trigger | Key Changes |
|-----------|------|-------|---------|-------------|
| 1 | [DATE] | ASSESS | Initial analysis | Mode selected: [MODE] |

## Current Phase
- **Phase**: [0:ASSESS | 1:INGEST | 2:ANALYZE | 3:PRESENT | 4:ITERATE | 5:SYNTHESIZE | 6:OUTPUT]
- **Status**: [In Progress | Awaiting User Confirmation | Complete]

---

## Open Questions

### Unanswered
| ID | Question | Category | Raised In | Blocks |
|----|----------|----------|-----------|--------|
| Q1 | [QUESTION] | [Technical/Process/Scope/Stakeholder/Timeline] | Phase X: NAME | [Finding IDs or "None"] |

### Answered
| ID | Question | Answer | Answered By | Answered In |
|----|----------|--------|-------------|-------------|
| Q2 | [QUESTION] | [ANSWER] | [User/Analysis] | Phase X: NAME |

### Deferred
| ID | Question | Reason | Deferred In | Revisit When |
|----|----------|--------|-------------|--------------|
| Q3 | [QUESTION] | [Out of scope/Future phase/etc.] | Phase X: NAME | [Trigger condition] |

---

## Active Findings

### Critical (🔴)
<!-- Issues that block progress -->

### High (🟠)
<!-- Significant risks requiring attention -->

### Medium (🟡)
<!-- Notable issues to plan for -->

### Low (🟢)
<!-- Minor concerns for opportunistic fix -->

## Resolved Findings

| ID | Resolution | Iteration | Resolved In | Notes |
|----|------------|-----------|-------------|-------|
<!-- Findings closed through iteration -->

---

## Assumption Register

| ID | Assumption | Category | Status | Validation Method | Risk if False |
|----|------------|----------|--------|-------------------|---------------|
| A1 | [ASSUMPTION] | Tech/Org/Env | [Unverified/Confirmed/Rejected] | [HOW_TO_CHECK] | [IMPACT] |

## User-Provided Constraints

<!-- Constraints, decisions, and boundaries provided by user during analysis -->
| Constraint | Provided In | Impact |
|------------|-------------|--------|

---

## SEAMS Analysis Summary

### Structure
<!-- Component cohesion, coupling, boundary clarity -->

### Execution
<!-- Happy path, edge cases, failure modes, recovery -->

### Assumptions
<!-- Key assumptions cataloged above -->

### Mismatches
<!-- Requirements ↔ Design ↔ Implementation alignment -->

### Stakeholders
<!-- Perspectives considered: Operator, Security, Integrator, User, Maintainer -->

## Critical Path Summary
<!-- Only populated in COMPLEX mode -->

### Dependencies
<!-- Key dependency chains identified -->

### Single Points of Failure
<!-- SPOFs identified and mitigation status -->

### Bottlenecks
<!-- Potential throughput limiters -->

---

## Output Structure (Phase 5+)

### SIMPLE Mode
- Single output: `refined-specification.md`

### COMPLEX Mode
- Domain specifications: [List planned files]
- Cross-cutting: `cross-cutting-concerns.md` (if applicable)
- Open items: `open-items.md`

---

## Next Steps

<!-- Recommended actions based on current analysis state -->
1. [ACTION_1]
2. [ACTION_2]
