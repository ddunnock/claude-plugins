# Technology Stack

**Analysis Date:** 2026-01-23

## Languages

**Primary:**
- Python 3.10+ - MCP servers (`mcps/session-memory/`, `mcps/knowledge-mcp/`)
- Python 3.11-3.13 - Knowledge MCP with strict typing requirements
- Markdown - Skill documentation and templates (`.skill` files)
- YAML - Configuration, plugin manifests, frontmatter

**Secondary:**
- Bash/Shell - Tool scripts and streaming output commands (`skills/streaming-output/scripts/`)

## Runtime

**Environment:**
- Python 3.10+ (standard MCPs)
- Python 3.11-3.13 (Knowledge MCP specifically, per `pyproject.toml`)
- Claude Desktop (plugin hosting environment)

**Package Manager:**
- **pip** - Standard dependency installation for MCPs
- **Poetry** - Knowledge MCP dependency management (`mcps/knowledge-mcp/pyproject.toml`)
- Lockfile: `poetry.lock` (Knowledge MCP only, committed)

## Frameworks

**Core:**
- **MCP SDK** (mcp >= 1.0.0) - Model Context Protocol implementation for tool servers
  - Used in: `mcps/session-memory/server.py`, `mcps/knowledge-mcp/`
  - Provides: Server implementation, tool definitions, stdio communication

**Data/Storage:**
- **SQLite** - Local indexing and checkpoint metadata (`mcps/session-memory/storage/index.sqlite`)
- **JSONL** - Event log storage (`mcps/session-memory/storage/events.jsonl`)

**API/HTTP:**
- **httpx** >= 0.25.0 - Async HTTP client for Cloudflare/cloud sync integration
- **boto3** >= 1.34.0 - AWS/S3-compatible object storage (optional, for R2 sync)

**Document Processing:**
- **PyMuPDF/fitz** >= 1.23.0 - PDF parsing (optional dependency)
- **python-docx** >= 0.8.11 / >= 1.1.0 - DOCX document processing
- **beautifulsoup4** >= 4.12.0 - HTML parsing (optional)
- **pymupdf4llm** >= 0.0.5 - PDF-to-text conversion (Knowledge MCP)
- **mammoth** >= 1.8.0 - DOCX to markdown conversion (Knowledge MCP)

**Embeddings/AI:**
- **openai** >= 1.0.0 - OpenAI API client for embeddings (text-embedding-3-small, text-embedding-3-large)
  - Required for semantic search in session-memory and knowledge-mcp
  - Optional dependencies: sentence-transformers (for local offline embeddings)

**Vector Database:**
- **qdrant-client** >= 1.7.0 - Qdrant Cloud vector store client (primary for Knowledge MCP)
- **chromadb** >= 0.4.0 - Local vector store fallback (optional, Knowledge MCP)
- **cohere** >= 4.0.0 - Reranking for improved search quality (optional, Knowledge MCP)

**Data Validation:**
- **pydantic** >= 2.0.0 - Data validation and configuration management (Knowledge MCP)
- **python-dotenv** >= 1.0.0 - Environment variable loading from .env files

**Utilities:**
- **tiktoken** >= 0.5.0 - Token counting for chunking (Knowledge MCP)
- **rich** >= 13.0.0 - Terminal output formatting (Knowledge MCP)
- **PyYAML** - YAML parsing for plugin validation (`tools/validate_plugin.py`)

## Configuration

**Environment:**
- **.env files** - Configuration loading via python-dotenv
  - Project root `.env` (highest priority)
  - `~/.claude/.env` (global fallback)
  - Never committed; use `.env.example` as template

**Key Configs:**
- `mcps/session-memory/config.json` - Session memory features, checkpoints, cloud sync
- `mcps/knowledge-mcp/pyproject.toml` - Dependency and tool configuration
- `skills/*/SKILL.md` - Skill manifests with frontmatter (name, description)
- `.claude-plugin/plugin.json` - Plugin metadata and MCP server entry points

**Build:**
- **Poetry** - `pyproject.toml` for Knowledge MCP (includes build-system specification)
- **Python modules** - Standard `__main__.py` entry points for CLI execution

## Platform Requirements

**Development:**
- Python 3.10+ (3.11+ recommended for Knowledge MCP)
- pip or Poetry
- Git (for version control and checkpoints)
- Claude Desktop (for plugin integration testing)

**Production:**
- Claude Desktop environment (primary deployment target)
- Python 3.10+ runtime available
- Network access to external APIs:
  - OpenAI API (for embeddings)
  - Qdrant Cloud (for vector storage)
  - Cloudflare API (for D1/R2 cloud sync, optional)
  - Cohere API (for reranking, optional)

## Dependency Management

**Critical Dependencies:**
- `mcp` - Core protocol implementation (blocks all MCP functionality)
- `openai` - Embedding generation (required for semantic search features)

**Storage Dependencies:**
- `qdrant-client` - Primary vector store for Knowledge MCP
- `chromadb` - Fallback vector store, optional grouping in Poetry

**Document Processing:**
- Optional as a group in Knowledge MCP
- PDF: PyMuPDF4llm, PyMuPDF (pymupdf)
- DOCX: python-docx, mammoth
- HTML: beautifulsoup4, lxml

**Cloud/Remote:**
- `httpx` - Cloudflare D1/R2 sync
- `boto3` - S3-compatible object storage

**Development/Quality:**
- `pytest`, `pytest-asyncio` - Testing (Knowledge MCP)
- `ruff` - Linting and formatting (Knowledge MCP)
- `pyright` - Type checking in strict mode (Knowledge MCP)
- `pip-audit` - Security scanning (Knowledge MCP)

## Version Constraints

**Python:**
- General MCPs: >= 3.10
- Knowledge MCP: >= 3.11, < 3.14 (as specified in `pyproject.toml`)

**MCP SDK:**
- session-memory: >= 1.0.0 (general), >= 1.25.0 (specific in session-memory/requirements.txt)
- knowledge-mcp: >= 1.0.0

**OpenAI:**
- >= 1.0.0 (supports modern API with structured outputs and improved async)

---

*Stack analysis: 2026-01-23*
