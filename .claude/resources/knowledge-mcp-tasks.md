# Knowledge MCP Implementation Tasks

> **Generated**: 2026-01-16
> **Plan**: plan.md
> **Specification**: knowledge-mcp-a-spec.md

---

## Metadata

- **Total Tasks**: 28
- **Phases**: 6
- **SMART Compliance**: 100%

---

## Phase 1: Document Ingestion

### TASK-001: Create IngestedDocument Data Model

**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @models

**Plan Reference**: Phase 1, ADR-003
**Requirements**: A-REQ-INGEST-004, A-REQ-DATA-001

**Description**: Create the `IngestedDocument` Pydantic model that represents a parsed document before chunking. This model serves as the intermediate representation between format-specific ingestors and the chunking pipeline.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/models/document.py` exists with `IngestedDocument` class
      Verification: `ls src/knowledge_mcp/models/document.py && grep -l "class IngestedDocument" src/knowledge_mcp/models/document.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Model includes fields: `document_id`, `document_title`, `document_type`, `source_path`, `sections` (list), `metadata` (dict)
      Verification: `grep -E "(document_id|document_title|document_type|source_path|sections|metadata)" src/knowledge_mcp/models/document.py | wc -l` returns ≥6
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `IngestedSection` nested model includes: `title`, `level`, `content`, `page_numbers`, `clause_number`, `children`
      Verification: `grep -l "class IngestedSection" src/knowledge_mcp/models/document.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Model exports added to `src/knowledge_mcp/models/__init__.py`
      Verification: `grep "IngestedDocument" src/knowledge_mcp/models/__init__.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Pyright passes with zero errors on new file
      Verification: `poetry run pyright src/knowledge_mcp/models/document.py`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None

---

### TASK-002: Create BaseIngestor Abstract Class

**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @ingest

**Plan Reference**: Phase 1, ADR-003
**Requirements**: A-REQ-INGEST-001, A-REQ-IF-004

**Description**: Create the abstract base class that defines the ingestor interface. All format-specific ingestors (PDF, DOCX, Markdown) will inherit from this class.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/base.py` exists with `BaseIngestor` class
      Verification: `ls src/knowledge_mcp/ingest/base.py && grep -l "class BaseIngestor" src/knowledge_mcp/ingest/base.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Class is abstract with `@abstractmethod` decorators on `ingest()` and `supports_format()` methods
      Verification: `grep -c "@abstractmethod" src/knowledge_mcp/ingest/base.py` returns ≥2
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `ingest()` method signature returns `IngestedDocument`
      Verification: `grep "IngestedDocument" src/knowledge_mcp/ingest/base.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Includes `get_ingestor_for_file()` factory function that selects ingestor by file extension
      Verification: `grep "def get_ingestor_for_file" src/knowledge_mcp/ingest/base.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Google-style docstrings on all public methods
      Verification: `grep -c '"""' src/knowledge_mcp/ingest/base.py` returns ≥4
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-001

---

### TASK-003: Implement PDFIngestor

**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @ingest

**Plan Reference**: Phase 1, ADR-003, ADR-006
**Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-INGEST-003, A-REQ-PERF-003

