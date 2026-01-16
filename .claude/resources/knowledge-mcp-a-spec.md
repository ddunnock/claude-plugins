# Knowledge MCP — A-Specification

> **Document ID**: KMCP-A-SPEC
> **Version**: 0.2.0
> **Status**: Clarified
> **Created**: 2026-01-15
> **Last Updated**: 2026-01-16
> **Validated**: 2026-01-15
> **Clarifications**: KMCP-CLARIFY v1.0.0 (7 resolutions)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the requirements for **Knowledge MCP**, a Model Context Protocol (MCP) server that provides semantic search capabilities over technical reference documents. It defines the functional behavior, interfaces, data models, and quality attributes the system must exhibit.

### 1.2 Scope

Knowledge MCP enables Claude Desktop (and other MCP clients) to search, retrieve, and query a curated knowledge base of systems engineering standards and handbooks. The system:

- **Ingests** technical documents (PDF, DOCX, Markdown)
- **Chunks** content while preserving document structure
- **Embeds** chunks using OpenAI embedding models
- **Stores** vectors in Qdrant Cloud (primary) or ChromaDB (fallback)
- **Serves** semantic and keyword search via MCP tools

#### 1.2.1 In Scope

- MCP tool definitions and behavior
- Document ingestion pipeline requirements
- Search and retrieval functionality
- CLI interface for ingestion
- Error handling and resilience
- Configuration and logging

#### 1.2.2 Out of Scope

- Incremental document updates (full re-ingest model for v1)
- Document deletion (handled via full re-ingest)
- Multi-user access control
- Web UI or REST API (MCP only)

### 1.3 Definitions

| Term              | Definition                                                            |
|-------------------|-----------------------------------------------------------------------|
| **Chunk**         | A semantically coherent unit of text extracted from a source document |
| **Dense Vector**  | High-dimensional embedding representing semantic meaning              |
| **Sparse Vector** | Keyword-based representation for lexical matching (BM25)              |
| **Hybrid Search** | Combination of dense and sparse vector search                         |
| **Normative**     | Content containing mandatory requirements (shall/must)                |
| **Informative**   | Advisory or explanatory content (should/may)                          |
| **MCP**           | Model Context Protocol — standard for AI tool integration             |

### 1.4 References

| Document             | Description                                        |
|----------------------|----------------------------------------------------|
| MCP Specification    | https://modelcontextprotocol.io/specification      |
| OpenAI Embeddings    | https://platform.openai.com/docs/guides/embeddings |
| Qdrant Documentation | https://qdrant.tech/documentation/                 |

---

## 2. System Overview

### 2.1 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Desktop                         │
│                            │                                │
│                      [MCP Protocol]                         │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Knowledge MCP                       │  │
│  │                                                       │  │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────────────┐   │  │
│  │   │ Ingest  │───▶│  Chunk  │───▶│      Embed      │   │  │
│  │   └────┬────┘    └─────────┘    └────────┬────────┘   │  │
│  │        │                                 │            │  │
│  │   [File System]                    [OpenAI API]       │  │
│  │                                          │            │  │
│  │   ┌──────────────────────────────────────▼─────────┐  │  │
│  │   │                Vector Store                    │  │  │
│  │   │     ┌──────────┐       ┌───────────────┐       │  │  │
│  │   │     │  Qdrant  │  OR   │   ChromaDB    │       │  │  │
│  │   │     │  Cloud   │       │   (local)     │       │  │  │
│  │   │     └──────────┘       └───────────────┘       │  │  │
│  │   └────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Major Components

| Component           | Responsibility                                            |
|---------------------|-----------------------------------------------------------|
| **MCP Server**      | Tool registration, request dispatch, response formatting  |
| **Ingest Pipeline** | Document parsing, text extraction, metadata capture       |
| **Chunk Engine**    | Structure-aware text segmentation, hierarchy preservation |
| **Embed Service**   | Vector generation via OpenAI API                          |
| **Vector Store**    | Persistent storage and similarity search                  |
| **Search Engine**   | Query processing, filtering, result ranking               |
| **CLI**             | Command-line interface for ingestion operations           |

### 2.3 External Interfaces

| Interface    | Type          | Description                                 |
|--------------|---------------|---------------------------------------------|
| MCP Protocol | Bidirectional | Tool invocation and responses via stdio/SSE |
| OpenAI API   | Outbound      | Embedding generation requests               |
| Qdrant Cloud | Outbound      | Vector storage and search queries           |
| ChromaDB     | Local         | Alternative vector storage (fallback)       |
| File System  | Inbound       | Source document access                      |

