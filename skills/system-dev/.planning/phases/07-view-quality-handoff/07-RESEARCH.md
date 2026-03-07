# Phase 7: View Quality & Handoff - Research

**Researched:** 2026-03-07
**Domain:** View assembler enhancement (ranking, handoff format, determinism, logging)
**Confidence:** HIGH

## Summary

Phase 7 enhances the existing `scripts/view_assembler.py` with four capabilities: relevance ranking via relationship density, a diagram-compatible handoff format (edges array + metadata), deterministic output via content hashing, and structured logging using Python stdlib. The codebase is well-structured with clear extension points -- `assemble_view()` is the single assembly function (line 365), `capture_snapshot()` handles snapshot creation (line 146), `_organize_hierarchically()` already tracks component-interface-contract relationships (line 267), and `logger` is defined but unused (line 24).

The existing `view.json` schema uses `additionalProperties: false` at the top level, so new fields (edges, metadata) require schema updates. The `view-spec.json` schema also uses `additionalProperties: false`, requiring a schema change to add the optional `ranking` field. All 73 existing tests pass in 0.28s, providing a solid regression baseline.

**Primary recommendation:** Implement in two plans -- (1) relevance ranking + deterministic output (internal quality), (2) handoff format + structured logging (external interface). This separates computation logic from output format concerns.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Rank slots by **relationship density** (count of connections: interfaces linked to components, contracts linked to interfaces, traceability links referencing slots)
- Count **direct + one hop** transitive connections (e.g., component -> interface -> contract counts for the component)
- Tie-breaking: **version descending** (most recently updated slots first), then alphabetical by name as final tiebreaker
- **Global default with per-spec override**: all views use density ranking by default; view-specs can declare an alternative `ranking` field to override (e.g., `"ranking": "alphabetical"` or `"ranking": "none"`)
- **Enrich existing view.json** rather than creating a separate diagram-input schema -- one format serves both human display and diagram generation
- Add a top-level **`edges` array** listing relationships between slots (source_id, target_id, relationship_type) for direct diagram edge mapping
- Add **inline `relationships` field** on each slot listing connected slot IDs -- co-located data for human readability
- Add a top-level **`metadata` section** with assembly stats: timing (elapsed_ms), per-section slot counts, ranking method used, format_version
- **Gap indicators stay as-is** -- current format (scope_pattern, severity, reason, suggestion) is sufficient; diagram generator decides gap visualization
- Derive **snapshot_id from content hash** (hash of serialized registry state) -- same content always produces same ID
- **Always deterministic** -- no opt-in flag; content-based IDs and sorted output are the default behavior
- **Sorted output guaranteed**: after ranking, apply stable sort (by rank score desc, then version desc, then name asc) within each section
- `assembled_at` timestamp stays in output for human use; **determinism tested on content fields only** (sections, gaps, edges, metadata -- excluding assembled_at and timing)
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

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| VIEW-03 | View assembler supports relevance-ranked retrieval for contextual views | Relationship density ranking using `_organize_hierarchically()` relationship data; per-spec `ranking` field override |
| VIEW-04 | View assembler outputs views in a defined handoff format compatible with diagram-renderer | Edges array, inline relationships, metadata section added to view.json; format_version bump to "1.1" |
| VIEW-09 | View assembler produces deterministic output for same input state | Content-hash snapshot_id via hashlib; sorted output; determinism tested excluding assembled_at/timing |
| VIEW-11 | View assembler emits structured log entries for assembly operations | Python stdlib logging with `view.*` namespaced extra fields; INFO milestones + DEBUG details |
| VIEW-12 | View assembler meets performance target for contextual view assembly | Timing instrumentation via `time.perf_counter()`; target < 500ms for 100-slot registries |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| hashlib (stdlib) | Python 3.x | Content-based snapshot hashing | Standard library, no dependencies; SHA-256 is fast and collision-resistant |
| logging (stdlib) | Python 3.x | Structured log entries | Already imported and logger defined at line 24 |
| time (stdlib) | Python 3.x | Performance timing via perf_counter() | Monotonic clock, sub-microsecond resolution |
| json (stdlib) | Python 3.x | Deterministic serialization with sort_keys | Already imported |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| jsonschema | existing | Schema validation for extended view.json | Already used via SchemaValidator |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| hashlib SHA-256 | hashlib MD5 | SHA-256 is marginally slower but no collision concerns; use SHA-256 |
| time.perf_counter() | time.time() | perf_counter is monotonic and higher resolution; always prefer it |
| json.dumps(sort_keys=True) | canonical JSON lib | sort_keys is sufficient for determinism; no external dep needed |

