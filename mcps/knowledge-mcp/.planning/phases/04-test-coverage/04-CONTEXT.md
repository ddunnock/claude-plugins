# Phase 4: Test Coverage - Context

**Gathered:** 2026-01-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Achieve 80% line coverage and 75% branch coverage across the Knowledge MCP codebase through comprehensive unit and integration tests. This includes testing the critical path (search → store → MCP server), document ingestion pipeline, and all error/fallback paths.

</domain>

<decisions>
## Implementation Decisions

### Coverage Prioritization
- Critical path first: Search → Store → MCP server (the path users actually hit)
- Error branches prioritized over conditional logic branches for branch coverage
- Document ingestion code included in 80% target (not deferred)
- Aggregate 80% target only — no per-module minimums

### Integration Test Scope
- Vector store tests use mocked BaseStore interface only — no real Qdrant/ChromaDB
- Embedding tests use mocked embeddings only — no real OpenAI API calls
- MCP tool handlers get full E2E protocol tests (actual JSON-RPC over stdio)
- Docling ingestion tested with real sample documents (small PDFs/DOCXs in fixtures)

### Test Data Strategy
- Shared fixtures in tests/conftest.py, reused across tests
- Minimal sample documents — small PDF, DOCX, Markdown with minimal content
- Fixed deterministic vectors for synthetic embeddings ([0.1, 0.2, ...] style)
- Environment variables mocked/stubbed — tests never read real env vars

### Edge Case Depth
- Comprehensive error path testing — every exception type, timeout, retry, fallback
- Full empty state coverage — empty query, empty store, missing metadata, null fields
- Boundary condition tests — n_results=0, n_results=50, token overflow, dimension mismatch
- Full fallback path testing — connection failure, timeout, auth error each triggers fallback

### Security Testing
- Test injection vectors — malicious query strings, path traversal in document paths
- Verify sensitive data filtering — logs filter API keys, error messages don't expose secrets
- Stress testing with memory leak detection — run many operations, monitor memory growth
- Add ruff security rules and complexity limits

### Claude's Discretion
- Specific test file organization within tests/ directory
- Which edge cases are most important given code analysis
- How to structure stress tests for leak detection
- Specific ruff rules to enable for security/complexity

</decisions>

<specifics>
## Specific Ideas

- Tests should be fast — mocking external services is critical for CI speed
- E2E MCP protocol tests verify real JSON-RPC behavior, not just handler functions
- Real sample documents for Docling tests ensure actual parsing works, not just mocked paths
- Memory leak detection via repeated operations and tracemalloc or similar

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-test-coverage*
*Context gathered: 2026-01-27*
