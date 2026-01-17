# Knowledge MCP Implementation Plan

> **Document ID**: KMCP-PLAN
> **Version**: 1.0.0
> **Status**: Proposed
> **Created**: 2026-01-16
> **Spec Reference**: KMCP-A-SPEC v0.2.0
> **Requirements**: 37 total (33 Must Have, 4 Should Have)

---

## PLANS Coverage Summary

| Category | Status | Notes |
|----------|--------|-------|
| **P**hases | ✓ Complete | 5 phases defined with clear milestones |
| **L**inkages | ✓ Complete | Dependencies mapped, no circular deps |
| **A**rchitecture | ✓ Complete | 8 ADRs documented |
| **N**otes | ✓ Complete | Task generation guidance per phase |
| **S**cope | ✓ Complete | 37/37 requirements mapped |

---

## 1. Requirements Mapping

### 1.1 Requirements by Phase

| Phase | Requirements Covered | Priority |
|-------|---------------------|----------|
| Phase 1: Foundation | A-REQ-DATA-001 through A-REQ-DATA-005, A-REQ-CONFIG-001, A-REQ-MAINT-002, A-REQ-REL-003 | Must Have |
| Phase 2: Ingestion | A-REQ-INGEST-001 through A-REQ-INGEST-006, A-REQ-CLI-001 | Must Have (5), Should Have (1) |
| Phase 3: Search | A-REQ-SEARCH-001 through A-REQ-SEARCH-003 | Must Have |
| Phase 4: MCP Server | A-REQ-TOOL-001 through A-REQ-TOOL-006, A-REQ-IF-001, A-REQ-CLI-002 | Must Have (7), Should Have (1) |
| Phase 5: Quality | A-REQ-TEST-001 through A-REQ-TEST-003, A-REQ-MAINT-001, A-REQ-REL-001, A-REQ-REL-002, A-REQ-PERF-001 through A-REQ-PERF-003 | Must Have (7), Should Have (3) |

### 1.2 Full Traceability Matrix

| Requirement ID | Category | Phase | ADR | Priority |
|---------------|----------|-------|-----|----------|
| A-REQ-TOOL-001 | MCP Tools | 4 | ADR-002, ADR-005 | Must Have |
| A-REQ-TOOL-002 | MCP Tools | 4 | ADR-002, ADR-006 | Must Have |
| A-REQ-TOOL-003 | MCP Tools | 4 | ADR-002 | Must Have |
| A-REQ-TOOL-004 | MCP Tools | 4 | ADR-002, ADR-005 | Must Have |
| A-REQ-TOOL-005 | MCP Tools | 4 | ADR-002 | Must Have |
| A-REQ-TOOL-006 | MCP Tools | 4 | ADR-002 | Should Have |
| A-REQ-INGEST-001 | Ingestion | 2 | ADR-003 | Must Have |
| A-REQ-INGEST-002 | Ingestion | 2 | ADR-003 | Must Have |
| A-REQ-INGEST-003 | Ingestion | 2 | ADR-004 | Must Have |
| A-REQ-INGEST-004 | Ingestion | 2 | ADR-004 | Must Have |
| A-REQ-INGEST-005 | Ingestion | 2 | ADR-004 | Must Have |
| A-REQ-INGEST-006 | Ingestion | 2 | - | Should Have |
| A-REQ-SEARCH-001 | Search | 3 | ADR-005 | Must Have |
| A-REQ-SEARCH-002 | Search | 3 | ADR-005 | Must Have |
| A-REQ-SEARCH-003 | Search | 3 | ADR-005 | Must Have |
| A-REQ-CLI-001 | CLI | 2 | ADR-007 | Must Have |
| A-REQ-CLI-002 | CLI | 4 | ADR-007 | Must Have |
| A-REQ-DATA-001 | Data Model | 1 | ADR-001 | Must Have |
| A-REQ-DATA-002 | Enumeration | 1 | ADR-001 | Must Have |
| A-REQ-DATA-003 | Enumeration | 1 | ADR-001 | Must Have |
| A-REQ-DATA-004 | Enumeration | 1 | ADR-001 | Must Have |
| A-REQ-DATA-005 | Data Model | 1 | ADR-004 | Must Have |
| A-REQ-IF-001 | Interface | 4 | ADR-002 | Must Have |
| A-REQ-IF-002 | Interface | 1 | ADR-008 | Must Have |
| A-REQ-IF-003 | Interface | 1 | ADR-001 | Must Have |
| A-REQ-IF-004 | Interface | 2 | - | Must Have |
| A-REQ-PERF-001 | Performance | 5 | - | Should Have |
| A-REQ-PERF-002 | Performance | 5 | - | Should Have |
| A-REQ-PERF-003 | Performance | 2 | ADR-003 | Must Have |
| A-REQ-REL-001 | Reliability | 5 | - | Must Have |
| A-REQ-REL-002 | Reliability | 5 | ADR-008 | Must Have |
| A-REQ-REL-003 | Reliability | 1 | - | Must Have |
| A-REQ-MAINT-001 | Maintainability | 5 | - | Must Have |
| A-REQ-MAINT-002 | Maintainability | 1 | - | Must Have |
| A-REQ-TEST-001 | Testability | 5 | - | Must Have |
| A-REQ-TEST-002 | Testability | 5 | - | Must Have |
| A-REQ-TEST-003 | Testability | 5 | - | Must Have |
| A-REQ-CONFIG-001 | Configuration | 1 | - | Must Have |

