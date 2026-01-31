# RCCA Skills Test Prompts

Copy-paste these prompts to test each skill. Save the outputs as examples.

---

## 1. RCCA Master

### Test 1.1: Start New Investigation
```
I need to conduct an 8D investigation. We've received 5 customer complaints
in the past 2 weeks about our Model X-500 power supply units failing within
30 days of installation. The units are overheating and shutting down. This
affects our enterprise customers and we've already issued $50,000 in credits.

Help me start the 8D process.
```

### Test 1.2: Resume at Specific Phase
```
We've completed D0-D3 for our power supply investigation:
- D0: Manufacturing defect, High severity, Immediate urgency
- D1: Team formed (QE lead, Manufacturing Eng, Thermal Eng, Production Sup)
- D2: Problem statement: "Model X-500 PSU overheats (>95°C) and shuts down
  within 30 days of installation at 15% of customer sites, versus 0% expected"
- D3: Containment: Halted shipments, customer advisory issued

Now help me with D4 - which root cause tool should I use?
```

### Test 1.3: Tool Selection Guidance
```
For our 8D investigation, the problem is:
- Occurring on multiple production lines
- Started 3 months ago
- We have defect data by category
- Problem is recurring despite previous fixes

Which root cause analysis tool should we use and why?
```

---

## 2. Problem Definition

### Test 2.1: Full 5W2H + IS/IS NOT
```
Help me define this problem using 5W2H and IS/IS NOT:

"Our website checkout is broken and customers are complaining."
```

### Test 2.2: Validate Existing Statement
```
Is this problem statement ready for root cause analysis?
Identify any issues:

"The assembly operators on Line 3 are not following the work instructions
properly, which is causing too many defects because they need more training."
```

### Test 2.3: Improve Vague Statement
```
Transform this vague statement into a proper problem definition:

"There are quality issues with our product."

Context: We make automotive brake components.
```

### Test 2.4: Deviation Statement
```
Help me write a deviation-based problem statement:
- Expected: 99.5% first-pass yield on SMT assembly
- Actual: 94.2% first-pass yield
- Product: ECU controller board
- Time: Last 3 weeks
- Location: Building B, Line 2
```

---

## 3. Five Whys Analysis

### Test 3.1: Basic Analysis
```
Run a 5 Whys analysis on this problem:

"Customer order #78432 shipped 5 days late, causing the customer to
miss their product launch deadline."
```

### Test 3.2: With Evidence Verification
```
Help me do a rigorous 5 Whys analysis with evidence requirements for each step.

Problem: "3 of 50 PCB assemblies failed electrical test on Tuesday.
The failure was open circuit on U12 pin 7."
```

### Test 3.3: Verify Root Cause Depth
```
I've done a 5 Whys and landed on "lack of training" as the root cause.

Problem: Operator assembled part backwards
Why 1: Didn't notice orientation marking
Why 2: Marking was faded
Why 3: Laser marker settings wrong
Why 4: Operator didn't verify settings
Why 5: Lack of training on verification step

Is this really a root cause or should I go deeper? What questions should
I ask to verify?
```

### Test 3.4: Multiple Causal Chains
```
Our problem has two potential causal paths. Help me analyze both:

Problem: "Machine stopped unexpectedly at 2:15 PM"
Path A: Relates to the PLC controller
Path B: Relates to the hydraulic system

Guide me through both chains.
```

---

## 4. Fishbone Diagram

### Test 4.1: Manufacturing (6Ms)
```
Create a fishbone diagram using 6Ms for:

"Surface finish defects (scratches, pitting) on CNC machined aluminum
housings. Reject rate is 8% vs. target of 2%."
```

### Test 4.2: Service (8Ps)
```
Build a fishbone diagram using 8Ps for:

"Customer support ticket resolution time averages 72 hours,
target is 24 hours."
```

### Test 4.3: With Prioritization
```
Help me build a fishbone and prioritize the causes for:

"Software deployment failures - 3 of last 10 deployments had to be
rolled back due to production issues."

After building the fishbone, guide me through prioritizing which
causes to investigate first.
```

### Test 4.4: Custom Categories
```
I want to create a fishbone diagram for healthcare appointment no-shows,
but 6Ms doesn't fit. Help me define appropriate custom categories and
build the diagram.

Problem: "25% of scheduled appointments result in no-shows"
```

---

## 5. Pareto Analysis

### Test 5.1: Basic Frequency Analysis
```
Create a Pareto analysis for our defect data from Q4:

| Defect Type | Count |
|-------------|-------|
| Solder bridges | 156 |
| Missing components | 89 |
| Tombstoning | 67 |
| Cold joints | 45 |
| Wrong polarity | 34 |
| Insufficient solder | 28 |
| Other | 22 |

Identify the vital few and recommend focus areas.
```

### Test 5.2: Cost-Weighted Analysis
```
Do a cost-weighted Pareto analysis:

| Issue | Occurrences | Cost per Occurrence |
|-------|-------------|---------------------|
| Rework | 120 | $50 |
| Scrap | 45 | $200 |
| Field returns | 30 | $500 |
| Warranty claims | 15 | $1,200 |
| Shipping errors | 80 | $75 |

Which issues should we prioritize based on total cost impact?
```

### Test 5.3: Trend Comparison
```
Compare these two Pareto distributions and identify what's changed:

**January:**
Defect A: 60, Defect B: 45, Defect C: 30, Defect D: 25, Defect E: 15

**February:**
Defect A: 35, Defect B: 50, Defect C: 55, Defect D: 20, Defect E: 18

What does this tell us about our improvement efforts?
```

