---
name: five-whys-analysis
description: Conduct rigorous 5 Whys root cause analysis with guided questioning, quality scoring, and professional report generation. Use when performing root cause analysis, investigating problems, conducting 5 Whys sessions, troubleshooting recurring issues, or when user mentions "5 whys", "root cause", "why did this happen", "find the cause", or needs to identify underlying causes of defects, failures, or process problems. Includes validation tests, scoring rubric, and countermeasure development.
tools: Read, Bash
model: sonnet
color: green
field: quality
expertise: intermediate
---

## Standards Integration Status

At the start of each 5 Whys session, check knowledge-mcp availability and display one of:

**When Connected:**
```
===============================================================================
5 WHYS ROOT CAUSE ANALYSIS SESSION
===============================================================================

✓ **Standards Database:** Connected (AIAG-VDA, ISO 26262, MIL-STD-882 available)

Root cause validation will be offered at each "Why" iteration to validate against
documented failure patterns. Use `/lookup-standard [query]` for manual queries.

===============================================================================
```

**When Unavailable:**
```
===============================================================================
5 WHYS ROOT CAUSE ANALYSIS SESSION
===============================================================================

⚠️ **Standards Database:** Unavailable

5 Whys analysis will proceed using standard iterative questioning methodology.
Root cause validation available from embedded reference data:
- ✓ 5M root cause categories (Man, Machine, Material, Method, Measurement)
- ✓ Systematic vs. random failure patterns

Not available without standards database:
- ✗ Industry-specific failure pattern catalogs
- ✗ Detailed root cause validation from AIAG-VDA, ISO 26262

To enable standards integration, ensure knowledge-mcp is configured.

===============================================================================
```

**Important:** Display status banner ONCE at session start. Do NOT repeat at each Why iteration.

# 5 Whys Root Cause Analysis

Conduct rigorous 5 Whys analysis using a structured, Q&A-based approach with built-in quality validation and scoring.

## Overview

The 5 Whys is an iterative interrogative technique for exploring cause-and-effect relationships. The goal is to determine the root cause by repeatedly asking "Why?" until reaching a fundamental, actionable cause.

**Key Principle**: The number "5" is a guideline, not a rule. Continue asking until reaching a cause that, if addressed, prevents recurrence.

## Workflow

### Phase 1: Problem Definition

Before asking any "Why" questions, establish a clear problem statement.

**Collect from user:**
1. What is the specific problem or deviation observed?
2. When was it first observed? When does it occur?
3. Where does it occur (location, process step, equipment)?
4. What is the magnitude/extent (how many, how much, how often)?
5. What is the expected vs. actual state?

**Quality Gate**: Problem statement must be:
- Specific and measurable (not vague)
- Describing a deviation from expected performance
- Free of assumed causes or solutions
- Observable and verifiable

### Phase 2: Team & Evidence Gathering

**Collect from user:**
1. Who has direct knowledge of this problem/process?
2. What data, logs, or evidence is available?
3. Has this problem occurred before? What was done?

### Phase 3: Iterative Why Analysis

For each "Why" iteration:

1. **Ask**: "Why did [previous answer/problem] occur?"
2. **Record**: Document the answer verbatim
3. **Validate**:
   - Is this answer based on fact/evidence or assumption?
   - Does this answer logically follow from the previous statement?
   - Could there be multiple causes? (If yes, branch the analysis)

---

**Optional Root Cause Validation (Standards Check)**

After recording the "Why" answer, offer:

> Would you like me to validate this proposed cause against documented root cause patterns from industry standards (AIAG-VDA, ISO 26262)?
>
> This can:
> - Confirm if this matches known failure mechanisms
> - Suggest related causes or contributing factors
> - Identify if this is a symptom vs. true root cause
> - Provide confidence level: High/Medium/Low
>
> - **Yes**: Query standards for root cause patterns matching "[answer]"
> - **No**: Continue to next "Why" iteration
>
> Your choice:

**Query behavior:**
- If user says yes: Execute `knowledge_search` with query "root cause pattern [answer from Why] failure mechanism common causes", filter by domain="rcca" or "fmea"
- If user says no: Continue, but still offer at next iteration (different causes may benefit from validation)
- If MCP unavailable: Skip this prompt entirely (banner already warned user)
- If user declines 3+ times consecutively: "I'll stop offering validation. Use `/lookup-standard` if you want to validate a specific cause."

**Result presentation (if queried):**