---

## 3. Functional Requirements

### 3.1 MCP Tools

#### 3.1.1 knowledge_search

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TOOL-001 |
| **Priority** | Must Have      |

**Description:** The system shall provide a `knowledge_search` tool that performs semantic search over the knowledge base using natural language queries.

**Parameters:**

| Parameter        | Type    | Required  | Constraints       | Default   |
|------------------|---------|-----------|-------------------|-----------|
| `query`          | string  | Yes       | 1-2000 characters | —         |
| `n_results`      | integer | No        | 1-100             | 10        |
| `document_type`  | string  | No        | See §4.2.2        | null      |
| `chunk_type`     | string  | No        | See §4.2.1        | null      |
| `normative_only` | boolean | No        | —                 | false     |
| `use_hybrid`     | boolean | No        | —                 | true      |
| `hybrid_weight`  | float   | No        | 0.0-1.0           | 0.7       |

**Response Schema:**
```json
{
  "results": [
    {
      "id": "string (UUID)",
      "content": "string",
      "score": "float (0.0-1.0)",
      "source": {
        "document_id": "string",
        "document_title": "string",
        "document_type": "string",
        "source_path": "string",
        "page_numbers": ["integer"],
        "section": "string",
        "citation": "string"
      },
      "metadata": {
        "chunk_type": "string",
        "normative": "boolean",
        "section_hierarchy": ["string"],
        "references": ["string"]
      }
    }
  ],
  "total": "integer",
  "query": "string",
  "search_type": "semantic | hybrid | keyword"
}
```

**Empty Result Response:**
```json
{
  "results": [],
  "total": 0,
  "query": "string",
  "search_type": "string",
  "message": "No documents matched your query",
  "suggestions": ["Try broader terms", "Remove filters"]
}
```

---

#### 3.1.2 knowledge_lookup

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TOOL-002 |
| **Priority** | Must Have      |

**Description:** The system shall provide a `knowledge_lookup` tool that retrieves definitions for specific terms or concepts.

**Parameters:**

| Parameter  | Type   | Required  | Constraints      | Default  |
|------------|--------|-----------|------------------|----------|
| `term`     | string | Yes       | 1-200 characters | —        |

**Response Schema:**
```json
{
  "term": "string",
  "found": "boolean",
  "definitions": [
    {
      "definition": "string",
      "source": {
        "document_id": "string",
        "document_title": "string",
        "citation": "string"
      }
    }
  ]
}
```

**Not Found Response:**
```json
{
  "term": "string",
  "found": false,
  "message": "Term 'X' not found in knowledge base",
  "similar_terms": ["string"]
}
```

**Similar Terms Algorithm:** *(CLARIFY-003)*

1. Search definition chunks using query term with semantic embedding similarity
2. Return top 3 results with similarity score > 0.5
3. If fewer than 3 semantic matches found, supplement with fuzzy string matching:
   - Use Levenshtein edit distance ≤ 2 against indexed definition terms
   - Exclude duplicates already found via semantic search
4. Return empty array if no similar terms found by either method

**Example:**
- Query: "requiremnt" (typo)
- Semantic search: ["system requirement", "functional requirement"]
- Fuzzy match: ["requirement"] (edit distance = 1)
- Result: ["requirement", "system requirement", "functional requirement"]


---

#### 3.1.3 knowledge_requirements

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TOOL-003 |
| **Priority** | Must Have      |

**Description:** The system shall provide a `knowledge_requirements` tool that finds requirements related to a specific topic from standards.

**Parameters:**

| Parameter   | Type    | Required  | Constraints       | Default |
|-------------|---------|-----------|-------------------|---------|
| `topic`     | string  | Yes       | 1-1000 characters | —       |
| `standard`  | string  | No        | 1-100 characters  | null    |
| `n_results` | integer | No        | 1-50              | 10      |

**Response Schema:**
```json
{
  "results": [
    {
      "requirement_text": "string",
      "requirement_id": "string (clause number)",
      "source": {
        "document_id": "string",
        "document_title": "string",
        "citation": "string"
      },
      "normative": "boolean",
      "score": "float"
    }
  ],
  "topic": "string",
  "standard_filter": "string | null",
  "total": "integer"
}
```

