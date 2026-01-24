# Knowledge MCP

Semantic search over engineering standards (IEEE, INCOSE, ISO, NASA) for systems engineering RAG workflows.

**Standards Compliance**: This project adheres to `_references/claude-standards/` (see [CLAUDE.md](./CLAUDE.md) for details).

## Features

- **Semantic Search**: Find relevant standards content using natural language queries
- **Source Citations**: Results include standard name, clause number, and page references
- **Hybrid Storage**: Qdrant Cloud (primary) with ChromaDB fallback for offline use
- **Evaluation Framework**: Golden test set with RAG metrics for quality monitoring
- **Cost Tracking**: Token usage monitoring with daily aggregation

## Installation

### Claude Desktop (Recommended)

1. Download the latest `.mcpb` bundle from releases
2. Double-click to install, or drag to Claude Desktop
3. Configure environment variables when prompted:
   - `OPENAI_API_KEY` (required): Your OpenAI API key

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/dunnock/claude-plugins.git
cd claude-plugins/mcps/knowledge-mcp

# Install dependencies
poetry install --with dev,chromadb

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
poetry run python -m knowledge_mcp
```

## Configuration

### Required

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for embedding generation |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | - | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | - | Qdrant Cloud API key |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `CHROMADB_PATH` | `./data/chromadb` | Local ChromaDB storage path |
| `COLLECTION_NAME` | `se_knowledge_base` | Vector collection name |

## Usage

### MCP Tools

Once installed, the following tools are available in Claude:

**knowledge_search**
```
Search for: "system verification requirements"
```
Returns relevant chunks with source citations (e.g., "IEEE 15288 Clause 6.4.7").

**knowledge_stats**
```
Show knowledge base statistics
```
Returns collection counts and storage information.

### CLI Commands

```bash
# Token usage summary
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
# Type checking
poetry run pyright

# Linting
poetry run ruff check src tests
poetry run ruff format src tests
```

### Building Package

```bash
# Create MCPB bundle
./scripts/package_mcpb.sh
```

## Architecture

```
knowledge-mcp/
├── src/knowledge_mcp/
│   ├── server.py          # MCP server entry point
│   ├── search/            # Semantic search implementation
│   ├── embed/             # Embedding generation + cache
│   ├── store/             # Vector storage (Qdrant, ChromaDB)
│   ├── evaluation/        # Golden tests + RAG metrics
│   └── monitoring/        # Token tracking + logging
├── data/
│   ├── golden_queries.yml # Evaluation test set
│   └── embedding_cache/   # Cached embeddings
└── tests/
```

## License

MIT License - see [LICENSE](./LICENSE) file for details.
