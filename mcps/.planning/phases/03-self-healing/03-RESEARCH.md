# Phase 3: Self-Healing - Research

**Researched:** 2026-03-08
**Domain:** Zod schema introspection, type coercion, structured fix generation
**Confidence:** HIGH

## Summary

Phase 3 implements a healing engine that inspects Zod `safeParse` validation errors, maps each error to a fix strategy (apply default, coerce type, or flag as manual), and either applies fixes to the raw data (auto mode) or returns structured suggestions (suggest mode). The existing `sv_heal` tool stub in `tools.ts` already has the correct parameter schema -- it just needs the `notImplemented()` call replaced with a real handler.

The core technical challenge is bridging Zod's validation output (which strips unknown fields) with the requirement to preserve unknown fields. The solution is to apply fixes directly to the raw parsed data object, then re-validate. Zod's `safeParse` returns structured issues with exact field paths, and Zod's `_def` internals expose default values and type information needed to generate fixes.

**Primary recommendation:** Build a single `healData()` function in `src/schemas/healer.ts` that takes raw parsed data + a ZodTypeAny schema, runs safeParse, maps issues to fix objects, applies fixes to the raw data (preserving unknowns), and re-validates. The sv_heal tool handler calls this function and conditionally writes with atomicWrite().

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Conservative coercion only**: safe type coercions (string '5' -> number 5, string 'true' -> boolean true, null -> schema default). No ambiguous coercions (e.g., 'yes' -> boolean)
- **Schema defaults for missing fields**: use Zod `.default()` values when defined. If no default exists for a required field, report as unfixable (never invent data)
- **Single pass**: apply all fixable corrections in one pass, then re-validate. If still invalid, return partial results + remaining errors
- **Partial healing allowed**: write partially-healed file to disk, return both applied fixes and remaining unfixable errors
- **Fix instructions list**: array of structured fix objects with path, issue, currentValue, suggestedValue, fixType, confidence
- **Unfixable errors included**: same list, tagged with fixType: 'manual' and human-readable explanation
- **Two-tier confidence**: 'safe' (schema default applied, exact type coercion) and 'uncertain' (lossy coercion, multiple possible fixes)
- **Already-valid files**: return { valid: true, suggestions: [] }
- **Unknown fields always preserved**: fields not in the schema pass through untouched during healing
- **Healing at raw data layer**: merge fixes into raw parsed data before Zod validation, not from Zod's validated output
- **No backup files**: applied changes list serves as the record
- **Enum mismatches are unfixable**: report as manual with allowed values listed
- **Simple API**: keep existing three params (filePath, schemaName, mode: 'auto' | 'suggest')
- **Auto mode response**: { healed: true, data: <full healed object>, applied: [...fixes], remaining: [...unfixable], filePath, format }
- **Suggest mode response**: { suggestions: [...fixes], remaining: [...unfixable] }
- **Already-valid response**: { healed: true, data: <valid data>, applied: [], remaining: [] }
- **Both modes use identical fix objects**: { path, fixType, oldValue, newValue, confidence, message }

### Claude's Discretion
- Fix object field naming and exact TypeScript types
- Internal healing engine architecture (single function vs strategy pattern)
- How to extract Zod default values programmatically
- Test file structure and fixture design
- Error handling for edge cases (empty files, binary content detected, etc.)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| HEAL-01 | Skill can auto-fix a malformed file (apply defaults, coerce types, add missing required fields) | Zod safeParse issues map directly to fix strategies; _def.defaultValue() extracts defaults; raw data mutation preserves unknowns; atomicWrite for disk persistence |
| HEAL-02 | Skill can request fix suggestions for a malformed file without modifying it | Same healing engine, just skip the atomicWrite step; return identical fix objects in suggestions array |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| zod | ^3.25 | Schema validation + introspection | Already in use; safeParse provides structured issues; _def exposes defaults |
| bun:test | built-in | Test framework | Already established in prior phases |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| write-file-atomic | ^7.0.1 | Atomic file writes | Auto mode file persistence (already imported) |

