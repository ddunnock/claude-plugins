# Phase 2: Requirements Ingestion Pipeline - Research

**Researched:** 2026-03-01
**Domain:** Upstream registry ingestion, delta detection, schema gap handling
**Confidence:** HIGH

## Summary

Phase 2 bridges the requirements-dev output (6 JSON registries with 48 needs, 479 requirements, 21 sources, 16 assumptions, and 1069 traceability links) into the Phase 1 Design Registry. The core technical challenge is threefold: (1) mapping 5 distinct upstream entity types with different schemas into Design Registry slots via the existing SlotAPI, (2) detecting deltas on re-ingestion without overwriting manual design work downstream, and (3) handling known upstream schema gaps (BUG-1..3, SCHEMA-1..3, GAP-1..8 from CROSS-SKILL-ANALYSIS.md) gracefully with structured gap markers.

The existing SlotAPI (from Phase 1) currently supports 4 slot types: `component`, `interface`, `contract`, `requirement-ref`. Phase 2 must extend this to support 5 new ingestion slot types (`need`, `requirement`, `source`, `assumption`, `traceability-link`) OR repurpose/extend existing types. The `requirement-ref` type is the closest match but lacks fields for upstream provenance metadata, confidence levels, and cross-references. New schemas and slot type registrations are required.

**Primary recommendation:** Extend the registry with 5 new slot types and schemas, implement ingestion as a single Python script (`scripts/ingest_upstream.py`) that reads all upstream registries in dependency order, uses content hashing for delta detection, and produces structured reports. Do not use the SlotAPI's auto-generated UUIDs for ingested slots -- use deterministic IDs based on the `type:upstream-id` convention from CONTEXT.md decisions.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- All-at-once ingestion: single init command reads all registries in dependency order
- Selective re-ingestion happens implicitly via delta detection (only changed items update)
- Explicit path argument: user provides path to `.requirements-dev/` directory
- Warn but ingest when upstream gates aren't all passed -- show which phases are incomplete, still ingest available data, mark incomplete areas with gap markers (aligns with XCUT-01 partial-state tolerance)
- Preserve upstream confidence levels (high/medium/low/ungrounded) as metadata on source slots -- addresses GAP-4 from CROSS-SKILL-ANALYSIS
- Content hash comparison: hash each upstream registry entry, store hashes in a manifest, compare on re-ingest to find adds/updates/deletes
- Conflicts (upstream change vs. local design edit): report conflict, don't overwrite -- flag in delta report, preserve local edit, user resolves manually
- Delta report: both console summary (immediate visibility) and persistent `.system-dev/delta-report.json` (for downstream agents like impact analysis)
- Upstream deletions with downstream design artifacts flagged as 'breaking' severity; deletions with no downstream refs flagged as 'info'
- Work around known upstream bugs (BUG-1, BUG-2, BUG-3) in our parser -- handle both buggy and correct schemas, no upstream dependency
- Ingest what exists, gap-mark the rest -- for known gaps (research gaps, citations, ungrounded claims not in upstream JSON), produce structured gap markers referencing CROSS-SKILL-ANALYSIS finding IDs
- Gap marker format: structured JSON object with `type`, `finding_ref`, `severity`, and `description` fields in slot metadata -- machine-readable for downstream agents
- Compatibility report: after ingestion, write `.system-dev/compatibility-report.json` listing all gap markers by finding ID, affected slot counts, and severity
- One slot per entity: each need -> `need` slot, each requirement -> `requirement` slot, each source -> `source` slot, etc.
- Naming convention: `type:upstream-id` (e.g., `need:N-001`, `requirement:REQ-026`, `source:SRC-003`, `assumption:A-001`) -- type prefix enables filtering, upstream ID preserved
- Traceability as slot cross-references: explicit link fields pointing to other slot IDs (e.g., `derives_from: ['need:N-003']`) -- enables Phase 5 graph traversal natively
- Provenance metadata on every ingested slot: `{source: 'requirements-dev', upstream_file: '...', ingested_at: '...', hash: '...'}` -- enables delta detection and audit trails

