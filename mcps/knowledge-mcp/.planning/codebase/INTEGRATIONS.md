# External Integrations

**Analysis Date:** 2026-01-20

## APIs & External Services

**Embeddings:**
- **OpenAI** - Embedding generation for semantic search
  - SDK/Client: `openai>=1.0.0` (`AsyncOpenAI` client)
  - Model: `text-embedding-3-small` (1536 dimensions)
  - Auth: `OPENAI_API_KEY` environment variable
  - Implementation: `src/knowledge_mcp/embed/openai_embedder.py`
  - Features:
    - Async API calls
    - Batching (max 100 texts per API call)
    - Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
    - Handles: `APIConnectionError`, `APITimeoutError`, `RateLimitError`

**Vector Storage (Primary):**
- **Qdrant Cloud** - Managed vector database for semantic search
  - SDK/Client: `qdrant-client>=1.7.0` (`QdrantClient`)
  - Auth: `QDRANT_URL` and `QDRANT_API_KEY` environment variables
  - Implementation: `src/knowledge_mcp/store/qdrant_store.py`
  - Features:
    - Dense vector search (cosine distance)
    - Hybrid search support (sparse vectors via BM25)
    - Payload indexing for metadata filters
    - Full-text search on content field
    - Batch upsert (100 points per batch)
    - 60-second timeout

**Document Processing:**
- **Docling** - AI-powered document parsing (IBM)
  - SDK: `docling>=2.15.0`, `docling-core>=2.15.0[chunking]`
  - Implementation: `src/knowledge_mcp/ingest/docling_ingestor.py`
  - AI Models Used:
    - DocLayNet - Layout analysis
    - TableFormer - Table structure recognition
  - Supported Formats: PDF, DOCX, PPTX, XLSX, HTML, images (PNG, JPG, TIFF, BMP)
  - Features:
    - OCR support (configurable via `DOCLING_OCR_ENABLED`)
    - Table extraction modes: accurate/fast (`DOCLING_TABLE_MODE`)
    - Formula and code block extraction
    - Section hierarchy preservation (max 6 levels)

**Reranking (Optional):**
- **Cohere** - Result reranking for improved relevance
  - SDK: `cohere>=4.0.0` (in `rerank` optional group)
  - Status: Optional dependency, not currently implemented in core

**Local Embeddings (Optional):**
- **Sentence Transformers** - Offline embedding models
  - SDK: `sentence-transformers>=2.2.0` (in `local` optional group)
  - Status: Optional dependency, not currently implemented in core

## Data Storage

**Databases:**
- **Qdrant Cloud** (Primary)
  - Connection: `QDRANT_URL` + `QDRANT_API_KEY`
  - Client: `qdrant-client` Python SDK
  - Collection: Configurable via `QDRANT_COLLECTION` (default: `se_knowledge_base`)
  - Vector Config:
    - Dense vectors: 1536 dimensions, cosine distance
    - Sparse vectors: Optional for hybrid search
  - Indexed Fields: `document_id`, `document_type`, `chunk_type`, `normative`, `clause_number`
  - Full-text index on `content` field

- **ChromaDB** (Fallback)
  - Connection: Local path via `CHROMADB_PATH` (default: `./collections/chromadb`)
  - Client: `chromadb.PersistentClient`
  - Collection: `CHROMADB_COLLECTION` (default: `se_knowledge_base`)
  - Implementation: `src/knowledge_mcp/store/chromadb_store.py`
  - Features:
    - Persistent local storage
    - Cosine distance metric
    - Telemetry disabled
    - Metadata filters (converted to ChromaDB where clause format)

**File Storage:**
- Local filesystem for document sources (`data/sources/`)
- Local filesystem for processed output (`data/processed/`)
- ChromaDB data: `./collections/chromadb/` (when using local fallback)

**Caching:**
- None implemented (embeddings computed on demand)

## Authentication & Identity

