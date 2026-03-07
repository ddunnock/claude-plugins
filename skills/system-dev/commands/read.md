# /system-dev:read

Read a design slot by its ID and display formatted content.

## Invocation

```
/system-dev:read <slot_id>
```

**Parameters:**
- `slot_id` (required): The full slot ID (e.g., `comp-a1b2c3d4-...`)

## Workflow

1. **Look up slot in index**: Find the slot entry in `.system-dev/index.json` by ID.

2. **Read slot file**: Load the JSON file from the path recorded in the index.

3. **Format output**: Display the slot content in structured markdown.

## Output Format

```markdown
## Slot: comp-a1b2c3d4-e5f6-7890-abcd-ef1234567890

**Type:** component
**Name:** User Authentication Service
**Version:** 3
**Status:** approved
**Created:** 2026-02-28T12:00:00Z
**Updated:** 2026-02-28T14:30:00Z

### Description

Handles user login, token generation, and session management.

### Type-Specific Fields

| Field | Value |
|-------|-------|
| source_block | AUTH-BLOCK |
| parent_requirements | REQ-001, REQ-015 |
| rationale | Extracted from auth subsystem decomposition |

### Extensions

(custom fields if any)
```

## Error Handling

- **Slot not found**: Display "Slot ID not found in index" with suggestion to use `/system-dev:query` to list available slots.
- **File missing**: If index entry exists but file is missing, report inconsistency and suggest re-indexing.
- **No workspace**: Suggest running `/system-dev:init` first.