**Description**: Implement PDF document parsing using pymupdf4llm. Must extract text with structure preservation, page numbers, and section hierarchy. Use generator pattern for memory efficiency.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/pdf_ingestor.py` exists with `PDFIngestor` class extending `BaseIngestor`
      Verification: `grep -l "class PDFIngestor(BaseIngestor)" src/knowledge_mcp/ingest/pdf_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Uses `pymupdf4llm` for structure-aware PDF extraction
      Verification: `grep "pymupdf4llm" src/knowledge_mcp/ingest/pdf_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Extracts section hierarchy up to 6 levels from heading styles
      Verification: Unit test `test_pdf_ingestor_hierarchy` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Tracks page numbers for each section
      Verification: `grep "page_number" src/knowledge_mcp/ingest/pdf_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Detects clause numbers using regex pattern (e.g., "5.3.1.2")
      Verification: `grep -E "re\.(compile|match|search).*clause" src/knowledge_mcp/ingest/pdf_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests exist in `tests/unit/test_ingest/test_pdf_ingestor.py` with ≥5 test cases
      Verification: `grep -c "def test_" tests/unit/test_ingest/test_pdf_ingestor.py` returns ≥5
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-002

---

### TASK-004: Implement DOCXIngestor

**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @ingest

**Plan Reference**: Phase 1, ADR-003
**Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-INGEST-003

**Description**: Implement DOCX document parsing using python-docx. Must extract text with structure preservation from heading styles and paragraph formatting.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/docx_ingestor.py` exists with `DOCXIngestor` class extending `BaseIngestor`
      Verification: `grep -l "class DOCXIngestor(BaseIngestor)" src/knowledge_mcp/ingest/docx_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Uses `python-docx` for OOXML parsing
      Verification: `grep "from docx import" src/knowledge_mcp/ingest/docx_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Extracts section hierarchy from Heading 1-6 styles
      Verification: Unit test `test_docx_ingestor_hierarchy` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Extracts tables as text content
      Verification: `grep -i "table" src/knowledge_mcp/ingest/docx_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests exist in `tests/unit/test_ingest/test_docx_ingestor.py` with ≥4 test cases
      Verification: `grep -c "def test_" tests/unit/test_ingest/test_docx_ingestor.py` returns ≥4
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-002

---

### TASK-005: Implement MarkdownIngestor

**Status**: PENDING
**Priority**: P1
**Phase**: 1
**Group**: @ingest

**Plan Reference**: Phase 1, ADR-003
**Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-INGEST-003

**Description**: Implement Markdown document parsing with YAML frontmatter support. Must extract section hierarchy from ATX headings and metadata from frontmatter.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/ingest/markdown_ingestor.py` exists with `MarkdownIngestor` class extending `BaseIngestor`
      Verification: `grep -l "class MarkdownIngestor(BaseIngestor)" src/knowledge_mcp/ingest/markdown_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Parses YAML frontmatter for document metadata (title, document_type, etc.)
      Verification: `grep -E "(yaml|frontmatter)" src/knowledge_mcp/ingest/markdown_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Extracts section hierarchy from `#` through `######` headings
      Verification: Unit test `test_markdown_ingestor_hierarchy` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Preserves code blocks and tables as content
      Verification: `grep -E "(code|table)" src/knowledge_mcp/ingest/markdown_ingestor.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests exist in `tests/unit/test_ingest/test_markdown_ingestor.py` with ≥4 test cases
      Verification: `grep -c "def test_" tests/unit/test_ingest/test_markdown_ingestor.py` returns ≥4
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-002

---

## Phase 2: Document Chunking

### TASK-006: Create BaseChunker Abstract Class

**Status**: PENDING
**Priority**: P1
**Phase**: 2
**Group**: @chunk

**Plan Reference**: Phase 2, ADR-001
**Requirements**: A-REQ-INGEST-005

**Description**: Create the abstract base class that defines the chunker interface. Chunkers transform `IngestedDocument` into a sequence of `KnowledgeChunk` objects.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/chunk/base.py` exists with `BaseChunker` class
      Verification: `ls src/knowledge_mcp/chunk/base.py && grep -l "class BaseChunker" src/knowledge_mcp/chunk/base.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Abstract method `chunk()` accepts `IngestedDocument` and yields `KnowledgeChunk` objects
      Verification: `grep -E "def chunk.*IngestedDocument" src/knowledge_mcp/chunk/base.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Constructor accepts `chunk_size_min`, `chunk_size_max`, `chunk_overlap` parameters
      Verification: `grep -E "(chunk_size_min|chunk_size_max|chunk_overlap)" src/knowledge_mcp/chunk/base.py | wc -l` returns ≥3
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Includes `count_tokens()` helper method using tiktoken
      Verification: `grep "tiktoken" src/knowledge_mcp/chunk/base.py`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-001

---

### TASK-007: Implement HierarchicalChunker

**Status**: PENDING
**Priority**: P1
**Phase**: 2
**Group**: @chunk

**Plan Reference**: Phase 2, ADR-001
**Requirements**: A-REQ-INGEST-003, A-REQ-INGEST-005, A-REQ-DATA-005

