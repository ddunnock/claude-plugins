# Phase 1: Format Engine & Server - Research

**Researched:** 2026-03-08
**Domain:** MCP server infrastructure, multi-format parsing/serialization, file security
**Confidence:** HIGH

## Summary

Phase 1 builds a TypeScript MCP server that parses and serializes JSON, YAML, XML, and TOML files with path safety and atomic writes. The stack is well-established: `@modelcontextprotocol/sdk` (v1.27.x) provides the server framework with built-in Zod integration for tool definitions, and mature single-purpose libraries handle each format (`js-yaml`, `fast-xml-parser`, `smol-toml`). JSON is native to the runtime.

The server uses bun as both runtime and package manager (decided in CONTEXT.md). All libraries are compatible with bun. The MCP SDK's `McpServer` class with `StdioServerTransport` provides the exact pattern needed -- tool registration with Zod schemas, resource exposure, and stdio transport. The official docs show the exact import paths and patterns.

**Primary recommendation:** Use `McpServer` + `StdioServerTransport` from the MCP SDK, register all tools (working + stubs) at startup, implement format parsers as a registry keyed by file extension, and use temp-file-then-rename for atomic writes.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions
- Location: `mcps/schema-validator/` -- sibling to existing MCP servers
- Internal structure: layered `src/` -- `src/server/`, `src/formats/`, `src/security/`
- Plugin manifest: `schema-validator/.claude-plugin/plugin.json` -- matches existing pattern
- Package manager: **bun** -- fast runtime + package manager with good TypeScript support
- XML use case is **prompt markup** -- elements with text content, minimal attributes, no namespaces
- Register **all planned tools** as stubs in Phase 1 (validate, read, write, patch, register, list, heal)
- Tools that depend on Phase 2 return clear "not implemented" errors
- Phase 1 tools that work: parse_file, detect_format, and any raw format operations
- Expose **MCP resources** alongside tools -- supported formats and registered schemas as resources
- **Structured + detailed** errors: JSON with error code, message, file path, line/column if available, suggested fix
- Path validation errors **include the rejected path**
- Parse errors use **best-effort partial** parsing -- return whatever parsed successfully + list of parse errors
- **Stderr logging** for errors and warnings -- stdout reserved for MCP protocol

### Claude's Discretion
- Exact XML-to-object mapping conventions (guided by prompt markup use case)
- Build tool choice (tsup vs bun build)
- Test file organization within the layered structure
- Specific error code taxonomy

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFR-01 | MCP server runs via stdio transport using @modelcontextprotocol/sdk | MCP SDK McpServer + StdioServerTransport pattern fully documented |
| INFR-02 | MCP is declared in plugin.json for Claude Code integration | Existing plugin.json patterns from knowledge-mcp and session-memory |
| FMT-01 | MCP correctly parses and serializes JSON files | Native JSON.parse/JSON.stringify -- zero dependencies |
| FMT-02 | MCP correctly parses and serializes YAML files | js-yaml load/dump API documented |
| FMT-03 | MCP correctly parses and serializes XML files with attribute handling | fast-xml-parser XMLParser/XMLBuilder with attributeNamePrefix and textNodeName |
| FMT-04 | MCP correctly parses and serializes TOML files | smol-toml parse/stringify API documented |
| FMT-05 | MCP auto-detects file format from extension | Extension-to-parser registry pattern |
| SEC-01 | All file paths validated against traversal attacks | path.resolve + startsWith check pattern |
| SEC-02 | File writes use atomic operations (temp file + rename) | write-file-atomic or manual tmpfile+rename pattern |
| SEC-03 | Schema loading validates file structure before dynamic import | Zod validation of loaded file contents before processing |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| @modelcontextprotocol/sdk | ^1.27 | MCP server framework | Official SDK, built-in Zod integration, stdio transport |
| zod | ^3.25 | Schema validation for tool inputs | Required peer dep of MCP SDK, used for all tool input schemas |
| js-yaml | ^4.1 | YAML parsing and serialization | Most popular YAML lib, 45M+ weekly downloads, YAML 1.2 compliant |
| fast-xml-parser | ^5.3 | XML parsing and building | Fastest pure-JS XML parser, supports round-trip with proper options |
| smol-toml | ^1.6 | TOML parsing and serialization | TOML 1.1.0 compliant, small footprint, TypeScript native |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| write-file-atomic | ^6.0 | Atomic file writes | Every file write operation (SEC-02) |
| @types/js-yaml | ^4.0 | TypeScript types for js-yaml | Dev dependency for type safety |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| smol-toml | @iarna/toml | @iarna/toml is older (TOML 0.5), less maintained; smol-toml is newer, TS-native, TOML 1.1 |
| write-file-atomic | Manual tmpfile+rename | write-file-atomic handles edge cases (permissions, cleanup); manual is simpler but error-prone |
| fast-xml-parser | xml2js | xml2js uses callbacks, slower, less configurable for round-trip |
| bun build | tsup | tsup adds a dependency; bun build is built-in and sufficient for this project |

