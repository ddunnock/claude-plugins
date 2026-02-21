# tests/unit/test_config.py
"""Unit tests for configuration module."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from knowledge_mcp.utils.config import KnowledgeConfig, load_config
from conftest import TEST_OPENAI_API_KEY, TEST_QDRANT_API_KEY, TEST_SK_API_KEY, TEST_COHERE_API_KEY


class TestKnowledgeConfig:
    """Tests for KnowledgeConfig validation."""

    def test_validate_missing_openai_key(self) -> None:
        """Test validation fails when OpenAI key is missing with OpenAI provider."""
        config = KnowledgeConfig(openai_api_key="", embedding_provider="openai")

        errors = config.validate()

        assert "OPENAI_API_KEY is required when embedding_provider=openai" in errors

    def test_validate_local_provider_no_openai_key_required(self) -> None:
        """Test validation passes when using local embeddings without OpenAI key."""
        config = KnowledgeConfig(
            openai_api_key="",
            embedding_provider="local",
            vector_store="chromadb",  # Don't require Qdrant credentials
        )

        errors = config.validate()

        # Should not complain about OpenAI key
        assert not any("OPENAI_API_KEY" in e for e in errors)

    def test_validate_qdrant_missing_url(self) -> None:
        """Test validation fails when Qdrant URL is missing."""
        config = KnowledgeConfig(
            openai_api_key=TEST_SK_API_KEY,
            vector_store="qdrant",
            qdrant_url="",
        )

        errors = config.validate()

        assert "QDRANT_URL is required when using Qdrant" in errors

    def test_validate_success(self) -> None:
        """Test validation passes with complete config."""
        config = KnowledgeConfig(
            openai_api_key=TEST_SK_API_KEY,
            vector_store="qdrant",
            qdrant_url="https://test.qdrant.io",
            qdrant_api_key=TEST_QDRANT_API_KEY,
            offline_mode=True,  # Skip DATABASE_URL requirement for unit test
        )

        errors = config.validate()

        assert errors == []

    def test_validate_requires_database_url_when_online(self) -> None:
        """Test validation requires DATABASE_URL when offline_mode=False."""
        config = KnowledgeConfig(
            openai_api_key=TEST_SK_API_KEY,
            vector_store="qdrant",
            qdrant_url="https://test.qdrant.io",
            qdrant_api_key=TEST_QDRANT_API_KEY,
            offline_mode=False,
        )

        errors = config.validate()

        assert "DATABASE_URL is required when offline_mode=False" in errors

    def test_chunk_overlap_validation(self) -> None:
        """Test that overlap cannot exceed minimum chunk size."""
        with pytest.raises(ValueError, match="chunk_overlap must be less than"):
            KnowledgeConfig(
                openai_api_key=TEST_SK_API_KEY,
                chunk_size_min=200,
                chunk_overlap=250,  # Greater than min
            )


class TestVersionedCollectionName:
    """Tests for versioned collection name generation."""

    def test_versioned_collection_name_default(self) -> None:
        """Test versioned collection name with default model."""
        config = KnowledgeConfig(openai_api_key=TEST_OPENAI_API_KEY)
        # Default model is text-embedding-3-small
        assert config.versioned_collection_name == "se_knowledge_base_v1_te3small"

    def test_versioned_collection_name_custom_base(self) -> None:
        """Test versioned collection name with custom base name."""
        config = KnowledgeConfig(
            openai_api_key=TEST_OPENAI_API_KEY,
            qdrant_collection="my_collection",
        )
        assert config.versioned_collection_name == "my_collection_v1_te3small"

    def test_versioned_collection_name_different_model(self) -> None:
        """Test versioned collection name with different embedding model."""
        config = KnowledgeConfig(
            openai_api_key=TEST_OPENAI_API_KEY,
            embedding_model="text-embedding-3-large",
        )
        assert config.versioned_collection_name == "se_knowledge_base_v1_te3large"

    def test_versioned_chromadb_collection_name(self) -> None:
        """Test ChromaDB versioned collection name."""
        config = KnowledgeConfig(openai_api_key=TEST_OPENAI_API_KEY)
        assert config.versioned_chromadb_collection_name == "se_knowledge_base_v1_te3small"


class TestCacheConfiguration:
    """Tests for cache configuration fields."""

    def test_cache_defaults(self) -> None:
        """Test that cache configuration has correct defaults."""
        config = KnowledgeConfig(openai_api_key=TEST_OPENAI_API_KEY)

        assert config.cache_dir == Path("./data/embeddings/cache")
        assert config.cache_enabled is True
        assert config.cache_size_limit == 10 * 1024 * 1024 * 1024  # 10GB

    def test_cache_size_limit_minimum_validation(self) -> None:
        """Test that cache_size_limit enforces minimum of 100MB."""
        with pytest.raises(ValueError):
            KnowledgeConfig(
                openai_api_key=TEST_OPENAI_API_KEY,
                cache_size_limit=50 * 1024 * 1024,  # 50MB - below minimum
            )

    def test_cache_configuration_from_values(self) -> None:
        """Test creating config with custom cache values."""
        config = KnowledgeConfig(
            openai_api_key=TEST_OPENAI_API_KEY,
            cache_dir=Path("/custom/cache/path"),
            cache_enabled=False,
            cache_size_limit=500 * 1024 * 1024,  # 500MB
        )

        assert config.cache_dir == Path("/custom/cache/path")
        assert config.cache_enabled is False
        assert config.cache_size_limit == 500 * 1024 * 1024


class TestTokenTrackingConfiguration:
    """Tests for token tracking configuration fields."""

    def test_token_tracking_defaults(self) -> None:
        """Test that token tracking configuration has correct defaults."""
        config = KnowledgeConfig(openai_api_key=TEST_OPENAI_API_KEY)

        assert config.token_log_file == Path("./data/token_usage.json")
        assert config.token_tracking_enabled is True
        assert config.daily_token_warning_threshold == 1_000_000

    def test_token_tracking_threshold_validation(self) -> None:
        """Test that daily_token_warning_threshold must be non-negative."""
        with pytest.raises(ValueError):
            KnowledgeConfig(
                openai_api_key=TEST_OPENAI_API_KEY,
                daily_token_warning_threshold=-1000,
            )

    def test_token_tracking_configuration_from_values(self) -> None:
        """Test creating config with custom token tracking values."""
        config = KnowledgeConfig(
            openai_api_key=TEST_OPENAI_API_KEY,
            token_log_file=Path("/custom/tokens.json"),
            token_tracking_enabled=False,
            daily_token_warning_threshold=500_000,
        )

        assert config.token_log_file == Path("/custom/tokens.json")
        assert config.token_tracking_enabled is False
        assert config.daily_token_warning_threshold == 500_000


class TestLoadConfigEnvironment:
    """Tests for loading configuration from environment variables."""

    def test_load_cache_config_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading cache configuration from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("CACHE_DIR", "/env/cache")
        monkeypatch.setenv("CACHE_ENABLED", "false")
        monkeypatch.setenv("CACHE_SIZE_LIMIT", str(5 * 1024**3))  # 5GB

        config = load_config()

        assert config.cache_dir == Path("/env/cache")
        assert config.cache_enabled is False
        assert config.cache_size_limit == 5 * 1024**3

    def test_load_token_tracking_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading token tracking configuration from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("TOKEN_LOG_FILE", "/env/tokens.json")
        monkeypatch.setenv("TOKEN_TRACKING_ENABLED", "false")
        monkeypatch.setenv("DAILY_TOKEN_WARNING_THRESHOLD", "2000000")

        config = load_config()

        assert config.token_log_file == Path("/env/tokens.json")
        assert config.token_tracking_enabled is False
        assert config.daily_token_warning_threshold == 2_000_000