# Common Pitfalls in Problem Definition

A well-defined problem is half solved. These pitfalls undermine investigation effectiveness.

## 1. Embedding Cause

**The Problem:** Stating assumed cause as part of the problem definition, before investigation has determined root cause.

| Bad (Embedded Cause) | Good (Neutral) |
|---------------------|----------------|
| "Cracked due to over-torque" | "Cracked at locking tab area" |
| "Corrosion from moisture ingress" | "Corrosion observed on contact surfaces" |
| "Failure caused by operator error" | "Failure occurred during manual assembly" |
| "Weld defect from wrong parameters" | "Incomplete weld fusion on joint B" |

**Why It Matters:** Embedding cause biases the investigation, leading teams to confirm the assumed cause rather than discover the actual cause.

## 2. Embedding Solution

**The Problem:** Framing the problem as a need for a specific solution.

| Bad (Embedded Solution) | Good (Neutral) |
|------------------------|----------------|
| "Need to change supplier" | "Material does not meet hardness spec" |
| "Operator needs retraining" | "Assembly sequence deviation observed" |
| "Software needs update" | "System displays incorrect values" |
| "Design requires modification" | "Interference between components A and B" |

**Why It Matters:** Embedding solution skips root cause analysis and leads to treating symptoms rather than causes.

## 3. Vagueness

**The Problem:** Non-specific language that doesn't bound the investigation.

| Bad (Vague) | Good (Specific) |
|-------------|-----------------|
| "Part failed" | "Bearing seized after 1,200 operating hours" |
| "Quality issue" | "Surface finish Ra 3.2 µm; spec requires Ra 1.6 µm max" |
| "Customer unhappy" | "Customer reported intermittent power loss during startup" |
| "Bad batch" | "Lot #4521: 47 of 500 units (9.4%) out of tolerance" |

**Why It Matters:** Vague problems lead to vague investigations. Without specifics, teams chase the wrong issues.

## 4. Blame Language

**The Problem:** Attributing fault to individuals or groups, which poisons the investigation environment.

| Bad (Blame) | Good (Neutral) |
|-------------|----------------|
| "Operator caused defect" | "Defect observed after manual operation" |
| "Supplier shipped bad parts" | "Incoming material failed inspection" |
| "Engineering designed it wrong" | "Design does not meet load requirement" |
| "QC missed the defect" | "Defect escaped detection at Station 3" |

**Why It Matters:** Blame discourages honest input from those with direct knowledge. People protect themselves rather than contribute to solutions.

## 5. Scope Creep

**The Problem:** Problem definition too broad, encompassing multiple distinct issues.

| Bad (Too Broad) | Good (Bounded) |
|-----------------|----------------|
| "General quality problems" | "Dimensional variation on Feature X" |
| "Machine unreliable" | "Spindle motor overheating after 4-hour continuous run" |
| "Process out of control" | "Temperature excursion beyond UCL on 3 of 12 batches" |

**Why It Matters:** Broad problems require multiple investigations. Trying to solve everything at once dilutes focus and delays resolution.

## 6. Missing Quantification

**The Problem:** No numerical data to characterize severity, frequency, or extent.

| Bad (Unquantified) | Good (Quantified) |
|-------------------|-------------------|
| "Several units affected" | "47 of 500 units (9.4%)" |
| "Happens sometimes" | "3 occurrences in 30-day period" |
| "Dimension out of spec" | "Measured 12.7mm; spec 12.0 ± 0.2mm" |
| "High reject rate" | "Reject rate 4.2% vs. target 0.5%" |

**Why It Matters:** Quantification enables prioritization, trend analysis, and verification that corrective action was effective.

## 7. Copying Customer Description Verbatim

**The Problem:** Customer complaints often describe symptoms, not technical problems.

| Customer Says | Technical Problem Definition |
|---------------|------------------------------|
| "It doesn't work" | "Unit fails to power on; no LED indication" |
| "Makes a funny noise" | "Audible grinding noise from motor at >2000 RPM" |
| "Looks wrong" | "Surface discoloration in Zone A; no functional impact" |

**Why It Matters:** Customer language is subjective and often lacks technical detail needed for investigation.

## Self-Check Questions

Before finalizing a problem definition, ask:

1. Could someone read this and understand exactly what's wrong without my explanation?
2. Have I stated facts only, or have I included assumptions about cause?
3. Can the extent be measured and tracked?
4. Would the people involved feel safe contributing information?
5. Is this one bounded problem, or multiple issues combined?