**Empty Result Response:**
```json
{
  "results": [],
  "topic": "string",
  "standard_filter": "string | null",
  "total": 0,
  "message": "No requirements found for this topic"
}
```

---

#### 3.1.4 knowledge_keyword_search

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TOOL-004 |
| **Priority** | Must Have      |

**Description:** The system shall provide a `knowledge_keyword_search` tool that performs full-text keyword search for exact term matching.

**Parameters:**

| Parameter   | Type    | Required  | Constraints       | Default |
|-------------|---------|-----------|-------------------|---------|
| `query`     | string  | Yes       | 1-500 characters  | —       |
| `n_results` | integer | No        | 1-100             | 10      |

**Response Schema:** Same as `knowledge_search` (§3.1.1) with `search_type: "keyword"`.

---

#### 3.1.5 knowledge_stats

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TOOL-005 |
| **Priority** | Must Have      |

**Description:** The system shall provide a `knowledge_stats` tool that returns statistics about the knowledge base.

**Parameters:** None.

**Response Schema:**
```json
{
  "knowledge_base": {
    "total_chunks": "integer",
    "total_documents": "integer",
    "total_tokens": "integer",
    "storage_bytes": "integer"
  },
  "documents": [
    {
      "document_id": "string",
      "document_title": "string",
      "document_type": "string",
      "chunk_count": "integer",
      "ingested_at": "string (ISO 8601)"
    }
  ],
  "vector_store": {
    "backend": "qdrant | chromadb",
    "status": "healthy | degraded | unavailable",
    "hybrid_enabled": "boolean"
  },
  "embedding": {
    "model": "string",
    "dimensions": "integer"
  }
}
```

---

#### 3.1.6 knowledge_health

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TOOL-006 |
| **Priority** | Should Have    |

**Description:** The system shall provide a `knowledge_health` tool that checks the status of external dependencies.

**Parameters:** None.

**Response Schema:**
```json
{
  "status": "healthy | degraded | unhealthy",
  "checks": {
    "vector_store": {
      "status": "up | down",
      "latency_ms": "integer",
      "message": "string"
    },
    "embedding_service": {
      "status": "up | down",
      "latency_ms": "integer",
      "message": "string"
    }
  },
  "timestamp": "string (ISO 8601)"
}

**Health Status Determination:** *(CLARIFY-007)*

| Condition | Status |
|-----------|--------|
| All checks up AND all latency < 500ms | `healthy` |
| All checks up AND any latency ≥ 500ms | `degraded` |
| Any check down | `unhealthy` |

**Configuration:**
- `HEALTH_LATENCY_THRESHOLD_MS`: Latency threshold in milliseconds (default: 500)

```

---

### 3.2 Ingestion Pipeline

#### 3.2.1 Format Support

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-INGEST-001 |
| **Priority** | Must Have        |

**Description:** The system shall support ingestion of the following document formats:

| Format         | Extensions  | Notes                            |
|----------------|-------------|----------------------------------|
| PDF            | `.pdf`      | Up to 1000 pages                 |
| Microsoft Word | `.docx`     | OOXML format only                |
| Markdown       | `.md`       | CommonMark with YAML frontmatter |

---

#### 3.2.2 Ingestion Capability Matrix

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-INGEST-002 |
| **Priority** | Must Have        |

**Description:** The system shall extract the following elements per format:

| Capability                         | PDF  | DOCX  | Markdown   |
|------------------------------------|------|-------|------------|
| Text extraction                    | ✓    | ✓     | ✓          |
| Section hierarchy (up to 6 levels) | ✓    | ✓     | ✓          |
| Page numbers                       | ✓    | —     | —          |
| Tables (as text)                   | ✓    | ✓     | ✓          |
| Figures (caption only)             | ✓    | ✓     | ✓          |
| Cross-references                   | ✓    | ✓     | ✓          |
| Frontmatter metadata               | —    | ✓     | ✓          |
| Clause numbering                   | ✓    | ✓     | ✓          |

---

#### 3.2.3 Structure Preservation

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-INGEST-003 |
| **Priority** | Must Have        |

**Description:** The system shall preserve document structure during ingestion:

1. Maintain section/subsection hierarchy up to 6 levels
2. Preserve clause numbers (e.g., "5.3.1.2")
3. Detect and tag normative vs. informative content
4. Extract definitions, requirements, and guidance as distinct chunk types
5. Capture cross-references between sections

