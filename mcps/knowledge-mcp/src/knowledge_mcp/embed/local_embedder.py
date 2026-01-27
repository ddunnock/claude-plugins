# src/knowledge_mcp/embed/local_embedder.py
"""Local embedding using sentence-transformers.

Provides cost-free, offline-capable embedding generation using
HuggingFace sentence-transformers models.

Supported models:
- all-MiniLM-L6-v2: 384 dimensions, fast (default)
- all-mpnet-base-v2: 768 dimensions, higher quality

Example:
    >>> embedder = LocalEmbedder(model_name="all-MiniLM-L6-v2")
    >>> vector = await embedder.embed("What is systems engineering?")
    >>> len(vector)
    384

Security Note:
    No API keys required. Model files are downloaded from HuggingFace Hub
    on first use and cached locally.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from knowledge_mcp.embed.base import BaseEmbedder

if TYPE_CHECKING:
    from collections.abc import Sequence


class LocalEmbedder(BaseEmbedder):
    """Local embedding using sentence-transformers models.

    Implements the BaseEmbedder interface using local sentence-transformers
    models. Synchronous model inference is wrapped with asyncio.run_in_executor
    to avoid blocking the event loop.

    Attributes:
        dimensions: The dimensionality of generated embeddings (384 for default model).
        model_name: The name of the HuggingFace model being used.

    Example:
        >>> embedder = LocalEmbedder()
        >>> vectors = await embedder.embed_batch(["text1", "text2"])
        >>> len(vectors)
        2

    Note:
        Model is loaded during __init__, which may take several seconds
        on first run (downloads from HuggingFace Hub).
    """

    __slots__ = ("_model_name", "_normalize", "_executor", "_model", "_dimensions")

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        normalize_embeddings: bool = True,
    ) -> None:
        """Initialize local embedder.

        Args:
            model_name: HuggingFace model name. Default is all-MiniLM-L6-v2
                which produces 384-dimensional embeddings.
            device: Device to run inference on ("cuda", "cpu", or None for auto).
                None will auto-detect GPU availability.
            normalize_embeddings: L2-normalize embeddings for cosine similarity.
                Default is True (CRITICAL for correct similarity scores).

        Raises:
            ImportError: If sentence-transformers is not installed.
            OSError: If model cannot be loaded (network error on first run).

        Example:
            >>> embedder = LocalEmbedder()  # Uses default all-MiniLM-L6-v2
            >>> embedder = LocalEmbedder(model_name="all-mpnet-base-v2")  # Higher quality
            >>> embedder = LocalEmbedder(device="cpu")  # Force CPU
        """
        # Import inside __init__ for lazy loading (optional dependency)
        from sentence_transformers import SentenceTransformer

        self._model_name = model_name
        self._normalize = normalize_embeddings
        self._executor = ThreadPoolExecutor(max_workers=1)

        # Load model (blocking on first call, downloads from HuggingFace)
        self._model = SentenceTransformer(model_name, device=device)
        self._dimensions: int = self._model.get_sentence_embedding_dimension()

    @property
    def dimensions(self) -> int:
        """Return the embedding dimensionality.

        Returns:
            Number of dimensions in the embedding vectors.
            For all-MiniLM-L6-v2: 384
            For all-mpnet-base-v2: 768

        Example:
            >>> embedder = LocalEmbedder()
            >>> embedder.dimensions
            384
        """
        return self._dimensions

    @property
    def model_name(self) -> str:
        """Return the configured model name.

        Returns:
            HuggingFace model identifier string.

        Example:
            >>> embedder = LocalEmbedder(model_name="all-mpnet-base-v2")
            >>> embedder.model_name
            'all-mpnet-base-v2'
        """
        return self._model_name

    async def embed(self, text: str) -> list[float]:
        """Generate embedding asynchronously.

        Wraps synchronous SentenceTransformer.encode() with run_in_executor
        to avoid blocking the event loop.

        Args:
            text: The input text to embed. Must be non-empty.

        Returns:
            A list of floats representing the embedding vector.
            Length will equal self.dimensions.

        Raises:
            ValueError: If text is empty.

        Example:
            >>> vector = await embedder.embed("What is a requirement?")
            >>> len(vector) == embedder.dimensions
            True
        """
        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(
            self._executor,
            self._sync_embed,
            text,
        )
        return embedding

    def _sync_embed(self, text: str) -> list[float]:
        """Synchronous embedding (run in executor).

        Args:
            text: Text to embed.

        Returns:
            List of floats representing the embedding.
        """
        embedding = self._model.encode(
            text,
            normalize_embeddings=self._normalize,
            show_progress_bar=False,
        )
        return embedding.tolist()

    async def embed_batch(
        self,
        texts: Sequence[str],
        *,
        batch_size: int = 32,
    ) -> list[list[float]]:
        """Generate embeddings for batch.

        Processes texts in a single call for efficiency.
        Wraps synchronous encoding with run_in_executor.

        Args:
            texts: Sequence of texts to embed.
            batch_size: Maximum texts per encoding batch. Defaults to 32.

        Returns:
            List of embedding vectors, one per input text.
            Each vector has length equal to self.dimensions.

        Example:
            >>> texts = ["term 1", "term 2", "term 3"]
            >>> vectors = await embedder.embed_batch(texts)
            >>> len(vectors)
            3
        """
        if not texts:
            return []

        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(
            self._executor,
            self._sync_embed_batch,
            list(texts),
            batch_size,
        )
        return embeddings

    def _sync_embed_batch(
        self,
        texts: list[str],
        batch_size: int,
    ) -> list[list[float]]:
        """Synchronous batch embedding (run in executor).

        Args:
            texts: List of texts to embed.
            batch_size: Batch size for encoding.

        Returns:
            List of embedding vectors.
        """
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=self._normalize,
            show_progress_bar=False,
        )
        return [emb.tolist() for emb in embeddings]
