# Plan Structure Reference

Guidelines for structuring implementation plans in simple and complex modes.

## Table of Contents
- [Simple vs Complex Plans](#simple-vs-complex-plans)
- [Simple Plan Structure](#simple-plan-structure)
- [Complex Plan Structure](#complex-plan-structure)
- [Plan Content Guidelines](#plan-content-guidelines)
- [Requirements Traceability](#requirements-traceability)
- [Architecture Decisions](#architecture-decisions)

---

## Simple vs Complex Plans

### When to Use Simple Mode

- Single functional domain
- Fewer than 10 pages of specifications
- 1-2 stakeholders
- Clear, well-defined scope
- No significant domain boundaries

### When to Use Complex Mode

- Multiple distinct functional domains
- More than 10 pages of specifications
- 3+ stakeholders with different concerns
- Ambiguous or evolving scope
- Clear domain boundaries (auth, API, UI, etc.)

---

## Simple Plan Structure

Single `plan.md` file with complete implementation approach.

```markdown
# Implementation Plan

## Document Info
- Spec Source: [spec file]
- Created: [date]
- Last Updated: [date]
- Version: [version]

## Overview

[2-3 paragraph summary of what will be built and the approach]

## Requirements Mapping

| Req ID | Description | Status | Plan Section |
|--------|-------------|--------|--------------|
| REQ-001 | User authentication | Covered | §2.1 |
| REQ-002 | Data persistence | Covered | §2.2 |
| REQ-003 | API endpoints | Covered | §3.1 |

## Architecture Decisions

### AD-001: [Decision Title]
**Status**: Accepted
**Context**: [Why this decision is needed]
**Decision**: [What was decided]
**Rationale**: [Why this option was chosen]
**Consequences**: [What this means for implementation]
**Alternatives Considered**:
- Option A: [Description] - Rejected because [reason]
- Option B: [Description] - Rejected because [reason]

### AD-002: [Decision Title]
...

## Implementation Approach

### Phase 1: Foundation
**Objective**: [What this phase achieves]
**Scope**:
- [Item 1]
- [Item 2]
**Prerequisites**: None
**Outputs**: [What exists after this phase]

### Phase 2: Core Features
**Objective**: [What this phase achieves]
**Scope**:
- [Item 1]
- [Item 2]
**Prerequisites**: Phase 1 complete
**Outputs**: [What exists after this phase]

### Phase 3: Integration & Polish
**Objective**: [What this phase achieves]
**Scope**:
- [Item 1]
- [Item 2]
**Prerequisites**: Phase 2 complete
**Outputs**: [What exists after this phase]

## Verification Strategy

### Unit Testing
[Approach for unit tests]

### Integration Testing
[Approach for integration tests]

### Acceptance Testing
[How to verify spec compliance]

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Medium | High | [Mitigation approach] |

## Notes for Task Generation

[Guidance for the /speckit.tasks command]
- [Note 1]
- [Note 2]
```

---

## Complex Plan Structure

Master `plan.md` with references to domain-specific plans.

### Master Plan

```markdown
# Master Implementation Plan

## Document Info
- Spec Source: [spec file]
- Created: [date]
- Last Updated: [date]
- Version: [version]
- Mode: Complex (Multi-Domain)

## Overview

[High-level summary of the entire project]

## Domain Overview

| Domain | Plan File | Priority | Dependencies | Status |
|--------|-----------|----------|--------------|--------|
| Authentication | plans/auth-plan.md | P1 | None | Draft |
| API | plans/api-plan.md | P1 | Auth | Draft |
| UI | plans/ui-plan.md | P2 | API | Draft |
| Reporting | plans/reporting-plan.md | P3 | API, UI | Pending |

## Cross-Domain Concerns

### Shared Data Models
[Data structures used across domains]

### Integration Points
[How domains connect to each other]

### Common Infrastructure
[Shared services, utilities, configurations]

### Security Boundaries
[Cross-cutting security concerns]

## Execution Order

```
Phase 1: Authentication Domain
    ↓
Phase 2: API Domain (parallel where possible)
    ↓
Phase 3: UI Domain
    ↓
Phase 4: Reporting Domain
    ↓
Phase 5: Integration & Polish
```

## Global Architecture Decisions

### GAD-001: [Cross-Domain Decision]
**Affects**: All domains
**Decision**: [What was decided]
**Rationale**: [Why]

## Domain Summaries

### Authentication
**Owner**: [Team/Person]
**Scope**: User registration, login, session management
**Key Decisions**: OAuth 2.0, JWT tokens
**See**: plans/auth-plan.md

### API
**Owner**: [Team/Person]
**Scope**: REST endpoints, data validation
**Key Decisions**: OpenAPI spec, versioning strategy
**See**: plans/api-plan.md

### UI
**Owner**: [Team/Person]
**Scope**: React components, state management
**Key Decisions**: Next.js, Tailwind
**See**: plans/ui-plan.md

## Global Risks

| Risk | Domains Affected | Mitigation |
|------|------------------|------------|
| [Risk 1] | Auth, API | [Approach] |

## Notes for Task Generation
[Global guidance for /speckit.tasks]
```

### Domain Plan Template

```markdown
# [Domain Name] Plan

## Domain Info
- Parent Plan: plan.md
- Domain: [Domain Name]
- Priority: [P1/P2/P3]
- Dependencies: [List]

## Scope

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1] (covered by [other domain])

## Requirements Covered

| Req ID | Description | Status |
|--------|-------------|--------|
| REQ-001 | ... | Covered |

## Domain Architecture Decisions

### DAD-001: [Domain-Specific Decision]
**Context**: [Why needed]
**Decision**: [What decided]
**Rationale**: [Why]

## Implementation Approach

### Phase 1: [Domain Phase 1]
**Objective**: ...
**Scope**: ...
**Prerequisites**: ...

### Phase 2: [Domain Phase 2]
...

## Integration Points

### Provides To Other Domains
- [Service/API] used by [Domain]

### Requires From Other Domains
- [Service/API] from [Domain]

## Verification Strategy

### Domain-Specific Tests
[How to test this domain in isolation]

### Integration Tests
[How to test integration with other domains]

## Domain Risks

| Risk | Mitigation |
|------|------------|
| ... | ... |

## Notes for Task Generation
[Domain-specific guidance]
```

---

## Plan Content Guidelines

### Plans SHOULD Contain

| Content | Purpose |
|---------|---------|
| Requirements mapping | Traceability |
| Architecture decisions | Design rationale |
| Phase definitions | Execution structure |
| Verification strategy | Quality assurance |
| Risk identification | Risk management |

### Plans SHOULD NOT Contain

| Content | Reason |
|---------|--------|
| Individual tasks | That's /speckit.tasks |
| Implementation code | Too detailed |
| Time estimates | Out of scope |
| Detailed how-to | Too prescriptive |

---

## Requirements Traceability

Every requirement must map to a plan section:

```markdown
## Requirements Mapping

| Req ID | Description | Coverage | Plan Section | Notes |
|--------|-------------|----------|--------------|-------|
| REQ-001 | User login | Full | §2.1 | |
| REQ-002 | Password reset | Full | §2.2 | |
| REQ-003 | 2FA | Partial | §2.3 | Deferred to Phase 2 |
| REQ-004 | SSO | None | - | Out of scope |
```

Coverage levels:
- **Full**: Completely addressed
- **Partial**: Partially addressed, with notes
- **None**: Not addressed, with reason

---

## Architecture Decisions

Use Architecture Decision Records (ADR) format:

```markdown
### AD-001: Database Selection

**Status**: Accepted | Superseded | Deprecated

**Context**:
The application needs persistent data storage. We need to choose
between SQL and NoSQL options based on our data model and scale.

**Decision**:
We will use PostgreSQL as our primary database.

**Rationale**:
- Relational data model fits our domain
- Strong ACID compliance needed for financial data
- Team has PostgreSQL expertise
- Excellent tooling and ecosystem

**Consequences**:
- Need to set up PostgreSQL infrastructure
- Schema migrations required
- Connection pooling needed for scale

**Alternatives Considered**:
1. **MongoDB**: Rejected - relational model better fits our needs
2. **MySQL**: Rejected - PostgreSQL has better JSON support
3. **SQLite**: Rejected - not suitable for production scale
```

Decisions are referenced by ID in tasks:
```markdown
**Plan Reference**: AD-001, PHASE-1
```