## Architecture Patterns

### Code Changes Map
```
scripts/
  view_assembler.py      # ALL changes here + one new helper module
    capture_snapshot()    # MODIFY: content-hash snapshot_id
    assemble_view()       # MODIFY: add ranking, edges, metadata, logging
    _organize_hierarchically()  # READ-ONLY: reuse relationship data for edges
    _compute_density_scores()   # NEW: relationship density computation
    _extract_edges()            # NEW: build edges array from snapshot relationships
    _rank_slots()               # NEW: sort slots by density score + tiebreakers
schemas/
  view.json              # MODIFY: add edges, metadata, slot relationships fields
  view-spec.json         # MODIFY: add optional ranking field
tests/
  test_view_assembler.py # MODIFY: add tests for ranking, edges, determinism, logging
```

### Pattern 1: Relationship Density Scoring
**What:** Count connections per slot from snapshot data. Components count linked interfaces + transitive contracts. Interfaces count linked contracts + parent components. Contracts count parent interface.
**When to use:** Default ranking for all views unless overridden by spec `ranking` field.
**Implementation approach:**

The `_organize_hierarchically()` function (line 267) already builds:
- `comp_interface_map`: component_id -> list of linked interfaces
- `intf_contract_map`: interface_id -> list of linked contracts
- `linked_interfaces` / `linked_contracts` sets

These same data structures are the basis for density scoring. The density computation should happen BEFORE hierarchical organization (or in parallel) since it needs the same relationship traversal.

Density formula for a component:
```
direct_connections = len(interfaces where source_component == comp_id or target_component == comp_id)
one_hop_connections = sum(len(contracts where interface_id == intf_id) for each linked interface)
density_score = direct_connections + one_hop_connections
```

Traceability links add to density:
```
trace_connections = len(traceability_links where from_id == slot_id or to_id == slot_id)
density_score += trace_connections
```

### Pattern 2: Content-Hash Snapshot ID
**What:** Replace `uuid4()` in `capture_snapshot()` with SHA-256 hash of serialized registry state.
**When to use:** Always -- determinism is the default.
**Implementation approach:**

```python
import hashlib

# In capture_snapshot():
serialized = json.dumps(slots_by_type, sort_keys=True, separators=(',', ':'))
snapshot_id = hashlib.sha256(serialized.encode()).hexdigest()[:16]
```

Key detail: Use compact separators `(',', ':')` and `sort_keys=True` for canonical JSON. Truncate to 16 hex chars (64 bits) -- sufficient for uniqueness within a single project's registry.

### Pattern 3: Edges Array Extraction
**What:** Walk snapshot relationships and build explicit edge objects for diagram consumption.
**When to use:** Always included in assembled output.
**Implementation approach:**

Relationship types derivable from existing schema fields:
- `interface.source_component` / `interface.target_component` -> edge type: `"component_interface"`
- `contract.interface_id` -> edge type: `"interface_contract"`
- `contract.component_id` -> edge type: `"component_contract"`
- `traceability-link.from_id` / `traceability-link.to_id` -> edge type: uses `link_type` field value

Edge object shape:
```json
{
  "source_id": "comp-abc123",
  "target_id": "intf-def456",
  "relationship_type": "component_interface"
}
```

Only include edges where BOTH source and target are present in the assembled view's sections (not all registry edges, only in-view edges).

### Pattern 4: Structured Logging with Extra Fields
**What:** Use Python logging's `extra` parameter for structured data alongside message strings.
**When to use:** Every significant operation in assembly pipeline.
**Implementation approach:**

```python
import time

start = time.perf_counter()
# ... operation ...
elapsed_ms = (time.perf_counter() - start) * 1000

logger.info(
    "Snapshot captured: %d slot types, %d total slots",
    len(slots_by_type),
    total,
    extra={
        "view.operation": "snapshot_capture",
        "view.slot_count": total,
        "view.elapsed_ms": round(elapsed_ms, 2),
    },
)
```

