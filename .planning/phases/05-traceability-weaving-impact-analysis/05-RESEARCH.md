# Phase 5: Traceability Weaving + Impact Analysis - Research

**Researched:** 2026-03-01
**Domain:** Graph construction, chain validation, impact path computation over Design Registry slots
**Confidence:** HIGH

## Summary

Phase 5 builds the traceability graph from existing registry slots (needs, requirements, components, interfaces, contracts, V&V assignments) and provides two user-facing capabilities: (1) a `trace` command that displays end-to-end chains grouped by stakeholder need with gap/break detection, and (2) an `impact` command that computes forward/backward propagation paths from any design element. Additionally, a write-time trace validator enforces mandatory trace fields on design element writes (components, interfaces, contracts).

The implementation is fundamentally a graph construction and traversal problem over JSON slot data already in the registry. No external libraries are needed -- Python's built-in `collections.deque` for BFS and dict-based adjacency lists are sufficient for the expected graph sizes (REQ-312 targets 10k nodes in 5 seconds). The phase introduces two new slot types (`traceability-graph`, `impact-analysis`), two new scripts (`traceability_agent.py`, `trace_validator.py`), two new commands (`trace.md`, `impact.md`), and integration with the existing SlotAPI write pipeline.

**Primary recommendation:** Follow the established agent pattern (data preparation class with prepare/analyze/create workflow) for the traceability agent. Implement the graph as a dict-based adjacency list with typed edges. The trace validator should follow the SchemaValidator pattern as a separate validation layer called by SlotAPI after schema validation passes.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Graph built from BOTH sources: pairwise traceability-link slots AND embedded fields (requirement_ids, relationships, component_ids, source_requirement_ids on committed slots)
- Edges merged with deduplication; conflicting edges from both sources included and flagged as divergence (union strategy)
- Edge types include REQ-305 types (derives_from, allocated_to, verified_by, conflicts_with) PLUS inferred relationship edges (communicates_with, constrained_by) from interface/contract structure
- Hybrid cached-with-staleness approach: graph materialized as traceability-graph slot in registry, with staleness marker tracking upstream changes since last build
- Auto-rebuild when stale; manual rebuild also available
- Three-level severity classification: Critical (chain fully broken), Warning (partial chain with gaps), Info (orphan element)
- Orphan detection covers ALL slot types
- Divergences between traceability-link slots and embedded fields reported in SEPARATE section from gap report
- Chain-per-need summary output grouped by stakeholder need with completeness percentage at top
- Default unlimited depth for impact, configurable via --depth N flag
- Tree view output for impact: hierarchical tree from changed element outward
- Support --type filter for impact output (full graph still traversed internally)
- Impact results BOTH displayed AND persisted as impact-analysis slot in registry
- Uncertainty markers when graph coverage < 100% for traversed subgraph
- Write-time enforcement: warn but allow; writes succeed with warnings listing missing trace fields; gap markers automatically added
- Enforcement scope: design elements only (components, interfaces, contracts) -- not upstream-ingested slots
- Implemented as separate trace_validator.py alongside schema_validator.py, called by SlotAPI after schema validation passes
- Reference validation: check that all referenced slot IDs actually exist in registry; flag non-existent references as warnings

