# Requirements: System Dev (AI-Assisted Systems Design Platform)

**Defined:** 2026-02-28
**Core Value:** Design decisions captured as explicit, reviewable, traceable records in a Design Registry (NEED-001, NEED-002)

## Requirements Source

**478 requirements** across 45 blocks formalized in:
- `~/projects/brainstorming/.requirements-dev/requirements_registry.json` (machine-readable, queryable)
- `~/projects/brainstorming/.requirements-dev/deliverables/REQUIREMENTS-SPECIFICATION.md` (human-readable)

**Non-negotiable:** Every phase must reference specific REQ-IDs. Query the JSON registry for full requirement details.

## v1 Requirements

### Design Registry Core

Foundation — all agents depend on this. Includes slot storage, schema validation, versioning, change journal.

- [x] **DREG-01**: Design Registry with named/typed slots, pure storage and query semantics — REQ-001..008, REQ-149..189 (design-registry: 31 reqs)
- [x] **DREG-02**: Slot storage engine with atomic writes, crash recovery, git integration, partitioning — REQ-149..189, REQ-396..406 (slot-storage-engine: 42 reqs)
- [x] **DREG-03**: Slot API providing read/write/query interface for all agents — REQ-190..206 (slot-api: 14 reqs)
- [x] **DREG-04**: Schema validation on every write, schema versioning — REQ-007..008, REQ-215..224, REQ-414..418 (schema-validator: 17 reqs)
- [x] **DREG-05**: Version history per slot, temporal queries — REQ-003..005, REQ-225..233 (version-manager: 10 reqs)
- [x] **DREG-06**: Change journal with append-only entries, time-range queries — REQ-207..214, REQ-406, REQ-471, REQ-479 (change-journal: 11 reqs)

### Skill Scaffold

Plugin structure, SKILL.md, command routing, security rules.

- [x] **SCAF-01**: SKILL.md under 500 lines with progressive disclosure to commands/agents/references
- [x] **SCAF-02**: Plugin directory structure consistent with requirements-dev (commands/, agents/, scripts/, references/, templates/, data/)
- [x] **SCAF-03**: Security rules: content-as-data, path validation, local scripts, external isolation
- [x] **SCAF-04**: ${CLAUDE_PLUGIN_ROOT} path patterns for all file access
- [x] **SCAF-05**: .system-dev/ workspace directory for user design state

### Requirements Ingestion

Bridge from requirements-dev outputs to Design Registry.

- [x] **INGS-01**: Ingest requirements-dev registries (needs, requirements, traceability, sources, assumptions) — REQ-026..030, REQ-141..145 (requirements-synchronizer: 12 reqs)
- [x] **INGS-02**: Ingestion engine parsing upstream JSON registries into design-registry slots — REQ-234..250 (ingestion-engine: 10 reqs)
- [x] **INGS-03**: Delta detection for re-ingestion (upstream requirement changes) — REQ-234..250 (delta-detector: 10 reqs)
- [x] **INGS-04**: Graceful handling of upstream schema gaps (known bugs accepted, gap markers produced)

### Structural Decomposition

AI-proposed component groupings from requirements.

- [x] **STRC-01**: Component proposal from requirements with functional coherence/data affinity rationale — REQ-031..033, REQ-251..258 (structural-decomposition-agent: 11 reqs)
- [x] **STRC-02**: Component proposer sub-agent with grouping algorithms — REQ-251..258 (component-proposer: 8 reqs)
- [x] **STRC-03**: Partial decomposition with gap markers when requirements are incomplete — REQ-090..092

### Approval Gate

Developer accept/reject/modify for all agent proposals.

- [x] **APPR-01**: Accept/reject/modify workflow for component proposals — REQ-259..266 (approval-gate: 11 reqs)
- [x] **APPR-02**: Atomic transactions (no partial state on accept/reject) — REQ-470
- [x] **APPR-03**: Decision persistence before response — REQ-450
- [x] **APPR-04**: Externalizable workflow state-transition rules — REQ-474

### Interface Resolution

Component boundary contracts and protocol definitions.

