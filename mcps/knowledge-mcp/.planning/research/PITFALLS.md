# Domain Pitfalls

**Domain:** MCP Server + RAG Pipeline for Technical Documents
**Researched:** 2026-01-20
**Context:** Completing existing codebase with known issues (55 pyright errors, 34% coverage)

---

## Critical Pitfalls

Mistakes that cause rewrites, production failures, or major blockers.

### Pitfall 1: Test-Code Mismatch Leading to False Confidence

**What goes wrong:** Tests import classes that do not exist in the source code, causing test collection failures. The test suite appears to run but actually skips all affected tests.

**Why it happens:**
- Code was refactored without updating tests
- Test stubs written speculatively for planned classes
- Copy-paste from documentation examples that were never implemented

**Consequences:**
- Test coverage metrics are wrong (shows 34% but real coverage may be lower)
- CI passes because pytest reports "0 failures" but actually collected nothing
- Bugs ship to production undetected

**Evidence in codebase:**
- `tests/unit/test_ingest/test_base.py` imports `IngestOutcome` and `IngestSection` which do not exist in `src/knowledge_mcp/ingest/base.py`
- `tests/unit/test_config.py` references `chunk_size_min` and `chunk_overlap` fields that do not exist in `KnowledgeConfig`

**Prevention:**
1. Run `pytest --collect-only` before any test run to verify all tests can be collected
2. Add CI step that fails if any import errors occur during collection
3. Use `# type: ignore` sparingly and never on test imports
4. Match test file structure exactly to source file structure

**Detection:**
- pytest collection errors (currently 1 error during collection)
- Missing coverage in modules that have tests
- CI logs showing "0 tests collected" for files with tests

**Phase to address:** Phase 1 (foundation) - Must fix before any new code

---

### Pitfall 2: Third-Party Type Stub Gaps Breaking Strict Mode

**What goes wrong:** Libraries like Qdrant and ChromaDB lack complete type stubs, causing cascading `reportUnknownMemberType` errors in pyright strict mode. Developers either give up on strict mode or litter code with `type: ignore`.

**Why it happens:**
- Python ecosystem has inconsistent typing support
- Vector database libraries prioritize functionality over typing
- Pyright strict mode is aggressive about `Any` propagation

**Consequences:**
- 55+ pyright errors blocking CI enforcement
- Type safety is compromised in the very code that needs it most (data persistence)
- IDE autocomplete and refactoring tools break down

**Evidence in codebase:**
- `src/knowledge_mcp/store/qdrant_store.py`: Multiple `reportUnknownMemberType` errors
- `src/knowledge_mcp/store/chromadb_store.py`: `type: ignore` comments scattered throughout

**Prevention:**
1. Create explicit wrapper functions with known return types for external calls
2. Use `cast()` with documented reasoning rather than `type: ignore`
3. Isolate third-party interactions to thin adapter layers
4. Consider contributing type stubs upstream or using `py.typed` stubs

**Detection:**
- Run pyright with `--outputjson` to count errors by category
- Track which libraries contribute most errors
- Monitor for `type: ignore` proliferation

**Recommended pattern:**
```python
# Instead of:
result = self.client.search(...)  # type: ignore[reportUnknownMemberType]

# Do this:
def _search_raw(self, params: SearchParams) -> list[dict[str, Any]]:
    """Wrapper with explicit return type."""
    raw_result = self.client.search(...)  # Single type: ignore here
    return cast(list[dict[str, Any]], raw_result)  # Document expected shape
```

**Phase to address:** Phase 1-2 - Create adapter layer patterns early

---

### Pitfall 3: MCP Server Without Functional Tools

**What goes wrong:** An MCP server is deployed that lists tools but returns "not implemented" for all of them. Claude can connect but cannot actually use the knowledge base.

**Why it happens:**
- Tool definitions are easy to write; implementations are complex
- Focus on protocol compliance without end-to-end testing
- No integration tests that verify search results flow to Claude

**Consequences:**
- Server appears healthy but is non-functional
- Users report "it doesn't work" with no actionable feedback
- Debugging requires understanding MCP protocol deeply

**Evidence in codebase:**
- `server.py:72-101`: `handle_list_tools()` returns empty list
- `handle_call_tool()` returns "not implemented" for all tools
- No integration tests for MCP tool invocation

