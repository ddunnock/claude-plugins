# FMEA Worked Examples

## Overview

This document provides worked examples demonstrating proper FMEA development following the AIAG-VDA 7-step approach. Each example includes structure analysis, function analysis, failure analysis, risk analysis, and optimization.

---

## Example 1: DFMEA - Automotive Power Window Motor

### Step 1: Planning & Preparation

**InTent**: Identify design risks in power window motor for new vehicle program
**Timing**: Concept phase, due before Design Verification milestone
**Team**: Motor design engineer, electronics engineer, durability engineer, manufacturing engineer, warranty analyst
**Tasks**: Complete DFMEA for motor assembly, feed critical items to PFMEA
**Scope**: Motor assembly including armature, housing, gear train, connector; excludes window regulator and switch

### Step 2: Structure Analysis

```
System Level: Power Window System
    └── Subsystem Level: Power Window Motor Assembly
            ├── Armature Assembly
            │       ├── Shaft
            │       ├── Commutator
            │       └── Windings
            ├── Motor Housing
            │       ├── Brush Assembly
            │       └── Bearings
            ├── Gear Train
            │       ├── Worm Gear
            │       └── Reduction Gear
            └── Electrical Connector
```

### Step 3: Function Analysis

| Element | Function | Requirement |
|---------|----------|-------------|
| Motor Assembly | Convert electrical energy to rotational torque | Output torque ≥ 2.5 Nm at 12V |
| Motor Assembly | Operate within speed range | 50-80 RPM no-load speed |
| Armature Shaft | Transmit torque from armature to gear train | Withstand 5 Nm peak torque |
| Bearings | Support shaft rotation with minimal friction | Bearing life ≥ 100,000 cycles |
| Connector | Maintain electrical continuity | Contact resistance < 5 mΩ |

### Step 4-5: Failure Analysis and Risk Analysis

**Focus Element**: Motor Assembly

| Failure Mode | Effect (S) | Cause | Prevention Controls | O | Detection Controls | D | AP |
|--------------|------------|-------|---------------------|---|-------------------|---|-----|
| Motor does not operate | Window inoperable; customer must manually close window; S=7 | Armature windings open circuit due to wire fatigue | Wire gauge specified per load calculation; vibration analysis | 4 | Functional test 100%; continuity test | 3 | M |
| Motor does not operate | Window inoperable; customer must manually close window; S=7 | Connector terminal backed out | Terminal retention feature in design; insertion force spec | 3 | Pull test at assembly; functional test | 4 | M |
| Motor operates intermittently | Window stops mid-travel; customer dissatisfied; S=6 | Brush wear excessive | Brush material spec; brush spring force requirement | 5 | Durability test 100K cycles; brush length inspection | 4 | M |
| Motor speed too slow | Window closes slowly; annoyance; S=4 | Bearing drag due to improper lubrication | Lubricant specification; quantity controlled | 4 | Speed test at EOL; torque test | 3 | L |
| Motor overheats | Circuit protection trips; window inoperable; potential harness damage; S=8 | Armature windings shorted due to insulation breakdown | Insulation class H specified; max temperature design calc | 3 | Thermal test at rated load; insulation test | 4 | M |

### Step 6: Optimization (High/Medium AP Items)

| Failure Mode | AP | Action | Type | Owner | Target |
|--------------|-----|--------|------|-------|--------|
| Motor does not operate (winding) | M | Add wire anchor at commutator to prevent fatigue from vibration | Prevention | J. Chen | 2024-02-15 |
| Motor does not operate (connector) | M | Increase terminal lance feature depth by 0.5mm | Prevention | J. Chen | 2024-02-15 |
| Motor operates intermittently | M | Increase brush length by 2mm for additional wear margin | Prevention | R. Patel | 2024-02-28 |
| Motor overheats | M | Add thermal cutoff device to motor assembly | Prevention | R. Patel | 2024-03-15 |

---

## Example 2: PFMEA - Welding Process

### Step 1: Planning & Preparation

**InTent**: Identify process risks for robotic MIG welding of automotive bracket
**Timing**: Pre-production, support PPAP submission
**Team**: Welding engineer, robot programmer, quality engineer, maintenance tech, production supervisor
**Scope**: MIG welding operation only; excludes material handling and inspection stations

