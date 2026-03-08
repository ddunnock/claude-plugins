# Codebase Structure

**Analysis Date:** 2026-03-08

## Directory Layout

```
mcps/                               # Workspace root (NOT git root -- git is at ~/projects/claude-plugins)
├── CLAUDE.md                       # Workspace-level instructions
├── requirements.txt                # Shared dependency list (session-memory + streaming-output)
├── .planning/                      # GSD planning files for this workspace
│   └── codebase/                   # Architecture analysis (this file)
│
├── session-memory/                 # MCP Server: persistent session memory
│   ├── server.py                   # Main server (single file, ~1900 lines)
│   ├── .claude-plugin/
│   │   └── plugin.json             # Claude plugin manifest
│   ├── plugins/                    # Plugin architecture
│   │   ├── base.py                 # SessionPlugin ABC, PluginState, ResumptionContext
│   │   ├── generic.py              # Default plugin for all skills
│   │   ├── speckit.py              # SpecKit skill plugin
│   │   └── spec_refiner.py         # Spec Refiner skill plugin
│   ├── modules/                    # Optional feature modules
│   │   ├── __init__.py             # Lazy imports
│   │   ├── embeddings.py           # OpenAI embedding service
│   │   ├── entities.py             # Knowledge graph (entities + relations)
│   │   ├── learning.py             # Cross-session learning service
│   │   ├── cloud_sync.py           # Cloudflare D1/R2 sync
│   │   └── document_ingest.py      # PDF/DOCX/HTML document ingestion
│   ├── storage/                    # Runtime data (gitignored)
│   │   ├── events.jsonl            # Event log
│   │   ├── index.sqlite            # SQLite index
│   │   └── checkpoints/            # Session checkpoints
│   │       ├── auto/
│   │       └── manual/
│   └── handoffs/                   # Session handoff summaries
│
├── knowledge-mcp/                  # MCP Server: SE knowledge base search
│   ├── CLAUDE.md                   # Project-specific development standards
│   ├── pyproject.toml              # Poetry configuration
│   ├── poetry.lock                 # Locked dependencies
│   ├── .claude-plugin/
│   │   └── plugin.json             # Claude plugin manifest
│   ├── src/
│   │   └── knowledge_mcp/          # Main package
│   │       ├── __init__.py          # Package init, exports, version
│   │       ├── __main__.py          # Entry point (server or CLI)
│   │       ├── server.py            # KnowledgeMCPServer class
│   │       ├── exceptions.py        # Custom exception hierarchy
│   │       ├── ingest/              # Document ingestion
│   │       │   ├── base.py          # BaseIngestor ABC, ParsedDocument
│   │       │   ├── pdf_ingestor.py
│   │       │   ├── docx_ingestor.py
│   │       │   ├── web_ingestor.py
│   │       │   └── pipeline.py      # Ingestion pipeline orchestration
│   │       ├── chunk/               # Chunking strategies
│   │       │   ├── base.py
│   │       │   └── hierarchical.py  # Hierarchical chunker
│   │       ├── embed/               # Embedding generation
│   │       │   ├── base.py          # BaseEmbedder ABC
│   │       │   ├── openai_embedder.py
│   │       │   ├── local_embedder.py
│   │       │   └── cache.py         # Disk-based embedding cache
│   │       ├── store/               # Vector storage
│   │       │   ├── base.py          # BaseStore ABC
│   │       │   ├── qdrant_store.py  # Primary: Qdrant Cloud
│   │       │   └── chromadb_store.py # Fallback: ChromaDB
│   │       ├── search/              # Search and retrieval
│   │       │   ├── semantic_search.py
│   │       │   ├── hybrid.py        # Hybrid search (semantic + keyword)
│   │       │   ├── bm25.py          # BM25 keyword search
│   │       │   ├── reranker.py      # Result reranking
│   │       │   ├── citation.py      # Citation formatting
│   │       │   ├── coverage.py      # Coverage gap assessment
│   │       │   ├── models.py        # SearchResult model
│   │       │   ├── workflow_search.py # WorkflowSearcher orchestrator
│   │       │   └── strategies/      # Workflow-specific strategies
│   │       │       ├── base.py      # SearchStrategy ABC, SearchQuery
│   │       │       ├── explore.py   # Multi-facet exploration
│   │       │       ├── plan.py      # Project planning support
│   │       │       ├── rcca.py      # Root cause analysis
│   │       │       └── trade_study.py # Trade study comparison
│   │       ├── tools/               # MCP tool handler implementations
│   │       │   ├── acquisition.py   # Source management handlers
│   │       │   └── workflows.py     # Workflow search handlers
│   │       ├── models/              # Core data models
│   │       │   ├── __init__.py
│   │       │   ├── chunk.py         # KnowledgeChunk dataclass
│   │       │   └── document.py      # DocumentMetadata dataclass
│   │       ├── db/                  # Database layer (SQLAlchemy)
│   │       │   ├── engine.py        # Async engine factory
│   │       │   ├── models.py        # SQLAlchemy ORM models
│   │       │   ├── repositories.py  # Repository pattern
│   │       │   └── migrations/      # Alembic migrations
│   │       │       └── versions/
│   │       ├── validation/          # Content validation
│   │       │   ├── critical_tables.py
│   │       │   ├── table_validator.py
│   │       │   └── reports.py
│   │       ├── evaluation/          # Search quality evaluation
│   │       │   ├── golden_set.py
│   │       │   ├── metrics.py
│   │       │   └── reporter.py
│   │       ├── monitoring/          # Observability
│   │       │   ├── logger.py
│   │       │   └── token_tracker.py
│   │       ├── sync/                # Offline sync
│   │       │   └── offline.py
│   │       ├── cli/                 # CLI commands (typer)
│   │       │   ├── main.py
│   │       │   ├── ingest.py
│   │       │   ├── validate.py
│   │       │   ├── verify.py
│   │       │   └── token_summary.py
│   │       └── utils/               # Utilities
│   │           ├── config.py        # Configuration loading
│   │           ├── hashing.py       # Content hashing
│   │           ├── logging.py       # Logging setup
│   │           ├── normative.py     # Normative text detection
│   │           └── tokenizer.py     # Token counting
│   ├── tests/
│   │   ├── conftest.py              # Shared test fixtures
│   │   ├── unit/                    # Unit tests (mirrors src/ structure)
│   │   │   ├── test_chunk/
│   │   │   ├── test_cli/
│   │   │   ├── test_db/
│   │   │   ├── test_embed/
│   │   │   ├── test_ingest/
│   │   │   ├── test_models/
│   │   │   ├── test_search/
│   │   │   ├── test_store/
│   │   │   ├── test_sync/
│   │   │   ├── test_utils/
│   │   │   └── test_validation/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── scripts/                     # Utility scripts
│   ├── data/                        # Runtime data
│   │   └── embeddings/cache/        # Embedding cache
│   ├── collections/                 # ChromaDB collections (fallback)
│   ├── docs/                        # Documentation (Diataxis)
│   │   ├── tutorials/
│   │   ├── how-to/
│   │   ├── reference/
│   │   └── explanation/
│   └── speckit/                     # SpecKit integration
│
└── streaming-output/               # MCP Server: structured content streaming
    └── server.py                   # Single-file server (~1700 lines)
```

