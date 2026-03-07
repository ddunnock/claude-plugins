# Architecture Research

**Domain:** Claude Code skill implementing INCOSE System Design phase (45 blocks, 478 requirements)
**Researched:** 2026-02-28
**Confidence:** HIGH (based on upstream skill patterns, requirements specification, and Anthropic skill authoring constraints)

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SKILL.md (< 500 lines)                             │
│              Entry point, commands, agent declarations                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  COMMANDS (user-facing slash commands)                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ :init    │ │ :decomp  │ │ :iface   │ │ :contract│ │ :trace   │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ :diagram │ │ :impact  │ │ :risk    │ │ :status  │ │ :resume  │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│       │            │            │            │            │             │
├───────┴────────────┴────────────┴────────────┴────────────┴─────────────┤
│                                                                         │
│  AGENTS (LLM sub-agents spawned by commands)                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │ chief-systems-  │ │ structural-     │ │ interface-      │           │
│  │ engineer        │ │ decomposition   │ │ resolution      │           │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │ behavioral-     │ │ traceability-   │ │ view-           │           │
│  │ contract        │ │ weaver          │ │ synthesizer     │           │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │ impact-analysis │ │ risk-registry   │ │ diagram-        │           │
│  │                 │ │                 │ │ renderer        │           │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘           │
│           │                   │                   │                     │
├───────────┴───────────────────┴───────────────────┴─────────────────────┤
│                                                                         │
│  SCRIPTS (deterministic Python, no LLM)                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                    │
│  │ slot-storage  │ │ schema-      │ │ slot-api     │                    │
│  │ -engine       │ │ validator    │ │              │                    │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                    │
│  │ change-      │ │ version-     │ │ ingestion-   │                    │
│  │ journal      │ │ manager      │ │ engine       │                    │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                    │
│         │                │                │                             │
├─────────┴────────────────┴────────────────┴─────────────────────────────┤
│                                                                         │
│  DESIGN REGISTRY (.system-dev/)                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  slots/               schemas/           state.json             │    │
│  │  ├── components/      ├── component.json  index.json            │    │
│  │  ├── interfaces/      ├── interface.json  change-journal.json   │    │
│  │  ├── contracts/       ├── contract.json   versions/             │    │
│  │  ├── requirements/    ├── requirement.json                      │    │
│  │  ├── traceability/    ├── traceability.json                     │    │
│  │  ├── risk/            ├── risk.json                             │    │
│  │  ├── diagrams/        └── ...                                   │    │
│  │  └── ...                                                        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Boundaries

### Layer 1: SKILL.md + Commands (User Interface)

| Component | Responsibility | Maps To |
|-----------|----------------|---------|
| SKILL.md | Entry point, command registry, agent declarations, behavioral rules, security rules | Top-level skill definition (< 500 lines) |
| sysdev:init | Initialize workspace, ingest upstream requirements, create Design Registry | requirements-synchronizer (REQ-026..030), ingestion-engine (REQ-242..250), delta-detector (REQ-234..241) |
| sysdev:decompose | Structural decomposition of requirements into components | structural-decomposition-agent (REQ-031..033), component-proposer (REQ-251..258), approval-gate (REQ-259..266) |
| sysdev:interface | Interface resolution between components | interface-resolution-agent (REQ-034..037), contract-generator (REQ-267..272), interface-proposer (REQ-278..282), change-responder (REQ-273..277) |
| sysdev:contract | Behavioral contract derivation | behavioral-contract-agent (REQ-038..041), obligation-deriver (REQ-283..288), contract-proposer (REQ-294..298) |
| sysdev:trace | Traceability graph construction and validation | traceability-weaver (REQ-042..044), graph-builder (REQ-304..309), chain-maintainer (REQ-299..303) |
| sysdev:diagram | Diagram generation from design state | diagram-renderer (REQ-063..065), view-synthesizer (REQ-058..062), view-assembler (REQ-354..359), relevance-ranker (REQ-360..364), output-formatter (REQ-365..369), diagram-generator (REQ-370..375), abstraction-manager (REQ-376..380) |
| sysdev:impact | Impact analysis for design changes | impact-analysis-agent (REQ-045..047), path-computer (REQ-310..315), change-tracer (REQ-316..320) |
| sysdev:risk | Risk computation and FMEA | risk-registry (REQ-066..069), risk-calculator (REQ-381..385), fmea-engine (REQ-386..390), trend-tracker (REQ-391..395) |
| sysdev:review | Coherence review and milestone gating | chief-systems-engineer (REQ-051..057), coherence-reviewer (REQ-332..337), governance-authority (REQ-344..348), orchestrator (REQ-338..343), resilience-handler (REQ-349..353) |
| sysdev:status | Dashboard showing current design state | volatility-tracker (REQ-048..050), metric-computer (REQ-321..326), snapshot-manager (REQ-327..331) |
| sysdev:resume | Resume interrupted session | Session state recovery |

