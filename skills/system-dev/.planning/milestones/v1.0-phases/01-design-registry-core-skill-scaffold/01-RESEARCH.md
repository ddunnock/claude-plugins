# Phase 1: Design Registry Core + Skill Scaffold - Research

**Researched:** 2026-02-28
**Domain:** JSON-file-backed design registry with schema validation, versioning, change journal; Claude Code skill scaffold
**Confidence:** HIGH

## Summary

Phase 1 builds the foundational infrastructure for the entire AI-Assisted Systems Design Platform. It has two major deliverables: (1) a Design Registry with CRUD operations, schema validation, monotonic versioning, and an append-only change journal, all backed by JSON files on disk with atomic write semantics; and (2) a Claude Code skill scaffold (SKILL.md, directory structure, security rules, `${CLAUDE_PLUGIN_ROOT}` path patterns) following Anthropic's skill authoring conventions.

The Design Registry is heavily specified with 125+ formal requirements across 6 sub-blocks (design-registry, slot-storage-engine, slot-api, schema-validator, version-manager, change-journal). The architecture is a layered system: slot-api is the single entry point for all agents, delegating to slot-storage-engine (persistence), schema-validator (validation), version-manager (history), and change-journal (audit trail). The only third-party dependency allowed is `jsonschema` (for the schema-validator); everything else must use Python stdlib + git CLI.

The skill scaffold follows patterns established by the sibling `requirements-dev` skill: SKILL.md under 500 lines with YAML frontmatter, progressive disclosure to `commands/`, `agents/`, `references/` directories, security rules as XML tags, and `${CLAUDE_PLUGIN_ROOT}` for all path references. The `.system-dev/` workspace directory mirrors `.requirements-dev/` conventions.

**Primary recommendation:** Build in three plans: (1) skill scaffold + workspace init, (2) storage engine + schema validator + slot API, (3) version manager + change journal. Each plan delivers testable, independently verifiable functionality.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Storage format**: JSON files per slot, one .json file per design element
- **Directory organization**: by slot type: `.system-dev/registry/components/`, `.system-dev/registry/interfaces/`, etc.
- **Atomic writes**: write-to-temp + rename strategy (write to .tmp, then atomic rename; orphaned .tmp on crash, original stays intact)
- **Workspace location**: `.system-dev/` relative to project root (mirrors `.requirements-dev/`)
- **Schema system**: Strict core fields + free-form `extensions` object per slot type
- **Schema files**: JSON Schema files shipped with the skill (e.g., `schemas/component.json`)
- **Phase 1 slot types**: component, interface, contract, requirement-ref only (more added later)
- **Validation errors**: detailed with exact field path + fix hint
- **Change journal**: Append-only JSONL at `.system-dev/journal.jsonl`, one JSON object per line
- **Versioning**: Monotonic integer per slot (v1, v2, v3...) for optimistic locking
- **Journal entries**: timestamp, slot_id, slot_type, operation, version_before, version_after, agent_id, summary, plus full JSON diff (RFC 6902 patch)
- **Version reconstruction**: Old versions reconstructed from journal diffs only (no snapshot files)
- **Command prefix**: `/system-dev` (e.g., `/system-dev:init`, `/system-dev:status`)
- **Init behavior**: Explicit `/system-dev:init` required -- no auto-init
- **Output format**: Structured markdown for terminal output
- **SKILL.md structure**: Overview + triggers + command index (under 500 lines); detailed workflows in `commands/` directory

