# Phase 3: Self-Healing - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Skills can automatically fix or get structured fix guidance for malformed files. Two modes: auto-fix (applies corrections and writes the file) and suggest (returns structured fix guidance without modifying the file). Implements HEAL-01 and HEAL-02 requirements.

</domain>

<decisions>
## Implementation Decisions

### Fix Strategies
- **Conservative coercion only**: safe type coercions (string '5' -> number 5, string 'true' -> boolean true, null -> schema default). No ambiguous coercions (e.g., 'yes' -> boolean)
- **Schema defaults for missing fields**: use Zod `.default()` values when defined. If no default exists for a required field, report as unfixable (never invent data)
- **Single pass**: apply all fixable corrections in one pass, then re-validate. If still invalid, return partial results + remaining errors
- **Partial healing allowed**: write partially-healed file to disk, return both applied fixes and remaining unfixable errors. Caller sees what was fixed and what still needs attention

### Suggestion Format
- **Fix instructions list**: array of structured fix objects with path, issue, currentValue, suggestedValue, fixType, confidence
- **Unfixable errors included**: same list, tagged with fixType: 'manual' and human-readable explanation of why it can't be auto-fixed
- **Two-tier confidence**: 'safe' (schema default applied, exact type coercion) and 'uncertain' (lossy coercion, multiple possible fixes)
- **Already-valid files**: return { valid: true, suggestions: [] } — clear signal healing isn't needed

### Data Safety
- **Unknown fields always preserved**: fields not in the schema pass through untouched during healing
- **Healing at raw data layer**: merge fixes into raw parsed data before Zod validation, not from Zod's validated output. Unknown fields survive regardless of schema strictness
- **No backup files**: applied changes list serves as the record of what changed (currentValue -> newValue in each fix object)
- **Enum mismatches are unfixable**: can't guess intended value from allowed options. Report as manual with allowed values listed

### Tool Interface
- **Simple API**: keep existing three params (filePath, schemaName, mode: 'auto' | 'suggest'). No additional parameters
- **Auto mode response**: { healed: true, data: <full healed object>, applied: [...fixes], remaining: [...unfixable], filePath, format }
- **Suggest mode response**: same fix object structure as auto's 'applied' array, just no file write. { suggestions: [...fixes], remaining: [...unfixable] }
- **Already-valid response**: { healed: true, data: <valid data>, applied: [], remaining: [] } — not an error, just nothing to fix
- **Both modes use identical fix objects**: { path, fixType, oldValue, newValue, confidence, message }

### Claude's Discretion
- Fix object field naming and exact TypeScript types
- Internal healing engine architecture (single function vs strategy pattern)
- How to extract Zod default values programmatically
- Test file structure and fixture design
- Error handling for edge cases (empty files, binary content detected, etc.)

</decisions>

<specifics>
## Specific Ideas

- Zod's safeParse already returns structured issues with exact field paths — the healing engine inverts these into corrections
- Each Zod issue type maps to a fix strategy: missing field -> apply default, wrong type -> coerce, unrecognized enum -> manual
- Fix objects use the same path format as Zod issues (array of string/number path segments) for direct correlation
- Consistent with Phase 2's sv_validate pattern: validation failure is expected behavior, not an error response

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/server/tools.ts`: sv_heal stub already registered with correct parameter schema — replace `notImplemented()` with real implementation
- `src/schemas/registry.ts`: SchemaRegistry with `.get()` returning RegisteredSchema including zodSchema
- `src/schemas/types.ts`: RegisteredSchema interface with zodSchema: ZodTypeAny
- `src/security/atomic-write.ts`: atomicWrite() for safe file writes in auto mode
- `src/security/path-validator.ts`: validatePath() already wired into all tools
- `src/formats/registry.ts`: getHandler() for parse/serialize — read malformed file, write healed file

### Established Patterns
- Tool error responses: JSON with {error, message, ...details} + isError: true
- sv_validate uses safeParse (non-throwing) — healing should use the same for error collection
- sv_read/sv_write use parse (throwing) for strict validation
- All file tools validate path, check existence, get format handler, then operate

### Integration Points
- New `src/schemas/healer.ts` (or similar) for healing engine — follows layered src/ pattern
- Healing engine receives RegisteredSchema + raw parsed data, returns fix list
- sv_heal tool handler in tools.ts calls healing engine, conditionally writes with atomicWrite()
- Fix objects reference Zod issue paths for direct correlation with validation errors

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-self-healing*
*Context gathered: 2026-03-08*