### Claude's Discretion
- Internal graph data structure and traversal algorithm
- Staleness detection mechanism specifics
- Structured logging format details (REQ-303/309/320)
- Performance optimization approach for REQ-312 (5-second target for 10k nodes)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| TRAC-01 | Graph construction from registry slots (REQ-042..044, REQ-299..309) | Graph builder reads all slot types, constructs adjacency list from traceability-link slots + embedded fields, writes traceability-graph slot |
| TRAC-02 | Graph builder with traversal and query (REQ-304..309) | BFS/DFS traversal over adjacency list, typed edge semantics, completeness metadata computation, schema for traceability-graph slot |
| TRAC-03 | Chain validation detecting broken segments (REQ-299..303, REQ-452) | Chain walker from needs through V&V, three-level severity, gap identification at specific missing link, divergence detection |
| TRAC-04 | Traceability enforced on write (per PITFALLS.md) | trace_validator.py as separate validation layer in SlotAPI write pipeline, warn-but-allow with auto gap markers, reference existence validation |
| IMPT-01 | Forward/backward impact path computation (REQ-045..047, REQ-310..320) | BFS from target element in both directions on traceability graph, depth-limited, uncertainty markers, tree-view output |
| IMPT-02 | Path computation with configurable depth limits (REQ-310..315) | --depth N flag with default unlimited, --type filter on output, 5-second performance target for 10k nodes |
| IMPT-03 | Change tracing from modification to affected elements (REQ-316..320) | Impact-analysis slot persisted to registry, partial reports with gap markers, structured logging |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (collections, json, os, logging) | 3.12+ | Graph data structures, file I/O, logging | Zero dependencies, sufficient for adjacency list graphs |
| jsonschema | existing | Schema validation for new slot types | Already in project for Draft 2020-12 validation |
| pytest | existing | Unit and integration tests | Already in project, 222 tests passing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| collections.deque | stdlib | BFS traversal queue | Forward/backward impact path computation |
| collections.defaultdict | stdlib | Adjacency list construction | Building graph from heterogeneous edge sources |
| time.perf_counter | stdlib | Performance measurement | REQ-312 compliance verification, structured logging |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| dict adjacency list | networkx | Overkill for this scale; adds dependency; project avoids unnecessary deps |
| BFS with deque | DFS with recursion | BFS gives level-by-level traversal matching tree-view output; DFS risks stack overflow on deep graphs |
| In-memory graph | SQLite/graph DB | Project uses JSON files; no database infrastructure per Out of Scope |

## Architecture Patterns

### Recommended Project Structure
```
scripts/
  traceability_agent.py    # Graph builder + chain validator + impact computer
  trace_validator.py       # Write-time trace enforcement (called by SlotAPI)
schemas/
  traceability-graph.json  # Schema for materialized graph slot
  impact-analysis.json     # Schema for impact analysis result slot
commands/
  trace.md                 # Trace command workflow
  impact.md                # Impact command workflow
tests/
  test_traceability_agent.py      # Unit tests for graph/chain/impact
  test_trace_validator.py         # Unit tests for write-time enforcement
  test_traceability_integration.py # Integration tests for trace command
  test_impact_integration.py       # Integration tests for impact command
```

### Pattern 1: Graph as Adjacency List with Typed Edges
**What:** Represent the traceability graph as `dict[str, list[Edge]]` where each key is a node_id (slot_id) and Edge is a dict with `target`, `edge_type`, `source` (which data source provided the edge).
**When to use:** All graph operations -- construction, chain walking, impact traversal.
**Example:**
```python
# Graph internal representation
graph = {
    "nodes": {
        "need:NEED-001": {"type": "need", "name": "..."},
        "requirement:REQ-042": {"type": "requirement", "name": "..."},
        "comp-abc123": {"type": "component", "name": "..."},
    },
    "adjacency": {
        "need:NEED-001": [
            {"target": "requirement:REQ-042", "edge_type": "derives_from", "source": "traceability-link"},
            {"target": "requirement:REQ-043", "edge_type": "derives_from", "source": "embedded_field"},
        ],
    },
    "reverse_adjacency": {
        "requirement:REQ-042": [
            {"target": "need:NEED-001", "edge_type": "derives_from", "source": "traceability-link"},
        ],
    },
}
```

