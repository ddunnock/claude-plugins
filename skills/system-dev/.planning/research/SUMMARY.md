# Project Research Summary

**Project:** system-dev (AI-Assisted INCOSE System Design Platform)
**Domain:** Claude Code skill -- multi-agent systems design with central Design Registry
**Researched:** 2026-02-28
**Confidence:** HIGH

## Executive Summary

system-dev is a Claude Code skill that implements the INCOSE system design phase of a multi-skill engineering pipeline. It consumes requirements from an upstream skill (requirements-dev) and produces structured design artifacts: component decompositions, interface contracts, behavioral obligations, V&V plans, traceability chains, and risk assessments. The proven approach, validated by the working requirements-dev skill, is a registry-centric architecture where all agents read/write through a central JSON-based Design Registry via deterministic Python scripts. This hub-and-spoke pattern decouples agents, enables checkpoint/resume, and provides a complete audit trail. The skill ships as Markdown files (SKILL.md entry point, command files, agent files) plus ~25 Python scripts, with zero external dependencies beyond Python stdlib and jsonschema.

The recommended approach is to build the Design Registry infrastructure first (slot storage, schema validation, change journal, version management), then the requirements ingestion pipeline, then layer on domain agents one at a time following the natural dependency chain: structural decomposition, interface resolution, behavioral contracts, traceability, impact analysis, and finally risk/views/orchestration. Every agent proposes through an approval gate -- the developer always decides. This build order is driven by strict data dependencies: you cannot define interfaces without components, cannot write contracts without interfaces, and cannot trace without all three.

The primary risks are context window exhaustion from bulk-loading registry data into agents (mitigate with projection queries from day one), JSON corruption from concurrent agent writes (mitigate with file partitioning and atomic writes), and schema mismatch at the upstream boundary (mitigate by validating against real requirements-dev output, not assumed schemas). All three risks are addressable in Phase 1 if the registry is designed correctly from the start. The documented bugs from the concept-dev-to-requirements-dev boundary (3 confirmed bugs from schema key mismatches) provide concrete evidence that upstream integration is the highest-risk technical area.

## Key Findings

### Recommended Stack

The stack replicates the proven requirements-dev pattern: Markdown for skill definitions, Python 3.11+ for all scripts, JSON for all data storage, and XML tags within Markdown for structured behavior rules. No npm, no database, no external services. `uv` manages Python dependencies (dev-only: pytest). All paths use `${CLAUDE_PLUGIN_ROOT}` -- never relative paths.

**Core technologies:**
- **Markdown (SKILL.md + commands/ + agents/)**: Skill entry point and progressive disclosure -- required by Claude Code skill format, SKILL.md under 500 lines
- **Python 3.11+ with uv**: All utility scripts (registry CRUD, validation, ingestion, state management) -- proven in requirements-dev with 16 scripts and zero npm dependencies
- **JSON flat files with git backend**: Design Registry storage and all machine-readable artifacts -- LLM-editable, atomic writes, schema-versioned, git provides free version history
- **XML tags in Markdown**: Structured behavior rules, security blocks, workflow steps -- Claude parses these reliably for unambiguous instruction boundaries

### Expected Features

**Must have (table stakes -- v1):**
- T1: Design Registry (central artifact store) -- foundational; every agent depends on it
- T2: Requirements ingestion from upstream -- no design without requirements
- T3: Structural decomposition with AI-driven rationale -- first design act; the key differentiator justifying AI
- T4: Developer approval gate -- human-in-the-loop is non-negotiable (NEED-013)
- T8: Schema validation on every write -- data integrity from day one
- T10: Partial-state tolerance with gap markers -- agents must not crash on incomplete data
- T11: Orchestration (basic agent sequencing) -- developer should not manage agent order manually
- T12: Structured logging -- observability for multi-agent debugging

**Should have (competitive advantage -- v1.x):**
- T5: Interface resolution and contract generation
- T6: Behavioral contracts and V&V planning
- T7: Traceability weaving (need-to-requirement-to-component chains)
- D2: Automated impact analysis (blast radius computation)
- D5: Coherence review (cross-concern inconsistency detection)
- D8: D2/Mermaid diagram generation from design state

**Defer (v2+):**
- D3: Volatility tracking, D4: Composite risk scoring, D6: Change-reactive re-proposal, D7: Contextual view synthesis, D9-D13: Milestone gating, trend analysis, schema evolution, agent resilience, configurable rules

### Architecture Approach

Four-layer architecture: (1) SKILL.md + 11 slash commands as the user interface, (2) 8 LLM sub-agents for judgment-requiring work (decomposition, interface negotiation, contract derivation, coherence review), (3) ~25 deterministic Python scripts for all storage, validation, graph traversal, and metric computation, (4) the Design Registry as a file-system-based JSON store in `.system-dev/`. The central architectural principle is hub-and-spoke: all inter-agent communication flows through the Design Registry. Agents never call each other directly.

