# Knowledge MCP Implementation Plan

> **Version**: 1.0.0
> **Source Specification**: knowledge-mcp-a-spec.md
> **Status**: Proposed
> **Created**: 2026-01-16

---

## Executive Summary

This plan implements the Knowledge MCP system - an MCP server for semantic search over technical reference documents. The specification defines 37 requirements (33 Must Have, 4 Should Have).

**Current State**: Foundation layer complete (~2,100 lines)
- Configuration management, data models, embeddings, Qdrant store, logging, error handling

**Remaining Work**: 4 phases covering ingestion, chunking, search, and MCP tools

---

## Requirements Coverage Matrix

| Category                        | Total   | Covered by Existing Code      | To Implement  |
|---------------------------------|---------|-------------------------------|---------------|
| MCP Tools (A-REQ-TOOL-*)        | 6       | 0 (skeleton only)             | 6             |
| Ingestion (A-REQ-INGEST-*)      | 6       | 0                             | 6             |
| Search (A-REQ-SEARCH-*)         | 3       | 1 (partial: A-REQ-SEARCH-001) | 2             |
| CLI (A-REQ-CLI-*)               | 2       | 0                             | 2             |
| Data Model (A-REQ-DATA-*)       | 5       | 3 (A-REQ-DATA-001, 002, 003)  | 2             |
| Interface (A-REQ-IF-*)          | 4       | 2 (A-REQ-IF-002, 003 partial) | 2             |
| Performance (A-REQ-PERF-*)      | 3       | 0                             | 3             |
| Reliability (A-REQ-REL-*)       | 3       | 1 (A-REQ-REL-002)             | 2             |
| Maintainability (A-REQ-MAINT-*) | 2       | 2 (complete)                  | 0             |
| Testability (A-REQ-TEST-*)      | 3       | 0 (infrastructure only)       | 3             |
| Configuration (A-REQ-CONFIG-*)  | 1       | 1 (complete)                  | 0             |

**Total**: 37 requirements, 10 addressed, 27 to implement

---

## Architecture Decisions

### ADR-001: Document Chunking Strategy

**Status**: proposed
**Date**: 2026-01-16
**Decision-makers**: Development team

#### Context and Problem Statement

The specification requires chunking documents while preserving structure (section hierarchy, clause numbers, normative status). How should we implement chunking to balance semantic coherence with structural fidelity?

#### Decision Drivers

* Must preserve section hierarchy up to 6 levels (A-REQ-INGEST-003)
* Must detect normative vs informative content (A-REQ-DATA-005)
* Must maintain configurable chunk sizes (A-REQ-INGEST-005)
* Should support different document types (standards, handbooks, guides)

#### Considered Options

1. **Hierarchical Chunking** - Split on document structure (headings, sections)
2. **Semantic Chunking** - Split on semantic boundaries using embeddings
3. **Fixed-Size Chunking** - Split at fixed token intervals with overlap
4. **Hybrid Approach** - Structure-first with semantic refinement

#### Decision Outcome

**Chosen option**: "Hybrid Approach", because standards documents have explicit structure that should be preserved, but we need semantic boundaries within large sections.

**Implementation**:
1. Primary split on structural boundaries (headings, clause numbers)
2. Secondary split on semantic boundaries for sections exceeding max_chunk_size
3. Preserve parent context via `section_hierarchy` and `parent_chunk_id`
4. Tag content type (definition, requirement, guidance) during chunking

**Consequences**:
* Good, because preserves document structure critical for citation
* Good, because handles both structured standards and flowing handbooks
* Bad, because more complex implementation than single strategy
* Bad, because requires tuning parameters per document type

#### Traceability

- **Requirements**: A-REQ-INGEST-003, A-REQ-INGEST-005, A-REQ-DATA-005
- **Affects Tasks**: chunk module implementation

---

### ADR-002: Hybrid Search Implementation

