# Phase 03 Plan 01: MCP Tool Handlers Summary

**One-liner:** Implemented working knowledge_search and knowledge_stats MCP tools with dependency injection, error handling, and comprehensive unit tests (12 test cases, 396 lines)

---

## What Was Built

### Core Implementation
- **Dependency injection** in KnowledgeMCPServer constructor for embedder and store
- **Lazy initialization** via `_ensure_dependencies()` to support test mocking
- **Two MCP tools** with comprehensive descriptions and JSON schemas:
  - `knowledge_search`: Semantic search with filters and score thresholds
  - `knowledge_stats`: Collection statistics (chunk count, config)
- **Tool handlers** that format results for LLM consumption with source citations
- **Error handling** wrapper returning structured `{error, isError}` responses
- **Unknown tool handling** with proper error responses

### Quality Assurance
- **12 comprehensive unit tests** across 4 test classes (396 lines)
- **Zero pyright errors** in strict mode
- **All 65 tests passing** (53 existing + 12 new)
- **Server starts successfully** via `python -m knowledge_mcp`

---

## Tasks Completed

### Task 1: Add dependency injection and tool definitions to server
**Files:** `src/knowledge_mcp/server.py`, `src/knowledge_mcp/__main__.py`, `src/knowledge_mcp/store/__init__.py`

**Changes:**
- Added optional `embedder` and `store` parameters to KnowledgeMCPServer constructor
- Implemented `_ensure_dependencies()` for lazy initialization when server runs
- Created SemanticSearcher instance combining embedder and store
- Defined knowledge_search tool with query, n_results, filter_dict, score_threshold parameters
- Defined knowledge_stats tool with empty schema (no parameters required)
- Fixed `print()` in `__main__.py` to use `sys.stderr.write()` (prevents JSON-RPC corruption)
- Updated `create_store()` return type from `Union[QdrantStore, ChromaDBStore]` to `BaseStore` for type safety

**Verification:**
- ✅ `poetry run pyright src/knowledge_mcp/server.py` - 0 errors
- ✅ `poetry run python -c "from knowledge_mcp.server import KnowledgeMCPServer; print('import OK')"` - Success

**Commit:** `a024388`

---

### Task 2: Implement call_tool handlers with error handling
**Files:** `src/knowledge_mcp/server.py`

**Changes:**
- Added `_handle_knowledge_search()` async method:
  - Calls `SemanticSearcher.search()` with all parameters
  - Formats results with source citations (document_title, section_title, clause_number, page_numbers)
  - Returns JSON with results array, query, and total_results count
- Added `_handle_knowledge_stats()` async method:
  - Calls `store.get_stats()` wrapped in `asyncio.to_thread` (sync method)
  - Returns collection statistics as JSON
- Implemented error handling wrapper in `handle_call_tool()`:
  - Catches all exceptions and returns `{error, isError: true}` response
  - Handles unknown tools with structured error response
- Added imports: `asyncio`, `json` for handler implementations

**Verification:**
- ✅ `poetry run pyright src/knowledge_mcp/server.py` - 0 errors
- ✅ `poetry run pytest -xvs` - All tests pass

**Commit:** `be03bd4`

---

### Task 3: Create unit tests for MCP tool handlers
**Files:** `tests/unit/test_server.py` (new file, 396 lines)

**Test Coverage:**
1. **TestListTools** (3 tests):
   - Tool count verification (2 tools returned)
   - knowledge_search schema validation (required params, properties)
   - knowledge_stats empty schema verification

2. **TestKnowledgeSearch** (4 tests):
   - Formatted results with content, score, query, total_results
   - Source citations included (document_title, section, clause, pages)
   - All arguments passed through correctly (n_results, filter_dict, score_threshold)
   - Empty results handled gracefully

3. **TestKnowledgeStats** (2 tests):
   - Collection info returned (collection_name, total_chunks, vectors_count)
   - store.get_stats() called correctly

4. **TestErrorHandling** (3 tests):
   - Unknown tools return structured error
   - Search errors handled gracefully (empty results via SemanticSearcher)
   - Stats errors return structured error response

**Test Infrastructure:**
- Fixtures for mock_embedder, mock_store, server instances
- Proper MCP request types (`ListToolsRequest`, `CallToolRequest`)
- Access response via `response.root.tools` and `response.root.content`

**Verification:**
- ✅ `poetry run pytest tests/unit/test_server.py -xvs` - 12/12 tests pass
- ✅ `poetry run pyright tests/unit/test_server.py` - 0 errors
- ✅ File length: 396 lines (exceeds 80 line minimum)

**Commit:** `c6973ce`

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Fixed create_store() return type**
- **Found during:** Task 1
- **Issue:** `create_store()` returned `Union[QdrantStore, ChromaDBStore]` causing pyright error when assigning to `BaseStore`
- **Fix:** Changed return type to `BaseStore` for proper type safety
- **Files modified:** `src/knowledge_mcp/store/__init__.py`
- **Commit:** a024388

**2. [Rule 1 - Bug] Fixed print() in __main__.py**
- **Found during:** Task 1
- **Issue:** Using `print()` corrupts JSON-RPC protocol in MCP stdio transport
- **Fix:** Replaced with `sys.stderr.write()` for error messages
- **Files modified:** `src/knowledge_mcp/__main__.py`
- **Commit:** a024388

