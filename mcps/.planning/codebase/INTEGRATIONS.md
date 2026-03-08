# External Integrations

**Analysis Date:** 2026-03-08

## APIs & External Services

**AI/Embeddings:**
- OpenAI API - Embedding generation for semantic search (both knowledge-mcp and session-memory)
  - SDK/Client: `openai >=1.0.0`
  - Auth: `OPENAI_API_KEY` env var
  - Model: `text-embedding-3-small` (1536 dimensions, configurable via `EMBEDDING_MODEL`)
  - Used in: `knowledge-mcp/src/knowledge_mcp/embed/openai_embedder.py`, `session-memory/modules/embeddings.py`

**Reranking (Optional):**
- Cohere API - Result reranking for improved search precision
  - SDK/Client: `cohere >=5.11.0` (optional dependency group)
  - Auth: Cohere API key (env var)
  - Used in: `knowledge-mcp/src/knowledge_mcp/search/reranker.py` (lazy import)

## Data Storage

**Vector Databases:**
- Qdrant Cloud (PRIMARY vector store for knowledge-mcp)
  - Client: `qdrant-client >=1.16.2`
  - Connection: `QDRANT_URL` env var (cluster URL)
  - Auth: `QDRANT_API_KEY` env var
  - Collection: configurable via `QDRANT_COLLECTION` (default: `se_knowledge_base`, versioned with model name)
  - Features: hybrid search enabled by default (`QDRANT_HYBRID_SEARCH=true`)
  - Config: `knowledge-mcp/src/knowledge_mcp/utils/config.py`

- ChromaDB (LOCAL FALLBACK vector store for knowledge-mcp)
  - Client: `chromadb >=0.4.0` (optional dependency group)
  - Storage: local filesystem at `CHROMADB_PATH` (default: `./collections/chromadb`)
  - Used when: `VECTOR_STORE=chromadb` or as fallback when Qdrant unavailable

**Relational Databases:**
- PostgreSQL (knowledge-mcp metadata store)
  - Client: SQLAlchemy 2.0 async + asyncpg
  - Connection: `DATABASE_URL` env var (format: `postgresql+asyncpg://...`)
  - Pool: configurable size (default 15) and overflow (default 10)
  - Migrations: Alembic in `knowledge-mcp/src/knowledge_mcp/db/migrations/`
  - Engine: `knowledge-mcp/src/knowledge_mcp/db/engine.py`
  - Models: `knowledge-mcp/src/knowledge_mcp/db/models.py`
  - Can bypass with `OFFLINE_MODE=true`

- SQLite (session-memory event index)
  - Client: Python stdlib `sqlite3`
  - Storage: `session-memory/storage/index.sqlite`
  - No ORM; direct SQL queries in `session-memory/server.py`

- SQLite (streaming-output document store)
  - Client: Python stdlib `sqlite3`
  - Storage: `~/.claude/streaming-output/streams.db`
  - No ORM; direct SQL queries in `streaming-output/server.py`

**File Storage:**
- Local filesystem for session-memory events: `session-memory/storage/events.jsonl`
- Local filesystem for session-memory checkpoints: `session-memory/storage/checkpoints/`
- Local filesystem for knowledge-mcp source documents: `knowledge-mcp/data/sources/`
- Local filesystem for knowledge-mcp embedding cache: `knowledge-mcp/data/embeddings/cache/` (via `diskcache`)
- Cloudflare R2 for session-memory cloud sync (S3-compatible, see below)

**Caching:**
- diskcache (knowledge-mcp embedding cache)
  - Package: `diskcache >=5.6.0`
  - Location: configurable via `CACHE_DIR` (default: `./data/embeddings/cache`)
  - Size limit: configurable via `CACHE_SIZE_LIMIT` (default: 10GB)
  - Implementation: `knowledge-mcp/src/knowledge_mcp/embed/cache.py`

## Authentication & Identity

**Auth Provider:**
- No user authentication system; these are local MCP servers
- API keys are passed via environment variables for external services
- Claude Desktop/Code invokes servers as local processes

## Cloud Sync (session-memory)

**Cloudflare D1 (SQL database sync):**
- Purpose: Sync session events to cloud for cross-device access
- Auth: `CF_ACCOUNT_ID`, `CF_API_TOKEN` env vars
- Database ID: configured in `session-memory/config.json` (`CF_D1_DATABASE_ID`)
- Client: `httpx >=0.25.0` (Cloudflare REST API)
- Implementation: `session-memory/modules/cloud_sync.py`