### Anti-Patterns to Avoid
- **Mutating snapshot data during ranking:** Ranking scores must be computed separately and NOT injected into the deep-copied snapshot slots. Use a parallel dict `{slot_id: score}` instead.
- **Building edges from the full registry:** Only include edges where both endpoints are in the assembled view. The edges array describes the view's subgraph, not the full registry graph.
- **Non-deterministic iteration:** Python dicts are insertion-ordered since 3.7, but `slots_by_type` keys from `SLOT_TYPE_DIRS` iteration are deterministic. Still, always sort explicitly for the output.
- **Logging inside hot loops without level check:** DEBUG logging in per-slot loops should use `logger.isEnabledFor(logging.DEBUG)` guard to avoid string formatting overhead in production.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Content hashing | Custom hash function | `hashlib.sha256` | Proven, fast, no edge cases |
| JSON canonicalization | Custom serializer | `json.dumps(sort_keys=True, separators=(',', ':'))` | Standard, deterministic, handles nested objects |
| High-resolution timing | `datetime.now()` subtraction | `time.perf_counter()` | Monotonic, not affected by clock adjustments |
| Structured log formatting | Custom log formatter | `logging.info(..., extra={})` | Standard logging protocol, works with any handler |

## Common Pitfalls

### Pitfall 1: Schema Backward Compatibility
**What goes wrong:** Adding required fields to view.json breaks existing consumers that don't produce those fields.
**Why it happens:** New fields (edges, metadata) added as required in schema.
**How to avoid:** Make `edges` and `metadata` required in the schema (they will always be produced by the updated assembler) but ensure the assembler always populates them, even as empty arrays/objects. Bump format_version to "1.1" to signal the schema change. The existing `additionalProperties: false` on view.json means we MUST update the schema before the code, or validation will reject the new fields.
**Warning signs:** `SchemaValidationError` on assembled output.

### Pitfall 2: Determinism Violated by Timestamps
**What goes wrong:** Tests comparing full output objects fail because `assembled_at` and `elapsed_ms` differ between runs.
**Why it happens:** Including non-deterministic fields in equality comparisons.
**How to avoid:** The CONTEXT.md explicitly states: determinism tested on content fields only (sections, gaps, edges, metadata -- excluding assembled_at and timing). Create a helper function `_deterministic_content(view)` that strips volatile fields for comparison. Also note `metadata.elapsed_ms` is volatile.
**Warning signs:** Flaky tests that pass sometimes.

### Pitfall 3: Edge Duplication
**What goes wrong:** An interface with both `source_component` and `target_component` generates two edges to the same interface, or edges appear for slots not in the view.
**Why it happens:** Not filtering edges to only include in-view slot IDs, or generating symmetric edges.
**How to avoid:** Build a set of `in_view_ids` from all sections, then only emit edges where both `source_id` and `target_id` are in that set. Each relationship field generates exactly one directed edge.
**Warning signs:** Edge count higher than expected in tests.

### Pitfall 4: Ranking Score Depends on Section Ordering
**What goes wrong:** Density scores differ depending on which scope patterns are in the spec, because only matched slots contribute to relationship counting.
**Why it happens:** Computing density from matched slots only, rather than from the full snapshot.
**How to avoid:** Compute density scores from the FULL SNAPSHOT (all slots), not just matched slots. A component's density should be the same regardless of which view includes it. Then apply scores only to the slots that appear in the view.
**Warning signs:** Same component has different rank scores in different views.

### Pitfall 5: view.json additionalProperties Blocks New Fields
**What goes wrong:** Adding `edges` or `metadata` to assembled output causes schema validation to reject the output.
**Why it happens:** Current view.json has `"additionalProperties": false` at top level.
**How to avoid:** Update the schema FIRST (or simultaneously) when adding new output fields. This is the deployment order: schema update -> code update -> test update.
**Warning signs:** All assembly tests fail with validation errors after code change.

## Code Examples

### Content-Hash Snapshot ID
```python
# In capture_snapshot() -- replace uuid4() with content hash
import hashlib

serialized = json.dumps(slots_by_type, sort_keys=True, separators=(',', ':'))
snapshot_id = hashlib.sha256(serialized.encode()).hexdigest()[:16]
```

