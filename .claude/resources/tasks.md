# Knowledge MCP — Implementation Tasks

> **Document ID**: KMCP-TASKS
> **Version**: 0.1.0
> **Status**: Generated
> **Source Plan**: plan.md (KMCP-PLAN v0.1.0)
> **Created**: 2026-01-15

---

## Task Summary

| Phase                       | Tasks  | P1     | P2     | P3    |
|-----------------------------|--------|--------|--------|-------|
| Phase 1: Foundation         | 5      | 4      | 1      | 0     |
| Phase 2: Embedding Service  | 4      | 3      | 1      | 0     |
| Phase 3: Ingestion Pipeline | 10     | 6      | 4      | 0     |
| Phase 4: Vector Store Layer | 6      | 5      | 1      | 0     |
| Phase 5: MCP Server & Tools | 9      | 7      | 2      | 0     |
| Phase 6: CLI Interface      | 5      | 4      | 1      | 0     |
| Phase 7: Quality & Testing  | 7      | 4      | 3      | 0     |
| **Total**                   | **46** | **33** | **13** | **0** |

---

## Phase 1: Foundation

**Objective:** Establish core infrastructure and fix broken imports.

**Dependencies:** None

---

### TASK-001: [CREATE] Missing `__init__.py` files

**Status**: ✅ COMPLETE
**Priority**: P1
**Constitution Sections**: python.md §6.1, §2.3
**Memory Files**: python.md
**Plan Reference**: Phase 1, Scope item 1
**Requirements**: A-REQ-MAINT-002 (partial: package structure aspect of maintainability; TASK-005 covers config validation, TASK-004 covers error hierarchy)

**Description**:
[CREATE] `__init__.py` files for all subdirectories in `src/knowledge_mcp/` that currently lack them. Per python.md §6.1, every directory containing Python modules MUST have an `__init__.py`.

**Acceptance Criteria**:
- [x] `src/knowledge_mcp/ingest/__init__.py` exists with package docstring
- [x] `src/knowledge_mcp/chunk/__init__.py` exists with package docstring
- [x] `src/knowledge_mcp/embed/__init__.py` exists with package docstring
- [x] `src/knowledge_mcp/search/__init__.py` exists with package docstring
- [x] `src/knowledge_mcp/cli/__init__.py` exists with package docstring
- [x] Each `__init__.py` includes `__all__` export list (empty initially)
- [x] `python -c "import knowledge_mcp"` runs without error

---

### TASK-002: [CREATE] `server.py` skeleton

**Status**: ✅ COMPLETE
**Priority**: P1
**Constitution Sections**: python.md §3.1, §3.2, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 1, Scope item 2; AD-001
**Requirements**: A-REQ-IF-001 (partial: §5.1 items 1,4 - stdio transport, MCP format; TASK-024 covers tool registration item 3, TASK-032 covers error handling item 5)

**Description**:
[CREATE] `src/knowledge_mcp/server.py` with a minimal MCP server skeleton. This fixes the current import error in `__init__.py`. Use the `mcp` SDK with FastMCP pattern per AD-001.

**Acceptance Criteria**:
- [x] File `src/knowledge_mcp/server.py` exists
- [x] Contains `KnowledgeMCPServer` class with `__init__` and `run` methods
- [x] Uses `mcp.server.Server` for MCP protocol handling
- [x] Includes comprehensive docstrings per python.md §3
- [x] All functions have complete type hints per python.md §4.1
- [x] `python -m knowledge_mcp` executes without import errors
- [x] Pyright passes with zero errors

---

### TASK-003: [CREATE] `BaseStore` abstract class

**Status**: ✅ COMPLETE
**Priority**: P1
**Constitution Sections**: python.md §3.3, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 1, Scope item 3; AD-002
**Requirements**: A-REQ-IF-003 (partial: abstract interface definition; TASK-018 covers Qdrant implementation, TASK-019/TASK-020 cover ChromaDB)

**Description**:
[CREATE] `src/knowledge_mcp/store/base.py` with an abstract base class defining the vector store interface. This enables backend switching between Qdrant and ChromaDB per AD-002.

**Acceptance Criteria**:
- [x] File `src/knowledge_mcp/store/base.py` exists
- [x] Contains `BaseStore(ABC)` with abstract methods:
  - `add_chunks(chunks: list[KnowledgeChunk]) -> int`
  - `search(query_embedding, n_results, filter_dict, score_threshold) -> list[dict]`
  - `get_stats() -> dict`
  - `health_check() -> bool`
- [x] Includes comprehensive docstrings per python.md §3.3
- [x] All methods have complete type hints
- [x] Pyright passes with zero errors

---

### TASK-004: [CREATE] Exception hierarchy

**Status**: ✅ COMPLETE
**Priority**: P1
**Constitution Sections**: python.md §3.2, constitution.md §5
**Memory Files**: python.md, security.md
**Plan Reference**: Phase 1, Scope item 4; AD-005
**Requirements**: A-REQ-REL-001, A-REQ-DATA-004

**Description**:
[CREATE] `src/knowledge_mcp/exceptions.py` with custom exception hierarchy per AD-005. Each exception maps to an error code from A-REQ-DATA-004.

**Acceptance Criteria**:
- [x] File `src/knowledge_mcp/exceptions.py` exists
- [x] Contains base `KnowledgeMCPError(Exception)` class
- [x] Contains all child exceptions per AD-005 hierarchy:
  - `ConfigurationError` (config_error)
  - `ConnectionError` (connection_error)
  - `TimeoutError` (timeout_error)
  - `AuthenticationError` (auth_error)
  - `NotFoundError` (not_found)
  - `ValidationError` (invalid_input)
  - `RateLimitError` (rate_limited)
  - `InternalError` (internal_error)
- [x] Each exception has an `error_code` property
- [x] Each exception has a docstring explaining when to use it
- [x] Pyright passes with zero errors

---

