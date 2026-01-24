# tests/unit/test_embed/test_openai_embedder.py
"""
Unit tests for OpenAIEmbedder.

Tests cover:
- Single text embedding
- Batch embedding (within limit)
- Batch embedding (exceeds limit, splits)
- Retry on transient error
- Failure after max retries
- Dimension validation

Uses AAA pattern (Arrange-Act-Assert) per testing.md §5.1.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import APIConnectionError, APITimeoutError, RateLimitError

from knowledge_mcp.embed.openai_embedder import OpenAIEmbedder
from knowledge_mcp.exceptions import (
    AuthenticationError,
    ConnectionError,
    RateLimitError as KMCPRateLimitError,
    TimeoutError,
    ValidationError,
)

if TYPE_CHECKING:
    pass


class TestOpenAIEmbedderInit:
    """Tests for OpenAIEmbedder initialization."""

    def test_init_with_valid_api_key(self) -> None:
        """Test successful initialization with valid API key."""
        # Arrange & Act
        embedder = OpenAIEmbedder(api_key="sk-test-key")

        # Assert
        assert embedder.dimensions == 1536
        assert embedder.model_name == "text-embedding-3-small"

    def test_init_with_custom_model(self) -> None:
        """Test initialization with custom model and dimensions."""
        # Arrange & Act
        embedder = OpenAIEmbedder(
            api_key="sk-test-key",
            model="text-embedding-3-large",
            dimensions=3072,
        )

        # Assert
        assert embedder.dimensions == 3072
        assert embedder.model_name == "text-embedding-3-large"

    def test_init_with_empty_api_key_raises_validation_error(self) -> None:
        """Test that empty API key raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            OpenAIEmbedder(api_key="")

        assert "API key is required" in str(exc_info.value)


class TestOpenAIEmbedderEmbed:
    """Tests for single text embedding."""

    @pytest.fixture
    def mock_embedder(self) -> OpenAIEmbedder:
        """Create an embedder with mocked OpenAI client."""
        with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
            return OpenAIEmbedder(api_key="sk-test-key")

    @pytest.mark.asyncio
    async def test_embed_single_text_success(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test successful embedding of a single text."""
        # Arrange
        expected_embedding = [0.1] * 1536
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=expected_embedding)]
        mock_embedder._client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await mock_embedder.embed("What is systems engineering?")

        # Assert
        assert result == expected_embedding
        assert len(result) == 1536
        mock_embedder._client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_empty_text_raises_validation_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that empty text raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await mock_embedder.embed("")

        assert "cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_embed_whitespace_only_raises_validation_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that whitespace-only text raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError):
            await mock_embedder.embed("   ")

    @pytest.mark.asyncio
    async def test_embed_dimension_mismatch_raises_validation_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that dimension mismatch raises ValidationError."""
        # Arrange
        wrong_size_embedding = [0.1] * 512  # Wrong size
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=wrong_size_embedding)]
        mock_embedder._client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await mock_embedder.embed("test text")

        assert "dimension mismatch" in str(exc_info.value)


