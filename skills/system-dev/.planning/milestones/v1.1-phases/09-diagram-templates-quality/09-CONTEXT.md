# Phase 9: Diagram Templates & Quality - Context

**Gathered:** 2026-03-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Diagram generation becomes template-driven with configurable abstraction layers, deterministic output, and structured logging. Enhances the existing `diagram_generator.py` with four capabilities without introducing new slot types or commands. Does not modify Phase 8's core D2/Mermaid generation logic — wraps it with template infrastructure.

Requirements in scope: DIAG-05, DIAG-07, DIAG-08, DIAG-10

Out of scope: SVG/PNG rendering (external tooling), interactive diagrams, real-time updates, new slot types, new commands.

</domain>

<decisions>
## Implementation Decisions

### Template Format & Registry (DIAG-07)
- **Jinja2 text templates**: Full D2/Mermaid source as `.j2` template files with data slots for sections, edges, gaps, metadata
- **Moderate Jinja2 features**: Variables, loops, conditionals, plus custom filters (`|sanitize_id`, `|gap_color`, `|truncate_label`). No macros, includes, or template inheritance
- **Two-tier template storage**: Built-in templates in skill's `templates/` directory with `manifest.json`; user overrides in `.system-dev/templates/` which take precedence by name
- **Template-to-spec mapping**: Resolution order is (1) `spec.diagram_template` explicit field, (2) format + diagram_hint auto-selects default (e.g., `d2 + structural -> d2-structural.j2`), (3) ValueError if no match
- **Built-in templates**: At minimum `d2-structural.j2`, `d2-component.j2`, `mermaid-behavioral.j2`
- Jinja2 is a new dependency for this phase

### Abstraction Layers (DIAG-05)
- **View-spec driven layers**: View specs declare an `abstraction_level` field that controls rendering granularity
- **Two levels**: `system` (top-level components only, children collapsed) and `component` (all sub-elements expanded)
- **Collapsed children at system level**: Parent component shows count badge — "(3 sub-components, 5 interfaces)" — in both D2 labels and Mermaid labels
- **Aggregated edges at system level**: Edges between child components rolled up to parent-to-parent connections with count labels (e.g., "implements (3)") when multiple edges exist between the same pair
- `abstraction_level` field added to `view-spec.json` schema as optional enum: `["system", "component"]`

### Determinism Strategy (DIAG-08)
- **Exclude comments only**: Header comments (timestamps, snapshot IDs) excluded from determinism comparison. All diagram elements (nodes, edges, styles, gaps, template structure) must be byte-identical for same input
- **Sorted context data**: All data pre-sorted before passing to Jinja2 templates — sections by type, slots by name, edges by source+target, gaps by type+index. Determinism is a data concern, not a template concern
- **Content-hash slot ID unchanged**: Keep current `diag-{spec}-{sha256(source)[:12]}` approach. Template changes that produce different output naturally produce different hashes

### Structured Logging (DIAG-10)
- **Mirror Phase 7 pattern exactly**: `diagram.*` namespace prefix (parallel to `view.*`), tiered verbosity, DEBUG guard with `logger.isEnabledFor(logging.DEBUG)`
- **INFO log points**: `diagram.format_resolved`, `diagram.template_loaded`, `diagram.generation_complete` (with elapsed_ms, line_count), `diagram.slot_written` (slot_id, status)
- **DEBUG log points**: `diagram.node_rendered`, `diagram.edge_rendered`, `diagram.gap_rendered`
- **Timing in slot metadata**: Add `generation_elapsed_ms` field to diagram slot content alongside existing fields

### Claude's Discretion
- Exact set of custom Jinja2 filters beyond the three discussed
- Template manifest.json schema and fields
- How `abstraction_level` interacts with edge aggregation implementation details
- D2 container nesting syntax for system-level collapsed components
- Mermaid subgraph usage for abstraction levels
- init_workspace changes for `.system-dev/templates/` directory creation
- Diagram schema updates for `generation_elapsed_ms` field

</decisions>

<specifics>
## Specific Ideas

- Templates should produce output visually identical to current hardcoded generators when using default settings — this is a refactor of rendering, not a redesign
- System-level diagrams should feel like "architecture overview" diagrams where you see the major building blocks and their connections, not implementation details
- Count badges on collapsed components should make it obvious that drilling into component-level will reveal more detail
- The `|sanitize_id` filter replaces the current `_sanitize_id()` Python function, making it available in templates

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `diagram_generator.py:generate_d2()` (line 53): Pure D2 generation function — rendering logic to extract into d2-structural.j2 template
- `diagram_generator.py:generate_mermaid()` (line 282): Pure Mermaid generation function — rendering logic to extract into mermaid-behavioral.j2 template
- `diagram_generator.py:_sanitize_id()` (line 24): ID sanitization — becomes `|sanitize_id` Jinja2 filter
- `diagram_generator.py:_GAP_COLORS` (line 17): Gap color mapping — becomes `|gap_color` Jinja2 filter
- `diagram_generator.py:generate_diagram()` (line 203): Orchestration layer — needs template loading and logging integration
- `diagram_generator.py:_compute_diagram_slot_id()` (line 39): Content-hash ID — stays as-is
- `view_assembler.py`: Structured logging pattern with `view.*` namespace — reference implementation for `diagram.*`
- `templates/.gitkeep`: Empty templates directory ready for Jinja2 templates and manifest

### Established Patterns
- Phase 7 structured logging: `view.*` namespace, tiered verbosity, elapsed_ms on INFO, DEBUG guard — exact pattern to mirror
- Phase 7 determinism: content-hash snapshot_id, sorted output, exclude timestamps — same approach for diagrams
- Phase 8 pure functions: generate_d2/generate_mermaid take view dict, return string — templates wrap this pattern
- XCUT-03 externalizable rules: diagram_hint on view-specs, gap-rules.json — templates continue this principle
- XCUT-04 slot-api exclusivity: diagram writes through SlotAPI.ingest() — no changes needed

### Integration Points
- Modified: `scripts/diagram_generator.py` — add template loading, Jinja2 rendering, logging, abstraction layer support
- New: `templates/manifest.json` — template registry manifest
- New: `templates/d2-structural.j2`, `templates/d2-component.j2`, `templates/mermaid-behavioral.j2` — Jinja2 templates
- Modified: `schemas/view-spec.json` — add optional `abstraction_level` field
- Modified: `schemas/diagram.json` — add `generation_elapsed_ms` field
- Modified: `scripts/init_workspace.py` — create `.system-dev/templates/` directory
- Modified: `view_assembler.py:BUILTIN_SPECS` — add `abstraction_level` to relevant built-in specs

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-diagram-templates-quality*
*Context gathered: 2026-03-07*
