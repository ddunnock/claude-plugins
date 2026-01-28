# IS / IS NOT Analysis

IS/IS NOT analysis (from Kepner-Tregoe methodology) sharpens problem boundaries by explicitly stating what the problem IS and what it IS NOT across multiple dimensions. The contrast between IS and IS NOT often reveals critical clues for root cause analysis.

## Core Concept

For each dimension, ask:
- **IS:** What is actually observed or affected?
- **IS NOT:** What could logically be affected but is not?

The gap between IS and IS NOT narrows the investigation scope and eliminates potential causes that don't fit the pattern.

## Standard Template

| Dimension | IS | IS NOT |
|-----------|----|----|
| **What (Object)** | Which items/parts have the problem? | Which similar items do NOT have it? |
| **What (Defect)** | What specific defect is observed? | What other defects are NOT present? |
| **Where (Geographic)** | Where does the problem occur? | Where does it NOT occur? |
| **Where (On Object)** | Where on the item is the defect? | Where on the item is it NOT? |
| **When (First Observed)** | When was it first seen? | When was it NOT seen (before)? |
| **When (In Lifecycle)** | At what process stage? | At what stages is it NOT seen? |
| **Extent** | How many are affected? | How many are NOT affected? |

## Example: Connector Housing Cracks

| Dimension | IS | IS NOT |
|-----------|----|----|
| **What (Object)** | Connector housing P/N 12345 | Connector pins, cable assembly, other housings |
| **What (Defect)** | Cracked | Discolored, deformed, dimensionally out of spec |
| **Where (Geographic)** | Final assembly station 3 | Stations 1, 2, or field returns |
| **Where (On Object)** | Locking tab area | Body, mounting flange, terminals |
| **When (First Observed)** | Week 12 production | Prior to Week 12 |
| **When (In Lifecycle)** | During torque verification | During installation or field operation |
| **Extent** | 12 of 400 units (3%) | Remaining 388 units (97%) unaffected |

## Analytical Value

The IS/IS NOT analysis enables:

**Distinction Testing:** A potential cause is more likely if it explains both what IS happening AND what IS NOT happening. If a hypothesis explains the IS but not the IS NOT, it's less likely to be the root cause.

**Boundary Definition:** Clearly defines investigation scope — focus resources on Week 12 production at Station 3, not entire production history.

**Pattern Recognition:** The contrast often reveals the distinguishing factor. Example: "Station 3 only" might point to equipment, tooling, or operator unique to that station.

**Misunderstanding Elimination:** Sometimes reveals the problem doesn't exist as described, or belongs to a different entity (wrong supplier blamed, wrong part suspected).

## Tips for Effective IS/IS NOT

1. **Be specific:** "Lot #2310" not "recent lots"
2. **Include negatives:** The IS NOT column is as important as IS
3. **Challenge assumptions:** Verify claims before recording
4. **Look for sharp contrasts:** The most useful patterns have clear boundaries
5. **Update as data emerges:** IS/IS NOT evolves during investigation

## Common Mistakes

- Leaving IS NOT column blank or vague
- Recording assumptions as facts
- Mixing cause hypotheses into the description
- Failing to verify whether IS NOT cases truly exist
