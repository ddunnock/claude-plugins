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