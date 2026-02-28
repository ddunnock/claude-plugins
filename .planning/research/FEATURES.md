# Feature Research

**Domain:** AI-Assisted INCOSE System Design (Claude Code Skill)
**Researched:** 2026-02-28
**Confidence:** HIGH (derived from 478 baselined requirements + MBSE tool landscape analysis)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = the skill is incomplete and cannot perform basic INCOSE system design.

| # | Feature | Why Expected | Complexity | Req Blocks | Key REQ-IDs |
|---|---------|--------------|------------|------------|-------------|
| T1 | **Design Registry (central artifact store)** | Without a persistent, queryable store for design artifacts, nothing else works. Every agent reads/writes through it. This is the foundation the entire system stands on. | HIGH | design-registry, slot-storage-engine, slot-api, schema-validator | REQ-001..025, REQ-149..189, REQ-190..206, REQ-215..224 |
| T2 | **Requirements ingestion from upstream** | The skill must consume requirements-dev output (needs, requirements, traceability). Without ingestion, the designer has nothing to design against. | MEDIUM | requirements-synchronizer, ingestion-engine, delta-detector | REQ-026..030, REQ-141..145, REQ-234..250 |
| T3 | **Structural decomposition (component proposals)** | Proposing component groupings from requirements is the first design act. Every MBSE tool provides decomposition. Without it, there is no system architecture. | MEDIUM | structural-decomposition-agent, component-proposer | REQ-031..033, REQ-070, REQ-080, REQ-251..258 |
| T4 | **Developer approval gate** | Agents must propose, not dictate. Accept/reject/modify is the human-in-the-loop contract (NEED-013). Without it, the tool is an autonomous agent, not an assistant. | MEDIUM | approval-gate | REQ-259..266, REQ-450, REQ-470 |
| T5 | **Interface resolution (contract generation)** | Defining component boundary contracts is core to INCOSE system design. Components without interfaces are boxes with no wires. | MEDIUM | interface-resolution-agent, contract-generator, interface-proposer, change-responder | REQ-034..037, REQ-267..282 |
| T6 | **Behavioral contracts and V&V planning** | INCOSE demands that verification planning happens at design time, not test time. This is a non-negotiable principle (NEED-015, NEED-016, NEED-017). | HIGH | behavioral-contract-agent, obligation-deriver, contract-proposer, vv-planner | REQ-038..041, REQ-283..298, REQ-289..293 |
| T7 | **Traceability weaving** | Unbroken need-to-requirement-to-component-to-interface-to-V&V chains are the hallmark of INCOSE process. Without traceability, the design is opaque. | HIGH | traceability-weaver, graph-builder, chain-maintainer | REQ-042..044, REQ-299..309 |
| T8 | **Schema validation on write** | Every slot write must be validated against a JSON schema. Without this, agents can silently corrupt the registry. This is a data integrity table stake. | MEDIUM | schema-validator, design-registry | REQ-007..008, REQ-190..206, REQ-414..418 |
| T9 | **Version history and rollback** | Design decisions evolve. Without version history, there is no undo and no temporal analysis. Every MBSE platform provides versioning. | MEDIUM | version-manager, change-journal | REQ-003..004, REQ-207..214, REQ-225..233 |
| T10 | **Partial-state tolerance (gap markers)** | Agents must work with incomplete data by producing output with explicit gaps, not crashing. This is pervasive across all agents (NEED-037, NEED-028). | MEDIUM | All agents | REQ-012, REQ-090..098, REQ-130..135 |
| T11 | **Orchestration (agent sequencing)** | Agents have dependency order. Without orchestration, the developer must manually invoke agents in the right sequence, defeating the purpose of automation. | HIGH | chief-systems-engineer, orchestrator | REQ-051..057, REQ-146..148, REQ-338..343 |
| T12 | **Structured logging per agent** | Every agent must emit structured logs. Without observability, debugging a multi-agent system is impossible. | LOW | All agents | REQ-136..140, REQ-188, REQ-206, REQ-214, REQ-224, REQ-258, etc. |