- [x] **INTF-01**: Interface identification between connected components — REQ-034..037, REQ-267..272 (interface-resolution-agent: 13 reqs)
- [x] **INTF-02**: Contract generation with data formats and protocols — REQ-267..272 (contract-generator: 7 reqs)
- [x] **INTF-03**: Interface proposal sub-agent — REQ-267..272 (interface-proposer: 8 reqs)
- [x] **INTF-04**: Change-reactive contract re-proposal on boundary changes — REQ-273..282 (change-responder: 8 reqs)

### Behavioral Contracts & V&V

Verification planning at design time per INCOSE principles.

- [x] **BHVR-01**: Behavioral obligation derivation per component — REQ-038..041, REQ-283..298 (behavioral-contract-agent: 14 reqs)
- [x] **BHVR-02**: Obligation deriver sub-agent — REQ-283..288 (obligation-deriver: 7 reqs)
- [x] **BHVR-03**: Contract proposal with accept/reject/modify — REQ-283..298 (contract-proposer: 8 reqs)
- [x] **BHVR-04**: V&V method assignment (test/analysis/inspection/demonstration) — REQ-040, REQ-289..293, REQ-407 (vv-planner: 7 reqs)

### Traceability Weaving

End-to-end need→requirement→component→interface→contract→V&V chains.

- [ ] **TRAC-01**: Graph construction from registry slots — REQ-042..044, REQ-299..309 (traceability-weaver: 11 reqs)
- [ ] **TRAC-02**: Graph builder with traversal and query — REQ-304..309 (graph-builder: 8 reqs)
- [ ] **TRAC-03**: Chain validation detecting broken segments — REQ-299..303, REQ-452 (chain-maintainer: 6 reqs)
- [x] **TRAC-04**: Traceability enforced on write, not just checked after — per PITFALLS.md

### Impact Analysis

Change propagation and blast radius computation.

- [ ] **IMPT-01**: Forward/backward impact path computation — REQ-045..047, REQ-310..320 (impact-analysis-agent: 12 reqs)
- [ ] **IMPT-02**: Path computation with configurable depth limits — REQ-310..315 (path-computer: 8 reqs)
- [ ] **IMPT-03**: Change tracing from modification to affected elements — REQ-316..320 (change-tracer: 8 reqs)

### Risk Registry & Volatility

Design risk identification, scoring, and trend tracking.

- [ ] **RISK-01**: Risk registry with composite scoring — REQ-066..069, REQ-381..395 (risk-registry: 14 reqs)
- [ ] **RISK-02**: Risk calculator combining volatility, impact, gaps, coherence — REQ-381..386 (risk-calculator: 6 reqs)
- [ ] **RISK-03**: FMEA engine for failure mode analysis — REQ-387..390 (fmea-engine: 6 reqs)
- [ ] **RISK-04**: Trend tracking across design checkpoints — REQ-391..395 (trend-tracker: 7 reqs)
- [ ] **RISK-05**: Volatility tracking with stability metrics — REQ-048..050, REQ-321..331 (volatility-tracker: 11 reqs)
- [ ] **RISK-06**: Metric computation (stability scores, change frequency) — REQ-325..328 (metric-computer: 6 reqs)
- [ ] **RISK-07**: Snapshot management for checkpoint comparison — REQ-329..331 (snapshot-manager: 7 reqs)

### Views, Diagrams & Output

Contextual design views and publishable diagrams.

- [ ] **VIEW-01**: Context-sensitive view synthesis from registry subsets — REQ-058..062, REQ-354..369 (view-synthesizer: 12 reqs)
- [ ] **VIEW-02**: View assembly with relevance ranking — REQ-358..363 (view-assembler: 8 reqs, relevance-ranker: 8 reqs)
- [ ] **VIEW-03**: Output formatting for different consumers — REQ-364..369 (output-formatter: 7 reqs)
- [ ] **DIAG-01**: D2/Mermaid diagram generation from design state — REQ-063..065, REQ-370..380 (diagram-renderer: 11 reqs)
- [ ] **DIAG-02**: Diagram generator from canonical model — REQ-370..375 (diagram-generator: 7 reqs)
- [ ] **DIAG-03**: Abstraction management (system/block/sub-block levels) — REQ-376..380 (abstraction-manager: 8 reqs)

### Orchestration & Coherence

Chief systems engineer, agent sequencing, coherence review.

