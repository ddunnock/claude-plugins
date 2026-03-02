# Phase 5: Traceability Weaving + Impact Analysis - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Build and query complete traceability chains (need to requirement to component to interface to contract to V&V) and compute change impact (blast radius) across the design graph. This phase adds graph construction, chain validation, impact path computation, and write-time trace enforcement to the existing Design Registry.

</domain>

<decisions>
## Implementation Decisions

### Chain Construction (Graph Source)
- Graph built from BOTH sources: pairwise traceability-link slots AND embedded fields (requirement_ids, relationships, component_ids, source_requirement_ids on committed slots)
- Edges are merged with deduplication; when both sources provide conflicting edges, include both and flag divergence as a separate finding (union strategy)
- Edge types include REQ-305 types (derives_from, allocated_to, verified_by, conflicts_with) PLUS inferred relationship edges (communicates_with, constrained_by) derived from interface/contract structure

### Graph Persistence
- Hybrid cached-with-staleness approach: graph materialized as traceability-graph slot in registry, with a staleness marker tracking whether upstream slots changed since last build
- Auto-rebuild when stale; manual rebuild also available
- Aligns with REQ-307/308 (write graph to registry)

### Gap & Break Detection
- Three-level severity classification:
  - Critical: chain fully broken (no path exists between endpoints)
  - Warning: partial chain (path exists but with gaps)
  - Info: orphan element (not connected to any chain)
- Orphan detection covers ALL slot types (needs, requirements, components, interfaces, contracts, V&V items)
- Divergences between traceability-link slots and embedded fields reported in a SEPARATE section from the gap report (not mixed together)

### Trace Command Output
- Chain-per-need summary: group by stakeholder need, each need shows its full chain (need to req to comp to intf to cntr to V&V) with breaks highlighted inline
- Completeness percentage displayed at top of output

### Impact Computation
- Default unlimited depth, configurable via --depth N flag
- Tree view output: hierarchical tree from changed element outward, each level shows affected elements with type and relationship
- Support --type filter to show only specific slot types in output (full graph still traversed internally)
- Results are BOTH displayed to user AND persisted as impact-analysis slot in registry (REQ-047/318)
- Uncertainty markers included when graph coverage < 100% for traversed subgraph (REQ-315)

### Write-Time Enforcement (TRAC-04)
- Warn but allow: writes succeed with warnings listing missing trace fields; gap markers automatically added to the slot (consistent with XCUT-01 partial-state tolerance)
- Scope: design elements only (components, interfaces, contracts) — not upstream-ingested slots (needs, requirements, sources, assumptions)
- Implemented as a separate trace_validator.py alongside schema_validator.py — called by SlotAPI after schema validation passes (semantic rules separate from structural rules)
- Reference validation: check that all referenced slot IDs actually exist in the registry; flag non-existent references as warnings (catches typos and stale references early)

### Claude's Discretion
- Internal graph data structure and traversal algorithm
- Staleness detection mechanism specifics
- Structured logging format details (REQ-303/309/320)
- Performance optimization approach for REQ-312 (5-second target for 10k nodes)

</decisions>

<specifics>
## Specific Ideas

- Requirements are highly prescriptive for this phase: REQ-299..320 plus REQ-452 define most of the functional behavior
- The graph-builder sub-agent pattern (REQ-304..309) and chain-maintainer pattern (REQ-299..303) map to the established agent structure from phases 3-4
- Impact analysis results feed directly into Phase 6 (risk scoring uses blast radius data)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `traceability-link` schema: already has from_id/to_id/link_type/gap_markers — foundation for graph edges
- `SchemaValidator` (scripts/schema_validator.py): pattern for trace_validator.py to follow
- `SlotAPI` (scripts/registry.py): entry point for all reads/writes, will integrate trace validator
- `ApprovalGate` (scripts/approval_gate.py): generic field-copy mechanism shows how to extend SlotAPI workflows
- `gap_markers` pattern: already present on components, interfaces, contracts — reuse for trace warnings

### Established Patterns
- Agent pattern from phases 3-4: agent class with prepare/analyze/create workflow (DecompositionAgent, InterfaceAgent, ContractAgent)
- Command pattern: markdown workflow files in commands/ calling Python scripts
- Test pattern: unit tests per script + integration tests for full command workflows
- All slot types already registered in SLOT_TYPE_DIRS and SLOT_ID_PREFIXES

### Integration Points
- `requirement_ids` on components, interfaces, contracts — existing trace-relevant fields
- `relationships` on components — adjacency data for inferred edges
- `source_requirement_ids` on contract obligations — V&V chain link
- `vv-rules.json` — V&V method assignments complete the chain endpoint
- New slot types needed: traceability-graph, impact-analysis (schemas + registry registration)

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-traceability-weaving-impact-analysis*
*Context gathered: 2026-03-01*