### Test 5.4: Multi-Level Pareto
```
Our top defect category is "Mechanical failures" (45% of total).
Help me do a second-level Pareto analysis within this category:

| Mechanical Sub-type | Count |
|---------------------|-------|
| Bearing failure | 42 |
| Shaft wear | 28 |
| Seal leak | 23 |
| Coupling damage | 18 |
| Housing crack | 12 |
| Other mechanical | 8 |
```

---

## 6. Fault Tree Analysis

### Test 6.1: Build Basic Fault Tree
```
Create a fault tree for:

TOP EVENT: "Complete loss of vehicle braking capability"

Consider: Primary hydraulic system, secondary/backup system,
electronic brake assist, mechanical parking brake.
```

### Test 6.2: Find Minimal Cut Sets
```
Analyze this fault tree and identify the minimal cut sets:

TOP: System Outage (OR)
├── Server Cluster Failure (AND)
│   ├── Server A fails
│   └── Server B fails
├── Network Failure (OR)
│   ├── Primary network down
│   └── Backup network down
└── Power Loss (AND)
    ├── Utility power fails
    └── UPS fails
    └── Generator fails
```

### Test 6.3: Probability Calculation
```
Calculate the top event probability given these basic event probabilities:

TOP: Data Loss (OR)
├── Hardware Failure (AND)
│   ├── Primary drive fails: P = 0.02
│   └── Backup drive fails: P = 0.02
└── Software Corruption (OR)
    ├── Application bug: P = 0.005
    └── OS failure: P = 0.001

What is the probability of data loss?
```

### Test 6.4: Identify Common Cause Failures
```
Review this system architecture for common cause failures:

"We have redundant pumps (A and B) for coolant circulation.
Both are powered by the same electrical panel. Both use the
same type of seal from the same supplier. Both are maintained
by the same technician on the same schedule."

Build a fault tree that reveals the common cause vulnerabilities.
```

---

## 7. FMEA Analysis

### Test 7.1: Start DFMEA
```
Create a DFMEA for a new lithium-ion battery charger with these functions:
1. Convert AC to DC power
2. Regulate charging current
3. Monitor battery temperature
4. Provide overcurrent protection
5. Indicate charging status

For each function, identify potential failure modes, effects, causes,
and current controls. Then assign S, O, D ratings and determine Action Priority.
```

### Test 7.2: Start PFMEA
```
Create a PFMEA for the PCB reflow soldering process:

Process steps:
1. Load PCB onto conveyor
2. Preheat zone (ramp to 150°C)
3. Soak zone (150-200°C for 60-90 sec)
4. Reflow zone (peak 245°C for 30 sec)
5. Cooling zone
6. Unload and inspect
```

### Test 7.3: Calculate Action Priority
```
Calculate the Action Priority (AP) for these failure modes and
recommend actions for HIGH priority items:

| Failure Mode | S | O | D |
|--------------|---|---|---|
| Thermal runaway | 10 | 3 | 6 |
| Incorrect voltage | 7 | 4 | 4 |
| LED indicator fails | 2 | 5 | 8 |
| Charge timeout too short | 5 | 6 | 5 |
| Connector overheating | 8 | 4 | 7 |
```

### Test 7.4: Optimize HIGH Priority Items
```
I have these HIGH Action Priority items in my FMEA. Help me develop
corrective actions and estimate revised ratings:

1. Failure Mode: Motor winding short circuit
   S=9, O=5, D=6, AP=HIGH
   Current controls: None

2. Failure Mode: Software freezes during operation
   S=8, O=6, D=8, AP=HIGH
   Current controls: Watchdog timer (not validated)

3. Failure Mode: Incorrect calibration data loaded
   S=7, O=4, D=9, AP=HIGH
   Current controls: Manual verification
```

---

## Combined Workflow Test

### Test: Full RCCA Flow
```
I need to run a complete root cause investigation. Here's the situation:

PROBLEM: Our automated packaging line has been rejecting 12% of products
at the final weight check station, versus a target of 2%. This started
3 weeks ago after we introduced a new product variant. The rejects are
being manually reworked, causing overtime costs and delayed shipments.

Walk me through:
1. Problem definition (D2)
2. Selecting the right analysis tool
3. Conducting the root cause analysis
4. Developing corrective actions

Use whichever RCCA tools are appropriate for each step.
```

---

## Script Verification Tests

### Python Script Tests

After running each skill, verify the Python scripts work:

```bash
# RCCA Master
cd ~/projects/claude-plugins/skills/rcca-master/scripts
python initialize_8d.py --id "TEST-001" --title "Test Investigation"
python score_8d.py --json '{"d0":4,"d1":4,"d2":3,"d3":4,"d4":3,"d5":3,"d6":2,"d7":2,"d8":2}'

# Problem Definition
cd ~/projects/claude-plugins/skills/problem-definition/scripts
python validate_statement.py "The machine broke because the operator forgot to check the oil"
python score_analysis.py --json '{"completeness":4,"specificity":3,"measurability":4,"neutrality":5}'

# Five Whys
cd ~/projects/claude-plugins/skills/five-whys-analysis/scripts
python score_analysis.py --json '{"problem_definition":4,"causal_chain_logic":4,"evidence_basis":3,"root_cause_depth":4,"actionability":4,"countermeasures":3}'

# FMEA
cd ~/projects/claude-plugins/skills/fmea-analysis/scripts
python calculate_fmea.py --interactive
```

---

## Notes for Saving Examples

When you run these tests, save the outputs to:
- `[skill-name]/examples/example-[test-number].md`

Include:
1. The prompt you used
2. The full response
3. Any diagrams or charts generated
4. Script outputs (if applicable)
