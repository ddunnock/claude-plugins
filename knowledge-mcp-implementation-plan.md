# Knowledge MCP Implementation Plan

## Detailed Architecture and Implementation Guide

**Date**: January 15, 2026
**Version**: 3.0
**Purpose**: Create a reusable MCP for chunking, embedding, and semantic search of technical reference documents
**Primary Backend**: Qdrant Cloud (Free Tier)
**Standards Compliance**: `_references/claude-standards/` (constitution.md, python.md, testing.md, documentation.md, security.md, git-cicd.md)

---

## 1. Executive Summary

This plan outlines the creation of a **Knowledge MCP** - a standalone, reusable project that provides semantic search capabilities over technical reference documents (IEEE standards, INCOSE guides, NASA handbooks, etc.). The MCP will:

1. **Ingest** PDF, DOCX, and Markdown documents
2. **Chunk** them using hierarchical semantic strategies optimized for technical specifications
3. **Embed** chunks using OpenAI's text-embedding-3-small (cost-effective) or text-embedding-3-large (high quality)
4. **Store** vectors in **Qdrant Cloud** (primary) with ChromaDB as local development fallback
5. **Serve** semantic search queries via MCP tools

### 1.1 Standards Compliance Summary

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| `python.md` §1 | Python ≥3.11,<3.14 | Enforced in pyproject.toml |
| `python.md` §2.3 | Poetry for package management | Poetry as build backend |
| `python.md` §3 | Google-style docstrings | Required on all public APIs |
| `python.md` §4.2 | Pyright strict mode | Configured in pyproject.toml |
| `python.md` §5.1 | Ruff linting with full ruleset | Configured in pyproject.toml |
| `python.md` §6 | `__init__.py` + `__main__.py` | Required in all packages |
| `testing.md` §1 | 80% line coverage minimum | pytest-cov configured |
| `documentation.md` §1 | Diátaxis framework | docs/ structure follows framework |
| `security.md` §2 | Secrets via environment variables | .env with validation |
| `git-cicd.md` §1 | Conventional Commits | Required for all commits |

### 1.2 Why Qdrant Cloud?

| Feature | Benefit |
|---------|---------|
| **1GB Free Forever** | No cost for your ~50-100MB knowledge base |
| **Hybrid Search** | Dense + sparse vectors for better technical doc retrieval |
| **Full-Text Search** | Built-in keyword search capability |
| **Rich Filtering** | Complex metadata queries on all fields |
| **No Dimension Limit** | Supports any embedding model (including 3072-dim) |
| **Official MCP Server** | Reference implementation available |

---

## 2. Reference Materials Inventory

Based on exploration of `_references/SE-RAG-Sources/`:

| Document | Size | Type | Sections |
|----------|------|------|----------|
| `INCOSE_SEHB5.pdf` | 10.1 MB | Systems Engineering Handbook | Multi-chapter |
| `12207-2017.pdf` | 1.7 MB | IEEE Software Life Cycle | Standards |
| `1362-1998.pdf` | 277 KB | IEEE Concept of Operations | Standards |
| `Guide_to_SEBoK_v2.13.pdf` | 21.6 MB | SEBoK | Encyclopedia-style |
| `nasa_systems_engineering_handbook_0.pdf` | 3.7 MB | NASA SE Handbook | Structured |
| `ieee-std-15288.2-2014/` | ~10 MB total | Technical Reviews | Pre-split sections |

