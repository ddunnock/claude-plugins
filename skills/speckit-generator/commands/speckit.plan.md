PLANS-enhanced implementation planning with ADR-style architecture decisions and requirement coverage mapping.

## Usage
- `/speckit.plan` - Plan from all specs
- `/speckit.plan spec.md` - Plan from specific spec
- `/speckit.plan --all` - Force regenerate all plans
- `/speckit.plan --status` - Show coverage without generating

## Session Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| ADR completeness | Required | Decisions must have context, rationale, consequences |
| Phase dependencies | No circular | DAG structure enforced |
| Requirement coverage | 100% target | All spec requirements traced |
| Save frequency | After each phase | Incremental validation |

---

## PLANS Taxonomy (5 Categories)

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

---

## ADR Format (MADR Template)

Each architecture decision follows this structure:

```markdown
### ADR-001: [Short title of solved problem and solution]

**Status**: proposed | accepted | rejected | deprecated | superseded by ADR-XXX
**Date**: YYYY-MM-DD
**Decision-makers**: [list]

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

#### Traceability

- **Requirements**: REQ-XXX
- **Affects Tasks**: TASK-XXX (populated after /tasks)
```

### ADR Template Levels

| Level | When to Use | Required Fields |
|-------|-------------|-----------------|
| Lightweight | Simple decisions, single-option obvious | Status, Context, Decision, Consequences |
| Standard | Multiple valid options | All except Confirmation |
| Full | Critical/security decisions | All fields |

---

## Workflow

1. **Locate specs** - Find spec files in .claude/resources/
2. **Assess complexity** - Single domain vs multi-domain
3. **PLANS coverage scan** - Evaluate all 5 categories
4. **Generate plans** - Create plan.md (and domain plans if complex)
5. **Create ADRs** - Document architecture decisions with rationale
6. **Validate** - 7-point checklist before completion
7. **Report** - Coverage summary with recommendations

---

## PLANS Coverage Scan

Before generating plans, evaluate current state:

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

---

## Output Structure

**Simple (single domain)**:
```
.claude/resources/
├── spec.md
└── plan.md
```

**Complex (multi-domain)**:
```
.claude/resources/
├── spec.md
├── plan.md              # Master plan with domain references
└── plans/
    ├── domain-a-plan.md
    ├── domain-b-plan.md
    └── domain-c-plan.md
```

## Plan Content

Plans contain:
- Requirements mapping (which spec sections covered)
- Architecture decisions (ADR format)
- Implementation approach (phases, NOT tasks)
- Verification strategy
- Notes for task generation

Plans do NOT contain:
- Individual tasks (that's /speckit.tasks)
- Implementation code
- Detailed how-to instructions

## Complexity Detection

| Indicator | Simple | Complex |
|-----------|--------|---------|
| Domains | Single | Multiple distinct |
| Page count | <10 pages | >10 pages |
| Stakeholder count | 1-2 | 3+ |

User can override detection.

## Idempotency
- Detects existing plans
- Offers update or regenerate
- Preserves manual edits with warning
- ADRs with `accepted` status never auto-modified

---

## 7-Point Validation Checklist

Before completing plan generation, verify ALL items:

```markdown
## Plan Validation

| # | Check | Status |
|---|-------|--------|
| 1 | Requirements mapping complete | [ ] |
| 2 | Coverage status documented per PLANS category | [ ] |
| 3 | ADRs have all required fields for their level | [ ] |
| 4 | Phase sequencing valid (no circular deps) | [ ] |
| 5 | Traceability established (REQ → Phase → ADR) | [ ] |
| 6 | Task generation notes present for each phase | [ ] |
| 7 | Markdown structure valid | [ ] |

**Issues found**: [count]
**Blocking issues**: [count]
```

### Validation Rules

| Check | Fail Condition | Action |
|-------|----------------|--------|
| 1. Requirements mapping | Any REQ-XXX not in plan | Block, list gaps |
| 2. Coverage status | PLANS scan incomplete | Block, complete scan |
| 3. ADR fields | Missing required field | Block, specify field |
| 4. Phase sequencing | Cycle detected | Block, show cycle |
| 5. Traceability | Orphan items | Warn, can proceed |
| 6. Task notes | Phase without notes | Warn, can proceed |
| 7. Markdown | Invalid syntax | Block, auto-fix |

---

## GATE: Required Before Proceeding

**STOP after plan generation. DO NOT proceed to `/speckit.tasks` automatically.**

After generating plans, you MUST:

1. **Present a plan summary** to the user showing:
   - PLANS coverage summary (5 categories)
   - Number of plans created (master + domain plans if complex)
   - ADR count and decisions made
   - Any assumptions or open questions identified

2. **Recommend next steps**:
   - Run `/speckit.analyze` to check plan compliance with constitution.md
   - Run `/speckit.clarify` if any `[TBD]` or `[NEEDS CLARIFICATION]` items exist
   - Review plans manually before approval

3. **Wait for explicit user approval** before proceeding to tasks

### Gate Response Template

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

Created [N] plan(s):
- plan.md (master plan)
- plans/domain-a-plan.md
- [etc.]

### Architecture Decisions

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | OAuth 2.0 for authentication | accepted |
| ADR-002 | PostgreSQL for persistence | accepted |
| ADR-003 | Next.js API routes for backend | proposed |

### Open Questions
- [Any [TBD] items or ambiguities found]

### 7-Point Validation
- [x] Requirements mapping complete
- [x] Coverage documented
- [x] ADRs complete
- [x] Phase sequencing valid
- [x] Traceability established
- [x] Task notes present
- [x] Markdown valid

### Recommended Next Steps
1. Review the generated plan(s)
2. Run `/speckit.analyze` to validate compliance
3. Run `/speckit.clarify` to resolve open questions

**Awaiting your approval before generating tasks.**
```
