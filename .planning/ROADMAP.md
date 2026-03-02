# Roadmap: System Dev (AI-Assisted Systems Design Platform)

## Overview

This skill implements INCOSE system design (#3) as a Claude Code skill with a central Design Registry, domain agents, and traceability infrastructure. Each phase delivers a complete, verifiable capability. Cross-cutting requirements (XCUT-01..04) are enforced in every phase.

## Milestones

- ✅ **v1.0** — Phases 1-5 (shipped 2026-03-02) — Design Registry + ingestion + decomposition + interfaces + contracts + traceability + impact
- 📋 **Next** — Phases 6-7 (planned) — Views, diagrams, risk, volatility, orchestration

## Phases

<details>
<summary>✅ v1.0 (Phases 1-5) — SHIPPED 2026-03-02</summary>

- [x] Phase 1: Design Registry Core + Skill Scaffold (3/3 plans) — completed 2026-02-28
- [x] Phase 2: Requirements Ingestion Pipeline (2/2 plans) — completed 2026-03-01
- [x] Phase 3: Structural Decomposition + Approval Gate (2/2 plans) — completed 2026-03-01
- [x] Phase 4: Interface Resolution + Behavioral Contracts (3/3 plans) — completed 2026-03-01
- [x] Phase 5: Traceability Weaving + Impact Analysis (3/3 plans) — completed 2026-03-01

See `.planning/milestones/v1.0-ROADMAP.md` for full phase details.

</details>

### Next Milestone (TBD)

- [ ] **Phase 6: Views, Diagrams, Risk & Volatility** — Context-sensitive views, D2/Mermaid diagrams, risk scoring, FMEA, volatility tracking
  - Requirements: VIEW-01..03, DIAG-01..03, RISK-01..07
  - Plans: TBD

- [ ] **Phase 7: Orchestration + Coherence Review** — Chief-systems-engineer agent: multi-agent sequencing, coherence review, milestone gating, resilience
  - Requirements: ORCH-01..05
  - Plans: TBD

### Cross-Cutting: Applied in Every Phase

**Requirements**: XCUT-01, XCUT-02, XCUT-03, XCUT-04
**Enforcement**:
  1. XCUT-01 (Partial-state tolerance): Every agent produces partial output with gap markers on incomplete input
  2. XCUT-02 (Structured logging): Every agent operation produces structured log entries
  3. XCUT-03 (Externalizable rules): Sub-block configuration is externalized, not hardcoded
  4. XCUT-04 (Slot-api exclusivity): All agents access design state through SlotAPI, never direct file access

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Design Registry Core + Skill Scaffold | v1.0 | 3/3 | Complete | 2026-02-28 |
| 2. Requirements Ingestion Pipeline | v1.0 | 2/2 | Complete | 2026-03-01 |
| 3. Structural Decomposition + Approval Gate | v1.0 | 2/2 | Complete | 2026-03-01 |
| 4. Interface Resolution + Behavioral Contracts | v1.0 | 3/3 | Complete | 2026-03-01 |
| 5. Traceability Weaving + Impact Analysis | v1.0 | 3/3 | Complete | 2026-03-01 |
| 6. Views, Diagrams, Risk & Volatility | Next | 0/TBD | Not started | - |
| 7. Orchestration + Coherence Review | Next | 0/TBD | Not started | - |