### Pattern 2: Two-Source Edge Collection with Divergence Detection
**What:** Collect edges from traceability-link slots AND embedded fields (requirement_ids, relationships, source_requirement_ids), deduplicate, and flag divergences.
**When to use:** Graph construction phase.
**Example:**
```python
def _collect_edges_from_links(self, api: SlotAPI) -> list[dict]:
    """Edges from traceability-link slots (explicit pairwise links)."""
    links = api.query("traceability-link")
    return [{"from": l["from_id"], "to": l["to_id"],
             "edge_type": l["link_type"], "source": "traceability-link"}
            for l in links]

def _collect_edges_from_embedded(self, api: SlotAPI) -> list[dict]:
    """Edges from embedded fields on committed slots."""
    edges = []
    # Components: requirement_ids -> allocated_to edges
    for comp in api.query("component"):
        for req_id in comp.get("requirement_ids", []):
            edges.append({"from": req_id, "to": comp["slot_id"],
                         "edge_type": "allocated_to", "source": "embedded_field"})
    # ... similar for interfaces, contracts, V&V
    return edges
```

### Pattern 3: Chain Walker (Need-to-V&V)
**What:** For each need, walk the expected chain: need -> requirement -> component -> interface -> contract -> V&V. Report breaks at each missing link level.
**When to use:** Chain validation (TRAC-03).
**Expected chain levels:**
```
Level 0: need
Level 1: requirement (via derives_from / traceability-link)
Level 2: component (via allocated_to / requirement_ids)
Level 3: interface (via component_id fields)
Level 4: contract (via interface_id / component_id)
Level 5: V&V (via vv_assignments on contracts)
```

### Pattern 4: Staleness Detection via Index Timestamps
**What:** Track the maximum `updated_at` across all source slots at graph build time. On next access, compare current max `updated_at` against stored value. If any slot is newer, graph is stale.
**When to use:** Auto-rebuild decision before trace/impact commands.
**Example:**
```python
def _check_staleness(self, api: SlotAPI, graph_slot: dict) -> bool:
    """True if any source slot was updated after graph was built."""
    built_at = graph_slot.get("built_at", "")
    for slot_type in TRACEABLE_TYPES:
        for slot in api.query(slot_type):
            if slot.get("updated_at", "") > built_at:
                return True
    return False
```

### Pattern 5: TraceValidator as SlotAPI Post-Hook
**What:** Separate validator called after schema validation passes, checking trace-relevant fields exist and referenced IDs resolve.
**When to use:** Every SlotAPI.create() and SlotAPI.update() for design element types.
**Example:**
```python
class TraceValidator:
    TRACE_FIELDS = {
        "component": ["requirement_ids"],
        "interface": ["requirement_ids", "source_component", "target_component"],
        "contract": ["component_id", "interface_id", "requirement_ids"],
    }
    DESIGN_ELEMENT_TYPES = {"component", "interface", "contract"}

    def validate(self, slot_type: str, content: dict, api: SlotAPI) -> list[dict]:
        """Return list of trace warnings (not errors). Never blocks writes."""
        if slot_type not in self.DESIGN_ELEMENT_TYPES:
            return []
        warnings = []
        # Check missing trace fields
        for field in self.TRACE_FIELDS.get(slot_type, []):
            value = content.get(field)
            if not value or (isinstance(value, list) and len(value) == 0):
                warnings.append({"field": field, "type": "missing_trace_field", ...})
        # Check reference existence
        # ...
        return warnings
```

### Anti-Patterns to Avoid
- **Building graph on every query:** The graph should be materialized as a slot and cached. Only rebuild when stale.
- **Blocking writes on trace validation failure:** TRAC-04 specifies warn-but-allow. Never raise exceptions from trace_validator.
- **Mixing divergence reports with gap reports:** CONTEXT.md explicitly requires separate sections.
- **Validating upstream-ingested slots for trace fields:** Enforcement scope is design elements only (components, interfaces, contracts).
- **Deep recursion for traversal:** Use iterative BFS with deque to avoid stack overflow on large graphs.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema validation | Custom field checking | jsonschema library (existing) | Already in project, handles Draft 2020-12 |
| Atomic file writes | Manual temp/rename | shared_io.atomic_write (existing) | Already handles fsync + rename pattern |
| Slot CRUD | Direct file I/O | SlotAPI (existing) | XCUT-04 mandates all access through SlotAPI |
| Change journaling | Custom audit log | ChangeJournal (existing) | Already integrated with SlotAPI |
| UUID generation | Custom ID scheme | uuid4 with prefix (existing pattern) | Consistent with all other slot types |

