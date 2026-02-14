# Black-Box Architecture — [Project Name]

**Session:** [session_id]
**Date:** [date]
**Phase:** Black-Box Architecture (Phase 3)
**Selected Approach:** [Approach Name]

---

## Concept Overview

[2-3 paragraph description of the selected architectural approach. What is the core insight? What distinguishes this approach?]

---

## Functional Block Diagram

```
[ASCII diagram showing all functional blocks and their relationships]
```

---

## Functional Blocks

### [Block Name]

**Responsibility:** [What this block does — functional description]

**Inputs:**
- [What it receives and from where]

**Outputs:**
- [What it produces and for whom]

**Key Behaviors:**
- [Behavior 1]
- [Behavior 2]

---

### [Block Name]

**Responsibility:** [What this block does]

**Inputs:**
- [Input description]

**Outputs:**
- [Output description]

**Key Behaviors:**
- [Behavior]

---

## Block Relationships

| From | To | Relationship | What Flows |
|------|----|-------------|------------|
| [Block A] | [Block B] | [provides/consumes/triggers] | [Data/control description] |
| [Block B] | [Block C] | [relationship] | [What flows] |

---

## Architectural Principles

1. **[Principle Name]** — [Description of the principle and why it matters]
2. **[Principle Name]** — [Description]
3. **[Principle Name]** — [Description]

---

## Enabled Capabilities

### Direct Capabilities
Capabilities that individual blocks provide:

1. **[Capability]** — [Description, referencing which block(s)]
2. **[Capability]** — [Description]

### Emergent Capabilities
Capabilities that arise from the integration of blocks — things not possible in isolation:

1. **[Capability]** — [Description of how block integration enables this]
2. **[Capability]** — [Description]

---

## Concept of Operations

### Scenario: [Scenario Name]

[Narrative walkthrough of how the concept operates in a representative scenario. Describe what happens step by step, referencing functional blocks.]

1. [Step — Block A does X]
2. [Step — Block B responds with Y]
3. [Step — Block C enables Z]
4. [Outcome]

### Scenario: [Scenario Name]

[Second scenario walkthrough]

---

## Alternative Approaches Considered

| Approach | Core Idea | Why Not Selected |
|----------|-----------|-----------------|
| [Approach 2] | [Brief description] | [Reason] |
| [Approach 3] | [Brief description] | [Reason] |

---

## Assumptions

| ID | Assumption | Category | Impact if Wrong |
|----|-----------|----------|-----------------|
| [A-xxx] | [Assumption text] | [architecture/scope/constraint] | [Impact] |

---

## Open Questions

Questions identified during architecture definition that need Phase 4 research:

1. [Question — which block it relates to]
2. [Question]

---

**Next Phase:** Drill-Down & Gap Analysis (`/concept:drilldown`)
