# Technology Stack

**Analysis Date:** 2026-03-08

## Languages

**Primary:**
- Python >=3.11,<3.14 - All three MCP servers (knowledge-mcp, session-memory, streaming-output)

**Secondary:**
- SQL - Alembic migrations in `knowledge-mcp/src/knowledge_mcp/db/migrations/versions/`
- Bash - Packaging script at `knowledge-mcp/scripts/package_mcpb.sh`

## Runtime

**Environment:**
- Python 3.11+ (target version in ruff/pyright config)
- CPython (standard interpreter)

**Package Manager:**
- Poetry (knowledge-mcp) - `knowledge-mcp/pyproject.toml`, lockfile: `knowledge-mcp/poetry.lock` (present)
- pip/requirements.txt (session-memory) - `session-memory/requirements.txt`
- pip/requirements.txt (root-level) - `requirements.txt`
- No package manager for streaming-output (single-file server)

## Frameworks

**Core:**
- MCP SDK `>=1.25.0,<2` - Model Context Protocol server framework; all three servers use `mcp.server.Server` and `mcp.server.stdio.stdio_server`
- Pydantic `>=2.0.0` - Data validation and configuration models (knowledge-mcp)
- SQLAlchemy `^2.0.25` (async) - PostgreSQL ORM for knowledge-mcp metadata store
- Alembic `^1.13.1` - Database migrations for knowledge-mcp

**Testing:**
- pytest `^8.0` - Test runner
- pytest-asyncio `^0.23` - Async test support (asyncio_mode = "auto")
- pytest-cov `^4.1` - Coverage reporting (minimum 80% line coverage)
- pytest-golden `>=0.2.0` - Golden file testing
- ragas `>=0.2.0` - RAG evaluation framework (dev dependency)

**Build/Dev:**
- Ruff `^0.4` - Linting and formatting (line-length=100, target-version=py311)
- Pyright `^1.1` - Type checking (strict mode)
- pip-audit `^2.7` - Dependency security scanning

## Key Dependencies

**Critical (knowledge-mcp):**
- `openai >=1.0.0` - Embedding generation via text-embedding-3-small (1536 dimensions)
- `qdrant-client >=1.16.2` - Primary vector store client (Qdrant Cloud)
- `asyncpg ^0.29.0` - Async PostgreSQL driver for SQLAlchemy
- `tiktoken >=0.5.0` - Token counting for chunking
- `bm25s >=0.1.0` - BM25 lexical search for hybrid retrieval

**Document Processing (knowledge-mcp):**
- `pymupdf4llm >=0.0.5` - PDF parsing optimized for LLM consumption
- `python-docx >=1.1.0` - DOCX file parsing
- `mammoth >=1.8.0` - DOCX to HTML conversion
- `docling >=2.70.0` - Advanced document understanding
- `crawl4ai >=0.8.0` - Web content ingestion

**Optional (knowledge-mcp):**
- `chromadb >=0.4.0` - Local vector store fallback (optional group)
- `cohere >=5.11.0` - Reranking for improved search results (optional group)
- `sentence-transformers >=3.0.0` - Local embedding models for offline use (optional group)

**Infrastructure (knowledge-mcp):**
- `tenacity >=8.0.0` - Retry logic with exponential backoff
- `diskcache >=5.6.0` - Persistent embedding cache
- `rich >=13.0.0` - Terminal output formatting
- `typer >=0.12.0` - CLI framework
- `python-dotenv >=1.0.0` - Environment variable loading from .env files

**Session-memory specific:**
- `httpx >=0.25.0` - HTTP client for Cloudflare D1/R2 cloud sync
- `boto3 >=1.34.0` - AWS SDK for Cloudflare R2 (S3-compatible) object storage
- `openai >=1.0.0` - Embeddings for semantic search over session events
- `PyPDF2 >=3.0.0` - PDF document ingestion
- `beautifulsoup4 >=4.12.0` - HTML parsing for document ingestion

**Streaming-output:**
- `mcp >=1.0.0` - MCP SDK (only dependency; uses stdlib sqlite3)

## Configuration

**Environment:**
- All servers use environment variables loaded from `.env` files via `python-dotenv`
- knowledge-mcp validates config at startup via `KnowledgeConfig.validate()` in `knowledge-mcp/src/knowledge_mcp/utils/config.py`
- session-memory reads config from `session-memory/config.json` for feature flags
- streaming-output has no external config (stores data at `~/.claude/streaming-output/streams.db`)

**Build:**
- `knowledge-mcp/pyproject.toml` - Poetry config, ruff, pyright, pytest settings
- No build step required; servers run directly via `python -m knowledge_mcp` or `python server.py`

## Platform Requirements

**Development:**
- Python 3.11+ installed
- Poetry installed (for knowledge-mcp dependency management)
- PostgreSQL instance accessible (for knowledge-mcp metadata, unless OFFLINE_MODE=true)
- OpenAI API key (for embeddings)
- Qdrant Cloud account (for vector storage, or use ChromaDB locally)

**Production:**
- Servers run as MCP stdio servers invoked by Claude Desktop/Claude Code
- Configured via Claude plugin manifests in `.claude-plugin/plugin.json` per server
- knowledge-mcp: `knowledge-mcp/.claude-plugin/plugin.json`
- session-memory: `session-memory/.claude-plugin/plugin.json`

## CLI Entry Points

**knowledge-mcp** (defined in `knowledge-mcp/pyproject.toml`):
- `knowledge` -> `knowledge_mcp.cli.main:cli`
- `knowledge-mcp` -> `knowledge_mcp.__main__:cli`
- `knowledge-ingest` -> `knowledge_mcp.cli.ingest:main`

---

*Stack analysis: 2026-03-08*
