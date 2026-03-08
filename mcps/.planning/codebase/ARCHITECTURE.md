# Architecture

**Analysis Date:** 2026-03-08

## Pattern Overview

**Overall:** Monorepo of independent MCP (Model Context Protocol) servers

**Key Characteristics:**
- Three independent MCP servers sharing a single git repository (rooted at `~/projects/claude-plugins`)
- Each server is a standalone Python process communicating via MCP stdio transport
- No shared code between servers -- each has its own dependencies and virtual environment
- Plugin/module architecture for extensibility within individual servers
- Graceful degradation pattern: optional features fail silently if dependencies are missing

## Servers

### 1. session-memory

**Purpose:** Persistent session memory across Claude conversations with categorized event recording, checkpoints, handoffs, and optional features (embeddings, knowledge graph, cloud sync, document ingestion).

**Architecture:** Single-file server (`session-memory/server.py`) with plugin system and optional feature modules.

**Entry Point:** `session-memory/server.py` -- launched via `python3 server.py`

**MCP Tools (20):**
- `session_init`, `session_record`, `session_query`, `session_checkpoint`
- `session_list_checkpoints`, `session_resume`, `session_handoff`, `session_status`
- `session_learn`, `learning_create`, `learning_apply`
- `session_semantic_search`
- `entity_create`, `entity_link`, `entity_query`
- `sync_status`, `sync_push`, `sync_pull`
- `session_ingest`

### 2. knowledge-mcp

**Purpose:** Semantic search over systems engineering standards (IEEE, INCOSE, NASA). RAG capabilities for grounding specifications in engineering knowledge.

**Architecture:** Well-structured Python package (`src/knowledge_mcp/`) with layered architecture following standard patterns (ingest -> chunk -> embed -> store -> search).

**Entry Point:** `python -m knowledge_mcp` via `src/knowledge_mcp/__main__.py`

**MCP Tools (14):**
- `knowledge_search`, `knowledge_stats`
- `knowledge_ingest`, `knowledge_sources`, `knowledge_assess`
- `knowledge_preflight`, `knowledge_acquire`, `knowledge_request`
- `knowledge_rcca`, `knowledge_trade`, `knowledge_explore`, `knowledge_plan`
- `list_collections`

### 3. streaming-output

**Purpose:** Streaming structured content to persistent SQLite storage with automatic session break recovery. Multi-format export (markdown, HTML, text, CSV, YAML).

**Architecture:** Single-file server (`streaming-output/server.py`) with document templates and format renderers.

**Entry Point:** `streaming-output/server.py` -- launched via `python3 server.py`

**MCP Tools (8):**
- `stream_start`, `stream_write`, `stream_status`, `stream_read`
- `stream_export`, `stream_finalize`, `stream_delete`, `stream_templates`

## Layers (knowledge-mcp)

knowledge-mcp is the only server with a formal layered architecture:

**Ingest Layer:**
- Purpose: Parse source documents (PDF, DOCX, web) into structured elements
- Location: `knowledge-mcp/src/knowledge_mcp/ingest/`
- Contains: `BaseIngestor` ABC, format-specific implementations (`pdf_ingestor.py`, `docx_ingestor.py`, `web_ingestor.py`), `pipeline.py`
- Depends on: `models/document.py` for `DocumentMetadata`
- Used by: CLI commands, MCP tool handlers

**Chunk Layer:**
- Purpose: Split parsed documents into semantically coherent chunks
- Location: `knowledge-mcp/src/knowledge_mcp/chunk/`
- Contains: `base.py`, `hierarchical.py` chunker
- Depends on: Ingest layer output (`ParsedDocument`)
- Used by: Ingestion pipeline

**Embed Layer:**
- Purpose: Generate vector embeddings for chunks
- Location: `knowledge-mcp/src/knowledge_mcp/embed/`
- Contains: `BaseEmbedder` ABC, `OpenAIEmbedder`, `LocalEmbedder`, `EmbeddingCache`
- Depends on: OpenAI API
- Used by: `SemanticSearcher`, ingestion pipeline

**Store Layer:**
- Purpose: Persist and retrieve vector embeddings
- Location: `knowledge-mcp/src/knowledge_mcp/store/`
- Contains: `BaseStore` ABC, `QdrantStore` (primary), `ChromaDBStore` (fallback)
- Depends on: Qdrant Cloud or ChromaDB
- Used by: `SemanticSearcher`, ingestion pipeline