---

#### 3.2.4 Metadata Extraction

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-INGEST-004 |
| **Priority** | Must Have        |

**Description:** The system shall extract and store the following metadata per chunk:

| Metadata Field      | Source                        | Required   |
|---------------------|-------------------------------|------------|
| `document_id`       | Filename or frontmatter       | Yes        |
| `document_title`    | Document title or frontmatter | Yes        |
| `document_type`     | Frontmatter or classification | Yes        |
| `section_hierarchy` | Parsed structure              | Yes        |
| `section_title`     | Heading text                  | Yes        |
| `page_numbers`      | PDF page tracking             | If PDF     |
| `clause_number`     | Pattern extraction            | If present |
| `chunk_type`        | Content analysis              | Yes        |
| `normative`         | Keyword detection             | Yes        |
| `references`        | Cross-reference extraction    | If present |

---

#### 3.2.5 Chunk Size

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-INGEST-005 |
| **Priority** | Must Have        |

**Description:** The system shall chunk content with the following constraints:

| Parameter          | Default    | Min  | Max  | Configurable  |
|--------------------|------------|------|------|---------------|
| Minimum chunk size | 200 tokens | 50   | 500  | Yes           |
| Maximum chunk size | 800 tokens | 200  | 2000 | Yes           |
| Chunk overlap      | 100 tokens | 0    | 500  | Yes           |

Constraint: `chunk_overlap` < `chunk_size_min`

---

#### 3.2.6 Content Deduplication

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-INGEST-006 |
| **Priority** | Should Have      |

**Description:** The system shall detect and handle duplicate content:

1. Compute SHA-256 hash of chunk content
2. Store hash as `content_hash` field
3. On re-ingest with `--force`, replace chunks with matching document_id
4. Log warning if identical content found in different documents

---

### 3.3 Search Capabilities

#### 3.3.1 Semantic Search

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-SEARCH-001 |
| **Priority** | Must Have        |

**Description:** The system shall perform semantic search using dense vector similarity:

1. Embed query using configured embedding model
2. Compute cosine similarity with stored vectors
3. Return top-N results ranked by similarity score
4. Support filtering by metadata fields

---

#### 3.3.2 Hybrid Search

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-SEARCH-002 |
| **Priority** | Must Have        |

**Description:** The system shall support hybrid search combining semantic and keyword matching:

| Parameter          | Description                                   |
|--------------------|-----------------------------------------------|
| **Algorithm**      | Dense vectors + BM25 sparse matching          |
| **Default Weight** | 70% semantic, 30% keyword                     |
| **Configurable**   | Yes, via `hybrid_weight` parameter (0.0-1.0)  |
| **Fusion Method**  | Reciprocal Rank Fusion (RRF) with k=60        |
| **Fallback**       | Dense-only with warning if hybrid unavailable |

---

#### 3.3.3 Metadata Filtering

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-SEARCH-003 |
| **Priority** | Must Have        |

**Description:** The system shall support filtering search results by:

| Filter          | Type    | Operators      |
|-----------------|---------|----------------|
| `document_id`   | string  | equals, in     |
| `document_type` | string  | equals, in     |
| `chunk_type`    | string  | equals, in     |
| `normative`     | boolean | equals         |
| `clause_number` | string  | equals, prefix |

---

### 3.4 CLI Interface

#### 3.4.1 Ingest Command

| Field        | Value         |
|--------------|---------------|
| **ID**       | A-REQ-CLI-001 |
| **Priority** | Must Have     |

**Description:** The system shall provide a `knowledge-ingest` CLI command.

**Usage:**
```
knowledge-ingest [OPTIONS] <source>
```

**Arguments:**

| Argument  | Description                         |
|-----------|-------------------------------------|
| `source`  | Path to file or directory to ingest |

**Options:**

| Option        | Description                            | Default             |
|---------------|----------------------------------------|---------------------|
| `--recursive` | Process directories recursively        | true                |
| `--pattern`   | Glob pattern for files                 | `*.pdf,*.docx,*.md` |
| `--dry-run`   | Show what would be ingested            | false               |
| `--force`     | Re-ingest even if content hash matches | false               |
| `--verbose`   | Show detailed progress                 | false               |

**Output:**
- Progress indicator during processing
- Summary on completion: files processed, chunks created, errors

**Exit Codes:**

