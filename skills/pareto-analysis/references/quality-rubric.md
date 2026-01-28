# Pareto Analysis Quality Scoring Rubric

Detailed scoring criteria for evaluating Pareto Analysis quality.

## Scoring Dimensions

### 1. Problem Clarity (15% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Specific outcome defined; measurement type clear (frequency/cost/time); direct business relevance articulated; scope bounded appropriately |
| 4 | Good | Clear problem statement; measurement type specified; business context understood |
| 3 | Adequate | Problem identified but lacks specificity in scope or measurement |
| 2 | Marginal | Vague problem statement; unclear what is being measured or why |
| 1 | Inadequate | No clear problem definition; measurement type undefined |

**Key Questions:**
- Is the analysis objective clear and specific?
- Is the measurement type appropriate for the problem?
- Is there clear business relevance?

### 2. Data Quality (25% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Representative time period; ≥50 data points; verified data accuracy; documented data sources; no missing categories |
| 4 | Good | Adequate time period; 30-50 data points; data source documented; minor gaps acceptable |
| 3 | Adequate | Minimum viable data (20-30 points); some documentation; potential gaps acknowledged |
| 2 | Marginal | Insufficient data (<20 points); undocumented sources; questionable accuracy |
| 1 | Inadequate | Too little data to draw conclusions; no source documentation |

**Key Questions:**
- Is the data representative of normal operations?
- Is the sample size sufficient for reliable conclusions?
- Are data sources documented and verifiable?

### 3. Category Design (20% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | MECE categories; 5-8 actionable categories; "Other" ≤5% of total; clear definitions documented |
| 4 | Good | Mostly MECE; 7-10 categories; "Other" ≤10%; definitions provided |
| 3 | Adequate | Minor overlap or gaps; 10-12 categories; "Other" ≤15% |
| 2 | Marginal | Significant overlap; too many (>12) or too few (<4) categories; large "Other" |
| 1 | Inadequate | Categories overlap heavily; non-actionable groupings; "Other" dominant |

**Key Questions:**
- Are categories mutually exclusive?
- Are categories collectively exhaustive?
- Can you take action on each category?
- Is the "Other" category appropriately sized?

### 4. Calculation Accuracy (15% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Correct descending sort; accurate percentages; correct cumulative calculation; proper 80% threshold identification |
| 4 | Good | All calculations correct; minor formatting issues |
| 3 | Adequate | Calculations mostly correct; small rounding errors |
| 2 | Marginal | Errors in cumulative calculation or threshold identification |
| 1 | Inadequate | Fundamental calculation errors; incorrect sorting |

**Key Questions:**
- Are categories sorted by value in descending order?
- Are percentages calculated correctly?
- Is the cumulative percentage computed correctly?
- Is the 80% threshold properly identified?

### 5. Pattern Interpretation (15% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Correctly identifies Pareto effect strength; validates findings with domain knowledge; acknowledges limitations; considers weighting appropriateness |
| 4 | Good | Correct pattern identification; reasonable conclusions; limitations noted |
| 3 | Adequate | Basic pattern recognition; conclusions reasonable but superficial |
| 2 | Marginal | Misinterprets pattern (e.g., claims 80/20 when flat); overconfident conclusions |
| 1 | Inadequate | No pattern analysis; incorrect conclusions from data |

**Key Questions:**
- Is the Pareto effect present (steep cumulative curve)?
- Are conclusions supported by the data?
- Are limitations acknowledged?
- Is weighting considered if appropriate?

### 6. Actionability (10% weight)

| Score | Rating | Criteria |
|-------|--------|----------|
| 5 | Excellent | Clear next steps defined; vital few linked to root cause investigation; cost/effort to address considered; timeline proposed |
| 4 | Good | Next steps identified; logical connection to improvement actions |
| 3 | Adequate | Some recommendations; general direction for action |
| 2 | Marginal | Vague recommendations; no clear path forward |
| 1 | Inadequate | No recommendations; analysis ends at chart creation |

**Key Questions:**
- Are specific next steps identified?
- Is there a clear link to root cause investigation for vital few?
- Is cost/effort to address each priority considered?

## Scoring Calculation

```
Total Score = Σ(Dimension Score × Weight × 20)

Where:
- Each dimension score is 1-5
- Weight is the percentage (as decimal)
- Multiply by 20 to scale to 100-point system
```

**Example Calculation:**
| Dimension | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Problem Clarity | 4 | 0.15 | 12.0 |
| Data Quality | 4 | 0.25 | 20.0 |
| Category Design | 3 | 0.20 | 12.0 |
| Calculation Accuracy | 5 | 0.15 | 15.0 |
| Pattern Interpretation | 4 | 0.15 | 12.0 |
| Actionability | 3 | 0.10 | 6.0 |
| **TOTAL** | | | **77.0** |

## Score Interpretation

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90-100 | Excellent | Professional-quality analysis ready for executive presentation |
| 80-89 | Good | Solid analysis with minor improvements possible |
| 70-79 | Adequate | Meets minimum standards; some refinement recommended |
| 60-69 | Marginal | Significant gaps; requires revision before use |
| <60 | Inadequate | Fundamental issues; redo analysis |

## Improvement Recommendations by Score

**If Problem Clarity score is low:**
- Revisit the problem statement
- Clarify the measurement type
- Document business relevance

**If Data Quality score is low:**
- Extend data collection period
- Increase sample size
- Verify data accuracy
- Document sources

**If Category Design score is low:**
- Review categories for MECE compliance
- Consider splitting large "Other" category
- Ensure categories are actionable

**If Calculation Accuracy score is low:**
- Use the provided calculation script
- Verify sort order
- Check cumulative formula

**If Pattern Interpretation score is low:**
- Assess cumulative curve steepness objectively
- Consider weighting if frequency alone is misleading
- Acknowledge when Pareto effect is weak

**If Actionability score is low:**
- Define specific next steps for vital few
- Link to root cause investigation (Fishbone, 5 Whys)
- Consider cost/effort matrix for priorities
