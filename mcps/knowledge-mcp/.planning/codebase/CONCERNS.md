# Codebase Concerns

**Analysis Date:** 2026-01-20

## Tech Debt

**Test File Import Mismatch:**
- Issue: Test file imports `IngestOutcome` and `IngestSection` from `knowledge_mcp.ingest.base` but these classes do not exist in the source
- Files: `tests/unit/test_ingest/test_base.py:11-18`
- Impact: Tests fail to collect, blocking all test runs - currently at 1 error during collection
- Fix approach: Either add missing `IngestOutcome` and `IngestSection` classes to `src/knowledge_mcp/ingest/base.py` or remove tests that depend on them

**Test Config Field Mismatch:**
- Issue: Test references `chunk_size_min` and `chunk_overlap` fields that don't exist in `KnowledgeConfig`
- Files: `tests/unit/test_config.py:54-61`
- Impact: Test failure on `test_chunk_overlap_validation`
- Fix approach: Remove the deprecated test or add the missing fields to `KnowledgeConfig` if they are needed

**Low Test Coverage (34%):**
- Issue: Test coverage is at 34.25%, far below the 80% requirement specified in CLAUDE.md
- Files: Coverage gaps throughout:
  - `src/knowledge_mcp/__main__.py`: 0% (14 lines)
  - `src/knowledge_mcp/ingest/docling_ingestor.py`: 18% (147 untested lines)
  - `src/knowledge_mcp/store/qdrant_store.py`: 16% (61 untested lines)
  - `src/knowledge_mcp/store/chromadb_store.py`: 22% (81 untested lines)
  - `src/knowledge_mcp/embed/openai_embedder.py`: 20% (60 untested lines)
  - `src/knowledge_mcp/server.py`: 25% (30 untested lines)
- Impact: Regressions may go undetected, build should be blocking but isn't properly enforced
- Fix approach: Add unit tests for uncovered modules, starting with high-value code paths

**MCP Server Stub Implementation:**
- Issue: `handle_list_tools()` returns empty list and `handle_call_tool()` returns "not implemented" for all tools
- Files: `src/knowledge_mcp/server.py:72-101`
- Impact: MCP server is non-functional - cannot actually search knowledge base
- Fix approach: Implement tool definitions and handlers as noted in code comments (TASK-024, Phase 5)

**Pyright Type Errors (55 errors):**
- Issue: 55 pyright errors in strict mode, mostly from Qdrant client lacking complete type stubs
- Files:
  - `src/knowledge_mcp/store/qdrant_store.py`: Multiple `reportUnknownMemberType` errors
  - `src/knowledge_mcp/store/chromadb_store.py`: `type: ignore` comments for chromadb lacking stubs
- Impact: Type safety is compromised, IDE experience degraded
- Fix approach: Add explicit type annotations for qdrant/chromadb return values, or use `# type: ignore` with explanatory comments

## Known Bugs

**Search Module Empty:**
- Symptoms: `src/knowledge_mcp/search/__init__.py` only has package docstring - no actual search implementation
- Files: `src/knowledge_mcp/search/__init__.py` (16 lines, all docstring)
- Trigger: Any attempt to use semantic search, hybrid search, or reranking features
- Workaround: Use store's raw `search()` method directly

**CLI Module Empty:**
- Symptoms: `src/knowledge_mcp/cli/__init__.py` only has package docstring - no CLI commands
- Files: `src/knowledge_mcp/cli/__init__.py` (15 lines, all docstring)
- Trigger: Any attempt to run CLI commands for document ingestion
- Workaround: None - must write custom scripts or use programmatic API

## Security Considerations

**API Keys in Memory:**
- Risk: OpenAI API keys stored in memory could be exposed via memory dumps
- Files: `src/knowledge_mcp/embed/openai_embedder.py:79-105`
- Current mitigation: Keys are never logged (per security.md §7.2), generic error messages
- Recommendations: Document that process memory should be protected, consider using secure string types

**No Input Sanitization on Search Queries:**
- Risk: Search queries passed directly to vector stores without validation
- Files: `src/knowledge_mcp/store/qdrant_store.py:215-270`, `src/knowledge_mcp/store/chromadb_store.py:342-410`
- Current mitigation: Relies on downstream library validation
- Recommendations: Add query length limits and content validation before passing to stores

## Performance Bottlenecks

**Synchronous Document Conversion:**
- Problem: Docling `DocumentConverter.convert()` is synchronous and can block for large documents
- Files: `src/knowledge_mcp/ingest/docling_ingestor.py:228`, `src/knowledge_mcp/ingest/docling_ingestor.py:281`
- Cause: No async wrapper around docling conversion, blocking I/O in async context
- Improvement path: Run docling conversion in thread pool executor or background worker

**Token Estimation Approximation:**
- Problem: Token count estimated as `len(text) // 4` instead of actual tokenizer
- Files: `src/knowledge_mcp/chunk/docling_chunker.py:340-342`
- Cause: Avoiding tiktoken dependency at chunk creation time
- Improvement path: Use actual tokenizer for accurate counts, or defer until embedding time

