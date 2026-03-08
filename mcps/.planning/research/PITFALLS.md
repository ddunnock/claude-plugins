# Pitfalls Research: Schema Validator MCP

## Critical Pitfalls

### 1. XML Impedance Mismatch
**Problem:** XML has attributes, mixed content, namespaces, and ordering — none of which map cleanly to Zod's object-oriented schemas. Naive XML→object conversion loses information.

**Warning signs:** Tests pass for simple XML but fail for real-world files with attributes or namespaces.

**Prevention:**
- Define clear XML-to-object mapping conventions (e.g., `@attributes` key, `#text` for text content)
- Document how Zod schemas should model XML-specific features
- Test with real skill XML files early, not toy examples

**Phase:** Format Layer (Phase 1)

### 2. Self-Healing That Destroys Data
**Problem:** Auto-fix that strips unknown fields or coerces types can silently destroy important data the schema doesn't know about.

**Warning signs:** Files work after healing but have lost fields that other tools depend on.

**Prevention:**
- Default to `passthrough()` not `strict()` for unknown fields
- Self-healing should be additive (add defaults, fix types) not destructive (strip unknowns)
- Always return a diff of what changed
- Require explicit opt-in for destructive operations

**Phase:** Self-Healing implementation

### 3. Schema Loading Security
**Problem:** Loading Zod schemas means executing arbitrary TypeScript. A malicious schema file could execute code at startup.

**Warning signs:** Convention scanner loads code from untrusted paths.

**Prevention:**
- Only load schemas from explicitly configured directories
- Consider declarative schema format (JSON/YAML → Zod) instead of raw .ts files for untrusted sources
- Validate schema file structure before dynamic import
- Document trust model clearly

**Phase:** Schema Registry / Convention Discovery

### 4. Format-Preserving Round-Trip Failures
**Problem:** Parse→modify→serialize loses comments, ordering, and formatting. Users expect their YAML comments to survive a write operation.

**Warning signs:** Users report that validated writes destroy their carefully formatted files.

**Prevention:**
- For v1, document that writes may not preserve comments
- Use `yaml` library's comment preservation features where possible
- TOML and JSON don't support comments, so this is mainly a YAML/XML concern
- Consider a "format-preserving" mode as a v2 feature

**Phase:** Format Layer

### 5. Zod Schema Versioning
**Problem:** Skills evolve their schemas. Old files validated against new schemas fail. No migration path.

**Warning signs:** After schema update, existing valid files start failing validation.

**Prevention:**
- Support schema versioning in registry (name@version)
- Self-healing can bridge version gaps (add new required fields with defaults)
- Document backward compatibility expectations

**Phase:** Schema Registry (v2 consideration, design for it in v1)

### 6. stdio Buffer Overflow with Large Files
**Problem:** MCP stdio transport has message size limits. Reading/writing very large files (multi-MB configs) may hit buffer limits.

**Warning signs:** Operations silently fail or hang on large files.

**Prevention:**
- Set reasonable file size limits (e.g., 10MB)
- Return clear errors for oversized files
- Consider streaming for large files in v2

**Phase:** File I/O Layer

### 7. Concurrent File Access
**Problem:** Multiple skills calling the MCP simultaneously could race on the same file.

**Warning signs:** Intermittent validation failures or corrupted writes.

**Prevention:**
- Use atomic writes (write to temp, rename)
- Consider file locking for write operations
- Document concurrency model

**Phase:** File I/O Layer

## Medium-Risk Pitfalls

### 8. TOML Type Strictness
TOML has strong opinions about types (dates, integers vs floats). Zod coercion may not align with TOML's type system.

**Prevention:** Test TOML-specific types (datetime, inline tables) early.

### 9. Path Traversal in File Operations
MCP receives file paths from clients. Without validation, a malicious path could read/write outside intended directories.

**Prevention:** Validate paths are within allowed directories. No `../` traversal.

### 10. Error Message Quality
Zod errors reference JavaScript paths (`data.items[0].name`). Users need these mapped to file-format-specific paths (YAML line numbers, XML XPath).

**Prevention:** Build error mapping layer that translates Zod paths to format-specific locations.
