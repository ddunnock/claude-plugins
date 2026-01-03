# Requirements Traceability Matrix

## Document Information
- **Project**: [PROJECT_NAME]
- **Generated**: [DATE]
- **Mode**: [SIMPLE | COMPLEX]
- **Analysis State**: [link to analysis-state.md]

---

## Coverage Summary

| Metric | Value |
|--------|-------|
| A-Spec Files | [count] |
| Total A-Spec Requirements | [count] |
| B-Spec Files | [count] |
| Total B-Spec Requirements | [count] |
| **Overall Coverage** | **[X]%** |

### Coverage Breakdown
| Category | Count | Percentage |
|----------|-------|------------|
| Fully Covered | [count] | [X]% |
| Partially Covered | [count] | [X]% |
| Not Covered (GAP) | [count] | [X]% |

---

## Coverage by Domain

| Domain | A-Spec | A-Reqs | B-Specs | B-Reqs | Coverage | Status |
|--------|--------|--------|---------|--------|----------|--------|
| [Domain 1] | [filename] | [count] | [count] | [count] | [X]% | [Draft/Reviewed/Approved/Baselined] |
| [Domain 2] | [filename] | [count] | [count] | [count] | [X]% | [Draft/Reviewed/Approved/Baselined] |
| **TOTAL** | **[count]** | **[count]** | **[count]** | **[count]** | **[X]%** | - |

---

## Full Traceability Matrix

### [Domain 1]

#### A-Spec: [domain1]-a-spec.md

| A-Spec Requirement | Description | B-Spec Requirement(s) | Coverage | Verification |
|--------------------|-------------|----------------------|----------|--------------|
| A-REQ-DOM1-001 | [Brief description] | B-REQ-DOM1-001, B-REQ-DOM1-002 | Full | Test |
| A-REQ-DOM1-002 | [Brief description] | B-REQ-DOM1-003 | Full | Analysis |
| A-REQ-DOM1-003 | [Brief description] | B-REQ-DOM1-004 | Partial | Test |
| A-REQ-DOM1-004 | [Brief description] | - | **GAP** | - |

#### Domain Coverage: [X]%

---

### [Domain 2]

#### A-Spec: [domain2]-a-spec.md

| A-Spec Requirement | Description | B-Spec Requirement(s) | Coverage | Verification |
|--------------------|-------------|----------------------|----------|--------------|
| A-REQ-DOM2-001 | [Brief description] | B-REQ-DOM2-001 | Full | Inspection |
| A-REQ-DOM2-002 | [Brief description] | B-REQ-DOM2-002, B-REQ-DOM2-003 | Full | Test |

#### Domain Coverage: [X]%

---

## Gap Analysis

### Uncovered Requirements (Critical)

A-Spec requirements with NO B-Spec coverage:

| A-Spec Req | Domain | Description | Impact | Recommended Action |
|------------|--------|-------------|--------|-------------------|
| A-REQ-XXX-001 | [Domain] | [Brief] | [High/Medium/Low] | [Create B-Spec / Defer / Accept risk] |
| A-REQ-XXX-002 | [Domain] | [Brief] | [High/Medium/Low] | [Create B-Spec / Defer / Accept risk] |

### Partially Covered Requirements

A-Spec requirements with incomplete B-Spec coverage:

| A-Spec Req | Domain | What's Missing | Impact | Recommended Action |
|------------|--------|----------------|--------|-------------------|
| A-REQ-XXX-003 | [Domain] | [Specific gap] | [High/Medium/Low] | [Add B-Req / Accept as-is] |

---

## Verification Status

Summary of verification methods assigned to B-Spec requirements:

| Verification Method | Count | Percentage | Notes |
|--------------------|-------|------------|-------|
| Test | [count] | [X]% | Automated or manual testing |
| Analysis | [count] | [X]% | Design review, calculation |
| Inspection | [count] | [X]% | Code review, audit |
| Demonstration | [count] | [X]% | Prototype, walkthrough |
| Not Specified | [count] | [X]% | **Needs attention** |
| **TOTAL** | **[count]** | **100%** | - |

---

## Cross-Domain Dependencies

Requirements with dependencies across domains:

| Requirement | Domain | Depends On | Dependency Domain | Status |
|-------------|--------|------------|-------------------|--------|
| B-REQ-DOM1-005 | Domain 1 | B-REQ-DOM2-001 | Domain 2 | [Resolved/Active] |

---

## Validation History

| Date | Validator | Action | Findings |
|------|-----------|--------|----------|
| [DATE] | [Phase 7] | Initial RTM generation | [count] gaps identified |
| [DATE] | [User] | Gap review | [count] gaps addressed |

---

## Notes

<!-- Additional context, decisions, or observations about traceability -->
