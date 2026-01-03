# Trade Study Report Template

## Document Information

| Field | Value |
|-------|-------|
| Study Title | [TITLE] |
| Document Version | [VERSION] |
| Date | [DATE] |
| Author(s) | [AUTHORS] |
| Approver | [APPROVER] |
| Classification | [CLASSIFICATION] |

---

## Executive Summary

### Recommendation

[STATE THE RECOMMENDED ALTERNATIVE AND KEY RATIONALE]

**Leading Alternative:** [NAME] (Score: [X.XX])  
**Decision Confidence:** [High/Medium/Low]

### Key Findings

1. [FINDING 1]
2. [FINDING 2]
3. [FINDING 3]

### Critical Assumptions

This recommendation is contingent on the following assumptions:
- [ASSUMPTION 1]
- [ASSUMPTION 2]

---

## 1. Introduction

### 1.1 Purpose

[DESCRIBE THE PURPOSE OF THIS TRADE STUDY]

### 1.2 Scope

[DEFINE THE SCOPE AND BOUNDARIES]

### 1.3 Methodology

This trade study follows the DAU 9-Step Trade Study Process as defined in "Systems Engineering Fundamentals" (DAU Press, 2001, Chapter 12):
1. Define the Problem
2. Identify Requirements
3. Establish Alternatives
4. Define Evaluation Criteria
5. Assign Criteria Weights
6. Develop Scoring Scales
7. Evaluate Alternatives
8. Perform Sensitivity Analysis
9. Document Results

---

## 2. Problem Statement

### 2.1 Problem Definition

[APPROVED PROBLEM STATEMENT]

**Source:** [SOURCE DOCUMENT]

### 2.2 Root Cause Analysis

[SUMMARY OF ROOT CAUSE ANALYSIS - 5 WHYS OR FISHBONE]

**Root Cause Identified:** [ROOT CAUSE]

---

## 3. Alternatives

### 3.1 Alternative Overview

| ID | Alternative | Description | Source |
|----|-------------|-------------|--------|
| A1 | [NAME] | [DESCRIPTION] | [SOURCE] |
| A2 | [NAME] | [DESCRIPTION] | [SOURCE] |
| A3 | [NAME] | [DESCRIPTION] | [SOURCE] |

### 3.2 Alternative Details

#### Alternative 1: [NAME]

[DETAILED DESCRIPTION]

**Source:** [SOURCE DOCUMENT, SECTION/PAGE]

#### Alternative 2: [NAME]

[DETAILED DESCRIPTION]

**Source:** [SOURCE DOCUMENT, SECTION/PAGE]

---

## 4. Evaluation Methodology

### 4.1 Criteria Definitions

| ID | Criterion | Description | Direction | Source |
|----|-----------|-------------|-----------|--------|
| C1 | [NAME] | [DESCRIPTION] | [Max/Min] | [SOURCE] |
| C2 | [NAME] | [DESCRIPTION] | [Max/Min] | [SOURCE] |

### 4.2 Weight Assignment

**Method Used:** [DIRECT/ROC/AHP]

| Criterion | Weight | Rationale | Source |
|-----------|--------|-----------|--------|
| [C1] | [0.XX] | [RATIONALE] | [SOURCE] |
| [C2] | [0.XX] | [RATIONALE] | [SOURCE] |

**AHP Consistency Ratio:** [CR VALUE] (Threshold: < 0.10)

### 4.3 Normalization

**Method:** [MIN-MAX / Z-SCORE / LOG / PERCENTILE]

### 4.4 Scoring Function

**Function:** [LINEAR / STEP / EXPONENTIAL / SIGMOID]

### 4.5 Aggregation

**Method:** [WEIGHTED SUM / WEIGHTED PRODUCT / TOPSIS]

---

## 5. Data Collection

### 5.1 Source Registry

| Source ID | Document | Type | Date | Confidence |
|-----------|----------|------|------|------------|
| SRC-001 | [NAME] | [TYPE] | [DATE] | [H/M/L] |
| SRC-002 | [NAME] | [TYPE] | [DATE] | [H/M/L] |

### 5.2 Data Quality Summary

- **High Confidence Data:** [N]%
- **Medium Confidence Data:** [N]%
- **Low Confidence Data:** [N]%
- **Data Gaps Addressed:** [N]

### 5.3 Raw Data

| Criterion | Alt 1 | Source | Alt 2 | Source | Alt 3 | Source |
|-----------|-------|--------|-------|--------|-------|--------|
| [C1] | [VAL] | SRC-X | [VAL] | SRC-X | [VAL] | SRC-X |
| [C2] | [VAL] | SRC-X | [VAL] | SRC-X | [VAL] | SRC-X |

---

## 6. Analysis Results

