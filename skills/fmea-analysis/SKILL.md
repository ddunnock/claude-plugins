---
name: fmea-analysis
description: Conduct Failure Mode and Effects Analysis (FMEA) for systematic identification and risk assessment of potential failures in designs, processes, or systems. Supports DFMEA (Design), PFMEA (Process), and FMEA-MSR (Monitoring & System Response). Uses AIAG-VDA 7-step methodology with Action Priority (AP) risk assessment replacing traditional RPN. Use when analyzing product designs for potential failures, evaluating manufacturing process risks, conducting proactive risk assessment, preparing for APQP/PPAP submissions, investigating field failures, or when user mentions "FMEA", "failure mode", "DFMEA", "PFMEA", "severity occurrence detection", "RPN", "Action Priority", "design risk analysis", or needs to identify and prioritize potential failure modes with their causes and effects.
---

# Failure Mode and Effects Analysis (FMEA)

Conduct comprehensive FMEA using the AIAG-VDA 7-step methodology with structured Q&A guidance, quality scoring, and professional report generation.

## Overview

FMEA is a systematic, proactive method for evaluating a process, design, or system to identify where and how it might fail, and to assess the relative impact of different failures. It prioritizes actions based on risk severity, not just likelihood.

**Key Principle**: FMEA is a "living document" that evolves with the design/process and should be updated whenever changes occur.

## FMEA Types

| Type | Focus | Primary Application |
|------|-------|---------------------|
| **DFMEA** | Design/Product | Product development, component design |
| **PFMEA** | Process/Manufacturing | Production, assembly, service delivery |
| **FMEA-MSR** | Monitoring & System Response | Diagnostic coverage, fault handling |

## Workflow: AIAG-VDA 7-Step Approach

### Step 1: Planning & Preparation (5T's)

**Collect from user:**

1. **InTent**: What is the purpose of this FMEA? What problem are we trying to prevent?
2. **Timing**: When is the FMEA needed? What milestones must it support?
3. **Team**: Who should participate? (Cross-functional: design, manufacturing, quality, service)
4. **Tasks**: What specific deliverables are required?
5. **Tools**: What resources, data, and prior FMEAs are available?

**Additional Planning Questions:**
- Is this DFMEA, PFMEA, or FMEA-MSR?
- What are the analysis boundaries? (Include/exclude scope)
- What customer requirements and specifications apply?
- What lessons learned from prior similar products/processes exist?

**Quality Gate**: Clear scope definition with documented boundaries, team assignments, and timeline.

### Step 2: Structure Analysis

**For DFMEA - Collect:**
1. What is the system/subsystem/component hierarchy?
2. What are the physical interfaces between components?
3. What energy, material, and data exchanges occur?
4. What are critical clearances and tolerances?

**For PFMEA - Collect:**
1. What is the process flow? (List all process steps in sequence)
2. What are the sub-steps within each major step?
3. What are the work elements (4M: Man, Machine, Material, Method)?
4. What equipment and tooling is used at each step?

**Output**: Structure tree or block diagram showing:
- Focus Element (item/step being analyzed)
- Next Higher Level (system/process it belongs to)
- Next Lower Level (sub-components/sub-steps)

### Step 3: Function Analysis

**Collect for each element:**
1. What is the intended function? (Use verb + noun format)
2. What are the performance requirements/specifications?
3. What characteristics must be achieved? (CTQ/CTQ)
4. How does this function relate to customer requirements?

**DFMEA Function Format**: "Function of [component] is to [verb] [noun] per [specification]"
**PFMEA Function Format**: "Function of [process step] is to [verb] [product characteristic] per [specification]"

**Quality Gate**: Every element has clearly defined, measurable functions linked to requirements.

### Step 4: Failure Analysis (Failure Chain)

For each function, establish the **Failure Chain**:

**4a. Failure Mode** - How can the function fail?
- Loss of function (complete failure)
- Degradation of function (partial failure)
- Intermittent function (inconsistent)
- Unintended function (wrong operation)
- Delayed function (timing failure)

**4b. Failure Effects** - What are the consequences?
- Effects on Next Higher Level element
- Effects on end customer/user
- Effects on plant operations (PFMEA)
- Safety and regulatory impacts

**4c. Failure Causes** - Why would the failure occur?
- Design deficiencies (DFMEA)
- Process variations (PFMEA)
- Material issues
- Environmental factors
- Human factors

**Documentation Format**:
```
Effect (Next Higher Level) ← Failure Mode (Focus Element) ← Cause (Next Lower Level)
```

### Step 5: Risk Analysis

**5a. Current Controls**

Identify existing controls for each cause:
- **Prevention Controls**: Actions that prevent the cause or reduce occurrence
- **Detection Controls**: Actions that detect the cause or failure mode

