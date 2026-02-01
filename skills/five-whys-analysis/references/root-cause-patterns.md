# Common Root Cause Patterns

Embedded root cause patterns for offline validation when knowledge-mcp is unavailable.

## 5M Root Cause Categories

The 5M framework provides a systematic categorization for root causes in manufacturing and process environments.

| Category | Description | Example Root Causes |
|----------|-------------|---------------------|
| **Man (People)** | Human factors, training, competence | Inadequate training, lack of standard work, operator error due to poor procedures, fatigue/workload |
| **Machine (Equipment)** | Equipment failures, maintenance, capability | Equipment not maintained to specification, machine capability insufficient, tooling wear, improper setup |
| **Material** | Material defects, variation, supplier issues | Material out of specification, supplier process change, batch variation, storage degradation |
| **Method (Process)** | Process design, control, procedures | Process not capable (Cpk <1.33), inadequate process control, missing verification step, sequence error |
| **Measurement** | Measurement error, inspection, calibration | Gage R&R >10%, calibration interval inadequate, inspection method ineffective, wrong measurement technique |

**Extended categories (6M, 8P):**
- **Mother Nature (Environment):** Temperature, humidity, contamination, vibration
- **Management:** Resource allocation, prioritization, communication
- **Money:** Budget constraints, cost pressures

## Systematic vs. Random Failures

Source: ISO 26262-9:2018 (automotive functional safety)

### Systematic Failures

Failures related in a deterministic way to a certain cause, which can only be eliminated by a modification of the design, manufacturing process, operational procedures, documentation, or other relevant factors.

**Characteristics:**
- Reproducible under same conditions
- Root cause traceable to specific design or process defect
- Eliminated through corrective action to process/design

**Common systematic failure root causes:**
- Design errors or flaws
- Manufacturing process defects
- Software bugs (specification, implementation, integration)
- Inadequate specifications or requirements
- Documentation errors
- Procedure gaps or ambiguity

**Root cause investigation approach:**
- Focus on process and design factors
- Look for "why was this error not detected earlier?"
- Address detection controls and prevention controls

### Random Failures

Failures that can occur unpredictably during the lifetime of a hardware element and that follow a probability distribution.

**Characteristics:**
- Stochastic occurrence (probabilistic)
- Cannot be completely eliminated through process improvements
- Addressed via redundancy, derating, or fault tolerance

**Common random failure root causes:**
- Component wear-out
- Environmental stress (thermal, vibration, humidity)
- Material degradation over time
- Fatigue
- Cosmic rays (soft errors in electronics)

**Root cause investigation approach:**
- Focus on usage environment and stress factors
- Look for overstress conditions or accelerated wear
- Address through design margins, derating, or redundancy

## AIAG-VDA Common Cause Patterns

Source: AIAG-VDA FMEA Handbook (2019), Section 4.3

### Process Control Failures

| Pattern | Description | Validation Questions |
|---------|-------------|---------------------|
| Lack of SPC | No statistical process control on critical parameters | Is the process monitored? Are control limits defined? |
| Inspection gap | Inadequate inspection frequency or coverage | When was defect first detectable? Why wasn't it caught? |
| Process capability | Cpk below 1.33 for critical dimensions | What is process capability? Is it sufficient? |
| Work instruction | Operator not following work instructions | Are instructions clear? Are operators trained? |
| Setup error | Incorrect setup not detected before production | How is setup verified? What controls exist? |

### Design Deficiencies

| Pattern | Description | Validation Questions |
|---------|-------------|---------------------|
| Validation gap | Inadequate design validation | Were all use conditions tested? What was missed? |
| Missing failure mode | Failure mode not identified in DFMEA | Why wasn't this failure mode anticipated? |
| Tolerance stack | Tolerance stack-up not analyzed | Do worst-case tolerances still meet function? |
| Material selection | Material inappropriate for environment | Were environmental conditions specified correctly? |
| Interface error | Interface specification incomplete | Were all interface parameters defined? |

### Supplier Quality

| Pattern | Description | Validation Questions |
|---------|-------------|---------------------|
| Incoming inspection | Incoming inspection ineffective | Does inspection catch defects at documented rate? |
| Process change | Supplier process change not validated | Was change notification received? Was re-validation done? |
| Critical characteristic | Critical characteristic not identified | Is characteristic in supplier FMEA? Is it controlled? |
| Specification gap | Specification does not capture requirement | Does specification fully describe required performance? |

## Symptom vs. Root Cause Discrimination

Use these tests to determine if you've reached root cause or are still at symptom level:

| Test | Question | If Yes... |
|------|----------|-----------|
| **Reversibility** | If we fix this, will the problem be prevented? | May be root cause |
| **Control** | Is this within our ability to address? | May be root cause |
| **Process focus** | Does this identify a process/system gap (not a person)? | May be root cause |
| **Prevention** | Would addressing this prevent similar problems? | May be root cause |
| **Symptom check** | Is this a consequence of something else? | Continue digging |
| **Blame check** | Does this blame a person rather than process? | Reframe to process |

## Citation Format

When MCP unavailable, cite as:
- "Common 5M root cause pattern: Method (Process) - inadequate process control (embedded reference data)"
- "Per ISO 26262 systematic failure definition (embedded reference data)"
- "Matches AIAG-VDA common cause pattern: supplier process change (embedded reference)"

**Never fabricate section numbers** when knowledge-mcp unavailable.

## Related References

For deeper root cause analysis guidance:
- `/lookup-standard 5 Whys stopping criteria` - When to stop asking Why
- `/lookup-standard fault tree analysis basic events` - Complementary FTA techniques
- `/lookup-standard root cause verification tests` - Validation approaches

---

**Document Version**: 1.0
**Sources:** ISO 26262-9 (2018), AIAG-VDA FMEA Handbook (2019)
**Last Updated**: 2026-01-31
