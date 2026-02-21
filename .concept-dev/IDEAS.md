# Ideas — Requirements Development Plugin (requirements-dev)

**Session:** 1f45143f
**Date:** 2026-02-20
**Phase:** Spit-Ball (Phase 1)

---

## Selected Themes

### Theme A: Needs Extraction & Formalization

**Energy Level:** high

| # | Idea | Feasibility | Notes |
|---|------|-------------|-------|
| 1 | Read concept-dev outputs (CONCEPT-DOCUMENT, BLACKBOX, SOLUTION-LANDSCAPE) as starting material | PRECEDENT_FOUND | Standard INCOSE NRM Section 4 process; concept-dev artifacts map to NRM inputs |
| 2 | Extract stakeholder needs from problem statement and enabled capabilities | PRECEDENT_FOUND | INCOSE needs = formal transformation of lifecycle concepts into expectations |
| 3 | Formalize into INCOSE-compliant need statements using GtWR v4 patterns | PRECEDENT_FOUND | Pattern-based need writing per R1; tools like Innoslate already do this |
| 4 | User reviews/refines each need; gate before proceeding to requirements | PRECEDENT_FOUND | Standard INCOSE practice — needs verification (NRM 5.1.2) |

**Connections:** Feeds directly into Theme B (requirements transformation). Traceability links established here flow through all downstream themes.

---

### Theme B: Requirements Transformation (Needs to Design Input Requirements)

**Energy Level:** high

| # | Idea | Feasibility | Notes |
|---|------|-------------|-------|
| 1 | Guided type-by-type transformation: functional, performance, interface/API, constraint, quality | PRECEDENT_FOUND | INCOSE NRM 6.2.1.2 "Considerations for Each Type of Requirement" |
| 2 | LLM seeds initial requirements from needs + architecture + research; user refines | NEEDS_INVESTIGATION | Skeptic flagged: no deterministic mapping exists; must be "seed with refinement" |
| 3 | 13 mandatory INCOSE attributes per requirement (A1-A5, A6-A9, A15, A17, A19, A28-A29, A34-A36) | PRECEDENT_FOUND | INCOSE GtWR v4 summary sheet defines mandatory attributes with asterisk |
| 4 | TBD/TBR tracking for unresolved items carried from concept-dev gaps | PRECEDENT_FOUND | INCOSE NRM 6.2.1.5 "Managing Unknowns" explicitly covers this |
| 5 | JSON requirements registry with unique IDs and traceability to concept-dev | PRECEDENT_FOUND | Extends concept-dev's existing registry pattern (SRC-xxx, ASM-xxx) |

**Connections:** Depends on Theme A (needs must exist before requirements). Feeds Theme C (quality checks), Theme D (V&V), and Theme E (traceability).

---

### Theme C: Quality Assurance (Requirements Linting)

**Energy Level:** high

| # | Idea | Feasibility | Notes |
|---|------|-------------|-------|
| 1 | Automated checking of ~24 syntactic INCOSE rules (vague terms, escape clauses, combinators, passive voice, etc.) | PRECEDENT_FOUND | QRA Corp QVscribe automates 24 rules; well-established NLP patterns |
| 2 | LLM best-effort semantic checks for remaining rules (solution-free, completeness, correctness) flagged for human review | NEEDS_INVESTIGATION | No benchmark for LLM accuracy on full 42-rule set; must frame as assist-and-flag |
| 3 | Per-requirement quality report with specific rule violations and suggested rewrites | PRECEDENT_FOUND | Innoslate and SPEC Innovations provide similar feedback |
| 4 | Set-level consistency/completeness checks (characteristics C10-C15) | NEEDS_INVESTIGATION | Requires cross-requirement analysis; LLM can assist but human review needed |
| 5 | Skeptic agent validates claims made during requirement writing (same pattern as concept-dev) | PRECEDENT_FOUND | Reuses concept-dev skeptic agent pattern |

**Connections:** Runs against Theme B output. Informs Theme E deliverable quality. Skeptic from concept-dev carries forward.

---

### Theme D: V&V Strategy Planning

**Energy Level:** high

| # | Idea | Feasibility | Notes |
|---|------|-------------|-------|
| 1 | Each requirement gets verification method (test, analysis, inspection, demonstration) | PRECEDENT_FOUND | Standard INCOSE practice; attributes A6-A9 are mandatory |
| 2 | Verification success criteria defined alongside requirement | PRECEDENT_FOUND | INCOSE A6 — explicitly required |
| 3 | Verification matrix as a deliverable (requirement x method x criteria) | PRECEDENT_FOUND | Standard SE artifact |
| 4 | Software-focused V&V: unit test, integration test, system test, code review, static analysis | PRECEDENT_FOUND | IEEE 29148 and INCOSE SaSIWG address software V&V |