## Directory Purposes

**`session-memory/`:**
- Purpose: Persistent memory server for Claude sessions
- Contains: Single main server file, plugin system, optional feature modules
- Key files: `server.py` (main), `plugins/base.py` (plugin ABC), `modules/` (optional features)

**`session-memory/plugins/`:**
- Purpose: Skill-specific session tracking plugins
- Contains: Base ABC and implementations
- Key files: `base.py` (SessionPlugin, PluginState, ResumptionContext), `generic.py` (default)

**`session-memory/modules/`:**
- Purpose: Optional features that gracefully degrade if dependencies missing
- Contains: Embeddings, entities, learning, cloud sync, document ingestion
- Key files: Each module is self-contained with its own dependency checks

**`knowledge-mcp/src/knowledge_mcp/`:**
- Purpose: Main package for knowledge base MCP server
- Contains: Server, ingestion pipeline, search, storage, CLI
- Key files: `server.py`, `__main__.py`, `exceptions.py`

**`knowledge-mcp/src/knowledge_mcp/search/strategies/`:**
- Purpose: Workflow-specific search customization (RCCA, trade study, explore, plan)
- Contains: SearchStrategy ABC and four implementations
- Key files: `base.py` (ABC + SearchQuery), `rcca.py`, `trade_study.py`, `explore.py`, `plan.py`

**`knowledge-mcp/src/knowledge_mcp/tools/`:**
- Purpose: MCP tool handler functions (separated from server registration)
- Contains: Handler functions grouped by domain
- Key files: `acquisition.py` (6 handlers), `workflows.py` (4 handlers)

**`knowledge-mcp/src/knowledge_mcp/db/`:**
- Purpose: SQLAlchemy-based relational persistence for source tracking
- Contains: Engine factory, ORM models, repositories, Alembic migrations
- Key files: `engine.py`, `models.py`, `repositories.py`

**`streaming-output/`:**
- Purpose: Structured content streaming with multi-format export
- Contains: Single-file server with templates and renderers
- Key files: `server.py` only

## Key File Locations

**Entry Points:**
- `session-memory/server.py`: Session memory MCP server entry
- `knowledge-mcp/src/knowledge_mcp/__main__.py`: Knowledge MCP entry (server or CLI)
- `streaming-output/server.py`: Streaming output MCP server entry

**Configuration:**
- `knowledge-mcp/pyproject.toml`: Poetry deps and project config
- `requirements.txt`: Shared pip requirements (session-memory + streaming-output)
- `session-memory/.claude-plugin/plugin.json`: Claude plugin manifest
- `knowledge-mcp/.claude-plugin/plugin.json`: Claude plugin manifest
- `knowledge-mcp/src/knowledge_mcp/utils/config.py`: Runtime config loading