### Layer 2: Agents (LLM Sub-Agents)

These are the 6 top-level domain agents from the requirements, each implemented as a Claude Code agent markdown file in `agents/`. Each agent reads from and writes to the Design Registry exclusively through the slot-api scripts.

| Agent | File | Sub-Blocks It Encompasses | Model |
|-------|------|---------------------------|-------|
| chief-systems-engineer | agents/chief-systems-engineer.md | orchestrator, coherence-reviewer, governance-authority, resilience-handler | opus |
| structural-decomposition-agent | agents/structural-decomposition.md | component-proposer, approval-gate | sonnet |
| interface-resolution-agent | agents/interface-resolution.md | contract-generator, interface-proposer, change-responder | sonnet |
| behavioral-contract-agent | agents/behavioral-contract.md | obligation-deriver, contract-proposer, vv-planner | sonnet |
| traceability-weaver | agents/traceability-weaver.md | graph-builder, chain-maintainer | sonnet |
| impact-analysis-agent | agents/impact-analysis.md | path-computer, change-tracer | sonnet |

**Non-agent top-level blocks** (these become commands or script-driven workflows, not LLM agents):

| Block | Implementation | Rationale |
|-------|----------------|-----------|
| design-registry | scripts/ (Python) | Pure storage and query -- deterministic, no LLM needed |
| requirements-synchronizer | sysdev:init command + scripts/ | Translation/ingestion is deterministic transformation |
| diagram-renderer | sysdev:diagram command + scripts/ + agent | Rendering is mostly template-driven; view synthesis needs LLM |
| view-synthesizer | agents/view-synthesizer.md | Assembling contextual views requires judgment for relevance |
| risk-registry | sysdev:risk command + agent | Risk computation is formula + LLM judgment for FMEA |
| volatility-tracker | scripts/ | Metric computation is deterministic |

### Layer 3: Scripts (Deterministic Python)

All 33 sub-blocks that are purely algorithmic become Python scripts. These form the Design Registry infrastructure and utility layer.

| Script Group | Scripts | Sub-Blocks Covered |
|-------------|---------|---------------------|
| Registry Core | slot_storage_engine.py, schema_validator.py, slot_api.py | slot-storage-engine (42 reqs), schema-validator (17 reqs), slot-api (14 reqs) |
| Registry Support | change_journal.py, version_manager.py, snapshot_manager.py | change-journal (11 reqs), version-manager (10 reqs), snapshot-manager (7 reqs) |
| Ingestion | ingestion_engine.py, delta_detector.py | ingestion-engine (10 reqs), delta-detector (10 reqs) |
| Metrics | metric_computer.py, risk_calculator.py, trend_tracker.py | metric-computer (6 reqs), risk-calculator (6 reqs), trend-tracker (7 reqs) |
| Graph | graph_builder.py, path_computer.py, chain_maintainer.py | graph-builder (8 reqs), path-computer (8 reqs), chain-maintainer (6 reqs) |
| View Pipeline | view_assembler.py, relevance_ranker.py, output_formatter.py, diagram_generator.py, abstraction_manager.py | view-assembler (8 reqs), relevance-ranker (8 reqs), output-formatter (7 reqs), diagram-generator (7 reqs), abstraction-manager (8 reqs) |
| Orchestration | orchestrator.py, resilience_handler.py | orchestrator (8 reqs), resilience-handler (7 reqs) |
| Governance | governance_authority.py, coherence_rules.py | governance-authority (5 reqs), coherence-reviewer (9 reqs -- rule engine is deterministic) |
| Session | init_session.py, update_state.py | Session lifecycle management |

### Layer 4: Design Registry (Data Store)

The Design Registry is a file-system-based JSON store in `.system-dev/` within the user's project directory. It follows the same pattern as `.requirements-dev/` and `.concept-dev/` from upstream skills.

