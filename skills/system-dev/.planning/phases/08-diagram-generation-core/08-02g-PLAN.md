---
phase: 08-diagram-generation-core
plan: 02g
type: execute
wave: 1
depends_on: []
files_modified:
  - scripts/diagram_generator.py
  - scripts/view_assembler.py
  - schemas/view-spec.json
  - tests/test_diagram_generator.py
  - .planning/REQUIREMENTS.md
autonomous: true
gap_closure: true
requirements: [DIAG-03, DIAG-09]

must_haves:
  truths:
    - "generate_diagram() orchestrates view assembly -> format selection -> D2/Mermaid generation -> SlotAPI.ingest()"
    - "diagram_hint field exists on view-spec.json schema as optional enum (structural, behavioral)"
    - "BUILTIN_SPECS entries have diagram_hint values matching CONTEXT.md decisions"
    - "Generating diagrams only writes diagram-type slots (DIAG-09 preservation)"
  artifacts:
    - path: "scripts/diagram_generator.py"
      provides: "generate_diagram() orchestration function"
      contains: "def generate_diagram"
    - path: "schemas/view-spec.json"
      provides: "Optional diagram_hint field"
      contains: "diagram_hint"
    - path: "scripts/view_assembler.py"
      provides: "diagram_hint in BUILTIN_SPECS"
      contains: "diagram_hint"
    - path: "tests/test_diagram_generator.py"
      provides: "Integration tests for orchestration"
      contains: "TestGenerateDiagramOrchestration"
  key_links:
    - from: "scripts/diagram_generator.py"
      to: "scripts/registry.py"
      via: "SlotAPI.ingest() for diagram slot writes"
      pattern: "api\\.ingest\\("
    - from: "scripts/diagram_generator.py"
      to: "scripts/view_assembler.py"
      via: "assemble_view() call for view data"
      pattern: "assemble_view\\("
    - from: "commands/diagram.md"
      to: "scripts/diagram_generator.py"
      via: "generate_diagram() entry point"
      pattern: "generate_diagram\\("
---

<objective>
Close Plan 08-02 gaps: implement the diagram orchestration layer that was never written despite commit 55d8d27 claiming otherwise.

Purpose: DIAG-03 (SlotAPI write integration) and DIAG-09 (slot preservation) are blocked because generate_diagram() does not exist. The diagram_hint field is missing from view-spec.json and BUILTIN_SPECS.

Output: Working generate_diagram() orchestrator, diagram_hint on specs, integration tests, corrected REQUIREMENTS.md
</objective>

<execution_context>
@/Users/dunnock/.claude/get-shit-done/workflows/execute-plan.md
@/Users/dunnock/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/08-diagram-generation-core/08-01-SUMMARY.md
@.planning/phases/08-diagram-generation-core/08-CONTEXT.md
@.planning/phases/08-diagram-generation-core/08-RESEARCH.md
@.planning/phases/08-diagram-generation-core/08-VERIFICATION.md

<interfaces>
<!-- Key types and contracts the executor needs. Extracted from codebase. -->

From scripts/registry.py — SlotAPI.ingest():
```python
def ingest(
    self,
    slot_id: str,
    slot_type: str,
    content: dict,
    agent_id: str = "ingestion-engine",
) -> dict:
    """Ingest an upstream entity as a slot with a deterministic ID.
    Conflict handling:
    - If slot exists with version > 1 (manually edited), SKIP (status "conflict").
    - If slot exists with version 1, treat as update: increment version.
    - If slot does not exist, create with version 1.
    Returns: Dict with status ("created", "updated", or "conflict"), slot_id, version.
    """
```

From scripts/registry.py — SlotAPI.query():
```python
def query(self, slot_type: str, filters: dict | None = None) -> list[dict]:
    """Query slots by type with optional field=value filters."""
```

From scripts/view_assembler.py — assemble_view():
```python
def assemble_view(
    api: SlotAPI,
    spec: dict,
    workspace_root: str,
    schemas_dir: str,
) -> dict:
    """Assemble a contextual view from registry slots based on a view spec.
    Returns: Assembled view dict conforming to view.json schema.
    """
```

From scripts/view_assembler.py — get_builtin_spec():
```python
def get_builtin_spec(name: str, parameters: dict | None = None) -> dict:
    """Look up a built-in view spec by name and resolve parameters.
    Returns: A deep copy of the spec dict with parameters resolved.
    Raises: ValueError if name is not a recognized built-in spec.
    """
```

From scripts/diagram_generator.py — existing functions:
```python
def generate_d2(view: dict) -> str: ...
def generate_mermaid(view: dict) -> str: ...
def _compute_diagram_slot_id(spec_name: str, source: str) -> str: ...
def _sanitize_id(slot_id: str) -> str: ...
```