**Major components:**
1. **Design Registry (Layer 4)** -- JSON slots partitioned by type (components/, interfaces/, contracts/, etc.), indexed, schema-validated, git-backed, with change journal and version history
2. **Python Scripts (Layer 3)** -- ~25 scripts covering registry CRUD, ingestion, graph building, metric computation, orchestration, and governance; deterministic, testable, zero LLM token cost
3. **LLM Agents (Layer 2)** -- 8 agent markdown files; 6 domain agents (structural-decomposition, interface-resolution, behavioral-contract, traceability-weaver, impact-analysis, view-synthesizer) plus risk-analyst and chief-systems-engineer (opus model for complex reasoning)
4. **Commands (Layer 1)** -- 11 slash commands orchestrating agent/script invocations with approval gates at design decision boundaries

### Critical Pitfalls

1. **Context window exhaustion from registry bulk-loading** -- Design slot-api with projection queries from day one; agents request specific slots by ID and field subset, never full registries; budget ~2000 tokens max per registry query
2. **JSON corruption from concurrent agent writes** -- Partition registry into separate files per slot type; implement atomic writes (temp-file-then-rename); use file-level locking; never have two agents write to the same file
3. **Schema mismatch at upstream boundary** -- 3 confirmed bugs exist in the concept-dev-to-requirements-dev boundary from exactly this pattern; validate against real upstream files, not assumed schemas; never use `.get(key, {})` for required fields
4. **SKILL.md overload** -- 45 blocks cannot fit in one file; keep SKILL.md under 300 lines; use progressive disclosure via commands/ and agents/ directories
5. **Agent coordination deadlocks** -- Define explicit operation phases with a dependency graph; agents within a phase run sequentially; coherence review runs after each phase boundary, not at the end

## Implications for Roadmap

Based on research, the build follows a strict dependency chain. The Design Registry is the foundation everything stands on. Agents layer on top in the order their data dependencies allow. Presentation and governance features come last.

### Phase 1: Design Registry Core + Skill Scaffold
**Rationale:** Every other component depends on registry read/write operations. The slot-api, schema validation, and atomic write infrastructure must be solid and tested before any agent writes to the registry. The SKILL.md scaffold and directory structure must be established to respect the 500-line limit.
**Delivers:** Working Design Registry with CRUD operations, schema validation, change journal, version history, session management, and the SKILL.md skeleton with security rules and path conventions.
**Addresses:** T1 (Design Registry), T8 (Schema Validation), T9 (Version History -- basic), T10 (Partial-state Tolerance -- gap marker support in schemas), T12 (Structured Logging -- shared_io.py)
**Avoids:** Pitfall 1 (context exhaustion -- projection queries built in), Pitfall 2 (SKILL.md overload -- scaffold enforces progressive disclosure), Pitfall 3 (JSON corruption -- atomic writes and file partitioning), Pitfall 6 (traceability integrity -- mandatory trace fields in schemas)

### Phase 2: Requirements Ingestion Pipeline
**Rationale:** Components cannot be proposed without ingested requirements. The ingestion pipeline bridges the upstream skill boundary, which is the highest-risk integration point (3 confirmed bugs in the analogous concept-dev boundary).
**Delivers:** Working `/sysdev:init` command that reads requirements-dev registries, validates upstream schemas, translates to local slot format, and presents inventory for user confirmation.
**Addresses:** T2 (Requirements Ingestion)
**Avoids:** Pitfall 4 (schema mismatch -- validate_upstream.py runs first)

### Phase 3: Structural Decomposition + Approval Gate
**Rationale:** The first design act and the first agent. This phase validates the entire agent-to-registry-to-approval-gate workflow end-to-end. If this works, all subsequent agents follow the same pattern.
**Delivers:** Working `/sysdev:decompose` command with AI-driven component proposals, rationale, and developer accept/reject/modify workflow.
**Addresses:** T3 (Structural Decomposition), T4 (Approval Gate), D1 (AI Component Rationale)
**Avoids:** Pitfall 5 (coordination deadlocks -- single agent, no coordination needed yet)

### Phase 4: Interface Resolution + Behavioral Contracts
**Rationale:** These two agents form the design triad with structural decomposition. Interfaces define component boundaries; behavioral contracts define obligations. Both reuse the approval gate pattern from Phase 3.
**Delivers:** Working `/sysdev:interface` and `/sysdev:contract` commands.
**Addresses:** T5 (Interface Resolution), T6 (Behavioral Contracts)

### Phase 5: Traceability + Impact Analysis
**Rationale:** With components, interfaces, and contracts in the registry, traceability chains can be constructed and impact analysis becomes meaningful. These features integrate all prior design artifacts.
**Delivers:** Working `/sysdev:trace` and `/sysdev:impact` commands. Full need-to-requirement-to-component-to-interface-to-contract chains.
**Addresses:** T7 (Traceability Weaving), D2 (Impact Analysis)
**Avoids:** Pitfall 6 (traceability integrity -- completeness checks, not just consistency)

