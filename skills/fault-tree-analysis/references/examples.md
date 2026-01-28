# Fault Tree Analysis Examples

## Example 1: Pump System Failure (Qualitative)

### Context
Cooling water pump system with redundant pumps serving a manufacturing process. Need to analyze "Loss of Cooling Water Flow" to process heat exchangers.

### System Definition
- **System**: Cooling water supply to Process Area 1
- **Boundaries**: From cooling tower basin to process heat exchanger inlet
- **Operating mode**: Normal continuous operation
- **Assumptions**: Single operating shift, adequate water supply from cooling tower
- **Purpose**: Design review for new installation

### Top Event
**"Cooling water flow to Process Area 1 falls below 500 GPM for more than 5 minutes"**

### Fault Tree Structure

```
Cooling Water Flow Loss (>5 min)
              |
          [OR gate]
    __________|___________
   |          |          |
Complete   Partial    Piping
Pumping    Flow       System
Failure    Loss       Failure
   |          |          |
[AND gate] [OR gate]  [OR gate]
  /   \      |   |      |    |
Pump A Pump B  |   |   Main  Branch
Fails  Fails   |   |   Line  Line
  |      |     |   |   Rupture Block
 ...    ...    |   |     |      |
           Control  Check  [Basic] [Basic]
           Valve    Valve
           Fails    Fails
             |        |
          [Basic]  [Basic]
```

### Detailed Branch: Pump A Fails
```
Pump A Fails
     |
  [OR gate]
   /   |   \
Motor  Pump  Loss of
Fails  Mech  Power to
  |    Fails  Pump A
  |      |      |
[OR]   [OR]   [OR]
 /|\    /|\    /|\
...    ...    ...
```

### Minimal Cut Sets (Qualitative)

**Order 1 (Single Points of Failure):**
- Main line rupture
- Control valve fails closed
- (None for pump failures due to redundancy)

**Order 2:**
- {Pump A fails, Pump B fails}
- {Pump A fails, Check valve fails}
- {Pump A power loss, Pump B mechanical failure}
- ... (additional combinations)

**Order 3:**
- {Pump A motor fails, Pump B impeller fails, Branch line blocked}
- ... (additional combinations)

### Key Findings

1. **Single Points of Failure Identified:**
   - Main supply line (no redundancy)
   - Control valve (single valve for flow control)
   
2. **Redundancy Effective For:**
   - Pump failures (two pumps in parallel)
   - Power supply (separate breakers)

3. **Recommendations:**
   - Consider redundant control valve or bypass
   - Assess main line failure probability (corrosion, external damage)
   - Review control valve maintenance frequency

### Quality Score: 85/100 (Good)
- System Definition: 4/5 - Clear boundaries, minor gaps in documentation
- Top Event Clarity: 5/5 - Specific, measurable, time-bounded
- Tree Completeness: 4/5 - Good development, some branches could go deeper
- Minimal Cut Sets: 4/5 - Correctly identified, prioritized
- Quantification: 3/5 - Not performed (acceptable for design review)
- Actionability: 4/5 - Clear recommendations tied to findings

---

## Example 2: Safety Interlock Failure (Quantitative)

### Context
Emergency shutdown system for chemical reactor. Two independent pressure sensors trigger shutdown when pressure exceeds limit. Need to calculate probability of failure to shutdown.

### System Definition
- **System**: Reactor Emergency Shutdown System (ESD)
- **Boundaries**: From pressure transmitters to shutdown valve actuator
- **Operating mode**: Standby safety system
- **Mission time**: 1 year continuous operation
- **Purpose**: Safety Integrity Level (SIL) verification

### Top Event
**"ESD fails to close shutdown valve within 1 second when reactor pressure exceeds 150 psig"**

### Fault Tree Structure

