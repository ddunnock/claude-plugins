# Requirements: System Dev v1.1 — Views & Diagrams

**Defined:** 2026-03-02
**Core Value:** Design decisions captured as explicit, reviewable, traceable records in a Design Registry

## v1.1 Requirements

Requirements for making design state visible through contextual views and diagrams. Each maps to roadmap phases and references upstream REQ-IDs from the requirements specification.

### View Assembly

- [ ] **VIEW-01**: View assembler constructs contextual views from registry slot subsets on demand without persisting as separate source of truth *(REQ-058, REQ-354)*
- [ ] **VIEW-02**: View assembler produces honest gap indicators for unpopulated slots rather than errors *(REQ-059, REQ-355)*
- [ ] **VIEW-03**: View assembler supports relevance-ranked retrieval for contextual views *(REQ-060)*
- [ ] **VIEW-04**: View assembler outputs views in a defined handoff format compatible with diagram-renderer *(REQ-061)*
- [ ] **VIEW-05**: View assembler reads/writes design state exclusively through SlotAPI *(REQ-062, REQ-077, REQ-357)*
- [ ] **VIEW-06**: View assembler produces view slots conforming to registered view schema *(REQ-087)*
- [ ] **VIEW-07**: View assembler constructs views from a single consistent registry snapshot *(REQ-428)*
- [ ] **VIEW-08**: View compositions defined as declarative view-specifications *(REQ-448, REQ-356)*
- [ ] **VIEW-09**: View assembler produces deterministic output for same input state *(REQ-108, REQ-128, REQ-359)*
- [ ] **VIEW-10**: View assembler preserves existing slots outside view type during execution *(REQ-118)*
- [ ] **VIEW-11**: View assembler emits structured log entries for assembly operations *(REQ-140, REQ-358)*
- [ ] **VIEW-12**: View assembler meets performance target for contextual view assembly *(REQ-401)*

### Diagram Generation

- [ ] **DIAG-01**: Diagram generator produces valid D2 structural diagrams from view data *(REQ-063, REQ-370)*
- [ ] **DIAG-02**: Diagram generator produces valid Mermaid behavioral diagrams from view data *(REQ-063, REQ-371)*
- [ ] **DIAG-03**: Diagram generator accepts view handoff format and writes diagram slots via SlotAPI *(REQ-065, REQ-373, REQ-078)*
- [ ] **DIAG-04**: Diagram generator produces diagram slots conforming to registered diagram schema *(REQ-088, REQ-374)*
- [ ] **DIAG-05**: Diagram generator supports hierarchical abstraction layers for readability *(REQ-064)*
- [ ] **DIAG-06**: Diagram generator creates placeholder elements for gap markers in view input *(REQ-097, REQ-131, REQ-372)*
- [ ] **DIAG-07**: Diagram generator loads templates from a configurable template registry *(REQ-436)*
- [ ] **DIAG-08**: Diagram generator produces deterministic output for same input state *(REQ-106, REQ-126)*
- [ ] **DIAG-09**: Diagram generator preserves existing slots outside diagram type during execution *(REQ-116)*
- [ ] **DIAG-10**: Diagram generator emits structured log entries for generation operations *(REQ-137, REQ-375)*

## Future Requirements

Deferred to subsequent milestones.

### Risk & Governance
- Risk registry with composite scoring and FMEA (risk-registry block — 14 reqs)
- Volatility tracking with stability metrics (volatility-tracker block — 11 reqs)
- Coherence reviewer for cross-concern consistency checking (coherence-reviewer block — 9 reqs)

### Orchestration
- Chief-systems-engineer orchestration and coherence review (chief-systems-engineer block — 20 reqs)
- Milestone gating and agent resilience

## Out of Scope

| Feature | Reason |
|---------|--------|
| SVG/PNG rendering | D2/Mermaid source output only; rendering is external tooling concern |
| Interactive diagrams | CLI skill produces text artifacts, not UI |
| Real-time diagram updates | Diagrams generated on-demand, not live-updating |
| Cross-skill diagram federation | Design state is local to this skill's registry |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| VIEW-01 | — | Pending |
| VIEW-02 | — | Pending |
| VIEW-03 | — | Pending |
| VIEW-04 | — | Pending |
| VIEW-05 | — | Pending |
| VIEW-06 | — | Pending |
| VIEW-07 | — | Pending |
| VIEW-08 | — | Pending |
| VIEW-09 | — | Pending |
| VIEW-10 | — | Pending |
| VIEW-11 | — | Pending |
| VIEW-12 | — | Pending |
| DIAG-01 | — | Pending |
| DIAG-02 | — | Pending |
| DIAG-03 | — | Pending |
| DIAG-04 | — | Pending |
| DIAG-05 | — | Pending |
| DIAG-06 | — | Pending |
| DIAG-07 | — | Pending |
| DIAG-08 | — | Pending |
| DIAG-09 | — | Pending |
| DIAG-10 | — | Pending |

**Coverage:**
- v1.1 requirements: 22 total
- Mapped to phases: 0
- Unmapped: 22 (pending roadmap creation)

**Upstream REQ-ID mapping:** 38 upstream requirements consolidated into 22 GSD requirements

---
*Requirements defined: 2026-03-02*
*Last updated: 2026-03-02 after initial definition*
