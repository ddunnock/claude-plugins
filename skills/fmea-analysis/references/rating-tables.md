# FMEA Rating Tables

## Overview

These tables provide standardized criteria for assigning Severity (S), Occurrence (O), and Detection (D) ratings, as well as determining Action Priority (AP) per AIAG-VDA methodology.

**Important**: Ratings are on 1-10 scale where:
- Severity: Higher = More severe impact
- Occurrence: Higher = More frequent
- Detection: Higher = Less likely to detect (worse detection)

---

## Severity Rating Tables

### DFMEA Severity (Effect on Customer/End User)

| Rating | Effect | Criteria |
|--------|--------|----------|
| **10** | Hazardous without warning | Failure affects safe operation and/or involves noncompliance with government regulations without warning |
| **9** | Hazardous with warning | Failure affects safe operation and/or involves noncompliance with government regulations with warning |
| **8** | Very High | Product inoperable, loss of primary function |
| **7** | High | Product operable but at reduced level of performance. Customer very dissatisfied |
| **6** | Moderate | Product operable but comfort/convenience items inoperable. Customer experiences discomfort |
| **5** | Low | Product operable but comfort/convenience items at reduced level. Customer somewhat dissatisfied |
| **4** | Very Low | Fit & finish/squeak & rattle item does not conform. Defect noticed by most customers |
| **3** | Minor | Fit & finish/squeak & rattle item does not conform. Defect noticed by average customers |
| **2** | Very Minor | Fit & finish/squeak & rattle item does not conform. Defect noticed by discriminating customers |
| **1** | None | No discernible effect |

### PFMEA Severity (Effect on Product/Operation)

| Rating | Effect | Criteria - Product | Criteria - Operation |
|--------|--------|-------------------|----------------------|
| **10** | Hazardous w/o warning | May endanger operator without warning | May endanger operator without warning |
| **9** | Hazardous with warning | May endanger operator with warning | May endanger operator with warning |
| **8** | Very High | 100% of product scrapped; or repair > 1 hour | Major disruption to production line |
| **7** | High | Product sorted and portion scrapped; or repair 0.5-1 hour | Minor disruption to production line |
| **6** | Moderate | Product reworked off-line and accepted | 100% of production run may have to be reworked off-line |
| **5** | Low | Product reworked at station before processed | A portion of production run reworked at station |
| **4** | Very Low | Product sorted with portion reworked | Product sorted with no scrap |
| **3** | Minor | Product reworked at station without delay | Minor disruption to production, operator inconvenience |
| **2** | Very Minor | Slight inconvenience to operation | Slight inconvenience to operation |
| **1** | None | No discernible effect | No discernible effect |

---

## Occurrence Rating Tables

### DFMEA Occurrence (Likelihood of Cause)

| Rating | Probability | Criteria | Approximate Rate |
|--------|-------------|----------|------------------|
| **10** | Very High | Failure is almost inevitable | ≥1 in 10 |
| **9** | Very High | Failure is very likely | 1 in 20 |
| **8** | High | Repeated failures | 1 in 50 |
| **7** | High | Failures are frequent | 1 in 100 |
| **6** | Moderately High | Occasional failures | 1 in 500 |
| **5** | Moderate | Infrequent failures | 1 in 2,000 |
| **4** | Moderately Low | Relatively few failures | 1 in 10,000 |
| **3** | Low | Isolated failures | 1 in 100,000 |
| **2** | Very Low | Failures are rare | 1 in 1,000,000 |
| **1** | Remote | Failure is unlikely | ≤1 in 1,000,000 |

### PFMEA Occurrence (Prevention Control Effectiveness)

| Rating | Probability | Prevention Control | Approximate Rate |
|--------|-------------|-------------------|------------------|
| **10** | Very High | No prevention control | ≥100 per 1,000 (10%) |
| **9** | High | Prevention control has little effect | 50 per 1,000 |
| **8** | High | Prevention control has limited effect | 20 per 1,000 |
| **7** | Moderately High | Prevention control has some effect | 10 per 1,000 |
| **6** | Moderate | Prevention control is moderately effective | 5 per 1,000 |
| **5** | Moderate | Prevention control is effective | 2 per 1,000 |
| **4** | Moderately Low | Prevention control is highly effective | 1 per 1,000 |
| **3** | Low | Prevention control is very highly effective | 0.5 per 1,000 |
| **2** | Very Low | Prevention control is almost certain to prevent | 0.1 per 1,000 |
| **1** | Remote | Prevention control is certain to prevent | ≤0.01 per 1,000 |

---

## Detection Rating Tables

### DFMEA Detection (Design Control Capability)

| Rating | Detection Likelihood | Criteria |
|--------|---------------------|----------|
| **10** | Almost Impossible | No design control; cannot detect or not analyzed |
| **9** | Very Remote | Very remote chance design control will detect |
| **8** | Remote | Remote chance design control will detect |
| **7** | Very Low | Very low chance design control will detect |
| **6** | Low | Low chance design control will detect |
| **5** | Moderate | Moderate chance design control will detect |
| **4** | Moderately High | Moderately high chance design control will detect |
| **3** | High | High chance design control will detect |
| **2** | Very High | Very high chance design control will detect |
| **1** | Almost Certain | Design control will almost certainly detect |

### PFMEA Detection (Process Control Capability)