## Common Pitfalls

### Pitfall 1: Graph Edge Direction Confusion
**What goes wrong:** Edges from traceability-links have from_id/to_id which may be in either direction. Embedded fields like requirement_ids on a component mean "this component is allocated FROM these requirements" -- the edge direction is requirement -> component.
**Why it happens:** Different slot types encode relationships in different directions.
**How to avoid:** Normalize all edges to a canonical direction during collection. Build both forward AND reverse adjacency lists at construction time.
**Warning signs:** Chain walker finds no paths even when data is present.

### Pitfall 2: Stale Graph Served to Impact Analysis
**What goes wrong:** Impact analysis uses an outdated graph and reports incorrect blast radius.
**Why it happens:** Graph was built before the most recent slot changes.
**How to avoid:** Always check staleness before using the graph. Auto-rebuild if stale. Include `built_at` timestamp in graph metadata.
**Warning signs:** Impact results reference slots that no longer exist or miss recently added slots.

### Pitfall 3: Missing Reverse Edges for Backward Traversal
**What goes wrong:** Forward impact works but backward impact finds nothing because the graph only has forward adjacency.
**Why it happens:** Building only a forward adjacency list.
**How to avoid:** Build both `adjacency` (forward) and `reverse_adjacency` (backward) at graph construction time. Forward impact uses `adjacency`, backward uses `reverse_adjacency`.
**Warning signs:** `impact --direction backward` always returns empty results.

### Pitfall 4: Trace Validator Breaking Existing Tests
**What goes wrong:** Adding trace validation to SlotAPI breaks 100+ existing tests that create slots without trace fields.
**Why it happens:** Existing tests don't include requirement_ids etc. because those weren't enforced before.
**How to avoid:** Trace validator returns warnings, not errors. Warnings are used to auto-add gap markers to the slot content. Existing tests continue to pass because validation never blocks. Only add gap_markers if the caller doesn't suppress warnings (or always add them -- gap markers are informational).
**Warning signs:** Mass test failures after integrating trace_validator into SlotAPI.

### Pitfall 5: Infinite Loops in Cyclic Graphs
**What goes wrong:** BFS/DFS traversal enters infinite loop because the graph has cycles (e.g., conflicts_with is bidirectional).
**Why it happens:** Not tracking visited nodes during traversal.
**How to avoid:** Always maintain a `visited: set[str]` during any traversal. Skip nodes already in the visited set.
**Warning signs:** Impact analysis hangs or returns impossibly large result sets.

### Pitfall 6: V&V Chain Endpoint Identification
**What goes wrong:** Chain walker doesn't know how to reach V&V assignments because they're nested inside contract slots (vv_assignments array), not separate slots.
**Why it happens:** V&V assignments are embedded in contracts, not standalone slot types.
**How to avoid:** During graph construction, extract vv_assignments from each contract and create synthetic nodes (e.g., `vv:{contract_id}:{obligation_id}`) with edges from the contract. This preserves the full chain without requiring a new V&V slot type.
**Warning signs:** Chains always appear to end at contracts, never reaching V&V level.

### Pitfall 7: SlotAPI Integration Order
**What goes wrong:** Trace validator is called before system fields are set, so it can't resolve references.
**Why it happens:** SlotAPI sets slot_id, version, timestamps THEN validates schema THEN persists.
**How to avoid:** Call trace validator AFTER schema validation passes (system fields already set) but BEFORE persistence. The trace validator can safely read the content's slot_type and any referenced IDs.
**Warning signs:** Trace validator sees incomplete content or null slot_ids.