**Batch Size Hardcoded:**
- Problem: Store batch sizes hardcoded to 100, may not be optimal for all use cases
- Files:
  - `src/knowledge_mcp/store/qdrant_store.py:205` (batch_size = 100)
  - `src/knowledge_mcp/store/chromadb_store.py:222` (batch_size = 100)
  - `src/knowledge_mcp/embed/openai_embedder.py:49` (MAX_BATCH_SIZE = 100)
- Cause: Conservative defaults for OpenAI limits
- Improvement path: Make batch size configurable via `KnowledgeConfig`

## Fragile Areas

**Store Fallback Logic:**
- Files: `src/knowledge_mcp/store/__init__.py:154-239`
- Why fragile: Complex conditional logic with exception handling across two backends
- Safe modification: Test both Qdrant and ChromaDB paths independently; mock health checks
- Test coverage: Only 19% - most error paths untested

**Docling Chunk Context Extraction:**
- Files: `src/knowledge_mcp/chunk/docling_chunker.py:271-317`
- Why fragile: Heavy use of `hasattr()` checks for Docling internals that may change
- Safe modification: Pin docling version; add integration tests with real documents
- Test coverage: 28% - context extraction largely untested

**Exception Hierarchy:**
- Files: `src/knowledge_mcp/exceptions.py:54-375`
- Why fragile: Custom exceptions shadow builtins (`ConnectionError`, `TimeoutError`)
- Safe modification: Always import from `knowledge_mcp.exceptions` explicitly
- Test coverage: 89% - relatively well tested

## Scaling Limits

**Vector Store Collection Size:**
- Current capacity: Qdrant Cloud free tier has undocumented limits; ChromaDB is local storage bound
- Limit: Large document collections may exceed free tier quotas or local disk
- Scaling path: Upgrade Qdrant tier; shard collections; implement pruning

**Embedding API Rate Limits:**
- Current capacity: OpenAI rate limits apply (varies by tier)
- Limit: High-volume ingestion will hit rate limits
- Scaling path: Implement adaptive rate limiting; consider local embedding models (mentioned in CLAUDE.md but not implemented: `local_embedder.py`)

## Dependencies at Risk

**Docling (IBM):**
- Risk: Early-stage library (version < 1.0), API may change
- Impact: Ingestion pipeline could break on updates
- Migration plan: Pin version strictly; abstract behind interface for potential replacement

**Qdrant Client Type Stubs:**
- Risk: Missing/incomplete type stubs cause 55 pyright errors
- Impact: Reduced type safety, IDE experience degraded
- Migration plan: Monitor for upstream stub improvements; add local type annotations

**ChromaDB Type Stubs:**
- Risk: ChromaDB lacks complete type stubs, requires `type: ignore` comments
- Impact: Type errors suppressed, may hide real issues
- Migration plan: Monitor chromadb releases for improved typing

## Missing Critical Features

**Local Embedding Support:**
- Problem: CLAUDE.md specifies `local_embedder.py` but it doesn't exist
- Blocks: Running without internet/API costs; offline deployment
- Files referenced in spec: `src/knowledge_mcp/embed/local_embedder.py` (missing)

**Search/Retrieval Layer:**
- Problem: No semantic search, hybrid search, or reranker implementation
- Blocks: Core RAG functionality - can only do raw vector search
- Files expected: `src/knowledge_mcp/search/semantic_search.py`, `hybrid_search.py`, `reranker.py` (all missing)

**CLI Interface:**
- Problem: No command-line interface for ingestion or verification
- Blocks: Operational workflows documented in CLAUDE.md
- Files expected: `scripts/ingest_documents.py`, `verify_embeddings.py` (scripts directory empty)

**Hierarchical/Semantic Chunkers:**
- Problem: Only DoclingChunker exists; specialized chunkers mentioned in CLAUDE.md are missing
- Blocks: Optimal chunking strategies for different document types
- Files expected: `src/knowledge_mcp/chunk/hierarchical.py`, `semantic.py`, `standards.py` (all missing)

## Test Coverage Gaps

**Integration Tests:**
- What's not tested: End-to-end flows from ingestion to search
- Files: Only `tests/integration/test_store_fallback.py` exists
- Risk: Component interactions may fail in production
- Priority: High

**MCP Protocol Handlers:**
- What's not tested: Server initialization, tool listing, tool invocation
- Files: `src/knowledge_mcp/server.py` (25% coverage)
- Risk: MCP server may not function correctly with Claude
- Priority: High (core functionality)

**Docling Integration:**
- What's not tested: Real document conversion, structure extraction, error handling
- Files: `src/knowledge_mcp/ingest/docling_ingestor.py` (18% coverage)
- Risk: Document processing may fail silently or corrupt data
- Priority: High

**OpenAI Embedder:**
- What's not tested: Actual API calls, retry logic, error classification
- Files: `src/knowledge_mcp/embed/openai_embedder.py` (20% coverage)
- Risk: Embedding failures may not be handled correctly
- Priority: Medium (retry logic critical)

**Vector Store Operations:**
- What's not tested: Add, search, stats, health check with real backends
- Files: `src/knowledge_mcp/store/qdrant_store.py` (16%), `chromadb_store.py` (22%)
- Risk: Data may not persist or retrieve correctly
- Priority: High

---

*Concerns audit: 2026-01-20*