**Installation:**
```bash
bun add @modelcontextprotocol/sdk zod js-yaml fast-xml-parser smol-toml write-file-atomic
bun add -D @types/js-yaml @types/node typescript
```

## Architecture Patterns

### Recommended Project Structure
```
schema-validator/
├── .claude-plugin/
│   └── plugin.json           # MCP server declaration for Claude Code
├── src/
│   ├── index.ts              # Entry point: create server, connect transport
│   ├── server/
│   │   ├── tools.ts          # Tool registrations (all tools, working + stubs)
│   │   └── resources.ts      # Resource registrations (formats list, etc.)
│   ├── formats/
│   │   ├── registry.ts       # Format registry: extension -> parser/serializer
│   │   ├── json.ts           # JSON format handler
│   │   ├── yaml.ts           # YAML format handler
│   │   ├── xml.ts            # XML format handler
│   │   └── toml.ts           # TOML format handler
│   └── security/
│       ├── path-validator.ts # Path traversal prevention
│       └── atomic-write.ts   # Atomic file write wrapper
├── tests/
│   ├── formats/              # Per-format round-trip tests
│   ├── security/             # Path validation and atomic write tests
│   └── server/               # MCP tool integration tests
├── package.json
└── tsconfig.json
```

### Pattern 1: Format Handler Interface
**What:** Each format implements a common interface for parse/serialize operations.
**When to use:** All format operations go through this interface.
**Example:**
```typescript
// Source: Architecture pattern for this project
interface FormatHandler {
  extensions: string[];
  parse(content: string): unknown;
  serialize(data: unknown): string;
}

// Example: YAML handler
import yaml from "js-yaml";

export const yamlHandler: FormatHandler = {
  extensions: [".yaml", ".yml"],
  parse: (content: string) => yaml.load(content),
  serialize: (data: unknown) => yaml.dump(data),
};
```

### Pattern 2: Format Registry
**What:** A registry mapping file extensions to format handlers, enabling auto-detection.
**When to use:** Every file operation uses the registry to find the right parser.
**Example:**
```typescript
// Source: Architecture pattern for this project
import path from "node:path";

const registry = new Map<string, FormatHandler>();

function register(handler: FormatHandler) {
  for (const ext of handler.extensions) {
    registry.set(ext.toLowerCase(), handler);
  }
}

function getHandler(filePath: string): FormatHandler {
  const ext = path.extname(filePath).toLowerCase();
  const handler = registry.get(ext);
  if (!handler) {
    throw new Error(`Unsupported format: ${ext}`);
  }
  return handler;
}
```

