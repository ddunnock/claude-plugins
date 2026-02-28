# /system-dev:status

Show a summary of the current design registry state.

## Invocation

```
/system-dev:status
```

No parameters required.

## Workflow

1. **Check workspace exists**: Verify `.system-dev/` exists. If not, suggest running `/system-dev:init`.

2. **Load index**: Read `.system-dev/index.json` to get slot counts and metadata.

3. **Count slots by type**: Aggregate slot counts from the index:
   - Components
   - Interfaces
   - Contracts
   - Requirement-refs

4. **Read recent journal entries**: Load the last 10 entries from `.system-dev/journal.jsonl` for recent activity.

5. **Load config**: Read `.system-dev/config.json` for workspace version info.

6. **Display summary**: Present formatted output.

## Output Format

```markdown
## Design Registry Status

**Workspace version:** 0.1.0
**Schema version:** 1.0.0

### Slot Counts

| Type | Count | Latest Update |
|------|-------|---------------|
| component | N | YYYY-MM-DDTHH:MM:SSZ |
| interface | N | YYYY-MM-DDTHH:MM:SSZ |
| contract | N | YYYY-MM-DDTHH:MM:SSZ |
| requirement-ref | N | YYYY-MM-DDTHH:MM:SSZ |

### Recent Activity (last 10 entries)

| Timestamp | Operation | Slot | Summary |
|-----------|-----------|------|---------|
| ... | create | comp-xxx | ... |
```

## Error Handling

- **No workspace**: Display message suggesting `/system-dev:init`.
- **Corrupt index**: Suggest re-indexing from filesystem scan.