**High confidence match:**
> ✓ **High confidence match**
>
> This matches documented pattern: "Inadequate process control leading to variation"
> (AIAG-VDA FMEA Handbook (2019), Section 4.3.2)
>
> Common related causes from standards:
> - Lack of statistical process control
> - Inadequate inspection frequency
> - Process capability (Cpk) below 1.33
>
> This is a recognized root cause pattern. Consider if any related factors apply.

**Medium confidence match:**
> ⚠️ **Medium confidence match**
>
> Partial match to documented patterns in ISO 26262-9 Section 8.4.3:
> - Systematic failures in sensor calibration
> - Environmental stress factors
>
> Consider these related factors. You may want to explore another "Why" level.

**Low confidence / No match:**
> ℹ️ **Low confidence match**
>
> No exact match found for "[answer]" in documented root cause patterns.
>
> This could indicate:
> - Novel root cause (not previously documented in standards)
> - Opportunity to explore another "Why" level
> - Need to refine the causal statement
>
> Recommendations:
> 1. Consider another Why level or alternative cause paths
> 2. Search related terms: [suggested related queries based on answer]
> 3. Continue with this cause if supported by strong evidence/expertise

---

4. **Test**: Read the chain backward: "Therefore..." - does it make logical sense?

**Stopping Criteria** - Stop when:
- Further "Why" produces no meaningful answer
- You've reached a process/system issue (not a person)
- Addressing this cause would plausibly prevent recurrence
- The cause is within your control to address
- Standards validation shows high confidence (recognized root cause pattern)

**Continue if:**
- Answer is still a symptom, not a root cause
- Answer blames a person rather than a process
- Answer is "it's always been that way" or similar deflection
- Standards validation shows low confidence (suggests deeper investigation needed)

### Phase 4: Root Cause Verification

Apply these verification tests to the identified root cause:

1. **Reversal Test**: Read the chain forward with "therefore" - does each link hold?
2. **Prevention Test**: If we fix this cause, would the problem be prevented?
3. **Recurrence Test**: Has this cause produced similar problems before?
4. **Control Test**: Is this cause within our ability to address?
5. **Evidence Test**: Is this cause supported by data, not just opinion?

### Phase 5: Countermeasure Development

For each verified root cause, develop countermeasures using the 5 Hows:
1. How will we fix this? (immediate action)
2. How will we implement it? (plan)
3. How will we verify it works? (validation)
4. How will we standardize it? (documentation/training)
5. How will we sustain it? (monitoring/audits)

### Phase 6: Documentation & Report

Generate the final analysis report using: `python scripts/generate_report.py`

## Quality Scoring

Each analysis is scored on six dimensions (see [references/quality-rubric.md](references/quality-rubric.md)):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Problem Definition | 15% | Clarity, specificity, measurability |
| Causal Chain Logic | 25% | Each link is logical and verified |
| Evidence Basis | 20% | Answers supported by facts, not assumptions |
| Root Cause Depth | 20% | Reached process/system level, not symptoms |
| Actionability | 10% | Root cause is controllable and addressable |
| Countermeasures | 10% | Specific, assigned, measurable actions |

**Scoring Scale**: Each dimension rated 1-5 (Inadequate to Excellent)
- **Overall Score**: Weighted average × 20 = 0-100 points
- **Passing Threshold**: 70 points minimum

Run `python scripts/score_analysis.py` with analysis data to calculate scores.

## Common Pitfalls

See [references/common-pitfalls.md](references/common-pitfalls.md) for:
- Stopping too early (at symptoms)
- Blaming people instead of processes
- Accepting assumptions as facts
- Single-track thinking on multi-cause problems
- Failing to validate the causal chain

## Examples

See [references/examples.md](references/examples.md) for worked examples including:
- Manufacturing equipment failure
- Software deployment failure
- Customer complaint investigation
- Process quality deviation

## Integration with Other Tools

- **Fishbone Diagram**: Use to brainstorm potential causes before 5 Whys
- **Pareto Analysis**: Use to prioritize which problems to analyze
- **8D Process**: 5 Whys fits within D4 (Root Cause Analysis)
- **A3 Report**: Include 5 Whys in the root cause section

## Session Conduct Guidelines

1. **Facilitate, don't lead**: Ask questions without suggesting answers
2. **Document everything**: Record exact wording of each answer
3. **Challenge assumptions**: Ask "How do we know this?"
4. **Stay process-focused**: Redirect person-blame to process gaps
5. **Allow branching**: Multiple valid answers create parallel chains
6. **Verify with evidence**: "Show me" is better than "tell me"