---

## 2. Implementation Phases

### Phase 1: Foundation Layer

**Objective**: Establish core data models, configuration system, and base abstractions.

**Prerequisites**: None (starting phase)

**Dependencies to Phase 2**: Models, configuration, base store/embedder interfaces

**Requirements Covered**:
- A-REQ-DATA-001: KnowledgeChunk schema
- A-REQ-DATA-002: chunk_type enumeration
- A-REQ-DATA-003: document_type enumeration
- A-REQ-DATA-004: error_code enumeration
- A-REQ-DATA-005: Normative detection
- A-REQ-CONFIG-001: .env file support
- A-REQ-MAINT-002: Environment variable configuration
- A-REQ-REL-003: Startup validation
- A-REQ-IF-002: OpenAI API integration
- A-REQ-IF-003: Vector store backend support

**Implementation Status**:
- [x] KnowledgeChunk model (src/knowledge_mcp/models/chunk.py)
- [x] Configuration system (src/knowledge_mcp/utils/config.py)
- [x] Exception hierarchy (src/knowledge_mcp/exceptions.py)
- [x] Base store interface (src/knowledge_mcp/store/base.py)
- [x] Qdrant store implementation (src/knowledge_mcp/store/qdrant_store.py)
- [x] Base embedder interface (src/knowledge_mcp/embed/base.py)
- [x] OpenAI embedder (src/knowledge_mcp/embed/openai_embedder.py)
- [ ] Enumerations for chunk_type, document_type, error_code
- [ ] ChromaDB fallback store
- [ ] Startup validation with clear error messages

**Task Generation Notes**:
- Update KnowledgeChunk to include all fields from A-REQ-DATA-001
- Add StrEnum classes for all enumerations
- Implement ChromaDB store with fallback logic per CLARIFY-005
- Add validation method to config that reports all errors before failing

---

### Phase 2: Ingestion Pipeline

**Objective**: Build complete document ingestion with format support, chunking, and embedding.

**Prerequisites**: Phase 1 (models, config, embedder, store)

**Dependencies to Phase 3**: Populated vector store with embedded chunks

**Requirements Covered**:
- A-REQ-INGEST-001: Format support (PDF, DOCX, Markdown)
- A-REQ-INGEST-002: Extraction capabilities matrix
- A-REQ-INGEST-003: Structure preservation
- A-REQ-INGEST-004: Metadata extraction
- A-REQ-INGEST-005: Chunk size constraints
- A-REQ-INGEST-006: Content deduplication (Should Have)
- A-REQ-IF-004: File system access
- A-REQ-PERF-003: Memory management
- A-REQ-CLI-001: knowledge-ingest CLI command

