# Phase 2: Schema Registry & File Operations - Research

**Researched:** 2026-03-08
**Status:** Complete

## 1. Schema Registry Architecture

### In-Memory Registry Design

The registry is a `Map<string, RegisteredSchema>` keyed by namespaced name (`skill/schema`).

```typescript
interface RegisteredSchema {
  name: string;               // e.g. "concept-dev/plugin-config"
  zodSchema: ZodTypeAny;      // The actual Zod validator
  source: "discovered" | "registered";
  fieldCount: number;         // Top-level field count for metadata
  extends?: string;           // Parent schema name if composed
}
```

**Why Map over object:** O(1) lookup, built-in iteration, no prototype pollution risk.

### JSON Schema → Zod Conversion (SCHM-01 wire format)

**Decision:** Use `json-schema-to-zod` (v2.7.0) for runtime conversion. This is the most mature library for converting JSON Schema objects to Zod schemas at runtime.

**Alternative considered:** Zod v4 has native `z.fromJSONSchema()`, but the project uses `zod: ^3.25` (v3). Upgrading to Zod v4 is a larger change best deferred. The `json-schema-to-zod` library works with Zod 3.x.

**Important:** `json-schema-to-zod` generates JavaScript source code strings, not Zod objects directly. For runtime use, we need `zod-from-json-schema` instead — it creates actual Zod type instances from JSON Schema at runtime without eval.

**Recommendation:** Use `zod-from-json-schema` for runtime JSON Schema → Zod conversion. No eval, returns Zod instances directly.

### Schema Composition (SCHM-04)

Composition via `extends` field: when registering a schema with `extends: "other/schema"`, the implementation:
1. Looks up the parent schema in the registry
2. Merges the new JSON Schema properties with the parent's
3. Converts the combined schema to Zod

For discovered `.ts` schemas, Zod's native `.extend()` / `.merge()` are available directly.

## 2. Schema Discovery (SCHM-03)

### Config File Format

```json
// schema-validator.config.json (project root or configured location)
{
  "skillPaths": [
    "../skills/concept-dev",
    "../skills/system-dev"
  ]
}
```

### Discovery Algorithm

1. At startup, read config file
2. For each skill path, scan `schemas/*.ts` files
3. For each file, run through existing `validateSchemaFile()` (SEC-03 pre-flight)
4. Dynamic import the validated file: `const mod = await import(filePath)`
5. Extract named exports that are Zod schemas (`instanceof z.ZodType`)
6. Register as `skillName/exportName` (namespace from directory name)
7. On error (syntax, invalid export): log warning via `console.error`, skip file, continue

### Pitfalls
- **Dynamic import paths:** Bun requires absolute paths for dynamic imports. Use `path.resolve()`.
- **Circular dependencies:** If schema A extends schema B and vice versa — detect cycles and error.
- **Hot reloading not needed:** Schemas are immutable; discover once at startup.

## 3. File Operations Architecture

### sv_read (FILE-01)

Flow: `validatePath → Bun.file → read → getHandler → parse → zodSchema.parse → return data`

On validation failure: return `isError` with Zod's `ZodError.issues` array (path, code, message, expected, received). No data returned.

### sv_write (FILE-02)

Flow: `validatePath → zodSchema.parse(data) → getHandler → serialize → mkdirp → atomicWrite`

- Creates parent directories if missing (`mkdir -p` equivalent via `Bun.write` or `node:fs/promises.mkdir({recursive: true})`)
- Validates BEFORE serializing — fail fast on bad data
- Uses existing `atomicWrite()` from `src/security/atomic-write.ts`

### sv_validate (FILE-03)

Flow: `validatePath → Bun.file → read → getHandler → parse → zodSchema.safeParse → return pass/fail + errors`

Lightweight: uses `safeParse` (no throw), returns `{valid: boolean, errors?: ZodIssue[]}`. No parsed data on success.

### sv_patch (FILE-04)

Flow: `validatePath → Bun.file → read → parse → deepMerge(existing, patch) → zodSchema.parse(merged) → serialize → atomicWrite → return merged`

### Deep Merge Implementation

**Decision:** Custom implementation (~20 lines) rather than a library dependency.