### Step 2: Structure Analysis

```
Process Level: Bracket Assembly Cell
    └── Process Step: MIG Weld Station
            ├── Part Loading (4M elements)
            │       ├── Man: Operator loads parts
            │       ├── Machine: Fixture
            │       ├── Material: Brackets
            │       └── Method: Loading procedure
            ├── Weld Execution (4M elements)
            │       ├── Man: N/A (automated)
            │       ├── Machine: Robot, welder
            │       ├── Material: Wire, gas
            │       └── Method: Weld program
            └── Part Unloading (4M elements)
```

### Step 3: Function Analysis

| Process Step | Function | Product Characteristic |
|--------------|----------|----------------------|
| Part Loading | Position bracket in fixture | Part seated against all locators |
| Part Loading | Secure bracket for welding | Clamp force maintains position during weld |
| Weld Execution | Deposit weld bead per specification | Weld length 25 ±2mm |
| Weld Execution | Achieve weld penetration | Fusion to both parent materials |
| Weld Execution | Maintain weld quality | No porosity, cracks, undercut |

### Step 4-5: Failure Analysis and Risk Analysis

**Focus Element**: Weld Execution Step

| Failure Mode | Effect (S) | Cause | Prevention Controls (O) | Detection Controls (D) | AP |
|--------------|------------|-------|------------------------|----------------------|-----|
| Weld length short | Joint strength reduced; potential field failure under load; S=8 | Robot program error (wrong endpoint) | Program verification procedure; master part qualification | Vision system measures weld length; O=3, D=3 | M |
| Weld length short | Joint strength reduced; potential field failure under load; S=8 | Part mislocated in fixture | Fixture sensors verify part position before weld; error-proof | Automated go/no-go before weld enable; O=2, D=2 | L |
| Porosity in weld | Reduced joint strength; potential crack initiation; S=7 | Insufficient shielding gas flow | Gas flow meter with low-flow alarm; PM to check regulator | Operator visual inspection 100%; O=5, D=6 | H |
| Porosity in weld | Reduced joint strength; potential crack initiation; S=7 | Contaminated base metal (oil, rust) | Supplier cleanliness spec; incoming inspection | Operator visual inspection 100%; O=4, D=6 | H |
| Incomplete fusion | Joint does not meet strength requirement; field failure; S=9 | Travel speed too fast | Weld parameter monitoring; program lock | Destructive test per lot; visual for obvious defects; O=3, D=7 | H |
| Incomplete fusion | Joint does not meet strength requirement; field failure; S=9 | Wrong wire type loaded | Color-coded wire spools; wire ID verification procedure | Visual check of wire label; O=2, D=5 | H |
| Spatter on part | Cosmetic defect; customer complaint; S=4 | Incorrect wire stickout | Stickout gauge at setup; contact tip change interval | Visual inspection 100%; O=5, D=3 | L |

### Step 6: Optimization (High AP Items)

| Failure Mode | AP | Action | Type | Owner | Target | Status |
|--------------|-----|--------|------|-------|--------|--------|
| Porosity (gas flow) | H | Install automated gas flow monitoring with interlock—stops weld if flow <15 CFH | Prevention | M. Lopez | 2024-01-30 | Complete |
| Porosity (gas flow) | H | Add inline gas flow sensor with real-time display at operator station | Detection | M. Lopez | 2024-01-30 | Complete |
| Porosity (contamination) | H | Add solvent wipe step before welding with verification checklist | Prevention | K. Wong | 2024-02-15 | In progress |
| Incomplete fusion (speed) | H | Add weld parameter monitoring system with automatic alarm for out-of-spec | Detection | M. Lopez | 2024-02-28 | Planned |
| Incomplete fusion (wire) | H | Install wire verification scanner—reads barcode on spool before enable | Prevention | K. Wong | 2024-02-28 | Planned |

### Re-evaluation After Actions

| Failure Mode | Original S/O/D/AP | Actions Taken | Revised S/O/D/AP |
|--------------|-------------------|---------------|------------------|
| Porosity (gas flow) | 7/5/6/H | Gas flow interlock installed | 7/2/3/L |
| Incomplete fusion (wire) | 9/2/5/H | Wire barcode scanner installed | 9/1/2/L |

---

## Example 3: FMEA Anti-Example (Common Mistakes)