**Implementation Status**:
- [ ] PDF ingestor (pymupdf4llm)
- [ ] DOCX ingestor (python-docx)
- [ ] Markdown ingestor
- [ ] Hierarchical chunker
- [ ] Metadata extractor
- [ ] Normative content detector
- [ ] CLI with progress indicator

**Task Generation Notes**:
- Create base Ingestor interface with common extraction logic
- PDF ingestor must handle corrupted/encrypted files per CLARIFY-001
- Implement hierarchical chunker preserving section_hierarchy up to 6 levels (CLARIFY-004)
- Use tiktoken for accurate token counting
- Implement streaming/page-by-page processing for memory management
- CLI must prompt user on errors (Continue/Abort) per spec

---

### Phase 3: Search Engine

**Objective**: Implement semantic, keyword, and hybrid search capabilities.

**Prerequisites**: Phase 2 (populated vector store with embeddings)

**Dependencies to Phase 4**: Search service for MCP tool handlers

**Requirements Covered**:
- A-REQ-SEARCH-001: Semantic search with filtering
- A-REQ-SEARCH-002: Hybrid search with RRF fusion
- A-REQ-SEARCH-003: Metadata filtering

**Implementation Status**:
- [ ] Semantic search service
- [ ] Keyword/BM25 search (Qdrant sparse vectors)
- [ ] Hybrid search with RRF (k=60)
- [ ] Metadata filter builder
- [ ] Similar terms algorithm (CLARIFY-003)

**Task Generation Notes**:
- SemanticSearch class wrapping embedder + store
- HybridSearch combining dense + sparse with configurable weight
- Filter builder supporting equals, in, prefix operators
- Implement Levenshtein distance for fuzzy term matching
- Must handle hybrid fallback gracefully (dense-only with warning)

---

### Phase 4: MCP Server

**Objective**: Implement all MCP tools with proper schemas and error handling.

**Prerequisites**: Phase 3 (search service)

**Dependencies to Phase 5**: Functional server for integration testing

**Requirements Covered**:
- A-REQ-TOOL-001: knowledge_search
- A-REQ-TOOL-002: knowledge_lookup
- A-REQ-TOOL-003: knowledge_requirements
- A-REQ-TOOL-004: knowledge_keyword_search
- A-REQ-TOOL-005: knowledge_stats
- A-REQ-TOOL-006: knowledge_health (Should Have)
- A-REQ-IF-001: MCP protocol implementation
- A-REQ-CLI-002: knowledge-mcp server command

**Implementation Status**:
- [ ] MCP server setup (mcp.Server)
- [ ] Tool: knowledge_search with all parameters
- [ ] Tool: knowledge_lookup with similar terms
- [ ] Tool: knowledge_requirements
- [ ] Tool: knowledge_keyword_search
- [ ] Tool: knowledge_stats
- [ ] Tool: knowledge_health with latency checks
- [ ] Server CLI with transport options

**Task Generation Notes**:
- Use mcp library's tool decorator pattern
- All tools must return structured JSON matching spec schemas
- Empty results must include message and suggestions
- Health check latency threshold configurable (CLARIFY-007)
- Validate all input parameters with Pydantic

---

### Phase 5: Quality & Polish

**Objective**: Achieve coverage targets, performance benchmarks, and production readiness.

**Prerequisites**: Phase 4 (functional MCP server)

**Dependencies**: None (final phase)

**Requirements Covered**:
- A-REQ-TEST-001: 80% line coverage minimum
- A-REQ-TEST-002: Pyright strict mode
- A-REQ-TEST-003: Ruff linting
- A-REQ-MAINT-001: Logging requirements
- A-REQ-REL-001: Structured error responses
- A-REQ-REL-002: Retry behavior
- A-REQ-PERF-001: Query latency targets (Should Have)
- A-REQ-PERF-002: Ingestion throughput (Should Have)