### No New Dependencies
This phase requires zero new packages. All needed functionality exists in Zod's runtime introspection API and the existing codebase.

## Architecture Patterns

### Recommended Project Structure
```
src/
├── schemas/
│   ├── healer.ts          # NEW: healing engine (healData function + types)
│   ├── registry.ts        # existing: schema lookup
│   └── types.ts           # existing: extend with HealFix type
├── server/
│   └── tools.ts           # MODIFY: replace sv_heal notImplemented() stub
```

### Pattern 1: Issue-to-Fix Mapping
**What:** Map each ZodIssue code to a fix strategy function
**When to use:** Processing safeParse error results

The healing engine processes Zod issues in a single pass:

```typescript
// Zod issue code -> fix strategy mapping
// Source: Verified via bun runtime inspection of Zod 3.25
const ISSUE_STRATEGIES: Record<string, FixStrategy> = {
  invalid_type: handleTypeIssue,      // coerce or apply default
  invalid_enum_value: handleEnumIssue, // always manual (can't guess)
  // All other codes -> manual (too_small, too_big, invalid_string, etc.)
};
```

### Pattern 2: Raw Data Mutation (Preserve Unknowns)
**What:** Apply fixes to the raw parsed data, never use Zod's validated output as the base
**When to use:** Always -- this is a locked decision

```typescript
// CRITICAL: Zod's default safeParse STRIPS unknown fields from output
// Verified: z.object({name: z.string()}).safeParse({name: "x", extra: 1})
//   => {success: true, data: {name: "x"}}  -- "extra" is GONE
//
// Therefore: mutate rawData directly, then re-validate
function applyFixes(rawData: Record<string, unknown>, fixes: HealFix[]): void {
  for (const fix of fixes) {
    setNestedValue(rawData, fix.path, fix.newValue);
  }
}
```

### Pattern 3: Zod Default Extraction via _def
**What:** Walk a ZodObject's shape to find fields wrapped in ZodDefault
**When to use:** When a missing/invalid field needs its schema default

```typescript
// Source: Verified via bun runtime -- Zod 3.25 _def structure
function getDefaultValue(schema: ZodTypeAny): { hasDefault: boolean; value?: unknown } {
  if (schema._def.typeName === 'ZodDefault') {
    return { hasDefault: true, value: schema._def.defaultValue() };
  }
  return { hasDefault: false };
}

// Walk to find the schema for a specific path in a ZodObject
function getSchemaAtPath(rootSchema: ZodTypeAny, path: (string | number)[]): ZodTypeAny | undefined {
  let current = rootSchema;
  for (const segment of path) {
    // Unwrap ZodDefault, ZodOptional, etc. to get inner type
    while (current._def.typeName === 'ZodDefault' || current._def.typeName === 'ZodOptional') {
      current = current._def.innerType;
    }
    if (current._def.typeName === 'ZodObject' && typeof segment === 'string') {
      current = current.shape[segment];
      if (!current) return undefined;
    } else if (current._def.typeName === 'ZodArray' && typeof segment === 'number') {
      current = current._def.type; // array element schema
    } else {
      return undefined;
    }
  }
  return current;
}
```

### Pattern 4: Tool Handler Pattern (Consistent with Phase 2)
**What:** sv_heal follows identical error handling structure as sv_validate/sv_read
**When to use:** Always

```typescript
// sv_heal follows the established pattern:
// 1. validatePath(filePath)
// 2. Check file exists
// 3. Read + parse with format handler
// 4. Get schema from registry
// 5. Call healData(rawData, schema)
// 6. If mode === 'auto' && fixes applied: atomicWrite()
// 7. Return structured response (never isError for valid files or partial heals)
```

