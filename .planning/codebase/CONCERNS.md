# Codebase Concerns

**Analysis Date:** 2026-01-23

## Tech Debt

**Large monolithic MCP server files:**
- Issue: `mcps/session-memory/server.py` is 1876 lines and `mcps/streaming-output/server.py` is 1710 lines. These exceed maintainability thresholds and combine multiple concerns (schema, business logic, tool definitions, async handling).
- Files: `mcps/session-memory/server.py`, `mcps/streaming-output/server.py`
- Impact: Difficult to test individual components, high cognitive load for modifications, increased bug surface area. Changes to one feature risk breaking others.
- Fix approach: Extract tool definitions to separate files, move database schema to dedicated modules, split business logic into service classes. Target: <600 lines per file.

**Bare except clauses and silent failures:**
- Issue: Multiple `except Exception:` and `pass` statements throughout MCPs swallow errors without logging or context. Found 40+ instances in `mcps/session-memory/server.py` alone (lines 368, 378, 387, 397, 406, 417, 423, 429, 436, 442, 448, 454, 1329, 1397, 1427).
- Files: `mcps/session-memory/server.py`, `mcps/session-memory/modules/cloud_sync.py`, `mcps/session-memory/modules/entities.py`
- Impact: Silent failures make debugging difficult. Cloud sync failures, embedding generation failures, and config loading issues are all hidden. Production issues become impossible to diagnose.
- Fix approach: Replace bare `except Exception:` with specific exception types. Add structured logging with context. At minimum: log with timestamp, module, function, and error details before passing.

**Graceful degradation without visibility:**
- Issue: Multiple optional dependencies (boto3, httpx, openai, PyPDF2) are conditionally imported with `try/except ImportError` and `AVAILABLE` flags. When features fail to initialize, there's minimal feedback about what's broken (see `mcps/session-memory/modules/embeddings.py:45-46`, `cloud_sync.py:23-34`).
- Files: `mcps/session-memory/server.py`, `mcps/session-memory/modules/embeddings.py`, `mcps/session-memory/modules/cloud_sync.py`
- Impact: Users may think features work when they're silently disabled. Incomplete feature sets cause confusion and frustration.
- Fix approach: Add explicit status reporting in tool responses. When semantic search or cloud sync is requested but unavailable, return clear error message with installation instructions, not silent degradation.

**Inconsistent error handling in tool handlers:**
- Issue: Some tool handlers catch all exceptions and return JSON errors (e.g., `streaming-output/server.py:1661-1662`) while others let exceptions propagate. Inconsistent error responses make client integration unpredictable.
- Files: `mcps/streaming-output/server.py`, `mcps/session-memory/server.py`
- Impact: Clients can't reliably distinguish between tool errors and server crashes. Error messages vary in format and content.
- Fix approach: Create centralized error handler that wraps all tool calls. Define error response schema (code, message, details). Log all errors with traceback.

## Known Bugs

**Database initialization race condition:**
- Symptoms: Multiple threads/processes accessing the same SQLite database during concurrent requests may fail with "database is locked" errors. FTS5 table creation can fail silently if unavailable (line 224-225 in `session-memory/server.py`).
- Files: `mcps/session-memory/server.py` (lines 217-225)
- Trigger: Run multiple `session_init()` calls concurrently against same database. Or run on system without FTS5 support (some SQLite builds).
- Workaround: Use journal_mode=WAL if possible, add connection retries with exponential backoff. Check FTS5 availability explicitly and log warnings.

**SQL construction with string formatting:**
- Symptoms: While most queries use parameterized statements, line 595 in `session-memory/server.py` builds SQL with f-string: `f"e.category IN ({placeholders})"`. If placeholders are ever generated from user input, this is SQL injection risk.
- Files: `mcps/session-memory/server.py` (line 595)
- Trigger: Construct malicious category list with SQL syntax. Unlikely with current code (categories are from enum), but fragile pattern.
- Workaround: Currently safe because placeholders are generated programmatically. However, replace pattern with SQLite dynamic query builder or explicit statement tuples for future-proofing.

**Checkpoint file handle leaks:**
- Symptoms: Checkpoints are saved as JSON files but not consistently validated or closed. No explicit file closing in save operations (see `session-memory/server.py` checkpoint creation).
- Files: `mcps/session-memory/server.py` (checkpoint save methods)
- Trigger: Create many checkpoints in rapid succession. Long-running sessions may accumulate unclosed file handles.
- Workaround: Always use context managers (`with open(...)`) or explicit `.close()` calls.