```
.system-dev/
├── state.json                    # Session state, phase tracking
├── config.json                   # Registry configuration
├── slots/                        # Design artifact storage
│   ├── requirements/             # Ingested upstream requirements
│   │   ├── REQ-001.json
│   │   └── ...
│   ├── components/               # Structural decomposition output
│   ├── interfaces/               # Interface contracts
│   ├── contracts/                # Behavioral contracts
│   ├── traceability/             # Traceability graph
│   ├── impact/                   # Impact analysis results
│   ├── risk/                     # Risk scores and FMEA
│   ├── diagrams/                 # Generated diagram sources
│   ├── coherence/                # CSE coherence findings
│   ├── volatility/               # Volatility metrics
│   └── snapshots/                # Baseline snapshots
├── schemas/                      # JSON Schema definitions per slot type
│   ├── component.schema.json
│   ├── interface.schema.json
│   ├── contract.schema.json
│   └── ...
├── index.json                    # Slot index (id -> path, type, modified)
├── change-journal.json           # Append-only change log
├── versions/                     # Version history per slot
│   ├── REQ-001/
│   │   ├── v1.json
│   │   └── v2.json
│   └── ...
└── deliverables/                 # Human-readable output
    ├── DESIGN-SPECIFICATION.md
    ├── TRACEABILITY-REPORT.md
    └── DIAGRAMS/
```

## Recommended Skill Structure

```
system-dev/
├── SKILL.md                      # Entry point (< 500 lines)
├── commands/                     # Slash command definitions
│   ├── sysdev.init.md            # /sysdev:init
│   ├── sysdev.decompose.md       # /sysdev:decompose
│   ├── sysdev.interface.md       # /sysdev:interface
│   ├── sysdev.contract.md        # /sysdev:contract
│   ├── sysdev.trace.md           # /sysdev:trace
│   ├── sysdev.diagram.md         # /sysdev:diagram
│   ├── sysdev.impact.md          # /sysdev:impact
│   ├── sysdev.risk.md            # /sysdev:risk
│   ├── sysdev.review.md          # /sysdev:review
│   ├── sysdev.status.md          # /sysdev:status
│   └── sysdev.resume.md          # /sysdev:resume
├── agents/                       # LLM sub-agent definitions
│   ├── chief-systems-engineer.md
│   ├── structural-decomposition.md
│   ├── interface-resolution.md
│   ├── behavioral-contract.md
│   ├── traceability-weaver.md
│   ├── impact-analysis.md
│   ├── view-synthesizer.md
│   └── risk-analyst.md
├── scripts/                      # Deterministic Python
│   ├── slot_storage_engine.py    # Core: file I/O, git, crash recovery
│   ├── schema_validator.py       # Core: JSON Schema validation
│   ├── slot_api.py               # Core: capability-based access routing
│   ├── change_journal.py         # Core: append-only change log
│   ├── version_manager.py        # Core: version history and rollback
│   ├── ingestion_engine.py       # Sync: upstream translation
│   ├── delta_detector.py         # Sync: change detection
│   ├── graph_builder.py          # Trace: graph construction
│   ├── path_computer.py          # Impact: path traversal
│   ├── chain_maintainer.py       # Trace: chain validation
│   ├── metric_computer.py        # Metrics: volatility
│   ├── risk_calculator.py        # Risk: composite scoring
│   ├── trend_tracker.py          # Risk: checkpoint comparison
│   ├── view_assembler.py         # View: slot subset assembly
│   ├── relevance_ranker.py       # View: pertinence ranking
│   ├── output_formatter.py       # View: handoff format
│   ├── diagram_generator.py      # Diagram: D2/Mermaid generation
│   ├── abstraction_manager.py    # Diagram: hierarchical layers
│   ├── orchestrator.py           # Control: agent sequencing
│   ├── resilience_handler.py     # Control: failure recovery
│   ├── governance_authority.py   # Control: milestone gating
│   ├── coherence_rules.py        # Control: consistency rule engine
│   ├── snapshot_manager.py       # Baseline: checkpoint capture
│   ├── init_session.py           # Session: workspace setup
│   ├── update_state.py           # Session: state management
│   └── shared_io.py              # Shared: path validation, logging
├── schemas/                      # JSON Schema definitions (bundled)
│   ├── component.schema.json
│   ├── interface.schema.json
│   ├── contract.schema.json
│   ├── requirement.schema.json
│   ├── traceability.schema.json
│   ├── impact.schema.json
│   ├── risk.schema.json
│   ├── diagram.schema.json
│   ├── coherence.schema.json
│   ├── volatility.schema.json
│   └── snapshot.schema.json
├── references/                   # Progressive-disclosure docs
│   ├── design-registry-guide.md
│   ├── slot-type-reference.md
│   ├── agent-manifest-format.md
│   ├── incose-design-patterns.md
│   └── d2-mermaid-templates.md
├── templates/                    # Output templates
│   ├── design-specification.md
│   ├── traceability-report.md
│   └── diagram-templates/
├── data/                         # Static configuration
│   ├── agent-manifests.json      # Declared input/output slot dependencies
│   └── default-config.json       # Default registry configuration
└── tests/                        # Test suite
    ├── test_slot_storage.py
    ├── test_schema_validator.py
    ├── test_slot_api.py
    └── ...
```

