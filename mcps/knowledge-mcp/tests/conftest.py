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