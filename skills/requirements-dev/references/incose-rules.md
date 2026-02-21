# INCOSE GtWR v4 Rule Definitions

Reference document containing all 42 INCOSE Guide to Writing Requirements (GtWR) v4 rule definitions organized by characteristic.

## Characteristics

### Necessity (C1)
Rules ensuring every requirement is needed and traceable to a higher-level need.

### Appropriateness (C2)
Rules ensuring requirements use correct language constructs and avoid ambiguity patterns.

### Unambiguity (C3)
Rules ensuring each requirement has exactly one interpretation.

### Completeness (C4)
Rules ensuring requirements contain all necessary information.

### Singular (C5)
Rules ensuring each requirement addresses a single capability or constraint.

### Conformance (C6)
Rules ensuring requirements follow organizational standards.

### Feasibility (C7)
Rules ensuring requirements are technically achievable.

### Verifiability (C8)
Rules ensuring requirements can be objectively tested or measured.

### Correctness (C9)
Rules ensuring requirements accurately reflect stakeholder intent.

## Detection Tiers

| Tier | Method | Rules |
|------|--------|-------|
| Tier 1 (Deterministic) | Regex/string matching | R2, R7, R8, R9, R10, R15, R16, R17, R19, R20, R21, R24, R26, R32, R33, R35, R40 + 4 more |
| Tier 2 (LLM) | Semantic analysis with CoT | R1, R3, R5, R6, R11, R12, R14, R22, R34 |
| Tier 3 (Manual) | Human review | Remaining rules requiring domain expertise |

## Rule Definitions

<!-- Each rule to be defined with: ID, Name, Characteristic, Tier, Description, Violation Example, Correction Example -->
<!-- Content to be populated with full INCOSE GtWR v4 rule set -->

## Few-Shot Examples for LLM Tier

<!-- 12-20 validated examples for quality-checker agent calibration -->
<!-- Each example: requirement text, expected violations, expected corrections -->