**Description**: Implement structure-aware chunking that respects document hierarchy. Primary split on section boundaries, secondary split on token limits.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/chunk/hierarchical.py` exists with `HierarchicalChunker` class
      Verification: `ls src/knowledge_mcp/chunk/hierarchical.py && grep -l "class HierarchicalChunker" src/knowledge_mcp/chunk/hierarchical.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Preserves section hierarchy in `section_hierarchy` field of output chunks
      Verification: `grep "section_hierarchy" src/knowledge_mcp/chunk/hierarchical.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Sets `parent_chunk_id` for chunks derived from same section
      Verification: `grep "parent_chunk_id" src/knowledge_mcp/chunk/hierarchical.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Chunks respect configured min/max token sizes (default 200-800)
      Verification: Unit test `test_hierarchical_chunk_sizes` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Applies overlap tokens when splitting within sections
      Verification: Unit test `test_hierarchical_overlap` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests in `tests/unit/test_chunk/test_hierarchical.py` with ≥6 test cases
      Verification: `grep -c "def test_" tests/unit/test_chunk/test_hierarchical.py` returns ≥6
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-006

---

### TASK-008: Implement Standards-Aware Chunking Patterns

**Status**: PENDING
**Priority**: P2
**Phase**: 2
**Group**: @chunk

**Plan Reference**: Phase 2, ADR-001
**Requirements**: A-REQ-DATA-002, A-REQ-DATA-005

**Description**: Implement detection and tagging of content types (definition, requirement, guidance, etc.) and normative vs informative classification.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/chunk/standards.py` exists with content type detection functions
      Verification: `ls src/knowledge_mcp/chunk/standards.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `detect_chunk_type()` function returns one of: definition, requirement, recommendation, guidance, example, figure, table, overview, reference, annex
      Verification: `grep -c -E "(definition|requirement|recommendation|guidance|example|figure|table|overview|reference|annex)" src/knowledge_mcp/chunk/standards.py` returns ≥10
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `detect_normative()` function returns True for content containing "shall", "must", "is required to"
      Verification: Unit test `test_detect_normative_keywords` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `detect_normative()` function returns False for "should", "may", "can", "is recommended"
      Verification: Unit test `test_detect_informative_keywords` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests in `tests/unit/test_chunk/test_standards.py` with ≥8 test cases
      Verification: `grep -c "def test_" tests/unit/test_chunk/test_standards.py` returns ≥8
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-006

---

### TASK-009: Implement Content Deduplication

**Status**: PENDING
**Priority**: P2
**Phase**: 2
**Group**: @chunk

**Plan Reference**: Phase 2
**Requirements**: A-REQ-INGEST-006

**Description**: Implement SHA-256 content hashing for chunk deduplication. Store hash as `content_hash` field on KnowledgeChunk.

**Acceptance Criteria**:
- [ ] `KnowledgeChunk.content_hash` field is computed as SHA-256 of `content` field
      Verification: `grep "sha256" src/knowledge_mcp/models/chunk.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Hash computation is automatic in model (via validator or computed field)
      Verification: `grep -E "(validator|computed)" src/knowledge_mcp/models/chunk.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit test verifies identical content produces identical hash
      Verification: `poetry run pytest tests/unit/test_models/ -k "content_hash" -v`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None (modifies existing KnowledgeChunk model)

---

## Phase 3: Search Implementation

### TASK-010: Create Search Module Base Classes

**Status**: PENDING
**Priority**: P1
**Phase**: 3
**Group**: @search

**Plan Reference**: Phase 3, ADR-002
**Requirements**: A-REQ-SEARCH-001

