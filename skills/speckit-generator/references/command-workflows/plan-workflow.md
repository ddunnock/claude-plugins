# Plan Workflow Reference

Detailed workflow for the `/speckit.plan` command with PLANS taxonomy and ADR-style architecture decisions.

## Purpose

Create implementation plans from specification files using the PLANS taxonomy. Plans define WHAT will be built and HOW it will be approached at a high level, with formal architecture decision records (ADRs) for key choices.

## Key Features

- **PLANS Taxonomy**: 5-category systematic coverage scan
- **ADR-Style Decisions**: MADR-format architecture decisions with traceability
- **7-Point Validation**: Comprehensive checklist before completion
- **Requirement Coverage Mapping**: Full traceability from spec to plan

## Idempotency

- Detects existing plan files
- Offers to update or regenerate
- Preserves manual annotations marked with `<!-- MANUAL -->`
- ADRs with `accepted` status are never auto-modified
- Never overwrites without confirmation

---

## PLANS Taxonomy

Systematic coverage scan for implementation planning:

| Category | Focus | Detection Target |
|----------|-------|------------------|
| **P**hases | Implementation phases, milestones | Missing phases, unclear objectives |
| **L**inkages | Inter-phase dependencies | Circular deps, undefined prerequisites |
| **A**rchitecture | ADR-based decisions | Undocumented choices, missing rationale |
| **N**otes | Task generation guidance | Vague notes, unclear scope indicators |
| **S**cope | Requirement coverage mapping | Orphan requirements, coverage gaps |

### Coverage Status Markers

| Symbol | Status | Meaning |
|--------|--------|---------|
| ✓ | Complete | All items addressed |
| ◐ | Partial | Some items need attention |
| ✗ | Missing | Critical gaps exist |
| ○ | N/A | Not applicable for project |

### PLANS Activation by Project Type

| Project Type | Heavy Categories | Rationale |
|--------------|------------------|-----------|
| Greenfield | ARCHITECTURE | New decisions needed |
| Migration | LINKAGES | Dependencies critical |
| Refactoring | ARCHITECTURE, NOTES | Preserve + improve |
| Feature Addition | SCOPE, NOTES | Fit into existing |

---

## Workflow Steps

### Step 1: Locate Specifications

```
1. Check speckit/ for spec files
2. Accept explicit spec file argument
3. If no specs found, offer to create template

Spec file patterns:
- *-spec.md
- *-requirements.md
- spec.md
- requirements.md
```

### Step 2: Parse Specification

Extract from spec:
- **Domains**: Major functional areas
- **Requirements**: Individual requirements with IDs (REQ-XXX)
- **Stakeholders**: Who is involved
- **Constraints**: Technical and organizational limits
- **Dependencies**: External dependencies

### Step 3: Assess Complexity

| Factor | Simple | Complex |
|--------|--------|---------|
| Domains identified | 1 | 2+ distinct |
| Page count | <10 | >10 |
| Stakeholder count | 1-2 | 3+ |
| Scope clarity | Clear | Ambiguous |

Present to user:
```
Complexity Assessment:
- Domains: [list]
- Pages: [count]
- Stakeholders: [count]
- Scope clarity: [Clear/Moderate/Ambiguous]

Recommendation: [SIMPLE/COMPLEX]

Options:
1. Accept recommendation
2. Override to SIMPLE
3. Override to COMPLEX
```

### Step 4: PLANS Coverage Scan

Before generating plans, evaluate current state across all 5 categories:

```markdown
## PLANS Coverage Assessment

| Category | Status | Findings |
|----------|--------|----------|
| Phases | ✓ Complete | 4 phases identified from spec |
| Linkages | ◐ Partial | Phase 3 → Phase 2 dependency unclear |
| Architecture | ✗ Missing | No auth strategy defined |
| Notes | ✓ Complete | Task guidance provided |
| Scope | ✓ Complete | All 12 requirements mappable |

**Recommendation**: Proceed with planning, flag LINKAGES for clarification
```

#### PLANS Scan Process

