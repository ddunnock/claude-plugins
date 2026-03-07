# /system-dev:create

Create a new design slot of a given type in the registry.

## Invocation

```
/system-dev:create <slot_type>
```

**Parameters:**
- `slot_type` (required): One of `component`, `interface`, `contract`, `requirement-ref`

## Workflow

1. **Validate slot type**: Confirm the type is one of the supported Phase 1 types.

2. **Gather slot data**: Collect required fields from the user:
   - `name` (required, 1-200 chars)
   - `description` (optional)
   - Type-specific fields (see [references/slot-types.md](../references/slot-types.md))

3. **Generate slot ID**: Create ID using type prefix + UUID4:
   - component: `comp-<uuid4>`
   - interface: `intf-<uuid4>`
   - contract: `cntr-<uuid4>`
   - requirement-ref: `rref-<uuid4>`

4. **Set metadata fields**:
   - `version`: 1
   - `status`: "proposed"
   - `created_at`: current UTC ISO 8601 timestamp
   - `updated_at`: same as created_at

5. **Validate against schema**: Run the slot content against the JSON Schema at `${CLAUDE_PLUGIN_ROOT}/schemas/<slot_type>.json`. If validation fails, report errors with field paths and fix hints.

6. **Write slot file**: Use atomic write (temp + rename) to save to `.system-dev/registry/<type_plural>/<slot_id>.json`.

7. **Update index**: Add entry to `.system-dev/index.json` with slot path, type, version, timestamp.

8. **Record in journal**: Append entry to `.system-dev/journal.jsonl` with operation "create", version_before 0, version_after 1.

9. **Report result**: Display the created slot with its ID and path.

## Output Format

```markdown
## Slot Created

**ID:** comp-a1b2c3d4-e5f6-7890-abcd-ef1234567890
**Type:** component
**Name:** User Authentication Service
**Version:** 1
**Path:** .system-dev/registry/components/comp-a1b2c3d4-e5f6-7890-abcd-ef1234567890.json
```

## Error Handling

- **Invalid slot type**: List valid types and exit.
- **Schema validation failure**: Display each error with field path, constraint violated, and fix hint.
- **Write failure**: Report error; atomic write ensures no partial files.
- **No workspace**: Suggest running `/system-dev:init` first.