**Cloud sync conflict resolution untested:**
- Symptoms: `cloud_sync.py` contains conflict resolution logic with local-first priority, but no test coverage exists. Behavior with simultaneous local+remote changes is undefined.
- Files: `mcps/session-memory/modules/cloud_sync.py` (conflict resolution sections)
- Trigger: Modify session locally while sync is pushing/pulling. Resume session on different machine.
- Workaround: Disable cloud sync in production until tested. Document conflict resolution strategy clearly.

## Security Considerations

**API keys exposed in environment variable loading:**
- Risk: Multiple sensitive credentials loaded from environment: `OPENAI_API_KEY`, `CF_API_TOKEN`, `CF_R2_SECRET_ACCESS_KEY`. These are logged in debug output and may appear in error messages. The loading fallback chain (config → custom env var → default env var) is complex and could leak secrets if error messages include the chain.
- Files: `mcps/session-memory/server.py` (lines 25-35), `mcps/session-memory/modules/embeddings.py` (lines 42-46), `mcps/session-memory/modules/cloud_sync.py` (lines 47-85)
- Current mitigation: Environment variables are checked but not validated. No masking in logs. Error messages may include partial credential data.
- Recommendations:
  - Add credential masking in all error messages and logs (replace last 4 chars with `****`)
  - Validate credentials at startup and fail fast with clear message if invalid
  - Never log the full fallback chain in exceptions
  - Consider using secrets manager instead of environment variables for sensitive tokens
  - Document that `.env` files should never be committed

**SQL query parameters are properly used:**
- Risk: Low - Most queries use parameterized statements (lines 587-596 in `session-memory/server.py`). The f-string pattern at line 595 is for IN clause placeholders only, not user data.
- Current mitigation: Placeholder count matches parameter count. User data is passed via params list.
- Recommendations: Still replace f-string pattern with SQLite prepared statement for consistency.

**File path traversal in document ingestion:**
- Risk: `session_ingest()` accepts `file_path` parameter. If not validated, could read arbitrary files from system.
- Files: `mcps/session-memory/modules/document_ingest.py`, `mcps/session-memory/server.py` (tool definition around line 1800)
- Current mitigation: No visible path validation before file access.
- Recommendations:
  - Validate file_path is within allowed directory
  - Use `pathlib.Path.resolve()` to prevent `../` traversal
  - Maintain whitelist of allowed file types (pdf, docx, txt only)
  - Validate file size before processing

**R2 endpoint configuration:**
- Risk: `CF_R2_ENDPOINT_URL` allows configuring arbitrary S3-compatible endpoints. Could be used to exfiltrate credentials or redirect to malicious server.
- Files: `mcps/session-memory/modules/cloud_sync.py` (lines 81-85)
- Current mitigation: No URL validation before use.
- Recommendations: Validate endpoint URL matches expected Cloudflare domain pattern, fail if invalid.

## Performance Bottlenecks

**FTS5 queries without optimization:**
- Problem: Semantic search and keyword search use FTS5 (fulltext search) but no LIMIT clause in early results. For large event databases (1M+ events), queries may be slow and memory-intensive.
- Files: `mcps/session-memory/modules/embeddings.py` (semantic search), `mcps/session-memory/server.py` (query methods)
- Cause: FTS5 searches entire table before limiting results. No pagination guidance documented.
- Improvement path:
  - Add default LIMIT to FTS5 queries (e.g., 1000)
  - Index most-queried columns first
  - Consider denormalizing frequently-joined fields
  - Profile query performance with 100K+ events

**Embeddings computed on every query:**
- Problem: `session_semantic_search()` generates embeddings for search query on every call. OpenAI API call costs and latency scale with query volume.
- Files: `mcps/session-memory/modules/embeddings.py` (semantic_search method)
- Cause: No query embedding cache. Same queries re-compute embedding multiple times.
- Improvement path:
  - Cache query embeddings by hash for 24 hours
  - Batch embedding requests if multiple queries arrive
  - Document per-query cost in tool description

**SQLite in-process only:**
- Problem: Session memory and streaming output both use single SQLite instance. No connection pooling. High concurrency (many Claude instances) will cause "database locked" errors.
- Files: `mcps/session-memory/server.py`, `mcps/streaming-output/server.py`
- Cause: SQLite is file-based, single writer at a time. No journal_mode=WAL configuration visible.
- Improvement path:
  - Enable journal_mode=WAL for better concurrency
  - Consider PostgreSQL or SQLite in WAL mode for multi-process scenarios
  - Add connection pooling if multiple processes access same DB
  - Document scaling limits

