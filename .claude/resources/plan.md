# Knowledge MCP — Implementation Plan

> **Document ID**: KMCP-PLAN
> **Version**: 0.1.0
> **Status**: Draft
> **Source Spec**: knowledge-mcp-a-spec.md (KMCP-A-SPEC v0.1.0)
> **Created**: 2026-01-15

---

## 1. Plan Overview

### 1.1 Purpose

This plan defines the implementation approach for Knowledge MCP based on the A-Specification (KMCP-A-SPEC). It organizes work into phases, identifies architectural decisions, and provides guidance for task generation.

### 1.2 Current State Analysis

| Component            | Status      | Files                     | Notes                                                                             |
|----------------------|-------------|---------------------------|-----------------------------------------------------------------------------------|
| Package structure    | ✅ Exists    | `src/knowledge_mcp/`      | Directory scaffold in place                                                       |
| KnowledgeChunk model | ✅ Complete  | `models/chunk.py`         | Matches A-REQ-DATA-001                                                            |
| KnowledgeConfig      | ✅ Complete  | `utils/config.py`         | Matches A-REQ-MAINT-002                                                           |
| QdrantStore          | ⚠️ Refactor | `store/qdrant_store.py`   | (1) Add BaseStore inheritance, (2) Update response format, (3) Add error handling |
| MCP Server           | ⚠️ BLOCKER  | `server.py`               | Import in __init__.py breaks package until created                                |
| Ingestors            | ❌ Missing   | `ingest/*.py`             | Directory exists, no files                                                        |
| Chunkers             | ❌ Missing   | `chunk/*.py`              | Directory exists, no files                                                        |
| Embedder             | ❌ Missing   | `embed/*.py`              | Directory exists, no files                                                        |
| Search               | ❌ Missing   | `search/*.py`             | Hybrid search logic needed                                                        |
| CLI                  | ❌ Missing   | `cli/*.py`                | Both commands needed                                                              |
| ChromaDB Store       | ❌ Missing   | `store/chromadb_store.py` | Fallback backend                                                                  |

### 1.3 Requirements Coverage

| Category        | Count  | Must Have  | Should Have  |
|-----------------|--------|------------|--------------|
| MCP Tools       | 6      | 5          | 1            |
| Ingestion       | 6      | 5          | 1            |
| Search          | 3      | 3          | 0            |
| CLI             | 2      | 2          | 0            |
| Data Model      | 5      | 5          | 0            |
| Interface       | 4      | 4          | 0            |
| Performance     | 3      | 1          | 2            |
| Reliability     | 3      | 3          | 0            |
| Maintainability | 2      | 2          | 0            |
| Testability     | 3      | 3          | 0            |
| Configuration   | 1      | 1          | 0            |
| **Total**       | **37** | **33**     | **4**        |

---

## 2. Architecture Decisions

### AD-001: MCP Server Framework

**Decision:** Use the `mcp` Python SDK directly with FastMCP pattern.

**Rationale:**
- Official SDK provides stdio transport out of the box
- FastMCP pattern simplifies tool registration
- Matches MCP specification requirements (A-REQ-IF-001)

**Implementation:**
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
```

### AD-002: Vector Store Abstraction

**Decision:** Implement `BaseStore` abstract class with Qdrant and ChromaDB implementations.

**Rationale:**
- A-REQ-IF-003 requires two backends
- Common interface enables backend switching via config
- Existing QdrantStore already follows this pattern

**Interface:**
```python
class BaseStore(ABC):
    @abstractmethod
    def add_chunks(self, chunks: list[KnowledgeChunk]) -> int: ...

    @abstractmethod
    def search(self, query_embedding, n_results, filter_dict, score_threshold) -> list[dict]: ...

    @abstractmethod
    def get_stats(self) -> dict: ...
