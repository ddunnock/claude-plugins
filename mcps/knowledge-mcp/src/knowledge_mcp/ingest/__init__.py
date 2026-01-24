# src/knowledge_mcp/ingest/__init__.py
"""
Document ingestion module for Knowledge MCP.

This module provides ingestors for parsing various document formats
(PDF, DOCX, Markdown) and extracting structured content for chunking.

Example:
    >>> from knowledge_mcp.ingest import PDFIngestor
    >>> ingestor = PDFIngestor()
    >>> sections = ingestor.ingest(Path("document.pdf"))
"""

from __future__ import annotations

from knowledge_mcp.ingest.base import BaseIngestor, ParsedDocument, ParsedElement
from knowledge_mcp.ingest.pdf_ingestor import PDFIngestor

__all__: list[str] = ["BaseIngestor", "ParsedDocument", "ParsedElement", "PDFIngestor"]
