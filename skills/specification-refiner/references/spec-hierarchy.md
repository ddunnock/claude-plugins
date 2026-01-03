# Specification Hierarchy Reference

This reference documents the A-Spec/B-Spec hierarchy used for specification generation.

## Table of Contents
- [Overview](#overview)
- [SIMPLE Mode (A-Spec Only)](#simple-mode-a-spec-only)
- [COMPLEX Mode (A-Spec/B-Spec Hierarchy)](#complex-mode-a-specb-spec-hierarchy)
- [Requirement ID Conventions](#requirement-id-conventions)
- [A-Spec Template](#a-spec-template)
- [B-Spec Template](#b-spec-template)
- [Status Definitions](#status-definitions)

---

## Overview

The specification hierarchy organizes requirements into two levels:

| Level | Name | Purpose | Used In |
|-------|------|---------|---------|
| **A-Spec** | Architecture/Aggregate Specification | High-level requirements defining WHAT the system must do | SIMPLE + COMPLEX |
| **B-Spec** | Behavioral/Build Specification | Detailed requirements defining HOW to implement | COMPLEX only |

Every B-Spec requirement must trace back to an A-Spec requirement, ensuring full coverage and traceability.

---

## SIMPLE Mode (A-Spec Only)

For single-domain, straightforward specifications:

- **Output**: Single `refined-specification.md` file
- **Requirement IDs**: `A-REQ-NNN` (e.g., A-REQ-001, A-REQ-002)
- **No B-Specs**: Implementation details embedded in A-Spec requirements
- **RTM**: Embedded summary section (100% coverage by definition)

---

## COMPLEX Mode (A-Spec/B-Spec Hierarchy)

For multi-domain, large-scale specifications:

### A-Spec Files
- **Purpose**: High-level requirements per domain
- **Naming**: `[domain]-a-spec.md` (e.g., `authentication-a-spec.md`)
- **Requirement IDs**: `A-REQ-[DOMAIN]-NNN` (e.g., A-REQ-AUTH-001)
- **Count**: One A-Spec per major domain or system area

### B-Spec Files
- **Purpose**: Detailed implementation requirements
- **Naming**: `[domain]-[subsystem]-b-spec.md` (e.g., `authentication-oauth-b-spec.md`)
- **Requirement IDs**: `B-REQ-[DOMAIN]-NNN` (e.g., B-REQ-AUTH-001)
- **Mandatory**: Each B-Spec requirement MUST include `Traces to: A-REQ-XXX-NNN`
- **Count**: One or more B-Specs per domain

### Supporting Files
- `traceability-matrix.md` - Full RTM with coverage metrics
- `cross-cutting-concerns.md` - Requirements spanning multiple domains (if applicable)
- `open-items.md` - Unresolved questions and findings

---

## Requirement ID Conventions

### Format Rules
| Mode | Spec Type | Format | Example |
|------|-----------|--------|---------|
| SIMPLE | A-Spec | `A-REQ-NNN` | A-REQ-001 |
| COMPLEX | A-Spec | `A-REQ-[DOMAIN]-NNN` | A-REQ-AUTH-001 |
| COMPLEX | B-Spec | `B-REQ-[DOMAIN]-NNN` | B-REQ-AUTH-001 |

### Domain Prefixes
Use short, consistent prefixes (3-5 characters):
- AUTH - Authentication
- DATA - Data management
- API - API/Integration
- UI - User interface
- SEC - Security
- PERF - Performance
- (Define project-specific prefixes as needed)

### Numbering
- Start at 001 within each domain
- Increment sequentially
- Do not reuse deleted IDs

---

## A-Spec Template

```markdown
# [Domain] Specification (A-Spec)

## Document Control
- **Spec ID**: A-SPEC-[DOMAIN]-[VERSION]
- **Status**: [Draft | Reviewed | Approved | Baselined]
- **Last Updated**: [DATE]
- **Author**: [NAME/ROLE]

## Overview
[High-level description of this domain's purpose and scope]

## Scope
### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1]
- [Item 2]

---

## Requirements

### A-REQ-[DOMAIN]-001: [Requirement Title]
**Priority**: [Must | Should | May]
**Category**: [Functional | Non-Functional | Constraint]

**Description**:
[Clear statement of what the system must do]

**Rationale**:
[Why this requirement exists]

**Acceptance Criteria**:
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]

**Dependencies**:
- [A-REQ-XXX-NNN if applicable]

---

### A-REQ-[DOMAIN]-002: [Requirement Title]
...

---

## Assumptions
| ID | Assumption | Status | Risk if False |
|----|------------|--------|---------------|
| ASM-001 | [Assumption text] | [Unverified/Confirmed] | [Impact] |

## Dependencies
| Dependency | Type | Status | Owner |
|------------|------|--------|-------|
| [External system/domain] | [Hard/Soft] | [Active/Resolved] | [Team] |

## Open Items
| ID | Item | Impact | Target Resolution |
|----|------|--------|-------------------|
| OI-001 | [Question/issue] | [High/Medium/Low] | [Date/Phase] |
```

---

## B-Spec Template

```markdown
# [Subsystem] Specification (B-Spec)

## Document Control
- **Spec ID**: B-SPEC-[DOMAIN]-[SUBSYSTEM]-[VERSION]
- **Parent A-Spec**: A-SPEC-[DOMAIN]-[VERSION]
- **Status**: [Draft | Reviewed | Approved | Baselined]
- **Last Updated**: [DATE]
- **Author**: [NAME/ROLE]

## Overview
[Detailed description of this subsystem and its role in satisfying parent A-Spec requirements]

## Scope
### Satisfies A-Spec Requirements
- A-REQ-[DOMAIN]-001
- A-REQ-[DOMAIN]-003
- A-REQ-[DOMAIN]-007

---

## Requirements

### B-REQ-[DOMAIN]-001: [Detailed Requirement Title]
**Traces to**: A-REQ-[DOMAIN]-001
**Priority**: [Must | Should | May]

**Description**:
[Detailed implementation requirement]

**Technical Details**:
- [Implementation detail 1]
- [Implementation detail 2]
- [Constraints and considerations]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]

**Verification Method**: [Test | Analysis | Inspection | Demonstration]

**Dependencies**:
- [B-REQ-XXX-NNN if applicable]

---

### B-REQ-[DOMAIN]-002: [Detailed Requirement Title]
**Traces to**: A-REQ-[DOMAIN]-001
...

---

## Interface Specifications

### [Interface Name]
- **Type**: [API | Event | File | Database]
- **Direction**: [Inbound | Outbound | Bidirectional]
- **Format**: [JSON | XML | Binary | etc.]
- **Contract**: [Link or inline specification]

---

## Error Handling

| Error Condition | Detection | Response | Recovery |
|-----------------|-----------|----------|----------|
| [Condition 1] | [How detected] | [System response] | [Recovery action] |

---

## Assumptions
| ID | Assumption | Status | Risk if False |
|----|------------|--------|---------------|
| ASM-001 | [Implementation assumption] | [Unverified/Confirmed] | [Impact] |

## Open Items
| ID | Item | Impact | Target Resolution |
|----|------|--------|-------------------|
| OI-001 | [Technical question/issue] | [High/Medium/Low] | [Date/Phase] |
```

---

## Status Definitions

All specifications progress through a defined status workflow:

| Status | Definition | Gate Criteria |
|--------|------------|---------------|
| **Draft** | Initial output from Phase 6 | Auto-assigned on generation |
| **Reviewed** | Technical review complete | No critical gaps, RTM coverage adequate |
| **Approved** | Stakeholder sign-off received | All high-priority issues resolved |
| **Baselined** | Locked for change control | Formal approval documented |

### Status Transitions
```
Draft -> Reviewed -> Approved -> Baselined
         ^                |
         |________________|
         (return to fix issues)
```

### Status Change Requirements
- Each transition requires explicit user approval in Phase 7
- Status changes are logged with timestamp and approver
- Regression (moving backward) requires documented justification
- Baselined specs require formal change request process to modify