**Implementation Status**:
- [ ] Unit tests for all modules
- [ ] Integration tests for MCP server
- [ ] Structured logging with configurable format
- [ ] Exponential backoff retry wrapper
- [ ] Performance benchmarks

**Task Generation Notes**:
- Write tests in parallel with implementation (TDD where practical)
- Use mocking for external services (OpenAI, Qdrant)
- Logging must support both text and JSON formats
- Retry decorator with configurable attempts and backoff

---

## 3. Architecture Decision Records

### ADR-001: Data Model Design with Pydantic

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

How should we structure the KnowledgeChunk data model to support all spec requirements while maintaining type safety and validation?

#### Decision Drivers

* Type safety per constitution.md (Pyright strict mode)
* Runtime validation for API boundaries
* Serialization for vector store payloads
* Extensibility for future chunk types

#### Considered Options

1. Pydantic BaseModel with strict validation
2. Python dataclasses with manual validation
3. TypedDict for lightweight schema

#### Decision Outcome

**Chosen option**: "Pydantic BaseModel with strict validation", because it provides:
- Automatic JSON schema generation for MCP tools
- Runtime validation with clear error messages
- Seamless serialization/deserialization
- Integration with existing config system

**Consequences**:
* Good, because type hints and runtime checks align
* Good, because JSON schema auto-generated for MCP
* Bad, because slight performance overhead vs dataclasses
* Bad, because Pydantic v2 migration needed if not current

**Confirmation**: All models pass `mypy --strict` and `pyright` with zero errors

#### Traceability

- **Requirements**: A-REQ-DATA-001, A-REQ-DATA-002, A-REQ-DATA-003, A-REQ-DATA-004, A-REQ-IF-003
- **Affects Tasks**: (populated after /tasks)

---

### ADR-002: MCP Server Architecture

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

How should we structure the MCP server to handle 6 tools with different concerns (search, stats, health)?

#### Decision Drivers

* Clean separation of concerns
* Testability with mocked dependencies
* Compliance with MCP SDK patterns
* Error handling consistency

#### Considered Options

1. Monolithic server.py with all tool handlers
2. Tool handlers in separate modules with dependency injection
3. Service layer pattern with tools as thin wrappers

#### Decision Outcome

**Chosen option**: "Service layer pattern with tools as thin wrappers", because:
- Tool handlers become thin, testable wrappers
- Business logic lives in reusable service classes
- Services can be unit tested without MCP protocol overhead
- Follows SOLID principles (single responsibility)

**Consequences**:
* Good, because services are independently testable
* Good, because logic reusable outside MCP context
* Bad, because more files/classes to maintain
* Neutral, because follows established patterns

**Confirmation**: Integration tests verify tool responses match spec schemas

#### Traceability

- **Requirements**: A-REQ-TOOL-001 through A-REQ-TOOL-006, A-REQ-IF-001
- **Affects Tasks**: (populated after /tasks)

---

### ADR-003: Document Parser Selection

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

Which libraries should we use for PDF, DOCX, and Markdown parsing to meet the extraction capability matrix?

#### Decision Drivers

* Extraction quality (tables, structure, metadata)
* Memory efficiency for large documents
* Active maintenance and community support
* Python 3.11+ compatibility

#### Considered Options

1. PDF: pymupdf4llm, PyPDF2, pdfplumber
2. DOCX: python-docx, docx2txt
3. Markdown: markdown-it-py, mistune, commonmark

#### Decision Outcome

**Chosen options**:
- PDF: **pymupdf4llm** - best structure preservation, LLM-optimized output
- DOCX: **python-docx** - full OOXML access, section/style support
- Markdown: **markdown-it-py** - CommonMark compliant, YAML frontmatter via plugin

**Consequences**:
* Good, because pymupdf4llm handles tables and structure well
* Good, because python-docx preserves heading hierarchy
* Bad, because pymupdf4llm is larger dependency
* Neutral, because all libraries are actively maintained

**Confirmation**: Test fixtures validate extraction against expected output

#### Traceability

- **Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-PERF-003
- **Affects Tasks**: (populated after /tasks)

---

### ADR-004: Hierarchical Chunking Strategy

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

