# Roadmap: Schema Validator MCP

## Overview

Build a TypeScript + Zod MCP server that gives Claude Code skills validated file I/O with self-healing. Phase 1 stands up the MCP server with multi-format parsing and security foundations. Phase 2 layers on schema registration and validated CRUD operations — the core value. Phase 3 adds self-healing (auto-fix and suggestions), the key differentiator.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Format Engine & Server** - MCP server with multi-format parsing, serialization, and security primitives
- [ ] **Phase 2: Schema Registry & File Operations** - Zod schema management and validated CRUD across all formats
- [ ] **Phase 3: Self-Healing** - Auto-fix and suggestion modes for malformed files

## Phase Details

### Phase 1: Format Engine & Server
**Goal**: A running MCP server that can parse and serialize JSON, YAML, XML, and TOML files with path safety and atomic writes
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-02, FMT-01, FMT-02, FMT-03, FMT-04, FMT-05, SEC-01, SEC-02, SEC-03
**Success Criteria** (what must be TRUE):
  1. MCP server starts via stdio and responds to tool calls from Claude Code
  2. Server correctly round-trips (parse then serialize) JSON, YAML, XML, and TOML files without data loss
  3. Server auto-detects file format from extension and applies the correct parser
  4. File paths containing traversal patterns (../) are rejected with a clear error
  5. File writes land atomically (no partial writes on failure)
**Plans:** 3/3 plans executed

Plans:
- [x] 01-01-PLAN.md — MCP server scaffold, stdio transport, plugin.json, tool stubs, shared types
- [x] 01-02-PLAN.md — Format engine (JSON, YAML, XML, TOML handlers + registry + auto-detection)
- [x] 01-03-PLAN.md — Security layer (path validation, atomic writes, schema load validation)

### Phase 2: Schema Registry & File Operations
**Goal**: Skills can register Zod schemas and use them for validated read, write, validate, and patch operations on structured files
**Depends on**: Phase 1
**Requirements**: SCHM-01, SCHM-02, SCHM-03, SCHM-04, FILE-01, FILE-02, FILE-03, FILE-04
**Success Criteria** (what must be TRUE):
  1. Skill can register a Zod schema by name and retrieve it for validation
  2. MCP discovers schemas from configured skill paths at startup without manual registration
  3. Skill can read a file and receive parsed, schema-validated data back
  4. Skill can write data that passes schema validation, and invalid data is rejected before touching disk
  5. Skill can patch specific fields in a structured file without clobbering unrelated data
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md — Schema registry core (register, list, discover, compose) + JSON Schema converter + merge-patch + startup wiring
- [ ] 02-02-PLAN.md — Validated file operations (sv_read, sv_write, sv_validate, sv_patch tool implementations)

### Phase 3: Self-Healing
**Goal**: Skills can automatically fix or get structured fix guidance for malformed files
**Depends on**: Phase 2
**Requirements**: HEAL-01, HEAL-02
**Success Criteria** (what must be TRUE):
  1. Skill can auto-fix a malformed file (defaults applied, types coerced, missing required fields added) and the result passes schema validation
  2. Skill can request fix suggestions for a malformed file and receive structured guidance without the file being modified
  3. Self-healing never strips unknown fields or destroys existing valid data
**Plans:** 2 plans

Plans:
- [ ] 03-01-PLAN.md — Healing engine core (healData function, HealFix/HealResult types, coercion helpers, unit tests)
- [ ] 03-02-PLAN.md — sv_heal tool wiring (replace stub with real handler, integration tests)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Format Engine & Server | 3/3 | Complete | 2026-03-08 |
| 2. Schema Registry & File Operations | 1/2 | In progress | - |
| 3. Self-Healing | 0/2 | Not started | - |