| Code  | Meaning                               |
|-------|---------------------------------------|
| 0     | Success                               |
| 1     | Partial failure (some files failed)   |
| 2     | Complete failure (no files processed) |
| 3     | Configuration error                   |

---

#### 3.4.2 Server Command

| Field        | Value         |
|--------------|---------------|
| **ID**       | A-REQ-CLI-002 |
| **Priority** | Must Have     |

**Description:** The system shall provide a `knowledge-mcp` CLI command to start the MCP server.

**Usage:**
```
knowledge-mcp [OPTIONS]
```

**Options:**

| Option        | Description                    | Default  |
|---------------|--------------------------------|----------|
| `--transport` | Transport type: `stdio`, `sse` | `stdio`  |
| `--log-level` | Logging level                  | `INFO`   |

**Exit Codes:**

| Code  | Meaning         |
|-------|-----------------|
| 0     | Clean shutdown  |
| 1     | Startup failure |

---

## 4. Data Requirements

### 4.1 Data Models

#### 4.1.1 KnowledgeChunk Schema

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-DATA-001 |
| **Priority** | Must Have      |

**Description:** Each knowledge chunk shall conform to the following schema:

| Field               | Type              | Required  | Description                           |
|---------------------|-------------------|-----------|---------------------------------------|
| `id`                | string (UUID)     | Yes       | Unique identifier                     |
| `document_id`       | string            | Yes       | Source document identifier            |
| `document_title`    | string            | Yes       | Human-readable document title         |
| `document_type`     | string            | Yes       | Document classification (see §4.2.2)  |
| `content`           | string            | Yes       | Text content                          |
| `content_hash`      | string            | Yes       | SHA-256 hash for deduplication        |
| `token_count`       | integer           | Yes       | Token count for context management    |
| `section_hierarchy` | array[string]     | Yes       | Path through document structure       |
| `section_title`     | string            | Yes       | Title of containing section           |
| `parent_chunk_id`   | string            | No        | Link to parent section chunk          |
| `chunk_type`        | string            | Yes       | Content classification (see §4.2.1)   |
| `normative`         | boolean           | Yes       | Whether content is mandatory          |
| `page_numbers`      | array[integer]    | No        | Source page references                |
| `clause_number`     | string            | No        | Clause identifier                     |
| `references`        | array[string]     | No        | Extracted cross-references            |
| `source_path`       | string            | Yes       | Original file path                    |
| `embedding`         | array[float]      | Yes*      | Vector embedding (*after embed phase) |
| `embedding_model`   | string            | Yes       | Model used for embedding              |
| `created_at`        | string (ISO 8601) | Yes       | Creation timestamp                    |
| `updated_at`        | string (ISO 8601) | Yes       | Last update timestamp                 |

---

### 4.2 Enumerations

#### 4.2.1 chunk_type

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-DATA-002 |
| **Priority** | Must Have      |

| Value            | Description                           |
|------------------|---------------------------------------|
| `definition`     | Term or concept definition            |
| `requirement`    | Normative requirement (shall/must)    |
| `recommendation` | Advisory guidance (should)            |
| `guidance`       | Informative guidance or best practice |
| `example`        | Illustrative example                  |
| `figure`         | Figure caption and description        |
| `table`          | Table content                         |
| `overview`       | Introductory or summary content       |
| `reference`      | Bibliography or cross-reference       |
| `annex`          | Annex/appendix content                |

---

#### 4.2.2 document_type

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-DATA-003 |
| **Priority** | Must Have      |

| Value           | Description                            |
|-----------------|----------------------------------------|
| `standard`      | Formal standard (IEEE, ISO, etc.)      |
| `handbook`      | Comprehensive reference (NASA, INCOSE) |
| `guide`         | Guidance document (SEBoK, etc.)        |
| `specification` | Technical specification                |
| `report`        | Technical report                       |
| `policy`        | Policy document                        |
| `custom`        | User-defined document type             |

---

#### 4.2.3 error_code

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-DATA-004 |
| **Priority** | Must Have      |

| Code               | Category      | Description                           |
|--------------------|---------------|---------------------------------------|
| `config_error`     | Configuration | Invalid or missing configuration      |
| `connection_error` | Network       | Unable to connect to external service |
| `timeout_error`    | Network       | Request timed out                     |
| `auth_error`       | Security      | Authentication failed                 |
| `not_found`        | Data          | Requested resource not found          |
| `invalid_input`    | Validation    | Invalid parameter value               |
| `rate_limited`     | Capacity      | Rate limit exceeded                   |
| `internal_error`   | System        | Unexpected internal error             |

