# src/knowledge_mcp/embed/base.py
"""
Abstract base class for embedding providers.

This module defines the `BaseEmbedder` interface that all embedding
providers must implement. This abstraction enables swapping between
OpenAI embeddings (cloud) and local models (offline use).

Example:
    >>> class MyEmbedder(BaseEmbedder):
    ...     @property
    ...     def dimensions(self) -> int:
    ...         return 1536
    ...
    ...     async def embed(self, text: str) -> list[float]:
    ...         # Implementation
    ...         ...
    ...
    ...     async def embed_batch(self, texts: list[str]) -> list[list[float]]:
    ...         # Implementation
    ...         ...

Security Note:
    Implementations MUST NOT include API keys or credentials in error
    messages per security.md §7.2.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class BaseEmbedder(ABC):
    """
    Abstract base class for embedding providers.

    Defines the interface for converting text into vector embeddings.
    All embedding implementations (OpenAI, local models) must inherit
    from this class and implement its abstract methods.

    Attributes:
        dimensions: The dimensionality of generated embeddings.

    Example:
        >>> embedder = OpenAIEmbedder(api_key="...", model="text-embedding-3-small")
        >>> vector = await embedder.embed("Systems engineering is...")
        >>> len(vector)
        1536
    """

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """
        Return the dimensionality of embeddings produced by this provider.

        Returns:
            Number of dimensions in the embedding vectors.
            For example, OpenAI text-embedding-3-small produces 1536 dimensions.

        Example:
            >>> embedder = OpenAIEmbedder(...)
            >>> embedder.dimensions
            1536
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Return the name of the embedding model.

        Returns:
            Model identifier string (e.g., "text-embedding-3-small").

        Example:
            >>> embedder = OpenAIEmbedder(...)
            >>> embedder.model_name
            'text-embedding-3-small'
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single text.

        Args:
            text: The input text to embed. Must be non-empty and within
                the model's token limit.

        Returns:
            A list of floats representing the embedding vector.
            Length will equal self.dimensions.

        Raises:
            ValidationError: If text is empty or exceeds token limit.
            ConnectionError: If embedding service is unreachable.
            TimeoutError: If embedding generation times out.
            AuthenticationError: If API credentials are invalid.
            RateLimitError: If rate limits are exceeded.

        Example:
            >>> vector = await embedder.embed("What is a system?")
            >>> len(vector) == embedder.dimensions
            True
        """
        ...

    @abstractmethod
    async def embed_batch(
        self,
        texts: Sequence[str],
        *,
        batch_size: int = 100,
    ) -> list[list[float]]:
        """
        Generate embedding vectors for multiple texts.

        Processes texts in batches to optimize API calls and respect
        rate limits. Returns embeddings in the same order as input texts.

        Args:
            texts: Sequence of texts to embed. Each must be non-empty.
            batch_size: Maximum texts per API call. Defaults to 100.
                Should not exceed provider limits.

        Returns:
            List of embedding vectors, one per input text.
            Each vector has length equal to self.dimensions.

        Raises:
            ValidationError: If any text is empty or exceeds token limit.
            ConnectionError: If embedding service is unreachable.
            TimeoutError: If batch embedding times out.
            AuthenticationError: If API credentials are invalid.
            RateLimitError: If rate limits are exceeded.

        Example:
            >>> texts = ["definition of system", "types of requirements"]
            >>> vectors = await embedder.embed_batch(texts)
            >>> len(vectors)
            2
            >>> all(len(v) == embedder.dimensions for v in vectors)
            True
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if the embedding service is available.

        Performs a minimal embedding request to verify connectivity
        and authentication.

        Returns:
            True if service is healthy, False otherwise.

        Example:
            >>> if await embedder.health_check():
            ...     print("Embedding service is ready")
        """
        try:
            # Embed a minimal test string
            result = await self.embed("test")
            return len(result) == self.dimensions
        except Exception:  # noqa: BLE001
            return False
