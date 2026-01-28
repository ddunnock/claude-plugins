# Problem Definition Examples

## Example 0: Elicitation Conversation Flow

This example shows how to use `AskUserQuestion` to iteratively gather information from a user who provides incomplete initial data.

### Turn 1 — User Initiates

**User:** "We're getting customer complaints about our connectors. Can you help me write up a problem definition?"

**Agent Response:**

I'll help you develop a structured problem definition using 5W2H methodology. Let me gather some key information first.

**WHAT: Object Identification**
What is the specific part number or product name for these connectors?

_Context: Precise identification prevents confusion with similar items._

Examples of useful answers:
- "Connector housing P/N 12345-A, Rev C"
- "Model X automotive connector, all variants"

**WHAT: Defect Description**
What specifically is wrong? What are customers reporting — failures, defects, or deviations from expected behavior?

_Context: Technical, measurable descriptions enable root cause analysis._

---

### Turn 2 — User Provides Partial Data

**User:** "It's the P/N CON-5500 series. Customers are saying they're cracking during assembly."

**Agent Response:**

Good — we have the object (P/N CON-5500 series) and a defect description (cracking during assembly). Let me get some additional details.

**HOW MUCH: Quantity**
How many units are affected? What's the total shipped or inspected population?

_Context: Quantification enables rate calculation and prioritization._

Examples of useful answers:
- "12 complaints from ~5,000 shipped units"
- "47 of 500 units in customer lot"

**WHERE: Location on Object**
Where on the connector is the cracking occurring? (Specific feature, area, or zone?)

_Context: Physical location may point to specific design features or manufacturing operations._

**WHEN: First Observed**
When did customers first report this issue? Is this recent or ongoing?

_Context: Timing helps correlate with process changes or material lots._

---

### Turn 3 — User Responds with Details

**User:** "We've had 15 complaints in the last month from about 10,000 units shipped. The cracks are at the locking tab area. First complaint came in around October 10th."

**Agent Response:**

Excellent detail. Now let me clarify the boundaries to complete the IS/IS NOT analysis.

**IS/IS NOT: Object**
Does this affect all CON-5500 variants, or specific ones only? Are other connector part numbers (CON-5400, CON-5600, etc.) unaffected?

_Context: Understanding what IS NOT affected helps narrow root cause._

**WHERE: Detection Point**
Where are customers when they discover this — during their incoming inspection, during their assembly process, or in field use?

_Context: Detection point indicates when in their process the defect manifests._

---

### Turn 4 — User Completes Data

**User:** "It's only the CON-5500-BLK variant — the white and gray versions seem fine. Customers find the cracks during their assembly operation when they're torquing the connector onto the housing."

**Agent Response:**

I now have enough information to generate your problem definition.

### 5W2H Summary

| Element | Finding |
|---------|---------|
| **What (Object)** | Connector P/N CON-5500-BLK (black variant only) |
| **What (Defect)** | Cracking at locking tab area |
| **Where (Geographic)** | Customer assembly operations |
| **Where (On Object)** | Locking tab area |
| **When (First Observed)** | ~10 October 2025 |
| **When (In Lifecycle)** | During customer assembly (torque application) |
| **Who** | Multiple customers |
| **How** | Discovered during assembly operation |
| **How Much** | 15 complaints from ~10,000 shipped (0.15%) |

### IS / IS NOT Analysis

| Dimension | IS | IS NOT |
|-----------|----|----|
| **What (Object)** | CON-5500-BLK (black variant) | CON-5500-WHT, CON-5500-GRY, other connector families |
| **What (Defect)** | Cracking | Other defect types not reported |
| **Where (On Object)** | Locking tab area | Body, terminals, other features |
| **When (First Observed)** | October 2025 shipments | Prior months (to be verified) |
| **Extent** | 15 of ~10,000 (0.15%) | Remaining ~9,985 units |

### Problem Statement

> Connector P/N CON-5500-BLK (black variant) exhibited cracking at the locking tab area during customer assembly operations (torque application), detected starting ~10 October 2025. 15 customer complaints received from approximately 10,000 units shipped (0.15%). White and gray variants (CON-5500-WHT, CON-5500-GRY) not affected.

### Validation ✓

- [x] No assumed cause embedded
- [x] No solution embedded  
- [x] Defect described with measurable terms
- [x] Extent quantified
- [x] Detection method stated
- [x] Scope bounded (IS/IS NOT completed)

---

## Example 1: Manufacturing Defect — Weld Quality

### Raw Input
Customer complaint: "Seat bracket welds look bad and feel loose."

### 5W2H Analysis

| Element | Finding |
|---------|---------|
| **What (Object)** | LH Seat-Frame Bracket, P/N SFB-2024-L |
| **What (Defect)** | Weld spatter present; incomplete fusion on joint; joint movement under hand pressure |
| **Where (Geographic)** | Detected at customer assembly line, OEM Plant B |
| **Where (On Object)** | MIG weld joint connecting bracket to seat frame |
| **When (First Observed)** | 15 October 2025, incoming inspection |
| **When (In Lifecycle)** | Post-shipment, during customer receiving inspection |
| **Who** | Customer QC inspector during torque tightening operation |
| **How** | Visual inspection (spatter); tactile check (joint movement) |
| **How Much** | 40 pcs nonconforming of 2,000 pcs in Lot #2310 (2.0%) |

### IS / IS NOT Analysis

