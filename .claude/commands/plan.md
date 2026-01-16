---
description: "PLANS-enhanced implementation planning with ADR-style architecture decisions"
handoffs:
  - label: Analyze Plan
    agent: analyze
    prompt: Run analysis to check plan consistency
  - label: Clarify Ambiguities
    agent: clarify
    prompt: Resolve any [TBD] items in the plan
  - label: Generate Tasks
    agent: tasks
    prompt: Generate implementation tasks from this plan
---

# Plan

PLANS-enhanced implementation planning with ADR-style architecture decisions and requirement coverage mapping.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## Usage

```
/plan                   # Plan from all specs
/plan spec.md           # Plan from specific spec
/plan --all             # Force regenerate all plans
/plan --status          # Show coverage without generating
```

---

## Memory Directives

Load these directive files for architecture decision guidance:

**Always loaded:**
- `constitution.md` - Global principles, quality gates
- `security.md` - Security requirements for ADRs
- `documentation.md` - Documentation standards

**Project-specific (detected: Python, Poetry, Pyright):**
- `python.md` - Python ≥3.11 standards, type hints, docstrings
- `git-cicd.md` - Git workflow and CI/CD standards
- `testing.md` - Test coverage requirements

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

### PLANS Activation

**Active for this project (Feature Addition/Enhancement):**
- [x] **Phases**: Implementation phases, milestones
- [x] **Linkages**: Inter-phase dependencies
- [x] **Architecture**: ADR-based decisions
- [x] **Notes**: Task generation guidance
- [x] **Scope**: Requirement coverage mapping

---

## ADR Template Level

**Selected for this project:** Standard

| Level | When to Use | Required Fields |
|-------|-------------|-----------------|
| Lightweight | Simple decisions, single-option obvious | Status, Context, Decision, Consequences |
| **Standard** | Multiple valid options | All except Confirmation |
| Full | Critical/security decisions | All fields |

### ADR Format

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

#### Traceability

- **Requirements**: REQ-XXX
- **Affects Tasks**: TASK-XXX (populated after /tasks)
```

---

## Workflow

1. **Locate specs** - Find spec files in .claude/resources/
2. **Assess complexity** - Single domain vs multi-domain
3. **PLANS coverage scan** - Evaluate all 5 categories
4. **Generate plans** - Create plan.md (and domain plans if complex)
5. **Create ADRs** - Document architecture decisions with rationale
6. **Validate ADRs** - Run ADR validator agent
7. **Validate checklist** - 7-point checklist before completion
8. **Report** - Coverage summary with recommendations

---

## ADR Validation (Agent)

After creating ADRs, invoke the ADR validator agent to ensure completeness.

**Invoke via Task tool:**
```
subagent_type: "speckit-generator:adr-validator"
prompt: "Validate ADRs in .claude/resources/plan.md at Standard level"
```

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
    └── domain-b-plan.md
```

## Plan Content

Plans contain:
- Requirements mapping (which spec sections covered)
- Architecture decisions (ADR format)
- Implementation approach (phases, NOT tasks)
- Verification strategy
- Notes for task generation

Plans do NOT contain:
- Individual tasks (that's /tasks)
- Implementation code
- Detailed how-to instructions

---

## 7-Point Validation Checklist

Before completing plan generation, verify ALL items:

| # | Check | Status |
|---|-------|--------|
| 1 | Requirements mapping complete | [ ] |
| 2 | Coverage status documented per PLANS category | [ ] |
| 3 | ADRs have all required fields for their level | [ ] |
| 4 | Phase sequencing valid (no circular deps) | [ ] |
| 5 | Traceability established (REQ → Phase → ADR) | [ ] |
| 6 | Task generation notes present for each phase | [ ] |
| 7 | Markdown structure valid | [ ] |

---

## Outputs

| Output | Location |
|--------|----------|
| Master plan | `.claude/resources/plan.md` |
| Domain plans (if complex) | `.claude/resources/plans/*.md` |

---

## Ralph Loop Mode (Autonomous Planning)

**Status**: ✓ Enabled (ralph-loop plugin detected)

Use `--ralph` flag for autonomous plan generation:

```
/plan --ralph                    # Until all ADRs have status: accepted
/plan --ralph --coverage 100     # Until 100% requirement coverage
```

### Exit Criteria

- All PLANS categories at ✓ Complete status
- All ADRs have status: accepted or rejected
- Coverage target reached (if specified)
- Hard limit: 20 iterations

---

## GATE: Required Before Proceeding

**STOP after plan generation. DO NOT proceed to `/tasks` automatically.**

After generating plans, you MUST:

1. **Present a plan summary** to the user showing:
   - PLANS coverage summary (5 categories)
   - Number of plans created (master + domain plans if complex)
   - ADR count and decisions made
   - Any assumptions or open questions identified

2. **Recommend next steps**:
   - Run `/analyze` to check plan compliance with constitution.md
   - Run `/clarify` if any `[TBD]` or `[NEEDS CLARIFICATION]` items exist
   - Review plans manually before approval

3. **Wait for explicit user approval** before proceeding to tasks

### Gate Response Template

```markdown
## Plan Generation Complete

### PLANS Coverage Summary

| Category | Status | Notes |
|----------|--------|-------|
| Phases | ✓ | N phases defined |
| Linkages | ✓ | Dependencies validated |
| Architecture | ✓ | N ADRs created |
| Notes | ✓ | Task guidance complete |
| Scope | ✓ | N/N requirements mapped |

### Architecture Decisions

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | [Decision summary] | accepted |

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
2. Run `/analyze` to validate compliance
3. Run `/clarify` to resolve open questions

**Awaiting your approval before generating tasks.**
```

---

## Handoffs

### Analyze Plan for Consistency
Run analysis to check plan compliance with constitution.md and find gaps.

Use: `/analyze`

### Clarify Ambiguities
If any `[TBD]` or `[NEEDS CLARIFICATION]` items exist in the plan.

Use: `/clarify`

### Generate Tasks
After plan is approved, generate implementation tasks.

Use: `/tasks`