1. **Phases (P)**: Identify all implementation phases from spec
   - Clear objectives for each phase?
   - Logical progression?
   - Milestone criteria defined?

2. **Linkages (L)**: Map dependencies between phases
   - Build dependency graph
   - Check for cycles (fail if found)
   - Identify prerequisite gaps

3. **Architecture (A)**: Identify decisions requiring ADRs
   - Technology choices
   - Design patterns
   - Integration approaches
   - Security decisions

4. **Notes (N)**: Check task generation guidance
   - Scope indicators present?
   - Complexity hints?
   - Testing requirements noted?

5. **Scope (S)**: Map requirements to plan sections
   - Every REQ-XXX traceable?
   - Coverage complete?
   - Orphan sections identified?

### Step 5: Generate Plan(s)

#### Simple Mode (Single Plan)

Generate `plan.md`:

```markdown
# Implementation Plan

## Overview
[High-level summary]

## PLANS Coverage

| Category | Status | Notes |
|----------|--------|-------|
| Phases | ✓ | 3 phases defined |
| Linkages | ✓ | Dependencies validated |
| Architecture | ✓ | 2 ADRs created |
| Notes | ✓ | Task guidance complete |
| Scope | ✓ | 8/8 requirements mapped |

## Requirements Mapping

| Req ID | Description | Plan Section | ADR |
|--------|-------------|--------------|-----|
| REQ-001 | User authentication | §2.1 | ADR-001 |
| REQ-002 | Data persistence | §2.2 | ADR-002 |

## Architecture Decisions

### ADR-001: OAuth 2.0 for Authentication

**Status**: accepted
**Date**: 2024-01-15
**Decision-makers**: Development Team

#### Context and Problem Statement

The system requires user authentication. We need to decide on an authentication mechanism that balances security, user experience, and implementation complexity.

#### Decision Drivers

* Security best practices require proven authentication
* Users expect social login options
* Implementation timeline is constrained

#### Considered Options

1. OAuth 2.0 with Google/GitHub
2. Email/password with JWT
3. Magic link (passwordless)

#### Decision Outcome

**Chosen option**: "OAuth 2.0 with Google/GitHub", because it provides industry-standard security, eliminates password management, and has well-documented Next.js integration patterns.

**Consequences**:
* Good, because users can authenticate with existing accounts
* Good, because no password storage/management needed
* Bad, because requires external service dependency

**Confirmation**: Integration tests verify OAuth flow works with test credentials

#### Traceability

- **Requirements**: REQ-001
- **Affects Tasks**: TASK-001, TASK-002, TASK-003

### ADR-002: PostgreSQL for Data Persistence
[Similar structure...]

## Implementation Approach

### Phase 1: Foundation
**Objective**: Establish project structure and authentication
**Scope**: Project setup, OAuth integration, basic user model
**Prerequisites**: None
**Notes for Tasks**: Focus on security; reference security.md

### Phase 2: Core Features
**Objective**: Implement primary functionality
**Scope**: [Feature list]
**Prerequisites**: Phase 1 complete
**Notes for Tasks**: [Guidance]

## Verification Strategy
[How to verify implementation meets spec]

## Notes for Task Generation
[Guidance for /speckit.tasks command including:
- Recommended task groupings
- Priority suggestions
- Complexity indicators
- Testing requirements]
```

#### Complex Mode (Hierarchical)

Generate `plan.md` (master) + domain plans:

**Master Plan**:
```markdown
# Master Implementation Plan

## PLANS Coverage (Master)

| Category | Status | Notes |
|----------|--------|-------|
| Phases | ✓ | Cross-domain execution order defined |
| Linkages | ✓ | Domain dependencies mapped |
| Architecture | ✓ | 5 cross-cutting ADRs |
| Notes | ✓ | Per-domain guidance linked |
| Scope | ✓ | All requirements assigned to domains |

## Domain Overview

| Domain | Plan File | Priority | Dependencies | ADRs |
|--------|-----------|----------|--------------|------|
| Authentication | plans/auth-plan.md | P1 | None | ADR-001 |
| API | plans/api-plan.md | P1 | Auth | ADR-002, ADR-003 |
| UI | plans/ui-plan.md | P2 | API | ADR-004 |

## Cross-Domain Architecture Decisions

### ADR-001: Shared Authentication Context
[ADR content...]

## Cross-Domain Concerns
- Shared data models
- Integration points
- Common infrastructure

## Execution Order
1. Authentication (foundation)
2. API (depends on Auth)
3. UI (depends on API)

## Domain Summaries

### Authentication
[Brief summary, see plans/auth-plan.md]

### API
[Brief summary, see plans/api-plan.md]
```

**Domain Plan** (e.g., `plans/auth-plan.md`):
```markdown
# Authentication Domain Plan

## PLANS Coverage (Domain)

| Category | Status | Notes |
|----------|--------|-------|
| Phases | ✓ | 2 phases for this domain |
| Linkages | ✓ | No internal cycles |
| Architecture | ✓ | 1 domain-specific ADR |
| Notes | ✓ | Task guidance complete |
| Scope | ✓ | 3/3 auth requirements covered |

## Scope
[What this domain covers]

## Requirements Covered
| Req ID | Description | ADR |
|--------|-------------|-----|
| REQ-001 | User registration | ADR-001 |
| REQ-002 | OAuth login | ADR-001 |
| REQ-003 | Session management | - |

## Architecture Decisions
[Domain-specific decisions]

## Implementation Approach
[Phases for this domain]

## Integration Points
[How this connects to other domains]

## Verification Strategy
[Domain-specific verification]

## Notes for Task Generation
[Domain-specific guidance]
```

### Step 6: 7-Point Validation

Before completing plan generation, verify ALL items:

```markdown
## Plan Validation

| # | Check | Status | Details |
|---|-------|--------|---------|
| 1 | Requirements mapping complete | ✓ | 12/12 REQ-XXX mapped |
| 2 | PLANS coverage documented | ✓ | All 5 categories assessed |
| 3 | ADRs have required fields | ✓ | 3 ADRs valid |
| 4 | Phase sequencing valid | ✓ | No cycles detected |
| 5 | Traceability established | ✓ | REQ → Phase → ADR links |
| 6 | Task generation notes present | ⚠ | Phase 3 missing notes |
| 7 | Markdown structure valid | ✓ | Linting passed |

**Issues found**: 1 warning
**Blocking issues**: 0
```

#### Validation Rules

| Check | Fail Condition | Action |
|-------|----------------|--------|
| 1. Requirements mapping | Any REQ-XXX not in plan | Block, list gaps |
| 2. PLANS coverage | Any category not assessed | Block, complete scan |
| 3. ADR fields | Missing required field | Block, specify field |
| 4. Phase sequencing | Cycle detected | Block, show cycle |
| 5. Traceability | Orphan items exist | Warn, can proceed |
| 6. Task notes | Phase without notes | Warn, can proceed |
| 7. Markdown | Invalid syntax | Block, auto-fix |

### Step 7: Save and Report

```markdown
## Plan Generation Complete

### PLANS Coverage Summary

| Category | Status | Notes |
|----------|--------|-------|
| Phases | ✓ | 4 phases defined |
| Linkages | ✓ | Dependencies validated |
| Architecture | ✓ | 3 ADRs created |
| Notes | ✓ | Task guidance complete |
| Scope | ✓ | 12/12 requirements mapped |

Created 4 plan(s):
- plan.md (master)
- plans/auth-plan.md
- plans/api-plan.md
- plans/ui-plan.md

### Architecture Decisions

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | OAuth 2.0 for authentication | accepted |
| ADR-002 | PostgreSQL for persistence | accepted |
| ADR-003 | Next.js API routes for backend | proposed |

### 7-Point Validation
- [x] Requirements mapping complete
- [x] PLANS coverage documented
- [x] ADRs complete
- [x] Phase sequencing valid
- [x] Traceability established
- [x] Task notes present
- [x] Markdown valid

Next step: Run /speckit.tasks to generate implementation tasks
```