### Claude's Discretion
- Internal ingestion order (which registry to process first)
- Hash algorithm choice for delta detection
- Console output formatting and verbosity levels
- Error recovery strategy for malformed upstream JSON

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INGS-01 | Ingest requirements-dev registries (needs, requirements, traceability, sources, assumptions) -- REQ-026..030, REQ-141..145 | New slot types/schemas for each entity type; field mapping from upstream to Design Registry; deterministic slot IDs; status filtering (registered/baselined only) |
| INGS-02 | Ingestion engine parsing upstream JSON registries into design-registry slots -- REQ-234..250 | Registry parser with field mapping layer; atomic transaction via staged writes; structured logging; gap marker production for untranslatable items |
| INGS-03 | Delta detection for re-ingestion (upstream requirement changes) -- REQ-234..250 | Content hash manifest stored in `.system-dev/ingestion-manifest.json`; hash comparison identifies adds/updates/deletes; staleness markers on modified slots; conflict detection for local edits |
| INGS-04 | Graceful handling of upstream schema gaps (known bugs accepted, gap markers produced) | Gap markers referencing CROSS-SKILL-ANALYSIS finding IDs; compatibility report; dual-schema parsing for BUG-1..3; missing-field tolerance for GAP-1..8 |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `json` | 3.11+ | Parse upstream JSON registries | Already used throughout Phase 1; zero dependencies |
| Python stdlib `hashlib` | 3.11+ | Content hashing for delta detection | SHA-256 is standard, deterministic, fast; stdlib avoids new deps |
| `jsonschema` | 4.20+ | Validate new slot type schemas | Already in `pyproject.toml`; used by Phase 1 SchemaValidator |
| Python stdlib `datetime` | 3.11+ | Timestamps for ingestion metadata | Already used by Phase 1 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Python stdlib `logging` | 3.11+ | Structured log output (REQ-241, REQ-250) | Every ingestion operation must emit structured logs |
| Python stdlib `copy` | 3.11+ | Deep copy for conflict detection | When comparing old vs new slot content |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SHA-256 for hashing | MD5 | MD5 is faster but has collision risk; SHA-256 is standard and security concerns are irrelevant here but there is no performance reason to deviate |
| `json.dumps(sort_keys=True)` for canonical form | `canonicaljson` library | External dep for a problem solvable with stdlib; sorted keys + separators produce deterministic output |

**Installation:** No new dependencies needed. Everything uses Python stdlib + existing `jsonschema`.

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── ingest_upstream.py       # Main ingestion engine (INGS-01, INGS-02)
├── delta_detector.py        # Delta detection logic (INGS-03)
├── upstream_schemas.py      # Field mapping + gap marker definitions (INGS-04)
├── registry.py              # Extended with new slot types (existing)
├── schema_validator.py      # Unchanged (existing)
├── shared_io.py             # Unchanged (existing)
├── change_journal.py        # Unchanged (existing)
├── version_manager.py       # Unchanged (existing)
└── init_workspace.py        # Extended to create new registry dirs (existing)

schemas/
├── need.json                # NEW: need slot schema
├── requirement.json         # NEW: requirement slot schema
├── source.json              # NEW: source slot schema
├── assumption.json          # NEW: assumption slot schema
├── traceability-link.json   # NEW: traceability link slot schema
├── component.json           # Unchanged (existing)
├── interface.json           # Unchanged (existing)
├── contract.json            # Unchanged (existing)
└── requirement-ref.json     # Unchanged (existing)

