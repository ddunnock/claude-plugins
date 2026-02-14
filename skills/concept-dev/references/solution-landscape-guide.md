# Solution Landscape Guide

How to present solution approaches without prescribing specific technologies.

## Core Principle

**Map the landscape of options. Do not pick the destination.**

The Solution Landscape document exists to inform future implementation decisions, not to make them. The concept development process defines WHAT needs to exist; implementation planning decides HOW to build it.

## Presentation Pattern

### For Each Sub-Function

```
For [function description], approaches include:

**[Approach A]** — [What it is and how it addresses the function]
  Maturity: [Mature / Emerging / Experimental]
  Strengths: [cited advantages]
  Limitations: [cited disadvantages]
  Sources: [SRC-xxx, SRC-yyy]

**[Approach B]** — [What it is and how it addresses the function]
  [Same structure]

**Defer** — Address this function in a later development phase.
  Trade-off: [what you lose by deferring]
```

### Language Rules

**Do say:**
- "Approaches include A, B, and C"
- "A is characterized by [feature], while B prioritizes [different feature]"
- "According to [source], A has been successfully deployed in [context]"
- "No approach fully addresses [gap] based on current research"

**Don't say:**
- "The best approach is A"
- "We recommend B"
- "A is clearly superior to B"
- "The obvious choice is C"
- "B should be used because..."

### Handling Trade-offs

Present trade-offs as dimensions, not rankings:

```
| Dimension    | Approach A | Approach B | Approach C |
|-------------|-----------|-----------|-----------|
| Maturity    | High      | Medium    | Low       |
| Flexibility | Low       | Medium    | High      |
| Complexity  | Low       | Medium    | High      |
| [Domain-specific] | [Value] | [Value] | [Value] |
```

Let the reader draw their own conclusions based on their priorities.

## Maturity Assessment

### Definitions

| Level | Definition | Evidence Required |
|-------|-----------|-------------------|
| **Mature** | Deployed in production environments, well-understood trade-offs, established best practices | Multiple sources documenting production use; known limitations documented |
| **Emerging** | Active development, limited production deployments, growing community/vendor support | Recent publications or releases; some production case studies; evolving best practices |
| **Experimental** | Research stage, proof-of-concept only, limited real-world validation | Academic papers; prototype demonstrations; no production deployment evidence |

### Honest Maturity Assessment

- If you can't find evidence of production deployment, it's not Mature
- If the most recent source is from a research lab, it's Experimental
- If in doubt, assess lower rather than higher
- Always cite the basis for your maturity assessment

## Gap Reporting

### What Makes a Good Gap Statement

**Good:** "GAP-007: No open standard exists for real-time cross-domain data fusion at the rate required by the Safety Monitoring function. Existing standards (DIS, HLA) operate at lower refresh rates. This gap affects blocks B and D."

**Bad:** "GAP-007: Need to figure out data fusion."

### Gap Prioritization

| Priority | Criteria |
|----------|---------|
| **High** | Blocks a critical capability; no known workaround; affects multiple blocks |
| **Medium** | Affects one block significantly; workarounds exist but are suboptimal |
| **Low** | Nice to resolve; doesn't block core concept; can be deferred |

## Confidence and Honesty

### When Research Is Insufficient

Be transparent:
```
NOTE: Research for this sub-function was limited by [reason —
no academic literature found, domain is emerging, proprietary
technology without public documentation]. The approaches listed
are based on [what was available]. Additional research recommended
before implementation planning.
```

### When Approaches Are Speculative

Flag speculation clearly:
```
SPECULATIVE: [Approach name] has not been validated for this
specific use case. Its inclusion is based on [analogy to similar
domain / theoretical applicability / vendor claims]. Confidence: LOW.
```

### When the "Do Nothing" Option Is Valid

Always include:
```
DEFER: This sub-function could be addressed in a later phase.
Impact of deferral: [What the concept loses without this function].
Risk: [What could go wrong if deferred too long].
```
