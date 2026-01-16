# Project Context: Knowledge MCP

> **Generated**: 2026-01-15
> **Source**: Detected from project files

---

## Project Identity

| Field           | Value                                                             |
|-----------------|-------------------------------------------------------------------|
| **Name**        | knowledge-mcp                                                     |
| **Version**     | 0.1.0                                                             |
| **Description** | MCP server for semantic search over technical reference documents |
| **License**     | MIT                                                               |

---

## Technology Stack

### Runtime
- **Language**: Python ≥3.11, <3.14
- **Package Manager**: Poetry
- **Entry Points**: `knowledge-mcp`, `knowledge-ingest`

### Core Dependencies
| Package         | Purpose                             |
|-----------------|-------------------------------------|
| `mcp`           | Model Context Protocol SDK          |
| `openai`        | Embeddings via OpenAI API           |
| `qdrant-client` | Primary vector store (Qdrant Cloud) |
| `pymupdf4llm`   | PDF processing                      |
| `python-docx`   | DOCX processing                     |
| `tiktoken`      | Tokenization                        |
| `pydantic`      | Data validation                     |
| `rich`          | CLI output formatting               |

### Optional Dependencies
| Group      | Package                 | Purpose                     |
|------------|-------------------------|-----------------------------|
| `chromadb` | `chromadb`              | Local fallback vector store |
| `rerank`   | `cohere`                | Result reranking            |
| `local`    | `sentence-transformers` | Local embeddings            |
| `docs`     | `sphinx`, `furo`        | Documentation               |

### Development Tools
| Tool        | Configuration                | Purpose               |
|-------------|------------------------------|-----------------------|
| **Pyright** | `[tool.pyright]` strict mode | Static type checking  |
| **Ruff**    | `[tool.ruff]`                | Linting + formatting  |
| **pytest**  | `[tool.pytest.ini_options]`  | Testing with coverage |

---

## Project Structure

```
knowledge-mcp/
├── src/knowledge_mcp/        # Main package
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py             # [TO BUILD] MCP server
│   ├── models/               # Data models
│   ├── utils/                # Configuration, utilities
│   ├── store/                # Vector store backends
│   ├── embed/                # [TO BUILD] Embedding service
│   ├── ingest/               # [TO BUILD] Document ingestors
│   ├── chunk/                # [TO BUILD] Chunking strategies
│   ├── search/               # [TO BUILD] Search engine
│   └── cli/                  # [TO BUILD] CLI commands
├── tests/                    # Test suite
├── docs/                     # Documentation
│   └── reference/
│       ├── claude-standards/ # Coding standards
│       └── specs/            # Specifications
└── .claude/                  # Claude Code resources
    ├── memory/               # Context memory files
    ├── resources/            # Specs, plans
    ├── commands/             # Custom commands
    ├── templates/            # Output templates
    └── scripts/              # Project scripts
```

---

## Quality Gates

Per `pyproject.toml` configuration:

| Gate          | Requirement              | Blocking  |
|---------------|--------------------------|-----------|
| Coverage      | ≥80% line coverage       | Yes       |
| Type Checking | Pyright strict, 0 errors | Yes       |
| Linting       | Ruff, 0 errors           | Yes       |

---

## Key Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Type check
poetry run pyright

# Lint
poetry run ruff check src tests

# Run MCP server
poetry run knowledge-mcp

# Ingest documents
poetry run knowledge-ingest <source>
```

---

## Specifications

| Document            | Location                                    | Status   |
|---------------------|---------------------------------------------|----------|
| A-Specification     | `.claude/resources/knowledge-mcp-a-spec.md` | Reviewed |
| Implementation Plan | `.claude/resources/plan.md`                 | Draft    |

---

## External Services

| Service      | Environment Variable           | Required          |
|--------------|--------------------------------|-------------------|
| OpenAI API   | `OPENAI_API_KEY`               | Yes               |
| Qdrant Cloud | `QDRANT_URL`, `QDRANT_API_KEY` | If using Qdrant   |
| ChromaDB     | `CHROMADB_PATH`                | If using ChromaDB |