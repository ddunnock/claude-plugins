# Architecture

**Analysis Date:** 2026-01-20

## Pattern Overview

**Overall:** Layered Architecture with Pipeline Processing

**Key Characteristics:**
- MCP server as primary entry point exposing tools via stdio transport
- Multi-stage document processing pipeline: Ingest -> Chunk -> Embed -> Store -> Search
- Abstract base classes enabling provider switching (vector stores, embedders, ingestors)
- Pydantic models for data validation throughout the pipeline
- Structured exception hierarchy mapping to MCP error codes

## Layers

**Presentation Layer (MCP Server):**
- Purpose: Expose knowledge search tools via Model Context Protocol
- Location: `src/knowledge_mcp/server.py`
- Contains: `KnowledgeMCPServer` class, MCP tool handlers, stdio transport
- Depends on: All lower layers
- Used by: AI assistants via MCP protocol

**Ingestion Layer:**
- Purpose: Parse documents and extract structured content
- Location: `src/knowledge_mcp/ingest/`
- Contains: `DoclingIngestor`, `BaseIngestor`, `IngestResult`, `IngestMetadata`
- Depends on: Docling library, exceptions
- Used by: CLI, pipeline orchestration (future)

**Chunking Layer:**
- Purpose: Split content into semantically coherent units
- Location: `src/knowledge_mcp/chunk/`
- Contains: `DoclingChunker`, `BaseChunker`, `ChunkMetadata`, `ChunkingResult`
- Depends on: Docling HybridChunker, models
- Used by: Pipeline orchestration (future)

**Embedding Layer:**
- Purpose: Convert text to vector embeddings
- Location: `src/knowledge_mcp/embed/`
- Contains: `OpenAIEmbedder`, `BaseEmbedder`
- Depends on: OpenAI API, tenacity for retries
- Used by: Pipeline orchestration (future)

**Storage Layer:**
- Purpose: Store and retrieve vector embeddings
- Location: `src/knowledge_mcp/store/`
- Contains: `QdrantStore`, `ChromaDBStore`, `BaseStore`, `create_store` factory
- Depends on: qdrant-client, chromadb (optional)
- Used by: Search layer, MCP server

**Models Layer:**
- Purpose: Define core data structures used across layers
- Location: `src/knowledge_mcp/models/`
- Contains: `KnowledgeChunk`, `ChunkType`, `DocumentType`, `ErrorCode` enums
- Depends on: Pydantic
- Used by: All layers

**Utilities Layer:**
- Purpose: Configuration, logging, and shared utilities
- Location: `src/knowledge_mcp/utils/`
- Contains: `KnowledgeConfig`, `load_config`, logging setup
- Depends on: python-dotenv, logging
- Used by: All layers

## Data Flow

**Document Ingestion Pipeline:**

1. Source document (PDF, DOCX, etc.) passed to `DoclingIngestor.ingest()`
2. Docling parses document, extracts structure and content
3. `IngestResult` objects yielded for each section with metadata
4. `DoclingChunker.chunk_document()` receives DoclingDocument
5. Docling's HybridChunker splits into token-aware chunks
6. `KnowledgeChunk` objects created with content hash, hierarchy
7. `OpenAIEmbedder.embed_batch()` generates embeddings
8. `QdrantStore.add_chunks()` (or ChromaDB fallback) persists vectors

**Search Flow:**

1. Query received via MCP tool call
2. `OpenAIEmbedder.embed()` generates query embedding
3. `QdrantStore.search()` performs vector similarity search
4. Optional metadata filters applied (document_type, chunk_type, normative)
5. Results formatted and returned via MCP protocol

**State Management:**
- Configuration loaded from environment at startup via `load_config()`
- Vector stores maintain persistent collections (Qdrant Cloud or ChromaDB local)
- No in-memory session state between MCP calls

## Key Abstractions

**BaseIngestor:**
- Purpose: Abstract interface for document format parsers
- Examples: `src/knowledge_mcp/ingest/docling_ingestor.py`
- Pattern: Template Method with registry for extension-to-ingestor mapping

**BaseChunker:**
- Purpose: Abstract interface for chunking strategies
- Examples: `src/knowledge_mcp/chunk/docling_chunker.py`
- Pattern: Strategy pattern allowing different chunking algorithms

**BaseEmbedder:**
- Purpose: Abstract interface for embedding providers
- Examples: `src/knowledge_mcp/embed/openai_embedder.py`
- Pattern: Adapter pattern wrapping embedding APIs

**BaseStore:**
- Purpose: Abstract interface for vector storage backends
- Examples: `src/knowledge_mcp/store/qdrant_store.py`, `src/knowledge_mcp/store/chromadb_store.py`
- Pattern: Repository pattern with factory method (`create_store`)

**KnowledgeChunk:**
- Purpose: Core data model representing searchable knowledge units
- Examples: Used throughout pipeline
- Pattern: Immutable Pydantic model with computed properties

## Entry Points

**MCP Server (`__main__.py`):**
- Location: `src/knowledge_mcp/__main__.py`
- Triggers: `python -m knowledge_mcp` or `poetry run knowledge-mcp`
- Responsibilities: Initialize server, run async event loop, handle signals

**Server Class:**
- Location: `src/knowledge_mcp/server.py`
- Triggers: Called by `__main__.py`
- Responsibilities: Set up MCP handlers, run stdio transport, dispatch tool calls

**CLI Scripts (defined in pyproject.toml):**
- `knowledge-mcp` -> `knowledge_mcp.__main__:cli`
- `knowledge-ingest` -> `knowledge_mcp.cli.ingest:main` (not yet implemented)

## Error Handling

**Strategy:** Structured exception hierarchy with MCP error code mapping

**Patterns:**
- All application exceptions inherit from `KnowledgeMCPError` (`src/knowledge_mcp/exceptions.py`)
- Each exception has `error_code`, `recoverable`, `default_suggestion` class attributes
- `to_dict()` method on exceptions returns structured `ErrorResponse` for MCP
- Async operations use tenacity for retries with exponential backoff

**Exception Types:**
| Exception | Error Code | Recoverable | Use Case |
|-----------|------------|-------------|----------|
| `ConfigurationError` | `config_error` | No | Missing env vars |
| `ConnectionError` | `connection_error` | Yes | Network failures |
| `TimeoutError` | `timeout_error` | Yes | API timeouts |
| `AuthenticationError` | `auth_error` | No | Invalid API keys |
| `NotFoundError` | `not_found` | No | Missing resource |
| `ValidationError` | `invalid_input` | No | Bad parameters |
| `RateLimitError` | `rate_limited` | Yes | API throttling |
| `InternalError` | `internal_error` | No | Unexpected errors |
| `IngestionError` | `internal_error` | No | Document parse failures |

## Cross-Cutting Concerns

**Logging:**
- Module: `src/knowledge_mcp/utils/logging.py`
- Features: JSON/human-readable formats, sensitive data filtering
- Pattern: `SensitiveDataFilter` redacts API keys and tokens
- Usage: `get_logger(__name__)` to obtain configured child logger

**Validation:**
- Pydantic models with field validators for all data structures
- `KnowledgeConfig.check_config()` validates configuration completeness
- Path validation in ingestors before processing

**Authentication:**
- API keys loaded from environment variables via `load_config()`
- Keys passed to clients at initialization, never logged
- `AuthenticationError` raised on invalid credentials

**Configuration:**
- Module: `src/knowledge_mcp/utils/config.py`
- Source: Environment variables with `.env` file support
- Pattern: Single `KnowledgeConfig` Pydantic model
- Required: `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY` (for Qdrant mode)

---

*Architecture analysis: 2026-01-20*