### Pattern 3: MCP Tool Registration with Stubs
**What:** Register all planned tools at startup; Phase 2+ tools return structured "not implemented" errors.
**When to use:** Server initialization.
**Example:**
```typescript
// Source: @modelcontextprotocol/sdk official docs
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "schema-validator",
  version: "0.1.0",
});

// Working tool
server.registerTool("sv_parse_file", {
  description: "Parse a structured data file (JSON, YAML, XML, TOML)",
  inputSchema: {
    filePath: z.string().describe("Path to the file to parse"),
  },
}, async ({ filePath }) => {
  // ... implementation
  return { content: [{ type: "text", text: JSON.stringify(result) }] };
});

// Stub tool (Phase 2)
server.registerTool("sv_validate", {
  description: "Validate a file against a registered schema",
  inputSchema: {
    filePath: z.string(),
    schemaName: z.string(),
  },
}, async () => {
  return {
    content: [{
      type: "text",
      text: JSON.stringify({
        error: "NOT_IMPLEMENTED",
        message: "Schema validation will be available in Phase 2",
      }),
    }],
    isError: true,
  };
});
```

### Anti-Patterns to Avoid
- **console.log() in stdio server:** NEVER use console.log -- it writes to stdout which corrupts the MCP JSON-RPC stream. Use console.error() for all logging.
- **Monolithic tool handler:** Don't put all tool logic in the registration callback. Extract business logic into separate modules (formats/, security/).
- **Synchronous file reads in tool handlers:** Use async fs operations throughout to avoid blocking the event loop.
- **Hardcoded format detection:** Don't use if/else chains for format detection. Use the registry pattern so new formats can be added without modifying detection logic.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML parsing | Custom YAML parser | js-yaml | YAML spec is deceptively complex (anchors, aliases, multi-doc, type coercion) |
| XML parsing | Regex-based XML extraction | fast-xml-parser | XML has entities, CDATA, namespaces, attributes -- even "simple" XML breaks regex |
| TOML parsing | Custom TOML parser | smol-toml | TOML has datetime types, inline tables, multi-line strings |
| Atomic writes | Manual tmp+rename | write-file-atomic | Edge cases: permissions, cleanup on crash, cross-device moves, Windows locking |
| Path validation | Simple string.includes("..") | path.resolve + path comparison | Encoded characters, symlinks, null bytes, Unicode normalization attacks |
| MCP protocol | Custom JSON-RPC over stdio | @modelcontextprotocol/sdk | Protocol versioning, capability negotiation, error formatting |

**Key insight:** Every format parser in this project handles a spec with edge cases that take years to get right. The libraries are battle-tested; hand-rolling any parser is a guaranteed source of bugs.

## Common Pitfalls

### Pitfall 1: stdout Corruption in stdio Servers
**What goes wrong:** Any console.log() call writes to stdout, corrupting the MCP JSON-RPC message stream. The server appears to crash or send malformed responses.
**Why it happens:** Developers default to console.log for debugging. Libraries may also write to stdout.
**How to avoid:** Use console.error() exclusively. Audit all dependencies for stdout writes. Set up a stderr-based logger at project init.
**Warning signs:** "Parse error" messages from the MCP client, server appears to hang.

### Pitfall 2: YAML Type Coercion Surprises
**What goes wrong:** js-yaml's `load()` converts strings like "yes", "no", "on", "off" to booleans, and "1.0" to numbers. This breaks round-trip fidelity.
**Why it happens:** YAML 1.1 spec auto-converts certain strings. js-yaml defaults to the YAML 1.2 core schema which is less aggressive, but still converts obvious numerics.
**How to avoid:** For maximum fidelity, use `yaml.load(content, { schema: yaml.JSON_SCHEMA })` to disable type coercion, or accept the default CORE_SCHEMA behavior and document it.
**Warning signs:** Boolean values appearing where strings were expected, numbers losing string formatting.

### Pitfall 3: XML Attribute/Text Node Confusion
**What goes wrong:** XML attributes and text content get mixed into the same object, making round-trip impossible. Or attributes are silently dropped.
**Why it happens:** Default fast-xml-parser options ignore attributes (`ignoreAttributes: true`).
**How to avoid:** Set `ignoreAttributes: false`, `attributeNamePrefix: "@_"`, `textNodeName: "#text"`. Use the same options for both XMLParser and XMLBuilder.
**Warning signs:** Attributes missing after parse-serialize cycle, text content in wrong position.