How should we chunk documents while preserving section hierarchy and meeting token size constraints?

#### Decision Drivers

* Preserve document structure for context
* Respect token limits (200-800 default)
* Support 6-level section hierarchy (CLARIFY-004)
* Enable parent-child chunk relationships

#### Considered Options

1. Recursive character splitter (LangChain style)
2. Structure-aware hierarchical chunker
3. Semantic chunking with sentence transformers

#### Decision Outcome

**Chosen option**: "Structure-aware hierarchical chunker", because:
- Respects document heading structure
- Keeps normative content intact
- Preserves clause numbers for traceability
- Enables parent_chunk_id relationships

**Consequences**:
* Good, because search results include section context
* Good, because requirements stay in single chunks when possible
* Bad, because more complex than simple splitting
* Neutral, because semantic chunking can be added later

**Confirmation**: Chunked output maintains section_hierarchy for all test documents

#### Traceability

- **Requirements**: A-REQ-INGEST-003, A-REQ-INGEST-004, A-REQ-INGEST-005, A-REQ-DATA-005
- **Affects Tasks**: (populated after /tasks)

---

### ADR-005: Hybrid Search Implementation

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

How should we implement hybrid search combining semantic and keyword matching?

#### Decision Drivers

* Leverage Qdrant's native sparse vector support
* Configurable weighting (default 70/30)
* Graceful fallback when hybrid unavailable
* Reciprocal Rank Fusion (RRF) per spec

#### Considered Options

1. Client-side fusion (separate dense/sparse queries)
2. Qdrant native hybrid search
3. Separate keyword index (Elasticsearch/Meilisearch)

#### Decision Outcome

**Chosen option**: "Qdrant native hybrid search", because:
- Single query round-trip
- Built-in RRF fusion support
- Consistent with Qdrant Cloud deployment
- Reduces infrastructure complexity

**Consequences**:
* Good, because simpler architecture (no separate keyword index)
* Good, because Qdrant handles fusion server-side
* Bad, because ChromaDB fallback is dense-only
* Neutral, because hybrid weight still configurable

**Confirmation**: Hybrid search returns results with RRF scores; fallback logs warning

#### Traceability

- **Requirements**: A-REQ-SEARCH-001, A-REQ-SEARCH-002, A-REQ-SEARCH-003, A-REQ-TOOL-001, A-REQ-TOOL-004
- **Affects Tasks**: (populated after /tasks)

---

### ADR-006: Similar Terms Algorithm

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

How should knowledge_lookup find similar terms when exact match fails (CLARIFY-003)?

#### Decision Drivers

* Handle typos (Levenshtein distance)
* Find semantically related terms
* Limit to 3 suggestions
* Performance on large vocabulary

#### Considered Options

1. Semantic search only (embedding similarity)
2. Fuzzy string matching only (Levenshtein)
3. Hybrid: semantic first, then fuzzy supplement

#### Decision Outcome

**Chosen option**: "Hybrid: semantic first, then fuzzy supplement", because:
- Semantic catches conceptually related terms
- Fuzzy catches typos that semantic might miss
- Combined approach per CLARIFY-003 specification
- Deduplication ensures unique results

**Consequences**:
* Good, because handles both typos and related concepts
* Good, because matches spec algorithm exactly
* Bad, because requires maintaining term index for fuzzy
* Neutral, because 3-result limit keeps it fast

**Confirmation**: Test with known typos returns expected corrections

#### Traceability

- **Requirements**: A-REQ-TOOL-002
- **Affects Tasks**: (populated after /tasks)

---

### ADR-007: CLI Framework Selection

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

Which CLI framework should we use for knowledge-ingest and knowledge-mcp commands?

#### Decision Drivers

* Type hints for arguments
* Progress indicator support
* User prompts (Continue/Abort)
* Async compatibility

#### Considered Options

1. Click - mature, widely used
2. Typer - modern, type-hint based
3. argparse - stdlib, no dependencies

#### Decision Outcome