---

#### 4.2.4 Normative Detection

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-DATA-005 |
| **Priority** | Must Have      |

**Description:** The `normative` field shall be determined by:

| normative = true                            | normative = false                                  |
|---------------------------------------------|----------------------------------------------------|
| Contains: "shall", "must", "is required to" | Contains: "should", "may", "can", "is recommended" |
| From normative sections of standards        | From informative sections                          |
|                                             | Includes: examples, notes, informative annexes     |

---

## 5. Interface Requirements

### 5.1 MCP Protocol

| Field        | Value        |
|--------------|--------------|
| **ID**       | A-REQ-IF-001 |
| **Priority** | Must Have    |

**Description:** The system shall implement MCP server protocol:

1. Support `stdio` transport (required)
2. Support `sse` transport (optional)
3. Register all tools with complete JSON schemas
4. Return responses within MCP message format
5. Handle tool invocation errors gracefully

---

### 5.2 OpenAI API

| Field        | Value        |
|--------------|--------------|
| **ID**       | A-REQ-IF-002 |
| **Priority** | Must Have    |

**Description:** The system shall integrate with OpenAI Embeddings API:

| Parameter  | Default                  | Configurable   |
|------------|--------------------------|----------------|
| Model      | `text-embedding-3-small` | Yes            |
| Dimensions | 1536                     | Yes (256-3072) |
| Batch size | 100 texts                | Yes            |

**Error Handling for OpenAI API:** *(CLARIFY-002)*

| OpenAI Error | Error Code | Action |
|--------------|------------|--------|
| 401 Unauthorized | `auth_error` | Fail immediately, exit code 3 |
| 429 Rate Limited (temporary) | `rate_limited` | Retry with backoff per §6.2.2 |
| 429 Quota Exceeded | `rate_limited` | Fail with clear message, suggest billing check |
| 400 Invalid Request | `invalid_input` | Skip content, log ERROR with chunk details |
| 500+ Server Error | `internal_error` | Retry with backoff per §6.2.2 |

For quota exhaustion: The system shall fail with a clear error message indicating:
- Current quota status (if available from API response)
- Suggestion to check OpenAI billing dashboard
- No local embedding fallback (preserves embedding space consistency)


---

### 5.3 Vector Store

| Field        | Value        |
|--------------|--------------|
| **ID**       | A-REQ-IF-003 |
| **Priority** | Must Have    |

**Description:** The system shall support two vector store backends:

**Qdrant Cloud (Primary):**
- Cloud-hosted vector database
- Requires: URL, API key
- Features: hybrid search, payload indexing, full-text search

**ChromaDB (Fallback):**
- Local embedded database
- Requires: local storage path
- Features: basic vector search, metadata filtering

Backend selection via `VECTOR_STORE` environment variable.

---

### 5.4 File System

| Field        | Value        |
|--------------|--------------|
| **ID**       | A-REQ-IF-004 |
| **Priority** | Must Have    |

**Description:** The system shall access source documents via file system:

1. Read files from specified source paths
2. Support absolute and relative paths
3. Handle permission errors gracefully
4. Report inaccessible files without aborting batch

---

## 6. Quality Requirements

### 6.1 Performance

#### 6.1.1 Query Latency

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-PERF-001 |
| **Priority** | Should Have    |

**Description:** Query response time shall be acceptable for interactive use:

| Metric                       | Target  | Maximum  |
|------------------------------|---------|----------|
| Semantic search (10 results) | < 2s    | 5s       |
| Keyword search (10 results)  | < 1s    | 3s       |
| Term lookup                  | < 1s    | 2s       |
| Stats retrieval              | < 500ms | 1s       |

*Note: Excludes network latency to external services.*

---

#### 6.1.2 Ingestion Throughput

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-PERF-002 |
| **Priority** | Should Have    |

**Description:** Ingestion shall process documents at reasonable speed:

| Document Size  | Target Time   |
|----------------|---------------|
| 100 pages      | < 2 minutes   |
| 500 pages      | < 10 minutes  |
| 1000 pages     | < 20 minutes  |

---

#### 6.1.3 Memory Management

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-PERF-003 |
| **Priority** | Must Have      |

**Description:** The system shall manage memory during ingestion:

1. Process documents page-by-page (PDF) or section-by-section (DOCX/MD)
2. Target peak memory usage < 500MB during ingestion
3. Stream large documents rather than loading entirely

---

### 6.2 Reliability

#### 6.2.1 Error Response Format

| Field        | Value         |
|--------------|---------------|
| **ID**       | A-REQ-REL-001 |
| **Priority** | Must Have     |

**Description:** All errors shall return structured responses:

```json
{
  "error": {
    "code": "string (see §4.2.3)",
    "message": "string (human-readable)",
    "details": "string (technical details)",
    "recoverable": "boolean",
    "suggestion": "string (recovery action)"
  }
}
```

---

#### 6.2.2 Retry Behavior

| Field        | Value         |
|--------------|---------------|
| **ID**       | A-REQ-REL-002 |
| **Priority** | Must Have     |

**Description:** The system shall retry failed external requests:

| Parameter           | Value                                         |
|---------------------|-----------------------------------------------|
| Retry count         | 3 attempts                                    |
| Backoff             | Exponential (1s, 2s, 4s)                      |
| Timeout per attempt | 10s (queries), 60s (ingestion batches)        |
| Retryable errors    | Connection errors, timeouts, 5xx responses    |
| Non-retryable       | Auth errors, validation errors, 4xx responses |

---

#### 6.2.3 Startup Validation

| Field        | Value         |
|--------------|---------------|
| **ID**       | A-REQ-REL-003 |
| **Priority** | Must Have     |

**Description:** The system shall validate configuration at startup:

1. Check all required environment variables are set
2. Validate API key formats
3. Test connectivity to vector store
4. Report all validation errors before failing
5. Exit with code 3 on configuration error

---

### 6.3 Maintainability

#### 6.3.1 Logging Requirements

| Field        | Value           |
|--------------|-----------------|
| **ID**       | A-REQ-MAINT-001 |
| **Priority** | Must Have       |

**Description:** The system shall log the following events:

| Level  | Event                 | Content                              |
|--------|-----------------------|--------------------------------------|
| INFO   | `server_start`        | Config summary, vector store status  |
| INFO   | `query_received`      | Tool name, query hash, filters       |
| INFO   | `query_complete`      | Tool name, result count, latency_ms  |
| WARN   | `retry_attempt`       | Service, attempt number, reason      |
| ERROR  | `query_failed`        | Tool name, error code, error message |
| DEBUG  | `embedding_generated` | Token count, latency_ms              |

**Configuration:**
- Format: Configurable via `LOG_FORMAT` (text or JSON)
- Level: Configurable via `LOG_LEVEL` (default: INFO)

---

#### 6.3.2 Configuration

| Field        | Value           |
|--------------|-----------------|
| **ID**       | A-REQ-MAINT-002 |
| **Priority** | Must Have       |

**Description:** The system shall be configured via environment variables:

| Variable               | Required    | Default                  | Description                     |
|------------------------|-------------|--------------------------|---------------------------------|
| `OPENAI_API_KEY`       | Yes         | —                        | OpenAI API key                  |
| `VECTOR_STORE`         | No          | `qdrant`                 | Backend: `qdrant` or `chromadb` |
| `QDRANT_URL`           | If Qdrant   | —                        | Qdrant Cloud cluster URL        |
| `QDRANT_API_KEY`       | If Qdrant   | —                        | Qdrant Cloud API key            |
| `QDRANT_COLLECTION`    | No          | `se_knowledge_base`      | Collection name                 |
| `QDRANT_HYBRID_SEARCH` | No          | `true`                   | Enable hybrid search            |
| `CHROMADB_PATH`        | If ChromaDB | `./collections/chromadb` | Local storage path              |
| `EMBEDDING_MODEL`      | No          | `text-embedding-3-small` | OpenAI model                    |
| `EMBEDDING_DIMENSIONS` | No          | `1536`                   | Vector dimensions               |
| `CHUNK_SIZE_MIN`       | No          | `200`                    | Minimum chunk tokens            |
| `CHUNK_SIZE_MAX`       | No          | `800`                    | Maximum chunk tokens            |
| `CHUNK_OVERLAP`        | No          | `100`                    | Overlap tokens                  |
| `LOG_LEVEL`            | No          | `INFO`                   | Logging level                   |
| `LOG_FORMAT`           | No          | `text`                   | Log format: `text` or `json`    |