**Search Layer:**
- Purpose: Semantic search with workflow-specific strategies
- Location: `knowledge-mcp/src/knowledge_mcp/search/`
- Contains: `SemanticSearcher`, `HybridSearch`, `BM25`, `Reranker`, `CoverageAssessor`
- Sub-layer: `strategies/` with `SearchStrategy` ABC and implementations (`ExploreStrategy`, `PlanStrategy`, `RCCAStrategy`, `TradeStudyStrategy`)
- Depends on: Embed layer, Store layer
- Used by: MCP tool handlers

**Tools Layer:**
- Purpose: MCP tool handler implementations
- Location: `knowledge-mcp/src/knowledge_mcp/tools/`
- Contains: `acquisition.py` (source management tools), `workflows.py` (search workflow tools)
- Depends on: Search layer, DB repositories
- Used by: `server.py` handler dispatch

**DB Layer:**
- Purpose: Relational data persistence (sources, acquisition requests)
- Location: `knowledge-mcp/src/knowledge_mcp/db/`
- Contains: SQLAlchemy models (`models.py`), repositories (`repositories.py`), Alembic migrations
- Depends on: SQLAlchemy async engine
- Used by: Acquisition tool handlers

**Models Layer:**
- Purpose: Core data models shared across layers
- Location: `knowledge-mcp/src/knowledge_mcp/models/`
- Contains: `KnowledgeChunk` (`chunk.py`), `DocumentMetadata` (`document.py`)
- Used by: All layers

## Data Flow

**knowledge-mcp Search Flow:**

1. User sends query via MCP `knowledge_search` tool
2. `server.py` dispatches to `_handle_search()` which calls `_ensure_dependencies()` (lazy init)
3. `SemanticSearcher.search()` embeds query via `OpenAIEmbedder`
4. Embedding is cached in `EmbeddingCache` (disk-based)
5. `BaseStore.search()` finds similar vectors in Qdrant Cloud
6. Results are ranked, filtered by score threshold, and returned as JSON

**knowledge-mcp Workflow Search Flow:**

1. User sends query via workflow tool (e.g., `knowledge_rcca`)
2. `server.py` dispatches to handler in `tools/workflows.py`
3. Handler creates `WorkflowSearcher` with appropriate `SearchStrategy`
4. Strategy preprocesses query (expand terms, add filters, define facets)
5. `SemanticSearcher` executes expanded search
6. Strategy adjusts ranking and formats output for workflow context

**knowledge-mcp Ingestion Flow:**

1. Document path/URL provided via `knowledge_ingest` tool or CLI
2. Format-specific `BaseIngestor` parses to `ParsedDocument`
3. `HierarchicalChunker` splits into `KnowledgeChunk` objects
4. `OpenAIEmbedder` generates embeddings for each chunk
5. `BaseStore.add_chunks()` persists to Qdrant Cloud

**session-memory Event Flow:**

1. `session_init` creates session, selects plugin based on skill name
2. `session_record` appends event to JSONL file and indexes in SQLite
3. Plugin `on_event()` hook updates `PluginState` (progress, phase tracking)
4. Auto-checkpoint timer creates periodic snapshots
5. `session_handoff` generates resumption context via plugin

**streaming-output Write Flow:**

1. `stream_start` creates stream record with schema type in SQLite
2. `stream_write` appends content blocks with deduplication (content hashing)
3. `stream_read` reconstructs document from blocks
4. `stream_export` renders to requested format (markdown, HTML, text, CSV, YAML)
5. `stream_finalize` marks stream complete; `stream_delete` removes it

## Key Abstractions

**SessionPlugin (session-memory):**
- Purpose: Extensible skill-specific session tracking
- Base class: `session-memory/plugins/base.py` -> `SessionPlugin` ABC
- Implementations: `GenericPlugin`, `SpecKitPlugin`, `SpecRefinerPlugin`
- Pattern: Strategy pattern -- plugins provide custom state schemas, progress calculation, and resumption context generation
- State model: `PluginState` dataclass with phase, progress, custom_data