- [ ] **ORCH-01**: Agent dependency graph and execution sequencing — REQ-051..057, REQ-338..343 (chief-systems-engineer: 20 reqs)
- [ ] **ORCH-02**: Orchestrator for phase/agent invocation — REQ-338..343 (orchestrator: 8 reqs)
- [ ] **ORCH-03**: Coherence review detecting cross-concern inconsistencies — REQ-332..337 (coherence-reviewer: 9 reqs)
- [ ] **ORCH-04**: Governance authority with milestone gating — REQ-344..348 (governance-authority: 5 reqs)
- [ ] **ORCH-05**: Agent resilience and conflict resolution — REQ-349..353 (resilience-handler: 7 reqs)

### Cross-Cutting

Partial-state tolerance, structured logging, configurable rules.

- [ ] **XCUT-01**: All agents produce partial output with gap markers on incomplete input — REQ-012, REQ-090..098, REQ-130..135
- [ ] **XCUT-02**: Structured logging per agent operation — REQ-136..140, REQ-188, REQ-206, REQ-214, REQ-224, REQ-258, etc.
- [ ] **XCUT-03**: Externalizable rules/configuration for sub-blocks — REQ-430..449
- [ ] **XCUT-04**: All agents access design state exclusively through slot-api (NEED-007) — constraint requirements per block

## v2 Requirements

### Schema Evolution & Governance
- **GOVN-01**: Schema versioning with backward compatibility checks — REQ-056, REQ-192, REQ-345
- **GOVN-02**: Migration approval workflow for schema changes

### Advanced Analytics
- **ANLZ-01**: Historical trend dashboards across milestones
- **ANLZ-02**: Design maturity scoring

### Cross-Skill Integration
- **XSKL-01**: Harmonized source registries across concept-dev, requirements-dev, system-dev
- **XSKL-02**: Skeptic agent cross-calibration (pass findings across skill boundaries)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Graphical UI / web dashboard | CLI-first skill; diagrams rendered via D2/Mermaid text |
| Multi-user collaboration | Single-developer workflow; git handles async multi-session |
| Full SysML v2 engine | Multi-year project; JSON schemas inspired by SysML concepts instead |
| Autonomous design decisions | Violates NEED-013; agents propose, developer decides |
| Database backend | JSON files consistent with upstream skills, LLM-editable, zero infrastructure |
| Upstream bug fixes | Work with current requirements-dev output as-is |
| Code generation | That's design-impl (skill #4) |

## Traceability

| GSD Requirement | Phase | Formal REQ-IDs | Status |
|-----------------|-------|----------------|--------|
| DREG-01..06 | Phase 1 | REQ-001..008, REQ-149..233, REQ-396..406, REQ-414..418, REQ-471, REQ-479 | Pending |
| SCAF-01..05 | Phase 1 | (skill structure, no formal REQ) | Pending |
| INGS-01..04 | Phase 2 | REQ-026..030, REQ-141..145, REQ-234..250 | Pending |
| STRC-01..03 | Phase 3 | REQ-031..033, REQ-070, REQ-080, REQ-090..092, REQ-251..258 | Pending |
| APPR-01..04 | Phase 3 | REQ-259..266, REQ-450, REQ-470, REQ-474 | Pending |
| INTF-01..04 | Phase 4 | REQ-034..037, REQ-267..282 | Pending |
| BHVR-01..04 | Phase 4 | REQ-038..041, REQ-283..298, REQ-407 | Pending |
| TRAC-01..04 | Phase 5 | REQ-042..044, REQ-299..309, REQ-452 | Pending |
| IMPT-01..03 | Phase 5 | REQ-045..047, REQ-310..320 | Pending |
| RISK-01..07 | Phase 6 | REQ-048..050, REQ-066..069, REQ-321..331, REQ-381..395 | Pending |
| VIEW-01..03, DIAG-01..03 | Phase 6 | REQ-058..065, REQ-354..380 | Pending |
| ORCH-01..05 | Phase 7 | REQ-051..057, REQ-332..353 | Pending |
| XCUT-01..04 | All phases | REQ-012, REQ-090..098, REQ-130..140, REQ-430..449 | Pending |

**Coverage:**
- v1 GSD requirements: 55 total (mapping to 478 formal requirements)
- Mapped to phases: 55
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-28*
*Last updated: 2026-02-28 after initial definition*