### Claude's Discretion
- Exact directory structure under `.system-dev/` beyond `registry/` and `journal.jsonl`
- JSON Schema draft version and validation library choice
- Internal code organization (modules, utilities)
- Error recovery strategy for orphaned .tmp files

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DREG-01 | Design Registry with named/typed slots (REQ-001..025, REQ-130) | Slot storage architecture, JSON file per slot, directory-by-type layout |
| DREG-02 | Slot storage engine with atomic writes, crash recovery, git integration (REQ-149..189) | Atomic write pattern from requirements-dev shared_io.py, stdlib-only constraint, git CLI integration |
| DREG-03 | Slot API providing read/write/query interface (REQ-190..206, REQ-403, REQ-408..409, REQ-465) | Capability-based access, uniform request structure, query filters |
| DREG-04 | Schema validation on every write (REQ-007..008, REQ-215..224, REQ-414..418) | jsonschema library with Draft 2020-12, schema registry pattern |
| DREG-05 | Version history per slot, temporal queries (REQ-003..005, REQ-225..233, REQ-473) | Monotonic versioning, journal-based reconstruction, optimistic locking |
| DREG-06 | Change journal with append-only entries, time-range queries (REQ-207..214, REQ-406, REQ-471, REQ-479) | JSONL append-only format, RFC 6902 diffs, immutable entries |
| SCAF-01 | SKILL.md under 500 lines with progressive disclosure | Skill authoring best practices, requirements-dev SKILL.md pattern (246 lines) |
| SCAF-02 | Plugin directory structure (commands/, agents/, scripts/, references/, templates/, data/) | Requirements-dev directory structure as template |
| SCAF-03 | Security rules: content-as-data, path validation, local scripts, external isolation | XML security tag pattern from requirements-dev |
| SCAF-04 | ${CLAUDE_PLUGIN_ROOT} path patterns for all file access | Path pattern templates from requirements-dev |
| SCAF-05 | .system-dev/ workspace directory for user design state | Init command creates workspace; mirrors .requirements-dev/ |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | >=3.11 | Runtime | Matches requirements-dev; needed for modern typing, pathlib |
| jsonschema | 4.x (latest) | JSON Schema Draft 2020-12 validation | REQ-203, REQ-204 explicitly require it; only allowed third-party dep |
| git (CLI) | system | Version control backend | REQ-023, REQ-180 require git CLI, no git library |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json (stdlib) | builtin | JSON serialization | All slot read/write, journal append |
| pathlib (stdlib) | builtin | Path manipulation | All file operations |
| tempfile (stdlib) | builtin | Atomic write temp files | Slot write operations |
| datetime (stdlib) | builtin | UTC timestamps | Journal entries, version entries |
| os (stdlib) | builtin | fsync, rename, file ops | Atomic write, crash recovery |
| uuid (stdlib) | builtin | Slot ID generation | Creating new slots |
| logging (stdlib) | builtin | Structured logging | XCUT-02 structured logging |
| argparse (stdlib) | builtin | Script CLI | Utility script entry points |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| jsonschema | fastjsonschema | Faster but less complete Draft 2020-12 support; REQ-204 names jsonschema |
| JSONL journal | SQLite | Better querying but violates LLM-editable, git-friendly file constraint |
| jsonpatch lib | Hand-rolled RFC 6902 | jsonpatch adds a dependency; simple dict-diff utility is adequate for slot-level diffs |
| uv | pip | uv is faster and already used by requirements-dev |

**Installation:**
```bash
# In pyproject.toml (using uv, matching requirements-dev pattern)
[project]
name = "system-dev"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.20"]

[tool.uv]
dev-dependencies = ["pytest>=7.0"]
```

## Architecture Patterns

### Recommended Skill Directory Structure
```
system-dev/
├── SKILL.md                    # Main skill file (<500 lines)
├── pyproject.toml              # Dependencies (jsonschema, dev: pytest)
├── uv.lock                     # Lock file
├── commands/                   # One file per command (progressive disclosure)
│   ├── init.md                 # /system-dev:init workflow
│   ├── status.md               # /system-dev:status workflow
│   ├── create.md               # /system-dev:create workflow
│   ├── read.md                 # /system-dev:read workflow
│   ├── update.md               # /system-dev:update workflow
│   ├── query.md                # /system-dev:query workflow
│   └── history.md              # /system-dev:history workflow
├── agents/                     # Agent definitions (later phases)
├── references/                 # Reference docs
│   └── slot-types.md           # Slot type catalog with field descriptions
├── templates/                  # Output templates
├── data/                       # Static data
├── schemas/                    # JSON Schema definitions (shipped with skill)
│   ├── component.json          # Component slot schema
│   ├── interface.json          # Interface slot schema
│   ├── contract.json           # Contract slot schema
│   └── requirement-ref.json    # Requirement reference slot schema
├── scripts/                    # Python utility scripts
│   ├── shared_io.py            # Atomic write, path validation (mirrors requirements-dev)
│   ├── registry.py             # Slot storage engine + API facade
│   ├── schema_validator.py     # Schema validation using jsonschema
│   ├── version_manager.py      # Version history from journal reconstruction
│   ├── change_journal.py       # JSONL append-only journal
│   └── init_workspace.py       # Creates .system-dev/ directory structure
└── tests/                      # pytest tests
```

