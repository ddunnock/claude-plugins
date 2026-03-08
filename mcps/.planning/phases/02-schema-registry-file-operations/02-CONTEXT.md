# Phase 2: Schema Registry & File Operations - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Skills can register Zod schemas and use them for validated read, write, validate, and patch operations on structured files. This phase implements the schema registry (register, list, discover, compose) and validated file operations (read, write, validate, patch) — replacing the Phase 2+ stubs from Phase 1.

</domain>

<decisions>
## Implementation Decisions

### Schema Discovery
- Config file (`schema-validator.config.json`) lists skill paths to scan at startup
- Convention: each skill has a `schemas/*.ts` folder, each `.ts` file exports a named Zod schema
- File name becomes schema name (e.g. `schemas/plugin-config.ts` → schema name derived from file)
- Schema names are **namespaced by skill**: `skill-name/schema-name` (e.g. `concept-dev/plugin-config`)
- On scan errors (syntax error, invalid Zod): **log warning and skip** — other schemas still load, server starts normally

### Schema Registration API
- `sv_register_schema` accepts **JSON Schema** objects as wire format — converted to Zod internally
- Auto-discovered `.ts` files use native Zod (full power); runtime registration uses JSON Schema (safe, no eval)
- Schema composition via **extend-by-name**: `sv_register_schema` accepts optional `extends` field referencing another schema name
- `sv_list_schemas` returns **metadata only**: name, source (discovered vs registered), field count, extends info
- Schemas are **immutable** once registered — re-registering the same name is an error

### Validation Behavior
- `sv_read` on validation failure: return **isError with structured Zod validation errors** (path, code, message, expected, received) — no data returned
- `sv_validate` is **pass/fail + errors only** — lightweight check, no parsed data returned on success
- Validation errors use **Zod's native issue format**: array of `{path, code, message, expected, received}`
- `sv_write` **creates the file if it doesn't exist** (including parent directories) — natural behavior for skills

### Patch Semantics
- `sv_patch` uses **deep merge** — recursively merge nested objects, arrays replaced wholesale
- Validation happens **after merge** — merge first, then validate complete result against schema
- **Null removes fields** — setting a field to null in the patch deletes it (JSON Merge Patch / RFC 7386 semantics)
- `sv_patch` **returns the full merged result** after writing — callers confirm final state without separate sv_read

### Claude's Discretion
- Config file location and structure details
- Internal Zod registry data structure
- JSON Schema to Zod conversion library choice
- Deep merge implementation (lodash-style vs custom)
- Parent directory creation strategy for sv_write

</decisions>

<specifics>
## Specific Ideas

- JSON Schema as wire format bridges the gap between native Zod in `.ts` files and safe runtime registration — no code eval needed
- Namespaced schema names (`skill/schema`) prevent collisions in multi-skill environments
- Immutable schemas prevent confusing mid-session state changes
- Zod native error format feeds directly into Phase 3 self-healing (errors map to fix suggestions)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/server/tools.ts`: All Phase 2 tool stubs already registered with parameter schemas — replace `notImplemented()` calls with real implementations
- `src/server/resources.ts`: `registered-schemas` resource returns empty array — wire up to registry
- `src/security/schema-loader.ts`: Pre-flight validation (extension, size, binary check) — use before dynamic import
- `src/security/path-validator.ts`: `validatePath()` — already wired into tools, reuse for all file operations
- `src/security/atomic-write.ts`: `atomicWrite()` — use for sv_write and sv_patch file writes
- `src/formats/registry.ts`: `getHandler()` + `getSupportedExtensions()` — parse/serialize for all formats

### Established Patterns
- Tool error responses: JSON with `{error, message, filePath, ...details}` + `isError: true`
- Format detection: `getHandler(filePath)` auto-detects from extension
- Path safety: `validatePath()` called before any file I/O
- Atomic writes: temp file + rename via `atomicWrite()`

### Integration Points
- New `src/schemas/` directory for registry module (follows layered src/ pattern)
- Config file loaded at startup in `src/index.ts` before `registerTools()`
- Schema registry instance passed to tool handlers (dependency injection)
- `registered-schemas` resource wired to live registry data

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-schema-registry-file-operations*
*Context gathered: 2026-03-08*
