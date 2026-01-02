---
name: specification-refiner
description: >
  Systematic analysis and refinement of specifications, requirements, architecture designs, and project plans.
  Use when the user wants to identify gaps, weaknesses, inefficiencies, or complications in a proposed plan, specification, or design document.
  Triggers on gap analysis, specification review, requirements analysis, architecture critique, design validation, plan assessment, weakness identification, assumption auditing, or when users share specs/plans asking for feedback.
  Produces actionable findings with remediations and maintains analysis state across iterations.
---

# Specification Refiner

Systematically analyze and refine specifications, requirements, and architectural designs through iterative gap analysis with persistent memory.

## Core Workflow

```
1. INGEST    → Load and understand the specification/plan
2. ANALYZE   → Run SEAMS + Critical Path analysis
3. PRESENT   → Surface findings with context and remediations
4. ITERATE   → Accept new ideas, re-analyze affected areas
5. PERSIST   → Update memory files with current state
```

## Analysis Invocation

On receiving a specification, requirements doc, architecture design, or project plan:

### Phase 1: Ingestion

1. Parse the document structure (sections, dependencies, interfaces)
2. Create initial memory file: `analysis-state.md`
3. Identify document type and select appropriate analysis lenses

### Phase 2: Dual-Process Analysis

Run BOTH analysis frameworks in parallel:

#### Framework A: SEAMS Analysis

**S**tructure → **E**xecution → **A**ssumptions → **M**ismatches → **S**takeholders

| Lens | Questions to Answer |
|------|---------------------|
| **Structure** | Completeness of I/O paths? Cohesion of components? Coupling risks? Boundary clarity? |
| **Execution** | Happy path works? Edge cases covered? Failure modes handled? Recovery possible? |
| **Assumptions** | Technical assumptions? Organizational assumptions? Environmental assumptions? |
| **Mismatches** | Requirements ↔ Design aligned? Design ↔ Implementation consistent? Docs ↔ Reality synced? |
| **Stakeholders** | Operator perspective? Security perspective? Integrator perspective? End-user perspective? |

#### Framework B: Critical Path Analysis

1. **Dependency Mapping**: Build N² matrix of component dependencies
2. **Critical Path Identification**: Find longest/riskiest chains
3. **Single Points of Failure**: Components whose failure cascades
4. **Bottleneck Detection**: Throughput limiters, scaling blockers
5. **Temporal Analysis**: Sequencing issues, timing dependencies

### Phase 3: Findings Synthesis

For EACH identified issue, document:

```markdown
## [ISSUE-ID]: [Brief Title]

**Category**: [Gap | Weakness | Inefficiency | Complication | Risk]
**Severity**: [Critical | High | Medium | Low]
**Confidence**: [High | Medium | Low]

### Description
[What the issue is and why it matters]

### Evidence
[Specific references to the source material]

### Impact
[What happens if unaddressed]

### Remediation Options
1. [Option A with trade-offs]
2. [Option B with trade-offs]
3. [Option C with trade-offs]

### Related Issues
[Cross-references to connected findings]
```

### Phase 4: Presentation

Present findings grouped by:
1. **Critical blockers** (must fix before proceeding)
2. **Significant gaps** (high impact, clear remediation)
3. **Optimization opportunities** (efficiency improvements)
4. **Considerations** (context-dependent, need user input)

Always end with: "What aspects would you like to explore further, or do you have new constraints/ideas to incorporate?"

### Phase 5: Iteration Loop

When user provides new information or ideas:

1. **Validate new input** against existing analysis
2. **Identify affected areas** in the specification
3. **Re-run analysis** on affected sections only (delta analysis)
4. **Assess cascading effects** on previously-identified issues
5. **Update memory file** with new state
6. **Present delta findings** (what changed, what's resolved, what's new)

## Memory File Management

### Required Memory File: `analysis-state.md`

Create in the working directory. Structure:

```markdown
# Specification Analysis State

## Document Under Analysis
- **Title**: [document name]
- **Version**: [version/date analyzed]
- **Hash**: [content hash for change detection]

## Analysis Iterations
| Iteration | Date | Trigger | Key Changes |
|-----------|------|---------|-------------|
| 1 | [date] | Initial analysis | [summary] |
| 2 | [date] | User input: [topic] | [summary] |

## Active Findings
[List of current open issues with status]

## Resolved Findings
[Issues closed by iteration, with resolution notes]

## Assumption Register
| ID | Assumption | Status | Validation Method |
|----|------------|--------|-------------------|
| A1 | [assumption] | [Unverified/Confirmed/Invalidated] | [how to check] |

## User-Provided Constraints
[Constraints or decisions provided during iteration]

## Open Questions
[Questions awaiting user input]
```

### Memory Update Protocol

After EACH interaction:
1. Read current `analysis-state.md`
2. Append new iteration entry
3. Update finding statuses
4. Record any new assumptions
5. Log user-provided constraints
6. Write updated file

## Analysis Depth Calibration

Match depth to document maturity:

| Document Stage | Analysis Focus |
|----------------|----------------|
| **Concept/Idea** | Feasibility, scope clarity, key assumptions |
| **Draft Spec** | Completeness, internal consistency, missing sections |
| **Detailed Design** | Interface contracts, error handling, edge cases |
| **Implementation Plan** | Dependencies, sequencing, resource conflicts |
| **Review/Audit** | Full SEAMS sweep, stakeholder perspectives |

## Quick Assessment Mode

For rapid feedback, use compressed analysis:

1. **Boundaries**: What's in/out of scope? What crosses the line?
2. **One Thread**: Trace critical path from input to output
3. **Three Assumptions**: The riskiest unstated beliefs
4. **Silent Failure**: What breaks without anyone noticing?
5. **Naive Question**: What would a newcomer ask that has no answer?

## Output Formatting

### Severity Indicators
- 🔴 **Critical**: Blocks progress, must address
- 🟠 **High**: Significant risk, should address soon
- 🟡 **Medium**: Notable issue, plan to address
- 🟢 **Low**: Minor concern, address opportunistically

### Confidence Qualifiers
- **High confidence**: Clear evidence, well-understood domain
- **Medium confidence**: Reasonable inference, some ambiguity
- **Low confidence**: Pattern recognition, needs validation

## Handling Incomplete Information

When specifications are incomplete:
1. Note the gap explicitly
2. State what would be needed to complete analysis
3. Offer reasonable assumptions (clearly marked)
4. Ask user to confirm or provide missing details
5. Document in assumption register

## Anti-Patterns to Avoid

- ❌ Vague criticism without specific evidence
- ❌ Recommendations without trade-off analysis
- ❌ Analysis paralysis on minor issues
- ❌ Ignoring stated constraints to suggest "ideal" solutions
- ❌ Failing to update memory after iterations
- ❌ Treating all findings as equal severity
