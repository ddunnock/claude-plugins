# External Integrations

**Analysis Date:** 2026-01-23

## APIs & External Services

**AI/Embeddings:**
- OpenAI - Text embeddings and semantic search capability
  - SDK/Client: `openai` package (>= 1.0.0)
  - Models: `text-embedding-3-small` (1536 dimensions, recommended), `text-embedding-3-large` (3072 dimensions), `text-embedding-ada-002` (legacy)
  - Auth: `OPENAI_API_KEY` environment variable
  - Usage: `mcps/session-memory/server.py`, `mcps/knowledge-mcp/`
  - Optional features: semantic search, entity learning, auto-embeddings for events

**Reranking (Optional):**
- Cohere - Result reranking for improved search relevance
  - SDK/Client: `cohere` package (>= 4.0.0)
  - Auth: `COHERE_API_KEY` environment variable
  - Usage: Knowledge MCP optional reranking feature
  - Feature flag: `USE_RERANKING` (default: false)

## Data Storage

**Vector Databases:**
- Qdrant Cloud (PRIMARY)
  - Provider: Cloud-hosted Qdrant vector database
  - Connection: HTTPS to Qdrant Cloud cluster
  - URL format: `https://<cluster-id>.<region>.gcp.cloud.qdrant.io`
  - Auth: `QDRANT_URL`, `QDRANT_API_KEY` environment variables
  - Client: `qdrant-client` package (>= 1.7.0)
  - Usage: `mcps/knowledge-mcp/`
  - Features: Hybrid search (dense + sparse), configurable collection names
  - Config: `QDRANT_COLLECTION` (default: "se_knowledge_base"), `QDRANT_HYBRID_SEARCH` (default: true)

- ChromaDB (LOCAL FALLBACK)
  - Provider: Local persistent vector store
  - Connection: File-based local storage
  - Path: `CHROMADB_PATH` (default: "./collections/chromadb")
  - Client: `chromadb` package (>= 0.4.0, optional dependency group)
  - Usage: Knowledge MCP fallback when offline or testing
  - Config: `CHROMADB_COLLECTION` (default: "se_knowledge_base")

**Relational Database:**
- SQLite (LOCAL)
  - Purpose: Event indexing and metadata for session memory
  - Location: `mcps/session-memory/storage/index.sqlite`
  - Usage: `mcps/session-memory/server.py`
  - Stores: Checkpoint metadata, indexed event lookups, session state
  - No external connection required (embedded)

**File Storage:**
- Local Filesystem (PRIMARY)
  - JSONL format: `mcps/session-memory/storage/events.jsonl` (event log)
  - Directory: `mcps/session-memory/storage/checkpoints/` (session checkpoints)
  - Handoffs: `mcps/session-memory/handoffs/` (session handoff summaries)

- Cloudflare R2 Object Storage (OPTIONAL SYNC)
  - Provider: Cloudflare R2 (S3-compatible)
  - Bucket: `CF_R2_BUCKET` environment variable (default: "session-memory-sync")
  - Auth: `CF_R2_ACCESS_KEY_ID`, `CF_R2_SECRET_ACCESS_KEY` environment variables
  - Endpoint: `CF_R2_ENDPOINT_URL` environment variable
  - Client: boto3 package (>= 1.34.0, optional)
  - Usage: Cloud sync feature in session-memory
  - Config: `cloud_sync.r2_*` in `config.json`

**Databases (Cloud):**
- Cloudflare D1 (SQLite)
  - Provider: Cloudflare D1 serverless SQL database
  - Database ID: `CF_D1_DATABASE_ID` environment variable
  - Auth: `CF_ACCOUNT_ID`, `CF_API_TOKEN` environment variables
  - Client: httpx package (>= 0.25.0, for REST API calls)
  - Usage: Cloud sync feature in session-memory (optional)
  - Config: `cloud_sync.d1_database_id` in `config.json`

## Authentication & Identity

**Auth Provider:**
- Custom (Environment Variable-based)
  - Implementation: Direct API key environment variables
  - No OAuth/OIDC integration currently
  - Keys managed via:
    - `.env` files (development)
    - Environment setup (production/Claude Desktop)
    - `~/.claude/.env` (global Claude defaults)

**Environment Variables Used:**
- `OPENAI_API_KEY` - OpenAI API authentication
- `QDRANT_API_KEY` - Qdrant Cloud authentication
- `CF_ACCOUNT_ID`, `CF_API_TOKEN` - Cloudflare account authentication
- `CF_R2_ACCESS_KEY_ID`, `CF_R2_SECRET_ACCESS_KEY` - R2 object storage credentials
- `COHERE_API_KEY` - Cohere API authentication (optional)

## Monitoring & Observability

