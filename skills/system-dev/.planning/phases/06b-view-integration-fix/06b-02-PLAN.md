---
phase: 06b-view-integration-fix
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - schemas/view.json
  - references/slot-types.md
autonomous: true
requirements: []
gap_closure: true

must_haves:
  truths:
    - "view.json schema enforces required fields (slot_id, slot_type, name, version) on sections[].slots items"
    - "view.json schema includes format_version field at top level"
    - "'unlinked' sentinel slot_type is documented for Phase 8 diagram consumers"
  artifacts:
    - path: "schemas/view.json"
      provides: "Tightened slot item schema with required fields and format_version"
      contains: "format_version"
    - path: "references/slot-types.md"
      provides: "Documentation of unlinked sentinel slot_type"
      contains: "unlinked"
  key_links:
    - from: "schemas/view.json"
      to: "scripts/view_assembler.py"
      via: "assemble_view validates output against view.json"
      pattern: "validate_or_raise.*view"
    - from: "scripts/view_assembler.py"
      to: "schemas/view.json"
      via: "_organize_hierarchically produces unlinked sections"
      pattern: "unlinked"
---

<objective>
Tighten view.json schema (required slot fields, format_version) and document the "unlinked" sentinel slot_type for downstream Phase 8 consumers.

Purpose: Close schema tech debt and documentation gaps so Phase 8 diagram generation has clear contracts for slot items and the unlinked sentinel.
Output: Updated schemas/view.json, updated references/slot-types.md.
</objective>

<execution_context>
@/Users/dunnock/.claude/get-shit-done/workflows/execute-plan.md
@/Users/dunnock/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/v1.1-MILESTONE-AUDIT.md

<interfaces>
<!-- Current view.json schema sections[].slots is bare "object" with no required fields -->
<!-- view_assembler.py always includes slot_id, slot_type, name, version in output (system fields) -->

From scripts/view_assembler.py:
```python
_SYSTEM_FIELDS = {"slot_id", "slot_type", "name", "version"}

# _organize_hierarchically produces "unlinked" sections for orphan slots:
if unlinked:
    result.append({"slot_type": "unlinked", "slots": unlinked})
```

From schemas/view.json (current — sections[].slots items typed as bare object):
```json
"slots": {
    "type": "array",
    "items": {
        "type": "object"
    }
}
```