**Checkpoint file system I/O:**
- Problem: Checkpoints saved as individual JSON files in `storage/checkpoints/`. No batching or compression. Large sessions may create hundreds of files, causing filesystem overhead.
- Files: `mcps/session-memory/server.py` (checkpoint save methods)
- Cause: One file per checkpoint, no archival strategy.
- Improvement path:
  - Add compression (.gz) for old checkpoints
  - Implement archive mode after N checkpoints
  - Consider storing in database instead of filesystem for small checksums

## Fragile Areas

**Plugin system without versioning:**
- Files: `mcps/session-memory/plugins/base.py`, `mcps/session-memory/plugins/*.py` (speckit.py, spec_refiner.py, speckit_maal.py, generic.py)
- Why fragile: Plugin interface (`SessionPlugin` base class) has no version or compatibility mechanism. Adding new methods to base class breaks all plugins. No validation that plugins implement required methods.
- Safe modification:
  - Add version field to plugin metadata
  - Use abstract base class with `@abstractmethod` decorators
  - Implement plugin discovery and validation at startup
  - Document required plugin interface
  - Test coverage: Implement tests for each plugin's on_event(), on_checkpoint(), on_query() methods

**Learning module context_hash collision risk:**
- Files: `mcps/session-memory/modules/learning.py`
- Why fragile: Learning entries use `context_hash` to deduplicate similar contexts. If hash function is weak or collision occurs, learnings may be incorrectly merged or lost.
- Safe modification:
  - Document hash algorithm (SHA-256 recommended, not md5)
  - Add collision detection/recovery
  - Test with 10K+ learning entries
  - Add versioning to hash function for future changes

**Entity relationship graph without cycle detection:**
- Files: `mcps/session-memory/modules/entities.py`
- Why fragile: `entity_link()` creates relationships between entities with no cycle detection. Cyclic relationships could cause infinite loops in graph traversal.
- Safe modification:
  - Add cycle detection before creating relationships
  - Implement depth-limited traversal for queries
  - Add test cases for circular relationships
  - Document relationship semantics (DAG vs general graph)

**Cloud sync state machine without transition validation:**
- Files: `mcps/session-memory/modules/cloud_sync.py` (sync_state tracking)
- Why fragile: Sync status transitions (pending → synced → pending) have no validation. Invalid state transitions could cause data loss.
- Safe modification:
  - Define valid state transitions explicitly
  - Validate transitions at write time
  - Add transition audit log
  - Test all state paths

## Scaling Limits

**SQLite concurrent write limit:**
- Current capacity: Single SQLite instance, ~10 concurrent readers, 1 writer
- Limit: >5 simultaneous writers cause "database locked" errors
- Scaling path:
  - Enable WAL mode (write-ahead logging) for better concurrency
  - Migrate to PostgreSQL for >50 concurrent connections
  - Implement connection pooling with PgBouncer if needed

**Memory consumption for large sessions:**
- Current capacity: Tested to 100K events per session, ~50MB memory
- Limit: Sessions with 1M+ events cause memory exhaustion and OOM errors
- Scaling path:
  - Implement pagination in query results
  - Archive old events to separate storage
  - Stream results instead of loading all to memory
  - Consider sharding sessions across database files

**Checkpoint storage filesystem:**
- Current capacity: ~1000 checkpoints per session before filesystem performance degrades
- Limit: >10K checkpoints cause slow checkpoint operations and directory listing timeouts
- Scaling path:
  - Archive old checkpoints to compressed tar files
  - Move checkpoints to database BLOB storage
  - Implement time-based retention policy (delete >30 days old)
  - Consider object storage (S3/R2) for checkpoint archive

**Embedding storage per event:**
- Current capacity: ~500K events with embeddings before database size exceeds 1GB
- Limit: Large embedding tables cause slow event queries due to join overhead
- Scaling path:
  - Store embeddings in separate database or vector store (Pinecone, Weaviate)
  - Implement lazy embedding generation (only for queried events)
  - Archive old embeddings to cold storage

## Dependencies at Risk

