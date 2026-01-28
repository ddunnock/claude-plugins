# IS/IS NOT Specification Matrix Guide

The IS/IS NOT specification is the cornerstone of Kepner-Tregoe Problem Analysis. It creates a precise boundary around the problem, distinguishing what IS affected from what IS NOT (but could be).

## Purpose

The IS/IS NOT matrix serves three critical functions:
1. **Bounds the problem** - Defines exactly where the problem exists and doesn't exist
2. **Generates distinctions** - Highlights what's different about affected vs. unaffected cases
3. **Tests possible causes** - A valid cause must explain BOTH the IS and IS NOT data

## The Four Dimensions

### WHAT (Object and Defect)

**IS Questions:**
- What object(s) has the problem?
- What specific defect or deviation do you observe?
- What type/model/version is affected?
- What symptom(s) are present?
- What exactly do you see, hear, feel, smell, taste?

**IS NOT Questions:**
- What similar objects could have the problem but don't?
- What defects could be present but aren't?
- What types/models/versions are not affected?
- What symptoms might you expect that are absent?

**Example:**
| IS | IS NOT | Distinction |
|----|--------|-------------|
| Model A pumps (2022 manufacture) | Model A pumps (2021 manufacture) | Manufacturing year - 2022 vs 2021 |
| Bearing seizure | Motor burnout, shaft misalignment | Only bearing affected, not other components |
| High-pitched squeal before failure | Grinding noise, vibration | Acoustic signature unique |

### WHERE (Location)

**IS Questions:**
- Where geographically is the problem observed?
- Where on/in the object does it occur?
- Where in the process does it occur?
- Where in the system/network does it manifest?
- What position, orientation, or environment?

**IS NOT Questions:**
- Where could it occur but doesn't?
- Where on the object is it not present?
- What process steps are unaffected?
- What system areas are working normally?
- What environments don't show the problem?

**Example:**
| IS | IS NOT | Distinction |
|----|--------|-------------|
| Plant A, Building 2 | Plant A, Building 1; Plant B | Building 2 is the newer wing (built 2023) |
| Right-side bearing only | Left-side bearing | Right side faces the wall, less airflow |
| Final assembly station | Machining, welding, prep stations | Assembly uses high-torque tools |

### WHEN (Timing)

**IS Questions:**
- When was it first observed?
- When does it occur (time of day, day of week, season)?
- When in the product lifecycle (new, after X cycles, age-related)?
- When in the process sequence?
- What's the pattern (constant, intermittent, cyclical)?
- When did something change before the problem started?

**IS NOT Questions:**
- When could it occur but doesn't?
- What times/shifts/seasons are unaffected?
- What lifecycle stages don't show the problem?
- When in the process is it not present?
- What periods are free of the issue?

**Example:**
| IS | IS NOT | Distinction |
|----|--------|-------------|
| First observed March 15, 2024 | Before March 15, 2024 | New lubricant supplier contract started March 1 |
| Day shift only | Night shift, weekends | Day shift has higher production volume |
| After 5,000-6,000 cycles | Before 5,000 cycles | Coincides with bearing wear-in period |
| Intermittent - 2-3x per week | Not constant | Correlates with high-humidity days |

### EXTENT (Magnitude)

**IS Questions:**
- How many units are affected?
- What percentage of production/population?
- How many defects per unit?
- What's the magnitude (size, severity, intensity)?
- Is it growing, stable, or decreasing?

**IS NOT Questions:**
- How many could be affected but aren't?
- What percentage is unaffected?
- What magnitude could it be but isn't?
- What's the limit or boundary of severity?
- Why isn't it more widespread?

**Example:**
| IS | IS NOT | Distinction |
|----|--------|-------------|
| 23 of 150 pumps (15%) | 127 pumps (85%) | Affected 23 are all from same production batch |
| 1-2 defects per affected unit | 3+ defects | Single-cause pattern, not systemic failure |
| Trending upward (5→8→10 per month) | Stable or decreasing | Recent change is accelerating the problem |
| Moderate severity (repair possible) | Catastrophic (total failure) | Early detection preventing full failure |