tests/
├── test_ingest_upstream.py  # NEW: ingestion engine tests
├── test_delta_detector.py   # NEW: delta detection tests
├── test_upstream_schemas.py # NEW: field mapping + gap marker tests
└── test_ingestion_integration.py  # NEW: end-to-end ingestion tests
```

### Pattern 1: Deterministic Slot IDs (Override Auto-Generated UUIDs)

**What:** Phase 1's SlotAPI generates random UUIDs (`comp-{uuid4()}`). Phase 2 needs deterministic IDs based on upstream identity (`need:NEED-001`, `requirement:REQ-026`). The ingestion engine must bypass auto-ID generation and set slot_id explicitly.

**When to use:** All ingested slots. Never for locally-created design artifacts (those still use UUIDs).

**Implementation approach:** The SlotAPI.create() currently force-sets `slot_id`. For ingestion, either:
- Option A: Add a `slot_id_override` parameter to `SlotAPI.create()` that accepts a pre-determined ID
- Option B: Create a separate `SlotAPI.ingest()` method that accepts pre-determined IDs
- **Recommendation: Option B** -- cleaner separation between ingestion (bulk, deterministic IDs, skip journaling per-item) and normal CRUD (single-item, auto-IDs, always journal)

**Why this matters:** Delta detection requires stable IDs. If a need is ingested as `need:NEED-001`, re-ingestion must find that same slot to compare hashes. UUID-based IDs would make re-identification impossible.

### Pattern 2: Content Hash Manifest for Delta Detection

**What:** Store a manifest of content hashes alongside the registry. On re-ingestion, hash each upstream entry, compare against the manifest, and classify as added (new hash), modified (hash changed), removed (hash in manifest but not upstream), or unchanged (same hash).

**When to use:** Every re-ingestion operation.

**Implementation:**
```python
import hashlib
import json