**Chosen option**: "Typer", because:
- Type hints match Pyright strict mode
- Rich integration for progress bars
- Built on Click (familiar patterns)
- Prompt support for interactive error handling

**Consequences**:
* Good, because type safety extends to CLI
* Good, because Rich progress indicators built-in
* Bad, because adds Typer + Rich dependencies
* Neutral, because Typer is thin wrapper over Click

**Confirmation**: CLI commands have --help generated from type hints

#### Traceability

- **Requirements**: A-REQ-CLI-001, A-REQ-CLI-002
- **Affects Tasks**: (populated after /tasks)

---

### ADR-008: Retry and Error Handling Strategy

**Status**: accepted
**Date**: 2026-01-16
**Decision-makers**: Project team

#### Context and Problem Statement

How should we implement retry logic and error responses across external service calls?

#### Decision Drivers

* Exponential backoff per A-REQ-REL-002
* Structured error responses per A-REQ-REL-001
* Distinguish retryable vs non-retryable errors
* OpenAI-specific handling (CLARIFY-002)

#### Considered Options

1. Custom retry decorator
2. tenacity library
3. httpx built-in retry

#### Decision Outcome

**Chosen option**: "tenacity library", because:
- Battle-tested retry logic
- Configurable backoff strategies
- Exception-based retry conditions
- Async support

**Consequences**:
* Good, because tenacity handles edge cases
* Good, because retry conditions are declarative
* Bad, because adds dependency
* Neutral, because tenacity is lightweight

**Confirmation**: Tests verify retry on 5xx, no retry on 4xx (except 429)

#### Traceability

- **Requirements**: A-REQ-REL-002, A-REQ-IF-002
- **Affects Tasks**: (populated after /tasks)

---

## 4. Verification Strategy

### 4.1 Unit Testing Approach

| Component | Test Focus | Mocking Strategy |
|-----------|-----------|------------------|
| Models | Schema validation, serialization | None (pure functions) |
| Config | Environment loading, validation | Mock os.environ |
| Ingestors | Extraction accuracy | Mock file I/O |
| Chunkers | Token counts, hierarchy | Real tokenizer |
| Embedders | API calls, batching | Mock OpenAI client |
| Stores | CRUD operations, search | Mock Qdrant client |
| Search | Filtering, fusion | Mock store |
| Tools | Parameter validation, response schemas | Mock services |

### 4.2 Integration Testing

| Test | Prerequisites | Validates |
|------|---------------|-----------|
| Ingest pipeline | Sample documents | End-to-end document → chunks |
| MCP server | Populated store | Tool invocation → response |
| Health check | Running services | Connectivity and latency |

### 4.3 Quality Gates

| Gate | Command | Blocking |
|------|---------|----------|
| Type check | `pyright` | Yes |
| Lint | `ruff check src tests` | Yes |
| Format | `ruff format --check src tests` | Yes |
| Unit tests | `pytest tests/unit` | Yes |
| Coverage | `pytest --cov --cov-fail-under=80` | Yes |
| Integration | `pytest tests/integration` | Yes |

---

## 5. Phase Dependencies (Linkages)

```
┌─────────────────┐
│   Phase 1       │
│   Foundation    │
│   (Models,      │
│    Config,      │
│    Store,       │
│    Embedder)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Phase 2       │
│   Ingestion     │
│   (Parsers,     │
│    Chunkers,    │
│    CLI)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Phase 3       │
│   Search        │
│   (Semantic,    │
│    Hybrid,      │
│    Filters)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Phase 4       │
│   MCP Server    │
│   (Tools,       │
│    Protocol,    │
│    Server CLI)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Phase 5       │
│   Quality       │
│   (Tests,       │
│    Logging,     │
│    Performance) │
└─────────────────┘
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4

**Parallel Opportunities**:
- Phase 5 testing can begin as each phase completes
- Logging can be implemented in Phase 1 and enhanced throughout

---

## 6. Open Questions

None currently. All ambiguities resolved via CLARIFY-001 through CLARIFY-007 in spec.

---

## 7. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-16 | Claude | Initial plan generation |

---

*End of Plan Document*