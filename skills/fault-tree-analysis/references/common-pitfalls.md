# Common Fault Tree Analysis Pitfalls

## Overview

This document catalogs frequent FTA errors with symptoms, examples, and correction strategies. Use during analysis review to identify and address weaknesses.

---

## Pitfall 1: AND/OR Gate Confusion

**Description**: Selecting wrong gate type reverses the logical relationship between events.

**Symptoms**:
- Cut sets don't match engineering intuition
- Redundancy appears ineffective (should be AND, used OR)
- Single failures dominate when multiple failures expected (should be OR, used AND)
- Probability calculations yield unexpected results

**Example - Incorrect**:
```
Pump System Fails
     |
  [AND gate]
    /    \
Pump A    Pump B
Fails     Fails
```
*Problem*: If pumps are parallel (either provides flow), AND is wrong.

**Example - Correct**:
```
Pump System Fails
     |
   [OR gate]
    /    \
Both      Single Pump
Pumps     Fails While
Fail      Other Running
  |            |
[AND]       [AND]
 /  \        /  \
A    B     Pump  Demand
Fails Fails  X   Exceeds
            Fails Capacity
```

**Remediation**:
- Ask: "Does ANY one cause failure (OR) or do ALL causes need to occur (AND)?"
- For redundant components: Use AND gate for complete failure
- For parallel paths where any works: Failure requires all to fail = AND
- Verify by reading: "Top event occurs if A AND B" vs "A OR B"

---

## Pitfall 2: Top Event Too Vague or Wrong Level

**Description**: Top event is poorly defined, too broad, or at inappropriate system level.

**Symptoms**:
- Tree becomes unwieldy (too high level)
- Tree too simple to be useful (too low level)
- Multiple interpretations of what "failure" means
- Difficulty connecting basic events to top event
- Analysis doesn't answer the actual question

**Example - Poor**:
- "System doesn't work" (what does "work" mean?)
- "Safety compromised" (too abstract)
- "Motor winding burns out" (too detailed for system analysis)

**Example - Good**:
- "Cooling system fails to maintain temperature below 150°F during normal operation"
- "Brake system fails to achieve >0.6g deceleration when commanded"
- "Fire suppression system fails to activate within 30 seconds of detection"

**Remediation**:
- Top event should be at functional level: "System fails to perform X function"
- Include success criteria in definition
- Specify operating mode and conditions
- Should be observable/measurable
- Test: Can you clearly determine if this event occurred?

---

## Pitfall 3: Missing Common Cause Failures (CCF)

**Description**: Treating redundant components as fully independent when common causes could fail multiple components.

**Symptoms**:
- AND gates show extremely low probabilities (e.g., 10^-12)
- Redundancy appears more effective than realistic
- Same component type appears in multiple branches under AND gates
- No consideration of shared environments, maintenance, or design

**Example - Incomplete**:
```
Redundant Sensors Fail
        |
     [AND gate]
      /     \
  Sensor A  Sensor B
  Fails     Fails
```
*Problem*: Sensors may share power supply, calibration procedure, environmental conditions.

**Example - Complete**:
```
Redundant Sensors Fail
         |
      [OR gate]
       /     \
   Both      Common
   Fail      Cause
 Independently  Fails Both
      |           |
   [AND]       [Basic]
    /  \        CCF
  A     B
 Ind.  Ind.
Fails  Fails
```

**Remediation**:
- For every AND gate with redundant components, ask: "What could fail both?"
- Consider: Environmental (temp, EMI, vibration), Maintenance (same procedure/person), Manufacturing (same batch/supplier), Design (same part number, shared software)
- Model CCF explicitly or apply beta-factor model
- Typical beta-factor: 1-10% of independent failure rate

---

## Pitfall 4: Incomplete Branch Development

**Description**: Stopping tree development too early, leaving intermediate events undeveloped.

**Symptoms**:
- Many diamond (undeveloped) events without justification
- Events at different levels of detail across tree
- Cannot assign probabilities to intermediate events
- Cut sets contain intermediate events instead of basic events
- Analysis doesn't reach actionable component level

**Example - Incomplete**:
```
Motor Fails to Start
       |
    [OR gate]
     /     \
 Electrical  Mechanical
  Failure     Failure
  [Diamond]   [Diamond]
```
*Problem*: "Electrical Failure" is not a basic event; can't assign probability or action.

**Example - Complete**:
```
Motor Fails to Start
        |
     [OR gate]
      /      \
Electrical  Mechanical
  Path         Path
    |            |
 [OR gate]    [OR gate]
  /  |  \     /   |   \
Power Wiring Motor Bearing Shaft  Coupling
 Loss Fault  Wind  Seize  Break  Fails
  |    |    Burn    |      |      |
[OR] [Basic] [Basic][Basic][Basic][Basic]
...
```

**Remediation**:
- Develop until reaching basic events (component failures)
- Each undeveloped event (diamond) needs explicit justification
- Stop when: Component level reached, out of scope (document why), no data available
- All branches should reach similar level of detail

---

## Pitfall 5: Ignoring Human Factors

**Description**: Tree contains only hardware/software failures, missing human errors that can cause or contribute to system failure.