### Differentiators (Competitive Advantage)

Features that set this tool apart from manual INCOSE design or traditional MBSE tools. Not expected by default, but provide significant value in an AI-assisted workflow.

| # | Feature | Value Proposition | Complexity | Req Blocks | Key REQ-IDs |
|---|---------|-------------------|------------|------------|-------------|
| D1 | **AI-driven component grouping rationale** | Traditional tools require the engineer to manually decompose. AI proposes groupings with rationale referencing functional coherence, data affinity, and operational independence. No MBSE tool does this. | MEDIUM | component-proposer | REQ-251..254 |
| D2 | **Automated impact analysis** | Forward/backward impact path computation from any design element. Existing tools require manual graph traversal. AI computes blast radius automatically. | HIGH | impact-analysis-agent, path-computer, change-tracer | REQ-045..047, REQ-310..320 |
| D3 | **Volatility tracking and stability metrics** | Identifying the most unstable design elements by change frequency is novel. Traditional tools track changes but do not compute stability scores or flag volatility hotspots. | MEDIUM | volatility-tracker, metric-computer, snapshot-manager | REQ-048..050, REQ-321..331 |
| D4 | **Composite risk scoring** | Combining volatility, impact depth, traceability gaps, V&V gaps, and coherence findings into a single risk score per design element. Traditional FMEA tools exist but do not integrate all these signals. | HIGH | risk-registry, risk-calculator, fmea-engine, trend-tracker | REQ-066..069, REQ-381..395 |
| D5 | **Coherence review (cross-concern inconsistency detection)** | Single-pass detection of inconsistencies across all slot types after agents operate. Traditional tools detect errors within a model type but rarely across heterogeneous artifact types. | HIGH | chief-systems-engineer, coherence-reviewer | REQ-051..053, REQ-332..337 |
| D6 | **Change-reactive contract re-proposal** | When component boundaries change, interface contracts are automatically re-proposed. In traditional tools, boundary changes require manual contract updates. | MEDIUM | change-responder | REQ-273..277 |
| D7 | **Contextual view synthesis** | On-demand views assembled from registry subsets by work pattern, with relevance ranking. Traditional tools show static model views; this assembles dynamic, context-sensitive views. | MEDIUM | view-synthesizer, view-assembler, relevance-ranker, output-formatter | REQ-058..062, REQ-354..369 |
| D8 | **D2/Mermaid diagram generation from canonical model** | Generating publishable diagrams (D2 for structural, Mermaid for behavioral) directly from the design state. No manual diagramming required. | MEDIUM | diagram-renderer, diagram-generator, abstraction-manager | REQ-063..065, REQ-370..380 |
| D9 | **Milestone gating on completeness and coherence** | Automated gate checks that block milestone advancement when criteria are unmet. Traditional tools rely on manual reviews. | MEDIUM | governance-authority | REQ-344..348 |
| D10 | **Risk trend analysis across checkpoints** | Tracking risk scores across design checkpoints and computing deltas (increasing/decreasing/stable). Provides continuous risk awareness, not just point-in-time assessment. | MEDIUM | trend-tracker | REQ-391..395 |
| D11 | **Schema evolution governance** | Formal schema versioning with backward compatibility checks and migration approval. Prevents schema drift that breaks agents silently. | LOW | governance-authority, schema-validator | REQ-056, REQ-192, REQ-345 |
| D12 | **Agent resilience and conflict resolution** | Graceful handling of subordinate agent failures and conflicting recommendations without halting the workflow. Traditional tools crash on errors. | MEDIUM | resilience-handler | REQ-349..353, REQ-426, REQ-445 |
| D13 | **Configurable/externalizable rules** | Nearly all sub-blocks support external configuration of rules, templates, and thresholds (REQ-430..449). This enables customization without code changes. | LOW | Multiple sub-blocks | REQ-430..449 |

