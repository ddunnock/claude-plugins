# Knowledge MCP

Semantic search over systems engineering standards (IEEE, INCOSE, ISO, NASA) for RAG-grounded specification workflows.

## Features

- **Semantic Search**: Find relevant standards content using natural language queries
- **Source Citations**: Results include standard name, clause number, and page references
- **Hybrid Storage**: Qdrant Cloud (primary) with ChromaDB fallback for offline use
- **Evaluation Framework**: Golden test set with RAG metrics for quality monitoring
- **Cost Tracking**: Token usage monitoring with daily aggregation and embedding cache

## Installation

### Claude Desktop / LLM Clients

Add to your MCP configuration (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "knowledge-mcp": {
      "command": "python3",
      "args": ["-m", "knowledge_mcp"],
      "cwd": "/path/to/claude-plugins/mcps/knowledge-mcp",
      "env": {
        "PYTHONPATH": "/path/to/claude-plugins/mcps/knowledge-mcp/src",
        "OPENAI_API_KEY": "sk-...",
        "QDRANT_URL": "https://your-cluster.qdrant.io",
        "QDRANT_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Claude Code Plugin

The plugin is automatically discovered when the repository is cloned:

```bash
# Check plugin is recognized
claude plugins list
```

Environment variables can be set in your shell or `.env` file.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for embeddings |
| `QDRANT_URL` | No | - | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | No | - | Qdrant Cloud API key |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | OpenAI embedding model |
| `CHROMADB_PATH` | No | `./data/chromadb` | Local ChromaDB storage path |
| `COLLECTION_NAME` | No | `se_knowledge_base` | Vector collection name |

If Qdrant credentials are not provided, the server automatically falls back to local ChromaDB storage.

### Development Setup

```bash
cd mcps/knowledge-mcp

# Install dependencies
poetry install --with dev,chromadb

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run the MCP server directly
poetry run python -m knowledge_mcp
```

## MCP Tools

Once configured, the following tools are available in Claude:

### knowledge_search

Search the knowledge base for relevant content.

```
Query: "system verification requirements"
→ Returns relevant chunks with source citations (e.g., "IEEE 15288 Clause 6.4.7")
```

### knowledge_stats

Get statistics about the knowledge base collections and document counts.

## CLI Commands

```bash
# Token usage summary (last 7 days)
poetry run python -m knowledge_mcp.cli.token_summary --days 7

# Run golden tests
poetry run pytest tests/evaluation/ -v
```

## Development

### Running Tests

```bash
# All tests
poetry run pytest tests/ -v

# With coverage
poetry run pytest tests/ --cov=src --cov-report=term-missing

# Evaluation tests only
poetry run pytest tests/evaluation/ -v
```

### Quality Checks

```bash
# Type checking (zero errors required)
poetry run pyright

# Linting
poetry run ruff check src tests
poetry run ruff format src tests
```

## Architecture

```
mcps/knowledge-mcp/
├── .claude-plugin/
│   └── plugin.json        # Claude Code plugin manifest
├── src/knowledge_mcp/
│   ├── server.py          # MCP server entry point
│   ├── search/            # Semantic search implementation
│   ├── embed/             # Embedding generation + cache
│   ├── store/             # Vector storage (Qdrant, ChromaDB)
│   ├── ingest/            # Document ingestion (PDF, DOCX)
│   ├── chunk/             # Hierarchical chunking
│   ├── evaluation/        # Golden tests + RAG metrics
│   └── monitoring/        # Token tracking + logging
├── data/
│   └── embedding_cache/   # Cached embeddings (LRU, 10GB limit)
└── tests/
    ├── unit/
    ├── integration/
    └── evaluation/
```

## License

MIT License
