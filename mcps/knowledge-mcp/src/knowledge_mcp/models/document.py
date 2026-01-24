# src/knowledge_mcp/models/document.py
"""
Data models for document metadata.

This module defines the DocumentMetadata dataclass used during
document ingestion to track source document information.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class DocumentMetadata:
    """
    Metadata for a source document.

    Tracks identifying information for documents being ingested
    into the knowledge base. Used by ingestors to populate chunk
    metadata during the ingestion pipeline.

    Attributes:
        document_id: Unique identifier (e.g., "ieee-15288-2014").
        title: Human-readable document title (e.g., "IEEE 15288.2-2014").
        document_type: Document classification (standard, handbook, guide, spec).
        source_path: Original file path per NFR-4.4 for provenance tracking.
        version: Document version string if available.
        publication_date: Publication date in ISO format if available.
        standard_id: Standards body identifier if applicable (e.g., "IEEE 15288").

    Example:
        >>> metadata = DocumentMetadata(
        ...     document_id="ieee-15288-2014",
        ...     title="IEEE 15288.2-2014",
        ...     document_type="standard",
        ...     source_path="/data/sources/ieee-15288.pdf",
        ...     version="2014",
        ...     standard_id="IEEE 15288",
        ... )
    """

    document_id: str
    title: str
    document_type: str
    source_path: str
    version: Optional[str] = None
    publication_date: Optional[str] = None
    standard_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert metadata to dictionary for serialization.

        Returns:
            Dictionary representation of metadata.
        """
        return {
            "document_id": self.document_id,
            "title": self.title,
            "document_type": self.document_type,
            "source_path": self.source_path,
            "version": self.version,
            "publication_date": self.publication_date,
            "standard_id": self.standard_id,
        }
