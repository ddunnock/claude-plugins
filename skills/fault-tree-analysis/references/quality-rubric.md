# Fault Tree Analysis Quality Rubric

## Overview

This rubric provides objective scoring criteria for evaluating Fault Tree Analysis quality. Each dimension is rated 1-5, weighted, and combined for an overall quality score.

## Scoring Dimensions

### 1. System Definition (Weight: 15%)

**5 - Excellent**
- System boundaries explicitly defined with clear in/out scope
- All operating modes and conditions specified
- Comprehensive assumptions documented
- Reference documentation identified and accessible
- Analysis purpose and objectives clearly stated

**4 - Good**
- Boundaries defined with minor ambiguities
- Primary operating conditions specified
- Key assumptions documented
- Most reference documentation available
- Purpose stated but could be more specific

**3 - Adequate**
- Boundaries loosely defined
- Some operating conditions missing
- Basic assumptions listed
- Limited documentation referenced
- Purpose generally understood

**2 - Marginal**
- Boundaries unclear or overly broad
- Operating conditions incomplete
- Assumptions vague or missing
- Documentation sparse
- Purpose unclear

**1 - Inadequate**
- No system boundaries defined
- Operating conditions not specified
- No assumptions documented
- No reference documentation
- Purpose not stated

### 2. Top Event Clarity (Weight: 15%)

**5 - Excellent**
- Single, specific, unambiguous event
- Failure state precisely defined with measurable criteria
- Appropriate system level (functional failure)
- Observable and verifiable condition
- Severity/criticality clearly characterized

**4 - Good**
- Clear event with minor ambiguity
- Failure state well-defined
- Appropriate level with slight room for refinement
- Observable condition
- Severity generally understood

**3 - Adequate**
- Event generally clear but some interpretation required
- Failure state defined but not precisely measurable
- Level acceptable but could be more specific
- Condition observable with some difficulty
- Severity mentioned but not quantified

**2 - Marginal**
- Event vague or too broad
- Failure state poorly defined
- Level too high or too low
- Observability questionable
- Severity not addressed

**1 - Inadequate**
- Multiple events conflated
- No clear failure definition
- Completely inappropriate level
- Cannot observe or verify
- No consideration of severity

### 3. Tree Completeness (Weight: 25%)

**5 - Excellent**
- All failure pathways fully developed to basic events
- Consistent and correct gate logic throughout
- No redundant or duplicate events
- Undeveloped events explicitly justified
- Human factors and external events included
- Common cause failure potential identified
- Tree structure is logical and traceable

**4 - Good**
- Most pathways fully developed
- Gate logic generally correct
- Minimal redundancy
- Most undeveloped events justified
- Key human factors considered
- Some CCF potential noted
- Structure mostly logical

**3 - Adequate**
- Primary pathways developed
- Some gate logic issues
- Minor redundancy present
- Several undeveloped events without justification
- Limited human factors consideration
- CCF not systematically addressed
- Structure acceptable but could be cleaner

**2 - Marginal**
- Significant gaps in development
- Multiple gate logic errors
- Notable redundancy
- Many unexplained undeveloped events
- Human factors ignored
- CCF not considered
- Structure confusing

**1 - Inadequate**
- Tree barely developed beyond top event
- Fundamental gate errors
- Extensive redundancy/contradiction
- Most events undeveloped
- Critical pathways missing
- No structure discipline

### 4. Minimal Cut Sets (Weight: 20%)

**5 - Excellent**
- All minimal cut sets correctly identified
- Cut sets listed by order
- Single points of failure clearly flagged
- CCF combinations identified
- Cut set importance ranked
- Design implications discussed

**4 - Good**
- Most MCS correctly identified
- Listed by order
- SPOFs noted
- Some CCF consideration
- Importance generally understood
- Some design implications noted

**3 - Adequate**
- Primary MCS identified
- Order partially organized
- SPOFs identified but incomplete
- Limited CCF analysis
- Importance not ranked
- Minimal design discussion

**2 - Marginal**
- MCS identification incomplete
- Not organized by order
- SPOFs missed
- No CCF analysis
- No importance assessment
- No design implications

**1 - Inadequate**
- MCS not identified
- Analysis stops at tree construction
- No understanding of cut set concept

### 5. Quantification (Weight: 15%)

*Note: Score 3 if quantitative analysis not performed but not required*

**5 - Excellent**
- All basic event probabilities documented
- Data sources identified and traceable
- Mission time/exposure clearly stated
- Calculations correct and verified
- Uncertainty/confidence levels stated
- Top event probability calculated correctly
- Importance measures computed

**4 - Good**
- Most probabilities documented
- Data sources generally identified
- Mission time stated
- Calculations generally correct
- Some uncertainty consideration
- Top event probability reasonable
- Basic importance analysis

**3 - Adequate / Not Required**
- Qualitative analysis only (acceptable if justified)
- OR partial quantification with gaps
- Limited data sources
- Some calculation issues
- No uncertainty analysis
- Approximate top event probability

**2 - Marginal**
- Incomplete probabilities
- Data sources questionable
- Calculation errors
- No uncertainty consideration
- Top event probability unreliable

**1 - Inadequate**
- No quantification attempted when required
- Fabricated probability values
- Fundamental calculation errors
- Results not usable

### 6. Actionability (Weight: 10%)

**5 - Excellent**
- Clear design improvement recommendations
- Prioritized by risk reduction effectiveness
- Cost/benefit consideration
- Implementation path identified
- Validation criteria specified
- Links to specific cut sets/vulnerabilities

**4 - Good**
- Design recommendations provided
- Some prioritization
- Implementation generally feasible
- Validation mentioned
- Links to analysis findings

**3 - Adequate**
- General recommendations made
- Limited prioritization
- Feasibility not fully assessed
- Generic validation approach
- Loose link to findings

**2 - Marginal**
- Vague recommendations
- No prioritization
- Feasibility questionable
- No validation approach
- Disconnected from analysis

**1 - Inadequate**
- No recommendations
- Analysis ends without conclusions
- No actionable outputs

## Score Calculation

### Individual Dimension Scores
Each dimension: 1-5 rating

### Weighted Score Calculation
```
Overall Score = (
    System_Definition × 0.15 +
    Top_Event_Clarity × 0.15 +
    Tree_Completeness × 0.25 +
    Minimal_Cut_Sets × 0.20 +
    Quantification × 0.15 +
    Actionability × 0.10
) × 20
```

### Score Ranges

| Range | Rating | Interpretation |
|-------|--------|----------------|
| 90-100 | Excellent | Comprehensive, rigorous analysis ready for critical decisions |
| 80-89 | Good | Solid analysis with minor gaps; suitable for most purposes |
| 70-79 | Adequate | Acceptable analysis; some areas need improvement |
| 60-69 | Marginal | Significant gaps; use findings with caution |
| <60 | Inadequate | Major deficiencies; do not rely on conclusions |

**Minimum Passing Score**: 70 points

## Critical Failures

Regardless of overall score, analysis fails if any of these are present:

1. **Logic Errors**: Fundamental AND/OR gate misuse that changes analysis conclusions
2. **Missing SPOFs**: Single points of failure exist but not identified
3. **Top Event Ambiguity**: Cannot clearly define what "failure" means
4. **Circular Logic**: Events reference themselves or create loops
5. **Calculation Errors**: Order-of-magnitude errors in probability calculations