**Description**: Create base search interface and result models for the search module.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/search/__init__.py` exports search classes
      Verification: `ls src/knowledge_mcp/search/__init__.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `SearchResult` dataclass with fields: `chunk_id`, `content`, `score`, `metadata`
      Verification: `grep "class SearchResult" src/knowledge_mcp/search/__init__.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `BaseSearch` abstract class with `search()` method returning `list[SearchResult]`
      Verification: `grep "class BaseSearch" src/knowledge_mcp/search/__init__.py`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None

---

### TASK-011: Implement Semantic Search

**Status**: PENDING
**Priority**: P1
**Phase**: 3
**Group**: @search

**Plan Reference**: Phase 3, ADR-002
**Requirements**: A-REQ-SEARCH-001

**Description**: Implement dense vector semantic search using the existing OpenAIEmbedder and QdrantStore.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/search/semantic_search.py` exists with `SemanticSearch` class
      Verification: `ls src/knowledge_mcp/search/semantic_search.py && grep -l "class SemanticSearch" src/knowledge_mcp/search/semantic_search.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `search()` method embeds query and performs cosine similarity search via store
      Verification: `grep -E "(embed|cosine|similarity)" src/knowledge_mcp/search/semantic_search.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Accepts `n_results` parameter (default 10, max 100)
      Verification: `grep "n_results" src/knowledge_mcp/search/semantic_search.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns results ranked by similarity score (0.0-1.0)
      Verification: Unit test `test_semantic_search_ranking` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests in `tests/unit/test_search/test_semantic_search.py` with ≥4 test cases
      Verification: `grep -c "def test_" tests/unit/test_search/test_semantic_search.py` returns ≥4
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-010

---

### TASK-012: Implement Metadata Filter Builder

**Status**: PENDING
**Priority**: P1
**Phase**: 3
**Group**: @search

**Plan Reference**: Phase 3
**Requirements**: A-REQ-SEARCH-003

**Description**: Implement filter construction for metadata-based query filtering. Support filters on document_id, document_type, chunk_type, normative, and clause_number.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/search/filters.py` exists with `FilterBuilder` class
      Verification: `ls src/knowledge_mcp/search/filters.py && grep -l "class FilterBuilder" src/knowledge_mcp/search/filters.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `equals` operator for all filter fields
      Verification: `grep "equals" src/knowledge_mcp/search/filters.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `in` operator for document_id, document_type, chunk_type
      Verification: `grep -E "in_|_in" src/knowledge_mcp/search/filters.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `prefix` operator for clause_number (e.g., "5.3" matches "5.3.1", "5.3.2")
      Verification: `grep "prefix" src/knowledge_mcp/search/filters.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Generates Qdrant-compatible filter format
      Verification: Unit test `test_filter_builder_qdrant_format` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests in `tests/unit/test_search/test_filters.py` with ≥6 test cases
      Verification: `grep -c "def test_" tests/unit/test_search/test_filters.py` returns ≥6
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-010

---

### TASK-013: Implement Hybrid Search with RRF Fusion

**Status**: PENDING
**Priority**: P1
**Phase**: 3
**Group**: @search

**Plan Reference**: Phase 3, ADR-002
**Requirements**: A-REQ-SEARCH-002