```

**Implementation Notes:**
- [CREATE] `store/base.py` with BaseStore ABC
- [REFACTOR] `qdrant_store.py` to inherit from BaseStore (preserve existing public API: `search()`, `add_chunks()`, `get_stats()`)
- [CREATE] `chromadb_store.py` with same interface

### AD-003: Ingestor Strategy Pattern

**Decision:** Use strategy pattern for format-specific ingestors with common interface.

**Rationale:**
- A-REQ-INGEST-001 specifies PDF, DOCX, Markdown
- Each format requires different parsing libraries
- Common interface enables pipeline orchestration

**Libraries:**
- PDF: `pdfplumber` (structure extraction) + `pymupdf` (fallback)
- DOCX: `python-docx`
- Markdown: `markdown-it-py` with frontmatter support

### AD-004: Hybrid Search Implementation

**Decision:** Implement RRF fusion in the search layer, not vector store.

**Rationale:**
- A-REQ-SEARCH-002 specifies RRF with k=60
- Qdrant has native hybrid, ChromaDB doesn't
- Application-level fusion ensures consistent behavior across backends

**Algorithm:**
```
RRF_score(doc) = Σ 1 / (k + rank_i(doc))
where k = 60, i ∈ {semantic, keyword}
```

**Implementation Notes:**
- Use Qdrant native hybrid search for Qdrant backend (already configured)
- [CREATE] `search/hybrid.py` with application-level RRF for ChromaDB parity
- RRF formula: `score(d) = Σ 1/(60 + rank_i(d))` where i ∈ {semantic, keyword}
- Unit test with known ranks to verify formula correctness

### AD-005: Error Handling Pattern

**Decision:** Use custom exception hierarchy with structured error responses.

**Rationale:**
- A-REQ-REL-001 specifies error schema
- A-REQ-DATA-004 defines error codes
- Consistent exception handling across all modules

**Hierarchy:**
```
KnowledgeMCPError
├── ConfigurationError (config_error)
├── ConnectionError (connection_error)
├── TimeoutError (timeout_error)
├── AuthenticationError (auth_error)
├── NotFoundError (not_found)
├── ValidationError (invalid_input)
├── RateLimitError (rate_limited)
└── InternalError (internal_error)
```

### AD-006: Retry Strategy

**Decision:** Use `tenacity` library for retry logic.

**Rationale:**
- A-REQ-REL-002 specifies exponential backoff
- `tenacity` provides clean decorator-based retries
- Integrates well with async code

**Configuration:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
)
```

---

## 3. Implementation Phases

### Phase 1: Foundation (Prerequisites)

**Objective:** Establish core infrastructure and fix broken imports.

**Scope:**
- Create missing `__init__.py` files in subdirectories
- Implement `server.py` skeleton (fix import error)
- Add `BaseStore` abstract class
- Add exception hierarchy
- Add structured logging setup

**Requirements Covered:**
- A-REQ-REL-001 (partial — error schema)
- A-REQ-MAINT-001 (logging setup)

**Dependencies:** None

**Verification:**
- `python -m knowledge_mcp` runs without import errors
- Pyright passes with zero errors

---

### Phase 2: Embedding Service

**Objective:** Implement OpenAI embedding integration with retry logic.

**Scope:**
- Create `embed/openai_embedder.py`
- Implement batching (100 texts per batch)
- Add retry logic with exponential backoff
- Add embedding dimension validation

**Requirements Covered:**
- A-REQ-IF-002 (OpenAI API integration)
- A-REQ-REL-002 (retry behavior)

**Dependencies:** Phase 1

**Verification:**
- Unit tests with mocked OpenAI client
- Integration test with live API (manual)

---

### Phase 3: Ingestion Pipeline

**Objective:** Implement document parsing and chunking.

**Scope:**
- Create `ingest/base.py` (BaseIngestor interface)
- Create `ingest/pdf_ingestor.py`
- Create `ingest/docx_ingestor.py`
- Create `ingest/markdown_ingestor.py`
- Create `chunk/hierarchical.py` (structure-aware chunking)
- Implement normative detection (shall/must keywords)
- Implement chunk_type classification

**Requirements Covered:**
- A-REQ-INGEST-001 (format support)
- A-REQ-INGEST-002 (capability matrix)
- A-REQ-INGEST-003 (structure preservation)
- A-REQ-INGEST-004 (metadata extraction)
- A-REQ-INGEST-005 (chunk size constraints)
- A-REQ-DATA-005 (normative detection)
- A-REQ-PERF-003 (memory management)

**Dependencies:** Phase 1, Phase 2

**Verification:**
- Test with sample documents (PDF, DOCX, MD)
- Verify hierarchy extraction (6 levels)
- Verify normative detection accuracy

---

### Phase 4: Vector Store Layer

**Objective:** Complete vector store abstraction and ChromaDB fallback.

**Scope:**
- Create `store/base.py` (BaseStore abstract class)
- Refactor `store/qdrant_store.py` to inherit from BaseStore
- Create `store/chromadb_store.py`
- Add hybrid search weight parameter support
- Implement RRF fusion for hybrid search

**Requirements Covered:**
- A-REQ-IF-003 (vector store backends)
- A-REQ-SEARCH-001 (semantic search)
- A-REQ-SEARCH-002 (hybrid search)
- A-REQ-SEARCH-003 (metadata filtering)
- A-REQ-INGEST-006 (deduplication)

