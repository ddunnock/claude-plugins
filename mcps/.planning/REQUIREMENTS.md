# Requirements: Schema Validator MCP

**Defined:** 2026-03-08
**Core Value:** Skills get reliable, validated file I/O with automatic error correction — no skill needs to implement its own parsing, validation, or self-healing logic.

## v1 Requirements

### Schema Management

- [ ] **SCHM-01**: Skill can register a Zod schema by name via MCP tool call
- [ ] **SCHM-02**: Skill can list all registered schemas with their names and metadata
- [ ] **SCHM-03**: MCP scans configured plugin/skill paths for schemas/ folders at startup
- [ ] **SCHM-04**: Skill can compose schemas by extending or merging existing registered schemas

### File Operations

- [ ] **FILE-01**: Skill can read a file and receive parsed, validated, typed data back
- [ ] **FILE-02**: Skill can write data to a file after validation against a named schema
- [ ] **FILE-03**: Skill can validate a file against a schema without reading full data (pass/fail + errors)
- [ ] **FILE-04**: Skill can patch/update specific fields in a structured file preserving existing data

### Self-Healing

- [ ] **HEAL-01**: Skill can auto-fix a malformed file (apply defaults, coerce types, add missing required fields)
- [ ] **HEAL-02**: Skill can request fix suggestions for a malformed file without modifying it

### Format Support

- [ ] **FMT-01**: MCP correctly parses and serializes JSON files
- [ ] **FMT-02**: MCP correctly parses and serializes YAML files
- [ ] **FMT-03**: MCP correctly parses and serializes XML files with attribute handling
- [ ] **FMT-04**: MCP correctly parses and serializes TOML files
- [ ] **FMT-05**: MCP auto-detects file format from extension

### Security & Reliability

- [ ] **SEC-01**: All file paths are validated against traversal attacks
- [ ] **SEC-02**: File writes use atomic operations (temp file + rename)
- [ ] **SEC-03**: Schema loading validates file structure before dynamic import

### Infrastructure

- [ ] **INFR-01**: MCP server runs via stdio transport using @modelcontextprotocol/sdk
- [ ] **INFR-02**: MCP is declared in plugin.json for Claude Code integration

## v2 Requirements

### Format Enhancements

- **FMT-06**: Format-preserving writes (maintain comments, ordering in YAML)
- **FMT-07**: Streaming support for large files

### Schema Enhancements

- **SCHM-05**: Schema versioning (name@version)
- **SCHM-06**: Schema migration tools (bridge version gaps)

### Operations

- **FILE-05**: Dry-run mode (validate proposed changes without writing)
- **FILE-06**: Batch operations (validate/read/write multiple files)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Schema generation from files | Inference is unreliable; users define schemas explicitly |
| Database/cloud storage | File-based only, keeps scope manageable |
| Real-time file watching | MCP is request-response, not event-driven |
| GUI/web interface | CLI/MCP tool, no visual component needed |
| Custom validation DSL | Zod IS the validation language |
| SSE/remote transport | Local stdio only for v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SCHM-01 | — | Pending |
| SCHM-02 | — | Pending |
| SCHM-03 | — | Pending |
| SCHM-04 | — | Pending |
| FILE-01 | — | Pending |
| FILE-02 | — | Pending |
| FILE-03 | — | Pending |
| FILE-04 | — | Pending |
| HEAL-01 | — | Pending |
| HEAL-02 | — | Pending |
| FMT-01 | — | Pending |
| FMT-02 | — | Pending |
| FMT-03 | — | Pending |
| FMT-04 | — | Pending |
| FMT-05 | — | Pending |
| SEC-01 | — | Pending |
| SEC-02 | — | Pending |
| SEC-03 | — | Pending |
| INFR-01 | — | Pending |
| INFR-02 | — | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 0
- Unmapped: 20

---
*Requirements defined: 2026-03-08*
*Last updated: 2026-03-08 after initial definition*
