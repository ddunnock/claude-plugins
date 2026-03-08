# Phase 9: Diagram Templates & Quality - Research

**Researched:** 2026-03-07
**Status:** Ready for planning

## Phase Goal

Diagram generation becomes template-driven with configurable abstraction layers, deterministic output, and structured logging. Enhances `diagram_generator.py` without introducing new slot types or commands.

## Requirements Analysis

| Req ID | Description | Key Constraint |
|--------|-------------|----------------|
| DIAG-05 | Hierarchical abstraction layers for readability | View-spec driven; system vs component levels |
| DIAG-07 | Templates from configurable template registry | Jinja2 `.j2` files with manifest; two-tier (built-in + user override) |
| DIAG-08 | Deterministic output for same input | Sorted data before template rendering; exclude header comments only |
| DIAG-10 | Structured log entries for generation operations | Mirror Phase 7 `view.*` pattern as `diagram.*` namespace |

## Codebase Analysis

### Current Architecture (Phase 8)

`diagram_generator.py` has three layers:
1. **Pure generators**: `generate_d2(view) -> str` (line 53) and `generate_mermaid(view) -> str` (line 282) — hardcoded string building with `lines.append()`
2. **Format resolver**: `_resolve_format(override, spec) -> (fmt, type)` (line 168) — maps hints/overrides to format+type tuples
3. **Orchestrator**: `generate_diagram(api, spec, workspace, schemas_dir, format_override) -> dict` (line 203) — assembles view, resolves format, generates, writes slot

**Helpers**: `_sanitize_id()` (line 24), `_GAP_COLORS` (line 17), `_compute_diagram_slot_id()` (line 39)

### Phase 7 Logging Pattern (Reference Implementation)

`view_assembler.py` establishes the logging pattern to mirror:
- `logger = logging.getLogger(__name__)` at module level
- INFO events: `view.operation` key with `view.elapsed_ms`, using `extra={}` dict
- DEBUG events: guarded by `logger.isEnabledFor(logging.DEBUG)`
- Namespace prefix: `view.*` — Phase 9 uses `diagram.*`
- Timing: `time.perf_counter()` pairs around operations, `round(elapsed, 2)`

### Schemas to Modify

**`view-spec.json`** (60 lines): Needs optional `abstraction_level` enum field. Currently has `diagram_hint` as optional enum — same pattern. Schema uses `additionalProperties: false`, so field must be explicitly added.

**`diagram.json`** (30 lines): Needs optional `generation_elapsed_ms` field. Currently has `additionalProperties: false` — must add field and keep it optional (not in `required`).

### Templates Directory

`templates/` exists but is empty (only `.gitkeep`). Ready for Jinja2 template files and `manifest.json`.

### init_workspace.py

Creates registry dirs but does NOT create `.system-dev/templates/` for user overrides. Needs addition at line 82 area.

### BUILTIN_SPECS (view_assembler.py:764)

Five built-in specs. Relevant ones need `abstraction_level` added:
- `system-overview` — natural candidate for `abstraction_level: "system"`
- `component-detail` — natural candidate for `abstraction_level: "component"`

## Technical Research

### Jinja2 Template Strategy

**Template extraction approach**: The current `generate_d2()` and `generate_mermaid()` functions build output via `lines.append()`. Templates should reproduce this exact output structure:

```jinja2
{# d2-structural.j2 #}
# Diagram: {{ spec_name }} (structural)
# Generated from snapshot: {{ snapshot_id }}
{% for section in sections %}
...
{% endfor %}
```

**Custom filters needed**:
- `|sanitize_id` — wraps existing `_sanitize_id()` Python function
- `|gap_color` — wraps existing `_GAP_COLORS` lookup
- `|truncate_label` — truncates long labels (new, for readability)

**Template context dict**: Templates receive a flat dict built from the view:
```python
{
    "spec_name": str,
    "snapshot_id": str,
    "sections": list[dict],  # pre-sorted
    "edges": list[dict],     # pre-sorted
    "gaps": list[dict],      # pre-sorted
    "abstraction_level": str, # "system" or "component"
}
```

### Template Registry Architecture

