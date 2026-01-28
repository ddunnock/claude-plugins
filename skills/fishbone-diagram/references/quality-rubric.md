# Fishbone Diagram Quality Rubric

## Overview

This rubric provides objective scoring criteria for evaluating Fishbone diagram quality. Use the scoring script (`scripts/score_analysis.py`) for calculation.

**Passing threshold**: 70 points
**Rating scale**: Poor (0-49), Fair (50-69), Good (70-84), Excellent (85-100)

---

## Dimension 1: Problem Clarity (15%)

Evaluates how well the problem/effect statement is defined.

| Score | Criteria |
|-------|----------|
| **5** | Specific, measurable, time-bounded. Observable effect (not assumed cause). Includes what, where, when, and extent. No blame or solution embedded. |
| **4** | Specific and measurable. Minor gaps in context (missing time or extent). Clear observable effect. |
| **3** | Moderately specific. Some vagueness in what/where/when. Generally understandable problem. |
| **2** | Vague or broad. Missing critical specifics. May be a symptom rather than problem. |
| **1** | Very vague, abstract, or unclear. Could apply to many different situations. May embed assumed cause or solution. |

**Key Questions**:
- Is it specific enough that two people would understand the same problem?
- Does it describe what happened, not why?
- Can you measure success in addressing it?

---

## Dimension 2: Category Coverage (20%)

Evaluates completeness of category exploration.

| Score | Criteria |
|-------|----------|
| **5** | All relevant categories explored with 3+ causes each. Categories customized appropriately for context. No blind spots evident. |
| **4** | All categories have 2+ causes. Minor gaps in 1-2 categories. Good overall coverage. |
| **3** | Most categories explored. 1-2 categories thin (1 cause) or missing. Adequate coverage of key areas. |
| **2** | Several categories thin or missing. Uneven coverage. Some relevant areas overlooked. |
| **1** | Many categories empty or missing. Narrow focus. Major blind spots evident. |

**Key Questions**:
- Does every category have at least 2-3 causes?
- Were prompting questions used for thin categories?
- Is the category framework appropriate for the context?

---

## Dimension 3: Cause Depth (25%)

Evaluates the depth of sub-cause analysis.

| Score | Criteria |
|-------|----------|
| **5** | Major causes have 3+ levels of sub-causes. "Why?" asked repeatedly until actionable root causes reached. Clear causal chains visible. |
| **4** | Most major causes have 2-3 levels. Good drilling into key causes. Some areas could be deeper. |
| **3** | Some sub-causes present but inconsistent. Mix of deep and shallow branches. Level 2 present, Level 3 sparse. |
| **2** | Mostly Level 1 causes only. Limited sub-cause drilling. Flat diagram structure. |
| **1** | No sub-causes. Only top-level causes listed. No "Why?" analysis evident. |

**Key Questions**:
- Can you trace from the problem through multiple levels to an actionable cause?
- Are the deepest causes actionable (something you could fix)?
- Did the analysis stop at symptoms or reach root causes?

---

## Dimension 4: Cause Quality (20%)

Evaluates the quality of individual causes identified.

| Score | Criteria |
|-------|----------|
| **5** | Causes are specific, distinct, non-overlapping. Process/system focused (not person-blame). Mix of obvious and non-obvious. Causes don't restate problem. Evidence-based where possible. |
| **4** | Most causes are specific and distinct. Generally process-focused. Minor overlap or vagueness in some causes. |
| **3** | Adequate specificity. Some causes are vague or overlap. May include some person-blame or problem restatement. |
| **2** | Many vague or generic causes. Significant overlap. Person-blame present. Some causes restate the problem. |
| **1** | Causes are vague, generic, or mostly person-blame. Heavy overlap. Problem restated as causes. |

**Key Questions**:
- Are causes specific enough to investigate?
- Do causes focus on processes/systems rather than individuals?
- Are causes distinct (not duplicates or overlapping)?

---

## Dimension 5: Prioritization (10%)

Evaluates how causes were prioritized for follow-up.

| Score | Criteria |
|-------|----------|
| **5** | Clear prioritization method applied (multi-voting, impact-effort, data-driven). Top 3-5 causes identified with rationale. Verification plan for each. |
| **4** | Prioritization method used. Top causes identified. Rationale documented. Minor gaps in verification planning. |
| **3** | Some prioritization evident. Top causes identified informally. Limited rationale documented. |
| **2** | Minimal prioritization. No clear method. Vague sense of "important" causes. |
| **1** | No prioritization. All causes treated equally or arbitrarily selected. |

**Key Questions**:
- Was a structured prioritization method used?
- Are the top 3-5 causes clearly identified?
- Is there a plan to verify/investigate the prioritized causes?

---

## Dimension 6: Documentation (10%)

Evaluates the quality of the documented output.

| Score | Criteria |
|-------|----------|
| **5** | Complete visual diagram. Clear labeling. All information captured. Professional presentation. Shareable with stakeholders. Action items assigned. |
| **4** | Good visual diagram. Minor labeling gaps. Most information captured. Presentable output. |
| **3** | Basic diagram created. Adequate labeling. Key information present. Needs cleanup for sharing. |
| **2** | Rough diagram. Poor labeling or organization. Missing information. Not shareable as-is. |
| **1** | No diagram or very incomplete. Information scattered or missing. Not usable for follow-up. |

**Key Questions**:
- Is the diagram visually clear and well-organized?
- Could someone not in the session understand it?
- Are action items and owners captured?

---

## Scoring Calculation

```
Score = (
    problem_clarity × 0.15 +
    category_coverage × 0.20 +
    cause_depth × 0.25 +
    cause_quality × 0.20 +
    prioritization × 0.10 +
    documentation × 0.10
) × 20

(Converts 1-5 scale to 0-100)
```

---

## Score Interpretation

| Score Range | Rating | Interpretation |
|-------------|--------|----------------|
| 85-100 | Excellent | Comprehensive analysis ready for root cause verification |
| 70-84 | Good | Solid analysis with minor improvements possible |
| 50-69 | Fair | Adequate starting point but significant gaps to address |
| 0-49 | Poor | Major issues - revisit problem definition and analysis |

---

## Improvement Recommendations by Dimension

### If Problem Clarity is low:
- Apply 5W2H framework to sharpen the statement
- Ask: "What would someone see if they observed this problem?"
- Separate the observable effect from assumed causes

### If Category Coverage is low:
- Use prompting questions for each category (see `category-frameworks.md`)
- Consider alternative frameworks (6Ms vs 8Ps vs custom)
- Challenge "this doesn't apply" assumptions

### If Cause Depth is low:
- For each major cause, ask "Why might this happen?" 2-3 times
- Set a minimum depth requirement (Level 3 for top causes)
- Consider applying 5 Whys to prioritized causes

### If Cause Quality is low:
- Review causes for person-blame and convert to system focus
- Check if any causes simply restate the problem
- Add specificity: "What exactly?" "Under what conditions?"

### If Prioritization is low:
- Conduct multi-voting exercise (3 votes per participant)
- Create impact-effort matrix for top 10 causes
- Use data (if available) to validate assumptions

### If Documentation is low:
- Generate formal diagram using `scripts/generate_diagram.py`
- Create HTML report with `scripts/generate_report.py`
- Ensure all causes legibly labeled, owner and date documented
