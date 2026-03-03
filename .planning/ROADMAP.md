# Roadmap: System Dev (AI-Assisted Systems Design Platform)

## Overview

This skill implements INCOSE system design (#3) as a Claude Code skill with a central Design Registry, domain agents, and traceability infrastructure. Each phase delivers a complete, verifiable capability. Cross-cutting requirements (XCUT-01..04) are enforced in every phase.

## Milestones

- ✅ **v1.0** — Phases 1-5 (shipped 2026-03-02) — Design Registry + ingestion + decomposition + interfaces + contracts + traceability + impact
- 🚧 **v1.1 Views & Diagrams** — Phases 6-9 (in progress) — Contextual view assembly + D2/Mermaid diagram generation

## Phases

<details>
<summary>v1.0 (Phases 1-5) — SHIPPED 2026-03-02</summary>

- [x] Phase 1: Design Registry Core + Skill Scaffold (3/3 plans) — completed 2026-02-28
- [x] Phase 2: Requirements Ingestion Pipeline (2/2 plans) — completed 2026-03-01
- [x] Phase 3: Structural Decomposition + Approval Gate (2/2 plans) — completed 2026-03-01
- [x] Phase 4: Interface Resolution + Behavioral Contracts (3/3 plans) — completed 2026-03-01
- [x] Phase 5: Traceability Weaving + Impact Analysis (3/3 plans) — completed 2026-03-01

See `.planning/milestones/v1.0-ROADMAP.md` for full phase details.

</details>

### v1.1 Views & Diagrams (In Progress)

**Milestone Goal:** Make design state visible through contextual views and D2/Mermaid diagrams

- [x] **Phase 6: View Assembly Core** - Construct contextual views from registry slot subsets with gap handling and snapshot consistency
- [ ] **Phase 7: View Quality & Handoff** - Relevance ranking, deterministic output, performance, and diagram-compatible handoff format
- [ ] **Phase 8: Diagram Generation Core** - D2 structural and Mermaid behavioral diagram generation from view data
- [ ] **Phase 9: Diagram Templates & Quality** - Template-driven generation with abstraction layers, determinism, and logging

## Phase Details

### Phase 6: View Assembly Core
**Goal**: Users can assemble contextual views from registry slot subsets that honestly represent design state including gaps
**Depends on**: Phase 5 (existing SlotAPI and registry infrastructure)
**Requirements**: VIEW-01, VIEW-02, VIEW-05, VIEW-06, VIEW-07, VIEW-08, VIEW-10
**Success Criteria** (what must be TRUE):
  1. View assembler constructs a contextual view from a subset of registry slots on demand, without creating a separate source of truth
  2. Views contain gap indicators for unpopulated or missing slots rather than failing with errors
  3. Views are assembled from a single consistent registry snapshot (no mid-assembly state changes)
  4. View compositions are defined via declarative view-specification configs, not hardcoded logic
  5. Assembling a view does not modify or delete existing slots outside the view type
**Plans**: 3 plans

Plans:
- [x] 06-01-PLAN.md — View schemas, scope pattern matcher, snapshot reader, gap builder
- [x] 06-02-PLAN.md — View assembler engine, built-in specs, command file, tree renderer
- [x] 06-03-PLAN.md — Gap closure: add view-spec schema validation to load_view_spec()

### Phase 7: View Quality & Handoff
**Goal**: Views are ranked by relevance, deterministic, performant, and produce output that diagram generation can consume
**Depends on**: Phase 6
**Requirements**: VIEW-03, VIEW-04, VIEW-09, VIEW-11, VIEW-12
**Success Criteria** (what must be TRUE):
  1. View assembler returns relevance-ranked results when retrieving slots for contextual views
  2. View assembler outputs a defined handoff format that diagram-renderer can consume without transformation
  3. Given identical registry state and view-spec, the view assembler produces byte-identical output
  4. View assembly operations emit structured log entries with operation type, slot counts, and timing
**Plans**: TBD

Plans:
- [ ] 07-01: TBD
- [ ] 07-02: TBD

### Phase 8: Diagram Generation Core
**Goal**: Users can generate valid D2 structural and Mermaid behavioral diagrams from view output, with gap markers rendered as placeholders
**Depends on**: Phase 7 (view handoff format must exist)
**Requirements**: DIAG-01, DIAG-02, DIAG-03, DIAG-04, DIAG-06, DIAG-09
**Success Criteria** (what must be TRUE):
  1. Diagram generator produces syntactically valid D2 source for structural diagrams from view data
  2. Diagram generator produces syntactically valid Mermaid source for behavioral diagrams from view data
  3. Diagram generator reads view handoff format and writes diagram slots through SlotAPI
  4. Gap markers in view input appear as visually distinct placeholder elements in diagram output
  5. Generating diagrams does not modify or delete existing slots outside the diagram type
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

### Phase 9: Diagram Templates & Quality
**Goal**: Diagram generation is template-driven with configurable abstraction layers, deterministic output, and structured logging
**Depends on**: Phase 8
**Requirements**: DIAG-05, DIAG-07, DIAG-08, DIAG-10
**Success Criteria** (what must be TRUE):
  1. Diagram generator supports hierarchical abstraction layers (e.g., system-level vs component-level) for readability
  2. Diagram templates are loaded from a configurable template registry, not hardcoded
  3. Given identical view input, the diagram generator produces byte-identical output
  4. Diagram generation operations emit structured log entries with operation type, diagram format, and timing
**Plans**: TBD

Plans:
- [ ] 09-01: TBD
- [ ] 09-02: TBD

### Cross-Cutting: Applied in Every Phase

**Requirements**: XCUT-01, XCUT-02, XCUT-03, XCUT-04
**Enforcement**:
  1. XCUT-01 (Partial-state tolerance): Every agent produces partial output with gap markers on incomplete input
  2. XCUT-02 (Structured logging): Every agent operation produces structured log entries
  3. XCUT-03 (Externalizable rules): Sub-block configuration is externalized, not hardcoded
  4. XCUT-04 (Slot-api exclusivity): All agents access design state through SlotAPI, never direct file access

## Progress

**Execution Order:** Phases execute in numeric order: 6 -> 7 -> 8 -> 9

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Design Registry Core + Skill Scaffold | v1.0 | 3/3 | Complete | 2026-02-28 |
| 2. Requirements Ingestion Pipeline | v1.0 | 2/2 | Complete | 2026-03-01 |
| 3. Structural Decomposition + Approval Gate | v1.0 | 2/2 | Complete | 2026-03-01 |
| 4. Interface Resolution + Behavioral Contracts | v1.0 | 3/3 | Complete | 2026-03-01 |
| 5. Traceability Weaving + Impact Analysis | v1.0 | 3/3 | Complete | 2026-03-01 |
| 6. View Assembly Core | v1.1 | 3/3 | Complete | 2026-03-03 |
| 7. View Quality & Handoff | v1.1 | 0/TBD | Not started | - |
| 8. Diagram Generation Core | v1.1 | 0/TBD | Not started | - |
| 9. Diagram Templates & Quality | v1.1 | 0/TBD | Not started | - |