def content_hash(entry: dict) -> str:
    """Produce deterministic SHA-256 hash of a registry entry."""
    canonical = json.dumps(entry, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()
```

**Manifest location:** `.system-dev/ingestion-manifest.json`
```json
{
  "schema_version": "1.0.0",
  "ingested_at": "2026-03-01T...",
  "upstream_path": "/path/to/.requirements-dev/",
  "upstream_state": {
    "gates_status": {"init": true, "needs": true, ...},
    "counts": {"needs": 48, "requirements": 479, ...}
  },
  "hashes": {
    "need:NEED-001": "a1b2c3...",
    "requirement:REQ-001": "d4e5f6...",
    ...
  }
}
```

### Pattern 3: Staged Atomic Ingestion (REQ-141, REQ-243)

**What:** Ingestion writes all slots to temporary staging, then commits atomically. If any write fails, nothing is persisted. This prevents partial ingestion that leaves the registry in an inconsistent state.

**When to use:** Initial ingestion and delta-based updates.

**Implementation approach:**
1. Parse all upstream registries and build a list of slot operations (create/update/delete)
2. Validate all operations against schemas before writing anything
3. Write all slots via SlotAPI (which already uses atomic_write per file)
4. Write updated manifest
5. Write delta report and compatibility report
6. If any step fails, the individual atomic writes are already committed (since each slot is a separate file), but the manifest is NOT updated -- so re-running ingestion will re-attempt failed items

**Note on atomicity:** True all-or-nothing atomicity across hundreds of files requires a transaction log, which adds complexity. The pragmatic approach is: each individual slot write is atomic (Phase 1 guarantee), the manifest tracks what was successfully ingested, and re-running ingestion is idempotent. This satisfies the spirit of REQ-141/REQ-243 without a custom transaction manager.

### Pattern 4: Upstream Field Mapping Layer

**What:** A dedicated mapping module that translates upstream registry field names/structures to Design Registry slot fields. This isolates all upstream-schema-specific knowledge in one place.

**When to use:** Every upstream registry field access.

**Why critical:** CROSS-SKILL-ANALYSIS found 3 bugs from reading wrong field names. A mapping layer ensures changes to upstream schemas require updating exactly one file.

**Example:**
```python
# upstream_schemas.py

NEED_FIELD_MAP = {
    # upstream_field -> slot_field
    "id": "upstream_id",
    "statement": "description",
    "stakeholder": "stakeholder",
    "source_block": "source_block",
    "source_artifacts": "source_artifacts",
    "concept_dev_refs": "concept_dev_refs",
    "status": "upstream_status",
    "rationale": "rationale",
    "registered_at": "upstream_registered_at",
}

REQUIREMENT_FIELD_MAP = {
    "id": "upstream_id",
    "statement": "description",
    "type": "requirement_type",
    "priority": "priority",
    "status": "upstream_status",
    "parent_need": "parent_need",
    "source_block": "source_block",
    "level": "decomposition_level",
    "attributes": "upstream_attributes",
    "quality_checks": "quality_checks",
    "rationale": "rationale",
    "registered_at": "upstream_registered_at",
    "baselined_at": "upstream_baselined_at",
}

# Source registry has field name mismatch (SCHEMA-1):
# upstream uses both "name" AND "title" -- handle both
SOURCE_FIELD_MAP = {
    "id": "upstream_id",
    "title": "name",         # SCHEMA-1: upstream uses "title"
    "name": "name",          # Some entries also have "name"
    "url": "url",
    "type": "source_type",
    "confidence": "confidence",  # GAP-4: preserve confidence levels
    "research_context": "research_context",
    "concept_dev_ref": "concept_dev_ref",
    "registered_at": "upstream_registered_at",
}
```

### Pattern 5: Gap Marker Injection

**What:** When upstream data is known to be missing or unreliable (per CROSS-SKILL-ANALYSIS findings), inject structured gap markers into slot metadata rather than crashing or silently producing empty data.

**Gap marker structure (from CONTEXT.md decision):**
```python
gap_marker = {
    "type": "missing_data",        # missing_data | schema_mismatch | known_bug
    "finding_ref": "GAP-4",        # CROSS-SKILL-ANALYSIS finding ID
    "severity": "medium",          # low | medium | high
    "description": "Confidence levels lost in translation from concept-dev to requirements-dev"
}
```

**Known gaps to handle:**

| Finding | What's Missing | Gap Marker |
|---------|---------------|------------|
| GAP-1 | Research gaps from concept-dev not in requirements-dev registries | `missing_data`, `GAP-1`, `medium` |
| GAP-2 | Ungrounded claims not carried forward | `missing_data`, `GAP-2`, `medium` |
| GAP-3 | Citation graph not carried forward | `missing_data`, `GAP-3`, `low` |
| GAP-4 | Confidence levels lost (but requirements-dev source_registry DOES have confidence) | Actually present -- `source_registry.json` has `confidence` field |
| GAP-5 | No concept-dev research artifact access | `missing_data`, `GAP-5`, `low` |
| GAP-7 | No assumption lifecycle in requirements-dev | `missing_data`, `GAP-7`, `medium` |
| GAP-8 | No backward traceability to concept artifacts | `missing_data`, `GAP-8`, `medium` |
| BUG-1 | Gate status schema mismatch | Handle both schemas in parser |
| BUG-2 | gap_analyzer reads wrong keys | N/A -- we read directly from registries |
| BUG-3 | Empty gates logic inversion | Handle empty/missing gates explicitly |

**Important discovery:** Re-examining the actual upstream data, `source_registry.json` DOES include a `confidence` field (GAP-4 was about concept-dev to requirements-dev, but requirements-dev already carries confidence forward). We can ingest confidence levels directly. The gap marker for GAP-4 should note that confidence IS available and was successfully ingested.

### Anti-Patterns to Avoid
- **Silent `.get()` with empty defaults:** Never use `.get("key", {})` for required fields without logging when the default is returned. This is exactly how BUG-1 and BUG-2 occurred. Use explicit `KeyError` for required fields, fallback for optional fields.
- **Hardcoded upstream paths:** The upstream path must be provided as an argument, not hardcoded. Phase 1 PITFALLS.md explicitly warns about this.
- **Reading full registry files into context:** Ingestion scripts run as Python, not in Claude's context window. But the ingestion report/delta report shown to the user must be concise (IDs + summaries, not full slot content).
- **Mixing ingestion slot IDs with design slot IDs:** Ingested slots use `type:upstream-id` convention. Design artifacts (components, interfaces, contracts) created by Phase 3+ agents use `prefix-uuid` convention. These must never collide.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON content hashing | Custom serialization | `json.dumps(sort_keys=True, separators=(',',':'))` + `hashlib.sha256` | Deterministic canonical form requires sorted keys and no whitespace; stdlib handles both |
| Schema validation | Custom field checking | `jsonschema` via existing `SchemaValidator` | Already battle-tested in Phase 1; new schemas plug in automatically |
| Atomic file writes | Custom temp file logic | Existing `shared_io.atomic_write()` | Already handles fsync + rename + cleanup |
| Timestamp formatting | Custom string formatting | `datetime.now(timezone.utc).isoformat()` | Already established pattern in Phase 1 |

**Key insight:** Phase 1 built all the infrastructure needed for safe persistence. Phase 2 should reuse `atomic_write`, `SchemaValidator`, `SlotStorageEngine`, and the journal -- extending only where new slot types require new schemas and new storage directories.

## Common Pitfalls

### Pitfall 1: Slot ID Convention Clash with SlotAPI Auto-Generation
**What goes wrong:** SlotAPI.create() force-generates IDs as `{prefix}-{uuid4()}`. Ingested slots need deterministic IDs like `need:NEED-001`. Calling create() ignores any provided slot_id.
**Why it happens:** Phase 1 designed create() for interactive design artifacts, not bulk ingestion.
**How to avoid:** Add an `ingest()` method or `slot_id_override` parameter to SlotAPI. Do NOT modify create() behavior -- existing tests depend on auto-generated IDs.
**Warning signs:** Ingested slots get random UUIDs; delta detection can't find them on re-run.

### Pitfall 2: SLOT_TYPE_DIRS Missing New Types
**What goes wrong:** `SLOT_TYPE_DIRS` in registry.py only has 4 entries (component, interface, contract, requirement-ref). Writing a `need` type slot raises `ValueError: Unknown slot type`.
**Why it happens:** Phase 1 only defined design artifact types, not ingestion types.
**How to avoid:** Add entries for all 5 new types to `SLOT_TYPE_DIRS` and `SLOT_ID_PREFIXES`. Also update `init_workspace.py` to create the new subdirectories. Must be done before any ingestion code runs.
**Warning signs:** `ValueError: Unknown slot type: 'need'` on first ingestion attempt.

### Pitfall 3: Traceability Links as Slots Are Expensive
**What goes wrong:** With 1069 traceability links, creating one slot per link means 1069 JSON files. This is manageable but increases ingestion time and directory clutter.
**Why it happens:** The "one slot per entity" decision applies uniformly.
**How to avoid:** This is an acceptable cost given the decision. However, consider storing traceability links in a compact format (fewer fields per slot) and use batch operations. The 500-requirement/5-second performance target (REQ-246) is feasible since each write is ~1ms atomic. 1069 links at 1ms each = ~1 second.
**Warning signs:** Ingestion time exceeds 5 seconds; directory listing becomes slow.

### Pitfall 4: Re-ingestion Overwrites Journal History
**What goes wrong:** Each ingested slot goes through SlotAPI which journals every mutation. Re-ingestion of 479+ requirements generates 479+ journal entries, flooding the change history with ingestion noise.
**Why it happens:** The journal-after-storage pattern from Phase 1 is designed for individual design changes, not bulk operations.
**How to avoid:** Use a dedicated `ingest()` method that writes a single batch journal entry (e.g., "Ingested 479 requirements from requirements-dev") rather than 479 individual entries. Or use the `agent_id` field to tag ingestion entries as `ingestion-engine` so they can be filtered.
**Warning signs:** Journal grows by 1000+ entries per ingestion; history queries become slow.

### Pitfall 5: Status Filtering Creates Phantom Deltas
**What goes wrong:** REQ-026/REQ-030 require filtering to registered/baselined status only. If a requirement transitions from baselined to withdrawn, the delta detector should flag it as "removed" (it's no longer processable). But if the filter runs before delta detection, the withdrawn requirement simply disappears from the input set, and delta detection sees it as "removed from upstream" rather than "status changed to withdrawn."
**Why it happens:** Status filtering and delta detection are conceptually separate but interact.
**How to avoid:** Run delta detection FIRST on the full upstream set (including withdrawn requirements), THEN filter. The delta report should distinguish "removed from upstream" from "status changed to non-processable" (REQ-236).
**Warning signs:** Delta report shows "removed" for requirements that were actually withdrawn; user doesn't understand why.

## Code Examples

### Upstream Registry Loading with Validation
```python
# Source: Derived from actual upstream schema analysis (2026-03-01)
import json
import os

def load_upstream_registry(base_path: str, filename: str, top_key: str) -> list[dict]:
    """Load an upstream registry file with validation.

    Args:
        base_path: Path to .requirements-dev/ directory.
        filename: Registry filename (e.g., 'needs_registry.json').
        top_key: Top-level key containing items (e.g., 'needs').

    Returns:
        List of registry entry dicts.

    Raises:
        FileNotFoundError: If registry file doesn't exist.
        KeyError: If expected top_key is missing (not silent .get()).
    """
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Upstream registry not found: {filepath}")

    with open(filepath) as f:
        data = json.load(f)

    # Explicit KeyError, NOT silent .get() -- learned from BUG-1/BUG-2
    if top_key not in data:
        raise KeyError(
            f"Expected key '{top_key}' not found in {filename}. "
            f"Available keys: {list(data.keys())}"
        )

    return data[top_key]
```

### Upstream Gate Status Check (BUG-1/BUG-3 Resistant)
```python
# Source: Derived from CROSS-SKILL-ANALYSIS BUG-1, BUG-3 findings
def check_upstream_gates(state_path: str) -> dict:
    """Check upstream requirements-dev gate status.

    Handles both the correct schema (state.json has flat 'gates' dict)
    and the concept-dev schema (nested 'phases.X.gate_passed').

    Returns dict with 'all_passed', 'gates', 'warnings'.
    """
    with open(state_path) as f:
        state = json.load(f)

    result = {"all_passed": False, "gates": {}, "warnings": []}

    # requirements-dev uses flat gates dict
    if "gates" in state:
        gates = state["gates"]
    # concept-dev uses nested phases (BUG-1 workaround)
    elif "phases" in state:
        gates = {
            name: phase.get("gate_passed", False)
            for name, phase in state["phases"].items()
        }
    else:
        # BUG-3: No gate info available -- NOT all_passed
        result["warnings"].append("No gate information found in state.json")
        return result

    # BUG-3: Empty gates is NOT all_passed
    if not gates:
        result["warnings"].append("Gate dict is empty -- no phases completed")
        return result

    failed = [name for name, passed in gates.items() if not passed]
    result["gates"] = gates
    result["all_passed"] = len(failed) == 0
    if failed:
        result["warnings"].append(f"Incomplete phases: {', '.join(failed)}")

    return result
```

### Content Hash for Delta Detection
```python
# Source: stdlib hashlib + json canonical form
import hashlib
import json

def content_hash(entry: dict, exclude_keys: set | None = None) -> str:
    """Produce deterministic SHA-256 hash of a registry entry.

    Args:
        entry: The registry entry to hash.
        exclude_keys: Keys to exclude from hashing (e.g., timestamps
            that change on every write but don't represent content change).

    Returns:
        Hex digest string.
    """
    if exclude_keys:
        entry = {k: v for k, v in entry.items() if k not in exclude_keys}
    canonical = json.dumps(entry, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()

# Exclude timestamps from hashing -- content changes matter, not write times
HASH_EXCLUDE_KEYS = {"registered_at", "baselined_at", "updated_at", "created_at"}
```

### Delta Classification
```python
def compute_deltas(
    upstream_entries: list[dict],
    manifest_hashes: dict[str, str],
    id_field: str,
    slot_prefix: str,
) -> dict[str, list]:
    """Classify upstream entries as added, modified, removed, or unchanged.

    Returns:
        Dict with 'added', 'modified', 'removed', 'unchanged' lists.
    """
    deltas = {"added": [], "modified": [], "removed": [], "unchanged": []}
    seen_ids = set()

    for entry in upstream_entries:
        slot_id = f"{slot_prefix}:{entry[id_field]}"
        seen_ids.add(slot_id)
        new_hash = content_hash(entry, HASH_EXCLUDE_KEYS)
        old_hash = manifest_hashes.get(slot_id)

        if old_hash is None:
            deltas["added"].append({"slot_id": slot_id, "entry": entry})
        elif old_hash != new_hash:
            deltas["modified"].append({"slot_id": slot_id, "entry": entry})
        else:
            deltas["unchanged"].append(slot_id)

    # Entries in manifest but not in upstream = removed
    for slot_id in manifest_hashes:
        if slot_id.startswith(f"{slot_prefix}:") and slot_id not in seen_ids:
            deltas["removed"].append(slot_id)

    return deltas
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| UUID slot IDs for all types | Deterministic IDs for ingested slots | Phase 2 (new) | Enables delta detection; requires SlotAPI extension |
| 4 slot types (component, interface, contract, requirement-ref) | 9 slot types (+ need, requirement, source, assumption, traceability-link) | Phase 2 (new) | Requires new schemas, storage dirs, type registrations |
| Manual requirement entry | Automated bulk ingestion from JSON registries | Phase 2 (new) | Replaces manual workflow; idempotent re-runs |

## Open Questions

1. **Should traceability links be slots or metadata?**
   - What we know: CONTEXT.md decides "one slot per entity" and uses cross-references in slot fields. Traceability links could be stored as slots (1069 files) OR as cross-reference fields on needs/requirements slots.
   - What's unclear: With 1069 links, individual slot files work but add directory clutter. Cross-reference fields on existing slots are more compact but lose independent versioning per link.
   - Recommendation: Follow the "one slot per entity" decision. 1069 files is manageable. The traceability-link slot type should be lightweight (few fields). Phase 5 traceability-weaver will consume these.

2. **Should ingestion use SlotAPI or write directly via SlotStorageEngine?**
   - What we know: SlotAPI enforces schema validation and journals every write. For bulk ingestion of 500+ items, journaling each item individually floods the journal.
   - What's unclear: Whether a single batch journal entry is sufficient for audit requirements.
   - Recommendation: Add an `ingest()` method to SlotAPI that validates each slot but writes a single summary journal entry for the batch. This preserves validation guarantees while keeping the journal manageable.

3. **Slot ID format: colon separator safe for filenames?**
   - What we know: The convention is `type:upstream-id` (e.g., `need:NEED-001`). Colons are problematic on Windows filesystems.
   - What's unclear: Whether this project will ever run on Windows.
   - Recommendation: Use colon in the logical slot_id but replace with underscore in the filename (e.g., file `need_NEED-001.json` with `slot_id: "need:NEED-001"`). Or use a different separator like `.` (e.g., `need.NEED-001`). The SlotStorageEngine already constructs filenames from slot_id, so this mapping is centralized.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.0+ (via uv) |
| Config file | None (pytest discovers tests/ automatically) |
| Quick run command | `.venv/bin/python -m pytest tests/ -x -q` |
| Full suite command | `.venv/bin/python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INGS-01 (REQ-026) | Translate registered/baselined requirements into slots | integration | `.venv/bin/python -m pytest tests/test_ingest_upstream.py::test_translate_requirements -x` | Wave 0 |
| INGS-01 (REQ-028) | Multi-block ingestion in single operation | integration | `.venv/bin/python -m pytest tests/test_ingest_upstream.py::test_multi_block_ingestion -x` | Wave 0 |
| INGS-01 (REQ-030) | Filter out draft/withdrawn requirements | unit | `.venv/bin/python -m pytest tests/test_ingest_upstream.py::test_status_filtering -x` | Wave 0 |
| INGS-01 (REQ-145) | Parse requirements_registry.json schema | unit | `.venv/bin/python -m pytest tests/test_upstream_schemas.py::test_parse_requirements_registry -x` | Wave 0 |
| INGS-02 (REQ-242) | Translate upstream to slot format | unit | `.venv/bin/python -m pytest tests/test_ingest_upstream.py::test_translate_to_slot -x` | Wave 0 |
| INGS-02 (REQ-243) | Atomic transaction for staged updates | integration | `.venv/bin/python -m pytest tests/test_ingest_upstream.py::test_atomic_ingestion -x` | Wave 0 |
| INGS-02 (REQ-245) | Gap markers for untranslatable items | unit | `.venv/bin/python -m pytest tests/test_upstream_schemas.py::test_gap_markers -x` | Wave 0 |
| INGS-02 (REQ-246) | 500 requirements in 5 seconds | performance | `.venv/bin/python -m pytest tests/test_ingest_upstream.py::test_bulk_performance -x` | Wave 0 |
| INGS-03 (REQ-234) | Delta detection: added/modified/removed | unit | `.venv/bin/python -m pytest tests/test_delta_detector.py::test_delta_classification -x` | Wave 0 |
| INGS-03 (REQ-235) | Staleness markers on modified slots | unit | `.venv/bin/python -m pytest tests/test_delta_detector.py::test_staleness_markers -x` | Wave 0 |
| INGS-03 (REQ-236) | Status transition detection | unit | `.venv/bin/python -m pytest tests/test_delta_detector.py::test_status_transitions -x` | Wave 0 |
| INGS-03 (REQ-237) | 500 requirements delta in 2 seconds | performance | `.venv/bin/python -m pytest tests/test_delta_detector.py::test_delta_performance -x` | Wave 0 |
| INGS-04 | Gap markers with finding refs | unit | `.venv/bin/python -m pytest tests/test_upstream_schemas.py::test_gap_marker_format -x` | Wave 0 |
| INGS-04 | Compatibility report generation | integration | `.venv/bin/python -m pytest tests/test_ingest_upstream.py::test_compatibility_report -x` | Wave 0 |
| INGS-04 (BUG-1..3) | Handle both buggy and correct gate schemas | unit | `.venv/bin/python -m pytest tests/test_upstream_schemas.py::test_gate_status_resilience -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `.venv/bin/python -m pytest tests/ -x -q`
- **Per wave merge:** `.venv/bin/python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_ingest_upstream.py` -- covers INGS-01, INGS-02 core ingestion
- [ ] `tests/test_delta_detector.py` -- covers INGS-03 delta detection
- [ ] `tests/test_upstream_schemas.py` -- covers INGS-04 field mapping and gap markers
- [ ] `tests/test_ingestion_integration.py` -- covers end-to-end ingestion with real upstream data structures
- [ ] `schemas/need.json` -- need slot type schema
- [ ] `schemas/requirement.json` -- requirement slot type schema
- [ ] `schemas/source.json` -- source slot type schema
- [ ] `schemas/assumption.json` -- assumption slot type schema
- [ ] `schemas/traceability-link.json` -- traceability link slot type schema

## Sources

### Primary (HIGH confidence)
- Actual upstream registry files at `~/projects/brainstorming/.requirements-dev/` -- directly examined all 6 JSON registries, verified field names, item counts, and structure (2026-03-01)
- CROSS-SKILL-ANALYSIS.md at `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/CROSS-SKILL-ANALYSIS.md` -- all BUG/SCHEMA/GAP findings verified (2026-02-23)
- Phase 1 implementation: `scripts/registry.py`, `scripts/schema_validator.py`, `scripts/shared_io.py`, `scripts/init_workspace.py` -- verified SlotAPI interface, SLOT_TYPE_DIRS, SLOT_ID_PREFIXES, atomic write patterns
- Existing schemas: `schemas/component.json`, `schemas/requirement-ref.json` -- verified JSON Schema Draft 2020-12 patterns with additionalProperties: false
- Phase 1 research: `.planning/research/PITFALLS.md` -- integration gotchas table and pitfall 4 (schema mismatch)

### Secondary (MEDIUM confidence)
- Python stdlib `hashlib` SHA-256 documentation -- standard approach, no verification needed
- Python stdlib `json.dumps(sort_keys=True)` for canonical form -- well-known pattern

### Tertiary (LOW confidence)
- None -- all findings verified against actual code and data

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all stdlib + existing deps, nothing new
- Architecture: HIGH -- patterns derived from examining actual upstream data and Phase 1 code
- Pitfalls: HIGH -- all pitfalls derived from documented bugs (CROSS-SKILL-ANALYSIS) and Phase 1 design constraints

**Research date:** 2026-03-01
**Valid until:** 2026-04-01 (upstream registries are baselined and stable)