### Structure Rationale

- **commands/:** One file per slash command. Each command orchestrates a design phase, calling scripts for deterministic work and agents for judgment-requiring work. Consistent with requirements-dev and concept-dev patterns.
- **agents/:** One file per LLM agent. 8 agents total (6 domain agents + view-synthesizer + risk-analyst). Sub-blocks are folded into their parent agent's prompt instructions. Agents never call each other directly -- they read/write through the Design Registry.
- **scripts/:** One file per deterministic sub-block. These are the workhorses: ~25 Python scripts handling all registry operations, graph traversal, metric computation, and orchestration logic. No LLM calls. Python stdlib + jsonschema only.
- **schemas/:** Bundled JSON Schema files shipped with the skill. Copied into `.system-dev/schemas/` on init. These define the contract between agents and the registry.
- **references/:** Progressive disclosure documents loaded by SKILL.md on specific conditions. Keeps SKILL.md under 500 lines.

## Data Flow

### Primary Data Flow: Requirements to Design Artifacts

```
Upstream (.requirements-dev/)
    │
    │  requirements_registry.json, needs_registry.json,
    │  traceability_registry.json
    │
    ▼
┌─────────────────────────────────────┐
│  /sysdev:init                       │
│  ingestion-engine + delta-detector  │
│  (scripts)                          │
└─────────────┬───────────────────────┘
              │ Writes requirement slots
              ▼
┌─────────────────────────────────────┐
│  DESIGN REGISTRY                    │
│  slot-api → schema-validator →      │
│  slot-storage-engine                │
│  (all reads/writes go through here) │
└──┬──────┬──────┬──────┬──────┬──────┘
   │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│decomp││iface ││contr ││trace ││impact│
│agent ││agent ││agent ││weaver││agent │
└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘
   │       │       │       │       │
   │  Each agent reads input slots, │
   │  produces output slots,        │
   │  through slot-api              │
   ▼       ▼       ▼       ▼       ▼
┌─────────────────────────────────────┐
│  DESIGN REGISTRY (updated)          │
│  components, interfaces, contracts, │
│  traceability graph, impact paths   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  /sysdev:review                     │
│  chief-systems-engineer             │
│  coherence review + milestone gate  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  /sysdev:diagram + /sysdev:risk     │
│  view pipeline + risk computation   │
│  (human-readable outputs)           │
└─────────────────────────────────────┘
               │
               ▼
         Downstream (design-impl #4)
```

### Developer Interaction Flow

```
Developer
    │
    ├─→ /sysdev:decompose ─→ structural-decomposition-agent
    │                              │
    │                              ▼
    │                        component-proposer (script)
    │                              │
    │                              ▼
    │   ◄──────────────────  approval-gate (script)
    │   Accept/Reject/Modify       │
    │   ────────────────────►      │
    │                              ▼
    │                        Design Registry (committed)
```

Every design decision passes through an approval gate (NEED-013, REQ-259..266). The developer sees proposals, makes decisions, and only approved content persists. This is consistent across all domain agents.

### Registry Internal Flow

```
Agent Request
    │
    ▼
slot-api.py
    ├── capability check (REQ-215..224)
    ├── [write] schema-validator.py (REQ-190..206)
    │         │
    │         ▼
    │   slot-storage-engine.py (REQ-149..189)
    │         ├── write-to-temp + atomic-rename
    │         ├── update index.json
    │         ├── git commit
    │         ├── notify change-journal.py
    │         └── notify version-manager.py
    │
    └── [read] slot-storage-engine.py
              └── index lookup → file read → return JSON
```

