# FMEA Quality Rubric

## Overview

This rubric provides objective scoring criteria for evaluating FMEA quality. Each dimension is rated 1-5, weighted, and combined for an overall quality score.

## Scoring Dimensions

### 1. Structure Analysis (Weight: 15%)

**5 - Excellent**
- Complete system/process breakdown to appropriate level
- All interfaces and interactions identified
- Clear hierarchy from system to component/step level
- Consistent nomenclature throughout
- Block diagrams or structure trees provided

**4 - Good**
- Most elements identified with minor gaps
- Key interfaces captured
- Hierarchy mostly clear
- Minor nomenclature inconsistencies
- Diagrams provided but could be more detailed

**3 - Adequate**
- Basic structure captured
- Some interfaces missing
- Hierarchy somewhat unclear
- Inconsistent naming conventions
- Limited visual documentation

**2 - Marginal**
- Incomplete breakdown
- Many interfaces missing
- Confusing hierarchy
- Naming issues throughout
- No supporting diagrams

**1 - Inadequate**
- No meaningful structure analysis
- Random element listing without organization
- No hierarchy established
- No standardized naming
- No documentation of system relationships

### 2. Function Definition (Weight: 15%)

**5 - Excellent**
- All functions stated in verb + noun format
- Each function linked to measurable requirement
- Performance specifications clearly stated
- Customer requirements traceable
- Functions cover all operating modes/conditions

**4 - Good**
- Most functions properly formatted
- Most functions linked to requirements
- Specifications mostly stated
- Good traceability
- Major operating modes covered

**3 - Adequate**
- Basic function statements present
- Some linkage to requirements
- Partial specifications
- Limited traceability
- Primary mode covered only

**2 - Marginal**
- Vague function statements
- Weak requirement linkage
- Missing specifications
- Poor traceability
- Operating modes not considered

**1 - Inadequate**
- No clear function statements
- No requirement linkage
- No specifications referenced
- No traceability
- No consideration of operating conditions

### 3. Failure Chain Logic (Weight: 20%)

**5 - Excellent**
- All failure modes relate to function loss/degradation
- Effects clearly describe impact at higher level AND customer
- Causes are at appropriate (lower) level
- Mode→Effect→Cause chain is logically complete
- Multiple effects and causes captured where appropriate
- Clear distinction between modes, effects, and causes

**4 - Good**
- Most failure modes properly linked to functions
- Effects generally clear
- Causes mostly at correct level
- Chain logic mostly sound
- Some multiple pathways captured
- Minor confusion between categories

**3 - Adequate**
- Basic failure modes identified
- Effects somewhat vague
- Causes sometimes at wrong level
- Chain logic has gaps
- Limited pathway analysis
- Some mode/cause confusion

**2 - Marginal**
- Incomplete failure mode identification
- Effects unclear or missing
- Causes frequently misplaced
- Logic chain broken
- Single pathway thinking
- Significant category confusion

**1 - Inadequate**
- Missing or nonsensical failure modes
- No meaningful effects analysis
- Causes confused with effects or modes
- No logical chain
- No pathway analysis
- Complete confusion of FMEA elements

### 4. Control Identification (Weight: 15%)

**5 - Excellent**
- Prevention controls clearly distinguished from detection
- All existing controls documented
- Control effectiveness realistically assessed
- Controls linked to specific causes
- Both design/process and verification controls captured
- Control gaps identified

**4 - Good**
- Prevention/detection mostly distinguished
- Most controls documented
- Effectiveness generally realistic
- Good cause linkage
- Most control types captured
- Some gaps identified

**3 - Adequate**
- Some prevention/detection confusion
- Basic controls documented
- Effectiveness sometimes optimistic
- Partial cause linkage
- Limited control types
- Gaps not systematically identified

**2 - Marginal**
- Prevention/detection confused
- Many controls missing
- Effectiveness unrealistic
- Weak cause linkage
- Narrow control focus
- Gaps ignored

**1 - Inadequate**
- No distinction between control types
- Controls not documented
- No effectiveness assessment
- No cause linkage
- No controls identified
- No gap analysis

### 5. Rating Consistency (Weight: 20%)

**5 - Excellent**
- Ratings consistently applied across all items
- Rating rationale documented
- Severity based on worst-case effect
- Occurrence based on data/evidence where available
- Detection based on control capability analysis
- Similar items receive similar ratings

**4 - Good**
- Ratings mostly consistent
- Most rationale documented
- Severity generally worst-case
- Occurrence mostly evidence-based
- Detection generally realistic
- Minor inconsistencies between similar items

**3 - Adequate**
- Some rating inconsistencies
- Limited rationale documentation
- Severity sometimes not worst-case
- Occurrence often opinion-based
- Detection sometimes optimistic
- Noticeable inconsistencies

**2 - Marginal**
- Significant inconsistencies
- No rationale documentation
- Severity understated
- Occurrence pure guesswork
- Detection overly optimistic
- Major inconsistencies across items

**1 - Inadequate**
- Random or arbitrary ratings
- No basis for ratings
- Severity ignored
- Occurrence meaningless
- Detection unrealistic
- No consistency whatsoever

### 6. Action Effectiveness (Weight: 15%)

**5 - Excellent**
- All High AP items have specific actions
- Actions target root cause (prevention) or improve detection
- Responsible person and target date assigned
- Actions are measurable and verifiable
- Re-evaluation ratings reflect actual improvement
- Low AP items justified if no action taken

**4 - Good**
- Most High AP items have actions
- Actions generally appropriate
- Most have ownership and dates
- Most actions measurable
- Re-evaluation mostly done
- Some Low AP justification

**3 - Adequate**
- Some High AP items lack actions
- Actions sometimes generic
- Ownership sometimes missing
- Measurability unclear
- Partial re-evaluation
- Limited Low AP justification

**2 - Marginal**
- Many High AP items without actions
- Actions vague or ineffective
- Poor ownership assignment
- Actions not measurable
- No re-evaluation
- No Low AP justification

**1 - Inadequate**
- No actions despite High AP items
- Actions meaningless or absent
- No ownership
- Nothing measurable
- No follow-through
- No justification anywhere

## Scoring Calculation

### Individual Dimension Score
Each dimension rated 1-5 based on criteria above.

### Overall Score Calculation
```
Overall Score = Σ(Dimension Score × Weight) × 20
```

Example:
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Structure Analysis | 4 | 0.15 | 0.60 |
| Function Definition | 4 | 0.15 | 0.60 |
| Failure Chain Logic | 3 | 0.20 | 0.60 |
| Control Identification | 4 | 0.15 | 0.60 |
| Rating Consistency | 4 | 0.20 | 0.80 |
| Action Effectiveness | 3 | 0.15 | 0.45 |
| **Total** | | | **3.65** |

Overall Score = 3.65 × 20 = **73 points**

### Score Interpretation

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90-100 | Excellent | Industry-leading FMEA |
| 80-89 | Good | Solid, effective analysis |
| 70-79 | Acceptable | Meets minimum requirements |
| 60-69 | Needs Improvement | Significant gaps to address |
| Below 60 | Unacceptable | Major rework required |

## Scoring Notes

1. **Weighted priorities**: Failure Chain Logic and Rating Consistency receive highest weights because they most directly impact risk identification accuracy.

2. **Critical failures**: Any dimension scoring 1 should trigger immediate remediation regardless of overall score.

3. **Safety items**: For FMEAs involving safety-critical items (Severity 9-10), require minimum score of 4 on Failure Chain Logic and Control Identification.

4. **Regulatory context**: Adjust thresholds based on industry requirements (automotive, aerospace, medical devices have varying standards).