**Status**: proposed
**Date**: 2026-01-16
**Decision-makers**: Development team

#### Context and Problem Statement

The specification requires hybrid search combining dense vector search with BM25 sparse matching (A-REQ-SEARCH-002). How should we implement this given that Qdrant Cloud supports hybrid search natively but ChromaDB does not?

#### Decision Drivers

* Must support hybrid search with configurable weights (A-REQ-SEARCH-002)
* Must work with both Qdrant and ChromaDB backends (A-REQ-IF-003)
* Should use RRF fusion with k=60 per specification
* Must fall back gracefully when hybrid unavailable

#### Considered Options

1. **Qdrant Native Hybrid** - Use Qdrant's built-in sparse vectors
2. **Application-Level Hybrid** - Implement sparse search in Python
3. **Dense-Only with Keyword Filter** - Pre-filter using metadata keywords
4. **Dual-Store Hybrid** - Separate dense/sparse indexes

#### Decision Outcome

**Chosen option**: "Qdrant Native Hybrid" with application-level fallback, because Qdrant provides optimized hybrid search, and we can implement a simpler fallback for ChromaDB.

**Implementation**:
1. Use Qdrant sparse vectors with `FastEmbed` BM25 encoder for primary backend
2. For ChromaDB: dense-only search with keyword matching via metadata filter
3. Implement RRF fusion in search module for consistent interface
4. Log warning when falling back to dense-only mode

**Consequences**:
* Good, because Qdrant's native hybrid is highly optimized
* Good, because ChromaDB fallback still provides functional search
* Bad, because ChromaDB users get degraded search quality
* Bad, because requires maintaining two code paths

#### Traceability

- **Requirements**: A-REQ-SEARCH-001, A-REQ-SEARCH-002
- **Affects Tasks**: search module, QdrantStore enhancements

---

### ADR-003: Document Ingestor Architecture

**Status**: proposed
**Date**: 2026-01-16
**Decision-makers**: Development team

#### Context and Problem Statement

The specification requires ingesting PDF, DOCX, and Markdown formats with different capabilities per format (A-REQ-INGEST-001, A-REQ-INGEST-002). How should we structure the ingestor components?

#### Decision Drivers

* Must handle three formats with different parsing capabilities
* Must extract consistent metadata across formats
* Must support page-by-page processing for memory efficiency (A-REQ-PERF-003)
* Should be extensible for future format support

#### Considered Options

1. **Single Monolithic Ingestor** - One class handles all formats
2. **Strategy Pattern** - Pluggable format handlers
3. **Pipeline Pattern** - Separate parse, extract, normalize stages
4. **Hybrid Strategy+Pipeline** - Format strategies feeding common pipeline

#### Decision Outcome

**Chosen option**: "Strategy Pattern" with common base class, because format-specific parsing differs significantly but output format is consistent.

**Implementation**:
```
BaseIngestor (abstract)
├── PDFIngestor (pymupdf4llm)
├── DOCXIngestor (python-docx)
└── MarkdownIngestor (mistune + frontmatter)
```

Each ingestor produces `IngestedDocument` with normalized structure that feeds into the chunking pipeline.

**Consequences**:
* Good, because each format gets optimized parsing
* Good, because easy to add new formats
* Good, because testable in isolation
* Bad, because some code duplication across ingestors

#### Traceability

- **Requirements**: A-REQ-INGEST-001, A-REQ-INGEST-002, A-REQ-INGEST-004
- **Affects Tasks**: ingest module implementation

---

### ADR-004: CLI Architecture

**Status**: proposed
**Date**: 2026-01-16
**Decision-makers**: Development team

#### Context and Problem Statement

The specification requires two CLI commands: `knowledge-ingest` and `knowledge-mcp` (A-REQ-CLI-001, A-REQ-CLI-002). How should we structure the CLI implementation?

#### Decision Drivers