**Dependencies:** Phase 1, Phase 2

**Verification:**
- Unit tests for both backends
- Hybrid search accuracy tests
- Filter operation tests

---

### Phase 5: MCP Server & Tools

**Objective:** Implement complete MCP server with all tools.

**Scope:**
- Complete `server.py` with tool registration
- Implement `knowledge_search` tool (A-REQ-TOOL-001)
- Implement `knowledge_lookup` tool (A-REQ-TOOL-002)
- Implement `knowledge_requirements` tool (A-REQ-TOOL-003)
- Implement `knowledge_keyword_search` tool (A-REQ-TOOL-004)
- Implement `knowledge_stats` tool (A-REQ-TOOL-005)
- Implement `knowledge_health` tool (A-REQ-TOOL-006)
- Implement structured response formatting
- Implement empty result handling with suggestions

**Requirements Covered:**
- A-REQ-TOOL-001 through A-REQ-TOOL-006
- A-REQ-IF-001 (MCP protocol)
- A-REQ-DATA-002 (chunk_type enum)
- A-REQ-DATA-003 (document_type enum)
- A-REQ-DATA-004 (error_code enum)

**Dependencies:** Phase 1, Phase 4

**Verification:**
- Tool schema validation
- Response format validation against spec
- Error response format validation

---

### Phase 6: CLI Interface

**Objective:** Implement CLI commands for ingestion and server.

**Scope:**
- Create `cli/__init__.py`
- Create `cli/ingest.py` (`knowledge-ingest` command)
- Create `cli/server.py` (`knowledge-mcp` command)
- Implement progress indicators
- Implement exit code handling
- Add startup validation

**Requirements Covered:**
- A-REQ-CLI-001 (ingest command)
- A-REQ-CLI-002 (server command)
- A-REQ-REL-003 (startup validation)
- A-REQ-CONFIG-001 (.env file support)

**Dependencies:** Phase 3, Phase 5

**Verification:**
- CLI help text validation
- Exit code testing
- Startup validation testing

---

### Phase 7: Quality & Testing

**Objective:** Achieve coverage thresholds and quality gates.

**Scope:**
- Write unit tests for all modules
- Write integration tests for ingestion pipeline
- Write MCP server integration tests
- Configure pytest with coverage
- Ensure Pyright strict mode passes
- Ensure Ruff linting passes

**Requirements Covered:**
- A-REQ-TEST-001 (coverage thresholds)
- A-REQ-TEST-002 (type checking)
- A-REQ-TEST-003 (linting)

**Dependencies:** Phase 1-6

**Verification:**
- `pytest --cov` shows ≥80% line coverage
- `pyright --strict` shows zero errors
- `ruff check` shows zero errors

---

## 4. Verification Strategy

### 4.1 Unit Testing

**Coverage Thresholds (per testing.md §4.1):**

| Metric            | Minimum | Target |
|-------------------|---------|--------|
| Line Coverage     | 80%     | 90%    |
| Branch Coverage   | 75%     | 85%    |
| Function Coverage | 85%     | 95%    |

**Module Coverage Targets:**

| Module            | Test Focus                      | Line Target |
|-------------------|---------------------------------|-------------|
| `models/chunk.py` | Serialization, defaults         | 95%         |
| `utils/config.py` | Validation, loading             | 90%         |
| `store/*.py`      | CRUD, search, filtering         | 85%         |
| `embed/*.py`      | Batching, retry, error handling | 85%         |
| `ingest/*.py`     | Parsing, metadata extraction    | 80%         |
| `chunk/*.py`      | Size constraints, hierarchy     | 85%         |
| `search/*.py`     | RRF fusion, filtering           | 90%         |
| `server.py`       | Tool dispatch, response format  | 85%         |
| `cli/*.py`        | Argument parsing, exit codes    | 80%         |

**Test Pattern:** All tests MUST use AAA pattern (Arrange-Act-Assert) per testing.md §5.1.

### 4.2 Integration Testing

| Scenario             | Components                             | Validation                           |
|----------------------|----------------------------------------|--------------------------------------|
| Full ingest pipeline | Ingestor → Chunker → Embedder → Store  | Document processed end-to-end        |
| Search with filters  | Server → Store → Response              | Filter operators work correctly      |
| Hybrid search        | Query → Embed → Store → RRF → Response | RRF fusion produces expected ranking |
| Error propagation    | Any → Error → Response                 | Structured error format returned     |

### 4.3 Acceptance Criteria