### Density Score Computation
```python
def _compute_density_scores(snapshot: dict) -> dict[str, int]:
    """Compute relationship density score for every slot in the snapshot.

    Returns dict mapping slot_id -> density_score.
    """
    scores: dict[str, int] = {}
    all_slots = []
    for slots in snapshot["slots_by_type"].values():
        all_slots.extend(slots)

    # Index: slot_id -> slot for quick lookup
    slot_index = {s["slot_id"]: s for s in all_slots}

    # Initialize all scores to 0
    for sid in slot_index:
        scores[sid] = 0

    # Interfaces contribute to their source/target components
    for intf in snapshot["slots_by_type"].get("interface", []):
        intf_id = intf["slot_id"]
        src = intf.get("source_component", "")
        tgt = intf.get("target_component", "")
        if src in scores:
            scores[src] += 1  # direct connection
        if tgt in scores:
            scores[tgt] += 1  # direct connection
        # Interface itself connects to its components
        if src in slot_index:
            scores[intf_id] += 1
        if tgt in slot_index:
            scores[intf_id] += 1

    # Contracts contribute to their interface and component
    for cntr in snapshot["slots_by_type"].get("contract", []):
        cntr_id = cntr["slot_id"]
        iid = cntr.get("interface_id", "")
        cid = cntr.get("component_id", "")
        if iid in scores:
            scores[iid] += 1
            scores[cntr_id] += 1
        if cid in scores:
            scores[cid] += 1  # one-hop: component -> interface -> contract
            scores[cntr_id] += 1

    # Traceability links contribute to both endpoints
    for link in snapshot["slots_by_type"].get("traceability-link", []):
        from_id = link.get("from_id", "")
        to_id = link.get("to_id", "")
        if from_id in scores:
            scores[from_id] += 1
        if to_id in scores:
            scores[to_id] += 1

    return scores
```

### Edge Extraction
```python
def _extract_edges(snapshot: dict, in_view_ids: set[str]) -> list[dict]:
    """Extract relationship edges from snapshot, filtered to in-view slots only."""
    edges = []

    for intf in snapshot["slots_by_type"].get("interface", []):
        intf_id = intf["slot_id"]
        src = intf.get("source_component", "")
        tgt = intf.get("target_component", "")
        if src in in_view_ids and intf_id in in_view_ids:
            edges.append({"source_id": src, "target_id": intf_id, "relationship_type": "component_interface"})
        if tgt in in_view_ids and intf_id in in_view_ids:
            edges.append({"source_id": intf_id, "target_id": tgt, "relationship_type": "component_interface"})

    for cntr in snapshot["slots_by_type"].get("contract", []):
        cntr_id = cntr["slot_id"]
        iid = cntr.get("interface_id", "")
        if iid in in_view_ids and cntr_id in in_view_ids:
            edges.append({"source_id": iid, "target_id": cntr_id, "relationship_type": "interface_contract"})

    for link in snapshot["slots_by_type"].get("traceability-link", []):
        link_id = link["slot_id"]
        from_id = link.get("from_id", "")
        to_id = link.get("to_id", "")
        link_type = link.get("link_type", "trace")
        if from_id in in_view_ids and to_id in in_view_ids:
            edges.append({"source_id": from_id, "target_id": to_id, "relationship_type": link_type})

    # Sort for determinism
    edges.sort(key=lambda e: (e["source_id"], e["target_id"], e["relationship_type"]))
    return edges
```

