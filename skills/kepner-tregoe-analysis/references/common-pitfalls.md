# Common Kepner-Tregoe Pitfalls

## Situation Appraisal Pitfalls

### 1. Skipping Situation Appraisal
**Symptom**: Jumping directly to Problem Analysis or Decision Analysis without clarifying the situation.

**Problem**: May be solving the wrong problem, missing related issues, or conflating multiple concerns.

**Remediation**: Always start with SA when facing complexity or ambiguity. List all concerns before prioritizing and routing to appropriate KT process.

---

### 2. Poor Prioritization
**Symptom**: All concerns rated as "High" urgency, or prioritization based on who's complaining loudest.

**Problem**: No clear direction on where to focus limited resources.

**Remediation**: 
- Use SUI framework rigorously: Seriousness (impact if unresolved), Urgency (time sensitivity), Impact/Trend (getting worse?)
- Force-rank if necessary: "If you can only address ONE, which?"
- Document rationale for each rating

---

### 3. Conflating Problems with Decisions
**Symptom**: Starting Problem Analysis when a choice needs to be made, or starting Decision Analysis when the cause is unknown.

**Problem**: Wrong process for the situation leads to wasted effort or incomplete analysis.

**Remediation**: Ask: "Do I need to find WHY something happened?" (PA) vs. "Do I need to choose WHAT to do?" (DA). Route correctly.

---

## Problem Analysis Pitfalls

### 4. Vague Problem Statements
**Symptom**: "The system isn't working right" or "Quality is bad" or "There are problems with the process."

**Problem**: Cannot build precise IS/IS NOT specification from vague deviation statement.

**Remediation**: 
- Specify the OBJECT: What exactly has the problem? (Model, serial number, type, version)
- Specify the DEVIATION: What exactly is wrong? (Observable symptom, measurable deviation)
- Format: "[Specific Object] is experiencing [Specific Deviation]"

---

### 5. Assumed Causes in Problem Statement
**Symptom**: "The bearing failed due to lack of lubrication" or "Operator error caused the defect."

**Problem**: Cause is assumed before analysis; analysis becomes confirmation bias rather than discovery.

**Remediation**: Remove cause from statement. State only the observable deviation: "Bearing Model X-100 is seizing after 5,000 cycles." Let the IS/IS NOT analysis reveal the cause.

---

### 6. Weak IS NOT Specification
**Symptom**: IS NOT column is empty, or contains only "Not affected" or negations of IS.

**Problem**: No basis for generating distinctions; cannot test causes properly.

**Remediation**: 
- IS NOT must contain meaningful comparisons: similar items, locations, times that COULD have the problem but don't
- Ask: "What similar [object/location/time/quantity] would you EXPECT to have this problem but doesn't?"
- The power of IS NOT is finding what's DIFFERENT about the IS cases

---

### 7. Jumping to Causes Before Completing Specification
**Symptom**: After one or two IS/IS NOT pairs, team starts discussing causes.

**Problem**: Incomplete specification means causes cannot be properly tested; may pursue wrong cause.

**Remediation**: 
- Complete ALL four dimensions (WHAT, WHERE, WHEN, EXTENT) before generating causes
- Use the Quality Checklist
- Discipline: "We're still gathering specification data. Cause discussion comes later."

---

### 8. Generating Causes Not from Distinctions
**Symptom**: Possible causes brainstormed without reference to the distinctions; cause list looks like generic troubleshooting.

**Problem**: Causes are untethered from the specific data; low probability of finding true cause.

**Remediation**: 
- For EACH distinction, ask: "What change related to this distinction could have caused the deviation?"
- Causes must be traceable to specific distinctions
- If a cause doesn't connect to a distinction, question its relevance

---

### 9. Failing to Test Causes Against Full Specification
**Symptom**: A cause is accepted because it "makes sense" or explains some facts, without systematic testing.

**Problem**: Cause may explain the IS but not the IS NOT; pursuing wrong cause.

**Remediation**: 
- Test every possible cause against EVERY specification row
- A valid cause must explain BOTH what IS affected AND what IS NOT affected
- The cause with the best fit (fewest unexplained specifications) is most probable

---

### 10. Accepting Unverified Causes
**Symptom**: Analysis concludes with "most probable cause" but no verification plan or action.

**Problem**: Most probable is not proven; corrective action may be wasted.

**Remediation**: 
- Always verify before implementing corrections
- Ask: "How can we prove this IS the cause?"
- Methods: Introduce/remove cause, examine physical evidence, trace timeline, replicate problem

---

## Decision Analysis Pitfalls

### 11. No Clear Decision Statement
**Symptom**: "We need to decide what to do about the budget" or team jumps to comparing vendors without stating the objective.

**Problem**: Without clear outcome, criteria will be unfocused and evaluation will be subjective.

**Remediation**: 
- State: "Select [what] to achieve [outcome]"
- Example: "Select a project management tool to improve team collaboration and visibility"

---