### Pitfall 4: Path Traversal via Encoded Characters
**What goes wrong:** Checking for `..` in raw path strings misses URL-encoded (`%2e%2e`) or Unicode variants.
**Why it happens:** Naive string matching instead of path resolution.
**How to avoid:** Use `path.resolve()` to normalize the path, then verify the resolved absolute path starts with the allowed base directory using `resolvedPath.startsWith(allowedBase)`. Also reject null bytes.
**Warning signs:** Security audit failures, files accessed outside intended directory.

### Pitfall 5: TOML Date Handling
**What goes wrong:** TOML has native datetime types (local date, local time, offset datetime). These serialize to custom objects in smol-toml, not plain strings or Date objects.
**Why it happens:** TOML spec requires distinct datetime types that JavaScript doesn't natively support.
**How to avoid:** smol-toml provides `TomlDate` class. When serializing back, ensure TomlDate objects are preserved. For JSON interop, convert to ISO strings explicitly.
**Warning signs:** `[object Object]` in serialized output, type errors on date fields.

### Pitfall 6: Partial Write on Crash
**What goes wrong:** Writing directly to the target file leaves a partial/corrupt file if the process crashes mid-write.
**Why it happens:** `fs.writeFile` is not atomic -- it truncates the file first, then writes.
**How to avoid:** Use write-file-atomic which writes to a temp file then renames atomically.
**Warning signs:** Corrupt files after server crash, zero-byte files.

## Code Examples

Verified patterns from official sources:

### MCP Server Setup (stdio)
```typescript
// Source: https://modelcontextprotocol.io/docs/develop/build-server
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "schema-validator",
  version: "0.1.0",
});

// Register a tool with Zod schema
server.registerTool("sv_parse_file", {
  description: "Parse a structured data file and return its contents",
  inputSchema: {
    filePath: z.string().describe("Absolute path to the file"),
    format: z.enum(["json", "yaml", "xml", "toml"]).optional()
      .describe("Force a specific format (default: auto-detect from extension)"),
  },
}, async ({ filePath, format }) => {
  // Implementation here
  return {
    content: [{ type: "text", text: JSON.stringify(parsed) }],
  };
});

// Register a resource
server.resource("supported-formats", "schema-validator://formats", async () => ({
  contents: [{
    uri: "schema-validator://formats",
    mimeType: "application/json",
    text: JSON.stringify({
      formats: ["json", "yaml", "xml", "toml"],
      extensions: {
        json: [".json"],
        yaml: [".yaml", ".yml"],
        xml: [".xml"],
        toml: [".toml"],
      },
    }),
  }],
}));

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Schema Validator MCP running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
```

### YAML Parse/Serialize
```typescript
// Source: https://github.com/nodeca/js-yaml
import yaml from "js-yaml";

// Parse
const data = yaml.load(fileContent);

// Serialize
const output = yaml.dump(data, {
  lineWidth: -1,    // No line wrapping
  noRefs: true,     // Don't use YAML anchors/aliases
  sortKeys: false,  // Preserve key order
});
```

### XML Parse/Serialize (Prompt Markup Use Case)
```typescript
// Source: https://github.com/NaturalIntelligence/fast-xml-parser
import { XMLParser, XMLBuilder } from "fast-xml-parser";

const parserOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  textNodeName: "#text",
  preserveOrder: false,
  trimValues: false,
  parseTagValue: false,        // Keep values as strings
  parseAttributeValue: false,  // Keep attribute values as strings
  removeNSPrefix: true,        // Strip namespace prefixes (user won't have them)
};

const parser = new XMLParser(parserOptions);
const data = parser.parse(xmlContent);

const builderOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  textNodeName: "#text",
  format: true,
  indentBy: "  ",
};

const builder = new XMLBuilder(builderOptions);
const xmlOutput = builder.build(data);
```

### TOML Parse/Serialize
```typescript
// Source: https://github.com/squirrelchat/smol-toml
import { parse, stringify } from "smol-toml";

// Parse
const data = parse(tomlContent);

// Serialize
const output = stringify(data);
```