* Must support multiple commands with different options
* Must provide progress indication during ingestion
* Must return specific exit codes per specification
* Should integrate with existing logging configuration

#### Considered Options

1. **argparse** - Standard library, no dependencies
2. **click** - Popular, decorator-based
3. **typer** - Modern, type-hint based (uses click internally)
4. **rich-click** - Click with rich formatting

#### Decision Outcome

**Chosen option**: "typer" with rich progress indicators, because it aligns with the type-hint philosophy of the codebase and provides excellent progress display.

**Implementation**:
- Single CLI entry point with subcommands
- `knowledge-mcp serve` - Start MCP server (renamed from bare `knowledge-mcp`)
- `knowledge-mcp ingest` - Ingest documents (combines with knowledge-ingest)
- Rich progress bars during ingestion
- Structured exit codes per specification

**Consequences**:
* Good, because type hints provide auto-completion and validation
* Good, because rich integration provides excellent UX
* Good, because single entry point simplifies installation
* Bad, because adds typer + rich as dependencies

#### Traceability

- **Requirements**: A-REQ-CLI-001, A-REQ-CLI-002
- **Affects Tasks**: cli module implementation

---

### ADR-005: MCP Tool Response Formatting

**Status**: proposed
**Date**: 2026-01-16
**Decision-makers**: Development team

#### Context and Problem Statement

The specification defines exact JSON response schemas for each MCP tool (§3.1.1-3.1.6). How should we ensure consistent response formatting and error handling?

#### Decision Drivers

* Must match exact schema structure from specification
* Must handle empty results with helpful messages
* Must include error responses in standard format (A-REQ-REL-001)
* Should support response validation during testing

#### Considered Options

1. **Dict Builders** - Functions returning dicts
2. **Pydantic Models** - Typed response models with serialization
3. **TypedDict** - Type hints without runtime overhead
4. **Dataclasses with JSON encoder** - Lightweight typed approach

#### Decision Outcome

**Chosen option**: "Pydantic Models" for all response types, because they provide runtime validation, automatic JSON serialization, and generate JSON schemas for MCP tool definitions.

**Implementation**:
- Response models in `src/knowledge_mcp/models/responses.py`
- Each tool has dedicated response model matching spec schema
- Error responses use `ErrorResponse` model
- Models generate JSON Schema for MCP tool inputSchema

**Consequences**:
* Good, because responses are validated against schema
* Good, because JSON schemas auto-generated for tool definitions
* Good, because consistent serialization
* Bad, because slight runtime overhead for model instantiation

#### Traceability

- **Requirements**: A-REQ-TOOL-001 through A-REQ-TOOL-006, A-REQ-REL-001
- **Affects Tasks**: models module, server tool handlers

---

### ADR-006: Memory Management During Ingestion

**Status**: proposed
**Date**: 2026-01-16
**Decision-makers**: Development team

#### Context and Problem Statement

The specification requires processing documents up to 1000 pages while keeping peak memory under 500MB (A-REQ-PERF-003). How should we manage memory during ingestion?

#### Decision Drivers

* Must process PDFs up to 1000 pages (A-REQ-INGEST-001)
* Must keep peak memory < 500MB (A-REQ-PERF-003)
* Should provide progress indication during processing
* Must handle batch embedding efficiently

#### Considered Options

1. **Load Full Document** - Simple but memory-intensive
2. **Page-by-Page Streaming** - Process one page at a time
3. **Section Batching** - Process document in structural batches
4. **Generator Pipeline** - Lazy evaluation throughout pipeline

#### Decision Outcome

**Chosen option**: "Generator Pipeline" with configurable batch sizes, because it provides memory efficiency with flexibility for different document sizes.

**Implementation**:
1. PDFIngestor yields pages as generators
2. Chunker yields chunks as processed
3. Embedder processes in configurable batches (default: 100)
4. Store upserts in batches to avoid memory buildup
5. Progress callback for UI updates

