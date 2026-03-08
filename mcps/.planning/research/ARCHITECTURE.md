# Architecture Research: Schema Validator MCP

## System Overview

The MCP follows a layered architecture with clear separation between transport, tool handling, schema management, and file I/O.

```
┌─────────────────────────────────────────┐
│           Claude Code (Client)           │
└──────────────────┬──────────────────────┘
                   │ stdio (JSON-RPC)
┌──────────────────▼──────────────────────┐
│           MCP Server Layer               │
│  ┌─────────────────────────────────┐    │
│  │      Tool Handlers (CRUD)       │    │
│  │  validate | read | write | patch│    │
│  │  register | list | heal         │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │      Schema Registry            │    │
│  │  In-memory map of named schemas │    │
│  │  Convention scanner at startup  │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │      Validation Engine          │    │
│  │  Zod validation + error mapping │    │
│  │  Self-healing (fix + suggest)   │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │      Format Layer               │    │
│  │  JSON | YAML | XML | TOML      │    │
│  │  Parse ↔ Serialize (per format) │    │
│  └──────────┬──────────────────────┘    │
│             │                            │
│  ┌──────────▼──────────────────────┐    │
│  │      File I/O Layer             │    │
│  │  Read | Write | Atomic ops     │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## Major Components

### 1. MCP Server Layer
- Registers tools with the MCP SDK
- Handles JSON-RPC messages over stdio
- Routes tool calls to appropriate handlers
- **Boundary:** Only touches MCP protocol concerns

### 2. Tool Handlers
- One handler per MCP tool (validate, read, write, patch, register, list, heal)
- Orchestrates schema lookup → format detection → validation → file I/O
- Returns structured results to MCP layer
- **Boundary:** Business logic orchestration only

### 3. Schema Registry
- In-memory `Map<string, ZodSchema>` keyed by schema name
- Populated at startup via convention scan (skill schemas/ folders)
- Can be extended at runtime via register tool
- **Boundary:** Schema storage and lookup only

### 4. Validation Engine
- Core Zod validation with rich error formatting
- Self-healing: auto-fix mode (apply defaults, coerce types, strip extras)
- Self-healing: suggestion mode (return structured fix instructions)
- **Boundary:** Data validation and transformation only

### 5. Format Layer
- Abstract interface: `parse(raw: string) → object` and `serialize(data: object) → string`
- Concrete implementations for JSON, YAML, XML, TOML
- Format detection from file extension
- **Boundary:** Serialization/deserialization only

### 6. File I/O Layer
- Atomic file reads and writes
- Path validation and security (no path traversal)
- **Boundary:** Filesystem interaction only

## Data Flow

### Read with Validation
```
Client → read_file(path, schema)
  → File I/O: read raw content
  → Format Layer: detect format, parse to object
  → Schema Registry: lookup schema by name
  → Validation Engine: validate object against schema
  → Return: { data, valid, errors? }
```

### Write with Validation
```
Client → write_file(path, schema, data)
  → Schema Registry: lookup schema
  → Validation Engine: validate data
  → Format Layer: serialize to target format
  → File I/O: atomic write
  → Return: { success, path }
```

### Self-Heal
```
Client → heal_file(path, schema, mode: "fix"|"suggest")
  → File I/O: read raw content
  → Format Layer: parse (lenient)
  → Schema Registry: lookup schema
  → Validation Engine: validate, collect errors
  → If mode="fix": apply defaults, coerce, strip → write back
  → If mode="suggest": return structured fix instructions
  → Return: { healed, changes[], original_errors[] }
```

## Suggested Build Order

1. **Format Layer** — Parse/serialize for all 4 formats (independent, testable)
2. **File I/O Layer** — Read/write with atomic operations (independent)
3. **Schema Registry** — In-memory storage, registration (independent)
4. **Validation Engine** — Zod validation + error formatting (depends on registry)
5. **Self-Healing** — Auto-fix + suggestion modes (depends on validation)
6. **Tool Handlers** — Wire everything together as MCP tools (depends on all above)
7. **MCP Server** — Register tools, stdio transport (depends on handlers)
8. **Convention Discovery** — Scan for schemas at startup (depends on registry)
