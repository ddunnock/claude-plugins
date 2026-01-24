"""
Base chunker interface for Knowledge MCP.

This module defines the abstract interface for document chunkers,
along with configuration and result models for chunking operations.

Example:
    >>> from knowledge_mcp.chunk.base import ChunkConfig, BaseChunker
    >>> config = ChunkConfig(target_tokens=500, max_tokens=1000)
    >>> chunker = SomeChunker(config)
    >>> results = chunker.chunk(elements, metadata)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from knowledge_mcp.utils.tokenizer import count_tokens

__all__ = ["ChunkConfig", "ChunkResult", "ParsedElement", "DocumentMetadata", "BaseChunker"]


@dataclass
class ChunkConfig:
    """
    Configuration for document chunking.

    Attributes:
        target_tokens: Target chunk size in tokens (soft limit).
        max_tokens: Maximum chunk size in tokens (hard limit, split if exceeded).
        overlap_tokens: Number of tokens to overlap between adjacent chunks.
        model: OpenAI model name for token counting.
        merge_small_chunks: Whether to merge chunks under 100 tokens with peers.

    Example:
        >>> config = ChunkConfig(target_tokens=500, max_tokens=1000)
        >>> config.overlap_tokens
        100
    """

    target_tokens: int = 500
    max_tokens: int = 1000
    overlap_tokens: int = 100
    model: str = "text-embedding-3-small"
    merge_small_chunks: bool = True


@dataclass
class ParsedElement:
    """
    A parsed element from a document.

    Represents a structural unit (paragraph, table, heading, etc.)
    extracted from a document during parsing.

    Attributes:
        element_type: Type of element (text, table, heading, list, figure).
        content: Text content of the element.
        section_hierarchy: Path through document structure (e.g., ["1", "1.2", "1.2.3"]).
        heading: Section heading text if applicable.
        page_numbers: Page numbers where element appears.
        metadata: Additional element-specific metadata.

    Example:
        >>> element = ParsedElement(
        ...     element_type="text",
        ...     content="The system shall...",
        ...     section_hierarchy=["5", "5.1"],
        ...     heading="Requirements",
        ... )
    """

    element_type: str
    content: str
    section_hierarchy: list[str] = field(default_factory=lambda: [])
    heading: str = ""
    page_numbers: list[int] = field(default_factory=lambda: [])
    metadata: dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class DocumentMetadata:
    """
    Metadata for a source document.

    Attributes:
        document_id: Unique document identifier.
        document_title: Human-readable document title.
        document_type: Document classification (standard, handbook, guide, spec).

    Example:
        >>> metadata = DocumentMetadata(
        ...     document_id="ieee-15288.2",
        ...     document_title="IEEE 15288.2-2014",
        ...     document_type="standard",
        ... )
    """

    document_id: str
    document_title: str
    document_type: str


@dataclass
class ChunkResult:
    """
    Result of chunking a document element.

    Represents a semantically coherent chunk suitable for embedding,
    with preserved metadata for retrieval.

    Attributes:
        content: Chunk text content.
        token_count: Number of tokens in chunk.
        section_hierarchy: Path through document structure.
        clause_number: Clause identifier if extracted from heading.
        page_numbers: Page numbers where chunk appears.
        chunk_type: Content classification (text, table, list, figure).
        has_overlap: True if chunk starts with overlap from previous chunk.
        metadata: Additional chunk-specific metadata (e.g., table caption).

    Example:
        >>> chunk = ChunkResult(
        ...     content="The system shall...",
        ...     token_count=45,
        ...     section_hierarchy=["5", "5.1"],
        ...     clause_number="5.1",
        ...     chunk_type="text",
        ... )
    """

    content: str
    token_count: int
    section_hierarchy: list[str] = field(default_factory=lambda: [])
    clause_number: str | None = None
    page_numbers: list[int] = field(default_factory=lambda: [])
    chunk_type: str = "text"
    has_overlap: bool = False
    metadata: dict[str, Any] = field(default_factory=lambda: {})


class BaseChunker(ABC):
    """
    Abstract base class for document chunkers.

    Chunkers split documents into semantically coherent units
    suitable for embedding and retrieval while respecting
    structural boundaries and token limits.

    Attributes:
        config: Chunking configuration.

    Example:
        >>> class MyChunker(BaseChunker):
        ...     def chunk(self, elements, metadata):
        ...         # Implementation here
        ...         pass
        >>> chunker = MyChunker()
        >>> results = chunker.chunk(elements, metadata)
    """

    def __init__(self, config: ChunkConfig | None = None) -> None:
        """
        Initialize chunker with configuration.

        Args:
            config: Chunking configuration. Uses defaults if None.
        """
        self.config = config or ChunkConfig()

    @abstractmethod
    def chunk(
        self,
        elements: list[ParsedElement],
        metadata: DocumentMetadata,
    ) -> list[ChunkResult]:
        """
        Chunk document elements into retrieval units.

        Args:
            elements: List of parsed document elements.
            metadata: Document metadata.

        Returns:
            List of chunk results with preserved metadata.

        Raises:
            ValueError: When elements list is empty.
        """
        pass

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text using configured model.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens in the text.

        Example:
            >>> chunker = SomeChunker()
            >>> count = chunker._count_tokens("Hello world")
            >>> count
            2
        """
        return count_tokens(text, model=self.config.model)