**Consequences**:
* Good, because constant memory regardless of document size
* Good, because enables progress reporting
* Good, because can tune batch sizes for performance vs memory
* Bad, because generator pipelines are harder to debug
* Bad, because error handling across generators is complex

#### Traceability

- **Requirements**: A-REQ-PERF-003, A-REQ-INGEST-001
- **Affects Tasks**: ingest pipeline, embed batching

---

## Implementation Phases

### Phase 1: Document Ingestion (Foundation)

**Objective**: Parse PDF, DOCX, and Markdown documents with structure preservation.

**Requirements Addressed**:
- A-REQ-INGEST-001 (Format Support)
- A-REQ-INGEST-002 (Capability Matrix)
- A-REQ-INGEST-003 (Structure Preservation)
- A-REQ-INGEST-004 (Metadata Extraction)
- A-REQ-IF-004 (File System Interface)

**Components**:
1. `ingest/base.py` - BaseIngestor abstract class
2. `ingest/pdf_ingestor.py` - PDF parsing with pymupdf4llm
3. `ingest/docx_ingestor.py` - DOCX parsing with python-docx
4. `ingest/markdown_ingestor.py` - Markdown parsing with mistune
5. `models/document.py` - IngestedDocument model

**Dependencies**: None (builds on existing infrastructure)

**Task Notes**:
- PDF ingestor should use pymupdf4llm for structure-aware extraction
- Section hierarchy detection needs regex patterns for clause numbers
- Normative detection based on keyword patterns (shall/must vs should/may)
- Test with sample IEEE/NASA documents

---

### Phase 2: Document Chunking

**Objective**: Implement structure-aware chunking with configurable parameters.

**Requirements Addressed**:
- A-REQ-INGEST-005 (Chunk Size)
- A-REQ-INGEST-006 (Content Deduplication)
- A-REQ-DATA-002 (chunk_type enumeration)
- A-REQ-DATA-005 (Normative Detection)

**Components**:
1. `chunk/base.py` - BaseChunker abstract class
2. `chunk/hierarchical.py` - Structure-aware chunking
3. `chunk/semantic.py` - Semantic boundary detection (optional)
4. `chunk/standards.py` - Standards-specific patterns (clause extraction)

**Dependencies**: Phase 1 (IngestedDocument model)

**Task Notes**:
- Hierarchical chunker is primary implementation
- Token counting via tiktoken (already in dependencies)
- SHA-256 content hashing for deduplication
- Preserve parent_chunk_id for hierarchy navigation

---

### Phase 3: Search Implementation

**Objective**: Implement semantic, keyword, and hybrid search capabilities.

**Requirements Addressed**:
- A-REQ-SEARCH-001 (Semantic Search)
- A-REQ-SEARCH-002 (Hybrid Search)
- A-REQ-SEARCH-003 (Metadata Filtering)

**Components**:
1. `search/semantic_search.py` - Dense vector search
2. `search/hybrid_search.py` - Combined dense + sparse
3. `search/filters.py` - Metadata filter construction
4. QdrantStore enhancements for sparse vectors

**Dependencies**: Existing QdrantStore, OpenAIEmbedder

**Task Notes**:
- Implement RRF fusion with k=60
- Filter builder for metadata queries
- Hybrid weight parameter (0.0-1.0)
- Fallback path for ChromaDB (dense-only)

---

### Phase 4: MCP Tools Implementation

**Objective**: Implement all 6 MCP tools with exact response schemas.

**Requirements Addressed**:
- A-REQ-TOOL-001 (knowledge_search)
- A-REQ-TOOL-002 (knowledge_lookup)
- A-REQ-TOOL-003 (knowledge_requirements)
- A-REQ-TOOL-004 (knowledge_keyword_search)
- A-REQ-TOOL-005 (knowledge_stats)
- A-REQ-TOOL-006 (knowledge_health)
- A-REQ-IF-001 (MCP Protocol)
- A-REQ-REL-001 (Error Response Format)
- A-REQ-REL-003 (Startup Validation)

