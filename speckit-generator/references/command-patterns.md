# Command Patterns Reference

## Table of Contents

1. [Command Structure](#command-structure)
2. [Generator Pattern](#generator-pattern)
3. [Analyzer Pattern](#analyzer-pattern)
4. [Orchestrator Pattern](#orchestrator-pattern)
5. [Decision Pattern](#decision-pattern)
6. [Handoff Design](#handoff-design)

---

## Command Structure

All commands follow this base structure:

```markdown
---
description: "[One-line description of what this command produces]"
agent:
  model: sonnet
---

# [Command Name]

## Purpose

[Clear statement of the deliverable this command produces]

## Prerequisites

- [ ] [Required input 1]
- [ ] [Required input 2]

## Workflow

### Phase 1: [Phase Name]

[Numbered steps with clear actions]

1. [Action 1]
2. [Action 2]

### Phase 2: [Phase Name]

[Continue with next phase]

## Outputs

- [Output 1]: [Description and location]
- [Output 2]: [Description and location]

## Completion Criteria

- [ ] [Verifiable criterion 1]
- [ ] [Verifiable criterion 2]

## Handoffs

### Proceed to [Next Command]

**Context**: [What was accomplished]
**Inputs Ready**: [What the next command receives]

Use: `/[next-command]`
```

---

## Generator Pattern

**Use When**: Creating structured documents from inputs

### Template

```markdown
---
description: "Generate [DELIVERABLE_TYPE] from [INPUT_TYPE]"
agent:
  model: sonnet
---

# Generate [Deliverable Name]

## Purpose

Create a complete [DELIVERABLE_TYPE] that [PURPOSE] by processing [INPUTS] and applying [STANDARDS/TEMPLATES].

## Prerequisites

- [ ] [Input file/data] available at [location]
- [ ] [Template] accessible
- [ ] [Prior command] completed (if dependent)

## Workflow

### Phase 1: Input Validation

1. Verify all required inputs exist
2. Check input format compliance
3. Log any issues to console

```bash
# Validate inputs
python scripts/validate-inputs.py <input-path> --json
```

### Phase 2: Content Generation

1. Load template from `.claude/templates/[template-name].md`
2. Process inputs according to template structure
3. Fill template sections systematically

**Template Sections:**
- [Section 1]: [How to populate]
- [Section 2]: [How to populate]

### Phase 3: Quality Validation

1. Run output validation

```bash
python scripts/validate-output.py <output-path> --json
```

2. Verify completeness criteria
3. Document any TBD items

### Phase 4: Output Finalization

1. Save generated document to `[OUTPUT_PATH]`
2. Update status in `.claude/memory/[status-file].md`
3. Log completion

## Outputs

- **Primary**: `[OUTPUT_PATH]/[deliverable].md`
- **Status Update**: `.claude/memory/[status-file].md`

## Completion Criteria

- [ ] All template sections populated
- [ ] Validation script passes
- [ ] TBD items documented
- [ ] Status file updated

## Handoffs

### Proceed to Review

**Context**: [DELIVERABLE] generated and validated
**Ready for**: Stakeholder review

Use: `/review.prepare`
```

### Example: Requirements Generator

```markdown
---
description: "Generate Software Requirements Specification from stakeholder needs"
agent:
  model: sonnet
---

# Generate Requirements Specification

## Purpose

Create a complete SRS document by eliciting, organizing, and formalizing requirements from stakeholder needs and system context.

## Prerequisites

- [ ] Stakeholder needs documented or available for elicitation
- [ ] System boundary defined
- [ ] Template: `.claude/templates/requirements/srs-template.md`

## Workflow

### Phase 1: Stakeholder Analysis

1. Identify all stakeholders
2. Document stakeholder concerns
3. Prioritize stakeholder needs

### Phase 2: Requirements Elicitation

For each stakeholder need:

1. Decompose into atomic requirements
2. Apply EARS syntax: [Precondition] [Trigger] The [System] shall [Response]
3. Assign unique ID: `FR-XXX` or `NFR-XXX`
4. Set priority (MoSCoW)
5. Identify verification method (I/A/D/T)

### Phase 3: Requirements Documentation

1. Load SRS template
2. Populate functional requirements table
3. Populate non-functional requirements table
4. Create traceability to stakeholder needs

### Phase 4: Validation

```bash
python scripts/requirements/validate-srs.py docs/srs.md --json
```

Check for:
- Unique IDs
- Complete traceability
- Testable statements
- No orphan requirements

## Outputs

- **Primary**: `docs/srs.md`
- **Traceability**: `docs/traceability-matrix.md`
- **Status**: `.claude/memory/requirements-status.md`

## Completion Criteria

- [ ] All stakeholder needs traced to requirements
- [ ] All requirements have unique IDs
- [ ] All requirements have verification methods
- [ ] Validation script passes

## Handoffs

### Proceed to Requirements Baseline

**Context**: SRS document generated and validated
**Ready for**: Formal baselining

Use: `/requirements.baseline`
```

---

## Analyzer Pattern

**Use When**: Examining existing artifacts for insights

### Template

```markdown
---
description: "Analyze [TARGET] to identify [INSIGHTS]"
agent:
  model: sonnet
---

# Analyze [Target Name]

## Purpose

Examine [TARGET] to identify [INSIGHTS], producing [REPORT_TYPE] that enables [DECISIONS/ACTIONS].

## Prerequisites

- [ ] [Target artifact(s)] available
- [ ] Analysis criteria defined
- [ ] Output location prepared

## Workflow

### Phase 1: Scope Definition

1. Confirm analysis scope
2. Identify specific questions to answer
3. Define success criteria for analysis

**Analysis Questions:**
- [Question 1]
- [Question 2]

### Phase 2: Data Collection

1. Gather target artifacts
2. Extract relevant information

```bash
# Extract data for analysis
python scripts/extract-data.py <target-path> --json
```

### Phase 3: Analysis Execution

For each analysis question:

1. Apply analysis method
2. Document findings
3. Identify patterns/anomalies
4. Quantify where possible

**Analysis Methods:**
- [Method 1]: [Application]
- [Method 2]: [Application]

### Phase 4: Report Generation

1. Organize findings by category
2. Highlight key insights
3. Provide recommendations
4. Document assumptions and limitations

## Outputs

- **Analysis Report**: `[OUTPUT_PATH]/[analysis-report].md`
- **Data Extract**: `[OUTPUT_PATH]/[data].json` (if applicable)

## Completion Criteria

- [ ] All analysis questions addressed
- [ ] Findings supported by evidence
- [ ] Recommendations actionable
- [ ] Assumptions documented

## Handoffs

### Proceed to [Action Command]

**Context**: Analysis complete with findings
**Key Insights**: [Summary]

Use: `/[action-command]`
```

---

## Orchestrator Pattern

**Use When**: Multi-phase execution with decision points

### Template

```markdown
---
description: "Orchestrate [PROCESS] through [PHASES] to produce [OUTCOME]"
agent:
  model: sonnet
---

# Orchestrate [Process Name]

## Purpose

Guide the complete [PROCESS] from [START_STATE] to [END_STATE], coordinating [N] phases and ensuring quality gates are met.

## Prerequisites

- [ ] [Initial inputs] available
- [ ] [Stakeholders] identified
- [ ] [Resources] accessible

## Process Overview

```
Phase 1: [Name] ──▶ Phase 2: [Name] ──▶ Phase 3: [Name]
     │                   │                   │
     ▼                   ▼                   ▼
 [Deliverable]      [Deliverable]      [Deliverable]
```

## Workflow

### Phase 1: [Phase Name]

**Objective**: [What this phase achieves]

**Sub-Commands**:
1. `/[sub-command-1]` - [Purpose]
2. `/[sub-command-2]` - [Purpose]

**Gate Criteria**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Decision Point**: [What decision is made]
- If [condition]: Proceed to Phase 2
- If [condition]: Iterate on Phase 1

### Phase 2: [Phase Name]

**Objective**: [What this phase achieves]

**Sub-Commands**:
1. `/[sub-command-1]` - [Purpose]

**Gate Criteria**:
- [ ] [Criterion 1]

### Phase 3: [Phase Name]

**Objective**: [What this phase achieves]

**Final Deliverables**:
- [Deliverable 1]
- [Deliverable 2]

## State Tracking

Update `.claude/memory/[process]-status.md` at each phase:

```markdown
## [Process] Status

| Phase | Status | Started | Completed | Notes |
|-------|--------|---------|-----------|-------|
| 1 | [STATUS] | [DATE] | [DATE] | [NOTES] |
| 2 | [STATUS] | [DATE] | [DATE] | [NOTES] |
| 3 | [STATUS] | [DATE] | [DATE] | [NOTES] |
```

## Completion Criteria

- [ ] All phases completed
- [ ] All gate criteria satisfied
- [ ] Final deliverables produced
- [ ] Status file updated to COMPLETE

## Handoffs

### Process Complete

**Final State**: [PROCESS] successfully completed
**Deliverables Ready**: [List of outputs]
**Next Steps**: [Recommended actions]
```

---

## Decision Pattern

**Use When**: Guiding stakeholder choices with structured evaluation

### Template

```markdown
---
description: "Evaluate [ALTERNATIVES] against [CRITERIA] to recommend [DECISION]"
agent:
  model: sonnet
---

# Evaluate [Decision Topic]

## Purpose

Systematically evaluate [ALTERNATIVES] against weighted [CRITERIA] to provide a defensible recommendation for [DECISION].

## Prerequisites

- [ ] Decision need established
- [ ] Stakeholders identified
- [ ] Constraints documented

## Workflow

### Phase 1: Problem Framing

1. Confirm decision statement
2. Document constraints (non-negotiables)
3. Identify assumptions

**Decision Statement**: [What are we deciding?]

**Constraints**:
- [Constraint 1]: [Description]
- [Constraint 2]: [Description]

**Assumptions**:
- [ASSUMPTION: rationale] [Description]

### Phase 2: Alternatives Identification

1. Brainstorm alternatives
2. Screen against constraints
3. Document surviving alternatives

| ID | Alternative | Description | Meets Constraints |
|----|-------------|-------------|-------------------|
| A1 | [NAME] | [DESCRIPTION] | Yes/No |

### Phase 3: Criteria Definition

1. Identify evaluation criteria
2. Assign weights (sum to 1.0)
3. Define scoring scale (1-5)

| ID | Criterion | Weight | Scale Definition |
|----|-----------|--------|------------------|
| C1 | [NAME] | [0.XX] | 1=[LOW]...5=[HIGH] |

### Phase 4: Evaluation

For each alternative, score against each criterion:

```bash
# Calculate weighted scores
python scripts/trades/calculate-scores.py <data-file> --json
```

| Alternative | C1 | C2 | C3 | Weighted Score |
|-------------|----|----|----|----|
| A1 | [1-5] | [1-5] | [1-5] | [TOTAL] |

### Phase 5: Sensitivity Analysis

Test robustness of recommendation:

1. Vary weights ±20%
2. Identify score margins
3. Document stability

### Phase 6: Recommendation

1. Present recommended alternative
2. Document rationale
3. Capture dissenting views
4. Identify accepted risks

## Outputs

- **Decision Record**: `docs/decisions/[decision-id].md`
- **Scoring Data**: `data/[decision-id]-scores.json`
- **Log Entry**: `.claude/memory/decisions-log.md`

## Completion Criteria

- [ ] All alternatives evaluated
- [ ] Sensitivity analysis performed
- [ ] Recommendation documented
- [ ] Stakeholder sign-off obtained

## Handoffs

### Decision Made

**Selected**: [ALTERNATIVE_ID]
**Rationale**: [Summary]
**Next Steps**: [Implementation actions]

Use: `/[implementation-command]`
```

---

## Handoff Design

Handoffs ensure smooth transitions between commands.

### Handoff Structure

```yaml
handoffs:
  - label: "Proceed to [Next Phase]"
    agent: "[target-command]"
    prompt: |
      ## Context
      [What was accomplished in the previous command]
      
      ## Inputs Available
      - [Input 1]: [Location/description]
      - [Input 2]: [Location/description]
      
      ## Objective
      [What the next command should accomplish]
      
      ## Constraints
      - [Any constraints carried forward]
```

### Best Practices

1. **Provide Complete Context**: Don't assume next command knows history
2. **List All Inputs**: Specify locations of all artifacts
3. **State Clear Objective**: What specifically should happen next
4. **Carry Forward Constraints**: Don't lose important limitations
5. **Update State First**: Ensure memory files are current before handoff

### Example Handoff Chain

```
/requirements.capture
    │
    ├── Context: Stakeholder needs elicited
    ├── Inputs: stakeholder-needs.md
    ├── Objective: Create formal requirements
    │
    ▼
/requirements.trace
    │
    ├── Context: SRS complete
    ├── Inputs: srs.md, stakeholder-needs.md
    ├── Objective: Build traceability matrix
    │
    ▼
/requirements.baseline
    │
    ├── Context: Requirements traced
    ├── Inputs: srs.md, traceability-matrix.md
    ├── Objective: Establish formal baseline
    │
    ▼
/architecture.design
```
