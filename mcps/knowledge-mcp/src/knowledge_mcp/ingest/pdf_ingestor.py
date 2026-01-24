# src/knowledge_mcp/ingest/pdf_ingestor.py
"""
Docling-based PDF ingestor.

This module provides a PDF ingestor using Docling's DocumentConverter
for parsing PDFs while preserving clause hierarchy, extracting tables
as structured data, and tracking page numbers.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument, NodeItem
from docling_core.types.doc.labels import DocItemLabel

from knowledge_mcp.exceptions import IngestionError
from knowledge_mcp.ingest.base import BaseIngestor, ParsedDocument, ParsedElement
from knowledge_mcp.models.document import DocumentMetadata

logger = logging.getLogger(__name__)


class PDFIngestor(BaseIngestor):
    """
    Docling-based PDF ingestor.

    Converts PDF documents to ParsedDocument objects using Docling's
    AI-based layout analysis. Preserves document structure, extracts
    tables as structured data, and tracks page numbers for all elements.

    Example:
        >>> ingestor = PDFIngestor()
        >>> doc = ingestor.ingest(Path("ieee-15288.pdf"))
        >>> print(f"Parsed {len(doc.elements)} elements")
    """

    def __init__(self) -> None:
        """Initialize the PDF ingestor with Docling converter."""
        self.converter = DocumentConverter()
        logger.debug("PDFIngestor initialized with DocumentConverter")

    def ingest(self, file_path: Path) -> ParsedDocument:
        """
        Ingest a PDF document and convert to ParsedDocument.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParsedDocument with metadata and ordered elements.

        Raises:
            IngestionError: If document cannot be parsed.
            FileNotFoundError: If file_path does not exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Ingesting PDF: {file_path}")

        try:
            # Convert PDF using Docling
            result = self.converter.convert(str(file_path))
            docling_doc: DoclingDocument = result.document

            # Extract metadata from document and file path
            metadata = self._extract_metadata(docling_doc, file_path)

            # Extract elements from document
            elements = self._extract_elements(docling_doc)

            logger.info(
                f"Successfully ingested {file_path.name}: "
                f"{len(elements)} elements extracted"
            )

            return ParsedDocument(metadata=metadata, elements=elements)

        except Exception as e:
            logger.error(f"Failed to ingest PDF {file_path}: {e}")
            raise IngestionError(f"Failed to parse PDF: {e}") from e

    def _extract_metadata(
        self, doc: DoclingDocument, file_path: Path
    ) -> DocumentMetadata:
        """
        Extract metadata from Docling document and file path.

        Args:
            doc: Docling document object.
            file_path: Source file path.

        Returns:
            DocumentMetadata with extracted information.
        """
        # Extract title from document name or first heading
        title = doc.name if hasattr(doc, "name") else file_path.stem

        # Try to extract title from first heading if available
        for item, _level in doc.iterate_items():
            if item.label == DocItemLabel.SECTION_HEADER:  # type: ignore
                title = item.text.strip()  # type: ignore
                break

        # Generate document_id from filename
        document_id = file_path.stem.lower().replace(" ", "-")

        # Default document type to "standard" (can be refined later)
        document_type = "standard"

        # Try to extract version from filename or metadata
        version: Optional[str] = None
        if "-" in file_path.stem:
            # Try to extract year-like pattern
            parts = file_path.stem.split("-")
            for part in parts:
                if part.isdigit() and len(part) == 4:
                    version = part
                    break

        return DocumentMetadata(
            document_id=document_id,
            title=str(title),  # type: ignore
            document_type=document_type,
            source_path=str(file_path.absolute()),
            version=version,
            publication_date=None,
            standard_id=None,
        )

    def _extract_elements(self, doc: DoclingDocument) -> list[ParsedElement]:
        """
        Extract elements from Docling document.

        Args:
            doc: Docling document object.

        Returns:
            List of ParsedElement objects.
        """
        elements: list[ParsedElement] = []
        section_stack: list[str] = []
        current_heading_level: int = 0

        for item, _level in doc.iterate_items():
            try:
                # Extract page number from provenance if available
                page_number: Optional[int] = None
                if hasattr(item, "prov") and item.prov:  # type: ignore
                    # Docling provenance contains page information
                    for prov_item in item.prov:  # type: ignore
                        if hasattr(prov_item, "page_no"):  # type: ignore
                            page_number = prov_item.page_no  # type: ignore
                            break

                # Determine element type and create ParsedElement
                element = self._create_element_from_item(
                    item, page_number, section_stack.copy(), current_heading_level  # type: ignore
                )

                if element:
                    elements.append(element)

                    # Update section hierarchy for headings
                    if element.element_type == "heading" and element.heading_level:
                        self._update_section_stack(
                            section_stack, element.heading_level, element.content
                        )
                        current_heading_level = element.heading_level

            except Exception as e:
                logger.warning(
                    f"Failed to parse element {item.label}: {e}. Skipping."  # type: ignore
                )
                continue

        return elements

    def _create_element_from_item(
        self,
        item: NodeItem,
        page_number: Optional[int],
        section_hierarchy: list[str],
        current_heading_level: int,
    ) -> Optional[ParsedElement]:
        """
        Create ParsedElement from Docling item.

        Args:
            item: Docling document NodeItem.
            page_number: Page number if available.
            section_hierarchy: Current section hierarchy.
            current_heading_level: Current heading depth.

        Returns:
            ParsedElement or None if item should be skipped.
        """
        # Extract text content safely
        text_content = item.text if hasattr(item, "text") and item.text else ""  # type: ignore
        # Map Docling labels to element types
        if item.label == DocItemLabel.SECTION_HEADER:  # type: ignore
            # Detect heading level from item or infer from hierarchy depth
            heading_level = len(section_hierarchy) + 1
            return ParsedElement(
                element_type="heading",
                content=str(text_content).strip(),  # type: ignore
                page_number=page_number,
                section_hierarchy=section_hierarchy,
                heading_level=heading_level,
            )

        elif item.label == DocItemLabel.PARAGRAPH:  # type: ignore
            return ParsedElement(
                element_type="paragraph",
                content=str(text_content).strip(),  # type: ignore
                page_number=page_number,
                section_hierarchy=section_hierarchy,
            )

        elif item.label == DocItemLabel.TABLE:  # type: ignore
            # Extract table as structured data
            table_data, caption = self._extract_table_data(item)
            return ParsedElement(
                element_type="table",
                content=str(text_content).strip(),  # type: ignore
                page_number=page_number,
                section_hierarchy=section_hierarchy,
                table_data=table_data,
                caption=caption,
            )

        elif item.label in (DocItemLabel.LIST_ITEM, DocItemLabel.CODE):  # type: ignore
            # Map list items and code blocks to appropriate types
            element_type = "list" if item.label == DocItemLabel.LIST_ITEM else "code"  # type: ignore
            return ParsedElement(
                element_type=element_type,
                content=str(text_content).strip(),  # type: ignore
                page_number=page_number,
                section_hierarchy=section_hierarchy,
            )

        elif item.label == DocItemLabel.PICTURE:  # type: ignore
            # Extract figure with caption
            caption_text: Optional[str] = None
            if hasattr(item, "caption") and item.caption:  # type: ignore
                caption_text = str(item.caption).strip()  # type: ignore
            return ParsedElement(
                element_type="figure",
                content=str(text_content).strip(),  # type: ignore
                page_number=page_number,
                section_hierarchy=section_hierarchy,
                caption=caption_text,
            )

        # Skip other element types for now
        return None

    def _extract_table_data(
        self, item: NodeItem
    ) -> tuple[Optional[list[list[str]]], Optional[str]]:
        """
        Extract structured table data from Docling table item.

        Args:
            item: Docling NodeItem representing a table.

        Returns:
            Tuple of (table_data, caption).
        """
        table_data: Optional[list[list[str]]] = None
        caption: Optional[str] = None

        try:
            # Export table to dataframe if possible
            if hasattr(item, "export_to_dataframe"):
                df = item.export_to_dataframe()  # type: ignore
                # Convert to list of lists (rows of cells)
                raw_data: Any = df.values.tolist()  # type: ignore
                # Convert all values to strings
                table_data = [[str(cell) for cell in row] for row in raw_data]  # type: ignore

            # Extract caption if available
            if hasattr(item, "caption") and item.caption:  # type: ignore
                caption = str(item.caption).strip()  # type: ignore

        except Exception as e:
            logger.warning(f"Failed to extract table data: {e}")

        return table_data, caption

    def _update_section_stack(
        self, section_stack: list[str], heading_level: int, heading_text: str
    ) -> None:
        """
        Update section hierarchy stack based on heading level.

        Args:
            section_stack: Current section stack to update in place.
            heading_level: Level of the new heading (1-6).
            heading_text: Text of the heading.
        """
        # Trim stack to current level
        if heading_level <= len(section_stack):
            section_stack[:] = section_stack[: heading_level - 1]

        # Add new section
        section_stack.append(heading_text)

    @classmethod
    def supported_extensions(cls) -> list[str]:
        """
        Get list of supported file extensions.

        Returns:
            List containing [".pdf"].
        """
        return [".pdf"]
