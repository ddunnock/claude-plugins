---
phase: 02-schema-registry-file-operations
plan: 01
subsystem: schema-registry
tags: [zod, json-schema, schema-registry, merge-patch, discovery, mcp-tools]

# Dependency graph
requires:
  - phase: 01-core-acquisition
    provides: "Format handlers, security layer, MCP server scaffold with tool stubs"
provides:
  - "SchemaRegistry class with register/get/list/discover/registerFromJsonSchema"
  - "JSON Schema to Zod runtime converter (eval-free)"
  - "RFC 7386 JSON Merge Patch utility"
  - "Schema discovery from skill paths"
  - "Working sv_register_schema and sv_list_schemas MCP tools"
  - "Live registered-schemas MCP resource"
affects: [02-02-file-operations, 03-self-healing]

# Tech tracking
tech-stack:
  added: [zod-from-json-schema]
  patterns: [registry-pattern, namespace-convention, json-schema-wire-format]

key-files:
  created:
    - schema-validator/src/schemas/types.ts
    - schema-validator/src/schemas/registry.ts
    - schema-validator/src/schemas/json-schema-converter.ts
    - schema-validator/src/schemas/merge-patch.ts
    - schema-validator/src/schemas/discovery.ts
    - schema-validator/tests/schemas/registry.test.ts
    - schema-validator/tests/schemas/discovery.test.ts
    - schema-validator/tests/schemas/merge-patch.test.ts
  modified:
    - schema-validator/src/server/tools.ts
    - schema-validator/src/server/resources.ts
    - schema-validator/src/index.ts
    - schema-validator/package.json
    - schema-validator/tests/server/startup.test.ts
    - schema-validator/tests/security/tools-security.test.ts

key-decisions:
  - "Used zod-from-json-schema for eval-free JSON Schema to Zod conversion at runtime"
  - "Schema names use skillDirName/exportName namespace convention"
  - "Config loaded from schema-validator.config.json at project root, graceful fallback to empty skillPaths"

patterns-established:
  - "Registry pattern: Map-backed immutable store with register/get/list interface"
  - "Schema composition via extends field merging parent ZodObject with child"
  - "Discovery: scan schemas/*.ts, dynamic import, filter ZodType exports"

requirements-completed: [SCHM-01, SCHM-02, SCHM-03, SCHM-04]

# Metrics
duration: 5min
completed: 2026-03-08
---

# Phase 2 Plan 1: Schema Registry Summary

**In-memory schema registry with JSON Schema wire format, Zod conversion, RFC 7386 merge-patch, skill-path discovery, and wired sv_register_schema/sv_list_schemas MCP tools**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-08T20:14:04Z
- **Completed:** 2026-03-08T20:18:35Z
- **Tasks:** 2
- **Files modified:** 14

## Accomplishments
- SchemaRegistry stores, retrieves, lists, and composes Zod schemas with immutability enforcement
- JSON Schema objects convert to Zod at runtime via zod-from-json-schema (no eval)
- RFC 7386 JSON Merge Patch handles all spec cases (null deletes, deep merge, array replace)
- Schema discovery scans skill paths, dynamic-imports .ts files, registers Zod exports with namespace
- sv_register_schema and sv_list_schemas are fully functional MCP tools replacing NOT_IMPLEMENTED stubs
- registered-schemas resource returns live registry data

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): Schema registry tests** - `f72fe4d` (test)
2. **Task 1 (GREEN): Schema registry core, converter, merge-patch, discovery** - `8fcf188` (feat)
3. **Task 2: Wire registry into MCP tools, resources, and startup** - `88ce7c9` (feat)

## Files Created/Modified
- `src/schemas/types.ts` - RegisteredSchema, SchemaRegistryConfig, SchemaRegistryError types
- `src/schemas/registry.ts` - SchemaRegistry class with register/get/list/discover/registerFromJsonSchema
- `src/schemas/json-schema-converter.ts` - jsonSchemaToZod using zod-from-json-schema
- `src/schemas/merge-patch.ts` - RFC 7386 JSON Merge Patch implementation
- `src/schemas/discovery.ts` - discoverSchemas scanning skill paths for Zod exports
- `src/server/tools.ts` - sv_register_schema and sv_list_schemas wired to registry
- `src/server/resources.ts` - registered-schemas resource wired to live registry
- `src/index.ts` - SchemaRegistry creation, config loading, discovery at startup, version 0.2.0
- `tests/schemas/registry.test.ts` - Registry tests (register, get, list, duplicate, extends, JSON Schema)
- `tests/schemas/discovery.test.ts` - Discovery tests (scan, skip invalid, namespace)
- `tests/schemas/merge-patch.test.ts` - Merge-patch tests (all RFC 7386 cases)

## Decisions Made
- Used `zod-from-json-schema` library for eval-free JSON Schema to Zod conversion (works with Zod 3.x despite importing from zod/v4 internally)
- Schema names follow `skillDirName/exportName` namespace convention for discovery, `name` for manual registration
- Config loaded from `schema-validator.config.json` at project root; gracefully handles missing config with empty skillPaths

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed TypeScript type mismatch in json-schema-converter**
- **Found during:** Task 2 (TypeScript verification)
- **Issue:** `convertJsonSchemaToZod` returns Zod v4 type incompatible with project's Zod v3 ZodTypeAny
- **Fix:** Added double cast `as unknown as ZodTypeAny` to bridge type systems
- **Files modified:** src/schemas/json-schema-converter.ts
- **Verification:** `bunx tsc --noEmit` passes clean
- **Committed in:** 88ce7c9 (Task 2 commit)

**2. [Rule 3 - Blocking] Updated existing test for new registerTools signature**
- **Found during:** Task 2 (TypeScript verification)
- **Issue:** tools-security.test.ts called `registerTools(server)` without registry argument
- **Fix:** Added SchemaRegistry import and passed `new SchemaRegistry()` as second argument
- **Files modified:** tests/security/tools-security.test.ts
- **Verification:** All 93 tests pass
- **Committed in:** 88ce7c9 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes necessary for type safety and test compatibility. No scope creep.

## Issues Encountered
None beyond the auto-fixed items above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Schema registry foundation complete; Plan 02 can implement sv_validate, sv_read, sv_write, sv_patch against registered schemas
- Merge-patch utility ready for sv_patch implementation
- All 93 tests green, no regressions from Phase 1

---
*Phase: 02-schema-registry-file-operations*
*Completed: 2026-03-08*