### TASK-005: [CREATE] Structured logging setup

**Status**: ✅ COMPLETE
**Priority**: P2
**Constitution Sections**: security.md §7, constitution.md §2
**Memory Files**: python.md, security.md
**Plan Reference**: Phase 1, Scope item 5
**Requirements**: A-REQ-MAINT-001

**Description**:
[CREATE] `src/knowledge_mcp/utils/logging.py` with logging configuration for structured JSON output (production) and human-readable output (development).

**Acceptance Criteria**:
- [x] File `src/knowledge_mcp/utils/logging.py` exists
- [x] Provides `setup_logging(level, json_format)` function
- [x] Supports log levels: DEBUG, INFO, WARNING, ERROR
- [x] JSON format includes: timestamp, level, message, module, extras
- [x] Never logs sensitive data (API keys, tokens) per security.md §7.2:
  - Unit test verifies `OPENAI_API_KEY` value does not appear in log output
  - Unit test verifies error messages redact credentials to `***REDACTED***`
  - Log output grep for common key patterns returns zero matches
- [x] Configurable via environment variable `LOG_LEVEL`
- [x] Includes docstrings and type hints
- [x] Pyright passes with zero errors

---

## Phase 2: Embedding Service

**Objective:** Implement OpenAI embedding integration with retry logic.

**Dependencies:** Phase 1

---

### TASK-006: [CREATE] Base embedder interface

**Status**: ✅ COMPLETE
**Priority**: P1
**Constitution Sections**: python.md §3.3, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 2; AD-003 (strategy pattern)
**Requirements**: A-REQ-IF-002 (partial: abstract interface definition; TASK-007 covers model/dimensions/batching implementation)

**Description**:
[CREATE] `src/knowledge_mcp/embed/base.py` with an abstract base class for embedding providers. This enables future support for local embeddings.

**Acceptance Criteria**:
- [x] File `src/knowledge_mcp/embed/base.py` exists
- [x] Contains `BaseEmbedder(ABC)` with abstract methods:
  - `embed(text: str) -> list[float]`
  - `embed_batch(texts: list[str]) -> list[list[float]]`
  - `dimensions` property returning embedding size
- [x] Includes comprehensive docstrings (Google-style with examples)
- [x] All methods have complete type hints
- [x] Error messages from implementations must not include API keys or credentials per security.md §7.2 (documented in module docstring)
- [x] Pyright passes with zero errors (verified: 0 errors, 0 warnings)

---

### TASK-007: [CREATE] OpenAI embedder

**Status**: ✅ COMPLETE
**Priority**: P1
**Constitution Sections**: python.md §3.2, security.md §2
**Memory Files**: python.md, security.md
**Plan Reference**: Phase 2, Scope items 1-4; AD-006
**Requirements**: A-REQ-IF-002, A-REQ-REL-002

**Description**:
[CREATE] `src/knowledge_mcp/embed/openai_embedder.py` implementing OpenAI text-embedding-3-small with batching and retry logic per AD-006.

**Acceptance Criteria**:
- [x] File `src/knowledge_mcp/embed/openai_embedder.py` exists
- [x] Implements `BaseEmbedder` interface (inherits from BaseEmbedder)
- [x] Uses `text-embedding-3-small` model (1536 dimensions) - DEFAULT_MODEL and DEFAULT_DIMENSIONS constants
- [x] Implements batching with max 100 texts per batch (MAX_BATCH_SIZE = 100)
- [x] Uses `tenacity` for retry logic per AD-006:
  - 3 attempts maximum (`stop_after_attempt(3)`)
  - Exponential backoff (1s, 2s, 4s) (`wait_exponential(multiplier=1, min=1, max=4)`)
  - Retries on APIConnectionError, APITimeoutError
- [x] Validates embedding dimensions match expected (1536) - checked in both `embed()` and `embed_batch()`
- [x] Raises appropriate exceptions from hierarchy (TASK-004): ValidationError, ConnectionError, TimeoutError, AuthenticationError, RateLimitError
- [x] API key read from config, never logged per security.md §2 - error messages sanitized, docstring documents security
- [x] Includes comprehensive docstrings and type hints (Google-style with examples)
- [x] Pyright passes with zero errors (verified: 0 errors, 0 warnings)

---

### TASK-008: [EXTEND] Embedder package exports

**Status**: ✅ COMPLETE
**Priority**: P1
**Constitution Sections**: python.md §6.1
**Memory Files**: python.md
**Plan Reference**: Phase 2
**Requirements**: A-REQ-IF-002 (partial: public API exports; TASK-006 defines interface, TASK-007 implements model/dimensions/batching)

**Description**:
[EXTEND] `src/knowledge_mcp/embed/__init__.py` to export the embedder classes.

**Acceptance Criteria**:
- [x] `embed/__init__.py` exports `BaseEmbedder` and `OpenAIEmbedder`
- [x] `__all__` list includes exported classes: `["BaseEmbedder", "OpenAIEmbedder"]`
- [x] Can import via `from knowledge_mcp.embed import OpenAIEmbedder` (verified)
- [x] Pyright passes with zero errors (verified: 0 errors, 0 warnings)

---

### TASK-009: [CREATE] Embedder unit tests