**Cloudflare R2 (object storage sync):**
- Purpose: Sync large session artifacts (checkpoints, documents)
- Bucket: `session-memory-sync` (configured in `session-memory/config.json`)
- Auth: `CF_R2_ENDPOINT_URL`, `CF_R2_ACCESS_KEY_ID`, `CF_R2_SECRET_ACCESS_KEY` env vars
- Client: `boto3 >=1.34.0` (S3-compatible API)
- Implementation: `session-memory/modules/cloud_sync.py`

## Monitoring & Observability

**Error Tracking:**
- No external error tracking service (Sentry, etc.)
- Errors returned as structured JSON in MCP tool responses

**Logs:**
- knowledge-mcp: structured logging via `knowledge-mcp/src/knowledge_mcp/utils/logging.py`
  - Dev dependency: `python-json-logger >=2.0.0`
- session-memory/streaming-output: Python stdlib logging

**Token Usage Tracking (knowledge-mcp):**
- Built-in OpenAI token usage tracking
- Log file: configurable via `TOKEN_LOG_FILE` (default: `./data/token_usage.json`)
- Warning threshold: `DAILY_TOKEN_WARNING_THRESHOLD` (default: 1,000,000 tokens)
- CLI summary: `knowledge-mcp/src/knowledge_mcp/cli/token_summary.py`

## CI/CD & Deployment

**Hosting:**
- Local execution only; MCP servers run as stdio processes on the developer machine
- Invoked by Claude Desktop or Claude Code via plugin manifests

**CI Pipeline:**
- Dependabot configured at repo root: `.github/dependabot.yml`
- No CI workflow files detected in `.github/workflows/`

**Plugin Distribution:**
- Claude plugin format via `.claude-plugin/plugin.json` in each server directory
- knowledge-mcp version: 0.1.3
- session-memory version: 1.0.1

## Environment Configuration

**Required env vars (knowledge-mcp, full mode):**
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `QDRANT_URL` - Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Qdrant Cloud API key
- `DATABASE_URL` - PostgreSQL connection string (`postgresql+asyncpg://...`)

**Required env vars (knowledge-mcp, offline mode):**
- `OPENAI_API_KEY` - OpenAI API key (or use `EMBEDDING_PROVIDER=local` for no API keys)
- `OFFLINE_MODE=true` - Bypasses PostgreSQL requirement, uses ChromaDB

**Required env vars (session-memory, minimal):**
- None (base functionality works without env vars)

**Optional env vars (session-memory features):**
- `OPENAI_API_KEY` - For semantic search embeddings
- `CF_ACCOUNT_ID` - Cloudflare account for cloud sync
- `CF_API_TOKEN` - Cloudflare API token for cloud sync
- `CF_R2_ENDPOINT_URL`, `CF_R2_ACCESS_KEY_ID`, `CF_R2_SECRET_ACCESS_KEY` - R2 storage

**Secrets location:**
- `.env` files (gitignored) in project directories
- `~/.claude/.env` as global fallback
- `.env.example` template at `knowledge-mcp/.env.example`

## Webhooks & Callbacks

**Incoming:**
- None (MCP servers use stdio transport, not HTTP)

**Outgoing:**
- None

## Document Ingestion Integrations

**Supported formats (knowledge-mcp):**
- PDF: `pymupdf4llm >=0.0.5` - `knowledge-mcp/src/knowledge_mcp/ingest/pdf_ingestor.py`
- DOCX: `python-docx >=1.1.0`, `mammoth >=1.8.0` - `knowledge-mcp/src/knowledge_mcp/ingest/docx_ingestor.py`
- Web/HTML: `crawl4ai >=0.8.0` - `knowledge-mcp/src/knowledge_mcp/ingest/web_ingestor.py`
- Advanced parsing: `docling >=2.70.0` - Multi-format document understanding

**Supported formats (session-memory):**
- PDF: `PyPDF2 >=3.0.0`
- DOCX: `python-docx >=1.0.0`
- HTML: `beautifulsoup4 >=4.12.0`, `lxml >=4.9`
- Implementation: `session-memory/modules/document_ingest.py`

---

*Integration audit: 2026-03-08*