**Core Logic:**
- `session-memory/server.py` -> `SessionMemoryServer` class: All session tools
- `knowledge-mcp/src/knowledge_mcp/server.py` -> `KnowledgeMCPServer` class: Tool registration and dispatch
- `streaming-output/server.py`: Stream management and format rendering

**Data Models:**
- `knowledge-mcp/src/knowledge_mcp/models/chunk.py`: `KnowledgeChunk` dataclass
- `knowledge-mcp/src/knowledge_mcp/models/document.py`: `DocumentMetadata` dataclass
- `session-memory/plugins/base.py`: `PluginState`, `ResumptionContext` dataclasses

**Testing:**
- `knowledge-mcp/tests/`: Full test suite (unit + integration + fixtures)
- No test files exist for session-memory or streaming-output

## Naming Conventions

**Files:**
- snake_case for all Python files: `semantic_search.py`, `cloud_sync.py`
- Test files mirror source: `test_chunk/`, `test_embed/`, `test_store/`

**Directories:**
- snake_case: `knowledge_mcp`, `cloud_sync`
- Hyphenated for top-level project dirs: `session-memory`, `knowledge-mcp`, `streaming-output`

**Classes:**
- PascalCase: `SessionMemoryServer`, `KnowledgeMCPServer`, `BaseStore`, `SearchStrategy`

**Functions:**
- snake_case: `handle_rcca()`, `create_store()`, `session_init()`

**MCP Tools:**
- snake_case with prefix: `session_*`, `knowledge_*`, `stream_*`, `entity_*`, `learning_*`, `sync_*`

## Where to Add New Code

**New MCP tool for session-memory:**
- Add tool implementation method to `SessionMemoryServer` in `session-memory/server.py`
- Add `Tool()` definition in the `list_tools()` handler (around line 1542)
- Add dispatch case in `call_tool()` handler (around line 1809)

**New MCP tool for knowledge-mcp:**
- Add handler function in `knowledge-mcp/src/knowledge_mcp/tools/acquisition.py` or `workflows.py` (or create new tool module)
- Add `Tool()` definition in `_setup_handlers()` in `knowledge-mcp/src/knowledge_mcp/server.py`
- Add dispatch case in the `call_tool` handler
- Add tests in `knowledge-mcp/tests/unit/`

**New search strategy for knowledge-mcp:**
- Create strategy file in `knowledge-mcp/src/knowledge_mcp/search/strategies/`
- Inherit from `SearchStrategy` ABC in `strategies/base.py`
- Implement `preprocess_query()`, `adjust_ranking()`, `format_output()`
- Create handler in `tools/workflows.py`
- Register tool in `server.py`

**New session-memory plugin:**
- Create plugin file in `session-memory/plugins/`
- Inherit from `SessionPlugin` ABC in `plugins/base.py`
- Implement required methods: `name`, `supported_skills`, `get_state_schema`, `calculate_progress`, `generate_resumption_context`
- Register in `_register_plugins()` in `session-memory/server.py` (around line 408)

**New optional feature module for session-memory:**
- Create module file in `session-memory/modules/`
- Wrap imports in try/except for graceful degradation
- Initialize in `_init_feature_modules()` in `session-memory/server.py` (around line 357)
- Add corresponding tool definitions and dispatch cases

**New vector store backend for knowledge-mcp:**
- Create store file in `knowledge-mcp/src/knowledge_mcp/store/`
- Inherit from `BaseStore` ABC in `store/base.py`
- Implement `add_chunks()`, `search()`, `get_stats()`, `health_check()`
- Update `create_store()` factory in `store/__init__.py`

**New document ingestor for knowledge-mcp:**
- Create ingestor file in `knowledge-mcp/src/knowledge_mcp/ingest/`
- Inherit from `BaseIngestor` ABC in `ingest/base.py`
- Implement `ingest()` and `supported_extensions()`
- Register in pipeline

**New MCP tool for streaming-output:**
- Add tool implementation function in `streaming-output/server.py`
- Add `Tool()` definition in the tools list (around line 1423)
- Add dispatch case in the tool handler

## Special Directories

**`session-memory/storage/`:**
- Purpose: Runtime data (events, index, checkpoints)
- Generated: Yes (created at startup)
- Committed: No (gitignored)

**`session-memory/handoffs/`:**
- Purpose: Session handoff summary files
- Generated: Yes (created by session_handoff tool)
- Committed: No

**`knowledge-mcp/data/`:**
- Purpose: Source documents and processed data, embedding cache
- Generated: Partially (cache is generated, sources are placed manually)
- Committed: No

**`knowledge-mcp/collections/`:**
- Purpose: ChromaDB local collections (fallback store)
- Generated: Yes
- Committed: No

**`knowledge-mcp/.venv/`:**
- Purpose: Python virtual environment (Python 3.12)
- Generated: Yes
- Committed: No

**`session-memory/.venv/`:**
- Purpose: Python virtual environment (Python 3.14)
- Generated: Yes
- Committed: No

**`.planning/`:**
- Purpose: GSD workflow planning and analysis files
- Generated: By GSD commands
- Committed: Yes

---

*Structure analysis: 2026-03-08*