### Recommended Workspace Directory Structure
```
.system-dev/                    # Created by /system-dev:init
├── registry/                   # Slot storage root
│   ├── components/             # Component slots
│   ├── interfaces/             # Interface slots
│   ├── contracts/              # Contract slots
│   └── requirement-refs/       # Requirement reference slots
├── journal.jsonl               # Append-only change journal
├── index.json                  # Slot index: ID -> path, type, timestamp, version
└── config.json                 # Workspace configuration (thresholds, limits)
```

### Pattern 1: Layered Module Architecture
**What:** Strict layering where slot-api is the only entry point, delegating to storage engine, schema validator, version manager, and change journal.
**When to use:** All registry operations.
**Example:**
```python
# Interaction flow (per requirements):
# Agent -> slot-api -> [schema-validator] -> slot-storage-engine -> [version-manager, change-journal]
#
# slot-api: capability check -> validate -> persist -> record history -> journal
# No agent ever touches files directly (XCUT-04)

class SlotAPI:
    """Single entry point for all registry operations (REQ-215..224)."""

    def __init__(self, storage_engine, schema_validator, version_manager, change_journal, capability_registry):
        self._storage = storage_engine
        self._validator = schema_validator
        self._versions = version_manager
        self._journal = change_journal
        self._capabilities = capability_registry

    def write(self, request: dict) -> dict:
        """Write slot: verify capability -> validate schema -> persist -> version -> journal."""
        # 1. Capability check (REQ-215, REQ-223)
        self._capabilities.verify(request["component_id"], request["slot_type"], "write")
        # 2. Schema validation (REQ-216)
        self._validator.validate(request["slot_type"], request["content"])
        # 3. Optimistic locking check (REQ-473)
        current = self._storage.read(request["slot_id"])
        if current and current["version"] != request.get("expected_version"):
            raise ConflictError(...)
        # 4. Persist (REQ-174)
        prev_content = current["content"] if current else None
        result = self._storage.write(request["slot_id"], request["slot_type"], request["content"])
        # 5. Version history (REQ-178, REQ-225)
        new_version = (current["version"] + 1) if current else 1
        self._versions.record(request["slot_id"], prev_content, request["content"], new_version)
        # 6. Change journal (REQ-176, REQ-207)
        self._journal.append(request["slot_id"], request["slot_type"], "update" if current else "create",
                            current["version"] if current else 0, new_version,
                            request.get("agent_id", "unknown"), request.get("summary", ""),
                            prev_content, request["content"])
        return {"status": "ok", "slot_id": request["slot_id"], "version": new_version, "path": result["path"]}
```

### Pattern 2: Atomic Write with Crash Recovery
**What:** Write-to-temp-then-rename pattern with orphan cleanup on startup.
**When to use:** All file mutations (slot writes, index updates).
**Example:**
```python
# Proven pattern from requirements-dev shared_io.py
import json, os
from tempfile import NamedTemporaryFile

def atomic_write(filepath: str, data: dict) -> None:
    """Write JSON atomically: temp file in same dir -> fsync -> rename."""
    target_dir = os.path.dirname(os.path.abspath(filepath))
    fd = NamedTemporaryFile(mode="w", dir=target_dir, suffix=".tmp", delete=False)
    try:
        json.dump(data, fd, indent=2)
        fd.write("\n")
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()
        os.rename(fd.name, filepath)  # Atomic on POSIX within same filesystem
    except Exception:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise

def cleanup_orphaned_temps(directory: str) -> list[str]:
    """Scan for and remove orphaned .tmp files from interrupted writes (REQ-153)."""
    cleaned = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".tmp"):
                path = os.path.join(root, f)
                os.unlink(path)
                cleaned.append(path)
    return cleaned
```

### Pattern 3: JSONL Append-Only Journal
**What:** One JSON object per line, append-only, immutable entries.
**When to use:** Change journal (REQ-207..214).
**Example:**
```python
import json, os
from datetime import datetime, timezone

def journal_append(journal_path: str, entry: dict) -> None:
    """Append a single JSON entry to the JSONL journal (REQ-207, REQ-479)."""
    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    line = json.dumps(entry, separators=(",", ":")) + "\n"
    with open(journal_path, "a") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())

def journal_query_time_range(journal_path: str, start: str, end: str) -> list[dict]:
    """Query journal entries within a UTC time range (REQ-208)."""
    results = []
    with open(journal_path) as f:
        for line in f:
            entry = json.loads(line)
            ts = entry["timestamp"]
            if start <= ts <= end:
                results.append(entry)
    return results
```