**Rationale:** The patch semantics are RFC 7386 JSON Merge Patch:
- Recursively merge nested objects
- Arrays replaced wholesale (not concatenated)
- `null` values delete fields
- Non-object values overwrite

This is simple enough that a custom function is clearer than configuring a library to match these specific semantics. Libraries like `deepmerge` default to array concatenation and don't support null-as-delete.

```typescript
function jsonMergePatch(target: unknown, patch: unknown): unknown {
  if (typeof patch !== "object" || patch === null || Array.isArray(patch)) {
    return patch;
  }
  const result = typeof target === "object" && target !== null && !Array.isArray(target)
    ? { ...target } : {};
  for (const [key, value] of Object.entries(patch)) {
    if (value === null) {
      delete (result as Record<string, unknown>)[key];
    } else {
      (result as Record<string, unknown>)[key] = jsonMergePatch(
        (result as Record<string, unknown>)[key], value
      );
    }
  }
  return result;
}
```

## 4. Integration with Existing Code

### Tools.ts Modifications

The `registerTools` function needs the schema registry instance. Change signature:

```typescript
export function registerTools(server: McpServer, registry: SchemaRegistry): void
```

Each Phase 2 tool handler receives `registry` via closure. Replace `notImplemented()` calls with real implementations.

### index.ts Startup Sequence

```typescript
async function main() {
  const config = await loadConfig();          // New: load schema-validator.config.json
  const registry = new SchemaRegistry();       // New: create registry
  await registry.discover(config.skillPaths);  // New: scan skill schemas

  const server = new McpServer({ name: "schema-validator", version: "0.2.0" });
  registerTools(server, registry);             // Modified: pass registry
  registerResources(server, registry);         // Modified: pass registry
  // ... transport setup unchanged
}
```

### Resources.ts Update

The existing `registered-schemas` resource currently returns an empty array. Wire it to `registry.list()` to return live metadata.

## 5. New File Structure

```
src/schemas/
  registry.ts          # SchemaRegistry class (Map, register, get, list, discover)
  discovery.ts         # Scan skill paths, dynamic import, extract Zod exports
  json-schema-converter.ts  # JSON Schema → Zod using zod-from-json-schema
  merge-patch.ts       # RFC 7386 JSON Merge Patch implementation
```

## 6. Dependencies

### New
- `zod-from-json-schema` — Runtime JSON Schema → Zod conversion (no eval)

### Existing (reused)
- `zod` ^3.25 — Schema definitions and validation
- `write-file-atomic` — Atomic file writes (sv_write, sv_patch)
- Format handlers (json, yaml, xml, toml) — Parse/serialize

## 7. Testing Strategy

### Unit Tests
- Registry: register, get, list, duplicate rejection, immutability
- Discovery: scan paths, extract schemas, skip invalid files, namespace generation
- JSON Schema conversion: basic types, nested objects, arrays, enums
- Merge patch: deep merge, null deletion, array replacement, nested merge
- Each tool: happy path, validation failure, file not found, schema not found

### Integration Tests
- Full round-trip: register schema → write file → read file → validate → patch
- Discovery + tool usage: config → discover → sv_list_schemas → sv_read with discovered schema
- Error propagation: Zod errors surface correctly through MCP tool responses

## Validation Architecture

### Requirement Coverage Matrix

| Requirement | Test Category | Key Scenarios |
|-------------|--------------|---------------|
| SCHM-01 | Registry unit | Register by name, duplicate rejection, immutability |
| SCHM-02 | Registry unit | List returns metadata, source tracking |
| SCHM-03 | Discovery integration | Scan paths, namespace, skip invalid, config loading |
| SCHM-04 | Registry unit | Extend by name, circular detection, missing parent |
| FILE-01 | Tool integration | Read + validate, format detection, Zod error format |
| FILE-02 | Tool integration | Write + validate, mkdir -p, atomic write, reject invalid |
| FILE-03 | Tool unit | Pass/fail, error format, no data on success |
| FILE-04 | Tool integration | Merge patch, validate after merge, null deletion, return merged |

### Critical Path Tests
1. Schema registered → sv_write validates → sv_read returns typed data (end-to-end)
2. Discovery scans real skill path → schemas appear in sv_list_schemas
3. sv_patch preserves unmodified fields and validates result

## RESEARCH COMPLETE
