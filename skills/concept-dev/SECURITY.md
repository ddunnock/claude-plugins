# Security Policy — concept-dev

## Data Handling

All user-provided concept descriptions, problem statements, and research data are stored as local JSON and Markdown files within the `.concept-dev/` workspace directory. No data is transmitted to external services except through web research commands (`/concept:research`, crawl4ai integration).

## Network Access

- **crawl4ai** (`web_researcher.py`) — The only component that makes outbound network requests. Crawls user-specified URLs to gather research content. Requires `crawl4ai >= 0.7.4`.
- **WebSearch / WebFetch** — Built-in Claude Code tools used for feasibility probing and source verification. These are platform-provided, not custom network code.
- No other scripts perform network access.

## Content Sanitization

`web_researcher.py` applies `_sanitize_content()` to all crawled content before writing artifacts. The sanitizer detects and redacts 8 categories of prompt injection patterns:

1. **role-switch** — Role markers in crawled text
2. **identity-override** — Identity reassignment attempts
3. **ignore-instructions** — Directive override attempts
4. **override-instructions** — Instruction bypass attempts
5. **prompt-leak** — System prompt reveal requests
6. **hidden-text** — Zero-width Unicode character sequences
7. **tag-injection** — XML/HTML tags targeting LLM delimiters
8. **jailbreak-keyword** — Known jailbreak pattern keywords

Redaction counts are tracked in artifact metadata (`injection_patterns_redacted` field). Redacted content is replaced with `[REDACTED:<category>]` markers.

## External Content Isolation

Crawled web content is wrapped in boundary markers:

```
<!-- BEGIN EXTERNAL CONTENT: [url] -->
[content]
<!-- END EXTERNAL CONTENT: [id] -->
```

All downstream agents (domain-researcher, gap-analyst, skeptic, document-writer) are instructed to treat content within these markers as data only and never follow instructions found within.

## Environment Variables

- `CLAUDE_PLUGIN_ROOT` — Set by the plugin runtime. Points to the skill's installation directory. Used to resolve script and template paths.
- No secrets, API keys, or credentials are required or stored.

## Path Validation

All scripts validate file paths via `utils.validate_path()`:
- Rejects path traversal (`..` components)
- Restricts file extensions to expected types (`.json`, `.md`, `.yaml`)
- Returns the resolved absolute path

## Attack Vectors and Mitigations

| Vector | Mitigation |
|--------|-----------|
| Prompt injection via crawled content | 8-category sanitizer + boundary markers + agent instructions |
| Path traversal in script arguments | `validate_path()` rejects `..` in all file path arguments |
| Symlink attacks on pipx Python | `web_researcher.py` validates pipx Python resolves under expected prefix |
| Dynamic code running | No dynamic code interpretation or user-controlled subprocess commands |
| Data exfiltration | Scripts write only to local `.concept-dev/` directory |
| Supply chain (crawl4ai) | Pinned minimum version in `requirements.txt`; no other runtime dependencies |
