# Knowledge MCP

A Model Context Protocol (MCP) server for semantic search over technical reference documents. Designed for systems engineering standards (IEEE, INCOSE, NASA) but works with any technical documentation.

**Standards Compliance**: This project adheres to `_references/claude-standards/` (see [CLAUDE.md](./CLAUDE.md) for details).

## Features

- **Multi-format ingestion**: PDF, DOCX, and Markdown documents
- **Structure-aware chunking**: Preserves document hierarchy (sections, clauses, annexes)
- **Semantic search**: Find relevant content using natural language queries
- **Metadata filtering**: Filter by document type, content type, normative status
- **Cross-reference tracking**: Maintains links between related sections
- **Dual vector store support**: Qdrant Cloud (primary) or ChromaDB (local)

## Quick Start

### 1. Prerequisites

- Python ≥3.11,<3.14
- Poetry (package manager)
- OpenAI API key (for embeddings)
- Qdrant Cloud account (free tier, no credit card required)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/knowledge-mcp.git
cd knowledge-mcp

# Install dependencies with Poetry
poetry install

# For development dependencies
poetry install --with dev

# For optional ChromaDB fallback
poetry install --with chromadb
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
# Required: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY
nano .env
```

### 4. Qdrant Cloud Setup

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io/)
2. Create a free cluster (1GB, no credit card)
3. Copy the cluster URL and API key to `.env`

### 5. Ingest Documents

```bash
# Ingest all documents from data/sources/
poetry run python -m knowledge_mcp.cli.ingest --source ./data/sources

# Or ingest a specific file
poetry run python -m knowledge_mcp.cli.ingest --file ./data/sources/INCOSE_SEHB5.pdf
```

### 6. Run the MCP Server

```bash
poetry run python -m knowledge_mcp
```

### 7. Configure Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "knowledge-mcp": {
      "command": "poetry",
      "args": ["run", "python", "-m", "knowledge_mcp"],
      "cwd": "/path/to/knowledge-mcp",
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "QDRANT_URL": "your-qdrant-url",
        "QDRANT_API_KEY": "your-qdrant-key"
      }
    }
  }
}
```

## MCP Tools

### `knowledge_search`

Search the knowledge base with natural language queries.

```json
{
  "query": "requirements traceability matrix",
  "n_results": 5,
  "document_type": "standard",
  "chunk_type": "requirement",
  "normative_only": true,
  "use_hybrid": true
}
```

### `knowledge_lookup`

Look up a specific term or definition.

```json
{
  "term": "verification"
}
```

### `knowledge_requirements`

Find requirements on a specific topic from standards.

```json
{
  "topic": "system requirements review",
  "standard": "IEEE 15288"
}
```

### `knowledge_keyword_search`

Full-text keyword search for exact term matching.

```json
{
  "query": "IEEE 15288.2 SRR",
  "n_results": 10
}
```

### `knowledge_stats`

Get statistics about the knowledge base.

## Supported Documents

This MCP is optimized for technical standards and handbooks:

| Document Type | Examples |
|--------------|----------|
| IEEE Standards | 15288, 12207, 1362 |
| INCOSE | Systems Engineering Handbook |
| NASA | SE Handbook, NPR 7123 |
| SEBoK | Systems Engineering Body of Knowledge |
| Custom | Your organization's standards |

## Development

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run only unit tests
poetry run pytest tests/unit/
```

### Code Quality

```bash
# Linting
poetry run ruff check src tests

# Format code
poetry run ruff format src tests

# Type checking (strict mode)
poetry run pyright

# Security scan
poetry run pip-audit --strict
```

### Pre-commit Checklist

- [ ] All tests pass
- [ ] Coverage ≥80%
- [ ] Pyright passes (zero errors)
- [ ] Ruff passes (zero errors)
- [ ] Documentation updated

## Cost Estimation

Using OpenAI text-embedding-3-small ($0.02/1M tokens):

| Content Size | Est. Cost |
|-------------|-----------|
| 100 pages | ~$0.01 |
| 1000 pages | ~$0.05 |
| 10000 pages | ~$0.50 |

Query costs are negligible (~$0.00002 per query).

Qdrant Cloud free tier: 1GB storage, unlimited queries.

## Project Structure

```
knowledge-mcp/
├── src/knowledge_mcp/       # Main package
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── server.py            # MCP server
│   ├── ingest/              # Document parsers
│   ├── chunk/               # Chunking strategies
│   ├── embed/               # Embedding generation
│   ├── store/               # Vector storage
│   ├── models/              # Data models
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── docs/                    # Sphinx documentation
└── data/sources/            # Place documents here
```

## License

MIT License - see [LICENSE](./LICENSE) file for details.