### Pattern 4: Simple RFC 6902 JSON Diff (No Third-Party Library)
**What:** Compute add/remove/replace operations between two JSON objects.
**When to use:** Journal entries recording what changed in a slot.
**Example:**
```python
def json_diff(old: dict | None, new: dict) -> list[dict]:
    """Compute RFC 6902-style JSON patch operations between old and new."""
    if old is None:
        return [{"op": "add", "path": "", "value": new}]
    ops = []
    all_keys = set(list(old.keys()) + list(new.keys()))
    for key in sorted(all_keys):
        path = f"/{key}"
        if key not in old:
            ops.append({"op": "add", "path": path, "value": new[key]})
        elif key not in new:
            ops.append({"op": "remove", "path": path})
        elif old[key] != new[key]:
            if isinstance(old[key], dict) and isinstance(new[key], dict):
                # Recurse for nested objects
                for sub_op in json_diff(old[key], new[key]):
                    sub_op["path"] = path + sub_op["path"]
                    ops.append(sub_op)
            else:
                ops.append({"op": "replace", "path": path, "value": new[key]})
    return ops
```

### Pattern 5: SKILL.md Structure
**What:** Skill entry point following Anthropic best practices.
**When to use:** The SKILL.md file itself.
**Example:**
```yaml
---
name: system-dev
description: >
  Guides AI-assisted systems design using INCOSE principles. Creates and manages
  a Design Registry with typed slots for components, interfaces, contracts, and
  requirements. Use when the user mentions system design, design registry,
  component decomposition, interface resolution, behavioral contracts,
  traceability, impact analysis, or /system-dev commands.
---
```
Then body contains: overview, security rules (`<security>` XML), path patterns (`<paths>` XML), command table, and progressive disclosure links to `commands/*.md`.

### Anti-Patterns to Avoid
- **Direct file access from agents:** All access must go through slot-api (XCUT-04). Never import storage engine directly from agent code.
- **Mutable journal entries:** Journal is append-only (REQ-406, REQ-479). No update-in-place.
- **Auto-creating workspace:** Must require explicit `/system-dev:init` per user decision.
- **Nested references in SKILL.md:** Keep all references one level deep. Commands reference SKILL.md directly; SKILL.md references commands/ directly.
- **Storing full version snapshots:** Per decision, old versions are reconstructed from journal diffs only. Do not store snapshot copies.
- **Using git library (e.g., gitpython):** REQ-180 requires CLI git only.
- **Cross-filesystem atomic rename:** Temp files must be in the same directory as target (REQ-186).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON Schema validation | Custom field-by-field checker | `jsonschema` library with Draft202012Validator | REQ-203, REQ-204 mandate it; handles $ref, allOf, oneOf, format, etc. |
| Atomic file writes | Custom lock file mechanism | tempfile + os.rename pattern | Proven pattern in requirements-dev; POSIX atomic rename guarantee |
| UUID generation | Custom ID format | `uuid.uuid4()` with type prefix | stdlib, no collisions, sortable with prefix (e.g., `comp-<uuid>`) |
| Path traversal protection | Regex-based validation | `os.path.realpath()` + startswith check | Handles symlinks, .., encoded chars correctly |
| UTC timestamps | Manual string formatting | `datetime.now(timezone.utc).isoformat()` | ISO 8601, timezone-aware, sortable as strings |

**Key insight:** The requirements explicitly constrain dependencies -- only jsonschema is allowed as a third-party dep for the schema-validator block, everything else must be stdlib (REQ-184). This means RFC 6902 diff computation and JSONL handling must be hand-built, but they are simple enough that a utility function suffices.

## Common Pitfalls

### Pitfall 1: Version Reconstruction from Journal Diffs
**What goes wrong:** The decision says "old versions reconstructed from journal diffs only" but journal entries could be truncated (REQ-210 allows time-based truncation), making old versions unrecoverable.
**Why it happens:** Retention policy removes entries needed for reconstruction.
**How to avoid:** Either (a) never truncate entries for slots that still exist, or (b) before truncation, ensure the current version on disk is always valid (it is -- only the current file exists). Version reconstruction should be best-effort: if journal entries are truncated, return "version history unavailable before [date]" rather than failing.
**Warning signs:** A rollback request targets a version whose journal entries have been truncated.