**5b. Rating Assignment**

Assign ratings using the standard 1-10 scales (see [references/rating-tables.md](references/rating-tables.md)):

| Rating | Scale | Direction |
|--------|-------|-----------|
| **Severity (S)** | 1-10 | Higher = More severe effect |
| **Occurrence (O)** | 1-10 | Higher = More frequent |
| **Detection (D)** | 1-10 | Higher = Less likely to detect |

**5c. Action Priority (AP) Determination**

Use the AP tables (replacing traditional RPN) to assign priority:

| Priority | Meaning | Action Required |
|----------|---------|-----------------|
| **H (High)** | Highest priority | Must identify action to improve controls |
| **M (Medium)** | Medium priority | Should identify action or justify current controls |
| **L (Low)** | Low priority | Could improve controls at discretion |

**Note**: AP prioritizes Severity first, then Occurrence, then Detection. Unlike RPN (S×O×D), AP ensures safety-critical issues (high S) are never ignored regardless of O and D.

### Step 6: Optimization

**For High and Medium AP items:**

1. **Identify Actions**: What specific actions will reduce risk?
   - Design changes (DFMEA)
   - Process changes (PFMEA)
   - Additional controls (prevention or detection)

2. **Assign Responsibility**: Who owns each action? Target completion date?

3. **Implement and Verify**: Document actions taken

4. **Re-evaluate**: Assign new S, O, D ratings after implementation
   - Severity can only change if design is modified
   - Occurrence changes with prevention controls
   - Detection changes with detection controls

**Action Types**:
- **Preventive Actions**: Reduce occurrence of cause
- **Detection Actions**: Improve detection capability

### Step 7: Results Documentation

Generate final FMEA documentation including:
- Complete FMEA worksheet with all failure chains
- Risk summary with AP distribution
- Action tracking with status
- Lessons learned and knowledge capture

**Run**: `python scripts/generate_report.py` to create professional HTML/PDF output.

## Quality Scoring

Each analysis is scored on six dimensions (see [references/quality-rubric.md](references/quality-rubric.md)):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Structure Analysis | 15% | Completeness of system/process breakdown |
| Function Definition | 15% | Clarity, measurability of functions |
| Failure Chain Logic | 20% | Correct Mode→Effect→Cause relationships |
| Control Identification | 15% | Completeness of prevention/detection controls |
| Rating Consistency | 20% | Appropriate, justified S/O/D ratings |
| Action Effectiveness | 15% | Specific, assigned, measurable actions |

**Scoring Scale**: Each dimension rated 1-5 (Inadequate to Excellent)
- **Overall Score**: Weighted average × 20 = 0-100 points
- **Passing Threshold**: 70 points minimum

Run `python scripts/score_analysis.py` with FMEA data to calculate scores.

## Common Pitfalls

See [references/common-pitfalls.md](references/common-pitfalls.md) for:
- Confusing failure modes with causes or effects
- Inconsistent rating scale application
- Using only RPN and ignoring high-severity items
- Incomplete function analysis
- Missing prevention vs. detection control distinction
- Treating FMEA as a "check-the-box" exercise

## Examples

See [references/examples.md](references/examples.md) for worked examples:
- DFMEA: Electronic control unit design
- PFMEA: Welding process analysis
- FMEA-MSR: Monitoring system response
- Anti-example showing common mistakes

## Integration with Other Tools

- **FTA (Fault Tree Analysis)**: Use FTA for top-down analysis; FMEA for bottom-up. FMEA failure modes feed FTA basic events.
- **5 Whys**: Use to drill deeper into FMEA causes
- **Control Plan**: FMEA outputs feed directly into Control Plans
- **APQP**: FMEA is a core deliverable in phases 2-4
- **DVP&R**: Design Verification integrates with DFMEA

## Rating Tables Quick Reference

See [references/rating-tables.md](references/rating-tables.md) for complete tables including:
- Severity rating criteria (DFMEA and PFMEA)
- Occurrence rating criteria
- Detection rating criteria
- Action Priority (AP) lookup tables

## Calculation Support

- **RPN Calculation**: `python scripts/calculate_fmea.py --mode rpn`
- **AP Determination**: `python scripts/calculate_fmea.py --mode ap`
- **Risk Summary**: `python scripts/calculate_fmea.py --mode summary`

## Session Conduct Guidelines

1. **Cross-functional participation**: Include design, manufacturing, quality, and service perspectives
2. **Function-first thinking**: Start with what the element must do, then explore failures
3. **Evidence-based ratings**: Use data, not opinions, for occurrence ratings
4. **Severity drives priority**: High severity (9-10) always requires action regardless of AP
5. **Document assumptions**: Record basis for all ratings
6. **Living document**: Update FMEA with design/process changes
