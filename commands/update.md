# /system-dev:update

Update an existing design slot with new field values.

## Invocation

```
/system-dev:update <slot_id>
```

**Parameters:**
- `slot_id` (required): The full slot ID to update

## Workflow

1. **Look up slot in index**: Find the slot entry in `.system-dev/index.json`.

2. **Read current slot**: Load the current slot content from disk.

3. **Optimistic locking check**: Compare the current version with the expected version. If the user specifies `expected_version` and it does not match the current version, abort with a conflict error.

4. **Gather updates**: Collect field changes from the user. Only specified fields are updated; others remain unchanged.

5. **Apply updates**: Merge new field values into the existing slot content. Update `updated_at` to current UTC timestamp.

6. **Increment version**: Set `version` to current version + 1.

7. **Validate against schema**: Run the updated content against the JSON Schema. If validation fails, report errors and do not write.

8. **Write slot file**: Use atomic write to save the updated slot.

9. **Update index**: Update the index entry with new version and timestamp.

10. **Record in journal**: Append entry with operation "update", version_before, version_after, and RFC 6902 diff of the changes.

11. **Report result**: Display updated slot summary with version change.

## Output Format

```markdown
## Slot Updated

**ID:** comp-a1b2c3d4-e5f6-7890-abcd-ef1234567890
**Version:** 2 -> 3
**Updated fields:** description, status
**Path:** .system-dev/registry/components/comp-a1b2c3d4-...json
```

## Error Handling

- **Slot not found**: Display "Slot ID not found" with suggestion to check ID.
- **Version conflict**: Display current version vs expected version. Suggest re-reading the slot before updating.
- **Schema validation failure**: Display errors with field paths and fix hints. Do not write.
- **No workspace**: Suggest running `/system-dev:init` first.