**Prevention:**
1. Implement ONE working tool end-to-end before adding more
2. Write integration test that: starts server -> calls tool -> verifies results
3. Use MCP Inspector tool for manual verification
4. Log tool invocations with input/output for debugging

**Detection:**
- MCP Inspector shows tools but they return errors
- `list_tools` returns empty or incomplete list
- Tool calls return generic "not implemented" messages

**Phase to address:** Phase 3 (MCP implementation) - Core functionality

---

### Pitfall 4: Store Fallback Logic That Masks Failures

**What goes wrong:** Fallback logic catches all exceptions uniformly, masking configuration errors as transient connection issues. A typo in QDRANT_URL causes silent fallback to ChromaDB.

**Why it happens:**
- Defensive programming taken too far
- Exception handling that catches `Exception` instead of specific types
- No distinction between "unavailable" and "misconfigured"

**Consequences:**
- Configuration errors discovered in production
- ChromaDB silently used when Qdrant was intended
- Debugging requires examining logs carefully
- 19% coverage means most error paths are untested

**Evidence in codebase:**
- `store/__init__.py:154-239`: Both `_try_qdrant` and `_try_chromadb` catch generic `Exception`
- No distinction between auth errors (config problem) and timeout errors (transient)
- Coverage only 19% on store module

**Prevention:**
1. Categorize exceptions: ConfigurationError should NOT trigger fallback
2. Only fallback on clearly transient errors (timeout, connection refused)
3. Log at ERROR level for auth failures, WARNING for transient
4. Test each fallback path explicitly

**Detection:**
- WARNING logs about fallback when QDRANT_URL is wrong
- ChromaDB being used unexpectedly
- Auth errors not surfaced to user

**Recommended exception hierarchy:**
```python
# DO fallback:
- ConnectionRefusedError
- TimeoutError
- socket.gaierror (DNS failure)

# DO NOT fallback:
- AuthenticationError (bad API key)
- ConfigurationError (invalid URL format)
- PermissionError (ChromaDB path not writable)
```

**Phase to address:** Phase 2 - Before deploying with real credentials

---

### Pitfall 5: Docling API Instability Across Versions

**What goes wrong:** Docling is pre-1.0 software. API changes between versions break the ingestor silently because the code uses extensive `hasattr()` checks that fail silently.

**Why it happens:**
- Docling evolves rapidly (IBM actively developing)
- Code written against one version, deployed with another
- `hasattr()` checks hide attribute removal instead of failing

**Consequences:**
- Documents ingest but metadata is missing
- Page numbers, headings, or hierarchy silently lost
- Chunking produces unexpected results
- No explicit error, just wrong data

**Evidence in codebase:**
- `docling_ingestor.py:504-534`: Multiple `hasattr()` checks for Docling internals
- `docling_chunker.py:287-317`: Similar pattern in context extraction
- Version pinned to `>=2.15.0` but not upper-bounded
- Only 18% test coverage on ingestor

**Prevention:**
1. Pin Docling version EXACTLY: `docling==2.15.0` not `>=2.15.0`
2. Add integration tests with REAL documents (not mocks)
3. Replace `hasattr()` with explicit attribute access and catch `AttributeError`
4. Create changelog review process when updating Docling

**Detection:**
- Missing metadata in ingested documents
- `AttributeError` exceptions in production (if not using hasattr)
- Chunks missing page numbers or headings

**Test strategy:**
```python
# Instead of mocking Docling:
def test_ingest_real_pdf():
    """Integration test with actual PDF."""
    ingestor = DoclingIngestor()
    doc = ingestor.ingest_to_docling_document(Path("tests/fixtures/sample.pdf"))

    # Verify specific fields we depend on
    assert hasattr(doc, 'iterate_items')  # Will fail if API changes
    items = list(doc.iterate_items())
    assert len(items) > 0
    assert hasattr(items[0][0], 'text')  # Verify item structure
```

**Phase to address:** Phase 1 and ongoing - Pin version immediately, add tests

---

## Moderate Pitfalls

Mistakes that cause delays or technical debt.

### Pitfall 6: Exception Hierarchy Shadowing Builtins

**What goes wrong:** Custom `ConnectionError` and `TimeoutError` classes shadow Python builtins, causing subtle bugs when code expects builtin behavior.

