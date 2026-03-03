# /system-dev:view

Assemble a contextual view from registry slot subsets.

## Invocation

```
/system-dev:view <spec_name_or_pattern> [--json] [--param key=value]
```

**Parameters:**
- `spec_name_or_pattern` (required): Name of a built-in spec, a file path to a view-spec JSON file (e.g., `.system-dev/view-specs/my-spec.json`), OR an ad-hoc scope pattern (e.g., `component:Auth*`)
- `--json` (optional): Output structured JSON instead of human-readable tree
- `--param` (optional, repeatable): Parameter for parameterized specs (e.g., `--param component_id="Auth Service"`)

## Workflow

1. **Determine spec**:
   a. If `spec_name_or_pattern` matches a built-in spec name (one of: system-overview, traceability-chain, component-detail, interface-map, gap-report), use `get_builtin_spec()`.
   b. If `spec_name_or_pattern` is a file path (ends with `.json` or contains `/`), load it with `load_view_spec(spec_path, parameters, schemas_dir)` where `schemas_dir` is `${CLAUDE_PLUGIN_ROOT}/schemas`. This enables schema validation of user-authored specs.
   c. Otherwise, treat it as an ad-hoc scope pattern and call `create_ad_hoc_spec()`.

2. **Resolve parameters**: Apply `--param` values to parameterized specs via `get_builtin_spec(name, parameters)`.

3. **Initialize**: Load `SlotAPI` from `.system-dev/` workspace and locate the `schemas/` directory.

4. **Assemble**: Call `assemble_view(api, spec, workspace_root, schemas_dir)` from `scripts/view_assembler.py`.

5. **Render**: If `--json` flag is set, serialize the assembled view dict as JSON. Otherwise, call `render_tree(view)` for human-readable output.

6. **Display**: Print the rendered output to the user.

## Built-in Views

| Name | Description |
|------|-------------|
| `system-overview` | All components and their interfaces |
| `traceability-chain` | Requirements through components, interfaces, and contracts |
| `component-detail` | Single component with related interfaces and contracts (requires `--param component_id=<name>`) |
| `interface-map` | All interfaces grouped by component pairs |
| `gap-report` | Comprehensive gap analysis across all slot types |

## File-Based Specs

Users can create custom view-spec JSON files in `.system-dev/view-specs/` and invoke them by path:

```
/system-dev:view .system-dev/view-specs/my-custom-view.json --param component_id="Auth Service"
```

File-based specs are validated against the `view-spec.json` schema (via `load_view_spec()` with `schemas_dir`) before assembly. This ensures user-authored specs conform to the same structure as built-in specs.

To create a custom spec, copy one of the built-in specs from `${CLAUDE_PLUGIN_ROOT}/data/` as a starting point, then modify the scope patterns and options to match your needs.

## Output Format

**Tree output (default):**

```
View: system-overview
Assembled: 2026-03-02T14:30:00Z
Slots: 5  Gaps: 1

component/ (3)
+-- Auth Service (id=comp-aaa..., v2, approved)
+-- Database Service (id=comp-bbb..., v1, proposed)
+-- API Gateway (id=comp-ccc..., v1, proposed)

interface/ (2)
+-- Auth API (id=intf-ddd..., v1)
+-- DB Connection (id=intf-eee..., v1)

Gaps:
+-- [GAP] [WARNING] contract: No contract slots matching 'contract:*' found
    Suggestion: Run /system-dev:contract to define contracts.

Gap Summary:
  warning: 1
```

**JSON output (`--json`):**

Returns the full assembled view dict conforming to the `schemas/view.json` schema, with `spec_name`, `assembled_at`, `snapshot_id`, `total_slots`, `total_gaps`, `gap_summary`, `sections`, and `gaps` fields.

## Error Handling

- **No workspace**: Suggest running `/system-dev:init` first.
- **Unknown spec name and not a valid pattern**: List available built-in specs (`system-overview`, `traceability-chain`, `component-detail`, `interface-map`, `gap-report`).
- **Missing required parameter**: Show which parameters are needed (e.g., `component_id` for `component-detail`).
- **Empty view (no slots, no gaps)**: Show "View is empty -- no slots or gaps found for this specification."
