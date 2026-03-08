# Schema Validator MCP

## What This Is

A TypeScript + Zod MCP server that provides schema-validated file I/O with self-healing for Claude Code skills. Supports JSON, YAML, XML, and TOML formats with 9 tools covering parsing, validated CRUD, schema management, and automatic error correction. Skills declare schemas in `schemas/` folders; the MCP handles everything else.

## Core Value

Skills get reliable, validated file I/O with automatic error correction — no skill needs to implement its own parsing, validation, or self-healing logic.

## Requirements

### Validated

- ✓ Zod-based schema validation for structured files — v1.0
- ✓ Self-healing: auto-fix mode that corrects malformed files automatically — v1.0
- ✓ Self-healing: suggestion mode that returns structured errors + fix guidance — v1.0
- ✓ Full CRUD operations: validate, read, write, patch/update structured files — v1.0
- ✓ JSON, YAML, XML, TOML format support with round-trip fidelity — v1.0
- ✓ Per-skill schema definitions (each skill has a `schemas/` folder with Zod definitions) — v1.0
- ✓ Hybrid schema discovery: convention-based scan at startup + explicit registration tool — v1.0
- ✓ stdio transport for local Claude Code usage — v1.0
- ✓ Declared via `plugin.json` for skill integration — v1.0
- ✓ Path traversal prevention on all file operations — v1.0
- ✓ Atomic file writes (temp file + rename) — v1.0
- ✓ Schema load validation before dynamic import — v1.0

### Active

- [ ] Format-preserving writes (maintain comments, ordering in YAML)
- [ ] Streaming support for large files
- [ ] Schema versioning (name@version)
- [ ] Schema migration tools (bridge version gaps)
- [ ] Dry-run mode (validate proposed changes without writing)
- [ ] Batch operations (validate/read/write multiple files)

### Out of Scope

- SSE/remote transport — local stdio only, matches Claude Code process model
- Database or cloud storage — file-based only, keeps scope manageable
- Non-structured files (binary, images) — structured data formats only
- Custom validation DSL — Zod IS the validation language
- Schema generation from files — inference is unreliable; users define schemas explicitly
- Real-time file watching — MCP is request-response, not event-driven

## Context

Shipped v1.0 with 4,260 LOC TypeScript (2,414 source + 1,846 tests).
Tech stack: Bun runtime, TypeScript, Zod, @modelcontextprotocol/sdk.
Format libs: js-yaml, fast-xml-parser, smol-toml, write-file-atomic.
Lives in `~/projects/claude-plugins/mcps/` monorepo subdirectory.

## Constraints

- **Tech stack**: TypeScript + Zod — must use these specifically
- **Transport**: stdio only — Claude Code local process model
- **Monorepo**: Git tracked at `~/projects/claude-plugins`, not in `mcps/` subdirectory
- **Runtime**: Bun — chosen for TypeScript-first execution

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Zod for schema definitions | Type-safe, composable, great TypeScript integration, runtime validation | ✓ Good — clean API, Zod internals accessible for healing |
| Hybrid schema discovery | Convention covers 90% of cases, registration handles edge cases | ✓ Good — startup scan + sv_register_schema tool |
| Dual self-healing modes | Auto-fix for convenience, suggestion mode for skill control | ✓ Good — clear separation of concerns |
| All 4 formats in v1 | JSON/YAML/XML/TOML covers the full skill file ecosystem | ✓ Good — FormatHandler interface makes adding formats trivial |
| Per-skill schemas/ folder | Co-locates schema with skill, clear ownership, easy to maintain | ✓ Good — namespace convention prevents collisions |
| JSON Schema wire format for registration | MCP tools can't pass Zod objects; JSON Schema is universal | ✓ Good — zod-from-json-schema converts eval-free |
| Conservative coercion in healing | Only string↔number, string↔boolean, number/boolean↔string | ✓ Good — safe, predictable, no data loss |
| Unknown field preservation | Mutate raw data in-place instead of using Zod output | ✓ Good — prevents stripping user data |
| safeParse for sv_validate, parse for CRUD | Validation failure is expected behavior for validate, exceptional for CRUD | ✓ Good — ergonomic distinction |

---
*Last updated: 2026-03-08 after v1.0 milestone*