| Rating | Detection Likelihood | Detection Method |
|--------|---------------------|------------------|
| **10** | Almost Impossible | No detection method available |
| **9** | Very Remote | Not likely to detect at any stage |
| **8** | Remote | Post-processing; problem detection by operator through visual/tactile/audible means |
| **7** | Very Low | Post-processing; problem detection by operator through use of variable or attribute gauging |
| **6** | Low | Post-processing; problem detection by automated controls (light, part presence, etc.) |
| **5** | Moderate | In-station; detection by operator through variable gauging after parts leave station |
| **4** | Moderately High | In-station; detection by automated controls (light, part presence) after parts leave station |
| **3** | High | In-station; detection by automated controls that will prevent further processing |
| **2** | Very High | Detection by automated controls that will detect discrepant part and lock out part |
| **1** | Almost Certain | Detection not applicable; error-proofing (poka-yoke) prevents cause |

---

## Action Priority (AP) Tables

### AIAG-VDA Action Priority Matrix

The AP replaces traditional RPN (S×O×D) and prioritizes Severity first, then Occurrence, then Detection.

**Key**: 
- **H** = High (Must take action)
- **M** = Medium (Should take action or justify)
- **L** = Low (Could take action)

### DFMEA Action Priority Table

| S | O | D=1-2 | D=3-4 | D=5-6 | D=7-8 | D=9-10 |
|---|---|-------|-------|-------|-------|--------|
| **9-10** | 9-10 | H | H | H | H | H |
| **9-10** | 7-8 | H | H | H | H | H |
| **9-10** | 5-6 | H | H | H | H | H |
| **9-10** | 3-4 | H | H | H | H | H |
| **9-10** | 1-2 | M | M | H | H | H |
| **7-8** | 9-10 | H | H | H | H | H |
| **7-8** | 7-8 | M | H | H | H | H |
| **7-8** | 5-6 | M | M | H | H | H |
| **7-8** | 3-4 | L | M | M | H | H |
| **7-8** | 1-2 | L | L | M | M | H |
| **5-6** | 9-10 | M | H | H | H | H |
| **5-6** | 7-8 | M | M | H | H | H |
| **5-6** | 5-6 | L | M | M | H | H |
| **5-6** | 3-4 | L | L | M | M | H |
| **5-6** | 1-2 | L | L | L | M | M |
| **3-4** | 9-10 | M | M | H | H | H |
| **3-4** | 7-8 | L | M | M | H | H |
| **3-4** | 5-6 | L | L | M | M | H |
| **3-4** | 3-4 | L | L | L | M | M |
| **3-4** | 1-2 | L | L | L | L | M |
| **1-2** | Any | L | L | L | L | L |

### PFMEA Action Priority Table

| S | O | D=1-2 | D=3-4 | D=5-6 | D=7-8 | D=9-10 |
|---|---|-------|-------|-------|-------|--------|
| **9-10** | 9-10 | H | H | H | H | H |
| **9-10** | 7-8 | H | H | H | H | H |
| **9-10** | 5-6 | H | H | H | H | H |
| **9-10** | 3-4 | M | H | H | H | H |
| **9-10** | 1-2 | L | M | H | H | H |
| **7-8** | 9-10 | H | H | H | H | H |
| **7-8** | 7-8 | M | H | H | H | H |
| **7-8** | 5-6 | M | M | H | H | H |
| **7-8** | 3-4 | L | M | M | H | H |
| **7-8** | 1-2 | L | L | M | M | H |
| **5-6** | 9-10 | M | H | H | H | H |
| **5-6** | 7-8 | M | M | H | H | H |
| **5-6** | 5-6 | L | M | M | H | H |
| **5-6** | 3-4 | L | L | M | M | H |
| **5-6** | 1-2 | L | L | L | M | M |
| **3-4** | 9-10 | M | M | H | H | H |
| **3-4** | 7-8 | L | M | M | H | H |
| **3-4** | 5-6 | L | L | M | M | H |
| **3-4** | 3-4 | L | L | L | M | M |
| **3-4** | 1-2 | L | L | L | L | M |
| **1-2** | Any | L | L | L | L | L |

---

## Action Priority Guidelines

### High (H) Priority
- **MUST** identify appropriate action to improve Prevention Controls, Detection Controls, or both
- **MUST** document actions taken
- Cannot close item without action unless design change makes it N/A

### Medium (M) Priority
- **SHOULD** identify appropriate action to improve Prevention Controls, Detection Controls, or both
- **MAY** justify why current controls are adequate with documented rationale
- Management review recommended before closing without action

### Low (L) Priority
- **COULD** identify action to improve Prevention or Detection Controls
- Action is optional based on cost/benefit analysis
- No documentation required for no action

---

## Traditional RPN Reference

While AP is recommended, some organizations still use RPN for supplementary analysis:

```
RPN = Severity (S) × Occurrence (O) × Detection (D)
```

| RPN Range | Traditional Interpretation |
|-----------|---------------------------|
| 1-50 | Low risk, action usually not required |
| 51-100 | Moderate risk, consider action |
| 101-200 | High risk, action recommended |
| 201-1000 | Critical risk, action required |

**Warning**: RPN can be misleading because it treats S, O, and D equally. A high-severity, low-occurrence, low-detection item may have same RPN as low-severity, high-occurrence, high-detection item. AP addresses this by prioritizing severity.

---

## Rating Assignment Best Practices

1. **Severity**: Always rate based on worst-case effect. Cannot be reduced by improving controls—only by design change.

2. **Occurrence**: Use historical data when available. Rate the cause, not the failure mode itself.

3. **Detection**: Rate based on current controls' ability to detect BEFORE customer is affected.

4. **Consistency**: Similar failure modes across an FMEA should have similar ratings.

5. **Documentation**: Record rationale for ratings, especially for values ≤3 or ≥8.

6. **Cross-check**: If Detection is rated low (1-3), verify a control actually exists and is effective.
