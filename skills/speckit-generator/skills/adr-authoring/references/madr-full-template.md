# MADR Full Template

Complete Markdown Any Decision Record template with all optional fields and guidance.

## Template

```markdown
# ADR-XXX: [Short Title in Imperative Form]

## Metadata

| Field | Value |
|-------|-------|
| Status | proposed / accepted / rejected / deprecated / superseded by ADR-XXX |
| Date | YYYY-MM-DD |
| Decision-makers | [List people involved in decision] |
| Consulted | [List people whose opinions were sought] |
| Informed | [List people who should know about this decision] |

## Context and Problem Statement

[Describe the context and problem statement in 2-5 sentences.
What is the issue that motivates this decision?
What are the forces at play?]

### Background

[Optional: Additional context that helps understand the situation.
This can include history, related decisions, or external factors.]

## Decision Drivers

<!-- List the factors that influence this decision, in priority order -->

1. [Primary driver - the most important factor]
2. [Secondary driver]
3. [Tertiary driver]
4. [Additional drivers as needed]

### Constraints

<!-- Hard limits that cannot be violated -->

- [Constraint 1: e.g., "Must run on existing infrastructure"]
- [Constraint 2: e.g., "Budget maximum: $X"]
- [Constraint 3: e.g., "Must be completed by date Y"]

## Considered Options

<!-- List all options that were seriously considered -->

1. **[Option 1 Name]** - [One-line description]
2. **[Option 2 Name]** - [One-line description]
3. **[Option 3 Name]** - [One-line description]
4. **[Do Nothing / Status Quo]** - [If applicable]

## Decision Outcome

**Chosen option**: "[Option N Name]"

[Explain in 2-3 sentences why this option was selected.
Tie the rationale back to the decision drivers.]

### Implementation Approach

[Optional: High-level description of how this will be implemented.
Not detailed design, but enough to understand the approach.]

## Pros and Cons of the Options

### Option 1: [Name]

[Optional: 1-2 sentence description of this option]

| Aspect | Assessment |
|--------|------------|
| Pros | [List good outcomes] |
| Cons | [List bad outcomes] |
| Neutral | [List side effects] |

**Detailed Analysis:**

- Good, because [positive outcome 1]
- Good, because [positive outcome 2]
- Bad, because [negative outcome 1]
- Bad, because [negative outcome 2]
- Neutral, because [side effect]

### Option 2: [Name]

[Same structure as Option 1]

### Option 3: [Name]

[Same structure as Option 1]

## Consequences

### Positive Consequences

- [Good outcome 1]
- [Good outcome 2]

### Negative Consequences

- [Bad outcome or trade-off 1]
- [Bad outcome or trade-off 2]

### Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Medium/High | Low/Medium/High | [How to address] |
| [Risk 2] | Low/Medium/High | Low/Medium/High | [How to address] |

## Confirmation

<!-- How will we verify this decision was correct? -->

### Success Metrics

- [Metric 1: e.g., "Latency < 100ms p95"]
- [Metric 2: e.g., "Zero security incidents related to this choice"]

### Review Schedule

- [ ] 30-day check: [What to evaluate]
- [ ] 90-day review: [What to evaluate]
- [ ] 6-month retrospective: [What to evaluate]

## Traceability

### Related Requirements

- REQ-XXX: [Requirement title]
- REQ-YYY: [Requirement title]

### Related Tasks

- TASK-XXX: [Task title]
- TASK-YYY: [Task title]

### Related ADRs

- Supersedes: ADR-XXX (if replacing a previous decision)
- Related to: ADR-YYY (if connected but not superseding)
- Superseded by: ADR-ZZZ (added when this ADR is superseded)

## Additional Information

### Links

- [Link to relevant documentation]
- [Link to proof of concept]
- [Link to related discussion]

### Notes

[Any additional information that doesn't fit elsewhere]
```

## Field Descriptions

### Status Values

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `proposed` | Under consideration | Initial state for new ADRs |
| `accepted` | Decision made, will implement | After team agrees |
| `rejected` | Considered but not chosen | Document why not chosen |
| `deprecated` | No longer recommended | Circumstances changed |
| `superseded by ADR-XXX` | Replaced by newer decision | Link to replacement |

### RACI for Decision-makers

| Role | Description |
|------|-------------|
| Decision-makers | People with authority to approve |
| Consulted | Subject matter experts whose input was sought |
| Informed | Stakeholders who need to know the outcome |

### Consequence Types

| Type | Meaning | Example |
|------|---------|---------|
| Good | Positive outcome | "Reduces latency by 40%" |
| Bad | Negative outcome or trade-off | "Increases operational complexity" |
| Neutral | Side effect, neither good nor bad | "Requires data migration" |

## Minimal Required Fields

For a valid ADR, at minimum include:

1. **Title** - Clear, imperative form
2. **Status** - Current state
3. **Context** - Why this decision is needed
4. **Decision Outcome** - What was decided
5. **Consequences** - At least one good and one bad

Everything else is optional but recommended for important decisions.
