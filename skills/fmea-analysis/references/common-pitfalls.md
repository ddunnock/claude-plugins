# FMEA Common Pitfalls

## Overview

This guide identifies the most common mistakes made during FMEA development and provides remediation strategies. Understanding these pitfalls helps teams produce more effective analyses.

---

## Pitfall 1: Confusing Failure Modes, Effects, and Causes

### Description
The most fundamental FMEA error: mixing up what belongs in each column of the failure chain.

### Symptoms
- Failure modes describe WHY something fails (that's a cause)
- Effects describe what fails (that's a failure mode)
- Causes describe consequences (that's an effect)
- Same information repeated across columns

### Examples

**Wrong:**
| Failure Mode | Effect | Cause |
|--------------|--------|-------|
| Material fatigue | Shaft breaks | Customer injury |

**Correct:**
| Failure Mode | Effect | Cause |
|--------------|--------|-------|
| Shaft fractures | Loss of torque transmission; vehicle immobilized; potential injury if loss of control | Material fatigue due to cyclic loading exceeding design limit |

### Remediation
- **Failure Mode**: HOW the function fails (loss, degradation, intermittent, unintended)
- **Effect**: WHAT HAPPENS as a result (impact on next higher level, customer, safety)
- **Cause**: WHY it fails (root cause at next lower level)

**Test**: Read the chain as "Because of [Cause], the [Focus Element] experiences [Failure Mode], which results in [Effect]"

---

## Pitfall 2: Starting with Failure Modes Instead of Functions

### Description
Teams jump directly to listing failure modes without first defining what the item/process is supposed to do.

### Symptoms
- No function statements documented
- Failure modes don't clearly relate to function loss
- Random failure modes with no logical structure
- Missed failure modes because functions weren't systematically analyzed

### Example

**Wrong**: "Let's list everything that could go wrong with this connector"

**Correct**: "The connector's function is to maintain electrical continuity between harness and ECU under vibration, temperature cycling, and moisture exposure. How could this function fail?"

### Remediation
1. Complete Function Analysis (Step 3) before Failure Analysis (Step 4)
2. Use verb + noun format: "Function is to [verb] [noun] per [specification]"
3. For each function, systematically consider: No function, Degraded function, Intermittent function, Unintended function

---

## Pitfall 3: Generic or Vague Failure Mode Descriptions

### Description
Failure modes are described so vaguely they provide no insight for risk assessment or action planning.

### Symptoms
- "Part fails"
- "Doesn't work"
- "Bad quality"
- "Process error"

### Examples

**Wrong:**
| Function | Failure Mode |
|----------|--------------|
| Seal prevents leakage | Seal fails |

**Correct:**
| Function | Failure Mode |
|----------|--------------|
| Seal prevents fluid leakage at interface | Seal allows fluid leakage past lip |
| Seal prevents fluid leakage at interface | Seal dislodged from groove |
| Seal prevents fluid leakage at interface | Seal degraded/cracked |

### Remediation
- Be specific about HOW the failure manifests
- Use physics-of-failure thinking: crack, fracture, wear, corrosion, deformation, etc.
- Consider different failure mechanisms separately
- Ask: "If this function failed, what would we physically observe?"

---

## Pitfall 4: Inconsistent Rating Scale Application

### Description
Different team members apply different standards when rating Severity, Occurrence, or Detection, leading to inconsistent prioritization.

### Symptoms
- Similar items receive wildly different ratings
- Ratings change based on who is facilitating
- No documented rationale for ratings
- Arguments about what ratings "should" be without criteria

### Examples

**Inconsistent:**
- Shaft fracture rated S=6 in one row, similar fracture rated S=9 in another
- "Visual inspection" rated D=3 by one person, D=6 by another

### Remediation
1. Use standardized rating tables with clear criteria
2. Document rationale for each rating, especially extremes (≤3 or ≥8)
3. Review similar failure modes together for consistency
4. Establish team calibration: review example items and agree on ratings before starting
5. Periodic consistency audits during FMEA development

---

## Pitfall 5: Ignoring High-Severity Items with Low RPN

### Description
Using only RPN (S×O×D) for prioritization allows high-severity, low-occurrence, low-detection items to be deprioritized.

### Symptoms
- Safety-related items (S=9 or 10) have no actions because RPN is "acceptable"
- Team focuses on high-RPN items while ignoring low-probability catastrophic failures
- Regulatory non-compliance risks overlooked

### Example

| S | O | D | RPN | Interpretation |
|---|---|---|-----|----------------|
| 10 | 1 | 2 | 20 | Safety-critical but low RPN |
| 5 | 6 | 6 | 180 | Moderate annoyance but high RPN |

Traditional RPN would prioritize the second item, but the first is a safety risk that demands attention.

### Remediation
1. Use Action Priority (AP) instead of or in addition to RPN
2. **Rule**: Any Severity ≥9 requires review and action regardless of RPN or AP
3. Create a "Critical Items" list for all S=9-10 items
4. Never accept "low probability" as justification for ignoring high-severity risks

---

## Pitfall 6: Conflating Prevention and Detection Controls

### Description
Teams list controls without distinguishing whether they prevent the cause from occurring or detect it after it occurs.

### Symptoms
- All controls listed in one column
- Unclear which control affects Occurrence vs. Detection rating
- Actions to "improve controls" without specifying prevention or detection

### Examples

**Wrong:**
| Controls |
|----------|
| Torque monitoring, visual inspection, preventive maintenance |

**Correct:**
| Prevention Controls | Detection Controls |
|--------------------|-------------------|
| Preventive maintenance schedule | Torque monitoring alarm |
| Calibrated tooling | Visual inspection at end of line |

### Remediation
1. Use separate columns for Prevention Controls and Detection Controls
2. **Prevention Controls** reduce Occurrence rating: Design features, error-proofing, process parameters
3. **Detection Controls** reduce Detection rating: Inspections, tests, alarms, monitoring
4. Map each control to specific cause in the failure chain

---

## Pitfall 7: Overly Optimistic Detection Ratings

### Description
Teams assume their detection controls are more effective than they actually are, leading to artificially low Detection ratings.

### Symptoms
- Detection ratings of 1-3 assigned to manual inspections
- "We have a visual inspection" → D=2
- Automated systems assumed perfect (D=1) without validation
- No consideration of detection failure modes

### Common Overoptimistic Patterns
| Claimed Control | Typical Assigned D | Realistic D |
|----------------|-------------------|-------------|
| "Visual inspection" | 2-3 | 6-8 |
| "100% inspection" | 1-2 | 4-6 |
| "Operator checks" | 3-4 | 6-8 |
| "Automated inspection" | 1 | 3-5 |

### Remediation
1. Validate detection capability with data (defect escape rates)
2. Consider: What if the inspector is tired? What if the gauge drifts?
3. For D ≤ 3, require documented evidence of control effectiveness
4. Remember: Detection = ability to detect BEFORE customer is affected
5. Ask: "What is the escape rate of this control?"

---

## Pitfall 8: Treating FMEA as a Documentation Exercise

### Description
FMEA becomes a "check-the-box" activity completed to satisfy requirements rather than a genuine risk reduction tool.

### Symptoms
- FMEA completed after design is frozen
- Copy-paste from previous similar products without review
- No actions taken despite High priority items
- FMEA never updated after initial creation
- Team treats it as paperwork, not problem-solving

### Consequences
- Real risks not identified or addressed
- False confidence in product/process
- FMEA provides no value, just consumes resources
- Field failures that were predictable

### Remediation
1. Start FMEA early in design/process development
2. Schedule regular FMEA reviews tied to design milestones
3. Track action completion rates and effectiveness
4. Update FMEA when design/process changes
5. Use FMEA outputs: feed into Control Plans, DVP&R, work instructions
6. Management review of FMEA quality, not just completion

---

## Pitfall 9: Missing Interfaces and Interactions

### Description
FMEA focuses only on individual components/steps and misses failures arising from interfaces, interactions, or combinations.

### Symptoms
- No analysis of what happens at component boundaries
- System-level effects not traced
- No consideration of how one failure affects adjacent systems
- Missing "cascade" failures

### Example

**Missed**: How does a sensor failure affect the controller that depends on its signal? How does controller response affect the actuator?

### Remediation
1. Include interface analysis in Structure Analysis (Step 2)
2. Explicitly identify: physical interfaces, data exchanges, energy transfers
3. Consider failure propagation: what downstream effects result from upstream failures?
4. For PFMEA: analyze station-to-station handoffs and information transfer
5. Cross-reference with system-level FMEA or FTA for complex systems

---

## Pitfall 10: Single-Cause Thinking

### Description
Team identifies only one cause per failure mode when multiple causes may exist, each requiring different controls.

### Symptoms
- One cause per failure mode
- Important root causes missed
- Controls address one cause but others remain uncontrolled
- Recurrence because alternate causes not addressed

### Example

**Incomplete:**
| Failure Mode | Cause |
|--------------|-------|
| Weld porosity | Contaminated base metal |

**Complete:**
| Failure Mode | Cause |
|--------------|-------|
| Weld porosity | Contaminated base metal |
| Weld porosity | Improper shielding gas flow |
| Weld porosity | Excessive travel speed |
| Weld porosity | Wrong filler material |

### Remediation
1. Brainstorm multiple causes using Fishbone diagram
2. Use "AND/OR" thinking: which causes can independently produce this failure?
3. Review historical data for actual cause distribution
4. Consider 6M categories: Man, Machine, Material, Method, Measurement, Mother Nature

---

## Pitfall 11: Actions Without Specificity

### Description
Recommended actions are vague and cannot be implemented or verified.

### Symptoms
- "Improve design"
- "Add inspection"
- "Train operators"
- "Review process"
- No owner or target date

### Examples

**Vague:**
| Action | Owner | Date |
|--------|-------|------|
| Improve inspection | Quality | TBD |

**Specific:**
| Action | Owner | Date |
|--------|-------|------|
| Implement automated vision system for weld bead inspection with go/no-go criteria documented in WI-4523 | J. Smith | 2024-03-15 |

### Remediation
- Actions must be SMART: Specific, Measurable, Assignable, Relevant, Time-bound
- Include: What will be done, who will do it, when complete, how verified
- Distinguish prevention actions from detection actions
- Follow up: verify action taken, re-rate S/O/D

---

## Pitfall 12: Not Re-evaluating After Actions

### Description
Actions are implemented but the FMEA is not updated with revised ratings.

### Symptoms
- Original ratings remain unchanged after significant improvements
- No "after" column for S, O, D
- Cannot demonstrate risk reduction from FMEA activities
- Actions documented but effectiveness unknown

### Remediation
1. Include "Original" and "Revised" rating columns
2. After action implementation, re-rate O and D (S rarely changes)
3. Document evidence supporting improved ratings
4. Track AP/RPN reduction as metric of FMEA effectiveness
5. Only close action items after re-evaluation confirms improvement

---

## Summary: FMEA Health Check Questions

Use these questions to assess your FMEA quality:

1. ☐ Does every failure mode relate to loss/degradation of a defined function?
2. ☐ Are Modes, Effects, and Causes clearly distinct and in correct columns?
3. ☐ Are Prevention and Detection Controls separately identified?
4. ☐ Are ratings consistent across similar items?
5. ☐ Do all High AP items have specific, assigned actions?
6. ☐ Have Severity ≥9 items been reviewed regardless of AP?
7. ☐ Have actions been verified and ratings re-evaluated?
8. ☐ Is the FMEA being used (Control Plans, DVP&R) or just filed?
