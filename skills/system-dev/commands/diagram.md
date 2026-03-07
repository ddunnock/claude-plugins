# /system-dev:diagram

Generate D2 structural or Mermaid behavioral diagrams from view specifications.

## Invocation

```
/system-dev:diagram <spec_name_or_path> [--format d2|mermaid] [--param key=value]
```

**Parameters:**
- `spec_name_or_path` (required): Name of a built-in spec (system-overview, traceability-chain, component-detail, interface-map) OR a file path to a view-spec JSON file. No ad-hoc patterns -- diagrams are intentional artifacts from named specs only.
- `--format` (optional): Override diagram format. `d2` for D2 structural, `mermaid` for Mermaid behavioral. Defaults to the spec's `diagram_hint` field. Error if neither specified.
- `--param` (optional, repeatable): Parameter for parameterized specs (e.g., `--param component_id="Auth Service"`)

## Workflow

1. **Determine spec**: Same as /system-dev:view (built-in via `get_builtin_spec()`, file path via `load_view_spec()`). Reject ad-hoc patterns with error message directing users to create a named spec instead.
2. **Resolve parameters**: Apply `--param` values via `get_builtin_spec(name, parameters)` or `load_view_spec(path, parameters, schemas_dir)`.
3. **Initialize**: Load `SlotAPI` from `.system-dev/` workspace and locate `schemas/` directory.
4. **Generate**: Call `generate_diagram(api, spec, workspace_root, schemas_dir, format_override)` from `scripts/diagram_generator.py`.
5. **Display**: Print header (format, diagram type, slot_id, storage path) then the diagram source to stdout.

## Built-in Diagram Specs

| Name | Default Format | Diagram Type |
|------|---------------|--------------|
| system-overview | D2 | structural |
| traceability-chain | Mermaid | behavioral |
| component-detail | D2 | structural |
| interface-map | D2 | structural |
| gap-report | (none -- requires --format) | varies |

## Output Format

Diagram source is printed to stdout with a header block:

```
--- Diagram: {spec_name} ---
Format: {d2|mermaid}
Type: {structural|behavioral}
Slot: {slot_id}
Status: {created|updated|unchanged}
Slots: {N}, Gaps: {N}
---
{diagram source code}
```

## Error Handling

- **No spec found**: List available built-in specs (system-overview, traceability-chain, component-detail, interface-map, gap-report).
- **No format** (no `diagram_hint`, no `--format`): Error with guidance to use `--format d2` or `--format mermaid`, or add `diagram_hint` to the view spec.
- **Empty view** (no slots matched): Generate minimal diagram with comment header only, warn user.
- **Invalid spec schema**: Error from `SchemaValidator` with field-level details.
- **Ad-hoc pattern rejected**: Error explaining diagrams require named specs, not ad-hoc patterns. Suggest creating a view-spec JSON file in `.system-dev/view-specs/`.