From schemas/view-spec.json — current properties:
```
name, description, scope_patterns, parameters, ranking
(additionalProperties: false — so diagram_hint must be added to properties)
```

From scripts/view_assembler.py — BUILTIN_SPECS keys:
```
system-overview, traceability-chain, component-detail, interface-map, gap-report
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add diagram_hint to view-spec schema and BUILTIN_SPECS, fix REQUIREMENTS.md</name>
  <files>schemas/view-spec.json, scripts/view_assembler.py, .planning/REQUIREMENTS.md</files>
  <behavior>
    - Test 1: view-spec.json schema accepts a spec with diagram_hint: "structural"
    - Test 2: view-spec.json schema accepts a spec with diagram_hint: "behavioral"
    - Test 3: view-spec.json schema accepts a spec without diagram_hint (backward compatible)
    - Test 4: view-spec.json schema rejects diagram_hint: "invalid"
    - Test 5: BUILTIN_SPECS["system-overview"] has diagram_hint "structural"
    - Test 6: BUILTIN_SPECS["traceability-chain"] has diagram_hint "behavioral"
    - Test 7: BUILTIN_SPECS["component-detail"] has diagram_hint "structural"
    - Test 8: BUILTIN_SPECS["interface-map"] has diagram_hint "structural"
    - Test 9: BUILTIN_SPECS["gap-report"] has no diagram_hint key
  </behavior>
  <action>
    1. Add `diagram_hint` property to `schemas/view-spec.json` as an optional field (NOT in required array):
       ```json
       "diagram_hint": {
         "type": "string",
         "enum": ["structural", "behavioral"],
         "description": "Hint for diagram format: structural -> D2, behavioral -> Mermaid"
       }
       ```

    2. Add `diagram_hint` values to BUILTIN_SPECS in `scripts/view_assembler.py`:
       - `system-overview`: `"diagram_hint": "structural"`
       - `traceability-chain`: `"diagram_hint": "behavioral"`
       - `component-detail`: `"diagram_hint": "structural"`
       - `interface-map`: `"diagram_hint": "structural"`
       - `gap-report`: NO diagram_hint (requires explicit --format per CONTEXT.md)

    3. Fix `.planning/REQUIREMENTS.md`: Change DIAG-03 and DIAG-09 from `[x]` back to `[ ]` (line 29 and 35). Also change status in traceability table from "Complete" to "Pending" for both.

    4. Write tests in `tests/test_diagram_generator.py` for view-spec schema validation and BUILTIN_SPECS diagram_hint presence (add a new TestDiagramHint class).
  </action>
  <verify>
    <automated>cd /Users/dunnock/projects/claude-plugins/skills/system-dev && python -m pytest tests/test_diagram_generator.py -x -q 2>&1 | tail -5</automated>
  </verify>
  <done>
    - view-spec.json has optional diagram_hint enum field
    - 4 of 5 BUILTIN_SPECS have diagram_hint values matching CONTEXT.md
    - gap-report has no diagram_hint
    - REQUIREMENTS.md correctly marks DIAG-03 and DIAG-09 as Pending
    - All existing + new tests pass
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Implement generate_diagram() orchestration and integration tests</name>
  <files>scripts/diagram_generator.py, tests/test_diagram_generator.py</files>
  <behavior>
    - Test 1: generate_diagram() calls assemble_view and returns diagram source + slot result
    - Test 2: generate_diagram() with format_override="d2" produces D2 output regardless of hint
    - Test 3: generate_diagram() with format_override="mermaid" produces Mermaid output regardless of hint
    - Test 4: generate_diagram() resolves "structural" hint to D2 generation
    - Test 5: generate_diagram() resolves "behavioral" hint to Mermaid generation
    - Test 6: generate_diagram() raises ValueError when no hint and no format_override
    - Test 7: generate_diagram() writes diagram slot via SlotAPI.ingest() with slot_type="diagram"
    - Test 8: generate_diagram() uses content-hash slot_id (diag-{spec}-{hash})
    - Test 9: generate_diagram() skips write when content hash matches existing slot (no-op)
    - Test 10: generate_diagram() only writes "diagram" type slots (DIAG-09)
    - Test 11: generate_diagram() populates all diagram schema fields (format, diagram_type, source, source_view_spec, source_snapshot_id, slot_count, gap_count)
    - Test 12: generate_diagram() with literal "d2" hint produces D2
    - Test 13: generate_diagram() with literal "mermaid" hint produces Mermaid
    - Test 14: generate_diagram() returns dict with source, slot_id, status keys
    - Test 15: generate_diagram() handles empty view (no sections/edges/gaps)
    - Test 16: generate_diagram() with spec that has no slots still produces valid diagram
    - Test 17: generate_diagram() passes diagram slot through schema validation before write
  </behavior>
  <action>
    Add `generate_diagram()` function to `scripts/diagram_generator.py`. This is the orchestration layer that:

    1. **Imports needed**: Add imports at top of file:
       ```python
       import copy
       import json
       from datetime import datetime, timezone
       from scripts.registry import SlotAPI
       from scripts.view_assembler import assemble_view
       from scripts.schema_validator import SchemaValidator
       ```

    2. **Format resolution** helper `_resolve_format(format_override, spec)`:
       - If format_override is provided, use it directly ("d2" or "mermaid")
       - Else check spec.get("diagram_hint"):
         - "structural" or "d2" -> "d2"
         - "behavioral" or "mermaid" -> "mermaid"
         - None/missing -> raise ValueError("No diagram_hint on spec '{name}' and no --format override provided")
       - Return tuple of (format_str, diagram_type_str) where diagram_type is "structural"/"behavioral"

    3. **Main function** `generate_diagram(api, spec, workspace_root, schemas_dir, format_override=None)`:
       - Call `assemble_view(api, spec, workspace_root, schemas_dir)` to get view dict
       - Resolve format via `_resolve_format(format_override, spec)`
       - Call `generate_d2(view)` or `generate_mermaid(view)` based on format
       - Compute slot_id via `_compute_diagram_slot_id(spec["name"], source)`
       - Check if slot already exists via `api.read(slot_id)` — if so, return `{"status": "unchanged", "slot_id": slot_id, "source": source}`
       - Build diagram slot content dict with all required fields:
         - name: f"diagram-{spec['name']}"
         - format: format_str (d2/mermaid)
         - diagram_type: diagram_type_str (structural/behavioral)
         - source: generated source string
         - source_view_spec: spec["name"]
         - source_snapshot_id: view["snapshot_id"]
         - slot_count: view["total_slots"]
         - gap_count: view["total_gaps"]
       - Call `api.ingest(slot_id, "diagram", content, agent_id="diagram-generator")`
       - Return dict: `{"status": result["status"], "slot_id": slot_id, "source": source, "format": format_str, "diagram_type": diagram_type_str}`

    4. **Integration tests** in `tests/test_diagram_generator.py`:
       - Add `TestGenerateDiagramOrchestration` class with 17 tests
       - Use `tmp_path` fixture to create temp workspace with registry dirs
       - Create a real SlotAPI instance pointing to tmp_path
       - Create minimal slots so assemble_view works
       - Test the full pipeline: generate_diagram() -> verify source + slot written
       - Test format override, hint resolution, error cases, DIAG-09 compliance
       - For DIAG-09 test: verify that after generate_diagram(), only "diagram" type slots were created/modified (query all slot types, compare before/after)
  </action>
  <verify>
    <automated>cd /Users/dunnock/projects/claude-plugins/skills/system-dev && python -m pytest tests/test_diagram_generator.py -x -q 2>&1 | tail -5</automated>
  </verify>
  <done>
    - generate_diagram() exists and orchestrates the full pipeline
    - Format resolution: format_override > spec.diagram_hint > ValueError
    - Hint mapping: structural/d2 -> D2, behavioral/mermaid -> Mermaid
    - Content-hash slot IDs with update-on-change-only semantics
    - SlotAPI.ingest() called with slot_type="diagram" only (DIAG-09)
    - All 17 new integration tests pass alongside existing 41 tests
    - Total: 58+ tests in test_diagram_generator.py
  </done>
</task>

</tasks>

<verification>
1. `python -m pytest tests/test_diagram_generator.py -x -q` — all tests pass (58+)
2. `python -m pytest tests/ -x -q` — full test suite passes
3. `grep -c "diagram_hint" scripts/view_assembler.py` — returns 4 (one per spec that has it)
4. `python -c "import json; s=json.load(open('schemas/view-spec.json')); print('diagram_hint' in s['properties'])"` — prints True
5. `grep "generate_diagram" scripts/diagram_generator.py | head -1` — shows function definition
6. `grep "DIAG-03" .planning/REQUIREMENTS.md` — shows `[ ]` not `[x]`
</verification>

<success_criteria>
- generate_diagram() orchestrates assemble_view -> format resolution -> generation -> SlotAPI.ingest()
- diagram_hint is an optional enum field on view-spec.json schema (backward compatible)
- BUILTIN_SPECS have correct diagram_hint values per CONTEXT.md decisions
- Only "diagram" type slots are written (DIAG-09)
- REQUIREMENTS.md correctly reflects DIAG-03 and DIAG-09 as Pending
- All tests pass (existing 41 + ~17 new integration tests)
</success_criteria>

<output>
After completion, create `.planning/phases/08-diagram-generation-core/08-02g-SUMMARY.md`
</output>