**Symptoms**:
- No human actions appear in tree
- Tree addresses "perfect operation" scenario only
- Post-incident analysis reveals human error not captured
- Safety barriers that require human action appear fully effective

**Example - Incomplete**:
```
Tank Overfills
     |
  [OR gate]
   /     \
Level   Control
Sensor   Valve
Fails   Fails
```
*Problem*: Missing operator fails to respond to alarm, maintenance error, etc.

**Example - Complete**:
```
Tank Overfills
       |
    [OR gate]
    /    |    \
Level  Control  Human
Sensor  Valve   Error
Fails   Fails     |
                [OR gate]
               /    |    \
           Operator  Wrong  Procedure
           Ignores   Valve  Not
           Alarm    Set    Followed
```

**Remediation**:
- For every automatic protection, ask: "What if human backup fails?"
- Include: Operator errors, maintenance mistakes, procedure non-compliance, training gaps
- Consider: Alarm overload, time pressure, inadequate procedures
- Human error probabilities available in handbooks (THERP, HEART)

---

## Pitfall 6: Double-Counting Events

**Description**: Same failure appears in multiple branches but is counted multiple times in quantitative analysis.

**Symptoms**:
- Same basic event name in multiple tree locations
- Probability seems too high for well-designed system
- Cut set analysis shows redundant entries
- Tree restructuring changes probability unexpectedly

**Example**:
```
System Fails
     |
  [OR gate]
   /     \
Path A   Path B
Fails    Fails
  |        |
[AND]    [AND]
/  \     /  \
A   B   B   C    <-- B appears twice!
```
*Problem*: If B fails, it contributes through both paths but may be counted twice.

**Remediation**:
- Use "repeat event" or "transfer" symbols for events appearing multiple times
- Mark events appearing multiple times with same identifier
- In MCS analysis, reduce cut sets to remove duplicates
- Calculation should use: P(A∪B) = P(A) + P(B) - P(A∩B)

---

## Pitfall 7: Circular Logic or Impossible Events

**Description**: Tree contains logical impossibilities or self-references.

**Symptoms**:
- Event A causes Event B which causes Event A
- Events that physically cannot occur in the scenario
- Contradictory events in same cut set
- Tree cannot be resolved mathematically

**Example - Circular**:
```
Pump Fails → No Cooling → Overheating → Pump Fails
```

**Example - Contradictory**:
Cut set contains both "Valve Open" and "Valve Closed"

**Remediation**:
- Review each branch for physical plausibility
- Check cut sets for mutually exclusive events
- Model time-dependent sequences using Event Trees instead
- If circular dependencies exist, may need dynamic analysis

---

## Pitfall 8: Missing External Events

**Description**: Tree only considers internal failures, ignoring external initiators.

**Symptoms**:
- No environmental events in tree
- Analysis assumes "normal" conditions only
- Known external hazards not addressed
- Post-incident reveals external cause not modeled

**Common Missing External Events**:
- Power outages
- Natural disasters (earthquake, flood, lightning)
- External fires
- Cyber attacks
- Human external actions (vehicle impact, sabotage)
- Environmental extremes (temperature, humidity)

**Remediation**:
- List external initiators relevant to system
- Include as basic events or house events
- If specific external event being analyzed, make it house event (TRUE)
- Consider regulatory requirements for external event analysis

---

## Pitfall 9: Probability Data Misuse

**Description**: Using failure data incorrectly or from inappropriate sources.

**Symptoms**:
- Probabilities from wrong operating environment
- Failure rates applied without mission time consideration
- Point estimates without uncertainty bounds
- Generic data for unique components
- Mixing frequencies and probabilities

**Common Errors**:
- Using hourly failure rate directly as probability (must multiply by time)
- Using commercial data for military/extreme environment
- Applying handbook values without considering operational context
- Ignoring confidence intervals in source data

**Remediation**:
- P(failure) = 1 - e^(-λt) ≈ λt for small λt
- Match data source to operating environment
- Document data sources for traceability
- Include uncertainty analysis when data quality varies
- Use conservative (higher) values when uncertain

---

## Pitfall 10: Analysis Stops at Tree

**Description**: Building the tree but not using it for insights or decisions.

**Symptoms**:
- No minimal cut set analysis
- No recommendations or design changes identified
- Tree filed away without action
- Same failures occur despite analysis

**Remediation**:
- Always identify minimal cut sets
- Flag single points of failure for design attention
- Prioritize improvements by risk reduction effectiveness
- Link analysis to design requirements or changes
- Track implementation of identified improvements
- Review tree when system changes

---

## Quick Reference Checklist

Before finalizing analysis, verify:

- [ ] Top event is single, specific, measurable
- [ ] Gate types match logical relationships (AND = all required, OR = any sufficient)
- [ ] All branches developed to basic events or justified undeveloped events
- [ ] Common cause failures considered for redundant systems
- [ ] Human errors included where relevant
- [ ] No duplicate events without proper handling
- [ ] No circular logic or impossible events
- [ ] External events considered
- [ ] Probability data sources documented and appropriate
- [ ] Minimal cut sets identified and analyzed
- [ ] Recommendations linked to analysis findings