## Building Distinctions

Distinctions are the KEY to cause identification. They answer: "What is different, peculiar, changed, or unique about the IS compared to the IS NOT?"

### Good Distinction Characteristics:
- **Specific and observable** - Not vague or assumed
- **Change-oriented** - Often related to something that changed
- **Factual** - Based on data, not speculation
- **Discriminating** - Truly differentiates IS from IS NOT

### Distinction Development Questions:
1. What's different about [IS] compared to [IS NOT]?
2. What changed around the time this started?
3. What's unique or peculiar about the affected cases?
4. What do all IS cases have in common that IS NOT cases don't?
5. What's special about the boundary between IS and IS NOT?

### Common Distinction Categories:
- **Material changes** - New suppliers, formulation, batch
- **Process changes** - Parameters, sequence, methods
- **People changes** - Training, staffing, procedures
- **Equipment changes** - Age, calibration, maintenance
- **Environmental changes** - Temperature, humidity, contamination
- **Design changes** - Revisions, modifications

## From Distinctions to Possible Causes

For each meaningful distinction, generate possible causes:

**Question**: "What change in or related to [distinction] could have caused the [deviation] in the [object]?"

**Example:**
- Distinction: "2022 pumps use a new bearing supplier"
- Possible Cause: "The new bearing supplier changed the tolerance specification"

**Example:**
- Distinction: "Right-side bearing faces the wall with less airflow"
- Possible Cause: "Reduced cooling causes thermal expansion beyond tolerance"

## Cause Testing Against Specification

A true cause must explain EVERY aspect of the specification:

| Test Question | Valid Cause Response |
|---------------|---------------------|
| Does it explain WHAT IS affected? | ✓ Must say yes |
| Does it explain WHAT IS NOT affected? | ✓ Must explain why not |
| Does it explain WHERE IS it observed? | ✓ Must say yes |
| Does it explain WHERE IS NOT observed? | ✓ Must explain why not |
| Does it explain WHEN IS it occurring? | ✓ Must say yes |
| Does it explain WHEN IS NOT occurring? | ✓ Must explain why not |
| Does it explain EXTENT IS? | ✓ Must say yes |
| Does it explain EXTENT IS NOT? | ✓ Must explain why not |

**Scoring:**
- ✓ = Explains this specification (1 point)
- ? = Partially explains or unknown (0.5 points)
- ✗ = Does NOT explain this specification (0 points)

The cause with the highest score and fewest ✗ marks is the most probable cause.

## Quality Checklist for IS/IS NOT Matrix

Before proceeding to cause generation, verify:

- [ ] Each dimension (WHAT, WHERE, WHEN, EXTENT) is completed
- [ ] IS column contains only factual, observed data
- [ ] IS NOT column contains meaningful comparisons (not just negations)
- [ ] Each row has a distinct piece of information (no redundancy)
- [ ] Distinctions are specific and change-oriented
- [ ] IS NOT cases are truly similar enough to expect the problem
- [ ] No assumed causes embedded in the specification
- [ ] Data sources are documented (who provided, how verified)

## Common IS/IS NOT Errors

| Error | Problem | Correction |
|-------|---------|------------|
| Vague IS | "The machine has problems" | "CNC Mill #7 has ±0.005" dimensional variation on X-axis" |
| Trivial IS NOT | "Everything else is fine" | List specific similar items that could be affected but aren't |
| Assumed cause in IS | "Operator error caused scrap" | "Parts from Station 3 have dimensional nonconformance" |
| Missing IS NOT | Only listing what IS affected | Always ask "what could be affected but isn't?" |
| Weak distinctions | "They're just different" | Identify specific, measurable differences |
| Negated IS | IS NOT = "Not affected" | IS NOT should be meaningful alternatives (what COULD be but isn't) |
