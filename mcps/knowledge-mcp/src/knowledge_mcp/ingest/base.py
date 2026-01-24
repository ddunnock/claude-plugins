# src/knowledge_mcp/ingest/base.py
"""
Base interfaces for document ingestion.

This module defines the base classes and data models for the
ingestion pipeline. All format-specific ingestors inherit from
BaseIngestor and produce ParsedDocument objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from knowledge_mcp.models.document import DocumentMetadata


@dataclass
class ParsedElement:
    """
    A parsed element from a document.

    Represents a structural element (heading, paragraph, table, etc.)
    extracted from a document during ingestion. Preserves hierarchy,
    location, and structured data for downstream chunking.

    Attributes:
        element_type: Type of element (heading, paragraph, table, list, figure).
        content: Text content or markdown representation.
        page_number: Source page number if available.
        section_hierarchy: Document structure path (e.g., ["4", "4.2", "4.2.3"]).
        heading_level: Heading depth (1-6) for heading elements only.
        table_data: Structured table data as rows of cells (for tables only).
        caption: Caption text for tables and figures if present.

    Example:
        >>> element = ParsedElement(
        ...     element_type="paragraph",
        ...     content="The SRR shall verify...",
        ...     page_number=12,
        ...     section_hierarchy=["4", "4.2"],
        ... )
    """

    element_type: str
    content: str
    page_number: Optional[int] = None
    section_hierarchy: list[str] = field(default_factory=lambda: [])
    heading_level: Optional[int] = None
    table_data: Optional[list[list[str]]] = None
    caption: Optional[str] = None


@dataclass
class ParsedDocument:
    """
    A fully parsed document with metadata and elements.

    Output format from all ingestors. Contains document metadata
    and a flat list of parsed elements that preserve the document's
    structure and content.

    Attributes:
        metadata: Document identification and provenance information.
        elements: Ordered list of parsed elements from the document.

    Example:
        >>> from knowledge_mcp.models.document import DocumentMetadata
        >>> metadata = DocumentMetadata(
        ...     document_id="ieee-15288-2014",
        ...     title="IEEE 15288.2-2014",
        ...     document_type="standard",
        ...     source_path="/data/sources/ieee-15288.pdf",
        ... )
        >>> elements = [
        ...     ParsedElement(element_type="heading", content="Introduction", heading_level=1),
        ...     ParsedElement(element_type="paragraph", content="This standard..."),
        ... ]
        >>> doc = ParsedDocument(metadata=metadata, elements=elements)
    """

    metadata: DocumentMetadata
    elements: list[ParsedElement] = field(default_factory=lambda: [])


class BaseIngestor(ABC):
    """
    Abstract base class for document ingestors.

    Defines the interface that all format-specific ingestors must implement.
    Each ingestor converts a source document to the common ParsedDocument
    representation for downstream processing.

    Example:
        >>> class PDFIngestor(BaseIngestor):
        ...     def ingest(self, file_path: Path) -> ParsedDocument:
        ...         # PDF-specific parsing logic
        ...         return ParsedDocument(...)
        ...
        ...     @classmethod
        ...     def supported_extensions(cls) -> list[str]:
        ...         return [".pdf"]
    """

    @abstractmethod
    def ingest(self, file_path: Path) -> ParsedDocument:
        """
        Ingest a document and convert to ParsedDocument.

        Args:
            file_path: Path to the source document file.

        Returns:
            ParsedDocument with metadata and ordered elements.

        Raises:
            IngestionError: If document cannot be parsed.
            FileNotFoundError: If file_path does not exist.
        """
        pass

    @classmethod
    @abstractmethod
    def supported_extensions(cls) -> list[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of file extensions (including leading dot, e.g., [".pdf", ".docx"]).

        Example:
            >>> PDFIngestor.supported_extensions()
            ['.pdf']
        """
        pass