---

### 6.4 Testability

#### 6.4.1 Coverage Requirements

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TEST-001 |
| **Priority** | Must Have      |

**Description:** The codebase shall meet coverage thresholds:

| Metric            | Minimum  | Target  |
|-------------------|----------|---------|
| Line coverage     | 80%      | 90%     |
| Branch coverage   | 75%      | 85%     |
| Function coverage | 85%      | 95%     |

---

#### 6.4.2 Type Checking

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TEST-002 |
| **Priority** | Must Have      |

**Description:** The codebase shall pass Pyright strict mode with zero errors.

---

#### 6.4.3 Linting

| Field        | Value          |
|--------------|----------------|
| **ID**       | A-REQ-TEST-003 |
| **Priority** | Must Have      |

**Description:** The codebase shall pass Ruff linting with zero errors.

---

## 7. Configuration

### 7.1 Environment Variables

See §6.3.2 for complete list.

### 7.2 .env File Support

| Field        | Value            |
|--------------|------------------|
| **ID**       | A-REQ-CONFIG-001 |
| **Priority** | Must Have        |

**Description:** The system shall support `.env` files:

1. Load `.env` from current working directory
2. Search parent directories for `.env` if not found
3. Environment variables override `.env` values
4. Provide `.env.example` template in repository

---

## Appendix A: Tool Response Schemas

Complete JSON schemas for all tool responses are defined in sections 3.1.1 through 3.1.6.

## Appendix B: Error Code Reference

Complete error code enumeration is defined in section 4.2.3.

## Appendix C: Requirements Traceability

| Requirement ID   | Category        | Priority    |
|------------------|-----------------|-------------|
| A-REQ-TOOL-001   | MCP Tools       | Must Have   |
| A-REQ-TOOL-002   | MCP Tools       | Must Have   |
| A-REQ-TOOL-003   | MCP Tools       | Must Have   |
| A-REQ-TOOL-004   | MCP Tools       | Must Have   |
| A-REQ-TOOL-005   | MCP Tools       | Must Have   |
| A-REQ-TOOL-006   | MCP Tools       | Should Have |
| A-REQ-INGEST-001 | Ingestion       | Must Have   |
| A-REQ-INGEST-002 | Ingestion       | Must Have   |
| A-REQ-INGEST-003 | Ingestion       | Must Have   |
| A-REQ-INGEST-004 | Ingestion       | Must Have   |
| A-REQ-INGEST-005 | Ingestion       | Must Have   |
| A-REQ-INGEST-006 | Ingestion       | Should Have |
| A-REQ-SEARCH-001 | Search          | Must Have   |
| A-REQ-SEARCH-002 | Search          | Must Have   |
| A-REQ-SEARCH-003 | Search          | Must Have   |
| A-REQ-CLI-001    | CLI             | Must Have   |
| A-REQ-CLI-002    | CLI             | Must Have   |
| A-REQ-DATA-001   | Data Model      | Must Have   |
| A-REQ-DATA-002   | Enumeration     | Must Have   |
| A-REQ-DATA-003   | Enumeration     | Must Have   |
| A-REQ-DATA-004   | Enumeration     | Must Have   |
| A-REQ-DATA-005   | Data Model      | Must Have   |
| A-REQ-IF-001     | Interface       | Must Have   |
| A-REQ-IF-002     | Interface       | Must Have   |
| A-REQ-IF-003     | Interface       | Must Have   |
| A-REQ-IF-004     | Interface       | Must Have   |
| A-REQ-PERF-001   | Performance     | Should Have |
| A-REQ-PERF-002   | Performance     | Should Have |
| A-REQ-PERF-003   | Performance     | Must Have   |
| A-REQ-REL-001    | Reliability     | Must Have   |
| A-REQ-REL-002    | Reliability     | Must Have   |
| A-REQ-REL-003    | Reliability     | Must Have   |
| A-REQ-MAINT-001  | Maintainability | Must Have   |
| A-REQ-MAINT-002  | Maintainability | Must Have   |
| A-REQ-TEST-001   | Testability     | Must Have   |
| A-REQ-TEST-002   | Testability     | Must Have   |
| A-REQ-TEST-003   | Testability     | Must Have   |
| A-REQ-CONFIG-001 | Configuration   | Must Have   |

**Total Requirements: 37**
- Must Have: 33
- Should Have: 4

---

*End of Document*