**Two-tier resolution**:
1. Built-in: `templates/manifest.json` + `templates/*.j2` in skill directory
2. User override: `.system-dev/templates/*.j2` — same filename takes precedence

**manifest.json schema**:
```json
{
  "templates": [
    {
      "name": "d2-structural",
      "file": "d2-structural.j2",
      "format": "d2",
      "diagram_type": "structural"
    }
  ]
}
```

**Resolution order** (from CONTEXT.md decisions):
1. `spec.diagram_template` explicit field (new optional field on view-spec)
2. `format + diagram_hint` auto-selects (e.g., d2 + structural -> d2-structural.j2)
3. ValueError if no match

### Abstraction Layer Implementation

**System level** (top-level components only):
- Collapse children: show parent with count badge "(3 sub-components, 5 interfaces)"
- Aggregate edges: roll up child-to-child edges to parent-to-parent with count labels

**Component level** (all sub-elements expanded):
- Current behavior — no changes needed, this is the default

**Implementation approach**: Pre-process the view data BEFORE passing to templates. Create `_apply_abstraction_level(view, level)` function that:
1. Groups slots by parent component
2. At system level: replaces children with count badges on parents
3. Aggregates edges between same parent pairs
4. Returns modified view dict (never mutates original)

This keeps templates simple — they don't need abstraction logic, just render what they receive.

### Determinism Strategy

**Current state**: `generate_d2()` and `generate_mermaid()` iterate sections/edges/gaps in the order they appear in the view dict. The view assembler already sorts edges (line 503) and ranks slots (line 671).

**What's needed**: Ensure template rendering is deterministic by:
1. Sorting all input data before template rendering (sections by type, slots by name, edges by source+target, gaps by type+index)
2. Using Jinja2's `sort` filter or pre-sorting in Python (CONTEXT.md says pre-sort in Python)
3. Excluding header comments (timestamps, snapshot IDs) from determinism comparison — these are "unstable" fields

**Testing**: Call generator twice with same input, compare output. The `_compute_diagram_slot_id()` content-hash approach already validates determinism — same source = same hash.

### Structured Logging Integration Points

In `generate_diagram()` orchestrator (line 203):
- `diagram.format_resolved` — after `_resolve_format()` call (INFO)
- `diagram.template_loaded` — after template lookup (INFO)
- `diagram.generation_complete` — after source generated (INFO, with elapsed_ms, line_count)
- `diagram.slot_written` — after `api.ingest()` (INFO, with slot_id, status)

In template rendering (DEBUG level):
- `diagram.node_rendered` — per node in template
- `diagram.edge_rendered` — per edge in template
- `diagram.gap_rendered` — per gap in template

DEBUG-level logging within templates is awkward with Jinja2. Better approach: log in the Python rendering wrapper, not in templates themselves.

## Validation Architecture

### Determinism Verification
- Generate diagram twice from same view input
- Compare output strings (excluding header comments)
- Verify content-hash slot IDs match

### Template Registry Verification
- Load template by explicit name
- Load template by format+hint auto-selection
- Verify user override takes precedence over built-in
- Verify ValueError on missing template

### Abstraction Layer Verification
- System-level view has fewer nodes than component-level
- System-level shows count badges on collapsed components
- System-level aggregates edges with count labels
- Component-level matches current output

### Logging Verification
- Capture log output during generation
- Verify INFO events contain required fields
- Verify DEBUG events only appear when DEBUG enabled
- Verify `diagram.*` namespace prefix on all log entries

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Jinja2 dependency adds complexity | Pin version in requirements; keep template features minimal (no macros/inheritance) |
| Template output differs from hardcoded | Write migration tests comparing template vs hardcoded output |
| Abstraction layer edge aggregation complexity | Pre-process in Python, keep templates simple |
| Determinism broken by template whitespace | Use `-%}` trim blocks; test byte-identical output |

## Dependencies

- **Jinja2**: New dependency — needs to be added to requirements/dependencies
- **Phase 8**: `generate_d2()`, `generate_mermaid()`, `generate_diagram()` — all modified
- **Phase 7**: Logging patterns from `view_assembler.py` — reference only, not modified

## RESEARCH COMPLETE

---
*Phase: 09-diagram-templates-quality*
*Research completed: 2026-03-07*