### 12. Disguised WANTS as MUSTS
**Symptom**: MUSTS list includes "Must be user-friendly" or "Must have excellent support" (subjective, not pass/fail).

**Problem**: Forces alternatives out inappropriately; loses ability to trade off preferences.

**Remediation**: 
- MUSTS must be: Mandatory, Measurable, Verifiable, Pass/Fail
- If it's not truly non-negotiable, it's a WANT
- Test: "Would we really reject an option that scores 8/10 on this?"

---

### 13. Setting MUSTS to Predetermine Outcome
**Symptom**: MUSTS are set so specifically that only one option passes (e.g., "Must be Vendor X certified").

**Problem**: Decision is predetermined; analysis is theater.

**Remediation**: 
- Have diverse team set criteria BEFORE reviewing options
- Question each MUST: "Why is this truly mandatory?"
- Ensure at least 2-3 alternatives can pass MUST screening

---

### 14. Inconsistent Scoring
**Symptom**: Same performance is scored 6 for one alternative and 8 for another; or scores vary based on presentation order.

**Problem**: Invalid comparison; conclusions unsupported.

**Remediation**: 
- Define scoring anchors for each WANT before evaluating
- Use consistent data sources for all alternatives
- Score all alternatives on one WANT before moving to next WANT

---

### 15. Manipulating Weights After Scoring
**Symptom**: After seeing results, weights are adjusted to change the outcome.

**Problem**: Post-hoc rationalization; decision is not based on stated criteria.

**Remediation**: 
- Lock weights BEFORE scoring alternatives
- If outcome doesn't match intuition, question whether criteria are complete—don't manipulate weights
- Document weight rationale upfront

---

### 16. Ignoring Adverse Consequences
**Symptom**: Alternative with highest weighted score is selected without considering risks.

**Problem**: High-risk option may fail catastrophically; better to choose lower-scoring option with lower risk.

**Remediation**: 
- Always complete risk assessment for top 2-3 alternatives
- Consider: "What could go wrong? How likely? How serious?"
- Balance score against risk profile

---

## Potential Problem Analysis Pitfalls

### 17. Doing PPA Too Early
**Symptom**: Planning contingencies before the decision is made or the plan is defined.

**Problem**: Wasted effort on plans that may not be executed.

**Remediation**: 
- Complete DA first to select the approach
- Define the plan/implementation steps
- THEN do PPA on the selected plan

---

### 18. Missing Critical Steps
**Symptom**: PPA focuses only on obvious risks; misses failure modes in key plan steps.

**Problem**: Unidentified risks can derail implementation.

**Remediation**: 
- List ALL critical steps in the plan
- For EACH step, ask: "What could go wrong here?"
- Also consider: Dependencies, resources, handoffs, timing

---

### 19. No Preventive Actions
**Symptom**: Risks are identified but no actions to reduce likelihood.

**Problem**: Reactive rather than proactive; risks remain unmitigated.

**Remediation**: 
- For each HIGH and MEDIUM risk: "What can we do to PREVENT this?"
- Assign responsibility and deadline for preventive actions
- Some risks can be eliminated or significantly reduced

---

### 20. Contingency Without Trigger
**Symptom**: "If X happens, we'll do Y" but no clear indicator of when to activate.

**Problem**: Contingency may be activated too late or not at all.

**Remediation**: 
- Define specific trigger: "Activate contingency when [measurable condition]"
- Assign responsibility for monitoring the trigger
- Ensure trigger is detectable before it's too late

---

## General Pitfalls

### 21. KT as Documentation Exercise
**Symptom**: Forms filled out after the fact; conclusions predetermined.

**Problem**: Loses the analytical value of the methodology; becomes bureaucratic overhead.

**Remediation**: 
- Do the thinking work as you fill in the framework
- Use KT to DISCOVER, not to document pre-existing conclusions
- If outcome is obvious, you may not need formal KT analysis

---

### 22. Working Solo
**Symptom**: One person completes the entire analysis without input from others.

**Problem**: Missing knowledge and perspectives; bias undetected.

**Remediation**: 
- Include people with direct knowledge of the problem/process
- Include diverse perspectives for DA criteria setting
- Challenge each other's assumptions

---

### 23. Rushing the Process
**Symptom**: Incomplete specifications, missing criteria, superficial cause testing—all in the name of speed.

**Problem**: Reaches conclusions quickly but conclusions are unreliable.

**Remediation**: 
- KT requires discipline and thoroughness
- Time invested upfront saves time from pursuing wrong causes/decisions
- If truly time-constrained, document assumptions explicitly

---

### 24. Not Integrating with Other Tools
**Symptom**: Using KT in isolation; not connecting to related analyses.

**Problem**: Misses benefits of tool synergy; may duplicate effort.

**Remediation**: 
- Use Problem Definition (5W2H) to gather initial facts for PA
- Use Fishbone to brainstorm causes, then test with KT specification
- Use 5 Whys to drill deeper after KT PA identifies most probable cause
- Feed DA decisions into FMEA/FTA for implementation risk analysis
