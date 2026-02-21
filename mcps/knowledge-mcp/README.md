# Knowledge MCP

Semantic search over systems engineering standards (IEEE, INCOSE, ISO, NASA) for RAG-grounded specification workflows.

## Important: Standards Not Included

**This MCP ships empty.** You must acquire and ingest your own standards documents.

This design enables:
- Marketplace distribution without copyright concerns
- Flexibility to use your organization's licensed standards
- Support for domain-specific standards (automotive, aerospace, defense)

### Quick Start: Ingest Standards

```bash
cd mcps/knowledge-mcp

# Ingest a standards PDF with validation
poetry run python -m knowledge_mcp.cli.ingest docs ./standards/your-standard.pdf \
  --collection rcca_standards \
  --document-id your-standard-id \
  --validate

# Validate the collection
poetry run python -m knowledge_mcp.cli.validate collection rcca_standards
```

### Recommended Standards for RCCA

| Standard | Purpose | Acquisition |
|----------|---------|-------------|
| AIAG-VDA FMEA 2019 | Action Priority tables | [Guide](docs/standards-acquisition/aiag-vda-2019.md) |
| MIL-STD-882E | Severity categories (FREE) | [Guide](docs/standards-acquisition/mil-std-882e.md) |
| ISO 9001:2015 | CAPA requirements | [Guide](docs/standards-acquisition/iso-9001-2015.md) |

See [How to Ingest Standards](docs/how-to/ingest-standards.md) for complete instructions.

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
# Ingest a standards document
poetry run python -m knowledge_mcp.cli.ingest docs ./path/to/standard.pdf \
  --collection rcca_standards \
  --document-id standard-id \
  --validate

# Validate a collection for RCCA readiness
poetry run python -m knowledge_mcp.cli.validate collection rcca_standards --verbose

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
│   ├── validation/        # Table validation for critical RCCA tables
│   ├── evaluation/        # Golden tests + RAG metrics
│   └── monitoring/        # Token tracking + logging
├── docs/
│   ├── standards-acquisition/  # Guides for acquiring RCCA standards
│   └── how-to/                 # Step-by-step guides
├── data/
│   └── embedding_cache/   # Cached embeddings (LRU, 10GB limit)
└── tests/
    ├── unit/
    ├── integration/
    └── evaluation/
```

## Version History

### v0.1.3 (Current)
- Update transitive deps: cryptography 46.0.5, pillow 12.1.1, protobuf 6.33.5, python-multipart 0.0.22, urllib3 2.6.3
- Known: nltk 3.9.2 zip-slip vulnerability (CVE-2025-14009) has no upstream fix; transitive dep from crawl4ai

### v0.1.2
- Update crawl4ai from ^0.7.8 to >=0.8.0 (fixes CVE-2026-26216 RCE, CVE-2026-26217 LFI)

### v0.1.1
- Add path validation to scripts (reject traversal, restrict extensions)
- Extract hardcoded test API keys into shared constants from environment variables
- Replace hashlib.md5 with hashlib.sha256 for content hashing

### v0.1.0
- Initial release with semantic search over systems engineering standards
- Qdrant Cloud primary storage with ChromaDB fallback
- Evaluation framework with golden test set and RAG metrics

## License

MIT License