## Architectural Patterns

### Pattern 1: Hub-and-Spoke via Design Registry

**What:** All inter-agent communication flows through the Design Registry. Agents never call each other directly. Each agent declares input slot types (reads) and output slot types (writes) in a machine-readable manifest (REQ-147).

**When to use:** Every agent interaction.

**Trade-offs:**
- Pro: Complete decoupling; agents can be developed, tested, and replaced independently
- Pro: Full audit trail via change-journal
- Pro: Natural checkpoint/resume boundary (registry state is the checkpoint)
- Con: Slightly more I/O than direct agent calls
- Con: Requires careful schema design upfront

This is the single most important architectural decision. It is mandated by NEED-007 and enforced by REQ-005, REQ-006, and the per-agent constraint requirements (REQ-070..079).

### Pattern 2: Script/Agent Split

**What:** Sub-blocks that perform deterministic operations (storage, validation, graph traversal, metric computation) are Python scripts. Sub-blocks requiring judgment (decomposition rationale, interface negotiation, contract derivation, coherence review) are LLM agents.

**When to use:** Every sub-block classification decision.

**Trade-offs:**
- Pro: Scripts are fast, testable, deterministic (REQ-187, REQ-205)
- Pro: Agents focus on what LLMs do well (reasoning, synthesis)
- Pro: Scripts have zero LLM token cost
- Con: Requires clear boundary -- some blocks could go either way (e.g., coherence-reviewer rules engine is a script, but CSE judgment layer is an agent)

### Pattern 3: Approval Gate Pattern

**What:** Design proposals are staged, presented to the developer, and only committed after explicit approval. Rejected proposals return to the proposing agent with rationale.

**When to use:** Every design artifact that commits to the registry (components, interfaces, behavioral contracts).

**Trade-offs:**
- Pro: Developer retains control (NEED-013)
- Pro: Rejection rationale feeds back into improved proposals
- Con: Slower than autonomous operation (but this is intentional for design decisions)

### Pattern 4: Graceful Degradation

**What:** Every agent and script produces partial output with explicit gap markers when prerequisites are incomplete, rather than failing (REQ-090..098, REQ-130..134).

**When to use:** All registry reads where upstream data may be absent.

**Trade-offs:**
- Pro: System works incrementally -- partial designs are valid intermediate states
- Pro: Prevents cascading failures when one agent hasn't run yet
- Con: Consumers must check for gap markers (adds complexity)

## Anti-Patterns

### Anti-Pattern 1: Direct Agent-to-Agent Communication

**What people do:** Have the structural-decomposition-agent call the interface-resolution-agent directly.
**Why it's wrong:** Breaks audit trail, creates tight coupling, makes checkpoint/resume impossible (violates NEED-007).
**Do this instead:** Agent A writes to registry, Agent B reads from registry. Orchestrator manages sequencing.

### Anti-Pattern 2: Monolithic Script

**What people do:** Put all registry logic in one giant Python file.
**Why it's wrong:** 42 requirements for slot-storage-engine alone; mixing concerns makes testing impossible.
**Do this instead:** One script per sub-block. Shared utilities in shared_io.py. Each script is independently testable.

### Anti-Pattern 3: Bulk-Loading Registry into Agent Context

**What people do:** Read the entire registry into an agent's context window.
**Why it's wrong:** Token-inefficient; registries can grow to thousands of slots. Violates NEED-004 (500KB partition limit).
**Do this instead:** Agents read specific slots by type/id. View-synthesizer assembles contextual subsets. Relevance-ranker filters to pertinent content.

### Anti-Pattern 4: Schemas as Afterthought

**What people do:** Define slot schemas after agents are built.
**Why it's wrong:** Schema defines the contract between all components. Changing schema later requires updating every agent and script.
**Do this instead:** Define schemas first (Phase 1 of build). They are the API contract.

## Block-to-Component Mapping (45 Blocks to Skill Structure)

### Design Registry Block (1 top-level + 5 sub-blocks) → Scripts

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| design-registry | Distributed across scripts + schemas/ | Infrastructure | 31 |
| slot-storage-engine | scripts/slot_storage_engine.py | Script | 42 |
| schema-validator | scripts/schema_validator.py | Script | 17 |
| slot-api | scripts/slot_api.py | Script | 14 |
| change-journal | scripts/change_journal.py | Script | 11 |
| version-manager | scripts/version_manager.py | Script | 10 |