**3. [Rule 2 - Missing Critical] Added type annotations for formatted_results**
- **Found during:** Task 2
- **Issue:** Pyright strict mode reported unknown types for list comprehension
- **Fix:** Added explicit type annotations `formatted_results: list[dict[str, Any]]` and `result_dict: dict[str, Any]`
- **Files modified:** `src/knowledge_mcp/server.py`
- **Commit:** be03bd4

---

## Key Technical Decisions

### Decision 1: Lazy Dependency Initialization
**Context:** Tests need to mock dependencies, but production needs real instances

**Chosen approach:** Lazy initialization via `_ensure_dependencies()`
- Constructor accepts optional embedder/store parameters
- If not provided, creates from config when `_ensure_dependencies()` is called
- Tests inject mocks, production uses real dependencies

**Alternatives considered:**
- Factory function: More complex, harder to test
- Always require parameters: No default behavior for production

**Rationale:** Enables clean test mocking while providing sensible defaults for production

---

### Decision 2: MCP Request Type Access Pattern
**Context:** MCP SDK uses request type classes as dictionary keys

**Chosen approach:** Access handlers via `server.request_handlers[ListToolsRequest](request)`
- Discovered through experimentation that `request_handlers` is a dict
- Keys are request type classes (`ListToolsRequest`, `CallToolRequest`)
- Values are handler functions

**Alternatives considered:**
- Direct method calls: Not exposed by MCP SDK
- String keys: Incorrect API

**Rationale:** Follow MCP SDK design pattern for handler registration and invocation

---

### Decision 3: Error Handling Strategy
**Context:** SemanticSearcher already implements graceful degradation (returns empty list on error)

**Chosen approach:** Two-layer error handling
- **SemanticSearcher layer:** Logs error, returns empty list (graceful degradation)
- **MCP handler layer:** Catches exceptions, returns `{error, isError: true}` for protocol errors

**Result:** Search errors return empty results (expected behavior), while unknown tools and stats errors return structured error responses

**Rationale:** Balances graceful degradation for search with proper error signaling for protocol-level issues

---

## Files Created/Modified

### Created
- `tests/unit/test_server.py` (396 lines)
  - Comprehensive unit tests for MCP tool handlers
  - 12 test cases across 4 test classes

### Modified
- `src/knowledge_mcp/server.py`
  - Added dependency injection (embedder, store parameters)
  - Implemented lazy initialization
  - Added tool definitions (knowledge_search, knowledge_stats)
  - Implemented tool handlers with error handling
  - Added `_handle_knowledge_search()` and `_handle_knowledge_stats()` methods

- `src/knowledge_mcp/__main__.py`
  - Fixed print() to sys.stderr.write() for JSON-RPC compatibility

- `src/knowledge_mcp/store/__init__.py`
  - Updated create_store() return type to BaseStore

---

## Next Phase Readiness

### Blockers
None - Phase 3 MCP tools implementation is complete and functional.

### Concerns
None - All success criteria met:
1. ✅ knowledge_search tool returns formatted search results with source citations
2. ✅ knowledge_stats tool returns collection statistics
3. ✅ python -m knowledge_mcp starts without import errors
4. ✅ Unknown tools return `{error, isError: true}`
5. ✅ All tests pass (65/65 including 12 new server tests)
6. ✅ Zero pyright errors

### Dependencies for Next Phase
The MCP server is now functional and ready for:
- Phase 4: Document ingestion pipeline
- Phase 5: Integration testing with real knowledge base
- Deployment configuration and documentation

---

## Testing

### Test Results
```
65 passed, 3 warnings in 22.09s
Coverage: 57% (improved from 26% baseline)
```

### New Test Coverage
- **TestListTools:** Tool definitions and schemas (3 tests)
- **TestKnowledgeSearch:** Search functionality and formatting (4 tests)
- **TestKnowledgeStats:** Statistics retrieval (2 tests)
- **TestErrorHandling:** Error responses and graceful degradation (3 tests)

### Type Safety
```
poetry run pyright src/knowledge_mcp/server.py
0 errors, 0 warnings, 0 informations

poetry run pyright tests/unit/test_server.py
0 errors, 0 warnings, 0 informations
```

---

## Performance

**Execution Time:** ~10 minutes
- Task 1: ~3 minutes (implementation + verification)
- Task 2: ~3 minutes (implementation + type fixing)
- Task 3: ~4 minutes (test creation + debugging MCP API)

**Test Execution:** 22 seconds for full test suite (65 tests)

---

## Lessons Learned

### What Worked Well
1. **Dependency injection pattern** enabled clean test mocking
2. **MCP SDK request handlers** pattern discovered through REPL experimentation
3. **Comprehensive test coverage** caught integration issues early
4. **Type safety** caught return type mismatch before runtime

### What Could Be Improved
1. **MCP SDK documentation** - Had to discover handler access pattern through experimentation
2. **Test iteration** - Several attempts needed to find correct MCP request type usage

### Knowledge Gained
- MCP SDK uses request type classes as dictionary keys for handler dispatch
- Server responses wrapped in `ServerResult` with `.root` accessor
- JSON-RPC protocol requires avoiding print() to stdout in stdio transport

---

## Metadata

**Phase:** 03-mcp-tools
**Plan:** 01
**Type:** execute
**Status:** ✅ Complete
**Duration:** ~10 minutes
**Commits:** 3 (a024388, be03bd4, c6973ce)
**Tests Added:** 12 (396 lines)
**Files Modified:** 4
**Files Created:** 1