**Why it happens:**
- Natural naming choice for custom exceptions
- Easy to import wrong one accidentally
- IDE autocomplete may suggest builtin

**Consequences:**
- `except ConnectionError` catches wrong exception
- Retry logic fails because it catches custom exception
- Debugging confusion about which exception was raised

**Evidence in codebase:**
- `exceptions.py:147-169`: Custom `ConnectionError` shadows `builtins.ConnectionError`
- `exceptions.py:172-194`: Custom `TimeoutError` shadows `builtins.TimeoutError`
- CONCERNS.md notes this as fragile area

**Prevention:**
1. Always import from `knowledge_mcp.exceptions` explicitly
2. Consider renaming: `KnowledgeConnectionError`, `KnowledgeTimeoutError`
3. Add lint rule to prevent `from builtins import ConnectionError`
4. Document clearly in module docstring

**Detection:**
- Unexpected exception handling behavior
- Retry logic not triggering
- Different behavior between Python versions

**Phase to address:** Phase 1 - Establish import conventions early

---

### Pitfall 7: Synchronous Docling in Async Context

**What goes wrong:** `DocumentConverter.convert()` is synchronous and blocks the event loop when called from async code, causing timeouts on large documents.

**Why it happens:**
- Docling doesn't provide async API
- Easy to miss in small test documents
- Event loop blocking not obvious in single-user testing

**Consequences:**
- MCP server becomes unresponsive during ingestion
- Other requests timeout while document processes
- CPU-bound work blocks entire async application

**Evidence in codebase:**
- `docling_ingestor.py:228`: `result = self.converter.convert(str(path))` - synchronous
- No thread pool executor wrapping
- CONCERNS.md lists this as performance bottleneck

**Prevention:**
1. Wrap synchronous calls in `asyncio.to_thread()` or `run_in_executor()`
2. Add timeout monitoring for conversion
3. Consider background worker process for large documents
4. Document expected processing times

**Detection:**
- Request timeouts during ingestion
- High latency on concurrent requests
- Event loop warnings in logs

**Recommended fix:**
```python
async def ingest_async(self, path: Path) -> list[IngestResult]:
    """Async wrapper that doesn't block event loop."""
    return await asyncio.to_thread(self.ingest, path)
```

**Phase to address:** Phase 4 (optimization) - After core functionality works

---

### Pitfall 8: Token Count Estimation Drift

**What goes wrong:** Token count is estimated as `len(text) // 4` but actual token count varies significantly, causing chunks that exceed embedding model limits.

**Why it happens:**
- Avoiding tiktoken dependency at chunk time
- English text averages ~4 chars/token but varies
- Technical documents have unusual token patterns (numbers, acronyms)

**Consequences:**
- Chunks rejected by embedding API for being too long
- Inconsistent chunk sizes affect retrieval quality
- Token budget calculations wrong

**Evidence in codebase:**
- `docling_chunker.py:340-342`: `estimated_tokens = len(text) // 4`
- Comment says "will be refined when embedding is computed" but no refinement code exists
- OpenAI has hard limits on input tokens

**Prevention:**
1. Use actual tokenizer for final token count before embedding
2. Add validation: reject chunks exceeding max tokens
3. Track estimation accuracy in metrics
4. Use conservative estimate (3 chars/token for technical text)

**Detection:**
- OpenAI API errors about token limits
- Wide variance in chunk sizes
- Retrieval quality degradation

**Phase to address:** Phase 2-3 - Before embedding large document sets

---

### Pitfall 9: Search Module As Empty Placeholder

**What goes wrong:** Architecture specifies semantic/hybrid search, but module only contains docstrings. Code calling `search` module will fail at runtime.

**Why it happens:**
- Designed but not implemented
- Module created to satisfy import structure
- No tests that would catch missing implementation

**Consequences:**
- Import succeeds but usage fails
- Architecture diagrams don't match reality
- Developers confused about what's implemented

**Evidence in codebase:**
- `search/__init__.py`: 16 lines, all docstring
- Missing: `semantic_search.py`, `hybrid_search.py`, `reranker.py`
- CONCERNS.md lists this as missing critical feature

**Prevention:**
1. Add `raise NotImplementedError()` to placeholder modules
2. Create failing tests for planned functionality
3. Mark unimplemented features clearly in documentation
4. Don't create module structure until implementing

