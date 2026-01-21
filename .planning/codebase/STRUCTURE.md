# Codebase Structure

**Analysis Date:** 2026-01-20

## Directory Layout

```
knowledge-mcp/
├── src/
│   └── knowledge_mcp/           # Main package (src layout)
│       ├── __init__.py          # Package exports, version
│       ├── __main__.py          # CLI entry point
│       ├── server.py            # MCP server implementation
│       ├── exceptions.py        # Exception hierarchy
│       ├── ingest/              # Document parsing
│       ├── chunk/               # Document chunking
│       ├── embed/               # Embedding generation
│       ├── store/               # Vector storage
│       ├── search/              # Search (stub)
│       ├── models/              # Data models
│       ├── utils/               # Configuration, logging
│       └── cli/                 # CLI commands (stub)
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data
├── docs/                        # Documentation (Diataxis)
├── data/                        # Document storage
├── collections/                 # ChromaDB local storage
├── .planning/                   # GSD planning documents
├── speckit/                     # Specification documents
├── pyproject.toml               # Poetry configuration
└── CLAUDE.md                    # Claude development standards
```

## Directory Purposes

**`src/knowledge_mcp/`:**
- Purpose: Main application package using src layout
- Contains: All production Python code
- Key files: `__init__.py` (public API), `server.py` (MCP server), `exceptions.py` (error types)

**`src/knowledge_mcp/ingest/`:**
- Purpose: Document format parsing and content extraction
- Contains: `DoclingIngestor`, base classes, registry functions
- Key files: `docling_ingestor.py`, `base.py`

**`src/knowledge_mcp/chunk/`:**
- Purpose: Document chunking strategies
- Contains: `DoclingChunker` using Docling HybridChunker
- Key files: `docling_chunker.py`, `base.py`

**`src/knowledge_mcp/embed/`:**
- Purpose: Text embedding generation
- Contains: `OpenAIEmbedder`, base interface
- Key files: `openai_embedder.py`, `base.py`

**`src/knowledge_mcp/store/`:**
- Purpose: Vector database operations
- Contains: `QdrantStore` (primary), `ChromaDBStore` (fallback), factory
- Key files: `qdrant_store.py`, `chromadb_store.py`, `base.py`, `__init__.py` (factory)

**`src/knowledge_mcp/models/`:**
- Purpose: Core data models and enums
- Contains: `KnowledgeChunk`, type enums
- Key files: `chunk.py`, `enums.py`

**`src/knowledge_mcp/utils/`:**
- Purpose: Shared utilities
- Contains: Configuration loading, logging setup
- Key files: `config.py`, `logging.py`

**`src/knowledge_mcp/search/`:**
- Purpose: Search and retrieval (stub)
- Contains: Empty `__init__.py`, awaiting implementation
- Key files: (none yet)

**`src/knowledge_mcp/cli/`:**
- Purpose: CLI commands (stub)
- Contains: Empty `__init__.py`, awaiting implementation
- Key files: (none yet)

**`tests/`:**
- Purpose: Test suite
- Contains: Unit and integration tests organized by module
- Key files: `conftest.py` (shared fixtures)

**`tests/unit/`:**
- Purpose: Unit tests mirroring src structure
- Contains: `test_chunk/`, `test_embed/`, `test_ingest/`, `test_models/`, `test_store/`
- Key files: Individual test modules

**`tests/integration/`:**
- Purpose: Integration tests requiring external services
- Contains: End-to-end pipeline tests (sparse)
- Key files: (being developed)

**`docs/`:**
- Purpose: Documentation following Diataxis framework
- Contains: `tutorials/`, `how-to/`, `reference/`, `explanation/`
- Key files: (minimal)

**`speckit/`:**
- Purpose: Project specification documents
- Contains: `spec.md`, `plan.md`, `designs/`, `plans/`
- Key files: Project planning artifacts

## Key File Locations

**Entry Points:**
- `src/knowledge_mcp/__main__.py`: CLI entry point (`python -m knowledge_mcp`)
- `src/knowledge_mcp/server.py`: `KnowledgeMCPServer` class, `main()` function

**Configuration:**
- `pyproject.toml`: Poetry deps, ruff/pyright config, pytest settings
- `src/knowledge_mcp/utils/config.py`: `KnowledgeConfig`, `load_config()`
- `.env` (gitignored): Environment variables