### Path Traversal Prevention
```typescript
// Source: Node.js security best practices
import path from "node:path";

function validatePath(filePath: string, allowedDirs: string[]): string {
  // Reject null bytes
  if (filePath.includes("\0")) {
    throw new PathValidationError("ERR_NULL_BYTE", filePath,
      "Path contains null bytes");
  }

  // Resolve to absolute path
  const resolved = path.resolve(filePath);

  // Check against allowed directories
  const isAllowed = allowedDirs.some(dir => {
    const normalizedDir = path.resolve(dir) + path.sep;
    return resolved.startsWith(normalizedDir) || resolved === path.resolve(dir);
  });

  if (!isAllowed) {
    throw new PathValidationError("ERR_PATH_TRAVERSAL", filePath,
      `Path '${filePath}' is outside allowed directories`);
  }

  return resolved;
}
```

### Atomic File Write
```typescript
// Source: https://github.com/npm/write-file-atomic
import writeFileAtomic from "write-file-atomic";

async function atomicWrite(filePath: string, content: string): Promise<void> {
  await writeFileAtomic(filePath, content, { encoding: "utf8" });
}
```

### plugin.json for Claude Code
```json
{
  "name": "schema-validator",
  "description": "Multi-format file parser, validator, and writer with schema enforcement",
  "version": "0.1.0",
  "mcpServers": {
    "schema-validator": {
      "command": "bun",
      "args": ["run", "${CLAUDE_PLUGIN_ROOT}/src/index.ts"],
      "cwd": "${CLAUDE_PLUGIN_ROOT}"
    }
  }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| server.tool() method | server.registerTool() method | MCP SDK ~1.20+ | registerTool supports title, outputSchema, more metadata |
| Zod v3 only | Zod v3.25+ (v4 compat) | 2025 | SDK imports from zod/v4 internally but works with v3.25+ |
| SSE transport | Streamable HTTP transport | March 2025 | SSE deprecated for remote; stdio unchanged for local |
| @iarna/toml | smol-toml | 2024 | smol-toml is actively maintained, TOML 1.1.0, TypeScript native |
| xml2js (callbacks) | fast-xml-parser v5 | 2023-2024 | Faster, no deps, better TypeScript support, configurable round-trip |

**Deprecated/outdated:**
- `server.tool()` still works but `server.registerTool()` is the newer, more complete API
- SSE transport is deprecated for new servers; use stdio (local) or Streamable HTTP (remote)
- `yaml.safeLoad()` was removed in js-yaml v4; use `yaml.load()` which is safe by default

## Open Questions

1. **Zod version compatibility with bun**
   - What we know: MCP SDK requires zod as peer dep. SDK internally uses zod/v4 paths but works with v3.25+.
   - What's unclear: Whether to install zod@3 or zod@4 with bun.
   - Recommendation: Install `zod@3` (as shown in official MCP docs) to avoid any edge cases. Can upgrade later.

2. **Allowed directories for path validation**
   - What we know: SEC-01 requires path traversal prevention.
   - What's unclear: What directories should be allowed? Current working directory? User-configurable list?
   - Recommendation: Default to `process.cwd()` as the allowed base. Make configurable via environment variable or tool parameter. This matches Claude Code's working directory model.

3. **bun build vs tsup for production bundle**
   - What we know: bun can run .ts files directly (no build step needed for dev). bun build can create a single-file bundle.
   - What's unclear: Whether a build step is needed at all since bun runs TS natively.
   - Recommendation: Use `bun run src/index.ts` directly in plugin.json (no build step). Add bun build only if startup performance becomes an issue.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | bun:test (built into bun) |
| Config file | none -- bun:test works out of the box |
| Quick run command | `bun test` |
| Full suite command | `bun test --coverage` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFR-01 | MCP server starts and responds via stdio | integration | `bun test tests/server/startup.test.ts` | Wave 0 |
| INFR-02 | plugin.json is valid and declares server | unit | `bun test tests/server/plugin.test.ts` | Wave 0 |
| FMT-01 | JSON round-trip (parse then serialize) | unit | `bun test tests/formats/json.test.ts` | Wave 0 |
| FMT-02 | YAML round-trip (parse then serialize) | unit | `bun test tests/formats/yaml.test.ts` | Wave 0 |
| FMT-03 | XML round-trip with attributes | unit | `bun test tests/formats/xml.test.ts` | Wave 0 |
| FMT-04 | TOML round-trip (parse then serialize) | unit | `bun test tests/formats/toml.test.ts` | Wave 0 |
| FMT-05 | Auto-detect format from extension | unit | `bun test tests/formats/registry.test.ts` | Wave 0 |
| SEC-01 | Path traversal rejected | unit | `bun test tests/security/path-validator.test.ts` | Wave 0 |
| SEC-02 | Atomic writes (no partial files) | unit | `bun test tests/security/atomic-write.test.ts` | Wave 0 |
| SEC-03 | Schema file structure validated before use | unit | `bun test tests/security/schema-loading.test.ts` | Wave 0 |

### Sampling Rate
- **Per task commit:** `bun test`
- **Per wave merge:** `bun test --coverage`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/formats/json.test.ts` -- round-trip fidelity for JSON
- [ ] `tests/formats/yaml.test.ts` -- round-trip fidelity for YAML, type coercion edge cases
- [ ] `tests/formats/xml.test.ts` -- round-trip with attributes, text content, prompt markup patterns
- [ ] `tests/formats/toml.test.ts` -- round-trip fidelity for TOML, datetime handling
- [ ] `tests/formats/registry.test.ts` -- extension detection, unknown extension error
- [ ] `tests/security/path-validator.test.ts` -- traversal, null bytes, encoded chars
- [ ] `tests/security/atomic-write.test.ts` -- write completes atomically
- [ ] `tests/server/startup.test.ts` -- server starts, tools listed
- [ ] `tests/server/plugin.test.ts` -- plugin.json structure valid
- [ ] Framework install: `bun add -D @types/node` -- bun:test is built-in

