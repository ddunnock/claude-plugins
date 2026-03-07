# /system-dev:history

Show the version history of a slot by reconstructing past states from journal diffs.

## Invocation

```
/system-dev:history <slot_id>
```

**Parameters:**
- `slot_id` (required): The full slot ID

## Workflow

1. **Look up slot in index**: Verify the slot exists.

2. **Read current slot**: Load the current slot content as the baseline.

3. **Query journal**: Read `.system-dev/journal.jsonl` and filter entries matching the slot ID. Sort by timestamp ascending.

4. **Display version timeline**: Show each version change with timestamp, operation, agent, summary, and key field changes.

5. **Reconstruct past version (on request)**: If the user asks to see a specific past version, apply journal diffs in reverse from the current version back to the requested version.

## Output Format

```markdown
## History: comp-a1b2c3d4-e5f6-7890-abcd-ef1234567890

**Current version:** 3
**Created:** 2026-02-28T10:00:00Z

| Version | Timestamp | Operation | Agent | Summary |
|---------|-----------|-----------|-------|---------|
| 1 | 2026-02-28T10:00:00Z | create | user | Initial creation |
| 2 | 2026-02-28T12:00:00Z | update | structural-decomposition | Updated boundaries |
| 3 | 2026-02-28T14:30:00Z | update | user | Changed status to approved |
```

If journal entries for early versions have been truncated:

```markdown
**Note:** History available from version 2 onwards. Earlier entries have been truncated.
```

## Error Handling

- **Slot not found**: Display "Slot ID not found" with suggestion to verify ID.
- **No journal entries**: Display "No history available" (slot may have been created before journaling was enabled).
- **Corrupt journal line**: Skip corrupt entries with a warning.
- **No workspace**: Suggest running `/system-dev:init` first.
