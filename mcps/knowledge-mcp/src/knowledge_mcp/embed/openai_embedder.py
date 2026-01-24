# src/knowledge_mcp/embed/openai_embedder.py
"""
OpenAI embedding provider for Knowledge MCP.

This module implements the `BaseEmbedder` interface using OpenAI's
text-embedding-3-small model. It includes batching for efficiency
and retry logic for resilience per AD-006.

Example:
    >>> from knowledge_mcp.embed import OpenAIEmbedder
    >>> embedder = OpenAIEmbedder(api_key="sk-...", model="text-embedding-3-small")
    >>> vector = await embedder.embed("What is systems engineering?")
    >>> len(vector)
    1536

Security Note:
    API keys are NEVER logged or included in error messages
    per security.md §7.2.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from knowledge_mcp.embed.base import BaseEmbedder
from knowledge_mcp.exceptions import (
    AuthenticationError,
    ConnectionError,
    RateLimitError as KMCPRateLimitError,
    TimeoutError,
    ValidationError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from knowledge_mcp.embed.cache import EmbeddingCache
    from knowledge_mcp.monitoring.token_tracker import TokenTracker


# Default configuration per A-REQ-IF-002
DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_DIMENSIONS = 1536
MAX_BATCH_SIZE = 100


class OpenAIEmbedder(BaseEmbedder):
    """
    OpenAI embedding provider using text-embedding-3-small.

    Implements batching with configurable batch size (max 100) and
    retry logic with exponential backoff per AD-006:
    - 3 attempts maximum
    - Exponential backoff (1s, 2s, 4s)
    - Retries on ConnectionError, TimeoutError

    Attributes:
        dimensions: Returns 1536 for text-embedding-3-small.
        model_name: Returns the configured model name.

    Example:
        >>> embedder = OpenAIEmbedder(api_key="sk-...")
        >>> vectors = await embedder.embed_batch(["text1", "text2"])
        >>> len(vectors)
        2

    Security:
        API key is stored in memory but never logged or exposed
        in error messages.
    """

    __slots__ = ("_client", "_model", "_dimensions", "_cache", "_token_tracker")

    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_MODEL,
        dimensions: int = DEFAULT_DIMENSIONS,
        cache: EmbeddingCache | None = None,
        token_tracker: TokenTracker | None = None,
    ) -> None:
        """
        Initialize the OpenAI embedder.

        Args:
            api_key: OpenAI API key. Must be valid and have embeddings access.
            model: Model name. Defaults to "text-embedding-3-small".
            dimensions: Expected embedding dimensions. Defaults to 1536.
            cache: Optional embedding cache for cost savings.
            token_tracker: Optional token usage tracker for monitoring.

        Raises:
            ValidationError: If api_key is empty.

        Example:
            >>> embedder = OpenAIEmbedder(api_key="sk-proj-...")
            >>> # With cache and tracking:
            >>> cache = EmbeddingCache(Path("data/cache"), "text-embedding-3-small")
            >>> tracker = TokenTracker(Path("data/tokens.json"))
            >>> embedder = OpenAIEmbedder(api_key="sk-...", cache=cache, token_tracker=tracker)
        """
        if not api_key:
            raise ValidationError("OpenAI API key is required")

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._dimensions = dimensions
        self._cache = cache
        self._token_tracker = token_tracker

    @property
    def dimensions(self) -> int:
        """Return the embedding dimensionality (1536 for text-embedding-3-small)."""
        return self._dimensions

    @property
    def model_name(self) -> str:
        """Return the configured model name."""
        return self._model

    @retry(
        retry=retry_if_exception_type((APIConnectionError, APITimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def _call_embedding_api(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Call OpenAI embedding API with retry logic.

        Args:
            texts: List of texts to embed (max 100).

        Returns:
            List of embedding vectors.

        Raises:
            APIConnectionError: On connection failure (retried).
            APITimeoutError: On timeout (retried).
            Other OpenAI exceptions: Propagated after conversion.
        """
        response = await self._client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    async def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single text.

        Checks cache before calling API. Stores result in cache and tracks
        token usage when configured.

        Args:
            text: The input text to embed. Must be non-empty.

        Returns:
            A list of floats representing the embedding vector.

        Raises:
            ValidationError: If text is empty.
            ConnectionError: If OpenAI API is unreachable after retries.
            TimeoutError: If request times out after retries.
            AuthenticationError: If API key is invalid.
            RateLimitError: If rate limit is exceeded.

        Example:
            >>> vector = await embedder.embed("What is a requirement?")
            >>> len(vector)
            1536
        """
        if not text or not text.strip():
            raise ValidationError("Text cannot be empty")

        # Check cache first (if configured)
        if self._cache is not None:
            cached = self._cache.get(text)
            if cached is not None:
                # Track cache hit (if tracker configured)
                if self._token_tracker is not None:
                    self._token_tracker.track_embedding(text, cache_hit=True)
                return cached

        # Cache miss - call OpenAI API
        try:
            result = await self._call_embedding_api([text])
            embedding = result[0]

            # Validate dimensions
            if len(embedding) != self._dimensions:
                raise ValidationError(
                    f"Embedding dimension mismatch: expected {self._dimensions}, "
                    f"got {len(embedding)}"
                )

            # Store in cache (if configured)
            if self._cache is not None:
                self._cache.set(text, embedding)

            # Track API usage (if tracker configured)
            if self._token_tracker is not None:
                self._token_tracker.track_embedding(text, cache_hit=False)

            return embedding

        except APITimeoutError as e:
            # Timeout is more specific - handle before APIConnectionError
            raise TimeoutError(
                "OpenAI embedding request timed out after retries"
            ) from e

        except APIConnectionError as e:
            # Connection failed after retries - generic message, no API key
            raise ConnectionError(
                "Failed to connect to OpenAI embedding service"
            ) from e

        except RateLimitError as e:
            raise KMCPRateLimitError(
                "OpenAI rate limit exceeded, please retry later"
            ) from e

        except ValidationError:
            # Let validation errors propagate unchanged
            raise

        except Exception as e:
            # Check for auth errors - message should not contain API key
            error_msg = str(e).lower()
            if "invalid api key" in error_msg or "unauthorized" in error_msg:
                raise AuthenticationError(
                    "Invalid or expired OpenAI API key"
                ) from e
            # Re-raise with generic message to avoid leaking internals
            raise ConnectionError(
                "Embedding generation failed"
            ) from e

    async def embed_batch(
        self,
        texts: Sequence[str],
        *,
        batch_size: int = MAX_BATCH_SIZE,
    ) -> list[list[float]]:
        """
        Generate embedding vectors for multiple texts.

        Processes texts in batches to optimize API calls.
        Uses per-text caching for optimal cache hit rate.
        Maximum batch size is 100 per OpenAI limits.

        Args:
            texts: Sequence of texts to embed.
            batch_size: Maximum texts per API call. Defaults to 100.
                Will be clamped to MAX_BATCH_SIZE if larger.

        Returns:
            List of embedding vectors, one per input text.

        Raises:
            ValidationError: If any text is empty.
            ConnectionError: If OpenAI API is unreachable.
            TimeoutError: If batch embedding times out.
            AuthenticationError: If API key is invalid.
            RateLimitError: If rate limit is exceeded.

        Example:
            >>> texts = ["term 1", "term 2", "term 3"]
            >>> vectors = await embedder.embed_batch(texts, batch_size=2)
            >>> len(vectors)
            3
        """
        if not texts:
            return []

        # Validate all texts first
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise ValidationError(f"Text at index {i} cannot be empty")

        texts_list = list(texts)  # Ensure we can slice

        # Separate cached vs uncached texts
        result_embeddings: dict[int, list[float]] = {}
        texts_to_embed: list[tuple[int, str]] = []

        for i, text in enumerate(texts_list):
            if self._cache is not None:
                cached = self._cache.get(text)
                if cached is not None:
                    result_embeddings[i] = cached
                    if self._token_tracker is not None:
                        self._token_tracker.track_embedding(text, cache_hit=True)
                    continue
            texts_to_embed.append((i, text))

        # Process uncached texts in batches
        if texts_to_embed:
            # Clamp batch size to maximum
            effective_batch_size = min(batch_size, MAX_BATCH_SIZE)

            for batch_start in range(0, len(texts_to_embed), effective_batch_size):
                batch_items = texts_to_embed[batch_start : batch_start + effective_batch_size]
                batch_texts = [text for _, text in batch_items]

                try:
                    batch_embeddings = await self._call_embedding_api(batch_texts)

                    # Validate dimensions and store results
                    for (original_idx, text), embedding in zip(batch_items, batch_embeddings):
                        if len(embedding) != self._dimensions:
                            raise ValidationError(
                                f"Embedding dimension mismatch at index {original_idx}: "
                                f"expected {self._dimensions}, got {len(embedding)}"
                            )

                        # Store in cache (if configured)
                        if self._cache is not None:
                            self._cache.set(text, embedding)

                        # Track API usage (if tracker configured)
                        if self._token_tracker is not None:
                            self._token_tracker.track_embedding(text, cache_hit=False)

                        result_embeddings[original_idx] = embedding

                except APITimeoutError as e:
                    raise TimeoutError(
                        "OpenAI embedding batch request timed out"
                    ) from e

                except APIConnectionError as e:
                    raise ConnectionError(
                        "Failed to connect to OpenAI embedding service"
                    ) from e

                except RateLimitError as e:
                    raise KMCPRateLimitError(
                        "OpenAI rate limit exceeded during batch processing"
                    ) from e

                except ValidationError:
                    # Let validation errors propagate unchanged
                    raise

                except Exception as e:
                    error_msg = str(e).lower()
                    if "invalid api key" in error_msg or "unauthorized" in error_msg:
                        raise AuthenticationError(
                            "Invalid or expired OpenAI API key"
                        ) from e
                    raise ConnectionError(
                        "Batch embedding generation failed"
                    ) from e

        # Reassemble results in original order
        return [result_embeddings[i] for i in range(len(texts_list))]