**Description**: Implement hybrid search combining dense vectors with BM25 sparse matching using Reciprocal Rank Fusion (k=60).

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/search/hybrid_search.py` exists with `HybridSearch` class
      Verification: `ls src/knowledge_mcp/search/hybrid_search.py && grep -l "class HybridSearch" src/knowledge_mcp/search/hybrid_search.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Implements RRF fusion formula: `1 / (k + rank)` with k=60
      Verification: `grep -E "k.*60|60.*k|RRF|rrf" src/knowledge_mcp/search/hybrid_search.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Accepts `hybrid_weight` parameter (0.0 = keyword only, 1.0 = semantic only, default 0.7)
      Verification: `grep "hybrid_weight" src/knowledge_mcp/search/hybrid_search.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Falls back to dense-only search with WARNING log when sparse search unavailable
      Verification: `grep -E "(WARNING|warn|fallback)" src/knowledge_mcp/search/hybrid_search.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Unit tests in `tests/unit/test_search/test_hybrid_search.py` with ≥5 test cases
      Verification: `grep -c "def test_" tests/unit/test_search/test_hybrid_search.py` returns ≥5
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-011, TASK-012

---

### TASK-014: Enhance QdrantStore for Sparse Vectors

**Status**: PENDING
**Priority**: P2
**Phase**: 3
**Group**: @store

**Plan Reference**: Phase 3, ADR-002
**Requirements**: A-REQ-SEARCH-002, A-REQ-IF-003

**Description**: Extend QdrantStore to support sparse vector storage and retrieval for hybrid search.

**Acceptance Criteria**:
- [ ] `QdrantStore.upsert()` accepts optional `sparse_vector` parameter
      Verification: `grep "sparse_vector" src/knowledge_mcp/store/qdrant_store.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `QdrantStore.search()` accepts optional `sparse_query` parameter for hybrid search
      Verification: `grep -E "sparse_query|hybrid" src/knowledge_mcp/store/qdrant_store.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Collection creation includes sparse vector configuration when `QDRANT_HYBRID_SEARCH=true`
      Verification: Unit test `test_qdrant_collection_sparse_config` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Existing dense-only functionality remains unchanged when sparse vectors not provided
      Verification: `poetry run pytest tests/unit/test_store/test_qdrant_store.py -v`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-011

---

## Phase 4: MCP Tools Implementation

### TASK-015: Create MCP Response Models

**Status**: PENDING
**Priority**: P1
**Phase**: 4
**Group**: @models

**Plan Reference**: Phase 4, ADR-005
**Requirements**: A-REQ-TOOL-001 through A-REQ-TOOL-006, A-REQ-REL-001

**Description**: Create Pydantic response models matching the exact JSON schemas defined in the specification for all 6 MCP tools.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/models/responses.py` exists
      Verification: `ls src/knowledge_mcp/models/responses.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `SearchResponse` model matches spec §3.1.1 schema (results, total, query, search_type)
      Verification: `grep -E "(results|total|query|search_type)" src/knowledge_mcp/models/responses.py | wc -l` returns ≥4
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `LookupResponse` model matches spec §3.1.2 schema (term, found, definitions)
      Verification: `grep "class LookupResponse" src/knowledge_mcp/models/responses.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `RequirementsResponse` model matches spec §3.1.3 schema
      Verification: `grep "class RequirementsResponse" src/knowledge_mcp/models/responses.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `StatsResponse` model matches spec §3.1.5 schema (knowledge_base, documents, vector_store, embedding)
      Verification: `grep -E "(knowledge_base|documents|vector_store|embedding)" src/knowledge_mcp/models/responses.py | wc -l` returns ≥4
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `HealthResponse` model matches spec §3.1.6 schema (status, checks, timestamp)
      Verification: `grep "class HealthResponse" src/knowledge_mcp/models/responses.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `ErrorResponse` model matches spec §6.2.1 schema (error.code, error.message, error.details, error.recoverable, error.suggestion)
      Verification: `grep "class ErrorResponse" src/knowledge_mcp/models/responses.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] All models generate valid JSON Schema via `.model_json_schema()`
      Verification: Unit test `test_response_models_schema_generation` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None

---

### TASK-016: Implement knowledge_search Tool

**Status**: PENDING
**Priority**: P1
**Phase**: 4
**Group**: @server

**Plan Reference**: Phase 4
**Requirements**: A-REQ-TOOL-001

**Description**: Implement the `knowledge_search` MCP tool handler in server.py with full parameter support.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_search` and complete inputSchema
      Verification: `grep '"knowledge_search"' src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Handler accepts all parameters: query, n_results, document_type, chunk_type, normative_only, use_hybrid, hybrid_weight
      Verification: `grep -E "(query|n_results|document_type|chunk_type|normative_only|use_hybrid|hybrid_weight)" src/knowledge_mcp/server.py | wc -l` returns ≥7
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns `SearchResponse` formatted as JSON text content
      Verification: `grep "SearchResponse" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns empty result response with suggestions when no matches
      Verification: `grep "suggestions" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Validates query length (1-2000 characters) with appropriate error
      Verification: Unit test `test_knowledge_search_query_validation` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-013, TASK-015

---

### TASK-017: Implement knowledge_lookup Tool

**Status**: PENDING
**Priority**: P1
**Phase**: 4
**Group**: @server

**Plan Reference**: Phase 4
**Requirements**: A-REQ-TOOL-002

**Description**: Implement the `knowledge_lookup` MCP tool for term/concept definition retrieval.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_lookup` and inputSchema requiring `term` parameter
      Verification: `grep '"knowledge_lookup"' src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Searches for chunks with `chunk_type: definition` matching the term
      Verification: `grep -E "chunk_type.*definition" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns `LookupResponse` with found=true and definitions array when term exists
      Verification: Unit test `test_knowledge_lookup_found` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns found=false with similar_terms suggestions when term not found
      Verification: Unit test `test_knowledge_lookup_not_found` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-011, TASK-015