class TestOpenAIEmbedderEmbedBatch:
    """Tests for batch embedding."""

    @pytest.fixture
    def mock_embedder(self) -> OpenAIEmbedder:
        """Create an embedder with mocked OpenAI client."""
        with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
            return OpenAIEmbedder(api_key="sk-test-key")

    @pytest.mark.asyncio
    async def test_embed_batch_within_limit(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test batch embedding with texts within the limit."""
        # Arrange
        texts = ["text 1", "text 2", "text 3"]
        embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in embeddings]
        mock_embedder._client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await mock_embedder.embed_batch(texts)

        # Assert
        assert len(result) == 3
        assert result == embeddings
        # Single API call since within batch limit
        mock_embedder._client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_batch_exceeds_limit_splits(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that batch exceeding limit is split into multiple calls."""
        # Arrange
        texts = [f"text {i}" for i in range(150)]  # 150 texts, exceeds 100 limit
        batch1_embeddings = [[0.1] * 1536 for _ in range(100)]
        batch2_embeddings = [[0.2] * 1536 for _ in range(50)]

        call_count = 0

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            if call_count == 1:
                response.data = [MagicMock(embedding=e) for e in batch1_embeddings]
            else:
                response.data = [MagicMock(embedding=e) for e in batch2_embeddings]
            return response

        mock_embedder._client.embeddings.create = mock_create

        # Act
        result = await mock_embedder.embed_batch(texts)

        # Assert
        assert len(result) == 150
        assert call_count == 2  # Should split into 2 API calls

    @pytest.mark.asyncio
    async def test_embed_batch_empty_list(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test that empty text list returns empty result."""
        # Arrange, Act
        result = await mock_embedder.embed_batch([])

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_embed_batch_with_empty_text_raises_validation_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that batch with empty text raises ValidationError."""
        # Arrange
        texts = ["valid text", "", "another valid"]

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await mock_embedder.embed_batch(texts)

        assert "index 1" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_embed_batch_custom_batch_size(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test batch embedding with custom batch size."""
        # Arrange
        texts = ["text 1", "text 2", "text 3"]
        embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]

        call_count = 0

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            # Return one embedding per call (batch_size=1)
            response = MagicMock()
            response.data = [MagicMock(embedding=embeddings[call_count - 1])]
            return response

        mock_embedder._client.embeddings.create = mock_create

        # Act
        result = await mock_embedder.embed_batch(texts, batch_size=1)

        # Assert
        assert len(result) == 3
        assert call_count == 3  # 3 separate API calls

    @pytest.mark.asyncio
    async def test_embed_batch_dimension_mismatch_raises_validation_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that batch dimension mismatch raises ValidationError."""
        # Arrange
        texts = ["text 1", "text 2"]
        wrong_size_embeddings = [[0.1] * 512, [0.2] * 512]  # Wrong size
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in wrong_size_embeddings]
        mock_embedder._client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await mock_embedder.embed_batch(texts)

        assert "dimension mismatch" in str(exc_info.value)


class TestOpenAIEmbedderRetry:
    """Tests for retry logic on transient errors."""

    @pytest.fixture
    def mock_embedder(self) -> OpenAIEmbedder:
        """Create an embedder with mocked OpenAI client."""
        with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
            return OpenAIEmbedder(api_key="sk-test-key")

    @pytest.mark.asyncio
    async def test_retry_on_connection_error_then_success(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test retry on connection error, succeeding on retry."""
        # Arrange
        expected_embedding = [0.1] * 1536
        call_count = 0

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise APIConnectionError(request=MagicMock())
            response = MagicMock()
            response.data = [MagicMock(embedding=expected_embedding)]
            return response

        mock_embedder._client.embeddings.create = mock_create

        # Act
        result = await mock_embedder.embed("test text")

        # Assert
        assert result == expected_embedding
        assert call_count == 2  # First failed, second succeeded

    @pytest.mark.asyncio
    async def test_retry_on_timeout_then_success(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test retry on timeout, succeeding on retry."""
        # Arrange
        expected_embedding = [0.1] * 1536
        call_count = 0

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise APITimeoutError(request=MagicMock())
            response = MagicMock()
            response.data = [MagicMock(embedding=expected_embedding)]
            return response

        mock_embedder._client.embeddings.create = mock_create

        # Act
        result = await mock_embedder.embed("test text")

        # Assert
        assert result == expected_embedding
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_failure_after_max_retries_connection_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that ConnectionError is raised after max retries."""
        # Arrange
        call_count = 0

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            raise APIConnectionError(request=MagicMock())

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(ConnectionError) as exc_info:
            await mock_embedder.embed("test text")

        assert "Failed to connect" in str(exc_info.value)
        assert call_count == 3  # 3 attempts per retry config

    @pytest.mark.asyncio
    async def test_failure_after_max_retries_timeout(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that TimeoutError is raised after max retries."""
        # Arrange
        call_count = 0

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            raise APITimeoutError(request=MagicMock())

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(TimeoutError) as exc_info:
            await mock_embedder.embed("test text")

        assert "timed out" in str(exc_info.value)
        assert call_count == 3


class TestOpenAIEmbedderErrorHandling:
    """Tests for error handling (auth, rate limit, etc.)."""

    @pytest.fixture
    def mock_embedder(self) -> OpenAIEmbedder:
        """Create an embedder with mocked OpenAI client."""
        with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
            return OpenAIEmbedder(api_key="sk-test-key")

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test that rate limit error is properly converted."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 429

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise RateLimitError(
                message="Rate limit exceeded",
                response=mock_response,
                body=None,
            )

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(KMCPRateLimitError) as exc_info:
            await mock_embedder.embed("test text")

        assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_authentication_error(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test that auth error is properly converted."""
        # Arrange
        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise Exception("Invalid API key provided")

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            await mock_embedder.embed("test text")

        # Verify error message doesn't contain the actual key
        error_msg = str(exc_info.value)
        assert "sk-test-key" not in error_msg
        assert "Invalid or expired" in error_msg

    @pytest.mark.asyncio
    async def test_generic_error(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test that generic error raises ConnectionError."""
        # Arrange
        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise Exception("Some unexpected error")

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(ConnectionError) as exc_info:
            await mock_embedder.embed("test text")

        assert "Embedding generation failed" in str(exc_info.value)


class TestOpenAIEmbedderBatchErrorHandling:
    """Tests for error handling in batch embedding."""

    @pytest.fixture
    def mock_embedder(self) -> OpenAIEmbedder:
        """Create an embedder with mocked OpenAI client."""
        with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
            return OpenAIEmbedder(api_key="sk-test-key")

    @pytest.mark.asyncio
    async def test_embed_batch_rate_limit_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that rate limit error in batch is properly converted."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 429

        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise RateLimitError(
                message="Rate limit exceeded",
                response=mock_response,
                body=None,
            )

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(KMCPRateLimitError) as exc_info:
            await mock_embedder.embed_batch(["text 1", "text 2"])

        assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_embed_batch_connection_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that connection error in batch raises ConnectionError."""
        # Arrange
        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise APIConnectionError(request=MagicMock())

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(ConnectionError) as exc_info:
            await mock_embedder.embed_batch(["text 1", "text 2"])

        assert "Failed to connect" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_embed_batch_timeout_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that timeout error in batch raises TimeoutError."""
        # Arrange
        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise APITimeoutError(request=MagicMock())

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(TimeoutError) as exc_info:
            await mock_embedder.embed_batch(["text 1", "text 2"])

        assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_embed_batch_auth_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that auth error in batch is properly converted."""
        # Arrange
        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise Exception("Invalid API key provided")

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            await mock_embedder.embed_batch(["text 1", "text 2"])

        assert "Invalid or expired" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_embed_batch_generic_error(
        self, mock_embedder: OpenAIEmbedder
    ) -> None:
        """Test that generic error in batch raises ConnectionError."""
        # Arrange
        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise Exception("Some unexpected error")

        mock_embedder._client.embeddings.create = mock_create

        # Act & Assert
        with pytest.raises(ConnectionError) as exc_info:
            await mock_embedder.embed_batch(["text 1", "text 2"])

        assert "Batch embedding generation failed" in str(exc_info.value)


class TestOpenAIEmbedderHealthCheck:
    """Tests for health check functionality."""

    @pytest.fixture
    def mock_embedder(self) -> OpenAIEmbedder:
        """Create an embedder with mocked OpenAI client."""
        with patch("knowledge_mcp.embed.openai_embedder.AsyncOpenAI"):
            return OpenAIEmbedder(api_key="sk-test-key")

    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test successful health check."""
        # Arrange
        expected_embedding = [0.1] * 1536
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=expected_embedding)]
        mock_embedder._client.embeddings.create = AsyncMock(return_value=mock_response)

        # Act
        result = await mock_embedder.health_check()

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_embedder: OpenAIEmbedder) -> None:
        """Test health check returns False on failure."""
        # Arrange
        async def mock_create(*args, **kwargs):  # noqa: ARG001
            raise APIConnectionError(request=MagicMock())

        mock_embedder._client.embeddings.create = mock_create

        # Act
        result = await mock_embedder.health_check()

        # Assert
        assert result is False
