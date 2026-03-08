# Features Research: Schema Validator MCP

## Table Stakes
Features users expect from a schema validation service. Without these, the MCP isn't useful.

| Feature | Complexity | Dependencies |
|---------|-----------|--------------|
| **Validate file against schema** — Return pass/fail with structured errors | Low | Zod, format parsers |
| **Read file with validation** — Parse + validate, return typed data | Low | Validate |
| **Write file with validation** — Validate data before writing to disk | Low | Validate |
| **Multi-format parsing** — JSON, YAML, XML, TOML | Medium | Format-specific parsers |
| **Structured error messages** — Path to error, expected vs actual, actionable descriptions | Low | Zod error formatting |
| **Schema registration** — Register schemas by name for reuse across tool calls | Low | In-memory registry |

## Differentiators
Features that set this apart from "just use Zod directly."

| Feature | Complexity | Dependencies |
|---------|-----------|--------------|
| **Self-healing auto-fix** — Automatically correct common issues (missing defaults, wrong types, extra fields) | High | Zod defaults, coercion |
| **Self-healing suggestions** — Return structured fix guidance without modifying files | Medium | Error analysis |
| **Patch/update operations** — Partial updates to structured files preserving existing data | Medium | Deep merge, format awareness |
| **Convention-based schema discovery** — Scan known plugin/skill paths for schemas/ folders | Medium | Filesystem, path conventions |
| **Format-preserving writes** — Maintain comments, ordering, formatting when possible | High | Format-specific handling |
| **Schema composition** — Combine/extend schemas across skills | Medium | Zod .extend, .merge |
| **Dry-run mode** — Validate proposed changes without writing | Low | Validate |

## Anti-Features
Things to deliberately NOT build.

| Anti-Feature | Reason |
|-------------|--------|
| **Schema generation from files** | Inference is unreliable. Users define schemas explicitly. |
| **Database/cloud storage** | File-based only. Keep it simple. |
| **Real-time file watching** | MCP is request-response, not event-driven. Skills call when needed. |
| **Schema migration tools** | Overly complex for v1. Skills handle their own migrations. |
| **GUI/web interface** | This is a CLI/MCP tool. No visual component needed. |
| **Custom validation DSL** | Zod IS the validation language. Don't reinvent it. |

## Feature Dependencies
```
Schema Registration ──► Validate ──► Read (validated)
                                 ──► Write (validated)
                                 ──► Patch/Update
                                 ──► Self-healing (auto-fix)
                                 ──► Self-healing (suggestions)

Convention Discovery ──► Schema Registration

Format Parsers ──► All file operations
```
