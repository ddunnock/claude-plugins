# Technology Stack

**Analysis Date:** 2026-01-20

## Languages

**Primary:**
- Python >=3.11,<3.14 - All application code in `src/knowledge_mcp/`

**Configuration:**
- TOML - `pyproject.toml` for project configuration

## Runtime

**Environment:**
- Python 3.11+ (target version: 3.11)
- Virtual environment via Poetry (`.venv/`)

**Package Manager:**
- Poetry (build-backend: `poetry.core.masonry.api`)
- Lockfile: `poetry.lock` (committed, 627KB)

## Frameworks

**Core:**
- MCP SDK (`mcp>=1.0.0`) - Model Context Protocol server implementation
- Pydantic (`>=2.0.0`) - Data validation and configuration

**Document Processing:**
- Docling (`>=2.15.0`) - Unified document parsing (PDF, DOCX, PPTX, XLSX, HTML, images)
- Docling-Core (`>=2.15.0` with `[chunking]` extra) - Document chunking with HybridChunker

**Vector Storage:**
- Qdrant Client (`>=1.7.0`) - Primary vector store (Qdrant Cloud)
- ChromaDB (`>=0.4.0`) - Optional local fallback (in `chromadb` extra group)

**Embeddings:**
- OpenAI SDK (`>=1.0.0`) - `text-embedding-3-small` embeddings (1536 dimensions)
- tiktoken (`>=0.5.0`) - Token counting for chunk size control

**Utilities:**
- tenacity (`>=8.0.0`) - Retry logic with exponential backoff
- python-dotenv (`>=1.0.0`) - Environment variable loading
- rich (`>=13.0.0`) - Console output formatting

**Testing:**
- pytest (`^8.0`) - Test framework
- pytest-cov (`^4.1`) - Coverage reporting
- pytest-asyncio (`^0.23`) - Async test support

**Code Quality:**
- Ruff (`^0.4`) - Linting and formatting (replaces flake8, black, isort)
- Pyright (`^1.1`) - Static type checking (strict mode)
- pip-audit (`^2.7`) - Security vulnerability scanning

**Documentation (optional):**
- Sphinx (`^7.2`)
- Furo (`^2024.1`) - Sphinx theme
- myst-parser (`^2.0`) - Markdown support for Sphinx

## Key Dependencies

**Critical (required for operation):**
- `openai>=1.0.0` - Embedding generation (OPENAI_API_KEY required)
- `qdrant-client>=1.7.0` - Vector storage/search (QDRANT_URL, QDRANT_API_KEY required)
- `mcp>=1.0.0` - MCP protocol implementation
- `docling>=2.15.0` - Document parsing with AI models

**Infrastructure:**
- `pydantic>=2.0.0` - Configuration validation (`KnowledgeConfig` model)
- `tenacity>=8.0.0` - Resilient API calls with retry logic
- `tiktoken>=0.5.0` - Token counting (uses `cl100k_base` tokenizer)

**Optional Groups:**
- `chromadb` - Local vector store fallback
- `rerank` - Cohere reranking for better results
- `local` - Local embedding models (sentence-transformers)
- `docs` - Documentation generation

## Configuration

**Environment Variables:**
Required (validated at startup via `KnowledgeConfig.check_config()`):
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `QDRANT_URL` - Qdrant Cloud cluster URL (when using Qdrant)
- `QDRANT_API_KEY` - Qdrant Cloud API key (when using Qdrant)

Optional (with defaults):
- `EMBEDDING_MODEL` - default: `text-embedding-3-small`
- `EMBEDDING_DIMENSIONS` - default: `1536`
- `VECTOR_STORE` - default: `qdrant` (or `chromadb`)
- `QDRANT_COLLECTION` - default: `se_knowledge_base`
- `QDRANT_HYBRID_SEARCH` - default: `true`
- `CHROMADB_PATH` - default: `./collections/chromadb`
- `CHROMADB_COLLECTION` - default: `se_knowledge_base`
- `CHUNK_MAX_TOKENS` - default: `512` (range: 100-2000)
- `CHUNK_TOKENIZER` - default: `cl100k_base`
- `CHUNK_MERGE_PEERS` - default: `true`
- `DOCLING_OCR_ENABLED` - default: `false`
- `DOCLING_TABLE_MODE` - default: `accurate` (or `fast`)
- `LOG_LEVEL` - default: `INFO`
- `LOG_FORMAT` - default: `text` (or `json`)
- `HEALTH_LATENCY_THRESHOLD_MS` - default: `500`

**Configuration Loading:**
- `.env` files searched in cwd and parent directories
- Uses `python-dotenv` for loading
- Validated by Pydantic model: `src/knowledge_mcp/utils/config.py`

**Build/Dev Configuration:**
- `pyproject.toml` - All tool configuration consolidated
  - `[tool.ruff]` - Linting (line-length: 100, target: py311)
  - `[tool.pyright]` - Type checking (strict mode)
  - `[tool.pytest.ini_options]` - Testing (asyncio_mode: auto, cov-fail-under: 80)
  - `[tool.coverage]` - Coverage settings (branch: true)

## Platform Requirements

**Development:**
- Python >=3.11,<3.14
- Poetry for dependency management
- Git for version control

**Production:**
- Python 3.11+ runtime
- Network access to OpenAI API
- Network access to Qdrant Cloud (or local ChromaDB path)
- Sufficient memory for Docling AI models (DocLayNet, TableFormer)

**Deployment:**
- Runs as MCP server via stdio transport
- Entry point: `python -m knowledge_mcp` or `knowledge-mcp` CLI
- Graceful shutdown on SIGINT/SIGTERM

## Scripts/Commands

**Defined in pyproject.toml:**
```bash
knowledge-mcp          # CLI entry point -> knowledge_mcp.__main__:cli
knowledge-ingest       # Document ingestion -> knowledge_mcp.cli.ingest:main
```

**Development Commands:**
```bash
poetry install                    # Install all dependencies
poetry install --with chromadb    # Include ChromaDB fallback
poetry install --with docs        # Include documentation tools

poetry run pytest                 # Run tests with coverage
poetry run ruff check src tests   # Lint code
poetry run ruff format src tests  # Format code
poetry run pyright                # Type check
poetry run pip-audit              # Security scan
```

---

*Stack analysis: 2026-01-20*