This example shows what NOT to do:

### Poor FMEA (Multiple Errors)

| Failure Mode | Effect | Cause | S | O | D | RPN | Controls |
|--------------|--------|-------|---|---|---|-----|----------|
| Fails | Bad | Operator error | 5 | 5 | 5 | 125 | Check |
| Part problem | Scrapped | Material | 6 | 4 | 4 | 96 | Inspection |
| Doesn't work | Customer complaint | Wrong | 8 | 3 | 3 | 72 | Visual |

### Problems Identified

1. **Failure Modes are vague**: "Fails", "Part problem", "Doesn't work" - no specificity
2. **Effects are non-specific**: "Bad", "Scrapped" don't describe actual consequences
3. **Causes are incomplete**: "Operator error", "Material", "Wrong" - what specifically?
4. **No function connection**: Where is the function these modes relate to?
5. **Controls not distinguished**: Prevention vs. Detection unclear
6. **Ratings likely inflated**: D=3-5 for "visual" and "inspection" are optimistic
7. **Using RPN only**: Missing AP assessment; S=8 item with RPN=72 may be overlooked
8. **No actions**: Despite RPN >50, no actions documented

### Corrected Version

| Function | Failure Mode | Effect | S | Cause | Prevention Controls | O | Detection Controls | D | AP | Action |
|----------|--------------|--------|---|-------|---------------------|---|-------------------|---|-----|--------|
| Seal bearing cavity from contamination | Seal allows contamination ingress | Bearing wear → motor failure → pump inoperable; replacement required | 7 | Seal lip damaged during assembly | Assembly fixture guides seal; torque-controlled press | 4 | Visual inspection of seal position | 6 | H | Add go/no-go gauge for seal position |
| Maintain shaft alignment within ±0.05mm | Shaft misaligned >0.10mm | Excessive vibration → bearing failure → customer complaint | 6 | Bearing bore out of tolerance | CNC machining process capability study; Cpk>1.67 | 3 | CMM inspection 1:50 ratio | 4 | M | Increase CMM inspection to 1:20 during launch |

---

## Example 4: FMEA-MSR (Monitoring and System Response)

### Context
Supplemental FMEA for an electric power steering system evaluating diagnostic capability during customer operation.

### Focus: Torque Sensor Monitoring

| Function | Failure Mode | Effect Without MSR | S₀ | Monitoring & Diagnostic | Response Action | S₁ | Diagnostic Coverage |
|----------|--------------|-------------------|-----|------------------------|-----------------|-----|---------------------|
| Measure steering torque input | Signal drift >5% | Incorrect assist level; potential loss of control | 9 | Continuous plausibility check vs. vehicle speed and steering angle | Warn driver via DIC; reduce assist to fixed level | 5 | 95% (signal drift detected within 100ms) |
| Measure steering torque input | Signal loss (open circuit) | No assist; heavy steering | 8 | Signal validity check; watchdog timer | Immediate warning; default to manual steering | 3 | 99% (immediate detection) |
| Measure steering torque input | Signal stuck at fixed value | Assist inconsistent with input; potential over/under-assist | 8 | Stuck signal detection algorithm | Warning; gradual assist reduction | 4 | 90% (detected within 500ms) |

### FMEA-MSR Key Concepts

1. **S₀**: Severity without monitoring/system response (worst case)
2. **S₁**: Severity with monitoring/system response (mitigated)
3. **Diagnostic Coverage**: Percentage of failure occurrences the monitoring can detect
4. **Response Action**: What the system does when failure is detected

### Goal
FMEA-MSR demonstrates that safety-critical failure modes are adequately covered by monitoring and that system response maintains safe state.

---

## Key Takeaways from Examples

1. **Start with functions**: Every failure mode should relate to a specific function
2. **Be specific**: Vague descriptions provide no value
3. **Use the failure chain**: Mode ← Cause → Effect with correct directionality
4. **Distinguish controls**: Prevention (affects O) vs. Detection (affects D)
5. **Prioritize by severity**: S=9-10 always requires attention regardless of AP/RPN
6. **Take action**: FMEA value comes from risk reduction, not documentation
7. **Re-evaluate**: Update ratings after actions to demonstrate improvement
8. **Keep it living**: FMEA evolves with the product/process
