# Plan Workflow Reference

Detailed workflow for the `/speckit.plan` command.

## Purpose

Create implementation plans from specification files. Plans define WHAT will be built and HOW it will be approached at a high level, without detailing individual tasks.

## Idempotency

- Detects existing plan files
- Offers to update or regenerate
- Preserves manual annotations
- Never overwrites without confirmation

---

## Workflow Steps

### Step 1: Locate Specifications

```
1. Check .claude/resources/ for spec files
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
- **Requirements**: Individual requirements with IDs
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

### Step 4: Generate Plan(s)

#### Simple Mode (Single Plan)

Generate `plan.md`:

```markdown
# Implementation Plan

## Overview
[High-level summary]

## Requirements Mapping

| Req ID | Description | Plan Section |
|--------|-------------|--------------|
| REQ-001 | ... | §2.1 |

## Architecture Decisions

### AD-001: [Decision Title]
**Context**: [Why this decision is needed]
**Decision**: [What was decided]
**Rationale**: [Why this option]
**Alternatives Considered**: [Other options]

## Implementation Approach

### Phase 1: Foundation
**Objective**: [What this phase achieves]
**Scope**: [What's included]
**Prerequisites**: [What must exist first]

### Phase 2: Core Features
...

## Verification Strategy
[How to verify implementation meets spec]

## Notes for Task Generation
[Guidance for /speckit.tasks command]
```

#### Complex Mode (Hierarchical)

Generate `plan.md` (master) + domain plans:

**Master Plan**:
```markdown
# Master Implementation Plan

## Domain Overview

| Domain | Plan File | Priority | Dependencies |
|--------|-----------|----------|--------------|
| Authentication | plans/auth-plan.md | P1 | None |
| API | plans/api-plan.md | P1 | Auth |
| UI | plans/ui-plan.md | P2 | API |

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

## Scope
[What this domain covers]

## Requirements Covered
| Req ID | Description |
|--------|-------------|
| REQ-001 | User registration |

## Architecture Decisions
[Domain-specific decisions]

## Implementation Approach
[Phases for this domain]

## Integration Points
[How this connects to other domains]

## Verification Strategy
[Domain-specific verification]
```

### Step 5: Validate Plan

Check for:
- All requirements mapped
- No orphan plan sections
- Dependencies are satisfiable
- Phases have clear scope

Report validation results:
```
Plan Validation:
✓ All requirements mapped
✓ No orphan sections
✓ Dependencies valid
⚠ Phase 2 scope overlaps with Phase 3

Issues found: 1 warning

Options:
1. Continue anyway
2. Revise plan
```

### Step 6: Save and Report

```
Plan generated:
- plan.md (master)
- plans/auth-plan.md
- plans/api-plan.md
- plans/ui-plan.md

Requirements coverage: 100%
Architecture decisions: 5

Next step: Run /speckit.tasks to generate implementation tasks
```

---

## Plan Content Guidelines

### What Plans SHOULD Contain

- High-level approach
- Architecture decisions with rationale
- Phase definitions with objectives
- Requirements traceability
- Verification strategy

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

Options:
1. Update plan (preserve structure, refresh content)
2. Regenerate plan (start fresh)
3. View differences
4. Cancel
```

Update mode:
- Preserves manual annotations marked with `<!-- MANUAL -->`
- Updates requirements mapping
- Refreshes architecture decisions
- Keeps existing phase structure unless spec changed

---

## Integration with Other Commands

### From /speckit.analyze
Plan validation integrates with analyze:
- Missing requirements flagged as GAPS
- Inconsistencies flagged as INCONSISTENCIES

### To /speckit.tasks
Plans provide:
- Phase structure for task grouping
- Requirements for task traceability
- Architecture decisions for task context
