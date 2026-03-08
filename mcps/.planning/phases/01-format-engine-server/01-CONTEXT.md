# Phase 1: Format Engine & Server - Context

**Gathered:** 2026-03-08
**Status:** Ready for planning

<domain>
## Phase Boundary

A running MCP server that can parse and serialize JSON, YAML, XML, and TOML files with path safety and atomic writes. All planned tool stubs are registered (returning "not implemented" for Phase 2+ features). Server runs via stdio, declared in plugin.json.

</domain>

<decisions>
## Implementation Decisions

### Project scaffold
- Location: `mcps/schema-validator/` — sibling to existing MCP servers
- Internal structure: layered `src/` — `src/server/`, `src/formats/`, `src/security/`
- Plugin manifest: `schema-validator/.claude-plugin/plugin.json` — matches existing pattern
- Package manager: **bun** — fast runtime + package manager with good TypeScript support
- First TypeScript MCP in this workspace (existing servers are all Python)

### XML object mapping
- XML use case is **prompt markup** — elements with text content, minimal attributes, no namespaces
- Not traditional config/data XML — simpler subset to support
- Claude's Discretion: attribute representation convention (recommend @_ prefix or $ grouping)
- Claude's Discretion: text content handling (#text key or similar)
- Claude's Discretion: namespace handling (strip prefixes — user's XML won't have them)

### Tool surface design
- Register **all planned tools** as stubs in Phase 1 (validate, read, write, patch, register, list, heal)
- Tools that depend on Phase 2 (schema registry) return clear "not implemented" errors
- Phase 1 tools that work: parse_file, detect_format, and any raw format operations
- Expose **MCP resources** alongside tools — supported formats and registered schemas as resources
- This gives callers a complete picture of the server's capabilities from day one

### Error responses
- **Structured + detailed** errors: JSON with error code, message, file path, line/column if available, suggested fix
- Path validation errors **include the rejected path** — helpful for debugging ("Path '/etc/passwd' is outside allowed directories")
- Parse errors use **best-effort partial** parsing — return whatever parsed successfully + list of parse errors
- **Stderr logging** for errors and warnings — stdout reserved for MCP protocol (critical pitfall from research)

### Claude's Discretion
- Exact XML-to-object mapping conventions (guided by prompt markup use case)
- Build tool choice (tsup vs bun build)
- Test file organization within the layered structure
- Specific error code taxonomy

</decisions>

<specifics>
## Specific Ideas

- "I use XML markup for making AI prompts be less ambiguous" — XML support should optimize for prompt-style markup (elements + text content, minimal attributes, no namespaces) rather than enterprise XML
- Follow `.claude-plugin/plugin.json` pattern from existing MCPs (knowledge-mcp, session-memory)
- Use bun as both runtime and package manager

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `knowledge-mcp/.claude-plugin/plugin.json`: Reference for plugin manifest structure
- `session-memory/.claude-plugin/plugin.json`: Additional plugin manifest reference
- `knowledge-mcp/src/knowledge_mcp/server.py`: MCP server pattern (Python, but tool registration and dispatch pattern translates)

### Established Patterns
- MCP tool naming: `snake_case` with domain prefix (e.g., `session_init`, `knowledge_search`)
- MCP error responses: JSON with error/message/retryable fields (from knowledge-mcp conventions)
- Abstract base classes in `base.py` for extensibility (format parsers should follow this)
- Factory pattern for creating implementations based on config

### Integration Points
- Plugin manifest in `.claude-plugin/plugin.json` for Claude Code to discover the server
- stdio transport — same as all existing MCP servers in this workspace
- Schema files will live in external skill directories (discovered via convention scan in Phase 2)

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-format-engine-server*
*Context gathered: 2026-03-08*
