# Phase 8: Diagram Generation Core - Context

**Gathered:** 2026-03-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate valid D2 structural and Mermaid behavioral diagrams from view handoff format, with gap markers rendered as visually distinct placeholders. Introduces a new `diagram` slot type written through SlotAPI, a new `diagram_generator.py` script, and a new `/system-dev:diagram` command. Does not include template registries, abstraction layers, determinism guarantees, or structured logging (those are Phase 9).

Requirements in scope: DIAG-01, DIAG-02, DIAG-03, DIAG-04, DIAG-06, DIAG-09

Out of scope for this phase: hierarchical abstraction layers (DIAG-05, Phase 9), configurable template registry (DIAG-07, Phase 9), deterministic output (DIAG-08, Phase 9), structured logging (DIAG-10, Phase 9).

</domain>

<decisions>
## Implementation Decisions

### D2 / Mermaid Mapping
- **Spec-driven mapping**: view specs declare a `diagram_hint` field (`"structural"` or `"behavioral"`). Structural produces D2, behavioral produces Mermaid
- Built-in spec defaults: `system-overview` -> structural (D2), `traceability-chain` -> behavioral (Mermaid), `component-detail` -> structural (D2), `interface-map` -> structural (D2), `gap-report` -> no diagram hint
- D2 structural: components as **nested containers** (rectangle shapes), interfaces as **labeled connections** between containers, contracts as connection annotations
- Mermaid behavioral: **flowchart** (`graph TD`) with nodes for slots and labeled arrows for edges. Relationship types shown as edge labels (e.g., `-->|traces|`)

### Gap Placeholder Style
- **Dashed + labeled** placeholders in both D2 and Mermaid: dashed-border shapes with `[GAP]` prefix in the label
- **Color-coded by severity**: error = red stroke (#dc3545), warning = orange (#e6a117), info = gray (#888888). Same colors in both D2 and Mermaid
- Suggestion text appears as **source code comments** near the gap node (not in the rendered label)
- Gap nodes connect to their expected context with dashed arrows where appropriate

### Diagram Slot Schema
- New slot type: `"diagram"` registered in `SLOT_TYPE_DIRS` -> `"registry/diagram/"`
- Core fields: `slot_id`, `slot_type`, `name`, `version`, `format` (d2/mermaid), `diagram_type` (structural/behavioral), `source` (diagram source code), `source_view_spec`, `source_snapshot_id`, `slot_count`, `gap_count`
- **Content-hash slot IDs**: `diag-{spec_name}-{sha256(source)[:12]}` for deterministic identification
- **Update on change only**: if content hash matches existing slot for same spec, skip write (no-op). If content differs, version-bump the existing slot

### Command Interface
- New command: `/system-dev:diagram` with dedicated `commands/diagram.md` and `scripts/diagram_generator.py`
- Accepts **named specs only** (built-in or file path). No ad-hoc patterns — diagrams are intentional artifacts
- Default output: write diagram slot to registry via SlotAPI AND print diagram source to stdout with header (format, type, storage path)
- **--format override**: default follows spec's `diagram_hint`, but `--format d2` or `--format mermaid` overrides. Error if no hint and no --format specified
- Supports `--param key=value` for parameterized specs (same as view command)

### Claude's Discretion
- Exact D2 style attributes (font sizes, colors for non-gap elements, spacing)
- Mermaid flowchart direction (TD vs LR) based on content shape
- How "unlinked" section slots render in diagrams
- Edge label formatting and truncation for long relationship types
- Error handling for invalid or empty view specs

</decisions>

<specifics>
## Specific Ideas

- The generator should iterate the view's `edges` array directly to emit diagram connections — this was the design intent from Phase 7
- Components should feel like "containers" in D2 — not just boxes, but regions that could hold sub-elements (this sets up Phase 9's abstraction layers)
- Gap placeholders should be immediately recognizable as "something missing" — the dashed + colored style should make gaps impossible to miss
- The `diagram_hint` field on view-specs aligns with XCUT-03 (externalizable rules) — the mapping isn't hardcoded in the generator

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `view_assembler.py:assemble_view()`: Produces the exact input format the diagram generator consumes (sections, edges, gaps, metadata)
- `view_assembler.py:_extract_edges()`: Edge extraction already done — generator just iterates the edges array
- `view_assembler.py:BUILTIN_SPECS`: Will need `diagram_hint` field added to built-in specs
- `registry.py:SlotAPI`: create/update methods for writing diagram slots (XCUT-04)
- `schema_validator.py:SchemaValidator`: Validates diagram slots against new `schemas/diagram.json`
- `shared_io.py`: Atomic writes for diagram slot files
- `scripts/init_workspace.py`: May need to create `registry/diagram/` directory on init

### Established Patterns
- Script + command .md pattern: `scripts/diagram_generator.py` + `commands/diagram.md`
- SlotAPI for all registry access (XCUT-04) — diagram writes go through `api.create()` / `api.update()`
- SchemaValidator for output validation — new `schemas/diagram.json` schema
- Content-hash IDs (Phase 7 snapshot_id pattern) — reuse for diagram slot_id
- Deep copy for immutability — view data should not be mutated during generation

### Integration Points
- New command: `commands/diagram.md` (orchestrates Claude + diagram_generator.py)
- New script: `scripts/diagram_generator.py` (D2 and Mermaid generation engines)
- New schema: `schemas/diagram.json` (diagram slot schema for DIAG-04)
- Modified: `registry.py:SLOT_TYPE_DIRS` — add `"diagram": "registry/diagram"`
- Modified: `schemas/view-spec.json` — add optional `diagram_hint` field
- Modified: `view_assembler.py:BUILTIN_SPECS` — add `diagram_hint` to built-in specs
- Modified: `scripts/init_workspace.py` — create `registry/diagram/` directory
- Reads from: view handoff format (output of assemble_view)
- Writes to: `"diagram"` slot type only (DIAG-09 preservation)

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-diagram-generation-core*
*Context gathered: 2026-03-07*