---

### TASK-018: Implement knowledge_requirements Tool

**Status**: PENDING
**Priority**: P1
**Phase**: 4
**Group**: @server

**Plan Reference**: Phase 4
**Requirements**: A-REQ-TOOL-003

**Description**: Implement the `knowledge_requirements` MCP tool for finding requirements related to a topic.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_requirements`
      Verification: `grep '"knowledge_requirements"' src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Accepts parameters: topic (required), standard (optional), n_results (optional, default 10)
      Verification: `grep -E "(topic|standard|n_results)" src/knowledge_mcp/server.py | grep requirements`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Filters search to `chunk_type: requirement` and `normative: true`
      Verification: `grep -E "(chunk_type.*requirement|normative.*true)" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns `RequirementsResponse` with requirement_text and requirement_id (clause number)
      Verification: Unit test `test_knowledge_requirements_response` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-011, TASK-015

---

### TASK-019: Implement knowledge_keyword_search Tool

**Status**: PENDING
**Priority**: P1
**Phase**: 4
**Group**: @server

**Plan Reference**: Phase 4
**Requirements**: A-REQ-TOOL-004

**Description**: Implement the `knowledge_keyword_search` MCP tool for full-text keyword matching.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_keyword_search`
      Verification: `grep '"knowledge_keyword_search"' src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Uses sparse-only search (BM25) instead of dense vectors
      Verification: `grep -E "(sparse|keyword|bm25)" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns `SearchResponse` with `search_type: "keyword"`
      Verification: Unit test `test_keyword_search_type` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-013, TASK-015

---

### TASK-020: Implement knowledge_stats Tool

**Status**: PENDING
**Priority**: P1
**Phase**: 4
**Group**: @server

**Plan Reference**: Phase 4
**Requirements**: A-REQ-TOOL-005

**Description**: Implement the `knowledge_stats` MCP tool for knowledge base statistics.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_stats` with no required parameters
      Verification: `grep '"knowledge_stats"' src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns total_chunks, total_documents, total_tokens from vector store
      Verification: `grep -E "(total_chunks|total_documents|total_tokens)" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns per-document breakdown with chunk_count and ingested_at
      Verification: Unit test `test_knowledge_stats_documents` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns vector_store info (backend, status, hybrid_enabled)
      Verification: `grep -E "(backend|hybrid_enabled)" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-015

---

### TASK-021: Implement knowledge_health Tool

**Status**: PENDING
**Priority**: P2
**Phase**: 4
**Group**: @server

**Plan Reference**: Phase 4
**Requirements**: A-REQ-TOOL-006

**Description**: Implement the `knowledge_health` MCP tool for checking external dependency status.