**Total**: ~47 MB of source material, ~800-1200 pages of technical content.
**Estimated Chunks**: ~4,000 chunks
**Estimated Vector Storage**: ~50-100 MB (well within Qdrant's 1GB free tier)

---

## 3. Architecture Design

### 3.1 High-Level Architecture (Qdrant Cloud)

```
┌──────────────────────────────────────────────────────────────────┐
│                        Knowledge MCP                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────┐ │
│  │   Ingest    │──▶│   Chunk     │──▶│        Embed            │ │
│  │   Pipeline  │   │   Engine    │   │    (OpenAI API)         │ │
│  └─────────────┘   └─────────────┘   └───────────┬─────────────┘ │
│         │                                         │               │
│         ▼                                         ▼               │
│  ┌─────────────┐                                                  │
│  │  Metadata   │                                                  │
│  │  Extractor  │                                                  │
│  └─────────────┘                                                  │
│                                                                   │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │       Qdrant Cloud            │
                │   (Free Tier - 1GB)           │
                │                               │
                │  ┌─────────────────────────┐  │
                │  │  se_knowledge_base      │  │
                │  │  - Dense vectors (1536) │  │
                │  │  - Sparse vectors (BM25)│  │
                │  │  - Rich metadata        │  │
                │  │  - Payload indexing     │  │
                │  └─────────────────────────┘  │
                │                               │
                │  Features:                    │
                │  • Hybrid search              │
                │  • Full-text search           │
                │  • Filtered queries           │
                │  • Scroll/pagination          │
                └───────────────────────────────┘
```

### 3.2 Component Details

#### Ingest Pipeline
- **PDF Parser**: `pymupdf4llm` (best for preserving structure)
- **DOCX Parser**: `python-docx` + `mammoth` for text extraction
- **Markdown Parser**: Native Python with frontmatter support

#### Chunk Engine
- **Hierarchical Semantic Chunking** for technical documents
- Respects document structure (sections, subsections, clauses)
- Preserves cross-references and definitions

#### Vector Store
- **Primary**: Qdrant Cloud (Free Tier)
  - URL: `https://<cluster-id>.<region>.gcp.cloud.qdrant.io`
  - 1GB storage free forever
  - No credit card required
- **Fallback**: ChromaDB (local development/offline)

---

## 4. Project Structure (Standards-Compliant)

### 4.1 Repository Layout

Per `python.md` §2.3 and §6, the project **MUST** follow this structure:

```
knowledge-mcp/
├── CLAUDE.md                    # Project-specific development standards
├── pyproject.toml               # Poetry configuration
├── poetry.lock                  # Locked dependencies (committed)
├── README.md                    # Project overview
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history (Keep a Changelog format)
├── .env.example                 # Environment template
├── .gitignore
│
├── src/
│   └── knowledge_mcp/           # Main package
│       ├── __init__.py          # Package initialization (REQUIRED per python.md §6.1)
│       ├── __main__.py          # Entry point (REQUIRED per python.md §6.2)
│       ├── server.py            # MCP server entry point
│       │
│       ├── ingest/              # Document ingestion
│       │   ├── __init__.py      # REQUIRED for every directory
│       │   ├── base.py          # Abstract ingestor
│       │   ├── pdf_ingestor.py  # PDF handling
│       │   ├── docx_ingestor.py # DOCX handling
│       │   └── markdown_ingestor.py # MD handling
│       │
│       ├── chunk/               # Chunking strategies
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract chunker
│       │   ├── hierarchical.py  # Structure-aware chunking
│       │   ├── semantic.py      # Semantic boundary detection
│       │   └── standards.py     # IEEE/INCOSE-specific rules
│       │
│       ├── embed/               # Embedding generation
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract embedder
│       │   ├── openai_embedder.py # OpenAI embeddings
│       │   └── local_embedder.py  # Optional: local models
│       │
│       ├── store/               # Vector storage
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract store interface
│       │   ├── qdrant_store.py  # Qdrant Cloud (PRIMARY)
│       │   └── chromadb_store.py # ChromaDB (fallback)
│       │
│       ├── search/              # Search and retrieval
│       │   ├── __init__.py
│       │   ├── semantic_search.py # Embedding-based search
│       │   ├── hybrid_search.py   # Dense + sparse (Qdrant)
│       │   └── reranker.py        # Optional reranking
│       │
│       ├── models/              # Data models
│       │   ├── __init__.py
│       │   ├── chunk.py         # KnowledgeChunk dataclass
│       │   └── document.py      # Document metadata
│       │
│       ├── cli/                 # Command-line interfaces
│       │   ├── __init__.py
│       │   └── ingest.py        # Document ingestion CLI
│       │
│       └── utils/               # Utilities
│           ├── __init__.py
│           ├── config.py        # Configuration handling
│           ├── hashing.py       # Content hashing
│           └── tokenizer.py     # Token counting
│
├── tests/                       # Test suite (per testing.md §3.1)
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_chunk/
│   │   │   ├── __init__.py
│   │   │   ├── test_hierarchical.py
│   │   │   └── test_semantic.py
│   │   ├── test_embed/
│   │   │   ├── __init__.py
│   │   │   └── test_openai_embedder.py
│   │   └── test_store/
│   │       ├── __init__.py
│   │       ├── test_qdrant_store.py
│   │       └── test_chromadb_store.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_ingest_pipeline.py
│   │   └── test_mcp_server.py
│   └── fixtures/
│       ├── sample_pdf.pdf
│       ├── sample_docx.docx
│       └── expected_chunks.json
│
├── scripts/
│   ├── ingest_documents.py      # CLI for bulk ingestion
│   ├── verify_embeddings.py     # Validation script
│   ├── export_collection.py     # Export for backup
│   └── setup_qdrant.py          # Initialize Qdrant collection
│
├── data/
│   ├── sources/                 # Place source documents here
│   └── processed/               # Intermediate processing output
│
├── docs/                        # Sphinx documentation (per documentation.md)
│   ├── conf.py                  # Sphinx configuration
│   ├── index.md                 # Documentation home
│   ├── tutorials/               # Learning-oriented (Diátaxis)
│   │   ├── index.md
│   │   └── getting-started.md
│   ├── how-to/                  # Task-oriented (Diátaxis)
│   │   ├── index.md
│   │   ├── installation.md
│   │   ├── ingest-documents.md
│   │   └── configure-qdrant.md
│   ├── reference/               # Information-oriented (Diátaxis)
│   │   ├── index.md
│   │   ├── api/
│   │   │   ├── index.md
│   │   │   └── mcp-tools.md
│   │   ├── configuration.md
│   │   └── changelog.md
│   ├── explanation/             # Understanding-oriented (Diátaxis)
│   │   ├── index.md
│   │   ├── architecture.md
│   │   └── chunking-strategy.md
│   ├── _static/
│   │   └── css/
│   │       └── custom.css
│   └── _templates/
│
├── .github/                     # GitHub workflows (per git-cicd.md)
│   ├── workflows/
│   │   ├── ci.yml               # CI pipeline
│   │   ├── security.yml         # Security scanning
│   │   └── docs.yml             # Documentation build
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml           # Automated updates
│
└── collections/                 # Local fallback storage
    ├── chromadb/                # Local ChromaDB files
    └── exports/                 # Portable exports
```

---

## 5. Code Implementation (Standards-Compliant)

### 5.1 Package Initialization (`__init__.py`)

Per `python.md` §6.1:

```python
# src/knowledge_mcp/__init__.py
"""
Knowledge MCP - Semantic search over technical reference documents.

This package provides MCP (Model Context Protocol) tools for searching
IEEE standards, INCOSE guides, NASA handbooks, and other systems
engineering reference materials.

Example:
    >>> from knowledge_mcp import KnowledgeMCPServer
    >>> server = KnowledgeMCPServer()
    >>> results = await server.search("system requirements review")

Attributes:
    __version__: Package version string.
"""

from knowledge_mcp.server import KnowledgeMCPServer

__version__ = "0.1.0"
__all__ = ["KnowledgeMCPServer", "__version__"]
```

### 5.2 Entry Point (`__main__.py`)

Per `python.md` §6.2:

```python
# src/knowledge_mcp/__main__.py
"""
Entry point for running package as a module.

Usage:
    python -m knowledge_mcp [options]

Examples:
    python -m knowledge_mcp --help
    python -m knowledge_mcp serve
    python -m knowledge_mcp ingest --source ./data/sources
"""

from __future__ import annotations

import sys


def cli() -> int:
    """
    Command-line interface entry point.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    import asyncio

    from knowledge_mcp.server import main as server_main

    try:
        asyncio.run(server_main())
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli())
```

### 5.3 Configuration Module (with Pydantic Validation)

Per `security.md` §3 and `python.md` §3:

```python
# src/knowledge_mcp/utils/config.py
"""
Configuration management for Knowledge MCP.

Loads configuration from environment variables with validation.
Supports .env files for local development.

Example:
    >>> config = load_config()
    >>> errors = config.validate()
    >>> if errors:
    ...     raise ValueError(f"Config errors: {errors}")
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class KnowledgeConfig(BaseModel):
    """
    Configuration for Knowledge MCP.

    All configuration is loaded from environment variables.
    Use .env file for local development.

    Attributes:
        openai_api_key: OpenAI API key for embeddings.
        embedding_model: OpenAI embedding model name.
        embedding_dimensions: Vector dimensions for embeddings.
        vector_store: Vector store backend (qdrant or chromadb).
        qdrant_url: Qdrant Cloud cluster URL.
        qdrant_api_key: Qdrant Cloud API key.
        qdrant_collection: Collection name in Qdrant.
        qdrant_hybrid_search: Enable hybrid search.
        chromadb_path: Path to local ChromaDB storage.
        chromadb_collection: Collection name in ChromaDB.
        chunk_size_min: Minimum chunk size in tokens.
        chunk_size_max: Maximum chunk size in tokens.
        chunk_overlap: Overlap between chunks in tokens.
    """

    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model",
    )
    embedding_dimensions: int = Field(
        default=1536,
        ge=256,
        le=3072,
        description="Vector dimensions",
    )

    # Vector Store Selection
    vector_store: Literal["qdrant", "chromadb"] = Field(
        default="qdrant",
        description="Vector store backend",
    )

    # Qdrant Cloud (Primary)
    qdrant_url: str = Field(default="", description="Qdrant Cloud URL")
    qdrant_api_key: str = Field(default="", description="Qdrant API key")
    qdrant_collection: str = Field(
        default="se_knowledge_base",
        description="Qdrant collection name",
    )
    qdrant_hybrid_search: bool = Field(
        default=True,
        description="Enable hybrid search",
    )

    # ChromaDB (Fallback)
    chromadb_path: Path = Field(
        default=Path("./collections/chromadb"),
        description="ChromaDB storage path",
    )
    chromadb_collection: str = Field(
        default="se_knowledge_base",
        description="ChromaDB collection name",
    )

    # Chunking Configuration
    chunk_size_min: int = Field(
        default=200,
        ge=50,
        le=500,
        description="Minimum chunk size in tokens",
    )
    chunk_size_max: int = Field(
        default=800,
        ge=200,
        le=2000,
        description="Maximum chunk size in tokens",
    )
    chunk_overlap: int = Field(
        default=100,
        ge=0,
        le=500,
        description="Chunk overlap in tokens",
    )

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v: int, info) -> int:
        """Ensure overlap is less than minimum chunk size."""
        if "chunk_size_min" in info.data and v >= info.data["chunk_size_min"]:
            msg = "chunk_overlap must be less than chunk_size_min"
            raise ValueError(msg)
        return v

    def validate(self) -> list[str]:
        """
        Validate configuration completeness.

        Returns:
            List of validation error messages. Empty if valid.
        """
        errors: list[str] = []

        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")

        if self.vector_store == "qdrant":
            if not self.qdrant_url:
                errors.append("QDRANT_URL is required when using Qdrant")
            if not self.qdrant_api_key:
                errors.append("QDRANT_API_KEY is required for Qdrant Cloud")

        return errors


def load_config() -> KnowledgeConfig:
    """
    Load configuration from environment variables.

    Searches for .env files in current directory and parents.

    Returns:
        Validated KnowledgeConfig instance.

    Example:
        >>> config = load_config()
        >>> print(config.embedding_model)
        'text-embedding-3-small'
    """
    import os

    from dotenv import load_dotenv

    # Load from .env files (project root takes precedence)
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # Also check parent directories
    for parent in Path.cwd().parents:
        parent_env = parent / ".env"
        if parent_env.exists():
            load_dotenv(parent_env, override=False)
            break

    # Build config from environment
    return KnowledgeConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "1536")),
        vector_store=os.getenv("VECTOR_STORE", "qdrant"),  # type: ignore[arg-type]
        qdrant_url=os.getenv("QDRANT_URL", ""),
        qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "se_knowledge_base"),
        qdrant_hybrid_search=os.getenv("QDRANT_HYBRID_SEARCH", "true").lower() == "true",
        chromadb_path=Path(os.getenv("CHROMADB_PATH", "./collections/chromadb")),
        chromadb_collection=os.getenv("CHROMADB_COLLECTION", "se_knowledge_base"),
        chunk_size_min=int(os.getenv("CHUNK_SIZE_MIN", "200")),
        chunk_size_max=int(os.getenv("CHUNK_SIZE_MAX", "800")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
    )
```

### 5.4 Data Models (with Type Hints and Docstrings)

Per `python.md` §3 and §4:

```python
# src/knowledge_mcp/models/chunk.py
"""
Data models for knowledge chunks.

This module defines the KnowledgeChunk dataclass used throughout
the ingestion, embedding, and search pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional


@dataclass
class KnowledgeChunk:
    """
    A chunk of knowledge from a technical document.

    Represents a semantically coherent unit of content extracted
    from a source document, enriched with metadata for retrieval.

    Attributes:
        id: Unique identifier (UUID).
        document_id: Source document identifier.
        document_title: Human-readable document title.
        document_type: Document classification (standard, handbook, guide, spec).
        content: The actual text content.
        content_hash: SHA-256 hash for deduplication.
        token_count: Number of tokens for context management.
        section_hierarchy: Path through document structure.
        section_title: Title of containing section.
        parent_chunk_id: Link to parent section chunk.
        chunk_type: Content classification (definition, requirement, guidance, etc.).
        normative: Whether content is mandatory (normative).
        page_numbers: Source page references.
        clause_number: Clause identifier if applicable.
        references: Extracted cross-references.
        embedding: Vector embedding (populated after embed phase).
        embedding_model: Model used for embedding.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    Example:
        >>> chunk = KnowledgeChunk(
        ...     id="550e8400-e29b-41d4-a716-446655440000",
        ...     document_id="ieee-15288.2",
        ...     document_title="IEEE 15288.2-2014",
        ...     document_type="standard",
        ...     content="The SRR shall verify...",
        ...     content_hash="abc123...",
        ...     token_count=150,
        ... )
    """

    # Identity
    id: str
    document_id: str
    document_title: str
    document_type: str

    # Content
    content: str
    content_hash: str
    token_count: int

    # Hierarchy
    section_hierarchy: list[str] = field(default_factory=list)
    section_title: str = ""
    parent_chunk_id: Optional[str] = None

    # Classification
    chunk_type: str = "content"
    normative: bool = False

    # Location
    page_numbers: list[int] = field(default_factory=list)
    clause_number: Optional[str] = None

    # Cross-references
    references: list[str] = field(default_factory=list)

    # Embeddings
    embedding: Optional[list[float]] = None
    embedding_model: str = "text-embedding-3-small"

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict:
        """
        Convert chunk to dictionary for serialization.

        Returns:
            Dictionary representation of chunk.
        """
        return {
            "id": self.id,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "document_type": self.document_type,
            "content": self.content,
            "content_hash": self.content_hash,
            "token_count": self.token_count,
            "section_hierarchy": self.section_hierarchy,
            "section_title": self.section_title,
            "parent_chunk_id": self.parent_chunk_id,
            "chunk_type": self.chunk_type,
            "normative": self.normative,
            "page_numbers": self.page_numbers,
            "clause_number": self.clause_number,
            "references": self.references,
            "embedding_model": self.embedding_model,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
```

### 5.5 Qdrant Store (Standards-Compliant)

```python
# src/knowledge_mcp/store/qdrant_store.py
"""
Qdrant Cloud vector store implementation.

Provides vector storage and retrieval using Qdrant Cloud's free tier.
Supports dense vector search, hybrid search, and full-text search.

Features:
    - Dense vector search (OpenAI embeddings)
    - Sparse vector search (BM25 for hybrid)
    - Rich metadata filtering
    - Payload indexing for fast queries
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
    NamedVector,
    OptimizersConfigDiff,
    PayloadSchemaType,
    PointStruct,
    SparseIndexParams,
    SparseVectorParams,
    TextIndexParams,
    TokenizerType,
    VectorParams,
)

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk
    from knowledge_mcp.utils.config import KnowledgeConfig


class QdrantStore:
    """
    Vector store using Qdrant Cloud.

    Provides storage and retrieval of knowledge chunks using
    Qdrant's vector database with support for hybrid search.

    Attributes:
        config: Knowledge MCP configuration.
        client: Qdrant client instance.
        collection: Collection name.
        hybrid_enabled: Whether hybrid search is enabled.

    Example:
        >>> config = load_config()
        >>> store = QdrantStore(config)
        >>> store.add_chunks(chunks)
        >>> results = store.search(query_embedding, n_results=5)
    """

    def __init__(self, config: KnowledgeConfig) -> None:
        """
        Initialize Qdrant store.

        Args:
            config: Knowledge MCP configuration with Qdrant settings.

        Raises:
            ConnectionError: When unable to connect to Qdrant Cloud.
        """
        self.config = config

        self.client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
            timeout=60,
        )

        self.collection = config.qdrant_collection
        self.hybrid_enabled = config.qdrant_hybrid_search

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection for c in collections)

        if not exists:
            vectors_config = {
                "dense": VectorParams(
                    size=self.config.embedding_dimensions,
                    distance=Distance.COSINE,
                )
            }

            sparse_vectors_config = None
            if self.hybrid_enabled:
                sparse_vectors_config = {
                    "sparse": SparseVectorParams(
                        index=SparseIndexParams(on_disk=False),
                    )
                }

            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=vectors_config,
                sparse_vectors_config=sparse_vectors_config,
                optimizers_config=OptimizersConfigDiff(indexing_threshold=0),
            )

            self._create_payload_indexes()

    def _create_payload_indexes(self) -> None:
        """Create indexes on frequently filtered fields."""
        index_fields = [
            ("document_id", PayloadSchemaType.KEYWORD),
            ("document_type", PayloadSchemaType.KEYWORD),
            ("chunk_type", PayloadSchemaType.KEYWORD),
            ("normative", PayloadSchemaType.BOOL),
            ("clause_number", PayloadSchemaType.KEYWORD),
        ]

        for field_name, field_type in index_fields:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection,
                    field_name=field_name,
                    field_schema=field_type,
                )
            except UnexpectedResponse:
                pass  # Index might already exist

        # Full-text index on content
        try:
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="content",
                field_schema=TextIndexParams(
                    type="text",
                    tokenizer=TokenizerType.WORD,
                    min_token_len=2,
                    max_token_len=20,
                    lowercase=True,
                ),
            )
        except UnexpectedResponse:
            pass

    def add_chunks(self, chunks: list[KnowledgeChunk]) -> int:
        """
        Add chunks to the collection.

        Args:
            chunks: List of KnowledgeChunk objects with embeddings.

        Returns:
            Number of chunks successfully added.

        Raises:
            ValueError: When chunks list is empty or missing embeddings.
        """
        if not chunks:
            return 0

        points = []
        for chunk in chunks:
            if chunk.embedding is None:
                msg = f"Chunk {chunk.id} missing embedding"
                raise ValueError(msg)

            vectors: dict = {"dense": chunk.embedding}

            point = PointStruct(
                id=chunk.id,
                vector=vectors if self.hybrid_enabled else chunk.embedding,
                payload={
                    "content": chunk.content,
                    "document_id": chunk.document_id,
                    "document_title": chunk.document_title,
                    "document_type": chunk.document_type,
                    "section_title": chunk.section_title,
                    "section_hierarchy": chunk.section_hierarchy,
                    "chunk_type": chunk.chunk_type,
                    "normative": chunk.normative,
                    "clause_number": chunk.clause_number or "",
                    "page_numbers": chunk.page_numbers,
                    "references": chunk.references,
                    "token_count": chunk.token_count,
                    "content_hash": chunk.content_hash,
                    "parent_chunk_id": chunk.parent_chunk_id or "",
                    "created_at": chunk.created_at,
                },
            )
            points.append(point)

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection,
                points=batch,
            )

        return len(points)

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        filter_dict: Optional[dict[str, object]] = None,
        score_threshold: float = 0.0,
    ) -> list[dict]:
        """
        Search for similar chunks.

        Args:
            query_embedding: Dense vector embedding of the query.
            n_results: Number of results to return.
            filter_dict: Metadata filters (e.g., {"chunk_type": "requirement"}).
            score_threshold: Minimum similarity score (0-1).

        Returns:
            List of matching chunks with scores and metadata.

        Example:
            >>> results = store.search(
            ...     query_embedding=embedder.embed("SRR"),
            ...     n_results=5,
            ...     filter_dict={"chunk_type": "requirement"},
            ... )
        """
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                if isinstance(value, bool):
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                elif isinstance(value, list):
                    conditions.append(FieldCondition(key=key, match=MatchAny(any=value)))
                else:
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            query_filter = Filter(must=conditions)

        if self.hybrid_enabled:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=NamedVector(name="dense", vector=query_embedding),
                limit=n_results,
                query_filter=query_filter,
                score_threshold=score_threshold,
                with_payload=True,
            )
        else:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=n_results,
                query_filter=query_filter,
                score_threshold=score_threshold,
                with_payload=True,
            )

        return [
            {
                "id": str(r.id),
                "content": r.payload.get("content", ""),
                "metadata": {
                    "document_id": r.payload.get("document_id", ""),
                    "document_title": r.payload.get("document_title", ""),
                    "document_type": r.payload.get("document_type", ""),
                    "section_title": r.payload.get("section_title", ""),
                    "section_hierarchy": r.payload.get("section_hierarchy", []),
                    "chunk_type": r.payload.get("chunk_type", ""),
                    "normative": r.payload.get("normative", False),
                    "clause_number": r.payload.get("clause_number", ""),
                    "page_numbers": r.payload.get("page_numbers", []),
                    "references": r.payload.get("references", []),
                },
                "score": r.score,
            }
            for r in results
        ]

    def get_stats(self) -> dict:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection metadata and counts.
        """
        info = self.client.get_collection(self.collection)
        return {
            "collection_name": self.collection,
            "total_chunks": info.points_count,
            "vectors_count": info.vectors_count,
            "indexed_vectors": info.indexed_vectors_count,
            "status": info.status,
            "config": {
                "vector_size": self.config.embedding_dimensions,
                "hybrid_enabled": self.hybrid_enabled,
            },
        }
```

---

## 6. CI/CD Configuration

Per `git-cicd.md`:

### 6.1 GitHub Actions CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run Ruff
        run: poetry run ruff check src tests

      - name: Run Pyright
        run: poetry run pyright

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run tests with coverage
        run: poetry run pytest --cov=src --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run pip-audit
        run: poetry run pip-audit --strict
```

### 6.2 Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: "0 0 * * *"  # Daily

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run pip-audit
        run: poetry run pip-audit --strict
```

### 6.3 Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 7. Testing Strategy

Per `testing.md`:

### 7.1 Test Configuration (conftest.py)

```python
# tests/conftest.py
"""
Shared test fixtures for Knowledge MCP.

Provides mock objects, sample data, and test configuration
used across unit and integration tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk
    from knowledge_mcp.utils.config import KnowledgeConfig


@pytest.fixture
def mock_config() -> KnowledgeConfig:
    """Create a test configuration."""
    from knowledge_mcp.utils.config import KnowledgeConfig

    return KnowledgeConfig(
        openai_api_key="test-api-key",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=1536,
        vector_store="chromadb",
        chromadb_path=Path("/tmp/test-chromadb"),
        chromadb_collection="test_collection",
    )


@pytest.fixture
def sample_chunk() -> KnowledgeChunk:
    """Create a sample knowledge chunk for testing."""
    from knowledge_mcp.models.chunk import KnowledgeChunk

    return KnowledgeChunk(
        id="test-chunk-001",
        document_id="ieee-15288.2",
        document_title="IEEE 15288.2-2014",
        document_type="standard",
        content="The System Requirements Review (SRR) shall verify...",
        content_hash="abc123def456",
        token_count=150,
        section_hierarchy=["5", "5.3", "5.3.1"],
        section_title="System Requirements Review",
        chunk_type="requirement",
        normative=True,
        page_numbers=[42, 43],
        clause_number="5.3.1",
        embedding=[0.1] * 1536,
    )


@pytest.fixture
def mock_qdrant_client() -> MagicMock:
    """Create a mock Qdrant client."""
    client = MagicMock()
    client.get_collections.return_value.collections = []
    return client


@pytest.fixture
def mock_openai_client() -> AsyncMock:
    """Create a mock OpenAI client."""
    client = AsyncMock()
    client.embeddings.create.return_value.data = [
        MagicMock(embedding=[0.1] * 1536)
    ]
    return client
```

### 7.2 Example Unit Test

```python
# tests/unit/test_config.py
"""Unit tests for configuration module."""

from __future__ import annotations

from pathlib import Path

import pytest

from knowledge_mcp.utils.config import KnowledgeConfig


class TestKnowledgeConfig:
    """Tests for KnowledgeConfig validation."""

    def test_validate_missing_openai_key(self) -> None:
        """Test validation fails when OpenAI key is missing."""
        config = KnowledgeConfig(openai_api_key="")

        errors = config.validate()

        assert "OPENAI_API_KEY is required" in errors

    def test_validate_qdrant_missing_url(self) -> None:
        """Test validation fails when Qdrant URL is missing."""
        config = KnowledgeConfig(
            openai_api_key="sk-test",
            vector_store="qdrant",
            qdrant_url="",
        )

        errors = config.validate()

        assert "QDRANT_URL is required when using Qdrant" in errors

    def test_validate_success(self) -> None:
        """Test validation passes with complete config."""
        config = KnowledgeConfig(
            openai_api_key="sk-test",
            vector_store="qdrant",
            qdrant_url="https://test.qdrant.io",
            qdrant_api_key="test-key",
        )

        errors = config.validate()

        assert errors == []

    def test_chunk_overlap_validation(self) -> None:
        """Test that overlap cannot exceed minimum chunk size."""
        with pytest.raises(ValueError, match="chunk_overlap must be less than"):
            KnowledgeConfig(
                openai_api_key="sk-test",
                chunk_size_min=200,
                chunk_overlap=250,  # Greater than min
            )
```

---

## 8. Implementation Timeline (Updated)

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Setup | Project structure per standards, Poetry config, CLAUDE.md, CI/CD |
| 2 | Core Models | KnowledgeChunk, KnowledgeConfig, exceptions, base interfaces |
| 3 | Vector Store | QdrantStore, ChromaDBStore with full test coverage |
| 4 | Ingestion | PDF/DOCX/MD parsers, structure extraction, chunking engine |
| 5 | MCP Server | Tool implementations, integration tests, hybrid search |
| 6 | Documentation | Diátaxis docs, README, CHANGELOG, specification-refiner integration |

---

## 9. Cost Estimation

### 9.1 Initial Setup Costs

| Component | Cost |
|-----------|------|
| Qdrant Cloud (Free Tier) | **$0** |
| OpenAI Embeddings (~4K chunks) | ~$0.04 |
| **Total** | **~$0.04** |

### 9.2 Ongoing Costs

| Usage Level | Queries/Month | OpenAI Cost | Qdrant Cost | Total |
|-------------|---------------|-------------|-------------|-------|
| Light | 1,000 | $0.002 | $0 | $0.002 |
| Medium | 10,000 | $0.02 | $0 | $0.02 |
| Heavy | 100,000 | $0.20 | $0 | $0.20 |

---

## 10. Sources

- [Claude Standards Constitution](../_references/claude-standards/constitution.md)
- [Claude Standards Python](../_references/claude-standards/python.md)
- [Claude Standards Testing](../_references/claude-standards/testing.md)
- [Claude Standards Documentation](../_references/claude-standards/documentation.md)
- [Qdrant Cloud Pricing](https://qdrant.tech/pricing/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Best Chunking Strategies for RAG 2025](https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025)
- [OpenAI Cookbook: Parse PDF docs for RAG](https://cookbook.openai.com/examples/parse_pdf_docs_for_rag)
