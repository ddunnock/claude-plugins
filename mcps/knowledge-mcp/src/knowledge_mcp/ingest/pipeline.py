# src/knowledge_mcp/ingest/pipeline.py
"""
Ingestion pipeline orchestrator.

This module provides the main entry point for document ingestion,
orchestrating parsing, chunking, and enrichment to produce KnowledgeChunks
ready for embedding and storage.
"""

from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path
from typing import Any

from knowledge_mcp.chunk.hierarchical import HierarchicalChunker
from knowledge_mcp.chunk.base import ChunkConfig, ChunkResult
from knowledge_mcp.exceptions import IngestionError
from knowledge_mcp.ingest.base import BaseIngestor
from knowledge_mcp.ingest.docx_ingestor import DOCXIngestor
from knowledge_mcp.ingest.pdf_ingestor import PDFIngestor
from knowledge_mcp.models.chunk import KnowledgeChunk
from knowledge_mcp.models.document import DocumentMetadata
from knowledge_mcp.utils.hashing import compute_content_hash
from knowledge_mcp.utils.normative import detect_normative, NormativeIndicator

logger = logging.getLogger(__name__)

__all__ = ["IngestionPipeline", "ingest_document"]


class IngestionPipeline:
    """
    Ingestion pipeline orchestrator.

    Coordinates document parsing, chunking, and enrichment to produce
    KnowledgeChunks ready for embedding. Automatically selects the
    appropriate ingestor based on file extension.

    Attributes:
        chunk_config: Configuration for chunking.
        ingestors: Registry of ingestors by file extension.
        chunker: Hierarchical chunker instance.

    Example:
        >>> pipeline = IngestionPipeline()
        >>> chunks = pipeline.ingest("path/to/document.pdf")
        >>> print(f"Generated {len(chunks)} chunks")
    """

    def __init__(self, chunk_config: ChunkConfig | None = None) -> None:
        """
        Initialize ingestion pipeline.

        Args:
            chunk_config: Configuration for chunking. Uses defaults if None.
        """
        self.chunk_config = chunk_config or ChunkConfig()

        # Create ingestor registry
        self.ingestors: dict[str, BaseIngestor] = {
            ".pdf": PDFIngestor(),
            ".docx": DOCXIngestor(),
        }

        # Create chunker
        self.chunker = HierarchicalChunker(self.chunk_config)

        logger.debug(
            f"IngestionPipeline initialized with {len(self.ingestors)} ingestors"
        )

    def ingest(
        self,
        file_path: Path | str,
        document_metadata: dict[str, Any] | None = None,
    ) -> list[KnowledgeChunk]:
        """
        Ingest a document and produce KnowledgeChunks.

        Orchestrates the full pipeline:
        1. Select ingestor based on file extension
        2. Parse document to extract elements
        3. Chunk elements respecting structure and token limits
        4. Enrich chunks with metadata (hash, normative, UUID)

        Args:
            file_path: Path to document file.
            document_metadata: Optional metadata to override extracted values.

        Returns:
            List of KnowledgeChunk objects ready for embedding.

        Raises:
            IngestionError: If file type is unsupported or processing fails.
            FileNotFoundError: If file_path does not exist.

        Example:
            >>> pipeline = IngestionPipeline()
            >>> chunks = pipeline.ingest("ieee-15288.pdf")
            >>> print(f"Generated {len(chunks)} chunks")
        """
        # Convert str to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)

        logger.info(f"Starting ingestion pipeline for {file_path}")

        # Select ingestor based on file extension
        file_extension = file_path.suffix.lower()
        ingestor = self.ingestors.get(file_extension)

        if ingestor is None:
            supported = ", ".join(self.ingestors.keys())
            raise IngestionError(
                f"Unsupported file extension '{file_extension}'. "
                f"Supported extensions: {supported}"
            )

        try:
            # Parse document
            logger.debug(f"Parsing document with {type(ingestor).__name__}")
            parsed = ingestor.ingest(file_path)

            # Override metadata if provided
            if document_metadata:
                for key, value in document_metadata.items():
                    if hasattr(parsed.metadata, key):
                        setattr(parsed.metadata, key, value)

            # Chunk document
            logger.debug(f"Chunking {len(parsed.elements)} elements")

            # Convert DocumentMetadata to chunk.base.DocumentMetadata
            from knowledge_mcp.chunk.base import DocumentMetadata as ChunkDocMetadata
            chunk_metadata = ChunkDocMetadata(
                document_id=parsed.metadata.document_id,
                document_title=parsed.metadata.title,
                document_type=parsed.metadata.document_type,
            )

            # Convert ParsedElements to chunk.base.ParsedElement
            from knowledge_mcp.chunk.base import ParsedElement as ChunkParsedElement
            chunk_elements: list[ChunkParsedElement] = []
            for elem in parsed.elements:
                elem_metadata: dict[str, Any] = {}
                if elem.caption:
                    elem_metadata["caption"] = elem.caption
                if elem.table_data:
                    elem_metadata["table_data"] = elem.table_data

                chunk_elem = ChunkParsedElement(
                    element_type=elem.element_type,
                    content=elem.content,
                    section_hierarchy=elem.section_hierarchy,
                    heading=elem.content if elem.element_type == "heading" else "",
                    page_numbers=[elem.page_number] if elem.page_number else [],
                    metadata=elem_metadata,
                )
                chunk_elements.append(chunk_elem)

            chunk_results = self.chunker.chunk(chunk_elements, chunk_metadata)

            # Enrich chunks
            logger.debug(f"Enriching {len(chunk_results)} chunks")
            chunks = self._enrich_chunks(chunk_results, parsed.metadata)

            logger.info(
                f"Successfully processed {file_path.name}: "
                f"{len(chunks)} chunks generated"
            )

            return chunks

        except (IngestionError, FileNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            raise IngestionError(f"Failed to process document: {e}") from e

    # RCCA metadata extraction patterns (pre-compiled for performance)
    _STANDARD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"aiag[-_]?vda[-_]?fmea[-_]?(\d{4})", re.IGNORECASE), "AIAG-VDA FMEA {0}"),
        (re.compile(r"aiag[-_]?fmea[-_]?(\d)[-_]?(\d{4})", re.IGNORECASE), "AIAG FMEA-{0} {1}"),
        (re.compile(r"mil[-_]?std[-_]?882([a-z]?)", re.IGNORECASE), "MIL-STD-882{0}"),
        (re.compile(r"iso[-_]?(\d+)[-_]?(\d{4})", re.IGNORECASE), "ISO {0}:{1}"),
        (re.compile(r"iec[-_]?(\d+)[-_]?(\d{4})", re.IGNORECASE), "IEC {0}:{1}"),
        (re.compile(r"sae[-_]?j(\d+)", re.IGNORECASE), "SAE J{0}"),
        (re.compile(r"iso[-_]?26262", re.IGNORECASE), "ISO 26262"),
        (re.compile(r"iatf[-_]?16949", re.IGNORECASE), "IATF 16949"),
        (re.compile(r"as[-_]?9100", re.IGNORECASE), "AS9100"),
    ]

    _DOMAIN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"(aiag|vda|fmea|sae[-_]?j1739)", re.IGNORECASE), "fmea"),
        (re.compile(r"(mil[-_]?std[-_]?882|iec[-_]?61508|iso[-_]?26262)", re.IGNORECASE), "safety"),
        (re.compile(r"(iso[-_]?9001|iatf[-_]?16949|as[-_]?9100)", re.IGNORECASE), "quality"),
        (re.compile(r"(iso[-_]?31000|fmeca)", re.IGNORECASE), "reliability"),
    ]

    _FAMILY_MAP: dict[str, str] = {
        "fmea": "fmea_methodology",
        "safety": "safety",
        "quality": "quality",
        "reliability": "reliability",
    }

    def _extract_standard_name(self, document_id: str) -> str | None:
        """
        Extract standard name from document_id.

        Matches document_id patterns to known standards and formats the name.

        Args:
            document_id: Document identifier (e.g., "aiag-vda-fmea-2019").

        Returns:
            Formatted standard name (e.g., "AIAG-VDA FMEA 2019") or None if unrecognized.

        Example:
            >>> pipeline._extract_standard_name("aiag-vda-fmea-2019")
            "AIAG-VDA FMEA 2019"
        """
        for pattern, template in self._STANDARD_PATTERNS:
            match = pattern.search(document_id)
            if match:
                groups = match.groups()
                # Format template with captured groups (uppercase letters)
                formatted = template.format(*[g.upper() if g else "" for g in groups])
                return formatted.strip()
        return None

    def _extract_domain(self, document_id: str) -> str | None:
        """
        Extract domain from document_id.

        Maps document_id patterns to domain categories.

        Args:
            document_id: Document identifier.

        Returns:
            Domain category ("fmea", "safety", "quality", "reliability") or None.

        Example:
            >>> pipeline._extract_domain("aiag-vda-fmea-2019")
            "fmea"
        """
        for pattern, domain in self._DOMAIN_PATTERNS:
            if pattern.search(document_id):
                return domain
        return None

    def _extract_version(self, document_id: str) -> str | None:
        """
        Extract version from document_id.

        Extracts year or version string from document_id.

        Args:
            document_id: Document identifier.

        Returns:
            Version string (e.g., "2019", "2015") or None.

        Example:
            >>> pipeline._extract_version("aiag-vda-fmea-2019")
            "2019"
        """
        # Match 4-digit year (1990-2099)
        year_match = re.search(r"(19|20)\d{2}", document_id)
        if year_match:
            return year_match.group(0)

        # Match version letter suffix (e.g., 882E -> "E")
        letter_match = re.search(r"[-_](\d+)([a-zA-Z])(?:[-_]|$)", document_id)
        if letter_match:
            return letter_match.group(2).upper()

        return None

    def _classify_family(self, domain: str | None) -> str | None:
        """
        Classify domain into standard family.

        Args:
            domain: Domain category.

        Returns:
            Standard family or None.

        Example:
            >>> pipeline._classify_family("fmea")
            "fmea_methodology"
        """
        if domain is None:
            return None
        return self._FAMILY_MAP.get(domain)

    def _enrich_chunks(
        self,
        chunk_results: list[ChunkResult],
        metadata: DocumentMetadata,
    ) -> list[KnowledgeChunk]:
        """
        Enrich chunks with computed metadata.

        Adds:
        - UUID for chunk id
        - Content hash for deduplication
        - Normative classification
        - Document metadata
        - RCCA metadata (standard, domain, version, family)

        Args:
            chunk_results: List of chunk results from chunker.
            metadata: Document metadata.

        Returns:
            List of enriched KnowledgeChunk objects.
        """
        chunks: list[KnowledgeChunk] = []

        # Extract RCCA metadata once per document
        rcca_standard = self._extract_standard_name(metadata.document_id)
        rcca_domain = self._extract_domain(metadata.document_id)
        rcca_version = self._extract_version(metadata.document_id)
        rcca_family = self._classify_family(rcca_domain)

        for chunk_result in chunk_results:
            # Generate UUID
            chunk_id = str(uuid.uuid4())

            # Compute content hash
            content_hash = compute_content_hash(chunk_result.content)

            # Detect normative status (True/False/None for unknown)
            section_path = " > ".join(chunk_result.section_hierarchy)
            normative_indicator = detect_normative(
                chunk_result.content,
                section_path=section_path,
            )
            normative_value: bool | None = None
            if normative_indicator == NormativeIndicator.NORMATIVE:
                normative_value = True
            elif normative_indicator == NormativeIndicator.INFORMATIVE:
                normative_value = False
            # UNKNOWN stays as None

            # Extract section title (last item in hierarchy)
            section_title = (
                chunk_result.section_hierarchy[-1]
                if chunk_result.section_hierarchy
                else ""
            )

            chunk = KnowledgeChunk(
                id=chunk_id,
                document_id=metadata.document_id,
                document_title=metadata.title,
                document_type=metadata.document_type,
                content=chunk_result.content,
                content_hash=content_hash,
                token_count=chunk_result.token_count,
                section_hierarchy=chunk_result.section_hierarchy,
                section_title=section_title,
                clause_number=chunk_result.clause_number,
                page_numbers=chunk_result.page_numbers,
                chunk_type=chunk_result.chunk_type,
                normative=normative_value,
                standard=rcca_standard,
                domain=rcca_domain,
                version=rcca_version,
                standard_family=rcca_family,
            )

            chunks.append(chunk)

        return chunks


def ingest_document(
    file_path: Path | str,
    **kwargs: Any,
) -> list[KnowledgeChunk]:
    """
    Convenience function to ingest a document.

    Creates an IngestionPipeline and processes the document.

    Args:
        file_path: Path to document file.
        **kwargs: Additional arguments passed to IngestionPipeline constructor.

    Returns:
        List of KnowledgeChunk objects ready for embedding.

    Raises:
        IngestionError: If file type is unsupported or processing fails.
        FileNotFoundError: If file_path does not exist.

    Example:
        >>> chunks = ingest_document("ieee-15288.pdf")
        >>> print(f"Generated {len(chunks)} chunks")
    """
    pipeline = IngestionPipeline(**kwargs)
    return pipeline.ingest(file_path)