### Anti-Features (Commonly Requested, Often Problematic)

Features to explicitly NOT build.

| # | Feature | Why Requested | Why Problematic | Alternative |
|---|---------|---------------|-----------------|-------------|
| A1 | **Graphical UI / web dashboard** | Visual MBSE tools have GUIs. Developers expect one. | This is a Claude Code CLI skill. Adding a GUI adds an entire frontend stack, breaks the CLI-first contract, and multiplies scope 5x. PROJECT.md explicitly scopes this out. | Generate D2/Mermaid text diagrams that render in existing viewers. Use view-synthesizer for contextual CLI output. |
| A2 | **Real-time multi-user collaboration** | Enterprise MBSE tools support concurrent users. | Single-developer workflow (PROJECT.md out of scope). Concurrent editing of JSON registry files introduces merge conflicts, locking complexity, and distributed state problems. | Git-based persistence handles async multi-session via version control. |
| A3 | **Full SysML v2 modeling engine** | INCOSE adopted SysML v2 as primary SE modeling language. | Building a SysML v2 parser/editor is a multi-year project. The skill needs structured design artifacts, not a modeling language runtime. | Use JSON slot schemas inspired by SysML concepts. Generate SysML-compatible views via diagram-renderer if needed later. |
| A4 | **Autonomous design decisions (no human approval)** | "Let the AI do everything" is tempting for speed. | Violates NEED-013 (developer accept/reject/modify). Autonomous AI design decisions are not auditable and erode trust. The approval gate exists for a reason. | Agents propose with rationale. Developer decides. This is the core contract. |
| A5 | **Database backend (PostgreSQL, SQLite, etc.)** | Databases are the "right" storage for structured data. | JSON files with git backing are consistent with upstream skills, LLM-editable, and require zero infrastructure. A database adds deployment complexity, migration burden, and breaks LLM direct-edit capability. | JSON files partitioned under 500KB per NEED-004, git backend per REQ-023. |
| A6 | **Fix upstream requirements-dev schema bugs** | Known integration gaps exist (CROSS-SKILL-ANALYSIS.md). | Scope creep into another skill's territory. The requirements-synchronizer must accept upstream output as-is. | Document known gaps. Handle gracefully in ingestion with gap markers. Address in a separate cross-skill fix. |
| A7 | **Automatic code generation from design** | Natural next step after design is complete. | That is design-impl (skill #4), not system-dev (skill #3). Mixing design and implementation in one skill conflates concerns. | Produce clean design artifacts that design-impl can consume. |

## Feature Dependencies

```
[T1] Design Registry
    |--required-by--> [T2] Requirements Ingestion
    |--required-by--> [T3] Structural Decomposition
    |--required-by--> [T5] Interface Resolution
    |--required-by--> [T6] Behavioral Contracts
    |--required-by--> [T7] Traceability Weaving
    |--required-by--> [T9] Version History
    |--required-by--> [T8] Schema Validation (embedded in T1)

[T2] Requirements Ingestion
    |--required-by--> [T3] Structural Decomposition

[T3] Structural Decomposition
    |--required-by--> [T4] Approval Gate (first use)
    |--required-by--> [T5] Interface Resolution
    |--required-by--> [T6] Behavioral Contracts

[T4] Approval Gate
    |--enhances--> [T3], [T5], [T6] (gates all proposals)

[T5] Interface Resolution
    |--required-by--> [T7] Traceability Weaving (interface nodes)
    |--required-by--> [D6] Change-reactive re-proposal

[T6] Behavioral Contracts
    |--required-by--> [T7] Traceability Weaving (V&V nodes)
    |--required-by--> [D5] Coherence Review

[T7] Traceability Weaving
    |--required-by--> [D2] Impact Analysis
    |--required-by--> [D4] Risk Scoring
    |--required-by--> [D9] Milestone Gating

[T9] Version History
    |--required-by--> [D3] Volatility Tracking

[D2] Impact Analysis
    |--required-by--> [D4] Risk Scoring

[D3] Volatility Tracking
    |--required-by--> [D4] Risk Scoring

[D5] Coherence Review
    |--required-by--> [D4] Risk Scoring
    |--required-by--> [D9] Milestone Gating

[D7] View Synthesis --enhances--> [D8] Diagram Generation

[D4] Risk Scoring --enhances--> [D10] Risk Trend Analysis
```

### Dependency Notes

- **T1 (Design Registry) is the foundational dependency:** Every other feature reads and writes through it. It must be built first, tested thoroughly, and stable before any agent work begins.
- **T2 (Requirements Ingestion) gates T3:** Components cannot be proposed without ingested requirements.
- **T3/T5/T6 form the core design triad:** Decomposition, interfaces, and behavioral contracts are the three pillars of system design. They depend on each other and all flow through the approval gate (T4).
- **T7 (Traceability) is the integrator:** It connects everything and is required before impact analysis, risk scoring, or milestone gating can function.
- **D2/D3/D5 all feed D4:** Composite risk scoring is the highest-complexity differentiator because it integrates outputs from three other differentiator features.
- **D7/D8 are presentation-layer features:** They depend on all other features having populated the registry but are not dependencies for any core workflow.

## MVP Definition

### Launch With (v1)

Minimum viable skill -- what is needed to validate the core design workflow.

- [ ] **T1: Design Registry** (slot-storage-engine, slot-api, schema-validator, version-manager, change-journal) -- Without storage, nothing works
- [ ] **T2: Requirements Ingestion** (ingestion-engine, delta-detector) -- Must consume upstream output
- [ ] **T3: Structural Decomposition** (component-proposer) -- First design act
- [ ] **T4: Approval Gate** -- Human-in-the-loop is non-negotiable
- [ ] **T8: Schema Validation** -- Data integrity from day one
- [ ] **T10: Partial-state Tolerance** -- Must not crash on incomplete data
- [ ] **T11: Orchestration** (basic sequencing only) -- Developer should not manage agent order manually
- [ ] **T12: Structured Logging** -- Observability from day one
- [ ] **D1: AI-driven component rationale** -- The single differentiator that justifies using AI over a manual tool

### Add After Validation (v1.x)

Features to add once core design workflow is validated.

- [ ] **T5: Interface Resolution** -- Add when components are stable enough to define boundaries
- [ ] **T6: Behavioral Contracts + V&V Planning** -- Add when interface contracts exist to derive obligations from
- [ ] **T7: Traceability Weaving** -- Add when components + interfaces + contracts exist to trace
- [ ] **T9: Version History** (full rollback) -- Add when registry has enough state to warrant rollback
- [ ] **D2: Impact Analysis** -- Add after traceability graph exists
- [ ] **D5: Coherence Review** -- Add after multiple agent outputs populate the registry
- [ ] **D8: Diagram Generation** -- Add when there is design state worth visualizing

### Future Consideration (v2+)

Features to defer until core workflow is proven.

- [ ] **D3: Volatility Tracking** -- Needs sufficient version history to be meaningful
- [ ] **D4: Composite Risk Scoring** -- Requires D2, D3, D5 as inputs
- [ ] **D6: Change-reactive Re-proposal** -- Optimization for iterative design
- [ ] **D7: Contextual View Synthesis** -- Presentation-layer enhancement
- [ ] **D9: Milestone Gating** -- Governance layer once design process is mature
- [ ] **D10: Risk Trend Analysis** -- Requires checkpoints and history
- [ ] **D11: Schema Evolution Governance** -- Low priority until schemas stabilize
- [ ] **D12: Agent Resilience** -- Important but not blocking MVP
- [ ] **D13: Configurable Rules** -- Enhancement once core rules are hardcoded and validated

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority | Phase |
|---------|------------|---------------------|----------|-------|
| T1: Design Registry | HIGH | HIGH | P1 | v1 |
| T2: Requirements Ingestion | HIGH | MEDIUM | P1 | v1 |
| T3: Structural Decomposition | HIGH | MEDIUM | P1 | v1 |
| T4: Approval Gate | HIGH | MEDIUM | P1 | v1 |
| T8: Schema Validation | HIGH | MEDIUM | P1 | v1 |
| T10: Partial-state Tolerance | HIGH | LOW | P1 | v1 |
| T11: Orchestration | HIGH | HIGH | P1 | v1 |
| T12: Structured Logging | MEDIUM | LOW | P1 | v1 |
| D1: AI Component Rationale | HIGH | MEDIUM | P1 | v1 |
| T5: Interface Resolution | HIGH | MEDIUM | P2 | v1.x |
| T6: Behavioral Contracts | HIGH | HIGH | P2 | v1.x |
| T7: Traceability Weaving | HIGH | HIGH | P2 | v1.x |
| T9: Version History | MEDIUM | MEDIUM | P2 | v1.x |
| D2: Impact Analysis | HIGH | HIGH | P2 | v1.x |
| D5: Coherence Review | HIGH | HIGH | P2 | v1.x |
| D8: Diagram Generation | MEDIUM | MEDIUM | P2 | v1.x |
| D3: Volatility Tracking | MEDIUM | MEDIUM | P3 | v2+ |
| D4: Composite Risk Scoring | HIGH | HIGH | P3 | v2+ |
| D6: Change-reactive Re-proposal | MEDIUM | MEDIUM | P3 | v2+ |
| D7: Contextual View Synthesis | MEDIUM | MEDIUM | P3 | v2+ |
| D9: Milestone Gating | MEDIUM | MEDIUM | P3 | v2+ |
| D10: Risk Trend Analysis | MEDIUM | MEDIUM | P3 | v2+ |
| D11: Schema Evolution | LOW | LOW | P3 | v2+ |
| D12: Agent Resilience | MEDIUM | MEDIUM | P3 | v2+ |
| D13: Configurable Rules | LOW | LOW | P3 | v2+ |

**Priority key:**
- P1: Must have for launch (MVP)
- P2: Should have, add in v1.x once core validates
- P3: Nice to have, v2+ consideration

## Competitor Feature Analysis

| Feature Area | IBM Rhapsody / DOORS | Cameo Systems Modeler | Visure Solutions | Our Approach (system-dev) |
|-------------|---------------------|----------------------|------------------|--------------------------|
| Requirements ingestion | Import from DOORS, RequisitePro | Import from various ALM tools | Built-in requirements management | Ingest from requirements-dev JSON registries (NEED-009..011) |
| Structural decomposition | Manual via SysML BDD/IBD | Manual via SysML diagrams | Manual | AI-proposed component groupings with rationale (D1) |
| Interface contracts | Manual diagram creation | Manual with contract patterns | N/A | AI-generated from component boundaries (T5) |
| Traceability | DOORS integration, manual linking | Matrix views, manual | Automated traceability matrices | Automated graph construction with orphan detection (T7) |
| Impact analysis | Manual traversal of DOORS links | Dependency analysis plugins | Change impact reports | Automated forward/backward path computation (D2) |
| Risk management | Separate tools (IQ-RM, etc.) | Risk modeling extensions | Risk assessment module | Integrated composite risk from 5+ data dimensions (D4) |
| Verification planning | Manual test case creation | V&V matrix support | Test management integration | Design-time V&V artifact generation with method assignment (T6) |
| Diagram generation | Model-to-diagram (SysML native) | SysML native diagrams | Requirements flow diagrams | D2 structural + Mermaid behavioral from canonical model (D8) |
| Change detection | DOORS baseline comparison | Model diff tools | Requirements diff | Delta detection with staleness markers, reactive re-proposal (D6) |
| AI assistance | IBM AI Hub MBSE use-case discovery agent (2025) | None native | AI classification/tagging | AI across all agents: decomposition, contracts, coherence, risk |
| Deployment | Enterprise server + thick client | Enterprise server + thick client | Cloud or on-premise | CLI skill running in Claude Code, zero infrastructure |
| Human-in-the-loop | Manual review/approval processes | Workflow with review states | Approval workflows | Formal approval gate with accept/reject/modify per proposal (T4) |

## Requirement Block Coverage

How features map to the 45 requirement blocks and 478 requirements:

| Feature | Blocks Covered | Approx Req Count | Coverage |
|---------|---------------|-------------------|----------|
| T1: Design Registry | design-registry, slot-storage-engine, slot-api, schema-validator, version-manager, change-journal | ~135 | 28% |
| T2: Requirements Ingestion | requirements-synchronizer, ingestion-engine, delta-detector | ~32 | 7% |
| T3: Structural Decomposition | structural-decomposition-agent, component-proposer | ~19 | 4% |
| T4: Approval Gate | approval-gate | ~11 | 2% |
| T5: Interface Resolution | interface-resolution-agent, contract-generator, interface-proposer, change-responder | ~34 | 7% |
| T6: Behavioral Contracts | behavioral-contract-agent, obligation-deriver, contract-proposer, vv-planner | ~35 | 7% |
| T7: Traceability Weaving | traceability-weaver, graph-builder, chain-maintainer | ~22 | 5% |
| T11: Orchestration | chief-systems-engineer, orchestrator, resilience-handler, governance-authority, coherence-reviewer | ~58 | 12% |
| D2: Impact Analysis | impact-analysis-agent, path-computer, change-tracer | ~28 | 6% |
| D3: Volatility Tracking | volatility-tracker, metric-computer, snapshot-manager | ~25 | 5% |
| D4: Composite Risk | risk-registry, risk-calculator, fmea-engine, trend-tracker | ~27 | 6% |
| D7: View Synthesis | view-synthesizer, view-assembler, relevance-ranker, output-formatter | ~32 | 7% |
| D8: Diagram Generation | diagram-renderer, diagram-generator, abstraction-manager | ~22 | 5% |

**Total coverage: 478/478 requirements mapped to features.**

## Sources

- [INCOSE Systems Engineering Tools Database](https://www.incose.org/communities/working-groups-initiatives/se-tools-database) -- INCOSE tool catalog
- [Best MBSE Tools in 2025](https://machinecircuit.com/best-model-based-systems-engineering-mbse-tools-in-2025-features-pricing-comparison/) -- MBSE tool comparison
- [IBM AI for MBSE](https://www.ibm.com/new/announcements/new-ai-automations-for-model-based-systems-engineering) -- IBM Engineering AI Hub capabilities
- [AI in MBSE](https://accuristech.com/maximizing-efficiency-ai-in-mbse-modern-engineering/) -- AI-assisted MBSE landscape
- [Key MBSE Tools Comparison](https://mgtechsoft.com/blog/top-tools-of-mbse/) -- Rhapsody vs Cameo comparison
- [Visure MBSE Tools](https://visuresolutions.com/alm-guide/best-mbse-tools-and-solutions/) -- MBSE tool features catalog
- [Requirements Traceability](https://en.wikipedia.org/wiki/Requirements_traceability) -- Traceability fundamentals
- 478 requirements from `~/projects/brainstorming/.requirements-dev/deliverables/REQUIREMENTS-SPECIFICATION.md`
- 48 stakeholder needs from `~/projects/brainstorming/.requirements-dev/needs_registry.json`

---
*Feature research for: AI-Assisted INCOSE System Design Platform*
*Researched: 2026-02-28*