**Acceptance Criteria**:
- [ ] Tool registered with name `knowledge_health` with no required parameters
      Verification: `grep '"knowledge_health"' src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Checks vector_store connectivity and measures latency_ms
      Verification: `grep "latency_ms" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Checks embedding_service (OpenAI) connectivity
      Verification: Unit test `test_knowledge_health_checks` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns overall status: "healthy" (all up), "degraded" (partial), "unhealthy" (all down)
      Verification: `grep -E "(healthy|degraded|unhealthy)" src/knowledge_mcp/server.py | wc -l` returns ≥3
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Includes ISO 8601 timestamp in response
      Verification: `grep -E "(isoformat|ISO.*8601)" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-015

---

### TASK-022: Implement Startup Validation

**Status**: PENDING
**Priority**: P1
**Phase**: 4
**Group**: @server

**Plan Reference**: Phase 4
**Requirements**: A-REQ-REL-003

**Description**: Implement configuration validation at server startup with connectivity checks.

**Acceptance Criteria**:
- [ ] Server validates all required environment variables at startup
      Verification: `grep -E "(validate|required)" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Server tests connectivity to vector store before accepting requests
      Verification: `grep -E "(connect|ping|health)" src/knowledge_mcp/server.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] All validation errors reported before failing (not fail-fast on first error)
      Verification: Unit test `test_startup_validation_collects_all_errors` passes
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Exits with code 3 on configuration error per spec
      Verification: Unit test `test_startup_config_error_exit_code` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None

---

## Phase 5: CLI Implementation

### TASK-023: Create CLI Entry Point with Typer

**Status**: PENDING
**Priority**: P1
**Phase**: 5
**Group**: @cli

**Plan Reference**: Phase 5, ADR-004
**Requirements**: A-REQ-CLI-001, A-REQ-CLI-002

**Description**: Create the main CLI entry point using Typer with subcommands for serve and ingest.

**Acceptance Criteria**:
- [ ] File `src/knowledge_mcp/cli/__init__.py` exists with Typer app
      Verification: `ls src/knowledge_mcp/cli/__init__.py && grep "typer" src/knowledge_mcp/cli/__init__.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] `knowledge-mcp` command registered in pyproject.toml scripts
      Verification: `grep "knowledge-mcp" pyproject.toml`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Running `knowledge-mcp --help` shows available subcommands (serve, ingest)
      Verification: `poetry run knowledge-mcp --help | grep -E "(serve|ingest)"`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: None

---

### TASK-024: Implement Ingest CLI Command

**Status**: PENDING
**Priority**: P1
**Phase**: 5
**Group**: @cli

**Plan Reference**: Phase 5, ADR-004
**Requirements**: A-REQ-CLI-001

**Description**: Implement the `knowledge-mcp ingest` command with all options specified in the spec.

