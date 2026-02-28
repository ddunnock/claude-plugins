# /system-dev:query

List slots of a given type with optional field-based filters.

## Invocation

```
/system-dev:query <slot_type> [--filter field=value]
```

**Parameters:**
- `slot_type` (required): One of `component`, `interface`, `contract`, `requirement-ref`
- `--filter` (optional, repeatable): Field-value filter in `field=value` format

## Workflow

1. **Validate slot type**: Confirm the type is supported.

2. **Load index**: Read `.system-dev/index.json` and filter to entries matching the slot type.

3. **Apply filters**: If `--filter` flags are provided, load each matching slot file and check that the specified field equals the specified value. String matching is case-insensitive.

4. **Sort results**: Order by `updated_at` descending (most recent first).

5. **Format output**: Display results as a table.

## Output Format

```markdown
## Query: component

**Filters:** status=approved
**Results:** 3 slots

| ID | Name | Version | Status | Updated |
|----|------|---------|--------|---------|
| comp-aaa... | Auth Service | 3 | approved | 2026-02-28T14:30:00Z |
| comp-bbb... | Data Store | 2 | approved | 2026-02-28T12:00:00Z |
| comp-ccc... | API Gateway | 1 | approved | 2026-02-27T10:00:00Z |
```

## Error Handling

- **Invalid slot type**: List valid types.
- **No results**: Display "No slots found matching query" with suggestion to broaden filters.
- **Invalid filter field**: Warn that the field is not in the schema but still attempt matching.
- **No workspace**: Suggest running `/system-dev:init` first.