| Dimension | IS | IS NOT |
|-----------|----|----|
| **What (Object)** | LH Seat-Frame Bracket | RH Bracket, other seat components |
| **What (Defect)** | Weld spatter, incomplete fusion | Porosity, undercut, dimensional deviation |
| **Where (Geographic)** | Welding Line 2, Shift B | Welding Lines 1, 3; Shifts A, C |
| **Where (On Object)** | Primary weld joint | Secondary welds, bracket body |
| **When (First Observed)** | Lot #2310, produced Week 42 | Prior lots, subsequent lots |
| **When (In Lifecycle)** | Customer receiving | In-process, final inspection |
| **Extent** | 40 of 2,000 (2.0%) | Remaining 1,960 (98%) acceptable |

### Problem Statement

> LH Seat-Frame Bracket (P/N SFB-2024-L) exhibited weld spatter and incomplete fusion at the primary MIG weld joint, detected by customer receiving inspection at OEM Plant B on 15 October 2025. Defects originated from Welding Line 2, Shift B, Lot #2310. 40 of 2,000 pieces (2.0%) found nonconforming. Potential risk of joint failure under load.

---

## Example 2: Field Failure — Electronic Component

### Raw Input
Field report: "Controller board randomly stops working."

### 5W2H Analysis

| Element | Finding |
|---------|---------|
| **What (Object)** | Power Controller Board, P/N PCB-5500-R3 |
| **What (Defect)** | Intermittent loss of output; board becomes unresponsive; requires power cycle to recover |
| **Where (Geographic)** | Field installations in Southeast region |
| **Where (On Object)** | Output stage circuitry (preliminary) |
| **When (First Observed)** | First report: 3 August 2025; 12 additional reports through 15 September 2025 |
| **When (In Lifecycle)** | After 6-18 months of field operation |
| **Who** | End users; service technicians during maintenance |
| **How** | Loss of system function; confirmed by bench test at service center |
| **How Much** | 13 confirmed failures from population of ~2,400 deployed units (0.54%) |

### IS / IS NOT Analysis

| Dimension | IS | IS NOT |
|-----------|----|----|
| **What (Object)** | PCB-5500-R3 | Earlier revisions R1, R2; other system boards |
| **What (Defect)** | Intermittent output loss, recoverable by power cycle | Permanent failure, smoke/burn damage, boot failure |
| **Where (Geographic)** | Southeast region (high humidity) | Northeast, Midwest, West Coast regions |
| **Where (On Object)** | Output stage area | Input stage, processor section, power supply |
| **When (First Observed)** | Units shipped Q1 2024 | Units shipped Q3-Q4 2024 |
| **When (In Lifecycle)** | 6-18 months after installation | During commissioning, first 6 months |
| **Extent** | 13 of ~2,400 units (0.54%) | Remaining ~2,387 units no reported failures |

### Problem Statement

> Power Controller Board (P/N PCB-5500-R3) exhibits intermittent loss of output requiring power cycle to recover. Failures occur in Southeast region field installations after 6-18 months of operation. 13 confirmed failures from ~2,400 deployed units (0.54%), all from Q1 2024 shipments. Output stage circuitry implicated based on preliminary bench test.

---

## Example 3: Process Deviation — Dimensional Nonconformance

### Raw Input
Inspection hold: "Shafts measuring out of spec."

### 5W2H Analysis

| Element | Finding |
|---------|---------|
| **What (Object)** | Drive Shaft, P/N DS-7890 |
| **What (Defect)** | Outer diameter 25.12mm; specification requires 25.00 ± 0.05mm |
| **Where (Geographic)** | CNC Lathe #4, Cell B |
| **Where (On Object)** | Journal diameter, Feature D per drawing |
| **When (First Observed)** | 22 October 2025, 14:30 shift |
| **When (In Lifecycle)** | In-process inspection after turning operation |
| **Who** | Operator self-inspection; confirmed by QC |
| **How** | Micrometer measurement per control plan |
| **How Much** | 8 consecutive parts out of tolerance; 23 total in shift production suspect |

### IS / IS NOT Analysis

| Dimension | IS | IS NOT |
|-----------|----|----|
| **What (Object)** | DS-7890 Drive Shaft | Other shaft part numbers on same machine |
| **What (Defect)** | OD oversize (+0.12mm) | Undersize, surface finish deviation, runout |
| **Where (Geographic)** | CNC Lathe #4 only | Lathes #1, #2, #3 |
| **Where (On Object)** | Feature D (journal diameter) | Features A, B, C, E |
| **When (First Observed)** | 22 October, 14:30 shift | Morning shift, previous days |
| **When (In Lifecycle)** | After turning operation 20 | Prior operations, final inspection |
| **Extent** | 8 confirmed, 23 suspect | ~150 prior parts in compliance |

### Problem Statement

> Drive Shaft (P/N DS-7890) outer diameter at Feature D measures 25.12mm, exceeding specification of 25.00 ± 0.05mm by 0.07mm. Deviation detected by in-process inspection at CNC Lathe #4, Cell B, on 22 October 2025 during 14:30 shift. 8 parts confirmed out of tolerance; 23 parts in shift production under suspect hold.

---

## Template for New Problem Definitions

### 5W2H Capture

| Element | Finding |
|---------|---------|
| **What (Object)** | |
| **What (Defect)** | |
| **Where (Geographic)** | |
| **Where (On Object)** | |
| **When (First Observed)** | |
| **When (In Lifecycle)** | |
| **Who** | |
| **How** | |
| **How Much** | |

### IS / IS NOT Analysis

| Dimension | IS | IS NOT |
|-----------|----|----|
| **What (Object)** | | |
| **What (Defect)** | | |
| **Where (Geographic)** | | |
| **Where (On Object)** | | |
| **When (First Observed)** | | |
| **When (In Lifecycle)** | | |
| **Extent** | | |

### Problem Statement

> [Object] exhibited [defect/failure mode] at [location] during [phase/operation], affecting [extent/quantity], detected by [method]. [Additional context as needed.]