### Requirements Synchronizer Block (1 top-level + 2 sub-blocks) → Command + Scripts

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| requirements-synchronizer | commands/sysdev.init.md | Command | 12 |
| ingestion-engine | scripts/ingestion_engine.py | Script | 10 |
| delta-detector | scripts/delta_detector.py | Script | 10 |

### Structural Decomposition Block (1 top-level + 2 sub-blocks) → Command + Agent

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| structural-decomposition-agent | agents/structural-decomposition.md | Agent | 11 |
| component-proposer | Embedded in agent prompt | Agent sub-task | 8 |
| approval-gate | scripts/approval_gate.py | Script | 11 |

### Interface Resolution Block (1 top-level + 3 sub-blocks) → Command + Agent

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| interface-resolution-agent | agents/interface-resolution.md | Agent | 13 |
| contract-generator | Embedded in agent prompt | Agent sub-task | 7 |
| interface-proposer | Embedded in agent prompt | Agent sub-task | 8 |
| change-responder | Embedded in agent prompt | Agent sub-task | 8 |

### Behavioral Contract Block (1 top-level + 3 sub-blocks) → Command + Agent

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| behavioral-contract-agent | agents/behavioral-contract.md | Agent | 14 |
| obligation-deriver | Embedded in agent prompt | Agent sub-task | 7 |
| contract-proposer | Embedded in agent prompt | Agent sub-task | 8 |
| vv-planner | Embedded in agent prompt | Agent sub-task | 7 |

### Traceability Weaver Block (1 top-level + 2 sub-blocks) → Command + Agent + Scripts

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| traceability-weaver | agents/traceability-weaver.md | Agent | 11 |
| graph-builder | scripts/graph_builder.py | Script | 8 |
| chain-maintainer | scripts/chain_maintainer.py | Script | 6 |

### Impact Analysis Block (1 top-level + 2 sub-blocks) → Command + Agent + Scripts

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| impact-analysis-agent | agents/impact-analysis.md | Agent | 12 |
| path-computer | scripts/path_computer.py | Script | 8 |
| change-tracer | scripts/change_tracer.py (or embedded in agent) | Script | 8 |

### Diagram Renderer Block (1 top-level + 5 sub-blocks) → Command + Scripts + Agent

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| diagram-renderer | commands/sysdev.diagram.md | Command | 11 |
| diagram-generator | scripts/diagram_generator.py | Script | 7 |
| abstraction-manager | scripts/abstraction_manager.py | Script | 8 |
| output-formatter | scripts/output_formatter.py | Script | 7 |
| relevance-ranker | scripts/relevance_ranker.py | Script | 8 |
| view-assembler | scripts/view_assembler.py | Script | 8 |

### View Synthesizer Block (1 top-level) → Agent

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| view-synthesizer | agents/view-synthesizer.md | Agent | 12 |

### Risk Registry Block (1 top-level + 3 sub-blocks) → Command + Agent + Scripts

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| risk-registry | agents/risk-analyst.md | Agent | 14 |
| risk-calculator | scripts/risk_calculator.py | Script | 6 |
| fmea-engine | Embedded in risk-analyst agent | Agent sub-task | 6 |
| trend-tracker | scripts/trend_tracker.py | Script | 7 |

### Chief Systems Engineer Block (1 top-level + 4 sub-blocks) → Command + Agent + Scripts

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| chief-systems-engineer | agents/chief-systems-engineer.md | Agent | 20 |
| orchestrator | scripts/orchestrator.py | Script | 8 |
| coherence-reviewer | scripts/coherence_rules.py (rules) + embedded in CSE agent (judgment) | Hybrid | 9 |
| governance-authority | scripts/governance_authority.py | Script | 5 |
| resilience-handler | scripts/resilience_handler.py | Script | 7 |

### Volatility Tracker Block (1 top-level + 2 sub-blocks) → Scripts

| Req Block | Skill Component | Type | Reqs |
|-----------|----------------|------|------|
| volatility-tracker | scripts/metric_computer.py (combined) | Script | 11 |
| metric-computer | scripts/metric_computer.py | Script | 6 |
| snapshot-manager | scripts/snapshot_manager.py | Script | 7 |

## Build Order (Dependency-Driven)

### Phase 1: Foundation -- Design Registry Core

**Must build first.** Every other component depends on registry read/write operations.