### Anti-Patterns to Avoid
- **Using Zod's validated output as healed data:** Strips unknown fields. Always mutate rawData.
- **Deep cloning before mutation:** Unnecessary overhead. The raw data object is already a fresh parse result.
- **Multiple validation passes:** Run safeParse once, generate all fixes, apply all, re-validate once. Not a loop.
- **Throwing on partial heal:** Partial healing is expected. Return applied + remaining, let the caller decide.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structured validation errors | Custom validator | `zodSchema.safeParse()` | Returns typed ZodIssue[] with path, code, expected, received |
| Default value discovery | Manual schema parsing | `schema._def.typeName === 'ZodDefault'` + `._def.defaultValue()` | Zod's own internal API, stable across 3.x |
| Atomic file writes | fs.writeFile + rename | `atomicWrite()` from existing security module | Already battle-tested in Phase 2 |
| Path validation | Custom path checks | `validatePath()` from existing security module | Already handles traversal attacks |
| JSON merge patch | Custom deep merge | Existing `jsonMergePatch()` | RFC 7386 compliant, already tested |

**Key insight:** The healing engine is essentially a mapper from ZodIssue[] to HealFix[], plus a simple applicator. No new dependencies needed.

## Common Pitfalls

### Pitfall 1: Zod Strips Unknown Fields
**What goes wrong:** Using Zod's validated output as the "healed" data loses any fields not in the schema
**Why it happens:** Zod's default object parsing mode is "strip" -- it silently removes unrecognized keys
**How to avoid:** Apply fixes directly to the raw parsed data object. Never use Zod's output as the base object.
**Warning signs:** Test with data containing extra fields and verify they survive healing

### Pitfall 2: Default Values Are Functions
**What goes wrong:** Storing `schema._def.defaultValue` instead of calling it
**Why it happens:** Zod stores defaults as thunks (functions that return the value), not plain values
**How to avoid:** Always call `schema._def.defaultValue()` with parentheses
**Warning signs:** Fix objects containing `[Function]` instead of actual values

### Pitfall 3: Nested Path Resolution
**What goes wrong:** Setting `rawData["config.timeout"] = 30` instead of `rawData.config.timeout = 30`
**Why it happens:** Zod issue paths are arrays like `["config", "timeout"]`, but naive fixes might join them
**How to avoid:** Implement proper nested value setter that walks the path segments, creating intermediate objects as needed
**Warning signs:** Tests with nested schemas failing silently

### Pitfall 4: Type Coercion Ambiguity
**What goes wrong:** Coercing "yes"/"no" to boolean, "null" to null, etc.
**Why it happens:** Overly aggressive coercion logic
**How to avoid:** Only coerce: string numeric -> number (via Number(), reject NaN), string "true"/"false" -> boolean (exact match, case-sensitive), null/undefined -> schema default. Everything else is manual.
**Warning signs:** Context decision explicitly says "no ambiguous coercions"

### Pitfall 5: Missing Required Field Without Default
**What goes wrong:** Inventing a value (empty string, 0, false) for a required field with no schema default
**Why it happens:** Trying to make every fix automatic
**How to avoid:** If no ZodDefault wrapper exists, the fix is `fixType: 'manual'`. Never invent data.
**Warning signs:** Healed files containing placeholder values not from the schema

### Pitfall 6: Already-Valid File Handling
**What goes wrong:** Running healing logic on a valid file and accidentally mutating it
**Why it happens:** Not checking safeParse success before entering fix logic
**How to avoid:** Check `safeParse(rawData).success` first. If true, short-circuit with `{ healed: true, data: rawData, applied: [], remaining: [] }`
**Warning signs:** Valid files being rewritten with stripped unknown fields

## Code Examples