**Components**:
1. `models/responses.py` - Pydantic response models
2. `server.py` - Complete tool handlers
3. Tool registration with JSON schemas

**Dependencies**: Phase 3 (Search module)

**Task Notes**:
- Response models must match spec schemas exactly
- Empty result handling with suggestions
- Error responses with recovery hints
- Health check with latency measurement

---

### Phase 5: CLI Implementation

**Objective**: Implement CLI commands for ingestion and server operation.

**Requirements Addressed**:
- A-REQ-CLI-001 (Ingest Command)
- A-REQ-CLI-002 (Server Command)

**Components**:
1. `cli/__init__.py` - CLI entry point
2. `cli/ingest.py` - Ingest command implementation
3. `cli/serve.py` - Server command implementation
4. Progress indicators with rich

**Dependencies**: Phases 1-4

**Task Notes**:
- Typer for command definition
- Rich progress bars for ingestion
- Exit codes per specification (0, 1, 2, 3)
- Verbose mode for detailed output

---

### Phase 6: Quality Assurance

**Objective**: Meet test coverage and quality requirements.

**Requirements Addressed**:
- A-REQ-TEST-001 (Coverage Requirements)
- A-REQ-TEST-002 (Type Checking)
- A-REQ-TEST-003 (Linting)
- A-REQ-PERF-001 (Query Latency)
- A-REQ-PERF-002 (Ingestion Throughput)

**Components**:
1. Unit tests for all modules
2. Integration tests for pipelines
3. Performance benchmarks
4. Sample document fixtures

**Dependencies**: All previous phases

**Task Notes**:
- 80% line coverage minimum
- Pyright strict mode (zero errors)
- Ruff linting (zero errors)
- Latency benchmarks against targets

---

## Phase Dependencies

```
Phase 1: Ingestion
    │
    ▼
Phase 2: Chunking
    │
    ▼
Phase 3: Search ──────────────┐
    │                         │
    ▼                         ▼
Phase 4: MCP Tools    Phase 5: CLI
    │                         │
    └─────────┬───────────────┘
              ▼
        Phase 6: QA
```

---

## Verification Strategy

### Unit Testing
- Each component testable in isolation
- Mock external services (OpenAI, Qdrant)
- Use pytest fixtures from conftest.py

### Integration Testing
- End-to-end ingest → embed → search pipeline
- MCP server tool invocation
- CLI command execution

### Performance Testing
- Query latency benchmarks (target: <2s semantic, <1s keyword)
- Ingestion throughput (target: 100 pages in <2 minutes)
- Memory profiling during large document ingestion

---

## Risk Mitigation

| Risk                        | Mitigation                                                   |
|-----------------------------|--------------------------------------------------------------|
| PDF structure varies widely | Test with diverse standards documents; fallback to text-only |
| Qdrant Cloud latency        | Connection pooling; retry logic already implemented          |
| OpenAI rate limits          | Batch embeddings; exponential backoff already implemented    |
| Memory during large ingests | Generator pipeline; batch processing                         |
| ChromaDB hybrid search gap  | Clear documentation; warning in degraded mode                |

---

## Open Questions

None identified. The specification is comprehensive and existing code provides clear patterns.

---

## PLANS Coverage Status

| Category         | Status     | Notes                              |
|------------------|------------|------------------------------------|
| **P**hases       | ✓ Complete | 6 phases with clear objectives     |
| **L**inkages     | ✓ Complete | Dependencies validated, no cycles  |
| **A**rchitecture | ✓ Complete | 6 ADRs covering key decisions      |
| **N**otes        | ✓ Complete | Task generation guidance per phase |
| **S**cope        | ✓ Complete | 37/37 requirements mapped          |

---

*End of Plan*