**Core Logic:**
- `src/knowledge_mcp/ingest/docling_ingestor.py`: Document parsing
- `src/knowledge_mcp/chunk/docling_chunker.py`: Chunking logic
- `src/knowledge_mcp/embed/openai_embedder.py`: OpenAI embeddings
- `src/knowledge_mcp/store/qdrant_store.py`: Qdrant operations
- `src/knowledge_mcp/store/__init__.py`: `create_store()` factory with fallback

**Data Models:**
- `src/knowledge_mcp/models/chunk.py`: `KnowledgeChunk` model
- `src/knowledge_mcp/models/enums.py`: `ChunkType`, `DocumentType`, `ErrorCode`
- `src/knowledge_mcp/exceptions.py`: Exception hierarchy

**Testing:**
- `tests/conftest.py`: Shared pytest fixtures
- `tests/unit/test_*/`: Module-specific unit tests

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `qdrant_store.py`, `openai_embedder.py`)
- Base classes: `base.py` in each subpackage
- Test files: `test_<module>.py` (e.g., `test_openai_embedder.py`)

**Directories:**
- Subpackages: `snake_case/` (e.g., `ingest/`, `chunk/`, `embed/`, `store/`)
- Test directories: `test_<subpackage>/` (e.g., `test_chunk/`, `test_store/`)

**Classes:**
- PascalCase with descriptive names
- Base classes: `Base<Concept>` (e.g., `BaseStore`, `BaseChunker`)
- Implementations: `<Provider><Concept>` (e.g., `QdrantStore`, `DoclingChunker`)

**Functions:**
- `snake_case` for all functions
- Factory functions: `create_<thing>` (e.g., `create_store`)
- Getters: `get_<thing>` (e.g., `get_ingestor`, `get_logger`)

## Where to Add New Code

**New Ingestor (e.g., for new file format):**
- Implementation: `src/knowledge_mcp/ingest/<format>_ingestor.py`
- Tests: `tests/unit/test_ingest/test_<format>_ingestor.py`
- Register with `@register_ingestor` decorator

**New Chunking Strategy:**
- Implementation: `src/knowledge_mcp/chunk/<strategy>_chunker.py`
- Tests: `tests/unit/test_chunk/test_<strategy>_chunker.py`
- Inherit from `BaseChunker`

**New Embedding Provider:**
- Implementation: `src/knowledge_mcp/embed/<provider>_embedder.py`
- Tests: `tests/unit/test_embed/test_<provider>_embedder.py`
- Inherit from `BaseEmbedder`

**New Vector Store:**
- Implementation: `src/knowledge_mcp/store/<provider>_store.py`
- Tests: `tests/unit/test_store/test_<provider>_store.py`
- Inherit from `BaseStore`, add to `create_store()` factory

**New MCP Tool:**
- Implementation: Add handler in `src/knowledge_mcp/server.py` `_setup_handlers()`
- Tests: `tests/unit/test_server.py` or `tests/integration/test_server.py`

**New CLI Command:**
- Implementation: `src/knowledge_mcp/cli/<command>.py`
- Entry point: Add to `pyproject.toml` `[tool.poetry.scripts]`
- Tests: `tests/unit/test_cli/test_<command>.py`

**New Data Model:**
- Implementation: `src/knowledge_mcp/models/<model>.py`
- Tests: `tests/unit/test_models/test_<model>.py`
- Export from `src/knowledge_mcp/models/__init__.py`

**Utilities:**
- Shared helpers: `src/knowledge_mcp/utils/<helper>.py`
- Export from `src/knowledge_mcp/utils/__init__.py`

## Special Directories

**`.planning/`:**
- Purpose: GSD planning and codebase analysis documents
- Generated: By GSD commands
- Committed: Selectively (codebase/* yes, others optional)

**`speckit/`:**
- Purpose: Project specification and planning artifacts
- Generated: Via speckit workflow
- Committed: Yes

**`collections/`:**
- Purpose: ChromaDB local persistent storage
- Generated: At runtime when using ChromaDB
- Committed: No (gitignored)

**`data/`:**
- Purpose: Source documents for ingestion
- Generated: User-provided
- Committed: No (gitignored, except samples)

**`.venv/`:**
- Purpose: Poetry virtual environment
- Generated: By `poetry install`
- Committed: No (gitignored)

---

*Structure analysis: 2026-01-20*
