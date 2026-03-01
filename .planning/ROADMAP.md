# Roadmap: System Dev (AI-Assisted Systems Design Platform)

## Overview

This skill implements INCOSE system design (#3) as a Claude Code skill with a central Design Registry, 6 domain agents, and an orchestrating chief-systems-engineer. The build follows a strict dependency chain: the Design Registry foundation first, then requirements ingestion, then domain agents layered in data-dependency order (decomposition, interfaces/contracts, traceability/impact), then presentation and orchestration on top. Each phase delivers a complete, verifiable capability. Cross-cutting requirements (XCUT-01..04) are enforced in every phase.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Design Registry Core + Skill Scaffold** - Foundation infrastructure: slot storage, schema validation, versioning, change journal, SKILL.md skeleton, plugin directory structure
- [ ] **Phase 2: Requirements Ingestion Pipeline** - Bridge from requirements-dev outputs into the Design Registry with delta detection and upstream schema handling
- [ ] **Phase 3: Structural Decomposition + Approval Gate** - First agent pattern: AI-driven component proposals with developer accept/reject/modify workflow
- [ ] **Phase 4: Interface Resolution + Behavioral Contracts** - Design triad completion: component boundary contracts, behavioral obligations, and V&V planning
- [ ] **Phase 5: Traceability Weaving + Impact Analysis** - Cross-artifact traceability chains and change propagation analysis across the full design graph
- [ ] **Phase 6: Views, Diagrams, Risk & Volatility** - Presentation layer and risk management: contextual views, D2/Mermaid diagrams, risk scoring, volatility tracking
- [ ] **Phase 7: Orchestration + Coherence Review** - Chief-systems-engineer agent: multi-agent sequencing, coherence review, milestone gating, resilience

## Phase Details

### Phase 1: Design Registry Core + Skill Scaffold
**Goal**: Developers have a working Design Registry with CRUD operations, schema validation, change tracking, and version history -- plus the complete skill scaffold (SKILL.md, directories, security rules) ready for agent development
**Depends on**: Nothing (first phase)
**Requirements**: DREG-01, DREG-02, DREG-03, DREG-04, DREG-05, DREG-06, SCAF-01, SCAF-02, SCAF-03, SCAF-04, SCAF-05
**Success Criteria** (what must be TRUE):
  1. A Python script can create, read, update, and query Design Registry slots with atomic writes and crash recovery
  2. Every write to the registry is schema-validated and rejected if invalid, with a clear error message
  3. The change journal records every mutation and supports time-range queries to reconstruct history
  4. SKILL.md exists under 500 lines with progressive disclosure to commands/, agents/, and references/ directories
  5. The .system-dev/ workspace directory is created on first use with proper path conventions using ${CLAUDE_PLUGIN_ROOT}
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md -- Skill scaffold, JSON schemas, and workspace initialization
- [ ] 01-02-PLAN.md -- Slot storage engine, schema validator, and slot API
- [ ] 01-03-PLAN.md -- Change journal, version manager, and SlotAPI integration

### Phase 2: Requirements Ingestion Pipeline
**Goal**: Developers can ingest all requirements-dev outputs (needs, requirements, traceability, sources, assumptions) into the Design Registry, with delta detection for re-ingestion when upstream changes
**Depends on**: Phase 1
**Requirements**: INGS-01, INGS-02, INGS-03, INGS-04
**Success Criteria** (what must be TRUE):
  1. Running the init command reads requirements-dev registries and populates Design Registry slots with the ingested data
  2. Re-running ingestion after upstream changes detects deltas and reports what changed without clobbering manual design work
  3. Known upstream schema gaps (from CROSS-SKILL-ANALYSIS.md) produce gap markers instead of crashes
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md -- New slot type schemas, registry extension, upstream field mapping, gap markers
- [ ] 02-02-PLAN.md -- Ingestion engine, delta detector, reports, comprehensive tests

### Phase 3: Structural Decomposition + Approval Gate
**Goal**: Developers can request AI-driven component proposals from ingested requirements, review rationale, and accept/reject/modify proposals through an approval gate that persists decisions atomically
**Depends on**: Phase 2
**Requirements**: STRC-01, STRC-02, STRC-03, APPR-01, APPR-02, APPR-03, APPR-04
**Success Criteria** (what must be TRUE):
  1. The decompose command produces component proposals with functional-coherence and data-affinity rationale derived from ingested requirements
  2. The developer can accept, reject, or modify each component proposal, and the decision is persisted atomically (no partial state)
  3. When requirements are incomplete, decomposition produces partial results with explicit gap markers indicating what is missing
  4. The approval gate workflow is reusable -- its state-transition rules are externalizable for use by subsequent agents
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md -- Component-proposal schema, declarative approval-rules config, generic approval gate engine
- [ ] 03-02-PLAN.md -- Decomposition agent with gap detection, command workflows, agent definition, integration tests

### Phase 4: Interface Resolution + Behavioral Contracts
**Goal**: Developers can identify interfaces between approved components, generate protocol/data-format contracts, derive behavioral obligations per component, and assign V&V methods -- all through the proven approval gate
**Depends on**: Phase 3
**Requirements**: INTF-01, INTF-02, INTF-03, INTF-04, BHVR-01, BHVR-02, BHVR-03, BHVR-04
**Success Criteria** (what must be TRUE):
  1. The interface command identifies boundaries between connected components and proposes interface definitions with data formats and protocols
  2. The contract command derives behavioral obligations per component from requirements and interface definitions, with V&V method assignments (test/analysis/inspection/demonstration)
  3. When a component boundary changes, the change-responder re-proposes affected contracts automatically
  4. All interface and contract proposals go through the approval gate with accept/reject/modify
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md -- Proposal schemas, committed schema extensions, ApprovalGate generalization, vv-rules config
- [ ] 04-02-PLAN.md -- Interface resolution agent, interface command, stale detection, integration tests
- [ ] 04-03-PLAN.md -- Behavioral contract agent, contract command, V&V assignment, integration tests

### Phase 5: Traceability Weaving + Impact Analysis
**Goal**: Developers can view and query complete traceability chains (need to requirement to component to interface to contract to V&V) and compute change impact (blast radius) across the design graph
**Depends on**: Phase 4
**Requirements**: TRAC-01, TRAC-02, TRAC-03, TRAC-04, IMPT-01, IMPT-02, IMPT-03
**Success Criteria** (what must be TRUE):
  1. The trace command builds and displays end-to-end traceability chains from stakeholder needs through V&V assignments
  2. Broken chain segments are detected and reported with specific gap identification (which link is missing)
  3. The impact command computes forward and backward propagation paths from any design element with configurable depth limits
  4. Traceability is enforced on write (mandatory trace fields in schemas) not just checked after the fact
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

### Phase 6: Views, Diagrams, Risk & Volatility
**Goal**: Developers can generate contextual design views for different audiences, produce D2/Mermaid diagrams at multiple abstraction levels, track design risks with composite scoring and FMEA, and monitor requirement/design change velocity
**Depends on**: Phase 5
**Requirements**: VIEW-01, VIEW-02, VIEW-03, DIAG-01, DIAG-02, DIAG-03, RISK-01, RISK-02, RISK-03, RISK-04, RISK-05, RISK-06, RISK-07
**Success Criteria** (what must be TRUE):
  1. The status command synthesizes a context-sensitive view from registry subsets, formatted for the requested consumer (developer summary, detailed spec, traceability report)
  2. The diagram command generates D2/Mermaid output at system, block, and sub-block abstraction levels from the current design state
  3. The risk command produces composite risk scores combining volatility, impact gaps, and coherence issues, with FMEA failure-mode analysis
  4. Volatility metrics (stability scores, change frequency) are computed across design checkpoints with trend tracking
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD
- [ ] 06-03: TBD

### Phase 7: Orchestration + Coherence Review
**Goal**: The chief-systems-engineer agent orchestrates multi-agent design workflows via a dependency graph, runs coherence review at phase boundaries, enforces milestone gating, and handles agent failures gracefully
**Depends on**: Phase 6
**Requirements**: ORCH-01, ORCH-02, ORCH-03, ORCH-04, ORCH-05
**Success Criteria** (what must be TRUE):
  1. The review command runs coherence checks detecting cross-concern inconsistencies (e.g., interface references non-existent component, contract contradicts requirement)
  2. Agent execution follows a dependency graph -- agents that depend on others run after their dependencies complete
  3. Milestone gating prevents progression when coherence review identifies blocking issues
  4. Agent failures produce structured error output and do not corrupt registry state (resilience handling)
**Plans**: TBD

Plans:
- [ ] 07-01: TBD
- [ ] 07-02: TBD

### Cross-Cutting: Applied in Every Phase
**Note**: These are not a separate phase. They are constraints enforced during every phase.
**Requirements**: XCUT-01, XCUT-02, XCUT-03, XCUT-04
**Enforcement**:
  1. XCUT-01 (Partial-state tolerance): Every agent produces partial output with gap markers on incomplete input -- verified in each phase's tests
  2. XCUT-02 (Structured logging): Every agent operation produces structured log entries -- logging infrastructure built in Phase 1, used in all phases
  3. XCUT-03 (Externalizable rules): Sub-block configuration is externalized, not hardcoded -- verified when each sub-block is built
  4. XCUT-04 (Slot-api exclusivity): All agents access design state through slot-api, never direct file access -- enforced by Phase 1 API design, verified in all phases

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Design Registry Core + Skill Scaffold | 0/3 | Planned | - |
| 2. Requirements Ingestion Pipeline | 0/1 | Not started | - |
| 3. Structural Decomposition + Approval Gate | 0/2 | Not started | - |
| 4. Interface Resolution + Behavioral Contracts | 0/3 | Not started | - |
| 5. Traceability Weaving + Impact Analysis | 0/2 | Not started | - |
| 6. Views, Diagrams, Risk & Volatility | 0/3 | Not started | - |
| 7. Orchestration + Coherence Review | 0/2 | Not started | - |
