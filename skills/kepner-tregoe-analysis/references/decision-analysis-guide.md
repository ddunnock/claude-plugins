# Decision Analysis Guide

Decision Analysis (DA) provides a systematic method for selecting the best alternative by evaluating options against weighted criteria and assessing risks.

## The Decision Statement

Every decision analysis begins with a clear decision statement that defines:
1. **What** choice must be made
2. **What outcome** is desired

**Format**: "Select [action/option] to [achieve outcome]"

**Good Examples:**
- "Select a CRM system to improve customer relationship management and sales tracking"
- "Select a vendor to supply hydraulic components with optimal quality and cost"
- "Select an approach to reduce production line downtime by 25%"

**Poor Examples:**
- "Pick the best vendor" (outcome unclear)
- "Decide what to do" (action unclear)
- "Fix the problem" (both unclear)

## Objectives: MUSTS vs WANTS

All decision criteria must be classified as either MUSTS (mandatory) or WANTS (desired).

### MUSTS (Mandatory Requirements)

MUSTS are non-negotiable requirements. An alternative MUST meet ALL must criteria to be considered - there is no compromise.

**Characteristics of MUSTS:**
- Pass/Fail evaluation only (no partial credit)
- Absolutely mandatory (no exceptions)
- Measurable and verifiable
- Realistic (achievable by at least one alternative)
- True limits (not disguised wants)

**Good MUST Examples:**
| MUST Criterion | Measurement | Pass/Fail Test |
|----------------|-------------|----------------|
| Budget ≤ $100,000 | Total cost | Is total cost ≤ $100K? |
| Delivery within 90 days | Lead time | Can vendor deliver in ≤90 days? |
| ISO 9001 certified | Certification | Does vendor hold current ISO 9001? |
| Operates at -40°C to +85°C | Temperature spec | Does product meet temp range? |
| FDA approved | Regulatory status | Has FDA approval? |

**Common MUST Categories:**
- Budget/cost constraints
- Timeline/schedule requirements
- Regulatory/compliance requirements
- Safety requirements
- Technical specifications (capacity, performance, compatibility)
- Geographic/location constraints
- Contractual obligations

**Warning Signs of MUST Abuse:**
- Setting MUSTS so tight only one option passes (predetermined outcome)
- Converting strong preferences to MUSTS to manipulate scoring
- Setting unrealistic MUSTS that no option can meet

### WANTS (Desired Outcomes)

WANTS are criteria where more is better (or less is better). They are weighted by importance and scored by how well each alternative satisfies them.

**Characteristics of WANTS:**
- Scored on a scale (typically 1-10)
- Can be partially satisfied
- Weighted by relative importance
- All alternatives can be compared

**Want Definition:**
1. **State the want** - What do you want to achieve/avoid?
2. **Define direction** - Is more better, or less better?
3. **Establish weight** - How important is this (1-10)?

**Good WANT Examples:**
| WANT | Direction | Weight (1-10) | Rationale for Weight |
|------|-----------|---------------|---------------------|
| Minimize maintenance cost | Lower is better | 8 | High operational impact |
| Maximize equipment uptime | Higher is better | 9 | Critical to production |
| Vendor support responsiveness | Faster is better | 6 | Important but not critical |
| Ease of training | Easier is better | 5 | One-time effort |
| Expandability for future needs | More is better | 7 | Strategic importance |

## Weighting WANTS

Assign weights from 1-10 based on relative importance:
- **10**: Critical - Essential to success
- **8-9**: Very Important - Major impact on outcome
- **6-7**: Important - Significant impact
- **4-5**: Moderate - Noticeable impact
- **2-3**: Minor - Small impact
- **1**: Minimal - Nice to have

**Weighting Methods:**

**Method 1: Direct Assignment**
Review each want and assign weight based on judgment.

**Method 2: Pairwise Comparison**
Compare each want to every other want:
- If Want A is more important than Want B, A gets +1
- Sum the wins to establish rank, then assign weights

**Method 3: Constant Sum**
Distribute 100 points across all wants based on importance. Convert to 1-10 scale.

## Scoring Alternatives

### Step 1: Eliminate on MUSTS

For each alternative, check every MUST:
- Does Alternative A meet MUST 1? (Yes/No)
- Does Alternative A meet MUST 2? (Yes/No)
- ...

**GO/NO-GO**: Any "No" eliminates that alternative from further consideration.

### Step 2: Score on WANTS

For each surviving alternative, score against each WANT (1-10):
- **10**: Fully satisfies or exceeds the want
- **7-9**: Satisfies most aspects of the want
- **4-6**: Partially satisfies the want
- **1-3**: Minimally satisfies the want
- **0**: Does not address the want at all

