# System Dev — AI-Assisted Systems Design Platform

## What This Is

A Claude Code skill implementing the System Design phase (#3) of the INCOSE SE lifecycle. It ingests requirements-dev outputs (needs, requirements, traceability, V&V plans) and guides the developer through structured system design: structural decomposition, interface resolution, behavioral contracts, diagram generation, impact analysis, and traceability weaving. All design artifacts persist in a central Design Registry accessible by 6 top-level agents and 33 sub-blocks, producing design artifacts that feed into design-impl (skill #4).

## Core Value

The developer's design decisions are captured as explicit, reviewable, traceable records in a Design Registry — so architectural choices are visible, auditable, and consistent across AI agent sessions (NEED-001, NEED-002).

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

### Sub-Blocks (33)

slot-storage-engine (42 reqs), schema-validator (17), slot-api (14), approval-gate (11), change-journal (11), delta-detector (10), ingestion-engine (10), version-manager (10), coherence-reviewer (9), change-tracer (8), change-responder (8), component-proposer (8), contract-proposer (8), graph-builder (8), interface-proposer (8), path-computer (8), relevance-ranker (8), view-assembler (8), abstraction-manager (8), orchestrator (8), contract-generator (7), diagram-generator (7), obligation-deriver (7), output-formatter (7), resilience-handler (7), snapshot-manager (7), trend-tracker (7), vv-planner (7), chain-maintainer (6), fmea-engine (6), metric-computer (6), risk-calculator (6), governance-authority (5)

### Requirement Distribution

- **By type:** Functional (153), Quality (156), Interface (74), Constraint (66), Performance (30)
- **By priority:** High (287), Medium (182), Low (10)

### Validated

(None yet — ship to validate)

### Active

All 478 requirements are active scope for this skill.

### Out of Scope

- Fixing upstream concept-dev ↔ requirements-dev schema bugs (CROSS-SKILL-ANALYSIS.md) — address separately
- Mobile/web UI — this is a Claude Code CLI skill
- Real-time collaboration — single-developer workflow

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
| REQUIREMENTS-SPECIFICATION.md | .requirements-dev/deliverables/ | Human-readable spec |
| TRACEABILITY-MATRIX.md | .requirements-dev/deliverables/ | Traceability tables |
| VERIFICATION-MATRIX.md | .requirements-dev/deliverables/ | V&V method assignments |

### Downstream Outputs (to design-impl)

Design artifacts in the Design Registry:
- Component specifications (structural decomposition)
- Interface definitions (protocols, data formats, contracts)
- Behavioral contracts (obligations, verification approaches)
- Traceability chains (need → requirement → component → interface → contract → V&V)
- Diagrams (system overview, block detail, sub-block detail)
- Risk registry entries
- Impact analysis results

### Architecture Patterns

- **Agent model:** Hybrid — some agents spawn as Claude Code subagents for parallel work (like GSD), others are interactive sequential phases. Classification based on independence analysis.
- **Design Registry:** Central hub — all agents read/write through slot-api, no direct agent-to-agent calls (NEED-007)
- **Gate discipline:** Developer approval at each phase boundary (NEED-013, REQ-259–266)
- **Consistency with upstream:** Follow requirements-dev patterns (JSON registries, ${CLAUDE_PLUGIN_ROOT} paths, security rules, cross-cutting notes)

### Reference Materials

- `~/projects/claude-plugins/_references/skill-authoring-best-practices.md` — Anthropic skill authoring guide
- `~/projects/claude-plugins/_references/SKILL.md` — Example multi-phase skill (spec-validator)
- `~/projects/claude-plugins/_references/claude-cookbooks/skills/` — Skills API cookbook
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
| 478 reqs are design reqs FOR the skill, not user data | Requirements define what to build, not what the skill processes | — Pending |
| GSD REQUIREMENTS.md summarizes categories with REQ-ID refs | 478 reqs too many for inline display; JSON is queryable source of truth | — Pending |
| Hybrid agent model (parallel + sequential) | Matches GSD operational pattern; agents classified by independence | — Pending |
| Work with current requirements-dev output | Don't fix upstream bugs in this skill's scope | — Pending |
| Design Registry as JSON files | Consistent with upstream skills; LLM-editable; no external dependencies | — Pending |

---
*Last updated: 2026-02-28 after initialization*