```
ESD Fails to Shutdown
         |
      [OR gate]
    _____|_____
   |           |
Sensing     Actuation
System       System
Fails        Fails
   |           |
[AND gate]  [OR gate]
  /    \     /    \
PT-1   PT-2  Logic  Valve
Fails  Fails Solver Fails
  |      |   Fails    |
[Basic] [Basic] |   [OR gate]
              [Basic]  /   \
                    Valve  Solenoid
                   Mech    Fails
                   Fails     |
                     |    [Basic]
                  [Basic]
```

### Basic Event Probability Data

| Event | Failure Rate | Mission Time | Probability | Source |
|-------|-------------|--------------|-------------|--------|
| PT-1 fails to detect | 5×10⁻⁶/hr | 8760 hr | 4.4×10⁻² | Field data |
| PT-2 fails to detect | 5×10⁻⁶/hr | 8760 hr | 4.4×10⁻² | Field data |
| Logic solver fails | 1×10⁻⁶/hr | 8760 hr | 8.8×10⁻³ | Vendor data |
| Valve mech fails | 2×10⁻⁶/hr | 8760 hr | 1.8×10⁻² | Handbook |
| Solenoid fails | 3×10⁻⁶/hr | 8760 hr | 2.6×10⁻² | Handbook |

*Note: P ≈ λ×t for λt << 1*

### Minimal Cut Sets with Probabilities

**Order 1:**
- {Logic solver fails}: P = 8.8×10⁻³

**Order 2:**
- {PT-1 fails, PT-2 fails}: P = 4.4×10⁻² × 4.4×10⁻² = 1.9×10⁻³
- {Valve mech fails, [any]}: Combined with OR branch
- {Solenoid fails, [any]}: Combined with OR branch

**Valve Subsystem (OR gate):**
- P(valve OR solenoid) = 1.8×10⁻² + 2.6×10⁻² - (1.8×10⁻² × 2.6×10⁻²)
- P(valve OR solenoid) ≈ 4.4×10⁻²

### Top Event Probability Calculation

```
P(Sensing Fails) = P(PT-1) × P(PT-2) = 1.9×10⁻³

P(Actuation Fails) = P(Logic) + P(Valve system) - P(Logic)×P(Valve)
                   = 8.8×10⁻³ + 4.4×10⁻² - (8.8×10⁻³ × 4.4×10⁻²)
                   ≈ 5.2×10⁻²

P(Top Event) = P(Sensing) + P(Actuation) - P(Sensing)×P(Actuation)
             = 1.9×10⁻³ + 5.2×10⁻² - (1.9×10⁻³ × 5.2×10⁻²)
             ≈ 5.4×10⁻² per year
```

### Importance Analysis

**Fussell-Vesely Importance** (contribution to top event):
1. Valve mechanical: 33%
2. Solenoid: 48%
3. Logic solver: 16%
4. Sensors (combined): 3%

### Key Findings

1. **Dominant Contributors:**
   - Valve actuation system dominates (81% of risk)
   - Logic solver is significant single point of failure
   - Redundant sensors are effective (only 3% contribution)

2. **SIL Assessment:**
   - PFD ≈ 5.4×10⁻² does not meet SIL 2 (requires PFD < 10⁻²)
   - System currently suitable for SIL 1 only

3. **Recommendations:**
   - Add redundant logic solver to reduce SPOF risk
   - Consider redundant shutdown valve (1oo2 configuration)
   - Increase testing frequency for valve components

### Common Cause Failure Consideration

For sensor AND gate, must consider CCF:
- Both sensors from same manufacturer
- Same calibration procedure
- Same process connection point

Applying β = 5% (typical for similar components):
- P(CCF) = 0.05 × 4.4×10⁻² = 2.2×10⁻³
- Revised P(Sensing) = P(independent AND) + P(CCF)
- Revised P(Sensing) = 1.9×10⁻³ + 2.2×10⁻³ = 4.1×10⁻³

This increases sensor contribution but actuation still dominates.

### Quality Score: 92/100 (Excellent)
- System Definition: 5/5 - Complete with mission time and purpose
- Top Event Clarity: 5/5 - Precise with time requirement
- Tree Completeness: 4/5 - Well developed, CCF could be more explicit
- Minimal Cut Sets: 5/5 - Complete with probabilities
- Quantification: 5/5 - Correct calculations, sources documented
- Actionability: 4/5 - Clear recommendations, could add cost analysis