1. **schemas/** -- Define all slot type JSON Schemas (the API contract)
2. **slot_storage_engine.py** -- File I/O, atomic writes, git integration, crash recovery
3. **schema_validator.py** -- JSON Schema validation
4. **slot_api.py** -- Capability-based routing layer
5. **change_journal.py** -- Append-only change log
6. **version_manager.py** -- Version history and rollback
7. **init_session.py** -- Workspace creation, `.system-dev/` scaffold
8. **SKILL.md** -- Skeleton with security rules, paths, and sysdev:init command
9. **sysdev.init.md** -- Init command (workspace + basic registry)

**Blocks covered:** design-registry, slot-storage-engine, schema-validator, slot-api, change-journal, version-manager
**Requirement coverage:** ~125 requirements (26% of total)

### Phase 2: Ingestion Pipeline

**Depends on:** Phase 1 (registry exists to write into)

1. **ingestion_engine.py** -- Upstream requirement translation
2. **delta_detector.py** -- Change detection between upstream and registry
3. **sysdev.init.md** -- Complete init command with ingestion
4. **shared_io.py** -- Common path validation, logging utilities

**Blocks covered:** requirements-synchronizer, ingestion-engine, delta-detector
**Requirement coverage:** ~32 additional requirements

### Phase 3: Structural Decomposition

**Depends on:** Phase 2 (requirements ingested to decompose)

1. **agents/structural-decomposition.md** -- LLM agent for component proposals
2. **approval_gate.py** -- Developer accept/reject/modify workflow
3. **sysdev.decompose.md** -- Decompose command

**Blocks covered:** structural-decomposition-agent, component-proposer, approval-gate
**Requirement coverage:** ~30 additional requirements

### Phase 4: Interface Resolution

**Depends on:** Phase 3 (components exist to define interfaces between)

1. **agents/interface-resolution.md** -- LLM agent for interface contracts
2. **sysdev.interface.md** -- Interface command

**Blocks covered:** interface-resolution-agent, contract-generator, interface-proposer, change-responder
**Requirement coverage:** ~36 additional requirements

### Phase 5: Behavioral Contracts

**Depends on:** Phase 3 (components exist), Phase 4 optional (interfaces enrich contracts)

1. **agents/behavioral-contract.md** -- LLM agent for behavioral obligations
2. **sysdev.contract.md** -- Contract command

**Blocks covered:** behavioral-contract-agent, obligation-deriver, contract-proposer, vv-planner
**Requirement coverage:** ~36 additional requirements

### Phase 6: Traceability

**Depends on:** Phases 3-5 (design artifacts exist to trace)

1. **graph_builder.py** -- Traceability graph construction
2. **chain_maintainer.py** -- Chain validation
3. **agents/traceability-weaver.md** -- LLM agent for graph assembly
4. **sysdev.trace.md** -- Trace command

**Blocks covered:** traceability-weaver, graph-builder, chain-maintainer
**Requirement coverage:** ~25 additional requirements

### Phase 7: Impact Analysis + Risk

**Depends on:** Phase 6 (traceability graph exists to traverse)

1. **path_computer.py** -- Forward/backward path traversal
2. **change_tracer.py** -- Requirement-level impact tracing
3. **agents/impact-analysis.md** -- LLM agent for impact assessment
4. **risk_calculator.py** -- Composite risk scoring
5. **trend_tracker.py** -- Checkpoint comparison
6. **agents/risk-analyst.md** -- LLM agent for FMEA
7. **sysdev.impact.md** -- Impact command
8. **sysdev.risk.md** -- Risk command

**Blocks covered:** impact-analysis-agent, path-computer, change-tracer, risk-registry, risk-calculator, fmea-engine, trend-tracker
**Requirement coverage:** ~61 additional requirements

### Phase 8: Views + Diagrams

**Depends on:** Phases 3-7 (design content exists to visualize)

1. **view_assembler.py** -- Slot subset assembly
2. **relevance_ranker.py** -- Pertinence ranking
3. **output_formatter.py** -- Handoff format production
4. **diagram_generator.py** -- D2/Mermaid generation
5. **abstraction_manager.py** -- Hierarchical layers
6. **agents/view-synthesizer.md** -- LLM agent for contextual views
7. **sysdev.diagram.md** -- Diagram command

**Blocks covered:** view-synthesizer, view-assembler, relevance-ranker, output-formatter, diagram-renderer, diagram-generator, abstraction-manager
**Requirement coverage:** ~56 additional requirements

### Phase 9: Orchestration + Coherence Review

**Depends on:** All domain agents exist (Phases 3-8)

1. **orchestrator.py** -- Agent invocation sequencing
2. **resilience_handler.py** -- Failure recovery
3. **governance_authority.py** -- Milestone gating
4. **coherence_rules.py** -- Consistency rule engine
5. **agents/chief-systems-engineer.md** -- LLM agent for coherence judgment
6. **sysdev.review.md** -- Review command

**Blocks covered:** chief-systems-engineer, orchestrator, coherence-reviewer, governance-authority, resilience-handler
**Requirement coverage:** ~49 additional requirements

### Phase 10: Status + Metrics + Polish

**Depends on:** All above phases

1. **metric_computer.py** -- Volatility metrics
2. **snapshot_manager.py** -- Baseline snapshots
3. **sysdev.status.md** -- Dashboard command
4. **sysdev.resume.md** -- Resume command
5. **update_state.py** -- Session state management

**Blocks covered:** volatility-tracker, metric-computer, snapshot-manager
**Requirement coverage:** ~28 additional requirements

## Integration Points

### Upstream Integration (requirements-dev)

| Artifact | Format | Integration Pattern |
|----------|--------|---------------------|
| requirements_registry.json | JSON | Direct file read during sysdev:init; delta-detector for re-sync |
| needs_registry.json | JSON | Direct file read during sysdev:init for traceability chain roots |
| traceability_registry.json | JSON | Direct file read for upstream traceability links |
| source_registry.json | JSON | Optional read for provenance metadata |

### Downstream Integration (design-impl)

| Artifact | Format | Integration Pattern |
|----------|--------|---------------------|
| .system-dev/ directory | JSON slots | design-impl reads slot files directly or through a future API |
| DESIGN-SPECIFICATION.md | Markdown | Human-readable summary of design state |
| D2/Mermaid sources | Text | Diagram files compilable by standard tooling |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Command → Agent | Agent spawned by command with context from registry reads | Command pre-loads relevant slot data into agent context |
| Command → Script | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/SCRIPT.py [args]` | Scripts are stateless CLI tools |
| Agent → Registry | Agent calls scripts via Bash tool to read/write slots | Never direct file access |
| Script → Script | Direct Python function calls within same process | e.g., slot_api.py calls schema_validator.py |

## Design Registry Implementation Decision

**Recommended:** JSON files on disk with git backend, managed by Python scripts.

**Why not SQLite:** Consistent with upstream skills (requirements-dev, concept-dev use JSON files). LLM agents edit JSON natively. Git provides version history and diff capability for free. No additional dependencies.

**Why not in-memory:** Design artifacts must persist across sessions (NEED-002). Must survive unplanned termination (REQ-024).

**Why git backend:** REQ-023 mandates it. Provides version history, rollback, diff, and merge capabilities. The slot-storage-engine commits each write.

**Key constraints:**
- Individual slot files stay under 500KB (REQ-020) for reliable LLM editing
- JSON serialization only, UTF-8 (REQ-182)
- POSIX-compatible filesystem operations (REQ-185)
- Python stdlib + jsonschema only (REQ-184, REQ-204)

## Sources

- `/Users/dunnock/projects/brainstorming/.requirements-dev/deliverables/REQUIREMENTS-SPECIFICATION.md` -- 478 requirements across 45 blocks (HIGH confidence, primary source)
- `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/SKILL.md` -- Upstream skill architecture pattern (HIGH confidence, verified implementation)
- `/Users/dunnock/projects/claude-plugins/skills/concept-dev/SKILL.md` -- Another upstream skill pattern (HIGH confidence, verified implementation)
- `/Users/dunnock/projects/claude-plugins/_references/SKILL.md` -- Multi-phase skill example (HIGH confidence, reference implementation)
- `/Users/dunnock/projects/claude-plugins/skills/system-dev/.planning/PROJECT.md` -- Project context and architecture decisions (HIGH confidence, project authority)
- Anthropic skill authoring best practices -- SKILL.md < 500 lines, progressive disclosure, ${CLAUDE_PLUGIN_ROOT} paths (HIGH confidence, referenced in CLAUDE.md)

---
*Architecture research for: Claude Code skill implementing INCOSE System Design phase*
*Researched: 2026-02-28*