### Verified: Zod SafeParse Issue Structure
```typescript
// Source: Verified via bun runtime with Zod 3.25
// safeParse returns structured issues with these fields:
interface ZodIssue {
  code: string;           // "invalid_type", "invalid_enum_value", etc.
  path: (string|number)[]; // ["config", "timeout"] for nested fields
  message: string;        // Human-readable error
  expected?: string;      // For invalid_type: "number", "boolean", etc.
  received?: string;      // For invalid_type: "string", "undefined", etc.
  options?: string[];     // For invalid_enum_value: allowed enum values
}

// Example issue for wrong type:
// { code: "invalid_type", expected: "number", received: "string",
//   path: ["version"], message: "Expected number, received string" }

// Example issue for missing required:
// { code: "invalid_type", expected: "string", received: "undefined",
//   path: ["name"], message: "Required" }

// Example issue for bad enum:
// { code: "invalid_enum_value", received: "extreme",
//   options: ["low","medium","high"], path: ["level"],
//   message: "Invalid enum value..." }
```

### Verified: Zod Default Value Extraction
```typescript
// Source: Verified via bun runtime with Zod 3.25
import { z, type ZodTypeAny } from "zod";

const schema = z.object({
  version: z.number().default(1),
  enabled: z.boolean().default(true),
  level: z.enum(["low","medium","high"]).default("medium"),
});

// Walking the shape:
// schema.shape.version._def.typeName === "ZodDefault"
// schema.shape.version._def.defaultValue() === 1
// schema.shape.version._def.innerType._def.typeName === "ZodNumber"
```

### Safe Type Coercion Functions
```typescript
// Conservative coercion per CONTEXT.md decisions
function coerceToNumber(value: unknown): { success: boolean; result?: number } {
  if (typeof value === 'string') {
    const num = Number(value);
    if (!Number.isNaN(num) && value.trim() !== '') {
      return { success: true, result: num };
    }
  }
  return { success: false };
}

function coerceToBoolean(value: unknown): { success: boolean; result?: boolean } {
  if (value === 'true') return { success: true, result: true };
  if (value === 'false') return { success: true, result: false };
  // "yes", "no", "1", "0" are NOT coerced (ambiguous per decision)
  return { success: false };
}

function coerceToString(value: unknown): { success: boolean; result?: string } {
  if (typeof value === 'number' || typeof value === 'boolean') {
    return { success: true, result: String(value) };
  }
  return { success: false };
}
```