### Phase 6: Views, Diagrams, and Risk
**Rationale:** Presentation-layer features that depend on populated design state. These are valuable but not blocking the core design workflow.
**Delivers:** Working `/sysdev:diagram`, `/sysdev:risk`, and `/sysdev:status` commands. D2/Mermaid diagrams, risk scores, dashboard.
**Addresses:** D8 (Diagram Generation), D4 (Risk Scoring -- basic), D7 (View Synthesis -- basic)

### Phase 7: Orchestration + Coherence Review
**Rationale:** The chief-systems-engineer agent orchestrates multi-agent workflows and runs coherence review. This requires all domain agents to exist first. This phase also adds `/sysdev:review` for milestone gating.
**Delivers:** Working `/sysdev:review` command with coherence review, milestone gating, and full agent orchestration. `/sysdev:resume` for session recovery.
**Addresses:** T11 (Orchestration -- full), D5 (Coherence Review), D9 (Milestone Gating)
**Avoids:** Pitfall 5 (coordination deadlocks -- dependency graph enforced by orchestrator)

### Phase Ordering Rationale

- **Phases 1-2 are foundation:** Registry and ingestion must exist before any agent can operate. These phases have zero LLM agent code -- they are pure Python infrastructure.
- **Phase 3 is the validation gate:** If the structural-decomposition agent works end-to-end through the registry and approval gate, the pattern is proven for all subsequent agents.
- **Phases 4-5 follow data dependencies:** Interfaces need components; contracts need interfaces; traceability needs all three. This ordering is not a preference -- it is a constraint.
- **Phases 6-7 are enhancement layers:** Views, diagrams, risk, and orchestration add value but the core design workflow functions without them.
- **This matches the feature dependency graph from FEATURES.md:** T1 -> T2 -> T3 -> T5/T6 -> T7 -> D2/D4/D5.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1 (Design Registry):** Complex -- 125 requirements across 6 sub-blocks. The slot-api projection query design and schema definitions are critical decisions that affect everything downstream. Needs `/gsd:research-phase`.
- **Phase 2 (Ingestion):** High risk -- upstream schema boundary is where the 3 known bugs occurred. Needs `/gsd:research-phase` to map exact upstream file structures.
- **Phase 7 (Orchestration):** The dependency graph and coherence rule engine are novel. No direct upstream pattern to copy. Needs `/gsd:research-phase`.

Phases with standard patterns (skip research-phase):
- **Phase 3 (Structural Decomposition):** Direct replication of requirements-dev agent pattern. Well-documented.
- **Phase 4 (Interface Resolution):** Same agent pattern as Phase 3.
- **Phase 5 (Behavioral Contracts):** Same agent pattern as Phase 3.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All recommendations derived from working upstream skill (requirements-dev) and Anthropic's official authoring guide. Zero speculation. |
| Features | HIGH | Derived from 478 baselined requirements with full block-to-feature mapping and MBSE tool landscape analysis. |
| Architecture | HIGH | Based on upstream skill patterns, 478-requirement specification, and Anthropic skill authoring constraints. 10-phase build order is dependency-driven. |
| Pitfalls | HIGH | Based on 3 confirmed upstream bugs, documented Claude Code GitHub issues, and Anthropic documentation. All pitfalls have concrete evidence. |

**Overall confidence:** HIGH

### Gaps to Address

- **Downstream handoff schema:** The output format for design-impl (skill #4) is not yet defined. Define the `.system-dev/` output schema in Phase 1 so downstream consumers know what to expect.
- **Approval gate UX:** The exact interaction pattern for accept/reject/modify is not specified in the upstream skill. Phase 3 will need to prototype and validate this.
- **Agent context budgeting:** The 2000-token-per-query budget is a guideline, not tested. Phase 1 should include synthetic load testing with a 100-component registry.
- **Hook reliability:** The PostToolUse hook pattern (hooks.json) has MEDIUM confidence from upstream. Need to verify it works reliably for state updates in a multi-agent context.
- **Parallel agent execution:** PROJECT.md mentions hybrid parallel/sequential orchestration, but Claude Code subagent parallelism has known issues (GitHub #4580). Phase 7 may need to fall back to sequential-only execution.

## Sources

### Primary (HIGH confidence)
- requirements-dev SKILL.md and scripts/ (16 Python scripts) -- working production skill, direct pattern source
- 478 requirements specification from brainstorming/.requirements-dev/ -- complete requirements baseline
- Anthropic skill authoring best practices -- official guidance on SKILL.md limits, progressive disclosure, context management
- CROSS-SKILL-ANALYSIS.md -- 3 bugs, 8 gaps from the concept-dev to requirements-dev boundary

### Secondary (HIGH confidence)
- INCOSE MBSE tool landscape analysis (IBM Rhapsody, Cameo, Visure) -- competitive feature baseline
- Claude Code GitHub issues #22365, #4580, #5024 -- documented performance issues with large sessions and multi-agent JSON serialization

### Tertiary (MEDIUM confidence)
- Multi-agent architecture patterns (Event Sourcing for Autonomous Agents, CloudGeometry) -- general patterns, not Claude Code-specific

---
*Research completed: 2026-02-28*
*Ready for roadmap: yes*
