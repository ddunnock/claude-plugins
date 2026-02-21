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

Each rule follows this format: ID, Name, Characteristic, Detection Tier, Description, Violation Example, Correction Example.

### R2: Use Active Voice (C2 - Appropriateness)
- **Tier:** 1 (Deterministic)
- **Description:** Requirements shall use active voice. Passive constructions obscure the responsible actor and create ambiguity about who/what performs the action.
- **Detection:** Regex for passive voice patterns (is/are/was/were/be/been/being + past participle). Whitelist for acceptable passive phrases (e.g., "is defined as", "is required").
- **Violation:** "The data shall be encrypted before transmission."
- **Correction:** "The system shall encrypt the data before transmission."

### R7: Avoid Vague Terms (C3 - Unambiguity)
- **Tier:** 1 (Deterministic)
- **Description:** Requirements shall not contain vague or subjective terms that allow multiple interpretations. Each term must be measurable or precisely defined.
- **Detection:** String matching against `data/vague_terms.json` word list.
- **Violation:** "The system shall provide adequate performance under normal operating conditions."
- **Correction:** "The system shall respond to API requests within 200ms at the 95th percentile under loads up to 1,000 concurrent users."

### R8: Avoid Escape Clauses (C3 - Unambiguity)
- **Tier:** 1 (Deterministic)
- **Description:** Requirements shall not contain escape clauses that provide loopholes for non-compliance. Escape clauses weaken the binding nature of requirements.
- **Detection:** String matching against `data/escape_clauses.json` phrase list.
- **Violation:** "The system shall encrypt data where possible."
- **Correction:** "The system shall encrypt all data at rest using AES-256."

### R19: Avoid Combinators (C5 - Singular)
- **Tier:** 1 (Deterministic)
- **Description:** Each requirement shall address a single capability. Combinators (and, or, but, as well as, in addition to) indicate multiple requirements bundled together. Exception: "and" connecting items in a list of the same type is acceptable.
- **Detection:** Regex for restricted combinators with context-aware exceptions.
- **Violation:** "The system shall authenticate users and log all access attempts."
- **Correction:** Split into: "The system shall authenticate users via OAuth 2.0." and "The system shall log all access attempts with timestamp and source IP."

### R1: Necessary (C1 - Necessity)
- **Tier:** 2 (LLM)
- **Description:** Every requirement must be traceable to a higher-level need or stakeholder goal. If a requirement cannot be traced, it may be unnecessary or the parent need is missing.
- **Detection:** Semantic analysis -- LLM checks whether the requirement's rationale connects to a documented need.
- **Violation:** "The system shall use a blue color scheme for the dashboard." (no stakeholder need for color scheme)
- **Correction:** Either trace to a need ("NEED-042: Operators need clear visual distinction between status levels") or remove.

### R22: Verifiable (C8 - Verifiability)
- **Tier:** 2 (LLM)
- **Description:** Every requirement must be stated in a way that allows objective verification. Quantitative requirements need thresholds; qualitative requirements need observable criteria.
- **Detection:** Semantic analysis -- LLM evaluates whether a clear test or analysis method exists.
- **Violation:** "The system shall be user-friendly."
- **Correction:** "The system shall achieve a System Usability Scale (SUS) score of 70 or higher when evaluated by 10 representative users."

<!-- Remaining rules to be populated with full INCOSE GtWR v4 rule set in section-05 -->

## Few-Shot Examples for LLM Tier

Examples for calibrating the quality-checker agent's semantic analysis.

### Example 1: Multiple violations
**Input:** "The system should provide fast response times where possible."
**Expected violations:**
- R7 (vague term: "fast")
- R8 (escape clause: "where possible")
- R22 (not verifiable: no measurable threshold)
**Expected correction:** "The system shall respond to user input within 100ms at the 99th percentile."

### Example 2: Singular violation
**Input:** "The system shall authenticate users and encrypt all data at rest."
**Expected violations:**
- R19 (combinator: "and" joins two distinct capabilities)
**Expected correction:** Split into two requirements.

### Example 3: Clean requirement
**Input:** "The system shall process payment transactions within 2 seconds at the 95th percentile under loads up to 500 concurrent transactions."
**Expected violations:** None
**Rationale:** Specific actor (system), measurable threshold (2s), defined conditions (95th percentile, 500 concurrent).

<!-- Additional few-shot examples to be added in section-05 -->