---

## Example 3: Anti-Example - Poor FTA

### Context
Same pump system as Example 1, but poorly executed.

### Problems Identified

**Poor Top Event:**
"Pump system doesn't work"
- *Problem*: Vague - what does "work" mean? No criteria.

**Incorrect Gate Usage:**
```
System Fails
    |
 [AND gate]   <-- WRONG! Should be OR
   /    \
Pump A  Pump B
Fails   Fails
```
- *Problem*: This says BOTH must fail for system to fail. If pumps are parallel (either provides flow), this is backwards. Should be OR gate because system fails if EITHER path fails.

**Incomplete Development:**
```
Pump A Fails
    |
 [Diamond]
"Electrical or
 Mechanical
  Problem"
```
- *Problem*: Not developed to basic events. Cannot analyze or assign probability.

**Missing Human Factors:**
- No operator errors considered
- No maintenance errors
- No procedure violations

**Missing CCF:**
- Redundant pumps treated as fully independent
- Same pump model, same maintenance crew, same power supply not considered

**No Cut Set Analysis:**
- Tree drawn but no minimal cut sets identified
- Single points of failure not flagged

**Probability Errors:**
- "Pump A failure rate: 0.001" (per what? hour? year?)
- "Top event probability: 0.000001" (where did this come from?)

### Corrected Version

See Example 1 for proper execution of this analysis.

### Quality Score: 38/100 (Inadequate)
- System Definition: 2/5 - Boundaries unclear
- Top Event Clarity: 1/5 - Completely vague
- Tree Completeness: 2/5 - Barely developed, wrong gates
- Minimal Cut Sets: 1/5 - Not identified
- Quantification: 1/5 - Numbers without basis
- Actionability: 2/5 - No useful recommendations

---

## Example 4: Manufacturing Equipment Hazard

### Context
Press machine safety analysis. Operator injury from unexpected press activation.

### Top Event
**"Press activates with operator's hands in die area during setup mode"**

### Key Tree Elements

```
Hazardous Press Activation
           |
        [AND gate]
        /        \
   Press         Hands in
  Activates      Die Area
  Unexpectedly      |
       |         [Basic]
    [OR gate]    Operator
     /  |  \     Position
    /   |   \    Error
   /    |    \
Control Safety  Electrical
System  Guard   Fault
Bypassed Failure Causes
   |       |    Activation
[OR gate] [OR]     |
  /  \    ...   [Basic]
 /    \
Operator Guard    
Defeats  Removed
Control  w/o     
   |    Lockout
[Basic]    |
        [Basic]
```

### Analysis Highlights

1. **AND Gate Justification:**
   - Both conditions must occur: press activates AND hands present
   - Reflects physical requirement for injury

2. **Human Factors Prominent:**
   - Operator defeats controls
   - Operator position error
   - Guard removed without lockout

3. **Key Minimal Cut Sets:**
   - {Operator defeats control, Operator position error}
   - {Guard removed w/o lockout, Position error, Electrical fault}

4. **Safety Barriers Identified:**
   - Two-hand control (requires both hands away)
   - Guard interlock
   - Setup mode lockout procedure

### Recommendations
- Add light curtain as additional barrier
- Implement positive guard interlock (not bypassable)
- Training emphasis on lockout procedures
- Consider presence-sensing device

---

## Summary: FTA Best Practices from Examples

1. **Top Event**: Always specific, measurable, time-bounded when relevant
2. **Gate Selection**: OR = any sufficient; AND = all required
3. **Development**: Continue to basic events; justify any diamonds
4. **CCF**: Always consider for redundant systems under AND gates
5. **Human Factors**: Include operator and maintenance errors
6. **Quantification**: Document sources, show calculations, state uncertainty
7. **Cut Sets**: Always identify and prioritize by order
8. **Action**: Link recommendations to specific vulnerabilities found