**Acceptance Criteria**:
- [ ] `ingest` subcommand accepts `source` argument (file or directory path)
      Verification: `poetry run knowledge-mcp ingest --help | grep "source"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `--recursive` flag (default true)
      Verification: `poetry run knowledge-mcp ingest --help | grep "recursive"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `--pattern` option for glob filtering (default: `*.pdf,*.docx,*.md`)
      Verification: `poetry run knowledge-mcp ingest --help | grep "pattern"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `--dry-run` flag to preview without processing
      Verification: `poetry run knowledge-mcp ingest --help | grep "dry-run"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `--force` flag to re-ingest matching content hash
      Verification: `poetry run knowledge-mcp ingest --help | grep "force"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Displays Rich progress bar during processing
      Verification: `grep "Progress" src/knowledge_mcp/cli/__init__.py`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns exit code 0 on success, 1 on partial failure, 2 on complete failure, 3 on config error
      Verification: Unit test `test_ingest_exit_codes` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-023, Phase 1 and 2 completion

---

### TASK-025: Implement Serve CLI Command

**Status**: PENDING
**Priority**: P1
**Phase**: 5
**Group**: @cli

**Plan Reference**: Phase 5, ADR-004
**Requirements**: A-REQ-CLI-002

**Description**: Implement the `knowledge-mcp serve` command to start the MCP server.

**Acceptance Criteria**:
- [ ] `serve` subcommand starts the MCP server
      Verification: `poetry run knowledge-mcp serve --help`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `--transport` option with values `stdio` (default) and `sse`
      Verification: `poetry run knowledge-mcp serve --help | grep "transport"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Supports `--log-level` option (default: INFO)
      Verification: `poetry run knowledge-mcp serve --help | grep "log-level"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Returns exit code 0 on clean shutdown, 1 on startup failure
      Verification: Unit test `test_serve_exit_codes` passes
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: TASK-023, TASK-022

---

## Phase 6: Quality Assurance

### TASK-026: Achieve 80% Test Coverage

**Status**: PENDING
**Priority**: P1
**Phase**: 6
**Group**: @qa

**Plan Reference**: Phase 6
**Requirements**: A-REQ-TEST-001

**Description**: Write unit tests to achieve minimum 80% line coverage across all modules.

**Acceptance Criteria**:
- [ ] Line coverage ≥80%
      Verification: `poetry run pytest --cov=src --cov-report=term --cov-fail-under=80`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Branch coverage ≥75%
      Verification: `poetry run pytest --cov=src --cov-branch --cov-report=term | grep "TOTAL" | awk '{print $6}' | grep -E "^[7-9][5-9]|^[8-9][0-9]|^100"`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] All test functions have docstrings describing test purpose
      Verification: `poetry run ruff check tests/ --select D103 --output-format text 2>&1 | grep -c "D103" | xargs test 0 -eq`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: All previous phases

---

### TASK-027: Pass Pyright Strict Mode

**Status**: PENDING
**Priority**: P1
**Phase**: 6
**Group**: @qa

**Plan Reference**: Phase 6
**Requirements**: A-REQ-TEST-002

**Description**: Ensure all code passes Pyright type checking in strict mode with zero errors.

**Acceptance Criteria**:
- [ ] Pyright strict mode passes with zero errors
      Verification: `poetry run pyright src/`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] All public functions have complete type annotations
      Verification: `poetry run pyright --verifytypes knowledge_mcp`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: All previous phases

---

### TASK-028: Pass Ruff Linting

**Status**: PENDING
**Priority**: P1
**Phase**: 6
**Group**: @qa

**Plan Reference**: Phase 6
**Requirements**: A-REQ-TEST-003

**Description**: Ensure all code passes Ruff linting with zero errors.

**Acceptance Criteria**:
- [ ] Ruff check passes with zero errors
      Verification: `poetry run ruff check src/ tests/`
      SMART: S✓ M✓ A✓ R✓ T✓
- [ ] Ruff format check passes (code is formatted)
      Verification: `poetry run ruff format --check src/ tests/`
      SMART: S✓ M✓ A✓ R✓ T✓

**Dependencies**: All previous phases

---

## Task Summary

| Phase              | Tasks  | P1     | P2    | P3    |
|--------------------|--------|--------|-------|-------|
| Phase 1: Ingestion | 5      | 5      | 0     | 0     |
| Phase 2: Chunking  | 4      | 2      | 2     | 0     |
| Phase 3: Search    | 5      | 4      | 1     | 0     |
| Phase 4: MCP Tools | 8      | 7      | 1     | 0     |
| Phase 5: CLI       | 3      | 3      | 0     | 0     |
| Phase 6: QA        | 3      | 3      | 0     | 0     |
| **Total**          | **28** | **24** | **4** | **0** |

---

## Dependency Graph

```
TASK-001 (IngestedDocument)
    │
    ├── TASK-002 (BaseIngestor)
    │   ├── TASK-003 (PDFIngestor)
    │   ├── TASK-004 (DOCXIngestor)
    │   └── TASK-005 (MarkdownIngestor)
    │
    └── TASK-006 (BaseChunker)
        ├── TASK-007 (HierarchicalChunker)
        └── TASK-008 (StandardsPatterns)

TASK-009 (Deduplication) ─── standalone

TASK-010 (SearchBase)
    ├── TASK-011 (SemanticSearch)
    │   ├── TASK-013 (HybridSearch)
    │   ├── TASK-014 (QdrantSparse)
    │   ├── TASK-017 (knowledge_lookup)
    │   └── TASK-018 (knowledge_requirements)
    │
    └── TASK-012 (FilterBuilder)
        └── TASK-013 (HybridSearch)

TASK-015 (ResponseModels)
    ├── TASK-016 (knowledge_search)
    ├── TASK-017 (knowledge_lookup)
    ├── TASK-018 (knowledge_requirements)
    ├── TASK-019 (knowledge_keyword_search)
    ├── TASK-020 (knowledge_stats)
    └── TASK-021 (knowledge_health)

TASK-022 (StartupValidation) ─── standalone

TASK-023 (CLI Entry)
    ├── TASK-024 (Ingest Command)
    └── TASK-025 (Serve Command)

TASK-026, TASK-027, TASK-028 (QA) ─── depend on all
```

---

*End of Tasks*