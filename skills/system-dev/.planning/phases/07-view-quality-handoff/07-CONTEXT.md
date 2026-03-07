# Phase 7: View Quality & Handoff - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Views are ranked by relevance, deterministic, performant, and produce output that diagram generation can consume. Enhances the existing view assembler engine (scripts/view_assembler.py) with four capabilities: relevance ranking, diagram-compatible handoff format, deterministic output, and structured logging. No new slot types or commands are introduced.

</domain>

<decisions>
## Implementation Decisions

### Relevance Ranking
- Rank slots by **relationship density** (count of connections: interfaces linked to components, contracts linked to interfaces, traceability links referencing slots)
- Count **direct + one hop** transitive connections (e.g., component → interface → contract counts for the component)
- Tie-breaking: **version descending** (most recently updated slots first), then alphabetical by name as final tiebreaker
- **Global default with per-spec override**: all views use density ranking by default; view-specs can declare an alternative `ranking` field to override (e.g., `"ranking": "alphabetical"` or `"ranking": "none"`)

### Handoff Format
- **Enrich existing view.json** rather than creating a separate diagram-input schema — one format serves both human display and diagram generation
- Add a top-level **`edges` array** listing relationships between slots (source_id, target_id, relationship_type) for direct diagram edge mapping
- Add **inline `relationships` field** on each slot listing connected slot IDs — co-located data for human readability
- Add a top-level **`metadata` section** with assembly stats: timing (elapsed_ms), per-section slot counts, ranking method used, format_version
- **Gap indicators stay as-is** — current format (scope_pattern, severity, reason, suggestion) is sufficient; diagram generator decides gap visualization

### Determinism Strategy
- Derive **snapshot_id from content hash** (hash of serialized registry state) — same content always produces same ID
- **Always deterministic** — no opt-in flag; content-based IDs and sorted output are the default behavior
- **Sorted output guaranteed**: after ranking, apply stable sort (by rank score desc, then version desc, then name asc) within each section
- `assembled_at` timestamp stays in output for human use; **determinism tested on content fields only** (sections, gaps, edges, metadata — excluding assembled_at and timing)

### Structured Logging
- Use **Python stdlib logging** via the existing `logger` (already defined but unused in view_assembler.py)
- **Tiered verbosity**: key milestones at INFO level, per-pattern details at DEBUG level
- **Timing on all INFO entries**: every INFO-level log includes `elapsed_ms` for the operation
- **Namespaced fields**: all structured log extra fields use `view.` prefix (e.g., `view.operation`, `view.slot_count`, `view.elapsed_ms`)
- INFO log points: snapshot capture, per-section match summary, gap detection summary, ranking applied, assembly complete (total time)
- DEBUG log points: individual pattern match attempts, individual gap decisions, ranking score computations

### Claude's Discretion
- Exact hashing algorithm for content-based snapshot_id
- view-spec schema changes for the `ranking` field
- Edge relationship_type taxonomy
- Performance target threshold for VIEW-12
- Exact metadata field names and structure

</decisions>

<specifics>
## Specific Ideas

- Edges array should be directly consumable by D2/Mermaid generators without transformation — Phase 8 should be able to iterate edges and emit diagram connections
- The metadata section serves double duty: structured logging captures the data, metadata exposes it in the output
- Relationship density ranking should make "hub" components (many connections) surface to the top of views — this matches how systems engineers think about architecture

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `view_assembler.py:assemble_view()` (line 365): Main assembly function to enhance — add ranking, edges, metadata, logging
- `view_assembler.py:capture_snapshot()` (line 146): Snapshot capture to modify for content-based hashing
- `view_assembler.py:_organize_hierarchically()` (line 267): Already tracks component→interface→contract relationships — reusable for edge extraction and density counting
- `view_assembler.py:logger` (line 24): Logger already defined, just needs calls added
- `schemas/view.json`: Schema to extend with edges, metadata, and inline relationships fields

### Established Patterns
- SlotAPI read-only access pattern (VIEW-10, XCUT-04) — ranking and edges must compute from snapshot, not query separately
- Deep copy for immutability — snapshot data is deep-copied, ranking should not mutate originals
- SchemaValidator for output validation — extended schema will be validated automatically
- Built-in specs pattern (BUILTIN_SPECS dict) — ranking override field follows same convention

### Integration Points
- `schemas/view.json` — must be updated to accept new fields while remaining backward-compatible
- `schemas/view-spec.json` — needs optional `ranking` field added
- `render_tree()` — may need updates to display ranking scores or edges (Claude's discretion)
- Phase 8 consumers — edges array is the primary handoff contract

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-view-quality-handoff*
*Context gathered: 2026-03-06*