---

## ADR Format Reference

### Template Levels

| Level | When to Use | Required Fields |
|-------|-------------|-----------------|
| Lightweight | Simple decisions, single-option obvious | Status, Context, Decision, Consequences |
| Standard | Multiple valid options | All except Confirmation |
| Full | Critical/security decisions | All fields |

### Full ADR Template (MADR)

```markdown
### ADR-XXX: [Short title of solved problem and solution]

**Status**: proposed | accepted | rejected | deprecated | superseded by ADR-XXX
**Date**: YYYY-MM-DD
**Decision-makers**: [list everyone involved]
**Consulted**: [subject-matter experts with two-way communication]
**Informed**: [stakeholders with one-way communication]

#### Context and Problem Statement

[Describe context and problem in 2-3 sentences or as a question]

#### Decision Drivers

* [driver 1, e.g., a force, concern]
* [driver 2]

#### Considered Options

1. [option 1]
2. [option 2]
3. [option 3]

#### Decision Outcome

**Chosen option**: "[option 1]", because [justification].

**Consequences**:
* Good, because [positive consequence]
* Bad, because [negative consequence]

**Confirmation**: [How implementation/compliance will be confirmed]

#### Pros and Cons of the Options

##### [option 1]
* Good, because [argument]
* Bad, because [argument]

##### [option 2]
* Good, because [argument]
* Bad, because [argument]

#### More Information

[Additional evidence, team agreement, links to related decisions]

#### Traceability

- **Requirements**: REQ-XXX, REQ-YYY
- **Affects Tasks**: TASK-XXX (populated after /tasks)
```

---

## Plan Content Guidelines

### What Plans SHOULD Contain

- High-level approach
- PLANS coverage assessment
- Architecture decisions (ADR format) with rationale
- Phase definitions with objectives
- Requirements traceability (REQ → Phase → ADR)
- Verification strategy
- Notes for task generation

### What Plans SHOULD NOT Contain

- Individual tasks (that's /speckit.tasks)
- Implementation code
- Detailed step-by-step instructions
- Time estimates

---

## Update Mode

When plan already exists:

```
Existing plan found: plan.md
Last modified: [date]
ADRs with 'accepted' status: 3

Options:
1. Update plan (preserve structure, refresh content, protect accepted ADRs)
2. Regenerate plan (start fresh, warn about accepted ADRs)
3. View differences
4. Cancel
```

Update mode:
- Preserves manual annotations marked with `<!-- MANUAL -->`
- **Never modifies ADRs with `accepted` status**
- Updates requirements mapping
- Refreshes PLANS coverage
- Keeps existing phase structure unless spec changed

---

## Integration with Other Commands

### From /speckit.clarify
Clarifications inform planning:
- Resolved ambiguities become requirements
- SEAMS findings map to PLANS categories

### From /speckit.analyze
Plan validation integrates with analyze:
- Missing requirements flagged as GAPS
- Inconsistencies flagged as INCONSISTENCIES
- ADR coverage checked

### To /speckit.tasks
Plans provide:
- Phase structure for task grouping
- Requirements for task traceability
- ADRs for task context and SMART criteria
- Notes for task generation guidance

---

## Continuation Format

After command completion, always present the next logical step using this standardized format:

```markdown
## ▶ Next Up
**{command}: {name}** — {one-line description}
`/{command}`
<sub>`/clear` first → fresh context window</sub>
```

### Next Step Logic for /plan

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| All 7 checks pass | `/tasks` | Generate implementation tasks |
| ADRs need review | Review ADRs, then `/tasks` | Get decisions approved first |
| Blocking issues | Fix issues, re-run `/plan` | Address validation failures |
| Clarifications needed | `/clarify` | Resolve ambiguities first |

### Example Output

```markdown
## ▶ Next Up
**tasks: Generate Tasks** — Create SMART-validated implementation tasks from plan
`/tasks`
<sub>`/clear` first → fresh context window</sub>
```