## Sources

### Primary (HIGH confidence)
- [@modelcontextprotocol/sdk npm](https://www.npmjs.com/package/@modelcontextprotocol/sdk) - v1.27.1, API patterns, Zod integration
- [MCP Build Server docs](https://modelcontextprotocol.io/docs/develop/build-server) - Official TypeScript server tutorial with McpServer, registerTool, StdioServerTransport
- [fast-xml-parser GitHub](https://github.com/NaturalIntelligence/fast-xml-parser) - XMLParser/XMLBuilder options for round-trip
- [smol-toml GitHub](https://github.com/squirrelchat/smol-toml) - v1.6, parse/stringify API
- [js-yaml GitHub](https://github.com/nodeca/js-yaml) - v4.1, load/dump API
- [write-file-atomic GitHub](https://github.com/npm/write-file-atomic) - Atomic write implementation

### Secondary (MEDIUM confidence)
- [MCP TypeScript SDK GitHub](https://github.com/modelcontextprotocol/typescript-sdk) - registerTool vs tool API, Zod v4 compatibility
- [Building MCP Servers with Bun](https://dev.to/gorosun/building-high-performance-mcp-servers-with-bun-a-complete-guide-32nj) - Bun + MCP SDK compatibility confirmed

### Tertiary (LOW confidence)
- Zod v3 vs v4 with MCP SDK -- the exact compatibility matrix may shift; pin to zod@3 for safety

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries are well-documented, actively maintained, widely used
- Architecture: HIGH - layered structure follows established MCP server patterns and user decisions
- Pitfalls: HIGH - stdout corruption and YAML coercion are well-documented; XML round-trip options verified in docs
- Validation: HIGH - bun:test is built-in, test structure maps cleanly to requirements

**Research date:** 2026-03-08
**Valid until:** 2026-04-08 (stable libraries, MCP SDK may release v2 in Q1 2026)
