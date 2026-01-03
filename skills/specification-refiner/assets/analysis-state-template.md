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
- **Phase**: [0:ASSESS | 1:INGEST | 2:ANALYZE | 3:PRESENT | 4:ITERATE | 5:SYNTHESIZE | 6:OUTPUT | 7:VALIDATE]
- **Status**: [In Progress | Awaiting User Confirmation | Complete]

---

## Specification Status

### Status Definitions
- **Draft**: Initial output from Phase 6, pending review
- **Reviewed**: Technical review complete, no major gaps
- **Approved**: Stakeholder sign-off received
- **Baselined**: Locked for change control

### Current Spec Status
| Specification | Type | Status | Last Changed | Changed By |
|---------------|------|--------|--------------|------------|
| [spec-name] | A-Spec | Draft | [date] | Phase 6 |
| [spec-name] | B-Spec | Draft | [date] | Phase 6 |

### Status History
| Date | Specification | From | To | Reason | Approved By |
|------|---------------|------|-----|--------|-------------|
| [date] | [spec-name] | Draft | Reviewed | [reason] | [user] |

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

## Requirements Traceability Summary

### Coverage Metrics
| Metric | Value |
|--------|-------|
| Total A-Spec Requirements | [count] |
| Total B-Spec Requirements | [count] |
| Coverage Percentage | [X]% |
| Fully Covered A-Reqs | [count] |
| Partially Covered A-Reqs | [count] |
| Uncovered A-Reqs (GAPS) | [count] |

### Gap Summary
<!-- A-Spec requirements with no B-Spec coverage -->
| A-Spec Requirement | Gap Status | Impact | Notes |
|--------------------|------------|--------|-------|
| A-REQ-XXX-001 | No coverage | [High/Med/Low] | [reason/plan] |

### Traceability Notes
<!-- Key observations about requirement coverage -->

---

## Output Structure (Phase 5+)

### SIMPLE Mode
- Single A-Spec output: `refined-specification.md`
- Requirements format: `A-REQ-NNN`
- Status: Draft (initial), progresses through validation

### COMPLEX Mode
- A-Spec files: [List planned A-Spec files by domain]
- B-Spec files: [List planned B-Spec files by subsystem]
- Requirements format: `A-REQ-[DOMAIN]-NNN`, `B-REQ-[DOMAIN]-NNN`
- Traceability: `traceability-matrix.md`
- Cross-cutting: `cross-cutting-concerns.md` (if applicable)
- Open items: `open-items.md`
- All specs status: Draft (initial), progresses through validation

---

## Next Steps

<!-- Recommended actions based on current analysis state -->
1. [ACTION_1]
2. [ACTION_2]