### Sorted Output for Determinism
```python
def _sort_section_slots(slots: list[dict], scores: dict[str, int]) -> list[dict]:
    """Sort slots by density score desc, version desc, name asc."""
    return sorted(
        slots,
        key=lambda s: (-scores.get(s["slot_id"], 0), -s.get("version", 1), s.get("name", "")),
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| uuid4() snapshot IDs | Content-hash snapshot IDs | Phase 7 | Enables deterministic output (VIEW-09) |
| No ranking | Density-based ranking | Phase 7 | Hub components surface to top (VIEW-03) |
| No edges in output | Explicit edges array | Phase 7 | Diagram generator can consume directly (VIEW-04) |
| Logger defined unused | Structured logging throughout | Phase 7 | Observability for assembly pipeline (VIEW-11) |
| format_version "1.0" | format_version "1.1" | Phase 7 | Signals schema evolution |

## Open Questions

1. **Performance target for VIEW-12**
   - What we know: Current 73 tests run in 0.28s total. Assembly is fast for small registries.
   - What's unclear: No explicit ms target defined in requirements.
   - Recommendation: Set target at < 500ms for 100-slot registries. Instrument with `time.perf_counter()` and assert in a performance test. This is Claude's discretion per CONTEXT.md.

2. **Edge direction convention for component_interface**
   - What we know: Interfaces have both `source_component` and `target_component` fields.
   - What's unclear: Should both directions generate edges, or only source->interface?
   - Recommendation: Generate one edge per field reference (source->intf and intf->target), matching the data flow direction. The edge is from the component that initiates to the interface, and from the interface to the receiving component. This gives diagram generators directional information.

3. **format_version bump**
   - What we know: Current format_version is "1.0", set in Phase 6b.
   - What's unclear: Should this become "1.1" or "2.0"?
   - Recommendation: Use "1.1" -- the changes are additive (new fields), not breaking (existing fields unchanged). The schema validation pattern `^\d+\.\d+$` already supports this.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | pyproject.toml or implicit |
| Quick run command | `python3 -m pytest tests/test_view_assembler.py -x -q` |
| Full suite command | `python3 -m pytest tests/ -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VIEW-03 | Ranked retrieval by density | unit | `python3 -m pytest tests/test_view_assembler.py -x -k "rank"` | No -- Wave 0 |
| VIEW-04 | Handoff format with edges + metadata | unit + integration | `python3 -m pytest tests/test_view_assembler.py -x -k "edge or metadata or handoff"` | No -- Wave 0 |
| VIEW-09 | Deterministic output | unit | `python3 -m pytest tests/test_view_assembler.py -x -k "deterministic or determinism"` | No -- Wave 0 |
| VIEW-11 | Structured log entries | unit | `python3 -m pytest tests/test_view_assembler.py -x -k "log"` | No -- Wave 0 |
| VIEW-12 | Performance target | unit | `python3 -m pytest tests/test_view_assembler.py -x -k "perf"` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/test_view_assembler.py tests/test_view_integration.py -x -q`
- **Per wave merge:** `python3 -m pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Tests for `_compute_density_scores()` -- density ranking logic
- [ ] Tests for `_extract_edges()` -- edge extraction and filtering
- [ ] Tests for `_sort_section_slots()` -- deterministic sort ordering
- [ ] Tests for deterministic snapshot_id (content hash)
- [ ] Tests for structured logging output (using `caplog` fixture)
- [ ] Tests for ranking override via view-spec `ranking` field
- [ ] Performance test asserting assembly time < 500ms for 100 slots
- [ ] Schema update tests for new view.json fields (edges, metadata)
- [ ] Integration test: same input -> byte-identical output (excluding volatile fields)

## Sources

### Primary (HIGH confidence)
- `scripts/view_assembler.py` -- current implementation, 672 lines, all extension points identified
- `schemas/view.json` -- current output schema with `additionalProperties: false`
- `schemas/view-spec.json` -- current spec schema with `additionalProperties: false`
- `schemas/interface.json` -- `source_component`, `target_component` fields for edge extraction
- `schemas/contract.json` -- `interface_id`, `component_id` fields for edge extraction
- `schemas/traceability-link.json` -- `from_id`, `to_id`, `link_type` fields for edge extraction
- `schemas/component.json` -- `relationships` field already exists (array of objects)
- `tests/test_view_assembler.py` -- 73 existing tests, all passing
- `07-CONTEXT.md` -- locked decisions from user discussion

### Secondary (MEDIUM confidence)
- Python stdlib `hashlib` documentation -- SHA-256 API
- Python stdlib `logging` documentation -- `extra` parameter for structured fields

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all stdlib, no new dependencies
- Architecture: HIGH -- clear extension points in existing code, relationship fields documented in schemas
- Pitfalls: HIGH -- identified from direct code analysis (additionalProperties, timestamp determinism)

**Research date:** 2026-03-07
**Valid until:** 2026-04-07 (stable -- no external dependencies changing)
