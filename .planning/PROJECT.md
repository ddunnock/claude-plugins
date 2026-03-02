# System Dev — AI-Assisted Systems Design Platform

## What This Is

A Claude Code skill implementing the System Design phase (#3) of the INCOSE SE lifecycle. It ingests requirements-dev outputs (needs, requirements, traceability, V&V plans) and guides the developer through structured system design: structural decomposition, interface resolution, behavioral contracts, traceability weaving, and impact analysis. All design artifacts persist in a central Design Registry with schema validation, version history, and change journaling. The skill produces traceable design artifacts that feed into design-impl (skill #4).

## Core Value

The developer's design decisions are captured as explicit, reviewable, traceable records in a Design Registry — so architectural choices are visible, auditable, and consistent across AI agent sessions (NEED-001, NEED-002).

## Current Milestone: v1.1 Views & Diagrams

**Goal:** Make design state visible through contextual views and D2/Mermaid diagrams

**Target features:**
- View synthesizer: on-demand contextual views from registry slot subsets with gap indicators
- View assembler: snapshot-consistent assembly with declarative view specifications
- Diagram renderer: D2 structural and Mermaid behavioral diagram output
- Diagram generator: template-driven generation with abstraction layers

## Current State

**Shipped:** v1.0 (2026-03-02)
**Codebase:** 12,498 LOC Python, 14 JSON schemas, 303 tests
**Architecture:** SlotAPI central hub with 14 slot types, 3 agents, generic approval gate

v1.0 delivers the complete design pipeline: requirements ingestion → structural decomposition → interface resolution → behavioral contracts → traceability weaving → impact analysis. All design artifacts are traceable from stakeholder needs through V&V assignments.

**Not yet built:** Views/diagrams (v1.1), risk/volatility tracking (future), orchestration/coherence review (future).

## Requirements

### Source of Truth

478 requirements across 45 blocks (12 top-level + 33 sub-blocks) defined in:
- `~/projects/brainstorming/.requirements-dev/requirements_registry.json` — machine-readable
- `~/projects/brainstorming/.requirements-dev/deliverables/REQUIREMENTS-SPECIFICATION.md` — human-readable
- `~/projects/brainstorming/.requirements-dev/needs_registry.json` — 48 stakeholder needs

**Non-negotiable:** Every GSD phase must reference the specific REQ-IDs applicable to that phase. The JSON registries are the authority; REQUIREMENTS.md summarizes by category with REQ-ID references.

### Top-Level Blocks (12)

| Block | Needs | Reqs | Role |
|-------|-------|------|------|
| design-registry | 15 | 31 | Central store: named/typed slots, pure storage & query |
| chief-systems-engineer | 6 | 20 | Orchestration, phase gating, developer interaction |
| behavioral-contract-agent | 3 | 14 | Behavioral obligations, V&V planning per component |
| interface-resolution-agent | 3 | 13 | Interface identification, protocol definition |
| requirements-synchronizer | 3 | 12 | Upstream requirements ingestion, drift detection |
| structural-decomposition-agent | 2 | 11 | Component decomposition from requirements |
| impact-analysis-agent | 2 | 12 | Change propagation, blast radius analysis |
| traceability-weaver | 3 | 11 | Cross-artifact traceability chains |
| diagram-renderer | 2 | 11 | Visual output from design state |
| view-synthesizer | 4 | 12 | Multi-perspective design views |
| risk-registry | 3 | 14 | Design risk identification and tracking |
| volatility-tracker | 2 | 11 | Requirement/design change velocity |

### Validated

- ✓ Design Registry with named/typed slots, CRUD, schema validation, versioning, change journal — v1.0
- ✓ Slot storage engine with atomic writes, crash recovery, optimistic locking — v1.0
- ✓ Requirements ingestion from upstream registries with delta detection — v1.0
- ✓ Structural decomposition agent with gap detection and stale flagging — v1.0
- ✓ Generic approval gate (accept/reject/modify) for all proposal types — v1.0
- ✓ Interface resolution agent with boundary discovery and protocol enrichment — v1.0
- ✓ Behavioral contract agent with INCOSE obligations and V&V assignment — v1.0
- ✓ Traceability graph with chain validation (need→req→comp→intf→cntr→V&V) — v1.0
- ✓ Impact analysis with forward/backward BFS and configurable depth limits — v1.0
- ✓ Write-time trace enforcement (warn-but-allow with gap markers) — v1.0

### Active (v1.1)

- [ ] Context-sensitive view synthesis from registry subsets (view-synthesizer, view-assembler — 20 reqs)
- [ ] D2/Mermaid diagram generation at multiple abstraction levels (diagram-renderer, diagram-generator — 18 reqs)

### Future

- [ ] Risk registry with composite scoring and FMEA
- [ ] Volatility tracking with stability metrics
- [ ] Chief-systems-engineer orchestration and coherence review
- [ ] Milestone gating and agent resilience
- [ ] Coherence reviewer (cross-concern consistency checking)

### Out of Scope

- Fixing upstream concept-dev ↔ requirements-dev schema bugs (CROSS-SKILL-ANALYSIS.md) — address separately
- Mobile/web UI — this is a Claude Code CLI skill
- Real-time collaboration — single-developer workflow
- Code generation — that's design-impl (skill #4)
- Full SysML v2 engine — JSON schemas inspired by SysML concepts instead

## Context

### INCOSE Lifecycle Position

```
concept-dev (#1) → requirements-dev (#2) → system-dev (#3) → design-impl (#4) → [future phases]
```

### Upstream Inputs (from requirements-dev)

| Artifact | Location | Content |
|----------|----------|---------|
| needs_registry.json | .requirements-dev/ | 48 stakeholder needs |
| requirements_registry.json | .requirements-dev/ | 478 requirements |
| traceability_registry.json | .requirements-dev/ | Bidirectional need→req→V&V links |
| source_registry.json | .requirements-dev/ | Sources with confidence levels |
| assumption_registry.json | .requirements-dev/ | Assumptions (active/challenged/invalidated) |

### Downstream Outputs (to design-impl)

Design artifacts in the Design Registry:
- Component specifications (structural decomposition)
- Interface definitions (protocols, data formats, contracts)
- Behavioral contracts (obligations, verification approaches)
- Traceability chains (need → requirement → component → interface → contract → V&V)
- Impact analysis results

### Architecture Patterns

- **Agent model:** Data-prep-then-AI-reasoning — agents prepare data via SlotAPI, Claude reasons in command workflows
- **Design Registry:** Central hub — all agents read/write through SlotAPI, no direct agent-to-agent calls (NEED-007)
- **Gate discipline:** Developer approval at each phase boundary via generic ApprovalGate (NEED-013, REQ-259–266)
- **Consistency with upstream:** Follow requirements-dev patterns (JSON registries, ${CLAUDE_PLUGIN_ROOT} paths, security rules)

### Reference Materials

- `~/projects/claude-plugins/_references/skill-authoring-best-practices.md` — Anthropic skill authoring guide
- `~/projects/claude-plugins/_references/SKILL.md` — Example multi-phase skill (spec-validator)
- `~/projects/claude-plugins/skills/requirements-dev/` — Upstream skill (pattern reference)
- `~/projects/claude-plugins/skills/requirements-dev/CROSS-SKILL-ANALYSIS.md` — Known integration gaps

## Constraints

- **Skill format:** Must follow Anthropic's skill authoring best practices (SKILL.md < 500 lines, progressive disclosure, third-person description)
- **Context window:** Design Registry and agent interactions must be token-efficient — slots accessed on demand, not bulk-loaded
- **Upstream compatibility:** Ingest requirements-dev output as-is (current schema, known bugs accepted)
- **Plugin structure:** Consistent with requirements-dev and concept-dev skill structures (commands/, agents/, scripts/, references/, templates/, data/)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 478 reqs are design reqs FOR the skill, not user data | Requirements define what to build, not what the skill processes | ✓ Good |
| GSD REQUIREMENTS.md summarizes categories with REQ-ID refs | 478 reqs too many for inline display; JSON is queryable source of truth | ✓ Good |
| Design Registry as JSON files | Consistent with upstream skills; LLM-editable; no external dependencies | ✓ Good |
| Work with current requirements-dev output | Don't fix upstream bugs in this skill's scope | ✓ Good — gap markers handle all known bugs |
| Data-prep-then-AI-reasoning agent model | Agents prepare data and format output; AI reasoning stays in command workflows | ✓ Good — testable without AI, clean separation |
| Generic ApprovalGate via config-driven state machine | One engine for all proposal types; declarative rules in approval-rules.json | ✓ Good — zero code changes for new proposal types |
| JSON Schema Draft 2020-12 with additionalProperties: false | Strict validation catches field typos; all slot types use same standard | ✓ Good |
| Atomic write via temp-file + fsync + rename | Crash recovery with no corrupt files; proven pattern | ✓ Good |
| Forward-replay version reconstruction | Journal diffs are old→new; replay is simpler than reverse-apply | ✓ Good |
| Singleton tgraph-current for traceability graph | One materialized graph with staleness detection; auto-rebuild when stale | ✓ Good |
| Warn-but-allow trace enforcement | Never blocks writes; injects gap markers for broken references | ✓ Good — zero impact on existing tests |
| BFS with visited set for impact analysis | Cycle-safe traversal; depth limits and type filtering | ✓ Good |
| Deterministic slot IDs (type:upstream-id) for ingestion | SlotAPI.ingest() accepts pre-determined IDs; enables delta detection | ✓ Good |
| One-level stale cascade (interface→contract only) | Prevents cascade explosion; each agent checks independently | ✓ Good |

---
*Last updated: 2026-03-02 after v1.1 milestone start*