- [ ] All 33 "Must Have" requirements implemented
- [ ] All 6 MCP tools return valid responses
- [ ] PDF, DOCX, MD ingestion works with sample docs
- [ ] Qdrant and ChromaDB backends both functional
- [ ] CLI commands execute with correct exit codes
- [ ] Coverage ≥80%, Pyright passes, Ruff passes

---

## 5. Notes for Task Generation

### 5.1 Task Ordering Dependencies

```
Phase 1 (Foundation)
    ↓
Phase 2 (Embedding) ←──────────────────┐
    ↓                                  │
Phase 3 (Ingestion) ──→ Phase 4 (Store) ←
    ↓                         ↓
    └────────→ Phase 5 (MCP Server)
                      ↓
              Phase 6 (CLI)
                      ↓
              Phase 7 (Testing)
```

### 5.2 Parallelization Opportunities

- Phase 2 and Phase 4 can proceed in parallel after Phase 1
- Individual ingestors (PDF, DOCX, MD) can be developed in parallel
- Unit tests can be written alongside implementation

### 5.3 Risk Areas

| Risk                                  | Mitigation                           |
|---------------------------------------|--------------------------------------|
| PDF structure extraction unreliable   | Use pdfplumber with pymupdf fallback |
| Large document memory issues          | Stream processing per A-REQ-PERF-003 |
| OpenAI rate limits during batch embed | Implement batch throttling           |
| Qdrant Cloud latency                  | Cache health checks, async queries   |

### 5.4 Open Questions

None — all requirements were clarified during specification refinement.

---

## Appendix: Requirements Mapping

| Requirement      | Phase  | Implementation Notes                     |
|------------------|--------|------------------------------------------|
| A-REQ-TOOL-001   | 5      | Primary search tool with hybrid_weight   |
| A-REQ-TOOL-002   | 5      | Filter for chunk_type=definition         |
| A-REQ-TOOL-003   | 5      | Filter for normative=true + topic search |
| A-REQ-TOOL-004   | 5      | Use Qdrant full-text index               |
| A-REQ-TOOL-005   | 5      | Aggregate stats from store               |
| A-REQ-TOOL-006   | 5      | Ping vector store + OpenAI               |
| A-REQ-INGEST-001 | 3      | Three ingestors                          |
| A-REQ-INGEST-002 | 3      | Capability per ingestor                  |
| A-REQ-INGEST-003 | 3      | Hierarchical chunker                     |
| A-REQ-INGEST-004 | 3      | Metadata in KnowledgeChunk               |
| A-REQ-INGEST-005 | 3      | Chunker configuration                    |
| A-REQ-INGEST-006 | 4      | Hash check in store                      |
| A-REQ-SEARCH-001 | 4      | Dense vector search                      |
| A-REQ-SEARCH-002 | 4      | RRF hybrid search                        |
| A-REQ-SEARCH-003 | 4      | Filter builders                          |
| A-REQ-CLI-001    | 6      | Click-based CLI                          |
| A-REQ-CLI-002    | 6      | Server launcher                          |
| A-REQ-DATA-001   | ✅      | Already in chunk.py                      |
| A-REQ-DATA-002   | 3,5    | Enum definition                          |
| A-REQ-DATA-003   | 3,5    | Enum definition                          |
| A-REQ-DATA-004   | 1      | Exception hierarchy                      |
| A-REQ-DATA-005   | 3      | Normative detector                       |
| A-REQ-IF-001     | 5      | MCP SDK                                  |
| A-REQ-IF-002     | 2      | OpenAI embedder                          |
| A-REQ-IF-003     | 4      | Store abstraction                        |
| A-REQ-IF-004     | 3      | File handling in ingestors               |
| A-REQ-PERF-001   | 4,5    | Query optimization                       |
| A-REQ-PERF-002   | 3      | Batch processing                         |
| A-REQ-PERF-003   | 3      | Streaming ingest                         |
| A-REQ-REL-001    | 1      | Error schema                             |
| A-REQ-REL-002    | 2      | Tenacity retries                         |
| A-REQ-REL-003    | 6      | Startup checks                           |
| A-REQ-MAINT-001  | 1      | Logging setup                            |
| A-REQ-MAINT-002  | ✅      | Already in config.py                     |
| A-REQ-TEST-001   | 7      | pytest-cov                               |
| A-REQ-TEST-002   | 7      | Pyright                                  |
| A-REQ-TEST-003   | 7      | Ruff                                     |
| A-REQ-CONFIG-001 | ✅      | Already in config.py                     |

---

*End of Plan*