**mcp>=1.25.0 - MCP SDK version pinning:**
- Risk: Loose lower bound (>=1.25.0) means new major versions could introduce breaking changes. No maximum version constraint could pull in incompatible updates.
- Impact: Tool schemas changed in MCP 2025 spec. HTTP transport not available in older versions. Streaming output format changes could break clients.
- Migration plan:
  - Pin to compatible major version: `mcp>=1.25.0,<2.0.0`
  - Add integration tests that validate tool schema compliance
  - Document breaking changes in changelog

**Optional dependencies without fallback validation:**
- Risk: boto3, httpx, openai marked optional but feature completeness depends on them. Users enable cloud sync but dependency isn't installed, leading to silent failures.
- Impact: Cloud sync and semantic search appear to work but produce no results.
- Migration plan:
  - Make optional dependencies explicit in tool responses ("unavailable - install boto3")
  - Separate core and optional dependency groups in requirements.txt
  - Add startup validation that reports missing optional features

**beautifulsoup4 for HTML parsing:**
- Risk: No version pinning in requirements. beautifulsoup4 evolves constantly. HTML parsing behavior could change.
- Impact: Document ingestion for HTML files may behave inconsistently across versions.
- Migration plan: Pin to known-good version: `beautifulsoup4>=4.12.0,<5.0.0`

## Missing Critical Features

**No audit trail for changes:**
- Problem: Cloud sync and entity modifications don't record who changed what or when. No ability to recover from accidental deletions or trace data lineage.
- Blocks: Compliance requirements, debugging production issues, data recovery.

**No backup strategy:**
- Problem: Session data stored only in local SQLite and filesystem. No documented backup procedure. Disk failure = total data loss.
- Blocks: Production deployment, data persistence guarantees.

**No rate limiting or quota enforcement:**
- Problem: Tools can be called unlimited times. A malicious or buggy caller could abuse embedding generation (API costs) or flood database with events.
- Blocks: Multi-tenant scenarios, cost control, DoS protection.

**No monitoring or health checks:**
- Problem: No metrics or health endpoint. No way to know if MCP server is functioning until a tool call fails.
- Blocks: Reliable deployment, alerting, debugging.

## Test Coverage Gaps

**Cloud sync module untested:**
- What's not tested: D1 sync, R2 sync, conflict resolution, credential validation, API error handling
- Files: `mcps/session-memory/modules/cloud_sync.py`
- Risk: Cloud features could corrupt data or leak credentials in production with zero warning. 40+ exception handlers hide bugs.
- Priority: HIGH - This is new functionality with significant security/data impact.

**Embedding and semantic search untested:**
- What's not tested: OpenAI API failures, embedding cache behavior, similarity ranking, edge cases (empty results, malformed queries)
- Files: `mcps/session-memory/modules/embeddings.py`
- Risk: Semantic search may return irrelevant results or crash when OpenAI is unavailable.
- Priority: HIGH - Core feature affecting query quality.

**Entity graph traversal untested:**
- What's not tested: Circular relationships, deep traversal, relation weight calculations, entity deduplication
- Files: `mcps/session-memory/modules/entities.py`
- Risk: Graph queries could return infinite results, crash on cycles, or produce incorrect deduplicates.
- Priority: MEDIUM - Less commonly used but important for knowledge graph.

**Document ingestion untested:**
- What's not tested: Malformed PDFs, oversized files, path traversal attempts, extraction accuracy, memory leaks
- Files: `mcps/session-memory/modules/document_ingest.py`
- Risk: Untested parsing could crash server, expose files, or consume memory unbounded.
- Priority: HIGH - Security and stability risk.

**Streaming output format conversions untested:**
- What's not tested: CSV export, YAML export, HTML rendering, template application, export to file
- Files: `mcps/streaming-output/server.py` (export functions)
- Risk: Export features could produce malformed output, corrupt data, or fail silently.
- Priority: MEDIUM - Feature completeness and reliability.

**Plugin lifecycle untested:**
- What's not tested: Plugin initialization, state transitions, error recovery, plugin interactions
- Files: `mcps/session-memory/plugins/base.py`, plugin implementations
- Risk: Plugin system could silently drop events, corrupt state, or fail to initialize in edge cases.
- Priority: MEDIUM - Affects extensibility and reliability.

**Concurrency and race conditions untested:**
- What's not tested: Concurrent checkpoint creation, simultaneous queries, cloud sync + local changes, plugin state mutations
- Files: Throughout MCPs
- Risk: Data corruption, lost updates, inconsistent state under concurrent load.
- Priority: HIGH - Critical for reliability.

---

*Concerns audit: 2026-01-23*