**BaseStore (knowledge-mcp):**
- Purpose: Swappable vector store backend
- Base class: `knowledge-mcp/src/knowledge_mcp/store/base.py` -> `BaseStore` ABC
- Implementations: `QdrantStore` (primary), `ChromaDBStore` (fallback)
- Pattern: Strategy pattern with factory function `create_store(config)`

**BaseIngestor (knowledge-mcp):**
- Purpose: Format-specific document parsing
- Base class: `knowledge-mcp/src/knowledge_mcp/ingest/base.py` -> `BaseIngestor` ABC
- Implementations: `PDFIngestor`, `DocxIngestor`, `WebIngestor`
- Output: `ParsedDocument` containing `ParsedElement` list

**SearchStrategy (knowledge-mcp):**
- Purpose: Workflow-specific search customization
- Base class: `knowledge-mcp/src/knowledge_mcp/search/strategies/base.py` -> `SearchStrategy` ABC
- Implementations: `ExploreStrategy`, `PlanStrategy`, `RCCAStrategy`, `TradeStudyStrategy`
- Pattern: Strategy pattern with 3-phase pipeline (preprocess -> rank -> format)

**BaseEmbedder (knowledge-mcp):**
- Purpose: Swappable embedding generation
- Base class: `knowledge-mcp/src/knowledge_mcp/embed/base.py` -> `BaseEmbedder` ABC
- Implementations: `OpenAIEmbedder`, `LocalEmbedder`

## Entry Points

**session-memory MCP Server:**
- Location: `session-memory/server.py`
- Triggers: Claude Desktop launches via `python3 server.py`
- Responsibilities: Creates `SessionMemoryServer`, registers MCP handlers, runs stdio transport

**knowledge-mcp MCP Server:**
- Location: `knowledge-mcp/src/knowledge_mcp/__main__.py`
- Triggers: Claude Desktop launches via `python3 -m knowledge_mcp`
- Responsibilities: Routes to MCP server or CLI based on args
- Server class: `knowledge-mcp/src/knowledge_mcp/server.py` -> `KnowledgeMCPServer`

**knowledge-mcp CLI:**
- Location: `knowledge-mcp/src/knowledge_mcp/cli/main.py`
- Triggers: `python -m knowledge_mcp cli <command>`
- Commands: `ingest`, `validate`, `verify`, `token_summary`

**streaming-output MCP Server:**
- Location: `streaming-output/server.py`
- Triggers: Claude Desktop launches via `python3 server.py`
- Responsibilities: Creates MCP Server, registers stream tools, runs stdio transport

## Error Handling

**Strategy:** Mixed approaches across servers

**session-memory:**
- Graceful degradation for optional features (try/except ImportError)
- Tool handlers return error dicts: `{"error": str(e)}`
- Thread safety via `threading.RLock`

**knowledge-mcp:**
- Custom exception hierarchy rooted at `KnowledgeMCPError` in `knowledge-mcp/src/knowledge_mcp/exceptions.py`
- Specific types: `ConfigurationError`, `ConnectionError`, `TimeoutError`, `AuthenticationError`, `NotFoundError`, `ValidationError`, `RateLimitError`, `InternalError`
- Tool handlers catch exceptions and return structured error JSON
- Lazy dependency initialization with `_ensure_dependencies()`

**streaming-output:**
- Content deduplication via SHA-256 hashing
- SQLite for persistence with automatic recovery
- Tool handlers return error dicts on failure

## Cross-Cutting Concerns

**Logging:**
- session-memory: Minimal (print to stderr)
- knowledge-mcp: Python `logging` module with structured logger per module
- streaming-output: Minimal

**Validation:**
- session-memory: Plugin state validation via `validate_state()`
- knowledge-mcp: Pydantic models for config validation, JSON Schema for MCP tool inputs
- streaming-output: Inline validation in tool handlers

**Authentication:**
- No auth between client and MCP servers (trusted local process)
- External service auth via environment variables (OpenAI, Qdrant, Cloudflare)

**State Management:**
- session-memory: SQLite + JSONL files for events, JSON files for checkpoints
- knowledge-mcp: Qdrant Cloud for vectors, SQLAlchemy/SQLite for relational data, disk cache for embeddings
- streaming-output: SQLite for all stream data

---

*Architecture analysis: 2026-03-08*