### Pitfall 2: Journal File Corruption on Partial Line Write
**What goes wrong:** If the process is killed mid-write to the JSONL journal, the last line may be incomplete JSON.
**Why it happens:** JSONL append is not atomic the way rename is.
**How to avoid:** On journal load/query, wrap each line parse in try/except. If the last line is corrupt, log a warning and skip it. Only the last line can ever be corrupt (append-only + fsync after each entry).
**Warning signs:** `json.loads()` fails on a journal line during query.

### Pitfall 3: Index File Inconsistency
**What goes wrong:** The slot index (`index.json`) gets out of sync with actual files on disk (e.g., crash between writing slot file and updating index).
**Why it happens:** Two separate file operations (slot write + index update) are not jointly atomic.
**How to avoid:** Write slot file first, then update index. On startup, offer index rebuild from filesystem scan (REQ-165). The index is a cache/optimization; the files on disk are the source of truth.
**Warning signs:** Index lists a slot ID that has no file, or a file exists not in the index.

### Pitfall 4: Optimistic Locking Race Condition
**What goes wrong:** Two concurrent writes read the same version, both pass the version check, both write.
**Why it happens:** No file-level locking between version check and write.
**How to avoid:** Since this is a single-user CLI tool (Claude Code context), true concurrency is unlikely. Still, serialize writes to the same slot using a simple file lock or in-process lock (REQ-157, REQ-405). A `fcntl.flock()` on the slot file during write is sufficient.
**Warning signs:** Version number jumps or journal shows two writes with the same version_before.

### Pitfall 5: Git Commit Per Write Slowing Everything Down
**What goes wrong:** REQ-152 says each write gets its own git commit. This can make writes very slow if many slots are updated in sequence.
**Why it happens:** `git add` + `git commit` for each individual slot write.
**How to avoid:** Consider a batch mode where git commits are deferred and batched (e.g., commit after all writes in a single agent operation complete). The requirement says "individual commit" but the intent is auditability -- a commit per logical operation (not per field) may be acceptable. Flag this as an implementation decision. Performance target is 300ms per git commit (REQ-168).
**Warning signs:** Batch operations taking 10+ seconds due to N sequential git commits.

### Pitfall 6: Schema Validation Error Messages Not Helpful
**What goes wrong:** jsonschema's default error messages are technical and unhelpful to users.
**Why it happens:** Library reports constraint violations in schema-speak, not user-speak.
**How to avoid:** Post-process `jsonschema.ValidationError` to produce user-friendly messages. Use `error.json_path` for the field path and write a custom message formatter that adds fix hints (per user decision). Example: transform `"'name' is a required property"` into `"Field 'components[0].name' is required. Add a name string to identify this component."`.
**Warning signs:** Users getting raw jsonschema error output.

## Code Examples

### JSON Schema for a Component Slot (Draft 2020-12)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://system-dev.local/schemas/component.json",
  "title": "Component Slot",
  "type": "object",
  "required": ["slot_id", "slot_type", "name", "version", "created_at", "updated_at"],
  "properties": {
    "slot_id": { "type": "string", "pattern": "^comp-[a-f0-9-]+$" },
    "slot_type": { "const": "component" },
    "name": { "type": "string", "minLength": 1, "maxLength": 200 },
    "description": { "type": "string" },
    "version": { "type": "integer", "minimum": 1 },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "source_block": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["proposed", "approved", "rejected", "modified", "deprecated"]
    },
    "parent_requirements": {
      "type": "array",
      "items": { "type": "string" }
    },
    "rationale": { "type": "string" },
    "extensions": { "type": "object" }
  },
  "additionalProperties": false
}
```

### Slot Index File Format
```json
{
  "schema_version": "1.0.0",
  "updated_at": "2026-02-28T12:00:00Z",
  "slots": {
    "comp-abc123": {
      "path": "registry/components/comp-abc123.json",
      "slot_type": "component",
      "version": 3,
      "updated_at": "2026-02-28T12:00:00Z"
    }
  }
}
```

### Journal Entry Format (JSONL)
```json
{"timestamp":"2026-02-28T12:00:00Z","slot_id":"comp-abc123","slot_type":"component","operation":"update","version_before":2,"version_after":3,"agent_id":"structural-decomposition","summary":"Updated component boundaries","diff":[{"op":"replace","path":"/description","value":"New description"}]}
```

### Schema Validation with User-Friendly Errors
```python
from jsonschema import Draft202012Validator, ValidationError