## Code Examples

### Traceability Graph Schema (traceability-graph.json)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://system-dev.local/schemas/traceability-graph.json",
  "title": "Traceability Graph Slot",
  "type": "object",
  "required": ["slot_id", "slot_type", "version", "created_at", "updated_at"],
  "properties": {
    "slot_id": { "type": "string", "pattern": "^tgraph-.+$" },
    "slot_type": { "const": "traceability-graph" },
    "version": { "type": "integer", "minimum": 1 },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "built_at": { "type": "string", "format": "date-time" },
    "nodes": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "type": { "type": "string" },
          "name": { "type": "string" }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from_id", "to_id", "edge_type"],
        "properties": {
          "from_id": { "type": "string" },
          "to_id": { "type": "string" },
          "edge_type": { "type": "string" },
          "source": { "type": "string" }
        }
      }
    },
    "completeness": {
      "type": "object",
      "properties": {
        "total_chains": { "type": "integer" },
        "complete_chains": { "type": "integer" },
        "percentage": { "type": "number" },
        "broken_chains": { "type": "integer" },
        "orphan_count": { "type": "integer" }
      }
    },
    "chain_report": {
      "type": "object",
      "properties": {
        "chains": { "type": "array" },
        "gaps": { "type": "array" },
        "divergences": { "type": "array" }
      }
    },
    "staleness_marker": { "type": "string", "format": "date-time" },
    "extensions": { "type": "object" }
  },
  "additionalProperties": false
}
```

### Impact Analysis Schema (impact-analysis.json)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://system-dev.local/schemas/impact-analysis.json",
  "title": "Impact Analysis Slot",
  "type": "object",
  "required": ["slot_id", "slot_type", "version", "created_at", "updated_at"],
  "properties": {
    "slot_id": { "type": "string", "pattern": "^impact-.+$" },
    "slot_type": { "const": "impact-analysis" },
    "version": { "type": "integer", "minimum": 1 },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "source_element": { "type": "string" },
    "direction": { "type": "string", "enum": ["forward", "backward", "both"] },
    "depth_limit": { "type": ["integer", "null"] },
    "type_filter": {
      "type": ["array", "null"],
      "items": { "type": "string" }
    },
    "paths": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "element_id": { "type": "string" },
          "element_type": { "type": "string" },
          "element_name": { "type": "string" },
          "depth": { "type": "integer" },
          "relationship": { "type": "string" },
          "children": { "type": "array" }
        }
      }
    },
    "affected_count": { "type": "integer" },
    "uncertainty_markers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "element_id": { "type": "string" },
          "reason": { "type": "string" }
        }
      }
    },
    "graph_coverage_percent": { "type": "number" },
    "gap_markers": {
      "type": "array",
      "items": { "type": "object" }
    },
    "extensions": { "type": "object" }
  },
  "additionalProperties": false
}
```

### BFS Impact Traversal
```python
from collections import deque

def compute_impact(graph: dict, start_id: str, direction: str = "forward",
                   depth_limit: int | None = None) -> list[dict]:
    """BFS traversal for forward or backward impact from a design element."""
    adj = graph["adjacency"] if direction == "forward" else graph["reverse_adjacency"]
    visited: set[str] = {start_id}
    queue: deque[tuple[str, int]] = deque([(start_id, 0)])
    result: list[dict] = []

    while queue:
        node_id, depth = queue.popleft()
        if depth_limit is not None and depth >= depth_limit:
            continue
        for edge in adj.get(node_id, []):
            target = edge["target"]
            if target not in visited:
                visited.add(target)
                node_info = graph["nodes"].get(target, {})
                result.append({
                    "element_id": target,
                    "element_type": node_info.get("type", "unknown"),
                    "element_name": node_info.get("name", target),
                    "depth": depth + 1,
                    "relationship": edge["edge_type"],
                    "from_element": node_id,
                })
                queue.append((target, depth + 1))
    return result
```

