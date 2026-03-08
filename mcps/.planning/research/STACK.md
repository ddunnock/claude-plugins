# Stack Research: Schema Validator MCP

## Recommended Stack

### Core Runtime & Language
- **TypeScript 5.x** — Required by project constraints. Use strict mode.
- **Node.js 20+ LTS** — Matches existing knowledge-mcp patterns in this workspace.
- **Confidence:** High

### MCP Framework
- **@modelcontextprotocol/sdk** (latest) — Official MCP SDK for TypeScript. Provides Server class, stdio transport, tool/resource registration.
- **Confidence:** High — this is the canonical choice.

### Schema Validation
- **Zod 3.x** — Required by project constraints. Runtime validation + TypeScript type inference.
- **zod-to-json-schema** — For exposing schemas as JSON Schema (useful for MCP tool input descriptions).
- **Confidence:** High

### File Format Parsers
| Format | Library | Rationale |
|--------|---------|-----------|
| JSON | Built-in `JSON.parse/stringify` | Native, zero deps |
| YAML | `yaml` (v2.x) | Best TypeScript support, preserves comments, YAML 1.2 compliant |
| XML | `fast-xml-parser` (v4.x) | Fast, configurable, good TS types, handles attributes |
| TOML | `smol-toml` | Small, fast, TOML 1.0 compliant, good TS support |
- **Confidence:** High for JSON/YAML, Medium-High for XML/TOML (alternatives exist but these are best-in-class)

### Build & Dev
- **tsup** or **tsx** — Fast TypeScript compilation. tsup for bundling, tsx for dev.
- **vitest** — Testing framework, fast, good TypeScript support.
- **Confidence:** High

## What NOT to Use
| Library | Reason |
|---------|--------|
| `ajv` (JSON Schema) | Project uses Zod, not JSON Schema. Don't mix validation paradigms. |
| `js-yaml` | Older, less maintained than `yaml` package. |
| `xml2js` | Callback-based, outdated. `fast-xml-parser` is superior. |
| `@iarna/toml` | Less maintained than `smol-toml`. |
| `joi`, `yup` | Zod is the requirement. Don't add competing validators. |
| `express`/`fastify` | MCP uses stdio transport, not HTTP. No web framework needed. |

## Dependencies Summary
```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "latest",
    "zod": "^3.x",
    "zod-to-json-schema": "^3.x",
    "yaml": "^2.x",
    "fast-xml-parser": "^4.x",
    "smol-toml": "^1.x"
  },
  "devDependencies": {
    "typescript": "^5.x",
    "tsup": "^8.x",
    "tsx": "^4.x",
    "vitest": "^2.x",
    "@types/node": "^20.x"
  }
}
```