**Auth Provider:**
- Custom API key validation (no external auth provider)
  - OpenAI API key validated at startup
  - Qdrant API key validated on first connection
  - Keys stored in environment variables (never logged)

**Security:**
- API keys never exposed in error messages
- Input validation via Pydantic models
- Exception hierarchy maps to MCP error codes

## Monitoring & Observability

**Error Tracking:**
- Custom exception hierarchy in `src/knowledge_mcp/exceptions.py`
- Structured error responses (code, message, details, recoverable, suggestion)
- Error codes mapped to MCP protocol

**Logs:**
- Python `logging` module
- Configurable level: `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Configurable format: `LOG_FORMAT` (text or json)
- Implementation: `src/knowledge_mcp/utils/logging.py`

**Health Checks:**
- `QdrantStore.health_check()` - Verifies Qdrant connectivity
- `ChromaDBStore.health_check()` - Verifies ChromaDB accessibility
- Latency threshold: `HEALTH_LATENCY_THRESHOLD_MS` (default: 500ms)

## CI/CD & Deployment

**Hosting:**
- Runs as MCP server (stdio transport)
- Designed for local execution with AI assistants (Claude, etc.)

**CI Pipeline:**
- GitHub Actions (`.github/` directory present)
- Ruff for linting
- Pyright for type checking
- pytest for testing (80% coverage minimum)
- pip-audit for security scanning

## Environment Configuration

**Required Environment Variables:**
```
OPENAI_API_KEY      # OpenAI API key for embeddings
QDRANT_URL          # Qdrant Cloud cluster URL
QDRANT_API_KEY      # Qdrant Cloud API key
```

**Optional Environment Variables:**
```
VECTOR_STORE        # "qdrant" (default) or "chromadb"
EMBEDDING_MODEL     # default: "text-embedding-3-small"
EMBEDDING_DIMENSIONS # default: 1536
QDRANT_COLLECTION   # default: "se_knowledge_base"
QDRANT_HYBRID_SEARCH # default: "true"
CHROMADB_PATH       # default: "./collections/chromadb"
CHROMADB_COLLECTION # default: "se_knowledge_base"
CHUNK_MAX_TOKENS    # default: 512
CHUNK_TOKENIZER     # default: "cl100k_base"
CHUNK_MERGE_PEERS   # default: "true"
DOCLING_OCR_ENABLED # default: "false"
DOCLING_TABLE_MODE  # default: "accurate"
LOG_LEVEL           # default: "INFO"
LOG_FORMAT          # default: "text"
HEALTH_LATENCY_THRESHOLD_MS # default: 500
```

**Secrets Location:**
- Environment variables loaded from `.env` files
- `.env` files searched in cwd and parent directories
- `.env` is gitignored (use `.env.example` as template)

## Webhooks & Callbacks

**Incoming:**
- None (MCP server uses stdio transport, not HTTP)

**Outgoing:**
- None (all external calls are synchronous API requests)

## MCP Protocol Integration

**Server Implementation:**
- Location: `src/knowledge_mcp/server.py`
- Transport: stdio (via `mcp.server.stdio.stdio_server`)
- Protocol: Model Context Protocol (MCP)

**Tool Registration:**
- Tools registered via `@self.server.list_tools()` decorator
- Tool invocations handled via `@self.server.call_tool()` decorator
- Current status: Tool registration scaffolded (TASK-024 pending)

**Graceful Shutdown:**
- SIGINT/SIGTERM handlers on Unix platforms
- Cancels all asyncio tasks on shutdown

## Data Flow Summary

```
[Document Files]
      |
      v
[DoclingIngestor] -- Docling AI models
      |
      v
[DoclingChunker] -- tiktoken tokenization
      |
      v
[OpenAIEmbedder] -- OpenAI API
      |
      v
[QdrantStore/ChromaDBStore] -- Vector DB
      |
      v
[MCP Server] -- stdio to AI assistant
```

---

*Integration audit: 2026-01-20*