**Connections:** Attached to each requirement from Theme B. Feeds into Theme E deliverables.

---

### Theme E: Traceability & Deliverables

**Energy Level:** high

| # | Idea | Feasibility | Notes |
|---|------|-------------|-------|
| 1 | Bidirectional traceability matrix (needs <- requirements -> V&V) | PRECEDENT_FOUND | INCOSE NRM 6.2.2; data modeling with JSON IDs |
| 2 | Requirements specification document structured per INCOSE R42 | PRECEDENT_FOUND | Template-based generation, same pattern as concept-dev deliverables |
| 3 | JSON registry for machine consumption by downstream tools | PRECEDENT_FOUND | Extends concept-dev registry pattern |
| 4 | Links back to concept-dev source_registry and assumption_registry | PRECEDENT_FOUND | Cross-workspace references via file paths and IDs |

**Connections:** Aggregates all other themes into deliverable artifacts. Terminal output of the skill.

---

### Theme F: Subsystem Decomposition (with Full Rigor)

**Energy Level:** high

| # | Idea | Feasibility | Notes |
|---|------|-------------|-------|
| 1 | Dedicated /reqdev:decompose command with its own agent | NEEDS_INVESTIGATION | Plugin can scaffold; engineering judgment must come from user |
| 2 | Functional decomposition phase: break system blocks into sub-functions guided by user | PRECEDENT_FOUND | INCOSE NRM 6.4; BLACKBOX.md already has functional blocks |
| 3 | Per-block allocation with budgeting rationale documented by user | NEEDS_INVESTIGATION | No LLM precedent for automated allocation; scaffolding feasible |
| 4 | Child requirements with trace to parent (INCOSE attribute A2) | PRECEDENT_FOUND | Standard traceability pattern |
| 5 | Gate checks before and after decomposition | PRECEDENT_FOUND | Same gate pattern as concept-dev |
| 6 | Skeptic review of decomposition completeness claims | NOVEL | Extends skeptic pattern to allocation/decomposition domain |

**Connections:** Optional phase after system-level requirements baselined (Theme B gate). Produces child requirements that feed back into Themes C, D, E.

---

## Deferred Ideas

| # | Idea | Theme (if any) | Reason Deferred |
|---|------|----------------|-----------------|
| 1 | Hardware/mixed-system support | B | User specified software-only focus |
| 2 | Automated performance budgeting (weight, power, cost) | F | Requires engineering judgment beyond LLM capability; software-only scope |
| 3 | Integration with external RM tools (DOORS, Jama, Innoslate) | E | Future scope; plugin should be self-contained first |
| 4 | Shared .concept-dev/ workspace | E | Deferred in favor of separate .requirements-dev/ for independence; can refactor later |

---

## Feasibility Research Notes

| Idea | Search Context | Finding | Confidence |
|------|---------------|---------|------------|
| AI-assisted INCOSE requirements writing | "INCOSE requirements management tools AI-assisted" | Tools like Innoslate, SPEC Innovations, QVscribe already use LLMs trained on GtWR v4 | HIGH |
| Automated INCOSE rule checking | QRA Corp QVscribe research | Only ~24 of 42 rules automatable via NLP; semantic rules need human review | HIGH |
| LLM requirements transformation | Skeptic review of commercial tools | No tool performs fully automated needs-to-requirements transformation; all require human input | MEDIUM |
| Software + INCOSE compatibility | INCOSE SaSIWG, Visure Solutions | INCOSE explicitly supports cross-domain including software; IEEE 29148 compatible | HIGH |

---

## Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| LLM can reliably apply all 42 INCOSE rules | DISPUTED | Commercial tools automate ~24 rules, cap at 78%. Reframe as "assist and flag" |
| Concept-dev outputs can be formally transformed to INCOSE requirements | UNVERIFIED_CLAIM | Outputs are starting material, not deterministic input. "Seed with user refinement" |
| Bidirectional traceability in JSON registries | VERIFIED | Structurally sound; operational discipline is the real risk |
| Quality scoring against 42 rules provides actionable feedback | DISPUTED | Syntactic rules (~24) yes; semantic rules produce best-effort suggestions needing review |
| V&V strategy at requirements time | VERIFIED | Standard INCOSE practice, not novel |
| Subsystem decomposition feasible in plugin | UNVERIFIED_CLAIM | Scaffolding feasible; automated allocation not demonstrated. Reframed with full rigor |
| Software-only focus compatible with INCOSE | VERIFIED | INCOSE is domain-agnostic by design; SaSIWG addresses software specifically |

---

**Next Phase:** Problem Definition (`/concept:problem`)