### Nested Value Setter
```typescript
// Set a value at a nested path in an object, creating intermediates
function setNestedValue(obj: Record<string, unknown>, path: (string|number)[], value: unknown): void {
  let current: any = obj;
  for (let i = 0; i < path.length - 1; i++) {
    const segment = path[i];
    if (current[segment] === undefined || current[segment] === null) {
      // Create intermediate: object if next segment is string, array if number
      current[segment] = typeof path[i + 1] === 'number' ? [] : {};
    }
    current = current[segment];
  }
  current[path[path.length - 1]] = value;
}

// Get a value at a nested path
function getNestedValue(obj: Record<string, unknown>, path: (string|number)[]): unknown {
  let current: any = obj;
  for (const segment of path) {
    if (current === undefined || current === null) return undefined;
    current = current[segment];
  }
  return current;
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Zod coerce API (z.coerce.number()) | Manual coercion at data layer | N/A | Zod coerce transforms at parse time, can't preserve unknowns |
| Zod .passthrough() to keep unknowns | Raw data mutation | N/A | passthrough still runs transforms that could alter values |

**Why not use Zod's built-in coercion:**
- `z.coerce.number()` would auto-coerce at parse time, but this changes the schema definition itself
- We need to coerce selectively (only when there's a type mismatch), not universally
- Using coerce schemas would mean modifying the registered schema, which breaks the single-source-of-truth principle

## Open Questions

1. **Nested object missing entirely vs. individual fields missing**
   - What we know: Zod reports `{code: "invalid_type", expected: "object", received: "undefined", path: ["config"]}` when an entire nested object is missing
   - What's unclear: Should we create the nested object with all defaults, or report as manual?
   - Recommendation: If the nested object schema has ALL required fields with defaults, create it with defaults. Otherwise report as manual. This follows the "never invent data" principle.

2. **Array element validation issues**
   - What we know: Zod paths include numeric indices for array elements, e.g., `["tags", 0]`
   - What's unclear: Should we attempt to fix individual array elements?
   - Recommendation: Array element type coercion is reasonable (e.g., string "5" in a number array). Removing invalid elements would destroy data, so flag as manual instead.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bun:test (built-in) |
| Config file | none (bun defaults) |
| Quick run command | `bun test tests/schemas/healer.test.ts` |
| Full suite command | `bun test` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HEAL-01 | Auto-fix applies defaults for missing fields | unit | `bun test tests/schemas/healer.test.ts -t "apply defaults"` | No - Wave 0 |
| HEAL-01 | Auto-fix coerces string to number | unit | `bun test tests/schemas/healer.test.ts -t "coerce"` | No - Wave 0 |
| HEAL-01 | Auto-fix writes healed file to disk | integration | `bun test tests/server/tools-phase3.test.ts -t "auto mode"` | No - Wave 0 |
| HEAL-01 | Healed file passes schema validation | unit | `bun test tests/schemas/healer.test.ts -t "re-validate"` | No - Wave 0 |
| HEAL-01 | Unknown fields preserved after healing | unit | `bun test tests/schemas/healer.test.ts -t "unknown fields"` | No - Wave 0 |
| HEAL-01 | Partial heal with remaining errors | unit | `bun test tests/schemas/healer.test.ts -t "partial"` | No - Wave 0 |
| HEAL-02 | Suggest mode returns fixes without file write | integration | `bun test tests/server/tools-phase3.test.ts -t "suggest mode"` | No - Wave 0 |
| HEAL-02 | Suggest mode fix objects match auto mode format | unit | `bun test tests/schemas/healer.test.ts -t "fix object"` | No - Wave 0 |
| HEAL-02 | Already-valid file returns empty suggestions | integration | `bun test tests/server/tools-phase3.test.ts -t "already valid"` | No - Wave 0 |

### Sampling Rate
- **Per task commit:** `bun test tests/schemas/healer.test.ts`
- **Per wave merge:** `bun test`
- **Phase gate:** Full suite green before verification

### Wave 0 Gaps
- [ ] `tests/schemas/healer.test.ts` -- unit tests for healing engine (covers HEAL-01, HEAL-02 core logic)
- [ ] `tests/server/tools-phase3.test.ts` -- integration tests for sv_heal tool (covers HEAL-01, HEAL-02 end-to-end)
- [ ] Test fixtures: malformed data objects with various Zod issue types

## Sources

### Primary (HIGH confidence)
- Zod 3.25 runtime API -- verified via `bun -e` with actual installed package:
  - `safeParse()` returns `{success, data, error}` with `error.issues[]`
  - `ZodIssueCode` enum: invalid_type, invalid_enum_value, invalid_literal, unrecognized_keys, too_small, too_big, invalid_string, custom, and more
  - `_def.typeName === 'ZodDefault'` identifies default-wrapped fields
  - `_def.defaultValue()` is a thunk (function) that returns the default value
  - `_def.innerType` accesses the unwrapped inner schema
  - Default safeParse strips unknown fields from validated output (confirmed)
- Existing codebase (tools.ts, registry.ts, types.ts, atomic-write.ts) -- read directly

### Secondary (MEDIUM confidence)
- Zod _def internals are stable across 3.x but not documented as public API. They work reliably and are widely used in the ecosystem for schema introspection.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- zero new dependencies, all existing
- Architecture: HIGH -- follows established patterns from Phase 1/2, Zod APIs verified at runtime
- Pitfalls: HIGH -- all verified through runtime experiments with actual Zod version
- Zod _def API stability: MEDIUM -- undocumented internal, but stable across 3.x and widely relied upon

**Research date:** 2026-03-08
**Valid until:** 2026-04-08 (Zod 3.x stable, no breaking changes expected)
