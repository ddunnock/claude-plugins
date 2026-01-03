# [Domain Name] Plan

## Domain Info
- **Parent Plan**: plan.md
- **Domain**: [Domain Name]
- **Priority**: [P1/P2/P3]
- **Dependencies**: [List of domain dependencies]
- **Owner**: [Team/Person]

## Scope

### In Scope
- [Item 1 - what this domain covers]
- [Item 2]
- [Item 3]

### Out of Scope
- [Item 1] (covered by [other domain])
- [Item 2] (future consideration)

## Requirements Covered

| Req ID | Description | Coverage | Notes |
|--------|-------------|----------|-------|
| REQ-001 | [Description] | Full | |
| REQ-002 | [Description] | Partial | [Explanation] |

## Domain Architecture Decisions

### DAD-001: [Domain-Specific Decision Title]
**Status**: Accepted
**Context**: [Why this decision is needed]
**Decision**: [What was decided]
**Rationale**: [Why this option]
**Alternatives Considered**:
- Option A: [Description] - Rejected because [reason]

### DAD-002: [Decision Title]
[Repeat format]

## Implementation Approach

### Phase 1: [Domain Phase Name]
**Objective**: [What this phase achieves]
**Scope**:
- [Item 1]
- [Item 2]
**Prerequisites**: [What must exist first]
**Outputs**: [What exists after this phase]

### Phase 2: [Domain Phase Name]
**Objective**: [What this phase achieves]
**Scope**:
- [Item 1]
- [Item 2]
**Prerequisites**: Phase 1 complete
**Outputs**: [What exists after this phase]

## Integration Points

### Provides To Other Domains
| Service/API | Consumer Domain | Contract |
|-------------|-----------------|----------|
| [Service 1] | [Domain X] | [Contract reference] |

### Requires From Other Domains
| Service/API | Provider Domain | Contract |
|-------------|-----------------|----------|
| [Service 1] | [Domain Y] | [Contract reference] |

## Verification Strategy

### Domain-Specific Tests
[How to test this domain in isolation]

### Integration Tests
[How to test integration with other domains]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Domain Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Medium | High | [Approach] |

## Notes for Task Generation

[Domain-specific guidance for /speckit.tasks]

- [Note 1: Domain-specific patterns]
- [Note 2: Constraints to respect]