### Step 3: Calculate Weighted Scores

For each alternative:
- Multiply each WANT score by its weight
- Sum all weighted scores
- Calculate total

**Example:**
| WANT | Weight | Option A | Score A | Option B | Score B |
|------|--------|----------|---------|----------|---------|
| Minimize cost | 8 | 7 | 56 | 9 | 72 |
| Maximize uptime | 9 | 8 | 72 | 6 | 54 |
| Vendor support | 6 | 5 | 30 | 8 | 48 |
| Ease of training | 5 | 9 | 45 | 4 | 20 |
| **TOTAL** | | | **203** | | **194** |

### Step 4: Analyze Results

The highest total weighted score indicates the "best" alternative based on stated criteria.

However, before final selection:
1. **Review the math** - Check for calculation errors
2. **Sensitivity check** - Would small changes in weights change the outcome?
3. **Face validity** - Does the result "make sense"? If not, are criteria missing?
4. **Risk assessment** - Consider adverse consequences (see below)

## Risk Assessment (Adverse Consequences)

Before finalizing the decision, evaluate risks for the top 2-3 alternatives.

### Identifying Adverse Consequences

For each alternative, ask:
- What could go wrong if we select this option?
- What negative consequences might occur?
- What concerns do stakeholders have?
- What has gone wrong with similar choices?

### Evaluating Adverse Consequences

For each identified risk:

| Adverse Consequence | Probability (H/M/L) | Seriousness (H/M/L) | Combined |
|--------------------|--------------------|---------------------|----------|
| Vendor goes out of business | L | H | Medium |
| Implementation exceeds timeline | M | M | Medium |
| Users resist the change | H | M | Medium-High |
| Hidden costs emerge | M | H | High |

**Probability Scale:**
- **H (High)**: >70% likely to occur
- **M (Medium)**: 30-70% likely
- **L (Low)**: <30% likely

**Seriousness Scale:**
- **H (High)**: Severe impact on objectives
- **M (Medium)**: Significant but manageable impact
- **L (Low)**: Minor impact

### Interpreting Combined Risk

| Probability | Seriousness | Combined Risk | Action |
|-------------|-------------|---------------|--------|
| H | H | CRITICAL | Avoid alternative or develop robust mitigation |
| H | M | HIGH | Requires mitigation before proceeding |
| M | H | HIGH | Requires mitigation before proceeding |
| H | L | MEDIUM | Monitor and manage |
| M | M | MEDIUM | Monitor and manage |
| L | H | MEDIUM | Have contingency ready |
| M | L | LOW | Accept |
| L | M | LOW | Accept |
| L | L | LOW | Accept |

## Making the Final Decision

The final decision balances:
1. **Weighted Score**: The quantitative evaluation
2. **Risk Profile**: The adverse consequence assessment
3. **Intangibles**: Factors difficult to quantify

**Decision Framework:**
- If one alternative has both highest score AND lowest risk → Clear winner
- If highest score has higher risk → Can risk be mitigated? Is score difference worth the risk?
- If scores are very close → Risk profile may be the deciding factor
- If top alternative has critical risks → Consider second-best or develop mitigation plan

## Common Decision Analysis Errors

| Error | Problem | Correction |
|-------|---------|------------|
| Predetermined winner | Setting criteria to favor one option | Have diverse team set criteria before reviewing options |
| Missing MUSTS | Forgetting hard constraints | Systematically review budget, time, compliance, safety |
| Disguised WANTS as MUSTS | "Must be easy to use" | If it's not truly pass/fail mandatory, it's a WANT |
| Inconsistent scoring | Rating same performance differently | Define scoring anchors before evaluating |
| Ignoring risks | Focusing only on scores | Always complete risk assessment for top alternatives |
| Analysis paralysis | Over-complicating criteria | Keep to 5-8 MUSTS and 5-10 WANTS maximum |
| Weight manipulation | Changing weights to get desired outcome | Lock weights before scoring alternatives |

## Quality Checklist

Before accepting DA results:

- [ ] Decision statement is clear and complete
- [ ] MUSTS are truly mandatory (not strong preferences)
- [ ] MUSTS are realistic (at least one option passes)
- [ ] WANTS are comprehensive (all stakeholder concerns represented)
- [ ] Weights were assigned before scoring alternatives
- [ ] Scoring is consistent across alternatives
- [ ] Calculation is verified
- [ ] Risk assessment completed for top alternatives
- [ ] Result makes intuitive sense (face validity)
