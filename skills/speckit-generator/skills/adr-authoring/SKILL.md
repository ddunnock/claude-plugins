---
name: adr-authoring
description: |
  This skill should be used when writing Architecture Decision Records (ADRs),
  documenting technical decisions, or reviewing architecture choices. Triggers on
  phrases like "document this decision", "create ADR", "architecture decision",
  "why did we choose", "record the decision", "MADR template", or when the user
  is working on plan files that contain ADR sections.
---

# Architecture Decision Record Authoring

Write clear, useful ADRs that capture the context, options, and rationale behind technical decisions. Good ADRs prevent re-litigation of decisions and help new team members understand the codebase.

## Quick Reference

### MADR Template Levels

| Level | When to Use | Required Fields |
|-------|-------------|-----------------|
| **Lightweight** | Quick decisions, low impact | Status, Context, Decision, Consequences |
| **Standard** | Most architectural decisions | + Date, Decision-makers, Drivers, Options |
| **Full** | Critical/reversible decisions | + Confirmation, Traceability |

### ADR Lifecycle

```
proposed → accepted → [deprecated → superseded]
                   ↘ rejected
```

## Lightweight ADR Template

For quick decisions with limited impact:

```markdown
### ADR-XXX: [Short Title]

**Status**: proposed | accepted | rejected | deprecated | superseded

**Context and Problem Statement**
[2-3 sentences describing the situation and what needs to be decided]

**Decision Outcome**
Chosen option: "[Option name]"

[1-2 sentences explaining why]

**Consequences**
- Good: [positive outcomes]
- Bad: [negative outcomes or trade-offs]
```

## Standard ADR Template

For most architectural decisions:

```markdown
### ADR-XXX: [Short Title]

**Status**: proposed | accepted | rejected | deprecated | superseded
**Date**: YYYY-MM-DD
**Decision-makers**: [names or roles]

**Context and Problem Statement**
[2-3 sentences describing the situation requiring a decision.
What is the issue? Why does it need to be addressed now?]

**Decision Drivers**
- [Driver 1: e.g., "Need to support 10x current load"]
- [Driver 2: e.g., "Team has no experience with technology X"]
- [Driver 3: e.g., "Budget constraint of $X/month"]

**Considered Options**
1. [Option 1 name]
2. [Option 2 name]
3. [Option 3 name]

**Decision Outcome**
Chosen option: "[Option N]" because [1-2 sentence rationale linking to drivers].

**Consequences**
- Good: [positive outcome 1]
- Good: [positive outcome 2]
- Bad: [trade-off or negative outcome]
- Neutral: [side effect that's neither good nor bad]
```

## Full ADR Template

For critical decisions requiring traceability:

```markdown
### ADR-XXX: [Short Title]

**Status**: proposed | accepted | rejected | deprecated | superseded
**Date**: YYYY-MM-DD
**Decision-makers**: [names or roles]

**Context and Problem Statement**
[Detailed context with background information.
Include relevant constraints and dependencies.]

**Decision Drivers**
- [Driver 1 with quantifiable metric if possible]
- [Driver 2]
- [Driver 3]

**Considered Options**
1. **[Option 1 name]**: [Brief description]
2. **[Option 2 name]**: [Brief description]
3. **[Option 3 name]**: [Brief description]

**Pros and Cons of Options**

#### Option 1: [Name]
- Good: [Pro 1]
- Good: [Pro 2]
- Bad: [Con 1]

#### Option 2: [Name]
- Good: [Pro 1]
- Bad: [Con 1]
- Bad: [Con 2]

#### Option 3: [Name]
- Good: [Pro 1]
- Neutral: [Neither good nor bad]
- Bad: [Con 1]

**Decision Outcome**
Chosen option: "[Option N]" because [rationale].

**Consequences**
- Good: [outcome 1]
- Bad: [outcome 2]

**Confirmation**
[How will we verify this decision was correct?]
- [Metric or checkpoint 1]
- [Metric or checkpoint 2]

**Traceability**
- Requirements: REQ-XXX, REQ-YYY
- Tasks: TASK-XXX, TASK-YYY
- Supersedes: ADR-ZZZ (if applicable)
```

## Writing Effective ADRs

### Context Section

**Do:**
- State the problem clearly in 2-3 sentences
- Include relevant constraints (time, budget, team skills)
- Mention what triggered this decision

**Don't:**
- Write a novel (save details for options analysis)
- Assume reader knows the background
- Include the solution in the context

### Decision Drivers

Quantify when possible:

| Vague | Specific |
|-------|----------|
| "Need better performance" | "Must handle 1000 req/sec" |
| "Team preference" | "3 of 4 developers have React experience" |
| "Cost concerns" | "Budget limit: $500/month" |

### Considered Options

Include at least 2 options. Always include:
- The chosen option
- The obvious alternative
- "Do nothing" if applicable

### Consequences

Be honest about trade-offs:

```markdown
**Consequences**
- Good: Reduces API latency by 40%
- Good: Team already knows this technology
- Bad: Adds operational complexity (new service to maintain)
- Bad: Vendor lock-in to AWS
- Neutral: Requires migration of existing data (one-time effort)
```

## ADR Numbering

Use sequential numbering within the project:

```markdown
ADR-001: Database Selection
ADR-002: Authentication Strategy
ADR-003: API Versioning Approach
```

For domain-specific ADRs in larger projects:

```markdown
ADR-AUTH-001: OAuth Provider Selection
ADR-DATA-001: Cache Strategy
ADR-INFRA-001: Container Orchestration
```

## When to Write an ADR

| Situation | ADR Level |
|-----------|-----------|
| Choosing a database | Standard or Full |
| Selecting a framework | Standard |
| API design patterns | Standard |
| Deployment strategy | Standard or Full |
| Library selection | Lightweight |
| Code organization | Lightweight |
| Naming conventions | Lightweight (or skip) |

## Integration with SpecKit

ADRs created during `/speckit.plan` should:

1. **Use consistent numbering** - ADR-001, ADR-002, etc.
2. **Reference requirements** - Link to REQ-XXX from spec
3. **Be validated** - `/speckit.analyze` checks ADR completeness
4. **Trace to tasks** - Tasks reference implementing ADRs

## Additional Resources

For detailed patterns and examples, see:

- **`references/madr-full-template.md`** - Complete MADR template with all fields
- **`references/adr-examples.md`** - Real-world ADR examples

## Checklist Before Finalizing

- [ ] Status is set (proposed for new ADRs)
- [ ] Context explains WHY a decision is needed
- [ ] At least 2 options were considered
- [ ] Decision clearly states the chosen option
- [ ] Consequences include both good AND bad
- [ ] Date and decision-makers are recorded (Standard+)
