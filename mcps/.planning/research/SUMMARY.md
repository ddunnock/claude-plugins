# Research Summary: Schema Validator MCP

## Stack
- **TypeScript 5.x + Node.js 20+ LTS** with `@modelcontextprotocol/sdk` for MCP server
- **Zod 3.x** for schema validation, `zod-to-json-schema` for exposing schemas
- **Format parsers:** `yaml` (YAML), `fast-xml-parser` (XML), `smol-toml` (TOML), built-in JSON
- **Build:** tsup + tsx, **Test:** vitest

## Table Stakes Features
- Validate file against schema with structured errors
- Read file with validation (parse + validate + return typed data)
- Write file with validation (validate before writing)
- Multi-format support (JSON, YAML, XML, TOML)
- Schema registration (name-based lookup)

## Differentiators
- Self-healing auto-fix (apply defaults, coerce types)
- Self-healing suggestions (structured fix guidance without modifying files)
- Patch/update operations (partial updates preserving existing data)
- Convention-based schema discovery (scan skill schemas/ folders)

## Architecture
Layered design: MCP Server → Tool Handlers → Schema Registry + Validation Engine → Format Layer → File I/O. Build order follows dependency chain bottom-up.

## Critical Watch-Outs
1. **XML impedance mismatch** — Define clear XML→object mapping conventions early
2. **Self-healing data destruction** — Default to additive fixes, never strip unknowns
3. **Schema loading security** — Only load from trusted/configured paths
4. **Path traversal** — Validate all file paths are within allowed directories
5. **Concurrent file access** — Use atomic writes (temp + rename)