From scripts/view_assembler.py assemble_view():
```python
# Output always includes format: assembled["format_version"] would need to be added
# Currently not in the assembled dict — need to add it to assemble_view() output too
assembled = {
    "spec_name": spec["name"],
    "assembled_at": datetime.now(timezone.utc).isoformat(),
    "snapshot_id": snapshot["snapshot_id"],
    ...
}
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Tighten view.json schema and add format_version</name>
  <files>schemas/view.json, scripts/view_assembler.py, tests/test_view_assembler.py, tests/test_view_integration.py</files>
  <behavior>
    - Test: assembled view includes format_version field with value "1.0"
    - Test: assembled view validates against updated schema with required slot fields
    - Test: existing integration tests still pass with tightened schema
  </behavior>
  <action>
**schemas/view.json** -- Make two changes:

1. Add `format_version` as a required top-level field:
   - Add `"format_version"` to the `"required"` array
   - Add property definition:
     ```json
     "format_version": {
         "type": "string",
         "pattern": "^\\d+\\.\\d+$",
         "description": "Schema format version for future evolution (e.g., '1.0')"
     }
     ```

2. Tighten `sections[].slots.items` from bare `"type": "object"` to require system fields:
   ```json
   "items": {
       "type": "object",
       "required": ["slot_id", "slot_type", "name", "version"],
       "properties": {
           "slot_id": { "type": "string", "minLength": 1 },
           "slot_type": { "type": "string", "minLength": 1 },
           "name": { "type": "string", "minLength": 1 },
           "version": { "type": "integer", "minimum": 1 }
       }
   }
   ```
   Do NOT add `additionalProperties: false` here -- slots have varying fields beyond the required system fields.

**scripts/view_assembler.py** -- In `assemble_view()`, add `"format_version": "1.0"` to the `assembled` dict (around line 433-442), before schema validation runs. Place it after `"spec_name"`:

```python
assembled = {
    "spec_name": spec["name"],
    "format_version": "1.0",
    "assembled_at": ...
}
```

**tests/test_view_assembler.py** -- Add a test that verifies `assemble_view()` output contains `format_version` equal to `"1.0"`. Can be a simple assertion added to an existing assembly test or a new focused test.

**tests/test_view_integration.py** -- If any integration tests construct view dicts manually for schema validation, add `format_version` to them. Run full test suite to catch any that need updating.

IMPORTANT: The "unlinked" section slots are real registry slots (interfaces/contracts) that have system fields. They will naturally satisfy the new required fields constraint. No special handling needed for unlinked sections.
  </action>
  <verify>
    <automated>cd /Users/dunnock/projects/claude-plugins/skills/system-dev && uv run python -m pytest tests/test_view_assembler.py tests/test_view_integration.py -x -q 2>&1 | tail -5</automated>
  </verify>
  <done>
    - view.json schema requires slot_id, slot_type, name, version on slot items
    - view.json schema requires and defines format_version field
    - assemble_view() outputs format_version: "1.0"
    - All view tests pass with tightened schema
  </done>
</task>

<task type="auto">
  <name>Task 2: Document "unlinked" sentinel slot_type for Phase 8 consumers</name>
  <files>references/slot-types.md</files>
  <action>
Add a new section to `references/slot-types.md` documenting the "unlinked" sentinel slot_type. Place it after the existing slot type documentation.

Add a section like:

```markdown
## View-Only Slot Types

These slot types appear only in assembled view output (not in the Design Registry).

### unlinked

**Purpose:** Contains orphan slots (interfaces and contracts) that could not be linked to a parent component within the view's scope.

**When it appears:** During hierarchical view organization, interfaces without a matching `source_component` or `target_component` in the view, and contracts without a matching `interface_id`, are grouped into an `"unlinked"` section rather than being dropped.

**For diagram consumers (Phase 8+):** When generating diagrams from view output, `slot_type: "unlinked"` sections should be rendered as a separate group or with visual distinction (e.g., dashed borders, "Unlinked" label) to indicate these slots lack structural connections in the current view scope.

**Schema:** Unlinked section slots have the same fields as their original slot type (interface or contract). The `slot_type` field on each individual slot retains its original value (e.g., `"interface"`, `"contract"`); only the section-level `slot_type` is `"unlinked"`.
```

Review the existing file structure first and match its formatting conventions.
  </action>
  <verify>
    <automated>cd /Users/dunnock/projects/claude-plugins/skills/system-dev && grep -q "unlinked" references/slot-types.md && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <done>
    - references/slot-types.md documents "unlinked" sentinel slot_type
    - Documentation explains purpose, when it appears, and guidance for Phase 8 diagram consumers
    - Individual slot items retain their original slot_type field
  </done>
</task>

</tasks>

<verification>
1. `uv run python -c "import json; s=json.load(open('schemas/view.json')); print('format_version' in s['required'])"` returns True
2. `uv run python -c "import json; s=json.load(open('schemas/view.json')); print(s['properties']['sections']['items']['properties']['slots']['items'].get('required'))"` shows system fields
3. `grep "unlinked" references/slot-types.md` shows documentation
4. `uv run python -m pytest tests/ -x -q` full regression passes
</verification>

<success_criteria>
- view.json schema enforces required fields on slot items (slot_id, slot_type, name, version)
- view.json schema includes format_version field
- assemble_view() produces format_version: "1.0" in output
- "unlinked" sentinel is documented in references/slot-types.md for Phase 8
- All tests pass
</success_criteria>

<output>
After completion, create `.planning/phases/06b-view-integration-fix/06b-02-SUMMARY.md`
</output>