**Logging:**
- Approach: Python standard logging via `logging` module
- Configuration: `LOG_LEVEL` environment variable (DEBUG, INFO, WARNING, ERROR)
- Output: stderr/stdout (Claude Desktop captures logs)
- Usage: `mcps/session-memory/server.py`, `mcps/knowledge-mcp/`

**Error Tracking:**
- None detected - errors logged to console/stderr

**Observability:**
- Checkpoint system: `mcps/session-memory/` tracks session state snapshots
- Event log: JSONL file provides audit trail of session events
- Metrics: Session-specific configuration tracks auto-checkpoint intervals and counts

## CI/CD & Deployment

**Hosting:**
- Claude Desktop - Primary deployment target
  - Configuration: `~/.config/claude/claude_desktop_config.json`
  - Entry point: Plugins run via Python subprocess (stdio communication with MCP SDK)
  - Example config:
    ```json
    {
      "mcpServers": {
        "session-memory": {
          "command": "python3",
          "args": ["~/.claude/session-memory/server.py"]
        }
      }
    }
    ```

**Deployment Method:**
- Package plugins as `.plugin` files using `tools/package_plugin.py`
- Install via `tools/install_mcp.py` (copies to `~/.claude/` or symlink for development)
- Skills loaded directly from `skills/` directory when registered in Claude

**CI Pipeline:**
- Not detected - no automated CI configuration found
- Manual testing and validation recommended using `tools/validate_plugin.py`

## Environment Configuration

**Required Environment Variables:**
- `OPENAI_API_KEY` - Essential for embeddings (semantic search, entity learning)
- `QDRANT_URL`, `QDRANT_API_KEY` - For Knowledge MCP vector search
- `QDRANT_COLLECTION` - Knowledge base collection name (default: "se_knowledge_base")

**Optional Environment Variables:**
- `QDRANT_HYBRID_SEARCH` - Enable hybrid search (default: true)
- `CHROMADB_PATH`, `CHROMADB_COLLECTION` - ChromaDB fallback configuration
- `CF_ACCOUNT_ID`, `CF_API_TOKEN` - Cloudflare account for D1/R2 sync
- `CF_D1_DATABASE_ID` - D1 database ID (preset in config.json: "07385c98-49e6-4137-b3c5-9ae8fb87664d")
- `CF_R2_BUCKET`, `CF_R2_*` - R2 bucket and credentials for object storage
- `COHERE_API_KEY`, `USE_RERANKING` - Cohere reranking (disabled by default)
- `USE_LOCAL_EMBEDDINGS`, `LOCAL_EMBEDDING_MODEL` - Offline embedding fallback
- `LOG_LEVEL` - Logging verbosity (default: INFO)
- `CHUNK_SIZE_MIN`, `CHUNK_SIZE_MAX`, `CHUNK_OVERLAP` - Document chunking parameters
- `SOURCES_PATH`, `PROCESSED_PATH` - Document processing directories

**Configuration Loading:**
- `.env` file in project root (highest priority)
- `~/.claude/.env` global defaults (fallback)
- Explicit environment variables (highest absolute priority)
- python-dotenv handles loading (optional dependency, graceful if missing)

**Secrets Location:**
- `.env` files (gitignored, never committed)
- `.env.example` provides template
- Example: `mcps/knowledge-mcp/.env.example`, `mcps/session-memory/.env.example`

## Webhooks & Callbacks

**Incoming:**
- Session handoff notifications - `mcps/session-memory/handoffs/` (file-based)
- No HTTP webhook endpoints exposed

**Outgoing:**
- Cloudflare D1 API calls (via httpx) - Cloud sync feature
- Cloudflare R2 API calls (via boto3) - Object storage sync
- OpenAI API calls - Embedding generation requests
- Qdrant Cloud API calls - Vector search and storage operations

## Plugin Integration Points

**Skill Loading:**
- `.claude-plugin/plugin.json` manifest in each skill directory
- Metadata: name, description, version, author, license, repository, keywords
- No external dependencies beyond SKILL.md format

**MCP Server Registration:**
- Entry point: `server.py` (Python)
- Protocol: stdio communication with MCP SDK
- Tools: Defined as Tool objects with descriptions and input schemas
- Plugin config: `.claude-plugin/plugin.json` specifies entry command

## Document Processing Pipeline

**Ingestion:**
- Input formats: PDF, DOCX, Markdown, HTML
- Processors: `pymupdf4llm`, `python-docx`, `mammoth`, `beautifulsoup4`
- Output: Chunks with embeddings (via OpenAI API)

**Chunking:**
- Strategy: Token-based splitting with configurable overlap
- Parameters: min/max chunk size, overlap (tokens)
- Configuration: `CHUNK_SIZE_*`, `CHUNK_OVERLAP` env vars
- Tools: `tiktoken` for accurate token counting

**Storage:**
- Chunks stored in Qdrant Cloud with vector embeddings
- Metadata: document_title, source, chunk_id, created_at

---

*Integration audit: 2026-01-23*
