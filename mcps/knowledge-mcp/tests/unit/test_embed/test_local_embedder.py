# tests/unit/test_embed/test_local_embedder.py
"""Unit tests for LocalEmbedder.

Tests verify that LocalEmbedder correctly implements the BaseEmbedder interface
using sentence-transformers, with proper async wrapping and normalization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

if TYPE_CHECKING:
    pass


class TestLocalEmbedder:
    """Tests for LocalEmbedder class."""

    @pytest.fixture
    def mock_model(self) -> MagicMock:
        """Create mock SentenceTransformer."""
        model = MagicMock()
        model.get_sentence_embedding_dimension.return_value = 384
        model.encode.return_value = np.array([0.1] * 384)
        return model

    @patch("sentence_transformers.SentenceTransformer")
    def test_dimensions(self, mock_st_cls: MagicMock, mock_model: MagicMock) -> None:
        """Test dimensions property returns model dimensions."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder()
        assert embedder.dimensions == 384

    @patch("sentence_transformers.SentenceTransformer")
    def test_model_name_default(self, mock_st_cls: MagicMock, mock_model: MagicMock) -> None:
        """Test model_name returns default model."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder()
        assert embedder.model_name == "all-MiniLM-L6-v2"

    @patch("sentence_transformers.SentenceTransformer")
    def test_model_name_custom(self, mock_st_cls: MagicMock, mock_model: MagicMock) -> None:
        """Test model_name returns configured model."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder(model_name="all-mpnet-base-v2")
        assert embedder.model_name == "all-mpnet-base-v2"

    @patch("sentence_transformers.SentenceTransformer")
    @pytest.mark.asyncio
    async def test_embed(self, mock_st_cls: MagicMock, mock_model: MagicMock) -> None:
        """Test embed returns list of floats."""
        mock_st_cls.return_value = mock_model
        mock_model.encode.return_value = np.array([0.5] * 384)
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder()
        result = await embedder.embed("test text")

        assert isinstance(result, list)
        assert len(result) == 384
        assert all(isinstance(v, float) for v in result)
        mock_model.encode.assert_called_once()

    @patch("sentence_transformers.SentenceTransformer")
    @pytest.mark.asyncio
    async def test_embed_batch(self, mock_st_cls: MagicMock, mock_model: MagicMock) -> None:
        """Test embed_batch returns list of embedding lists."""
        mock_st_cls.return_value = mock_model
        mock_model.encode.return_value = np.array([[0.5] * 384, [0.6] * 384])
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder()
        texts = ["text 1", "text 2"]
        results = await embedder.embed_batch(texts)

        assert len(results) == 2
        assert all(len(r) == 384 for r in results)

    @patch("sentence_transformers.SentenceTransformer")
    @pytest.mark.asyncio
    async def test_embed_batch_empty(self, mock_st_cls: MagicMock, mock_model: MagicMock) -> None:
        """Test embed_batch with empty list returns empty list."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder()
        results = await embedder.embed_batch([])

        assert results == []
        mock_model.encode.assert_not_called()

    @patch("sentence_transformers.SentenceTransformer")
    def test_normalize_embeddings_default_true(
        self, mock_st_cls: MagicMock, mock_model: MagicMock
    ) -> None:
        """Test normalize_embeddings defaults to True (critical for cosine similarity)."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder()
        # Access private attribute to verify
        assert embedder._normalize is True

    @patch("sentence_transformers.SentenceTransformer")
    def test_normalize_embeddings_can_be_disabled(
        self, mock_st_cls: MagicMock, mock_model: MagicMock
    ) -> None:
        """Test normalize_embeddings can be explicitly set to False."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder(normalize_embeddings=False)
        assert embedder._normalize is False

    @patch("sentence_transformers.SentenceTransformer")
    @pytest.mark.asyncio
    async def test_encode_called_with_normalize(
        self, mock_st_cls: MagicMock, mock_model: MagicMock
    ) -> None:
        """Test that encode is called with normalize_embeddings=True."""
        mock_st_cls.return_value = mock_model
        mock_model.encode.return_value = np.array([0.5] * 384)
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        embedder = LocalEmbedder()
        await embedder.embed("test")

        # Verify encode was called with normalize_embeddings=True
        call_kwargs = mock_model.encode.call_args
        assert call_kwargs[1]["normalize_embeddings"] is True
        assert call_kwargs[1]["show_progress_bar"] is False

    @patch("sentence_transformers.SentenceTransformer")
    def test_device_passed_to_model(
        self, mock_st_cls: MagicMock, mock_model: MagicMock
    ) -> None:
        """Test device parameter is passed to SentenceTransformer."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        LocalEmbedder(device="cpu")

        mock_st_cls.assert_called_once_with("all-MiniLM-L6-v2", device="cpu")

    @patch("sentence_transformers.SentenceTransformer")
    def test_custom_model_passed_to_sentence_transformer(
        self, mock_st_cls: MagicMock, mock_model: MagicMock
    ) -> None:
        """Test custom model name is passed to SentenceTransformer."""
        mock_st_cls.return_value = mock_model
        from knowledge_mcp.embed.local_embedder import LocalEmbedder

        LocalEmbedder(model_name="custom-model")

        mock_st_cls.assert_called_once_with("custom-model", device=None)


class TestCreateEmbedder:
    """Tests for create_embedder factory function."""

    @patch("sentence_transformers.SentenceTransformer")
    def test_create_local_embedder(self, mock_st_cls: MagicMock) -> None:
        """Test create_embedder returns LocalEmbedder for local provider."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st_cls.return_value = mock_model

        from knowledge_mcp.embed import create_embedder
        from knowledge_mcp.embed.local_embedder import LocalEmbedder
        from knowledge_mcp.utils.config import KnowledgeConfig

        config = KnowledgeConfig(embedding_provider="local")
        embedder = create_embedder(config)

        assert isinstance(embedder, LocalEmbedder)

    def test_create_openai_embedder(self) -> None:
        """Test create_embedder returns OpenAIEmbedder for openai provider."""
        from knowledge_mcp.embed import OpenAIEmbedder, create_embedder
        from knowledge_mcp.utils.config import KnowledgeConfig

        config = KnowledgeConfig(
            embedding_provider="openai",
            openai_api_key="test-key",
        )
        embedder = create_embedder(config)

        assert isinstance(embedder, OpenAIEmbedder)

    def test_create_embedder_unknown_provider(self) -> None:
        """Test create_embedder raises for unknown provider."""
        from knowledge_mcp.embed import create_embedder
        from knowledge_mcp.utils.config import KnowledgeConfig

        # Create config with invalid provider (need to bypass validation)
        config = KnowledgeConfig.model_construct(embedding_provider="invalid")

        with pytest.raises(ValueError, match="Unknown embedding provider"):
            create_embedder(config)

    @patch("sentence_transformers.SentenceTransformer")
    def test_create_local_with_custom_model(self, mock_st_cls: MagicMock) -> None:
        """Test create_embedder uses local_embedding_model from config."""
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st_cls.return_value = mock_model

        from knowledge_mcp.embed import create_embedder
        from knowledge_mcp.utils.config import KnowledgeConfig

        config = KnowledgeConfig(
            embedding_provider="local",
            local_embedding_model="all-mpnet-base-v2",
        )
        embedder = create_embedder(config)

        assert embedder.model_name == "all-mpnet-base-v2"
