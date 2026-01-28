# Question Bank for Problem Definition Elicitation

Use these templates when invoking `AskUserQuestion` to gather 5W2H data. Adapt wording to context.

## WHAT Questions

### What (Object) — Identify the Item

**Initial identification:**
> **WHAT: Object Identification**
> What is the specific part number, product name, or system exhibiting this problem?
>
> _Context: Precise identification prevents confusion with similar items and ensures we're investigating the correct object._
>
> Examples of useful answers:
> - "Connector housing P/N 12345-A, Rev C"
> - "Drive shaft assembly, drawing 7890-001"
> - "Customer order #45678, SKU MAT-2024-BLK"

**Clarifying similar items:**
> **WHAT: Object Clarification**
> Are there similar part numbers or variants? Is this specific to one revision/version, or does it affect multiple?
>
> _Context: Distinguishing affected vs. unaffected variants helps bound the investigation._

### What (Defect) — Characterize the Failure

**Initial defect description:**
> **WHAT: Defect Description**
> What specifically is wrong? Describe the observable defect, failure mode, or deviation from expected behavior.
>
> _Context: Technical, measurable descriptions enable root cause analysis. Avoid subjective terms like "bad" or "doesn't work."_
>
> Examples of useful answers:
> - "Cracked at locking tab; crack length ~3mm, through-wall"
> - "Output voltage reads 4.2V; specification requires 5.0V ± 0.1V"
> - "Surface roughness Ra 3.2 µm; drawing calls out Ra 1.6 µm max"

**Probing vague descriptions:**
> **WHAT: Defect Clarification**
> You mentioned "[vague term]." Can you describe what you observe more specifically? What does it look like, measure, or behave like?
>
> _Context: Converting subjective observations into measurable terms enables verification._

**Distinguishing defect types:**
> **WHAT: Defect Boundary**
> Is the defect [specific type observed], or are other defect types also present (e.g., [list alternatives])?
>
> _Context: Understanding what defects ARE present vs. ARE NOT present helps focus investigation._

---

## WHERE Questions

### Where (Geographic) — Location of Detection/Origin

**Detection location:**
> **WHERE: Detection Point**
> Where was this problem detected? (Facility, production line, workstation, customer site, etc.)
>
> _Context: Detection point identifies who found it and under what conditions._
>
> Examples of useful answers:
> - "Final assembly station 3, Building A"
> - "Customer receiving inspection at OEM Plant B"
> - "Field service call at customer site in Phoenix"

**Origin location:**
> **WHERE: Origin Point**
> Where did the problem originate? Is the detection point the same as where the defect was created?
>
> _Context: Detection and origin may differ. A defect created in machining might be found in assembly._

**Boundary clarification:**
> **WHERE: Location Boundary**
> Does this problem occur at other locations? (Other lines, stations, facilities, regions?)
>
> _Context: Understanding where it IS NOT occurring helps narrow root cause._

### Where (On Object) — Physical Location on Item

**Location on part:**
> **WHERE: Location on Object**
> Where on the item is the defect located? (Feature, zone, surface, component area)
>
> _Context: Physical location on the object may point to specific manufacturing operations or design features._
>
> Examples of useful answers:
> - "Locking tab area, specifically the base radius"
> - "Weld joint between bracket and frame"
> - "Display connector pins 3 and 4"

---

## WHEN Questions

### When (Calendar) — Time of Observation

**First observation:**
> **WHEN: First Observed**
> When was this problem first observed? (Date, shift, time if known)
>
> _Context: Specific timing helps correlate with process changes, material lots, or personnel shifts._
>
> Examples of useful answers:
> - "First reported 15 October 2025, afternoon shift"
> - "Customer complaint received Week 42"
> - "Noticed during Monday morning startup"

**Pattern detection:**
> **WHEN: Temporal Pattern**
> Is there a pattern to when this occurs? (Specific shifts, days, seasons, after certain events?)
>
> _Context: Temporal patterns often correlate with process variables or environmental conditions._

### When (Lifecycle) — Point in Process/Lifecycle

**Process stage:**
> **WHEN: Process Stage**
> At what point in the manufacturing process, test sequence, or product lifecycle was this detected?
>
> _Context: Lifecycle stage indicates when the defect was created vs. when it was found._
>
> Examples of useful answers:
> - "During incoming inspection, before assembly"
> - "After 6 months of field operation"
> - "At torque verification step in final assembly"

---

## HOW Questions

### How (Detection Method)

**Detection method:**
> **HOW: Detection Method**
> How was this problem discovered? (Inspection type, test method, customer report, automated system?)
>
> _Context: Detection method affects data reliability and indicates whether this is a sampling or 100% inspection find._
>
> Examples of useful answers:
> - "Visual inspection per control plan CP-2024-001"
> - "Functional test failure — unit did not power on"
> - "Customer complaint via warranty return"

**Detection reliability:**
> **HOW: Detection Confidence**
> Was this detected through routine inspection, or discovered incidentally? How confident are we in the detection method?
>
> _Context: Incidental finds may indicate escape from normal detection; routine finds indicate control system caught it._

### How (Manifestation)

**Observable symptoms:**
> **HOW: Symptoms**
> What are the observable symptoms or behaviors? Is it intermittent or consistent?
>
> _Context: Understanding how the failure manifests helps characterize the failure mode._

---

## HOW MUCH Questions

### Extent and Magnitude

**Quantity affected:**
> **HOW MUCH: Quantity**
> How many units are affected? What is the total population or sample size inspected?
>
> _Context: Quantification enables rate calculation and prioritization._
>
> Examples of useful answers:
> - "12 defective of 400 inspected (3%)"
> - "47 of 500 units in lot (9.4%)"
> - "3 field failures from ~2,000 deployed"

**Probing vague quantities:**
> **HOW MUCH: Quantity Clarification**
> You mentioned "[vague term like 'several' or 'some']." Can you provide a specific count or estimate?
>
> _Context: Precise numbers enable trend analysis and verification of corrective action effectiveness._

**Severity/impact:**
> **HOW MUCH: Severity**
> What is the severity or impact? (Safety critical, functional impact, cosmetic only, customer impact level?)
>
> _Context: Severity classification drives prioritization and containment urgency._

**Lot/batch scope:**
> **HOW MUCH: Batch Scope**
> Which lots, batches, or serial number ranges are affected? Which are confirmed unaffected?
>
> _Context: Batch boundaries help scope containment and identify common factors._

---

## IS / IS NOT Clarification Questions

Use these to sharpen boundaries after initial data is gathered:

> **IS/IS NOT: Object**
> The problem affects [Object A]. Does it also affect [similar Object B]? Are [Object C, D] confirmed unaffected?

> **IS/IS NOT: Location**
> You mentioned this occurs at [Location X]. Does it also occur at [Location Y, Z]? Or is it specific to [Location X] only?

> **IS/IS NOT: Time**
> This started in [Time Period A]. Was this problem present before that? Have units from [Time Period B] been checked?

> **IS/IS NOT: Extent**
> Of the affected population, are certain subgroups more affected than others? (e.g., specific operators, machines, material lots?)

---

## Follow-Up Probes for Incomplete Answers

**When user says "I don't know":**
> That's okay — we'll record this as "Unknown — requires investigation." Is there someone who might have this information, or a data source we could check?

**When user gives vague answer:**
> Can you be more specific? For example, when you say "[vague term]," do you mean [interpretation A] or [interpretation B]?

**When user embeds cause in answer:**
> I notice you mentioned "[cause assumption]." For now, let's focus on describing what we observe. We'll investigate causes later. Can you describe the defect without reference to why it might have happened?