**Detection:**
- `AttributeError` when accessing search functions
- Missing coverage because code doesn't exist
- Import works but call fails

**Phase to address:** Phase 3-4 - Implement or remove placeholder

---

## Minor Pitfalls

Mistakes that cause annoyance but are fixable.

### Pitfall 10: Hardcoded Batch Sizes

**What goes wrong:** Batch size of 100 is hardcoded in multiple places, preventing optimization for different environments.

**Why it happens:**
- Conservative default for OpenAI limits
- Copy-pasted between modules
- No configuration exposed

**Consequences:**
- Suboptimal performance for different use cases
- Cannot tune for rate limits or memory constraints
- Changes require modifying multiple files

**Evidence in codebase:**
- `qdrant_store.py:205`: `batch_size = 100`
- `chromadb_store.py:222`: `batch_size = 100`
- `openai_embedder.py:49`: `MAX_BATCH_SIZE = 100`

**Prevention:**
1. Centralize batch size in `KnowledgeConfig`
2. Allow environment variable override
3. Document why 100 was chosen

**Phase to address:** Phase 4 (optimization) - Nice to have

---

### Pitfall 11: Missing CLI Module

**What goes wrong:** CLAUDE.md documents CLI commands that don't exist. Users try documented commands and get errors.

**Why it happens:**
- Documentation written optimistically
- pyproject.toml defines entry points for non-existent code
- No validation that documented features exist

**Consequences:**
- User frustration
- Documentation loses credibility
- Workarounds needed for operational tasks

**Evidence in codebase:**
- `pyproject.toml:107-108`: Entry points defined for missing CLI
- `cli/__init__.py`: Only docstring, no commands
- Missing `scripts/ingest_documents.py`, `verify_embeddings.py`

**Prevention:**
1. Only document implemented features
2. Validate entry points in CI
3. Use TODO markers in docs for planned features

**Phase to address:** Phase 5 - When building operational tooling

---

### Pitfall 12: Metadata List Serialization for ChromaDB

**What goes wrong:** ChromaDB requires scalar metadata values, so lists are serialized as comma-separated strings. Reconstruction may fail on edge cases.

**Why it happens:**
- ChromaDB limitation
- Simple serialization chosen
- Edge cases not considered

**Consequences:**
- Metadata with commas in values corrupted
- Empty list `[]` becomes empty string `""`, then `[""]` on reconstruction
- Query results have wrong metadata

**Evidence in codebase:**
- `chromadb_store.py:181-183`: `",".join(...)` for lists
- `chromadb_store.py:309-322`: Reconstruction logic
- No handling for values containing commas

**Prevention:**
1. Use JSON serialization for complex types
2. Add round-trip tests for metadata
3. Document serialization format

**Detection:**
- Metadata mismatch between stored and retrieved
- Extra empty strings in lists
- Search filters returning wrong results

**Phase to address:** Phase 2 - When ChromaDB usage increases

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Foundation (1) | Test-code mismatch | Run `pytest --collect-only` first |
| Type Safety (1-2) | Type stub gaps | Create adapter layer with explicit types |
| Store Integration (2) | Fallback masking config errors | Categorize exceptions, don't catch-all |
| MCP Implementation (3) | Empty tool implementations | End-to-end test ONE tool first |
| Document Ingestion (3) | Docling API changes | Pin exact version, real-doc tests |
| Search Features (3-4) | Empty search module | Implement or remove placeholder |
| Optimization (4) | Sync blocking in async | Use `asyncio.to_thread()` |
| Operations (5) | Missing CLI | Implement documented features |

---

## Sources

- **Codebase analysis:** Direct inspection of `/Users/dunnock/projects/knowledge-mcp/src/`
- **CONCERNS.md:** `/Users/dunnock/projects/knowledge-mcp/.planning/codebase/CONCERNS.md`
- **CLAUDE.md:** Project standards document
- **Test files:** `/Users/dunnock/projects/knowledge-mcp/tests/`
- **pyproject.toml:** Dependency versions and configuration
- **Confidence:** HIGH for codebase-specific pitfalls (direct evidence), MEDIUM for general MCP/RAG patterns (based on training data, not verified with current docs)

---

*Concerns audit: 2026-01-20*