### 6.1 Decision Matrix

| Criterion | Weight | Alt 1 | Alt 2 | Alt 3 |
|-----------|--------|-------|-------|-------|
| [C1] | [W1] | [S1a] | [S1b] | [S1c] |
| [C2] | [W2] | [S2a] | [S2b] | [S2c] |
| **TOTAL** | **1.00** | **[T1]** | **[T2]** | **[T3]** |
| **RANK** | | **[R1]** | **[R2]** | **[R3]** |

### 6.2 [DIAGRAM: Decision Matrix Heatmap]

[INSERT DIAGRAM OR REFERENCE]

### 6.3 Score Comparison

[INSERT SCORE COMPARISON BAR CHART OR REFERENCE]

---

## 7. Sensitivity Analysis

### 7.1 Analyses Performed

- [x] Weight Zeroing (DAU Method)
- [x] Tornado Analysis (±[X]%)
- [x] Monte Carlo Simulation ([N] iterations)
- [x] Breakeven Analysis

### 7.2 Decision Robustness

**Overall Robustness:** [High/Medium/Low]

**Basis:** [EXPLANATION]

### 7.3 Decision-Driving Criteria

1. **[CRITERION]** - Removing this criterion would change the winner
2. **[CRITERION]** - High sensitivity to weight variations

### 7.4 Win Probability (Monte Carlo)

| Alternative | Win Frequency | 95% CI Score |
|-------------|---------------|--------------|
| [Alt 1] | [X]% | [LOW] - [HIGH] |
| [Alt 2] | [X]% | [LOW] - [HIGH] |

### 7.5 Breakeven Points

[DESCRIBE WEIGHT CHANGES REQUIRED TO FLIP DECISION]

### 7.6 [DIAGRAM: Tornado Diagram]

[INSERT DIAGRAM OR REFERENCE]

---

## 8. Findings and Recommendation

### 8.1 Key Findings

1. [FINDING 1 WITH SOURCE CITATION]
2. [FINDING 2 WITH SOURCE CITATION]
3. [FINDING 3 WITH SOURCE CITATION]

### 8.2 Recommendation

**Recommended Alternative:** [NAME]

**Score:** [X.XX] out of [Y.YY]

**Rationale:**

[DETAILED RATIONALE WITH SOURCE CITATIONS]

### 8.3 Implementation Considerations

[DISCUSS IMPLEMENTATION FACTORS]

### 8.4 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [RISK 1] | [L/M/H] | [L/M/H] | [MITIGATION] |

---

## 9. Assumptions and Limitations

### 9.1 Assumption Summary

**Total Assumptions:** [N]
- Data Assumptions: [n]
- Methodology Assumptions: [n]
- Scope Assumptions: [n]

### 9.2 Detailed Assumptions

#### Data Assumptions

**[A-001]** [DESCRIPTION]
- Basis: [SOURCE OR RATIONALE]
- Impact if incorrect: [HIGH/MEDIUM/LOW] - [EXPLANATION]
- Status: Approved

#### Methodology Assumptions

**[A-010]** [DESCRIPTION]
- Basis: [SOURCE OR RATIONALE]
- Impact if incorrect: [HIGH/MEDIUM/LOW] - [EXPLANATION]
- Status: Approved

### 9.3 Limitations

1. [LIMITATION 1]
   - Impact on conclusions: [ASSESSMENT]
   - Mitigation: [HOW ADDRESSED]

2. [LIMITATION 2]
   - Impact on conclusions: [ASSESSMENT]
   - Mitigation: [HOW ADDRESSED]

---

## 10. Source References

### 10.1 Primary Sources

1. **[SRC-001]** [DOCUMENT NAME]
   - Type: [TYPE]
   - Version: [VERSION]
   - Date: [DATE]
   - Cited in: [SECTIONS]

2. **[SRC-002]** [DOCUMENT NAME]
   - Type: [TYPE]
   - Version: [VERSION]
   - Date: [DATE]
   - Cited in: [SECTIONS]

### 10.2 User-Provided Information

1. **[USR-001]** [DESCRIPTION]
   - Date provided: [DATE]
   - Used for: [PURPOSE]

---

## Appendices

### Appendix A: Detailed Calculations

[INCLUDE DETAILED CALCULATION AUDIT TRAIL]

### Appendix B: Raw Data Tables

[INCLUDE COMPLETE RAW DATA]

### Appendix C: Sensitivity Analysis Details

[INCLUDE DETAILED SENSITIVITY RESULTS]

### Appendix D: Diagrams

[LIST OF ALL INCLUDED DIAGRAMS]

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | | | |
| Reviewer | | | |
| Approver | | | |

---

*Document generated using Trade Study Analysis Tool*
*All claims are grounded in documented sources as indicated*
