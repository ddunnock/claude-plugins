# Master Implementation Plan

## Document Info
- **Spec Source**: [SPEC_FILE]
- **Created**: [DATE]
- **Last Updated**: [DATE]
- **Version**: 1.0
- **Mode**: Complex (Multi-Domain)

## Overview

[High-level summary of the entire project - 2-3 paragraphs describing what will be built and the overall approach]

## Domain Overview

| Domain | Plan File | Priority | Dependencies | Status |
|--------|-----------|----------|--------------|--------|
| [Domain 1] | plans/[domain-1]-plan.md | P1 | None | Draft |
| [Domain 2] | plans/[domain-2]-plan.md | P1 | [Domain 1] | Draft |
| [Domain 3] | plans/[domain-3]-plan.md | P2 | [Domain 2] | Pending |

## Cross-Domain Concerns

### Shared Data Models
[Data structures used across multiple domains]

### Integration Points
[How domains connect to each other - APIs, events, shared state]

### Common Infrastructure
[Shared services, utilities, configurations]

### Security Boundaries
[Cross-cutting security concerns - auth, authorization, data protection]

## Execution Order

```
Phase 1: [Domain 1] - Foundation
    ↓
Phase 2: [Domain 2] - Core
    ↓
Phase 3: [Domain 3] - Enhancement
    ↓
Phase 4: Integration & Polish
```

## Global Architecture Decisions

### GAD-001: [Cross-Domain Decision Title]
**Status**: Accepted
**Affects**: All domains
**Context**: [Why this decision is needed]
**Decision**: [What was decided]
**Rationale**: [Why this option]
**Consequences**: [What this means]

### GAD-002: [Decision Title]
[Repeat format]

## Domain Summaries

### [Domain 1]
**Owner**: [Team/Person]
**Scope**: [Brief description]
**Key Decisions**: [Major architectural choices]
**See**: plans/[domain-1]-plan.md

### [Domain 2]
**Owner**: [Team/Person]
**Scope**: [Brief description]
**Key Decisions**: [Major architectural choices]
**See**: plans/[domain-2]-plan.md

### [Domain 3]
**Owner**: [Team/Person]
**Scope**: [Brief description]
**Key Decisions**: [Major architectural choices]
**See**: plans/[domain-3]-plan.md

## Global Risks

| Risk | Likelihood | Impact | Domains Affected | Mitigation |
|------|------------|--------|------------------|------------|
| [Risk 1] | Medium | High | All | [Approach] |
| [Risk 2] | Low | Medium | [Domain 1, 2] | [Approach] |

## Notes for Task Generation

[Global guidance for the /speckit.tasks command]

- [Note 1: Guidance that applies across domains]
- [Note 2: Common patterns to follow]
- [Note 3: Constraints to respect]
