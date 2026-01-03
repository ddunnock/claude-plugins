# SpecKit Deliverable Principles
## INCOSE & SDLC-Aligned Standards for Automation Outputs

## Table of Contents

1. [Foundational Frameworks](#foundational-frameworks)
2. [The Seven Principles](#the-seven-principles)
3. [Universal Template Structure](#universal-template-structure)
4. [Artifact-Specific Guidance](#artifact-specific-guidance)
5. [Process for New Deliverables](#process-for-new-deliverables)

---

## Foundational Frameworks

### INCOSE Technical Processes (ISO/IEC/IEEE 15288)

```
TECHNICAL PROCESSES
├── Business/Mission Analysis      → ConOps, MOEs, Stakeholder Needs
├── Stakeholder Needs Definition   → StRS, Context Diagrams
├── System Requirements Definition → SyRS, Traceability Matrix
└── Architecture Definition        → Architecture Description (AD)

TECHNICAL MANAGEMENT PROCESSES
├── Project Planning               → SEMP, WBS, Schedule
├── Decision Analysis              → Trade Study Reports
├── Risk Management                → Risk Register, Mitigation Plans
└── Configuration Management       → Baselines, Change Records
```

### SDLC Phase-Artifact Mapping

| Phase | Primary Artifacts | Character |
|-------|------------------|-----------|
| Concept | ConOps, Feasibility Study | Exploratory, narrative |
| Requirements | SRS/SyRS, Use Cases | Structured, traceable |
| Design | SDD, ICD, Views | Technical, hierarchical |
| Implementation | Code, Unit Tests | Executable |
| Verification | Test Plans, Reports | Procedural, evidence-based |
| Deployment | Release Notes | Operational |
| Maintenance | Change Requests | Incremental |

---

## The Seven Principles

### Principle 1: Traceability by Design

**INCOSE Foundation**: Every system element shall be traceable to a justified need (SE Handbook 4.3).

**Template Implementation:**
```markdown
## Traceability

| This Artifact | Traces To (Parent) | Traces From (Child) |
|---------------|-------------------|---------------------|
| [ARTIFACT_ID] | [PARENT_REF]      | [CHILD_REFS]        |

**Traceability Rationale**: [Why this artifact exists]
```

**Application:**
- Requirements trace to stakeholder needs
- Design elements trace to requirements
- Test cases trace to requirements
- Decisions trace to trade study criteria

---

### Principle 2: Artifact Maturity States

**INCOSE Foundation**: Work products progress through defined maturity states (SE Handbook 5.1).

**States:**

| State | Definition | Allowed Operations |
|-------|------------|-------------------|
| **DRAFT** | Initial capture, incomplete | Create, Edit, Comment |
| **IN_REVIEW** | Under stakeholder review | Comment, Approve/Reject |
| **BASELINED** | Approved, change-controlled | Read, Change Request only |
| **SUPERSEDED** | Replaced by newer version | Read only, Archive |

**Template Implementation:**
```markdown
## Document Control

| Field | Value |
|-------|-------|
| Status | [DRAFT | IN_REVIEW | BASELINED | SUPERSEDED] |
| Version | [MAJOR.MINOR] |
| Baseline ID | [BASELINE_REF or N/A] |
| Effective Date | [DATE or TBD] |
```

---

### Principle 3: Verification Evidence Binding

**INCOSE Foundation**: Verification demonstrates system fulfills requirements (SE Handbook 4.11).

**Template Implementation:**
```markdown
## Verification Matrix

| Requirement | Method | Evidence | Status |
|-------------|--------|----------|--------|
| [REQ_ID] | [I/A/D/T] | [EVIDENCE_REF] | [PASS/FAIL/OPEN] |

**Methods:**
- I = Inspection (document review)
- A = Analysis (modeling, calculation)
- D = Demonstration (functional operation)
- T = Test (formal test procedure)
```

---

### Principle 4: Decision Rationale Capture

**INCOSE Foundation**: Decision Analysis ensures systematic evaluation (SE Handbook 5.4).

**Template Implementation:**
```markdown
## Decision Record

### Context
**Problem Statement**: [What decision is needed]
**Constraints**: [Non-negotiable boundaries]
**Assumptions**: [Conditions assumed true]

### Alternatives Considered

| ID | Alternative | Description |
|----|-------------|-------------|
| A1 | [NAME] | [DESCRIPTION] |

### Evaluation Criteria

| ID | Criterion | Weight | Rationale |
|----|-----------|--------|-----------|
| C1 | [NAME] | [0.0-1.0] | [Why this matters] |

### Evaluation Results

| Alternative | C1 | C2 | Weighted Score |
|-------------|----|----|----------------|
| A1 | [SCORE] | [SCORE] | [TOTAL] |

### Decision
**Selected**: [ALTERNATIVE_ID]
**Rationale**: [Why selected]
**Dissenting Views**: [Disagreements]
**Risk Accepted**: [Inherent risks]
```

---

### Principle 5: Stakeholder-Appropriate Abstraction

**INCOSE Foundation**: Views present information appropriate to stakeholder concerns (ISO/IEC/IEEE 42010).

**Abstraction Levels:**

| Audience | Focus | Level | Language |
|----------|-------|-------|----------|
| Executive | Outcomes, cost, schedule | High | Business terms |
| Program Manager | Progress, risks | Medium | Program terms |
| Technical Lead | Architecture, interfaces | Medium-Low | Technical terms |
| Developer | Implementation | Low | Code/spec language |
| Operator | Procedures | Medium | Operational terms |

**Template Guidance:**
```markdown
<!--
AUDIENCE DEFINITION:
- Primary: [ROLE] - Needs [WHAT]
- Secondary: [ROLE] - Needs [WHAT]

ABSTRACTION RULES:
- Lead with [AUDIENCE] concerns
- Technical depth: [HIGH/MEDIUM/LOW]
- Assumed knowledge: [PREREQUISITES]
-->
```

---

### Principle 6: Temporal Context Preservation

**INCOSE Foundation**: Configuration management maintains integrity throughout lifecycle (SE Handbook 5.5).

**Template Implementation:**
```markdown
## Temporal Context

| Field | Value |
|-------|-------|
| Created | [ISO_DATE] |
| Last Modified | [ISO_DATE] |
| Valid From | [DATE or "Upon Approval"] |
| Valid Until | [DATE or "Until Superseded"] |
| Review Due | [DATE or N/A] |

**Point-in-Time Dependencies**:
- [Referenced artifact] as of [version/date]
```

---

### Principle 7: Completeness Criteria

**INCOSE Foundation**: Process outputs must meet defined completeness criteria.

**Template Implementation:**
```markdown
## Completeness Checklist

### Required Sections
- [ ] [Section 1] present and complete
- [ ] [Section 2] present and complete

### Required Quality Attributes
- [ ] [Attribute 1] verified
- [ ] [Attribute 2] verified

### Required Approvals
- [ ] [Role 1] approval obtained
- [ ] [Role 2] approval obtained

### TBD Resolution
- [ ] All TBD items resolved or have action plan
- [ ] All assumptions documented
```

---

## Universal Template Structure

All deliverables should follow this base structure:

```markdown
# [ARTIFACT_TITLE]

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | [ID] |
| Version | [VERSION] |
| Status | [STATUS] |
| Author | [AUTHOR] |
| Date | [DATE] |
| Classification | [CLASSIFICATION] |

## 2. Purpose & Scope

**Purpose**: [Why this document exists]
**Scope**: [What it covers and doesn't cover]
**Audience**: [Who should read this]

## 3. Traceability

### 3.1 Parent Trace
| This Element | Traces To |
|--------------|-----------|
| [ELEMENT] | [PARENT_REF] |

### 3.2 Child Trace
| Child Element | Traces From |
|---------------|-------------|
| [CHILD_REF] | [THIS_ELEMENT] |

## 4. [Main Content Sections]

[Artifact-specific content]

## 5. Verification

| Element | Method | Evidence | Status |
|---------|--------|----------|--------|
| [ELEMENT] | [I/A/D/T] | [EVIDENCE] | [STATUS] |

## Appendices

### A. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| [VER] | [DATE] | [AUTHOR] | [DESCRIPTION] |

### B. Open Items

| ID | Description | Owner | Due | Status |
|----|-------------|-------|-----|--------|
| [TBD_ID] | [DESCRIPTION] | [OWNER] | [DATE] | [STATUS] |

### C. Assumptions Log

| ID | Assumption | Rationale | Validation | Risk |
|----|------------|-----------|------------|------|
| [A_ID] | [ASSUMPTION] | [WHY] | [HOW TO VERIFY] | [IF WRONG] |
```

---

## Artifact-Specific Guidance

### Requirements Artifacts (SyRS, SRS, IRD)

**INCOSE Process**: System Requirements Definition (6.4.4)

```markdown
## Requirements

### Functional Requirements

| ID | Requirement | Rationale | Parent | Priority | V-Method |
|----|-------------|-----------|--------|----------|----------|
| FR-001 | The system shall [VERB] [OBJECT] [CONSTRAINT] | [WHY] | [NEED_REF] | [M/S/C/W] | [I/A/D/T] |

**Priority Key**: M=Must, S=Should, C=Could, W=Won't (MoSCoW)
```

### Architecture Artifacts (SDD, ICD)

**INCOSE Process**: Architecture Definition (6.4.3)

```markdown
## Architecture Views

### Functional View
[What the system does - functions and data flows]

### Physical View
[Physical components and allocation]

### Interface View
| Interface ID | From | To | Protocol | Data Elements |
|--------------|------|----|----------|---------------|
| IF-001 | [COMPONENT_A] | [COMPONENT_B] | [PROTOCOL] | [DATA] |
```

### Decision Artifacts (Trade Studies)

**INCOSE Process**: Decision Analysis (6.3.4)

```markdown
## Sensitivity Analysis

### Weight Sensitivity
| Criterion | Base Weight | +20% | -20% | Result Change |
|-----------|-------------|------|------|---------------|
| [CRITERION] | [BASE] | [SCORE] | [SCORE] | [STABLE/CHANGES] |

### Threshold Analysis
| Alternative | Score | Margin to Next | Robust? |
|-------------|-------|----------------|---------|
| [ALT] | [SCORE] | [MARGIN] | [YES/NO] |
```

### Verification Artifacts (Test Plans)

**INCOSE Process**: Verification (6.4.6)

```markdown
## Test Case

| Field | Value |
|-------|-------|
| Test ID | [TC_ID] |
| Requirement | [REQ_ID] |
| Objective | [WHAT_IS_VERIFIED] |
| Prerequisites | [REQUIRED_STATE] |
| Pass Criteria | [MEASURABLE_OUTCOME] |

### Procedure Steps

| Step | Action | Expected Result | Actual Result | P/F |
|------|--------|-----------------|---------------|-----|
| 1 | [ACTION] | [EXPECTED] | [ACTUAL] | [P/F] |
```

---

## Process for New Deliverables

When encountering a new deliverable type:

### Step 1: Identify INCOSE Process
Which technical or management process produces this artifact?

### Step 2: Define Information Flow
What inputs and outputs does this artifact have?

### Step 3: Determine Stakeholder Viewpoints
Who needs this artifact and what do they need from it?

### Step 4: Establish Completeness Criteria
How do we know this artifact is "done"?

### Step 5: Map to Command Pattern
Based on the analysis, select Generator, Analyzer, Orchestrator, or Decision.

### Step 6: Apply the Seven Principles
Verify the template includes all required elements.

---

## References

- INCOSE Systems Engineering Handbook, 5th Edition (2023)
- ISO/IEC/IEEE 15288:2023 - System life cycle processes
- ISO/IEC/IEEE 29148:2018 - Requirements engineering
- ISO/IEC/IEEE 42010:2022 - Architecture description
- IEEE 1012-2016 - Verification and Validation
