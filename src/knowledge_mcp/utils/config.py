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