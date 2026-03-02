# Phase 6: View Assembly Core - Context

**Gathered:** 2026-03-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Construct contextual views from registry slot subsets on demand with honest gap indicators and snapshot consistency. Views are ephemeral (not persisted as separate source of truth), assembled from declarative view-specifications, and must not modify existing slots outside the view type.

Requirements in scope: VIEW-01, VIEW-02, VIEW-05, VIEW-06, VIEW-07, VIEW-08, VIEW-10

Out of scope for this phase: relevance ranking (VIEW-03, Phase 7), diagram handoff format (VIEW-04, Phase 7), determinism (VIEW-09, Phase 7), structured logging (VIEW-11, Phase 7), performance targets (VIEW-12, Phase 7).

</domain>

<decisions>
## Implementation Decisions

### View Specification Format
- Named scope patterns using glob-like syntax (e.g., `component:subsystem-x.*`, `interface:*`)
- Specs stored as JSON files in `.system-dev/view-specs/`
- Flat specs only — no composition/includes between specs
- Parameterized specs: support variables like `{component_id}` in scope patterns, resolved at runtime
- JSON format for consistency with existing schemas/ and slot files

### Gap Representation
- Gap indicators include: scope pattern that expected slots, slot type, reason for gap, and actionable suggestion (e.g., "Run /system-dev:interface to discover interfaces")
- Three severity levels: info / warning / error
- Severity determined by externalized rules in a config file (e.g., `gap-rules.json`), aligning with XCUT-03
- Gaps interleaved inline where missing slots would appear AND summarized in a top-level `gap_summary` field with counts by severity

### View Output Structure
- Hierarchical organization by relationship: components as tree roots, interfaces nested under components, contracts under interfaces
- Orphan slots (no component parent) collected in an "unlinked" section
- Field selection controlled by view spec via a `fields` directive per scope pattern
- Rich metadata block: spec_name, assembled_at, snapshot info, total_slots, total_gaps, gap_summary by severity

### Built-in View Types
- Five preset view specs shipped in `.system-dev/view-specs/`:
  1. `system-overview` — all components + their interfaces
  2. `traceability-chain` — requirements → components → interfaces → contracts
  3. `component-detail` — single component + all related slots (parameterized by `{component_id}`)
  4. `interface-map` — all interfaces grouped by component pairs
  5. `gap-report` — view optimized to highlight all gaps across the design

### Command Interface
- View command supports both spec references and ad-hoc inline scope patterns
- Default output: human-readable formatted tree with indentation
- `--json` flag for structured JSON output
- Ad-hoc patterns create a transient spec internally

### Claude's Discretion
- Snapshot consistency mechanism (how to achieve VIEW-07 atomicity)
- Exact scope pattern syntax and matching algorithm
- View schema design (VIEW-06 conformance)
- Tree rendering format for human-readable output
- Gap rule defaults for the five built-in severity configs
- Slot preservation enforcement approach (VIEW-10)

</decisions>

<specifics>
## Specific Ideas

- Requirements hold priority over discussion decisions — if a requirement contradicts a decision here, the requirement wins
- REQ-354 clarifies: views are NOT persisted as separate registry slots — they're computed on demand
- REQ-448: maintainers create/modify views by editing specifications without modifying assembler code
- Gap suggestions should reference existing skill commands (e.g., "/system-dev:interface", "/system-dev:decompose")

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `SlotAPI` (registry.py): CRUD + query by type with filters — view assembler reads through this (XCUT-04)
- `SlotStorageEngine.query()`: Already supports type + field filter queries — scope pattern matching builds on this
- `SchemaValidator` (schema_validator.py): Validates slots against JSON schemas — will validate view schema (VIEW-06)
- `shared_io.py`: Atomic writes, path validation — reusable for view spec file management
- `index.json`: Central slot index with type/version/path — can be read atomically for snapshot consistency

### Established Patterns
- All slot access through SlotAPI (XCUT-04) — view assembler MUST follow this
- JSON schemas in `schemas/` for each slot type — new `view.json` schema needed
- Structured logging via Python `logging` module — XCUT-02 compliance
- Agent scripts in `scripts/` with corresponding command `.md` files
- XCUT-03: Externalizable rules — gap severity rules must be config-driven, not hardcoded

### Integration Points
- New command: `commands/view.md` (orchestrates Claude + view_assembler.py)
- New script: `scripts/view_assembler.py` (core assembly engine)
- New schema: `schemas/view.json` (view output schema for VIEW-06)
- New directory: `.system-dev/view-specs/` (declarative view specifications)
- New config: gap severity rules file
- Reads from: all existing slot types via SlotAPI
- Does NOT write to: existing slot types (VIEW-10 preservation)

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-view-assembly-core*
*Context gathered: 2026-03-02*
