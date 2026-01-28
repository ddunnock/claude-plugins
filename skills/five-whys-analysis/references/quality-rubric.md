# 5 Whys Quality Scoring Rubric

Detailed scoring criteria for evaluating 5 Whys root cause analyses.

## Scoring Dimensions

### 1. Problem Definition (15% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Specific, measurable, time-bound; includes what/where/when/extent; no embedded causes or solutions; verifiable with data |
| 4 | Good | Mostly specific with minor gaps; clear deviation statement; largely free of assumptions |
| 3 | Adequate | Identifies the problem but lacks specificity in 1-2 dimensions; somewhat vague extent |
| 2 | Marginal | Vague problem statement; missing key dimensions; may contain embedded assumptions |
| 1 | Inadequate | Too broad, unclear, or contains assumed causes/solutions in the statement |

**Key Questions:**
- Can you measure this problem?
- Is the deviation from standard clearly stated?
- Does the statement tell us what, where, when, and how much?
- Is the statement free of assumed causes?

### 2. Causal Chain Logic (25% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Every link is logical, specific, and verified; "therefore" test passes both directions; no logical gaps |
| 4 | Good | Chain is mostly logical with minor gaps; most links verified; occasional vagueness |
| 3 | Adequate | Chain follows generally but 1-2 links are weak or assumed; some logical jumps |
| 2 | Marginal | Multiple logical gaps; several unverified assumptions; chain difficult to follow |
| 1 | Inadequate | Chain is illogical, jumps to conclusions, or contains contradictions |

**Verification Test (Apply to each link):**
1. Read forward: "A occurred, therefore B occurred" - Does this make sense?
2. Read backward: "B occurred because A occurred" - Does this hold true?
3. Is this the ONLY reason, or are there alternatives not explored?

### 3. Evidence Basis (20% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | All answers supported by documented evidence (data, logs, observations, standards); sources cited |
| 4 | Good | Most answers evidence-based; 1-2 reasonable inferences clearly marked as such |
| 3 | Adequate | Mix of evidence and inference; assumptions identified but not all verified |
| 2 | Marginal | Primarily assumption-based; limited factual support; opinions treated as facts |
| 1 | Inadequate | No evidence provided; entirely speculative or opinion-based analysis |

**Evidence Types (Strongest to Weakest):**
1. Direct observation/measurement data
2. Documented records (logs, reports, procedures)
3. Multiple corroborating witness accounts
4. Single witness account
5. Expert opinion
6. Assumption/inference (must be validated)

### 4. Root Cause Depth (20% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Reached systemic/process level; addressing this cause prevents recurrence; controllable |
| 4 | Good | Reached actionable process cause; may have deeper systemic factors but current level is addressable |
| 3 | Adequate | Reached a contributing cause but may not be the deepest root; would reduce but not eliminate recurrence |
| 2 | Marginal | Stopped at symptom level; addressing this provides only temporary relief |
| 1 | Inadequate | Root cause is person-blame, external factor, or "it happens"; not actionable |

**Root Cause Level Indicators:**

| Level | Type | Example | Actionability |
|-------|------|---------|---------------|
| 1 | Symptom | "The machine stopped" | Restart it (temporary) |
| 2 | Direct Cause | "The fuse blew" | Replace fuse (temporary) |
| 3 | Contributing Cause | "The bearing wasn't lubricated" | Lubricate (addresses one path) |
| 4 | Root Cause | "No PM schedule exists" | Create schedule (systemic) |
| 5 | Systemic Root | "No system for creating PM schedules" | Implement CMMS (prevents class of problems) |

### 5. Actionability (10% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Root cause is 100% within control; clear ownership; resources available |
| 4 | Good | Cause is largely controllable; may need coordination with other departments |
| 3 | Adequate | Partial control; requires escalation or approval for full resolution |
| 2 | Marginal | Limited control; significant external dependencies or constraints |
| 1 | Inadequate | Cause is external, uncontrollable, or "acts of God" |

**Control Assessment Questions:**
- Who owns this process/system?
- What authority is needed to make changes?
- Are resources (time, money, people) available?
- Are there regulatory or contractual constraints?

### 6. Countermeasures (10% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Specific actions with owners, due dates, success criteria; includes verification and sustainability plan |
| 4 | Good | Clear actions assigned; may lack some specificity in verification or sustainability |
| 3 | Adequate | General actions identified; ownership unclear; limited verification plan |
| 2 | Marginal | Vague actions; no ownership or timeline; no verification method |
| 1 | Inadequate | No countermeasures proposed, or countermeasures address symptoms not root cause |

**Countermeasure Quality Checklist:**
- [ ] Specific action (what exactly will be done)
- [ ] Assigned owner (who is responsible)
- [ ] Due date (when will it be complete)
- [ ] Success criteria (how will we know it worked)
- [ ] Verification method (how will we check)
- [ ] Standardization plan (how will we make it permanent)
- [ ] Sustainability mechanism (how will we maintain it)

## Score Calculation

### Dimension Weights
```
Problem Definition:    15%
Causal Chain Logic:    25%
Evidence Basis:        20%
Root Cause Depth:      20%
Actionability:         10%
Countermeasures:       10%
                      ----
Total:                100%
```

### Formula
```
Overall Score = (Σ (Dimension Score × Weight)) × 20

Where:
- Each dimension is scored 1-5
- Weight is the decimal weight (e.g., 0.25 for 25%)
- Multiply by 20 to convert 5-point scale to 100-point scale
```

### Example Calculation
```
Problem Definition:    4 × 0.15 = 0.60
Causal Chain Logic:    3 × 0.25 = 0.75
Evidence Basis:        4 × 0.20 = 0.80
Root Cause Depth:      4 × 0.20 = 0.80
Actionability:         5 × 0.10 = 0.50
Countermeasures:       3 × 0.10 = 0.30
                              --------
Weighted Sum:                   3.75

Overall Score: 3.75 × 20 = 75 points
```

## Interpretation

| Score Range | Rating | Interpretation |
|-------------|--------|----------------|
| 90-100 | Excellent | Analysis is thorough, evidence-based, and actionable. Proceed with confidence. |
| 80-89 | Good | Analysis is solid with minor improvement opportunities. Acceptable for most applications. |
| 70-79 | Acceptable | Analysis meets minimum standards. Consider strengthening weak areas before major decisions. |
| 60-69 | Marginal | Analysis has significant gaps. Revisit weak dimensions before proceeding. |
| Below 60 | Inadequate | Analysis is insufficient for decision-making. Rework required. |

## Improvement Recommendations by Score

### Low Problem Definition Score
- Revisit the problem with 5W2H framework
- Gather more specific data on extent and timing
- Remove any assumed causes from the statement

### Low Causal Chain Logic Score
- Apply "therefore" test to each link
- Identify where logical jumps occur
- Explore alternative branches

### Low Evidence Basis Score
- Identify which answers are assumptions
- Gather data/documentation to verify
- Mark remaining assumptions clearly

### Low Root Cause Depth Score
- Continue asking "Why?" on the current answer
- Check if answer is person-blame and redirect to process
- Verify that fixing this cause would prevent recurrence

### Low Actionability Score
- Identify what IS controllable in the causal chain
- Escalate if root cause requires higher authority
- Consider interim countermeasures for uncontrollable factors

### Low Countermeasures Score
- Add specificity: who, what, when, how
- Define success criteria and verification method
- Plan for standardization and sustainability
