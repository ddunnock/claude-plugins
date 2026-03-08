# Schema Validator MCP

## What This Is

A TypeScript + Zod MCP server that provides schema validation with self-healing capabilities for Claude Code skills. Skills declare their file schemas in a `schemas/` folder, and this MCP handles validated reading, writing, patching, and CRUD operations across JSON, YAML, XML, and TOML formats. Runs locally via stdio, declared in `plugin.json` for any skill that needs it.

## Core Value

Skills get reliable, validated file I/O with automatic error correction — no skill needs to implement its own parsing, validation, or self-healing logic.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Zod-based schema validation for structured files
- [ ] Self-healing: auto-fix mode that corrects malformed files automatically
- [ ] Self-healing: suggestion mode that returns structured errors + fix guidance
- [ ] Full CRUD operations: validate, read, write, patch/update structured files
- [ ] JSON format support
- [ ] YAML format support
- [ ] XML format support
- [ ] TOML format support
- [ ] Per-skill schema definitions (each skill has a `schemas/` folder with Zod definitions)
- [ ] Hybrid schema discovery: convention-based scan of known plugin/skill paths at startup
- [ ] Hybrid schema discovery: explicit registration tool for custom schema paths
- [ ] stdio transport for local Claude Code usage
- [ ] Declared via `plugin.json` for skill integration

### Out of Scope

- SSE/remote transport — local stdio only for v1
- Hardcoded schema knowledge — all schemas are user-defined per skill
- Database or cloud storage — file-based only
- Non-structured files (binary, images, etc.)

## Context

- Lives in `~/projects/claude-plugins/mcps/` monorepo subdirectory
- Existing MCP servers in this workspace (knowledge-mcp) provide reference patterns
- Skills are Claude Code plugin skills that operate on structured config/log/record files
- Schema definitions are TypeScript files using Zod, co-located with each skill in `schemas/` folders
- The MCP is referenced in `plugin.json` so Claude Code loads it automatically for skills that declare it

## Constraints

- **Tech stack**: TypeScript + Zod — must use these specifically
- **Transport**: stdio only — Claude Code local process model
- **Monorepo**: Git tracked at `~/projects/claude-plugins`, not in `mcps/` subdirectory
- **Skills**: Must reference MCP-Builder skill for MCP development, Zod skill for schema work

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Zod for schema definitions | Type-safe, composable, great TypeScript integration, runtime validation | — Pending |
| Hybrid schema discovery | Convention covers 90% of cases, registration handles edge cases | — Pending |
| Dual self-healing modes | Auto-fix for convenience, suggestion mode for skill control | — Pending |
| All 4 formats in v1 | JSON/YAML/XML/TOML covers the full skill file ecosystem | — Pending |
| Per-skill schemas/ folder | Co-locates schema with skill, clear ownership, easy to maintain | — Pending |

---
*Last updated: 2026-03-08 after initialization*