### SlotAPI Integration for Trace Validator
```python
# In SlotAPI.create() and SlotAPI.update(), after schema validation:

# Schema validation (existing)
self._validator.validate_or_raise(slot_type, content)

# Trace validation (new -- warn but allow)
if self._trace_validator:
    trace_warnings = self._trace_validator.validate(slot_type, content, self)
    if trace_warnings:
        # Auto-add gap markers for missing trace fields
        existing_markers = content.get("gap_markers", [])
        for warning in trace_warnings:
            existing_markers.append({
                "type": "missing_trace_field" if warning["type"] == "missing_trace_field"
                        else "broken_reference",
                "finding_ref": f"TRACE-{warning['field']}",
                "severity": "medium",
                "description": warning["message"],
            })
        content["gap_markers"] = existing_markers
        logger.warning("Trace warnings for %s: %s", content.get("slot_id"), trace_warnings)

# Persist (existing)
self._storage.write(slot_id, slot_type, content)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Post-hoc trace checking | Write-time enforcement (TRAC-04) | This phase | Catch missing traces at creation time, not after |
| Traceability-link slots only | Dual-source graph (links + embedded fields) | This phase | More complete graph with divergence detection |
| No materialized graph | Cached graph slot with staleness | This phase | Fast repeated queries without full reconstruction |

## Open Questions

1. **Traceability-graph slot ID convention**
   - What we know: Other materialized slots use uuid-based IDs (comp-{uuid}, intf-{uuid})
   - What's unclear: Should there be one singleton traceability-graph slot (tgraph-current) or versioned snapshots?
   - Recommendation: Use a well-known singleton ID like `tgraph-current`. The version field handles history. Impact analysis results use individual IDs (impact-{uuid}).

2. **SlotAPI constructor change for TraceValidator**
   - What we know: SlotAPI constructor takes workspace_root, schemas_dir, journal_path
   - What's unclear: Adding trace_validator as optional param vs. internal construction
   - Recommendation: Add optional `trace_validator` parameter (default None) to SlotAPI constructor. This preserves backward compatibility -- all existing callers pass no trace_validator and get no trace enforcement. Tests can pass None explicitly. Production callers pass the validator.

3. **Performance of staleness check**
   - What we know: Staleness check queries all traceable slot types and compares timestamps
   - What's unclear: Cost of querying all slots on every trace/impact invocation
   - Recommendation: Use the index.json `updated_at` field (already maintained by SlotStorageEngine) as a quick staleness proxy. If index.updated_at > graph.built_at, do full check. This avoids scanning all slots when nothing has changed.

## Sources

### Primary (HIGH confidence)
- Existing codebase: `scripts/registry.py`, `scripts/schema_validator.py`, `scripts/interface_agent.py`, `scripts/contract_agent.py`, `scripts/approval_gate.py` -- established patterns for agent structure, SlotAPI integration, schema validation
- Existing schemas: `schemas/component.json`, `schemas/interface.json`, `schemas/contract.json`, `schemas/traceability-link.json` -- field names for embedded edge extraction
- Requirements registry: REQ-042..047, REQ-299..320, REQ-452 -- functional requirements for traceability and impact analysis

### Secondary (MEDIUM confidence)
- Python stdlib documentation for collections.deque BFS patterns -- well-established algorithm

### Tertiary (LOW confidence)
- None -- this phase is primarily a data structure + algorithm problem over well-understood existing data

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all stdlib Python, no new dependencies needed
- Architecture: HIGH -- follows established project patterns (agent class, SlotAPI integration, schema-per-type)
- Pitfalls: HIGH -- derived from deep reading of existing codebase (especially SlotAPI write pipeline, V&V embedding in contracts, edge direction conventions)

**Research date:** 2026-03-01
**Valid until:** 2026-04-01 (stable -- no external dependencies to go stale)