**Status**: ✅ COMPLETE
**Priority**: P2
**Constitution Sections**: testing.md §1, §5.1
**Memory Files**: testing.md, python.md
**Plan Reference**: Phase 2, Verification
**Requirements**: A-REQ-TEST-001 (partial: embed/*.py module coverage 85% target; TASK-017, TASK-023, TASK-032, TASK-037 cover other modules)

**Description**:
[CREATE] `tests/unit/test_embed/test_openai_embedder.py` with unit tests for the OpenAI embedder using mocked OpenAI client.

**Acceptance Criteria**:
- [x] File `tests/unit/test_embed/test_openai_embedder.py` exists
- [x] Tests use AAA pattern (Arrange-Act-Assert) per testing.md §5.1
- [x] Covers:
  - Single text embedding
  - Batch embedding (within limit)
  - Batch embedding (exceeds limit, splits)
  - Retry on transient error
  - Failure after max retries
  - Dimension validation
- [x] Uses `unittest.mock.AsyncMock` for OpenAI client
- [x] Uses shared fixtures from `tests/conftest.py` (mock embedder, sample config)
- [x] Achieves ≥85% coverage for `embed/*.py` (100% achieved for openai_embedder.py)
- [x] All tests pass with `pytest` (27 tests passing)

---

## Phase 3: Ingestion Pipeline

**Objective:** Implement document parsing and chunking.

**Dependencies:** Phase 1, Phase 2

---

### TASK-010: [CREATE] Base ingestor interface

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.3, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 3; AD-003
**Requirements**: A-REQ-INGEST-001 (partial: abstract interface definition; TASK-011 covers PDF, TASK-012 covers DOCX, TASK-013 covers Markdown)

**Description**:
[CREATE] `src/knowledge_mcp/ingest/base.py` with abstract base class for document ingestors using strategy pattern per AD-003. Also defines `DocumentSection` dataclass for raw parsed content.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/base.py` exists
- [ ] Contains `BaseIngestor(ABC)` with abstract methods:
  - `ingest(file_path: Path) -> list[DocumentSection]`
  - `supported_extensions` property
- [ ] Contains `DocumentSection` dataclass for raw parsed content
- [ ] Includes comprehensive docstrings
- [ ] All methods have complete type hints
- [ ] Pyright passes with zero errors

---

### TASK-011: [CREATE] PDF ingestor

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2, security.md §6
**Memory Files**: python.md, security.md
**Plan Reference**: Phase 3, Scope item 2; AD-003
**Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-INGEST-003, A-REQ-IF-004

**Description**:
[CREATE] `src/knowledge_mcp/ingest/pdf_ingestor.py` using `pymupdf4llm` (primary) for PDF structure extraction.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/pdf_ingestor.py` exists
- [ ] Implements `BaseIngestor` interface
- [ ] Extracts per A-REQ-INGEST-002:
  - Headings (6 levels)
  - Tables (preserved structure)
  - Lists (ordered/unordered)
  - Figure captions (if available)
  - Page numbers
- [ ] Preserves document hierarchy per A-REQ-INGEST-003
- [ ] Handles file not found, permission errors per security.md §6
- [ ] Error handling per A-REQ-REL-001:
  - Raises `IngestionError` with code `encrypted_document` for password-protected PDFs
  - Raises `IngestionError` with code `corrupted_document` for malformed/unreadable PDFs
  - Raises `IngestionError` with code `file_not_found` for missing files
  - Raises `IngestionError` with code `permission_denied` for inaccessible files
- [ ] Memory-efficient for large documents (streaming)
- [ ] Includes comprehensive docstrings and type hints
- [ ] Pyright passes with zero errors

---

### TASK-012: [CREATE] Implement DOCX ingestor

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2, §4.1, security.md §6
**Memory Files**: python.md, security.md
**Plan Reference**: Phase 3, Scope item 3; AD-003
**Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-INGEST-003, A-REQ-IF-004

**Description**:
[CREATE] `src/knowledge_mcp/ingest/docx_ingestor.py` using `python-docx` for DOCX parsing.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/docx_ingestor.py` exists
- [ ] Implements `BaseIngestor` interface
- [ ] Extracts per A-REQ-INGEST-002:
  - Headings (6 levels via style names)
  - Tables (preserved structure)
  - Lists (ordered/unordered)
- [ ] Preserves document hierarchy per A-REQ-INGEST-003
- [ ] Error handling per A-REQ-REL-001:
  - Raises `IngestionError` with code `unsupported_format` for legacy .doc files
  - Raises `IngestionError` with code `corrupted_document` for malformed DOCX files
  - Raises `IngestionError` with code `file_not_found` for missing files
  - Raises `IngestionError` with code `permission_denied` for inaccessible files
- [ ] All functions have complete type hints per python.md §4.1
- [ ] Includes comprehensive docstrings per python.md §3
- [ ] Pyright passes with zero errors

---

### TASK-013: [CREATE] Implement Markdown ingestor

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2, §4.1, security.md §6
**Memory Files**: python.md, security.md
**Plan Reference**: Phase 3, Scope item 4; AD-003
**Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-INGEST-003, A-REQ-IF-004

**Description**:
[CREATE] `src/knowledge_mcp/ingest/markdown_ingestor.py` with frontmatter support for Markdown parsing.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/markdown_ingestor.py` exists
- [ ] Implements `BaseIngestor` interface
- [ ] Extracts per A-REQ-INGEST-002:
  - Headings (6 levels via `#` markers)
  - Tables (GFM format)
  - Lists (ordered/unordered)
  - Code blocks (fenced)
- [ ] Parses YAML frontmatter for metadata
- [ ] Preserves document hierarchy per A-REQ-INGEST-003
- [ ] Handles file not found, permission errors (raises `IngestionError`)
- [ ] Returns error response per A-REQ-REL-001 on failure
- [ ] All functions have complete type hints per python.md §4.1
- [ ] Includes comprehensive docstrings per python.md §3
- [ ] Pyright passes with zero errors

---

### TASK-014: [CREATE] Hierarchical chunker

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 3, Scope item 5
**Requirements**: A-REQ-INGEST-003, A-REQ-INGEST-005, A-REQ-DATA-001

**Description**:
[CREATE] `src/knowledge_mcp/chunk/hierarchical.py` for structure-aware chunking that preserves document hierarchy.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/chunk/hierarchical.py` exists
- [ ] Takes `DocumentSection` list from ingestors (dataclass defined in `ingest/base.py` per TASK-010)
- [ ] Produces `KnowledgeChunk` objects per A-REQ-DATA-001
- [ ] Respects chunk size constraints per A-REQ-INGEST-005:
  - Min: 100 tokens
  - Max: 512 tokens (configurable)
  - Target: 400 tokens
- [ ] Preserves `section_hierarchy` (list of parent headings)
- [ ] Sets `parent_chunk_id` for hierarchical navigation
- [ ] Chunk splitting rules:
  - Splits at sentence boundaries if resulting chunk is ≥100 tokens
  - Splits mid-sentence only when sentence exceeds max chunk size (512 tokens)
  - Never splits within code blocks or table rows
- [ ] Includes comprehensive docstrings and type hints
- [ ] Pyright passes with zero errors

---

### TASK-015: [CREATE] Implement normative detection

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 3, Scope item 6
**Requirements**: A-REQ-DATA-005

**Description**:
[CREATE] `src/knowledge_mcp/chunk/normative.py` with logic to detect normative language (shall, must, will, should) in chunks.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/chunk/normative.py` exists
- [ ] Provides `detect_normative(text: str) -> bool` function
- [ ] Detects RFC 2119 keywords: SHALL, MUST, WILL, SHOULD (case-insensitive)
- [ ] Ignores keywords in code blocks or quoted text
- [ ] Returns `True` if any normative keyword found
- [ ] All functions have complete type hints per python.md §4.1
- [ ] Includes comprehensive docstrings per python.md §3
- [ ] Pyright passes with zero errors

---

### TASK-016: [CREATE] Implement chunk type classifier

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: python.md §3.2, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 3, Scope item 7
**Requirements**: A-REQ-DATA-002

**Description**:
[CREATE] `src/knowledge_mcp/chunk/classifier.py` with logic to classify chunk types based on content patterns.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/chunk/classifier.py` exists
- [ ] Provides `classify_chunk(content: str, section_title: str) -> ChunkType` function
- [ ] Classifies per A-REQ-DATA-002 enum:
  - `requirement`: Contains "shall", "must" in normative context
  - `definition`: Section title contains "definition", "terminology"
  - `procedure`: Contains step-by-step patterns (1., 2., 3. or a), b), c))
  - `example`: Section title contains "example", "sample"
  - `narrative`: Default for prose content
  - `table`: Content primarily tabular
  - `figure`: Figure reference or caption
- [ ] All functions have complete type hints per python.md §4.1
- [ ] Includes comprehensive docstrings per python.md §3
- [ ] Pyright passes with zero errors

---

### TASK-017A: [CREATE] DocumentType enumeration

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: python.md §3.2, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 3, Scope item 4
**Requirements**: A-REQ-DATA-003

**Description**:
[CREATE] `DocumentType` enumeration in `src/knowledge_mcp/models/document.py` to classify source document types.

**Acceptance Criteria**:
- [ ] `DocumentType` enum exists in `src/knowledge_mcp/models/document.py`
- [ ] Provides enumeration values per A-REQ-DATA-003:
  - `standard`: IEEE, ISO, IEC standards
  - `handbook`: NASA, ESA handbooks
  - `guide`: INCOSE, SEBoK guides
  - `specification`: Technical specifications
  - `report`: Technical reports
  - `other`: Unclassified documents
- [ ] `detect_document_type(metadata: dict) -> DocumentType` function provided
- [ ] All functions have complete type hints per python.md §4.1
- [ ] Includes comprehensive docstrings per python.md §3
- [ ] Pyright passes with zero errors

---

### TASK-017B: [CREATE] Streaming document processor

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: python.md §3.2, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 3, Scope item 8
**Requirements**: A-REQ-PERF-003

**Description**:
[CREATE] Streaming document processor in `src/knowledge_mcp/ingest/streaming.py` to handle large documents without loading entirely into memory.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/streaming.py` exists
- [ ] Provides `StreamingProcessor` class with:
  - `process_pdf_streaming(path: Path, chunk_size: int = 10) -> Iterator[DocumentSection]`
  - `process_docx_streaming(path: Path, chunk_size: int = 10) -> Iterator[DocumentSection]`
- [ ] Memory usage stays under 500MB for documents up to 1000 pages (per A-REQ-PERF-003)
- [ ] Uses generator patterns to yield sections incrementally
- [ ] All functions have complete type hints per python.md §4.1
- [ ] Includes comprehensive docstrings per python.md §3
- [ ] Pyright passes with zero errors

---

### TASK-017: [CREATE] Write ingestion pipeline tests

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: testing.md §1, §3.1, §5.1
**Memory Files**: testing.md, python.md
**Plan Reference**: Phase 3, Verification
**Requirements**: A-REQ-TEST-001 (partial: covers ingest and chunk modules)

**Description**:
[CREATE] Unit tests for ingestors and chunker with sample documents.

**Acceptance Criteria**:
- [ ] Test files exist in `tests/unit/test_ingest/` and `tests/unit/test_chunk/`
- [ ] Sample documents in `tests/fixtures/sample_documents/`:
  - `sample.pdf` (multi-section, tables)
  - `sample.docx` (headings, lists)
  - `sample.md` (frontmatter, code blocks)
- [ ] Tests verify:
  - Hierarchy extraction (6 levels)
  - Table preservation
  - Normative detection accuracy
  - Chunk size constraints
- [ ] Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1
- [ ] Uses `unittest.mock` for mocking external dependencies
- [ ] Uses shared fixtures from `tests/conftest.py` (sample documents, mock ingestors)
- [ ] Achieves ≥80% coverage for `ingest/*.py` and `chunk/*.py`
- [ ] All tests pass with `pytest`

---

## Phase 4: Vector Store Layer

**Objective:** Complete vector store abstraction and ChromaDB fallback.

**Dependencies:** Phase 1, Phase 2

---

### TASK-018: [REFACTOR] QdrantStore to inherit BaseStore

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.3
**Memory Files**: python.md
**Plan Reference**: Phase 4, Scope item 2; AD-002
**Requirements**: A-REQ-IF-003, A-REQ-SEARCH-001

**Description**:
[REFACTOR] `src/knowledge_mcp/store/qdrant_store.py` to inherit from `BaseStore` and implement all abstract methods. Preserves existing public API.

**Acceptance Criteria**:
- [ ] `QdrantStore` inherits from `BaseStore`
- [ ] Implements `health_check()` method (ping cluster)
- [ ] All existing functionality preserved
- [ ] Updated imports in `store/__init__.py`
- [ ] Pyright passes with zero errors
- [ ] Existing tests still pass

---

### TASK-019: [CREATE] ChromaDB store

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2, §3.3
**Memory Files**: python.md
**Plan Reference**: Phase 4, Scope item 3; AD-002
**Requirements**: A-REQ-IF-003

**Description**:
[CREATE] `src/knowledge_mcp/store/chromadb_store.py` as a local fallback vector store using ChromaDB.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/store/chromadb_store.py` exists
- [ ] Implements `BaseStore` interface
- [ ] Uses persistent storage (configurable path)
- [ ] Supports all filter operations per A-REQ-SEARCH-003
- [ ] Implements `health_check()` method
- [ ] Includes comprehensive docstrings and type hints
- [ ] Pyright passes with zero errors

---

### TASK-020: [CREATE] RRF hybrid search

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 4, Scope item 5; AD-004
**Requirements**: A-REQ-SEARCH-002

**Description**:
[CREATE] `src/knowledge_mcp/search/hybrid.py` with Reciprocal Rank Fusion implementation for hybrid search per AD-004.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/search/hybrid.py` exists
- [ ] Implements `rrf_fusion(semantic_results, keyword_results, k=60) -> list[dict]`
- [ ] Algorithm: `RRF_score(doc) = Σ 1 / (k + rank_i(doc))`
- [ ] Supports configurable `hybrid_weight` parameter (0.0-1.0)
- [ ] Weight 0.0 = pure keyword, 1.0 = pure semantic, 0.7 = default blend
- [ ] Returns results sorted by combined RRF score
- [ ] Includes comprehensive docstrings and type hints
- [ ] Pyright passes with zero errors

---

### TASK-021: [EXTEND] Deduplication logic

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 4; Appendix
**Requirements**: A-REQ-INGEST-006

**Description**:
[EXTEND] `BaseStore` and implementations with content hash-based deduplication to prevent duplicate chunks.

**Acceptance Criteria**:
- [ ] `BaseStore` includes `exists_by_hash(content_hash: str) -> bool` method
- [ ] `QdrantStore` implements hash lookup via filter
- [ ] `ChromaDBStore` implements hash lookup
- [ ] `add_chunks()` skips chunks with existing hashes (optional via flag)
- [ ] Returns count of new chunks added (excluding duplicates)
- [ ] Pyright passes with zero errors

---

### TASK-022: [CREATE] Filter builders

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 4
**Requirements**: A-REQ-SEARCH-003

**Description**:
[CREATE] `src/knowledge_mcp/search/filters.py` with helper functions to build metadata filters.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/search/filters.py` exists
- [ ] Provides filter builder functions for:
  - `by_document_type(types: list[str])` → filter dict
  - `by_chunk_type(types: list[str])` → filter dict
  - `by_normative(value: bool)` → filter dict
  - `by_document_id(id: str)` → filter dict
  - `combine_filters(*filters)` → merged filter dict
- [ ] Filters work with both Qdrant and ChromaDB stores
- [ ] Includes comprehensive docstrings and type hints
- [ ] Pyright passes with zero errors

---

### TASK-023: [CREATE] Vector store tests

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: testing.md §1, §5.1
**Memory Files**: testing.md, python.md
**Plan Reference**: Phase 4, Verification
**Requirements**: A-REQ-TEST-001 (partial: store/*.py and search/*.py module coverage 85% target; TASK-009, TASK-017, TASK-032, TASK-037 cover other modules)

**Description**:
[CREATE] Unit tests for both vector store backends with mocked clients.

**Acceptance Criteria**:
- [ ] Test files in `tests/unit/test_store/`
- [ ] Tests for both `QdrantStore` and `ChromaDBStore`
- [ ] Coverage includes:
  - `add_chunks()` with valid data
  - `search()` with various filters
  - `health_check()` success and failure
  - Deduplication behavior
  - RRF fusion accuracy
- [ ] Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1
- [ ] Uses `unittest.mock` for mocking external dependencies
- [ ] Uses shared fixtures from `tests/conftest.py` (mock store clients, sample chunks)
- [ ] Achieves ≥85% coverage for `store/*.py` and `search/*.py`
- [ ] All tests pass with `pytest`

---

## Phase 5: MCP Server & Tools

**Objective:** Implement complete MCP server with all tools.

**Dependencies:** Phase 1, Phase 4

---

### TASK-024: [EXTEND] MCP server implementation

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2, §4.1
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope item 1; AD-001
**Requirements**: A-REQ-IF-001

**Description**:
[EXTEND] `src/knowledge_mcp/server.py` (created in TASK-002) with full MCP protocol support, tool registration, and stdio transport.

**Acceptance Criteria**:
- [ ] Uses `mcp.server.Server` with stdio transport
- [ ] Implements `list_tools()` handler returning all 6 tools
- [ ] Implements `call_tool()` handler dispatching to tool implementations
- [ ] Proper async handling for all tool calls
- [ ] Graceful shutdown on SIGINT/SIGTERM
- [ ] Error responses sanitize sensitive config values per security.md §7.2:
  - API keys replaced with `***REDACTED***` in error messages
  - Connection strings sanitize credentials
- [ ] Logs do not contain API keys or credentials per security.md §7.2
- [ ] Includes comprehensive docstrings and type hints
- [ ] Pyright passes with zero errors

---

### TASK-025: [CREATE] `knowledge_search` tool

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope item 2
**Requirements**: A-REQ-TOOL-001

**Description**:
[CREATE] The primary search tool with hybrid search support.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_search`
- [ ] Input schema per A-REQ-TOOL-001:
  - `query` (required): Search query text
  - `n_results` (optional, default 5): Number of results
  - `hybrid_weight` (optional, default 0.7): Semantic vs keyword weight
  - `filter` (optional): Metadata filter object
- [ ] Returns structured response per A-REQ-DATA-001 format
- [ ] Empty results include suggestions per spec
- [ ] Errors return structured error format per A-REQ-REL-001
- [ ] Error handling for service unavailability:
  - Returns error code `connection_error` if vector store unreachable after 3 retries
  - Returns error code `timeout_error` if query exceeds 5 second timeout
- [ ] Pyright passes with zero errors

---

### TASK-026: [CREATE] `knowledge_lookup` tool

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope item 3
**Requirements**: A-REQ-TOOL-002

**Description**:
[CREATE] The definition lookup tool that filters for `chunk_type=definition`.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_lookup`
- [ ] Input schema per A-REQ-TOOL-002:
  - `term` (required): Term to look up
  - `n_results` (optional, default 3): Number of definitions
- [ ] Automatically applies `chunk_type: definition` filter
- [ ] Returns structured response with definition chunks
- [ ] Error handling for service unavailability:
  - Returns error code `connection_error` if vector store unreachable after 3 retries
  - Returns error code `timeout_error` if query exceeds 5 second timeout
- [ ] Pyright passes with zero errors

---

### TASK-027: [CREATE] `knowledge_requirements` tool

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope item 4
**Requirements**: A-REQ-TOOL-003

**Description**:
[CREATE] The requirements search tool that filters for normative content.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_requirements`
- [ ] Input schema per A-REQ-TOOL-003:
  - `topic` (required): Topic to search requirements for
  - `document_type` (optional): Filter by document type
  - `n_results` (optional, default 10): Number of results
- [ ] Automatically applies `normative: true` filter
- [ ] Returns structured response with requirement chunks
- [ ] Error handling for service unavailability:
  - Returns error code `connection_error` if vector store unreachable after 3 retries
  - Returns error code `timeout_error` if query exceeds 5 second timeout
- [ ] Pyright passes with zero errors

---

### TASK-028: [CREATE] `knowledge_keyword_search` tool

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope item 5
**Requirements**: A-REQ-TOOL-004

**Description**:
[CREATE] Keyword-only search tool using Qdrant's full-text index.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_keyword_search`
- [ ] Input schema per A-REQ-TOOL-004:
  - `keywords` (required): Keywords to search
  - `n_results` (optional, default 10): Number of results
  - `filter` (optional): Metadata filter
- [ ] Uses full-text search (not embedding-based)
- [ ] Returns structured response
- [ ] Error handling for service unavailability:
  - Returns error code `connection_error` if vector store unreachable after 3 retries
  - Returns error code `timeout_error` if query exceeds 5 second timeout
- [ ] Pyright passes with zero errors

---

### TASK-029: [CREATE] `knowledge_stats` tool

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope item 6
**Requirements**: A-REQ-TOOL-005

**Description**:
[CREATE] Statistics tool that returns collection metadata.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_stats`
- [ ] No required inputs
- [ ] Returns per A-REQ-TOOL-005:
  - Total chunk count
  - Breakdown by document_type
  - Breakdown by chunk_type
  - Collection configuration
- [ ] Error handling for service unavailability:
  - Returns error code `connection_error` if vector store unreachable after 3 retries
  - Returns error code `timeout_error` if stats query exceeds 5 second timeout
- [ ] Pyright passes with zero errors

---

### TASK-030: [CREATE] `knowledge_health` tool

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope item 7
**Requirements**: A-REQ-TOOL-006

**Description**:
[CREATE] Health check tool that pings vector store and OpenAI.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_health`
- [ ] No required inputs
- [ ] Returns per A-REQ-TOOL-006:
  - `vector_store`: status, latency_ms
  - `embedding_service`: status, latency_ms
  - `overall_status`: healthy/degraded/unhealthy
- [ ] Timeouts after 5 seconds per service
- [ ] Pyright passes with zero errors

---

### TASK-031: [CREATE] Response formatters

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 5, Scope items 8-9
**Requirements**: A-REQ-DATA-001, A-REQ-REL-001

**Description**:
[CREATE] `src/knowledge_mcp/server/formatters.py` with response formatting utilities.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/server/formatters.py` exists (or in main server.py)
- [ ] Provides `format_search_response(results: list[dict]) -> str`
- [ ] Provides `format_error_response(error: Exception) -> str`
- [ ] Provides `format_empty_response(query: str) -> str` with suggestions
- [ ] All responses are valid JSON
- [ ] Error responses include `error_code` per A-REQ-DATA-004
- [ ] Pyright passes with zero errors

---

### TASK-032: [CREATE] MCP server tests

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: testing.md §1, §3.1
**Memory Files**: testing.md, python.md
**Plan Reference**: Phase 5, Verification
**Requirements**: A-REQ-TEST-001 (partial: server.py module coverage 85% target; TASK-009, TASK-017, TASK-023, TASK-037 cover other modules)

**Description**:
[CREATE] Unit and integration tests for the MCP server and all tools.

**Acceptance Criteria**:
- [ ] Test files in `tests/unit/test_server.py` and `tests/integration/test_mcp_server.py`
- [ ] Unit tests cover:
  - Tool schema validation
  - Response format validation
  - Error response format
- [ ] Integration tests cover:
  - Full tool call flow (mocked store/embedder)
  - Empty result handling
- [ ] Achieves ≥85% coverage for `server.py`
- [ ] All tests pass with `pytest`
- [ ] Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1
- [ ] Uses `unittest.mock` for mocking external dependencies
- [ ] Uses shared fixtures from `tests/conftest.py` (mock MCP client, sample tool inputs)

---

## Phase 6: CLI Interface

**Objective:** Implement CLI commands for ingestion and server.

**Dependencies:** Phase 3, Phase 5

---

### TASK-033: [CREATE] CLI package structure

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §6.1, §6.2
**Memory Files**: python.md
**Plan Reference**: Phase 6, Scope item 1
**Requirements**: A-REQ-CLI-001, A-REQ-CLI-002

**Description**:
[CREATE] CLI package structure with Click-based command framework.

**Acceptance Criteria**:
- [ ] `src/knowledge_mcp/cli/__init__.py` exists with main entry point
- [ ] Uses Click library for command parsing
- [ ] Provides `main()` function as entry point
- [ ] Pyright passes with zero errors

---

### TASK-034: [CREATE] `knowledge-ingest` command

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 6, Scope item 2
**Requirements**: A-REQ-CLI-001

**Description**:
[CREATE] `src/knowledge_mcp/cli/ingest.py` implementing the document ingestion CLI.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/cli/ingest.py` exists
- [ ] Command: `knowledge-ingest --source <path> [options]`
- [ ] Options per A-REQ-CLI-001:
  - `--source` (required): Path to document or directory
  - `--recursive`: Process directories recursively
  - `--dry-run`: Parse without storing
  - `--verbose`: Detailed output
- [ ] Shows progress indicator (Rich library)
- [ ] Reports: files processed, chunks created, errors encountered
- [ ] Exit codes: 0 success, 1 partial failure, 2 complete failure
- [ ] Pyright passes with zero errors

---

### TASK-035: [CREATE] `knowledge-mcp` command

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §3.2
**Memory Files**: python.md
**Plan Reference**: Phase 6, Scope item 3
**Requirements**: A-REQ-CLI-002

**Description**:
[CREATE] `src/knowledge_mcp/cli/server.py` implementing the MCP server launcher.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/cli/server.py` exists
- [ ] Command: `knowledge-mcp [options]`
- [ ] Options per A-REQ-CLI-002:
  - `--config`: Path to config file
  - `--log-level`: Logging verbosity
- [ ] Runs MCP server on stdio transport
- [ ] Graceful shutdown on Ctrl+C
- [ ] Exit codes: 0 clean shutdown, 1 error
- [ ] Pyright passes with zero errors

---

### TASK-036: [CREATE] Startup validation

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: security.md §2, python.md §3.2
**Memory Files**: python.md, security.md
**Plan Reference**: Phase 6, Scope item 6
**Requirements**: A-REQ-REL-003, A-REQ-CONFIG-001

**Description**:
[CREATE] Startup validation to check configuration and connectivity before server starts.

**Acceptance Criteria**:
- [ ] Validates required environment variables per A-REQ-CONFIG-001:
  - `OPENAI_API_KEY`
  - `QDRANT_URL` (if using Qdrant)
  - `QDRANT_API_KEY` (if using Qdrant Cloud)
- [ ] Validates vector store connectivity
- [ ] Validates OpenAI API key (test embedding call)
- [ ] Clear error messages if validation fails
- [ ] Exit code 2 if validation fails
- [ ] Pyright passes with zero errors

---

### TASK-037: [CREATE] CLI tests

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: testing.md §1
**Memory Files**: testing.md, python.md
**Plan Reference**: Phase 6, Verification
**Requirements**: A-REQ-TEST-001 (partial: cli/*.py module coverage 80% target; TASK-009, TASK-017, TASK-023, TASK-032 cover other modules)

**Description**:
[CREATE] Tests for CLI commands using Click's test runner.

**Acceptance Criteria**:
- [ ] Test file `tests/unit/test_cli/test_commands.py` exists
- [ ] Uses `click.testing.CliRunner`
- [ ] Tests cover:
  - Help text output
  - Invalid arguments handling
  - Startup validation (mocked)
  - Exit code verification per CLI command specifications:
    - `knowledge-ingest`: 0 success, 1 partial failure, 2 complete failure
    - `knowledge-mcp`: 0 clean shutdown, 1 error
    - `knowledge-check`: 0 success, 2 validation failure
- [ ] Achieves ≥80% coverage for `cli/*.py`
- [ ] All tests pass with `pytest`
- [ ] Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1
- [ ] Uses `unittest.mock` for mocking external dependencies
- [ ] Uses shared fixtures from `tests/conftest.py` (mock config, CliRunner setup)

---

## Phase 7: Quality & Testing

**Objective:** Achieve coverage thresholds and quality gates.

**Dependencies:** Phase 1-6

---

### TASK-038: Achieve overall test coverage threshold

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: testing.md §1, constitution.md §2.1
**Memory Files**: testing.md
**Plan Reference**: Phase 7, Scope items 1-3
**Requirements**: A-REQ-TEST-001

**Description**:
Ensure all modules meet the 80% line coverage minimum threshold.

**Acceptance Criteria**:
- [ ] `pytest --cov=src --cov-branch --cov-fail-under=80` passes
- [ ] Line coverage ≥80% (target 90%)
- [ ] Branch coverage ≥75% (target 85%)
- [ ] Function coverage ≥85% (target 95%)
- [ ] `pytest-cov` configured with `--cov-branch` flag in `pyproject.toml`
- [ ] No critical paths uncovered

---

### TASK-039: [CREATE] Integration tests

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: testing.md §3.1
**Memory Files**: testing.md, python.md
**Plan Reference**: Phase 7, Scope item 2; Plan §4.2
**Requirements**: A-REQ-TEST-001

**Description**:
[CREATE] Integration tests for the complete ingestion pipeline and search flow.

**Acceptance Criteria**:
- [ ] `tests/integration/test_ingest_pipeline.py` exists
- [ ] Tests full flow: Ingestor → Chunker → Embedder → Store
- [ ] Uses sample documents from fixtures
- [ ] `tests/integration/test_search_flow.py` exists
- [ ] Tests: Query → Embed → Search → Format
- [ ] All integration tests pass with `pytest`
- [ ] Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1
- [ ] Uses `unittest.mock` for mocking external dependencies
- [ ] Uses shared fixtures from `tests/conftest.py` (sample documents, mock stores)

---

### TASK-040: Ensure Pyright strict mode passes

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §4.2, constitution.md §2.3
**Memory Files**: python.md
**Plan Reference**: Phase 7, Scope item 5
**Requirements**: A-REQ-TEST-002

**Description**:
Verify all code passes Pyright in strict mode with zero errors.

**Acceptance Criteria**:
- [ ] `pyproject.toml` has Pyright configured per python.md §4.2
- [ ] `poetry run pyright` shows zero errors
- [ ] No `# type: ignore` comments (or documented exceptions)
- [ ] All public APIs have complete type annotations

---

### TASK-041: Ensure Ruff linting passes

**Status**: PENDING
**Priority**: P1
**Constitution Sections**: python.md §5.1
**Memory Files**: python.md
**Plan Reference**: Phase 7, Scope item 6
**Requirements**: A-REQ-TEST-003

**Description**:
Verify all code passes Ruff linting with zero errors.

**Acceptance Criteria**:
- [ ] `pyproject.toml` has Ruff configured per python.md §5.1
- [ ] `poetry run ruff check src tests` shows zero errors
- [ ] `poetry run ruff format --check src tests` shows no changes needed
- [ ] All docstrings follow Google style (pydocstyle)

---

### TASK-042: [CREATE] CI/CD workflow

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: git-cicd.md §4
**Memory Files**: git-cicd.md
**Plan Reference**: Phase 7
**Requirements**: A-REQ-TEST-001, A-REQ-TEST-002, A-REQ-TEST-003

**Description**:
Create GitHub Actions workflow for automated testing on push/PR.

**Acceptance Criteria**:
- [ ] `.github/workflows/ci.yml` exists
- [ ] Runs on push to main/develop and all PRs
- [ ] Jobs:
  - Lint (ruff check, ruff format --check)
  - Type check (pyright)
  - Test (pytest with coverage)
- [ ] Fails if any quality gate not met
- [ ] Uploads coverage report to Codecov (optional)

---

### TASK-043: [CREATE/UPDATE] Documentation

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: documentation.md, constitution.md §8
**Memory Files**: documentation.md
**Plan Reference**: Phase 7
**Requirements**: A-REQ-MAINT-001

**Description**:
[UPDATE] README and [CREATE] essential documentation.

**Acceptance Criteria**:
- [ ] `README.md` includes:
  - Project overview
  - Installation instructions
  - Configuration (.env setup)
  - Quick start (ingest + query)
  - Available MCP tools
- [ ] `docs/how-to/ingest-documents.md` created (Diátaxis How-To)
- [ ] `docs/reference/tools.md` created with tool schemas
- [ ] All public APIs have docstrings per python.md §3

---

### TASK-044: [CREATE] Performance benchmark tests

**Status**: PENDING
**Priority**: P2
**Constitution Sections**: testing.md §1, §3.1
**Memory Files**: testing.md, python.md
**Plan Reference**: Phase 7, Performance validation
**Requirements**: A-REQ-PERF-001, A-REQ-PERF-002

**Description**:
[CREATE] Performance benchmark tests to validate latency and throughput requirements.

**Acceptance Criteria**:
- [ ] File `tests/performance/test_benchmarks.py` exists
- [ ] Benchmark tests for search latency per A-REQ-PERF-001:
  - p95 search response < 500ms
  - p99 search response < 1000ms
- [ ] Benchmark tests for ingestion throughput per A-REQ-PERF-002:
  - Ingestion rate ≥ 10 documents/minute (typical 20-page PDFs)
  - Embedding batch throughput ≥ 100 chunks/minute
- [ ] Uses `pytest-benchmark` for timing measurements
- [ ] Reports percentile latencies (p50, p95, p99)
- [ ] Tests run against mocked backends for reproducibility
- [ ] Uses shared fixtures from `tests/conftest.py` (mock backends, timing helpers)
- [ ] All tests pass with `pytest tests/performance/`

---

## Appendix: Task Dependencies

```
TASK-001 ──┬── TASK-002 ──┬── TASK-024 ── TASK-025 ── TASK-026 ─┐
           │              │                                     │
           ├── TASK-003 ──┼── TASK-018 ── TASK-019              │
           │              │                                     │
           ├── TASK-004 ──┼── TASK-007                          │
           │              │                                     │
           └── TASK-005   └── TASK-006 ── TASK-007 ── TASK-008  │
                                                                │
TASK-010 ──┬── TASK-011 ──┬── TASK-014 ── TASK-015 ── TASK-016  │
           │              │                                     │
           ├── TASK-012 ──┤                                     │
           │              │                                     │
           └── TASK-013 ──┘                                     │
                                                                │
TASK-018 ──┬── TASK-019 ──┬── TASK-020                          │
           │              │                                     │
           └── TASK-021 ──┴── TASK-022                          │
                                                                │
TASK-024 ──┬── TASK-025 ── TASK-026 ── TASK-027 ── TASK-028 ────┤
           │                                                    │
           ├── TASK-029 ── TASK-030                             │
           │                                                    │
           └── TASK-031 ── TASK-032                             │
                                                                │
TASK-033 ──┬── TASK-034 ── TASK-036                             │
           │                                                    │
           └── TASK-035 ── TASK-036                             │
                                                                │
TASK-038 ←─┴────────────────────────────────────────────────────┘
           │
           ├── TASK-039
           │
           ├── TASK-040
           │
           ├── TASK-041
           │
           ├── TASK-042
           │
           └── TASK-043
```

---

## Revision History

| Version  | Date       | Author     | Changes                 |
|----------|------------|------------|-------------------------|
| 0.1.0    | 2026-01-15 | D. Dunnock | Initial task generation |

---

*End of Tasks*