def validate_slot(slot_type: str, content: dict, schema: dict) -> list[dict]:
    """Validate slot content, returning user-friendly error list."""
    validator = Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(content), key=lambda e: list(e.path)):
        field_path = "/".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append({
            "path": field_path,
            "constraint": error.validator,
            "message": error.message,
            "hint": _generate_hint(error),
            "actual_value": error.instance if not isinstance(error.instance, dict) else "<object>",
        })
    return errors

def _generate_hint(error: ValidationError) -> str:
    """Generate a human-friendly fix hint from a validation error."""
    if error.validator == "required":
        field = error.message.split("'")[1]
        return f"Add the '{field}' field to this object."
    if error.validator == "type":
        return f"Change the value to type '{error.validator_value}'."
    if error.validator == "enum":
        return f"Use one of: {', '.join(repr(v) for v in error.validator_value)}."
    if error.validator == "pattern":
        return f"Value must match pattern: {error.validator_value}"
    return "Check the schema definition for valid values."
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| JSON Schema Draft 7 | JSON Schema Draft 2020-12 | 2020 | Required by REQ-203; uses `$dynamicRef`, vocabulary system |
| jsonschema 3.x | jsonschema 4.x | 2022 | New validator classes, referencing library, better error paths |
| os.path everywhere | pathlib preferred | Python 3.6+ | Cleaner path manipulation; still need os for fsync/rename |
| pip install | uv run | 2024+ | Faster, lockfile support, used by requirements-dev already |

**Deprecated/outdated:**
- `jsonschema.validate()` shorthand: Still works but `Draft202012Validator` class gives more control over error iteration
- `Draft4Validator`, `Draft7Validator`: Work but REQ-203 specifies 2020-12

## Open Questions

1. **Git commit granularity**
   - What we know: REQ-152 says "individual commit" per slot write. REQ-168 targets 300ms per commit.
   - What's unclear: Whether batch operations (e.g., ingesting 50 requirements) should produce 50 commits or 1.
   - Recommendation: Implement per-write commits as default with an optional batch context manager that defers commits. This satisfies the requirement while keeping batch operations practical.

2. **Capability registry bootstrap**
   - What we know: REQ-215..223 describe capability-based access where components need registered capabilities.
   - What's unclear: How capabilities are registered for Phase 1 when no agents exist yet.
   - Recommendation: Ship a default capability registry that grants all Phase 1 slot types to all known components. Tighten when agents arrive in Phase 3+.

3. **Version reconstruction depth limit**
   - What we know: Versions are reconstructed from journal diffs. Journal can be truncated.
   - What's unclear: What happens when a user requests version history for a slot whose early journal entries were truncated.
   - Recommendation: Return available history with a "history starts at version N" marker. Never fail on missing history.

4. **Slot ID format**
   - What we know: Must be unique, validated against character set (REQ-160).
   - What's unclear: Exact format convention.
   - Recommendation: `{type_prefix}-{uuid4}` (e.g., `comp-a1b2c3d4-...`). Type prefix aids debugging; UUID ensures uniqueness.

## Sources

### Primary (HIGH confidence)
- Requirements registry (`requirements_registry.json`) - All 125+ requirements for Phase 1 sub-blocks extracted and analyzed
- Skill authoring best practices (`_references/skill-authoring-best-practices.md`) - Anthropic's official guide
- Reference SKILL.md (`_references/SKILL.md`) - spec-validator skill as structural template
- Requirements-dev skill (`skills/requirements-dev/`) - Sibling skill providing proven patterns for directory structure, SKILL.md format, shared_io.py, security rules, path patterns
- [jsonschema PyPI](https://pypi.org/project/jsonschema/) - v4.26.0, Draft 2020-12 support confirmed
- [jsonschema docs](https://python-jsonschema.readthedocs.io/) - Draft202012Validator class, iter_errors API

### Secondary (MEDIUM confidence)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) - Spec referenced by REQ-203
- [jsonpatch PyPI](https://pypi.org/project/jsonpatch/) - v1.33, RFC 6902 reference (decided not to use as dependency)

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Requirements explicitly name libraries and versions; sibling skill provides proven pattern
- Architecture: HIGH - 125+ requirements define the architecture in detail; CONTEXT.md locks storage decisions
- Pitfalls: HIGH - Based on analysis of requirement interactions and proven failure modes in file-based storage systems
- Skill scaffold: HIGH - Direct copy of patterns from requirements-dev with well-documented Anthropic best practices

**Research date:** 2026-02-28
**Valid until:** 2026-03-28 (stable domain, low churn)
