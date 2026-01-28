---
name: problem-definition
description: Guide RCCA/8D problem definition using 5W2H and IS/IS NOT analysis. Transforms scattered failure data into precise, measurable problem statements that bound investigation scope without embedding cause or solution. Use when defining problems for root cause analysis, writing D2 sections of 8D reports, analyzing nonconformances, investigating failures, or when user mentions problem definition, problem statement, RCCA, 8D, failure analysis, or corrective action.
---

# Problem Definition for RCCA

Problem Definition (D2 in 8D methodology) transforms scattered observations about a failure, defect, or nonconformance into a precise, bounded statement that enables effective root cause analysis.

## Core Principle

**Describe what went wrong without inferring cause or prescribing solution.**

The problem definition answers: *"What is the deviation between expected and actual?"* — not *"why did it happen"* or *"how do we fix it."*

## Workflow

1. **Assess available information** — Review what the user has provided. Identify which 5W2H elements are known vs. missing.

2. **Elicit missing data** — For each gap, invoke `AskUserQuestion` using the structured format below. Ask 2-3 questions maximum per turn to avoid overwhelming the user.

3. **Apply 5W2H framework** — Systematically populate: What, Where, When, Who, How, How Much. Deliberately **exclude Why** (that's for root cause analysis). See [references/5w2h-framework.md](references/5w2h-framework.md).

4. **Sharpen boundaries with IS/IS NOT** — For each 5W2H dimension, explicitly state what the problem IS and IS NOT. The contrast reveals investigation clues. See [references/is-is-not-analysis.md](references/is-is-not-analysis.md).

5. **Quantify the gap** — Express deviation numerically: "Measured 15 in-lbs; specification requires 22 ± 2 in-lbs" not "torque was low."

6. **Synthesize problem statement** — Combine findings into a single statement using the template:

```
[Object] exhibited [defect/failure mode] at [location] during [phase/operation], 
affecting [extent/quantity], detected by [method].
```

7. **Validate against pitfalls** — Review statement for embedded cause, embedded solution, vagueness, or blame language. See [references/pitfalls.md](references/pitfalls.md).

---

## Elicitation: Using AskUserQuestion

When information is missing, invoke `AskUserQuestion` to gather data systematically. Do not guess or assume — elicit from the user.

### Question Format

Present questions using this structure:

```
**[5W2H Category]: [Element]**
[Question text — specific, closed-ended where possible]

_Context: [Brief explanation of why this matters for problem definition]_

Examples of useful answers:
- [Concrete example 1]
- [Concrete example 2]
```

### Question Sequencing

**Priority order for elicitation:**

1. **What (Object)** — Must identify the specific item first
2. **What (Defect)** — Must characterize the failure mode
3. **How Much (Extent)** — Critical for scoping and prioritization
4. **Where / When** — Bounds the investigation
5. **How (Detection)** — Validates data source reliability
6. **Who** — Typically least critical, often implicit

### Example Questions

**What (Object):**
> What is the specific part number, product, or system exhibiting the problem?
>
> _Context: Precise identification prevents confusion with similar items._
>
> Examples of useful answers:
> - "Connector housing P/N 12345-A, Rev C"
> - "Model X Controller Board, serial range SN2024-001 through SN2024-500"

**What (Defect):**
> What specifically is wrong? Describe the observable defect, failure mode, or deviation from specification.
>
> _Context: Technical, measurable descriptions enable root cause analysis. Avoid subjective terms like "bad" or "poor quality."_
>
> Examples of useful answers:
> - "Cracked at locking tab; crack length approximately 3mm"
> - "Output voltage 4.2V; specification requires 5.0V ± 0.1V"

**How Much (Extent):**
> How many units are affected? What is the failure rate or reject percentage?
>
> _Context: Quantification enables prioritization and verifies corrective action effectiveness._
>
> Examples of useful answers:
> - "12 of 400 units inspected (3%)"
> - "3 field failures from population of ~2,000 deployed units"

**IS/IS NOT Clarification:**
> You mentioned the problem occurs at Station 3. Does this problem occur at Stations 1 or 2? Are other similar parts from those stations unaffected?
>
> _Context: Understanding what IS NOT affected helps narrow root cause investigation._

### Elicitation Rules

- **Ask, don't assume:** If data is missing, ask. Do not infer or fabricate details.
- **Batch questions:** Group 2-3 related questions per turn. Do not ask all questions at once.
- **Accept uncertainty:** If user doesn't know, record as "Unknown — requires investigation" rather than leaving blank.
- **Probe vague answers:** If user says "several units," ask for specific count. If user says "recently," ask for date.
- **Avoid leading questions:** Do not embed assumed cause in questions (e.g., avoid "Was the torque too high?").

For complete question templates across all 5W2H categories, see [references/question-bank.md](references/question-bank.md).

## Quick Reference: 5W2H Questions

| Element | Question | Example |
|---------|----------|---------|
| **What** (Object) | What item has the problem? | Connector housing |
| **What** (Defect) | What is wrong with it? | Cracked at locking tab |
| **Where** (Geographic) | Where was it observed? | Final assembly station 3 |
| **Where** (On object) | Where on the item? | Locking tab area |
| **When** (Calendar) | When first observed? | Week 12 production |
| **When** (Lifecycle) | When in process sequence? | During torque verification |
| **Who** | Who detected/reported it? | QC inspector |
| **How** | How was it detected? | Visual inspection |
| **How Much** | What is the extent? | 12 of 400 units (3%) |

## Output Format

For structured output, generate both:

1. **5W2H + IS/IS NOT table** — Systematic data capture
2. **Problem statement** — Single synthesized statement

See [references/examples.md](references/examples.md) for worked examples.

## Validation Checklist

Before finalizing, verify:

- [ ] No assumed cause embedded ("due to...", "caused by...")
- [ ] No solution embedded ("need to change...", "should replace...")
- [ ] Defect described with measurable terms
- [ ] Extent quantified (count, percentage, rate)
- [ ] Detection method stated
- [ ] Scope bounded (what IS affected, what IS NOT)
