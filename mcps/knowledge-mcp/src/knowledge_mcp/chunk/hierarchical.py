"""
Hierarchical chunker for Knowledge MCP.

This module implements structure-aware document chunking that respects
clause boundaries, token limits, and table integrity while adding overlap
between chunks for context continuity.

Example:
    >>> from knowledge_mcp.chunk import HierarchicalChunker, ChunkConfig
    >>> chunker = HierarchicalChunker()
    >>> chunks = chunker.chunk(elements, metadata)
"""

from __future__ import annotations

import re

from knowledge_mcp.chunk.base import (
    BaseChunker,
    ChunkConfig,
    ChunkResult,
    DocumentMetadata,
    ParsedElement,
)
from knowledge_mcp.utils.tokenizer import truncate_to_tokens

__all__ = ["HierarchicalChunker"]


class HierarchicalChunker(BaseChunker):
    """
    Hierarchical document chunker with structure awareness.

    Splits documents into semantically coherent chunks while:
    - Respecting structural boundaries (clauses, paragraphs)
    - Staying within token limits (500 target, 1000 max)
    - Adding 20% overlap between adjacent chunks
    - Never splitting tables mid-row
    - Preserving section hierarchy and metadata

    Attributes:
        config: Chunking configuration.

    Example:
        >>> config = ChunkConfig(target_tokens=500, max_tokens=1000)
        >>> chunker = HierarchicalChunker(config)
        >>> results = chunker.chunk(elements, metadata)
        >>> len(results) > 0
        True
    """

    def __init__(self, config: ChunkConfig | None = None) -> None:
        """
        Initialize hierarchical chunker.

        Args:
            config: Chunking configuration. Uses defaults if None.
        """
        super().__init__(config)
        self._clause_pattern = re.compile(r"\b(\d+(?:\.\d+){0,4})\b")

    def chunk(
        self,
        elements: list[ParsedElement],
        metadata: DocumentMetadata,
    ) -> list[ChunkResult]:
        """
        Chunk document elements into retrieval units.

        Groups elements by section to maintain hierarchy, applies
        token limits, adds overlap between chunks, and handles
        tables with row-level splitting when needed.

        Args:
            elements: List of parsed document elements.
            metadata: Document metadata.

        Returns:
            List of chunk results with preserved metadata.

        Raises:
            ValueError: When elements list is empty.

        Example:
            >>> elements = [ParsedElement(element_type="text", content="Hello")]
            >>> metadata = DocumentMetadata("doc1", "Test Doc", "guide")
            >>> chunker = HierarchicalChunker()
            >>> chunks = chunker.chunk(elements, metadata)
            >>> len(chunks) > 0
            True
        """
        if not elements:
            raise ValueError("Elements list cannot be empty")

        chunks: list[ChunkResult] = []

        for element in elements:
            element_chunks = self._chunk_element(element)
            chunks.extend(element_chunks)

        # Add overlap between adjacent chunks
        if len(chunks) > 1:
            chunks = self._add_overlap(chunks)

        # Merge small chunks if configured
        if self.config.merge_small_chunks:
            chunks = self._merge_small_chunks(chunks)

        return chunks

    def _chunk_element(self, element: ParsedElement) -> list[ChunkResult]:
        """
        Chunk a single parsed element.

        Args:
            element: Parsed document element.

        Returns:
            List of chunk results for this element.
        """
        if element.element_type == "table":
            return self._chunk_table(element)

        # For text elements, split by token limit
        content = element.content
        token_count = self._count_tokens(content)

        if token_count <= self.config.max_tokens:
            # Single chunk
            return [
                ChunkResult(
                    content=content,
                    token_count=token_count,
                    section_hierarchy=element.section_hierarchy.copy(),
                    clause_number=self._extract_clause_number(
                        element.section_hierarchy, element.heading
                    ),
                    page_numbers=element.page_numbers.copy(),
                    chunk_type=element.element_type,
                    has_overlap=False,
                    metadata=element.metadata.copy(),
                )
            ]

        # Split large text into chunks
        return self._split_text(element)

    def _split_text(self, element: ParsedElement) -> list[ChunkResult]:
        """
        Split large text element into multiple chunks.

        Args:
            element: Parsed element with content exceeding max_tokens.

        Returns:
            List of chunk results from splitting.
        """
        chunks: list[ChunkResult] = []
        content = element.content

        # Split by paragraphs (double newline) to respect structure
        paragraphs = content.split("\n\n")
        current_chunk: list[str] = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._count_tokens(para)

            # If single paragraph exceeds max_tokens, truncate it
            if para_tokens > self.config.max_tokens:
                # Flush current chunk if any
                if current_chunk:
                    chunk_content = "\n\n".join(current_chunk)
                    chunks.append(
                        ChunkResult(
                            content=chunk_content,
                            token_count=self._count_tokens(chunk_content),
                            section_hierarchy=element.section_hierarchy.copy(),
                            clause_number=self._extract_clause_number(
                                element.section_hierarchy, element.heading
                            ),
                            page_numbers=element.page_numbers.copy(),
                            chunk_type=element.element_type,
                            has_overlap=False,
                            metadata=element.metadata.copy(),
                        )
                    )
                    current_chunk = []
                    current_tokens = 0

                # Truncate oversized paragraph
                truncated = truncate_to_tokens(
                    para, self.config.max_tokens, self.config.model
                )
                chunks.append(
                    ChunkResult(
                        content=truncated,
                        token_count=self._count_tokens(truncated),
                        section_hierarchy=element.section_hierarchy.copy(),
                        clause_number=self._extract_clause_number(
                            element.section_hierarchy, element.heading
                        ),
                        page_numbers=element.page_numbers.copy(),
                        chunk_type=element.element_type,
                        has_overlap=False,
                        metadata=element.metadata.copy(),
                    )
                )
                continue

            # Check if adding paragraph would exceed target
            if current_tokens + para_tokens > self.config.target_tokens and current_chunk:
                # Flush current chunk
                chunk_content = "\n\n".join(current_chunk)
                chunks.append(
                    ChunkResult(
                        content=chunk_content,
                        token_count=self._count_tokens(chunk_content),
                        section_hierarchy=element.section_hierarchy.copy(),
                        clause_number=self._extract_clause_number(
                            element.section_hierarchy, element.heading
                        ),
                        page_numbers=element.page_numbers.copy(),
                        chunk_type=element.element_type,
                        has_overlap=False,
                        metadata=element.metadata.copy(),
                    )
                )
                current_chunk = []
                current_tokens = 0

            # Add paragraph to current chunk
            current_chunk.append(para)
            current_tokens += para_tokens

        # Flush remaining chunk
        if current_chunk:
            chunk_content = "\n\n".join(current_chunk)
            chunks.append(
                ChunkResult(
                    content=chunk_content,
                    token_count=self._count_tokens(chunk_content),
                    section_hierarchy=element.section_hierarchy.copy(),
                    clause_number=self._extract_clause_number(
                        element.section_hierarchy, element.heading
                    ),
                    page_numbers=element.page_numbers.copy(),
                    chunk_type=element.element_type,
                    has_overlap=False,
                    metadata=element.metadata.copy(),
                )
            )

        return chunks

    def _chunk_table(self, element: ParsedElement) -> list[ChunkResult]:
        """
        Chunk a table element, splitting by rows if needed.

        Tables are never split mid-row. If a table exceeds max_tokens,
        it's split by rows with the header row preserved in each chunk.

        Args:
            element: Parsed table element.

        Returns:
            List of chunk results for the table.

        Example:
            >>> element = ParsedElement(
            ...     element_type="table",
            ...     content="Header\\nRow1\\nRow2",
            ...     metadata={"caption": "Test table"}
            ... )
            >>> chunker = HierarchicalChunker()
            >>> chunks = chunker._chunk_table(element)
            >>> chunks[0].chunk_type
            'table'
        """
        content = element.content
        token_count = self._count_tokens(content)

        # If table fits in max_tokens, return as single chunk
        if token_count <= self.config.max_tokens:
            caption = element.metadata.get("caption", "")
            chunk_content = f"{caption}\n\n{content}" if caption else content

            return [
                ChunkResult(
                    content=chunk_content,
                    token_count=self._count_tokens(chunk_content),
                    section_hierarchy=element.section_hierarchy.copy(),
                    clause_number=self._extract_clause_number(
                        element.section_hierarchy, element.heading
                    ),
                    page_numbers=element.page_numbers.copy(),
                    chunk_type="table",
                    has_overlap=False,
                    metadata=element.metadata.copy(),
                )
            ]

        # Split table by rows
        rows = content.split("\n")
        if not rows:
            return []

        # Assume first row is header
        header = rows[0] if rows else ""
        caption = element.metadata.get("caption", "")
        chunks: list[ChunkResult] = []
        current_rows = [header]
        current_tokens = self._count_tokens(header) + self._count_tokens(caption)

        for row in rows[1:]:
            row_tokens = self._count_tokens(row)

            # Check if adding row would exceed max_tokens
            if current_tokens + row_tokens > self.config.max_tokens and len(current_rows) > 1:
                # Flush current chunk
                chunk_content = "\n".join(current_rows)
                if caption:
                    chunk_content = f"{caption}\n\n{chunk_content}"

                chunks.append(
                    ChunkResult(
                        content=chunk_content,
                        token_count=self._count_tokens(chunk_content),
                        section_hierarchy=element.section_hierarchy.copy(),
                        clause_number=self._extract_clause_number(
                            element.section_hierarchy, element.heading
                        ),
                        page_numbers=element.page_numbers.copy(),
                        chunk_type="table",
                        has_overlap=False,
                        metadata=element.metadata.copy(),
                    )
                )
                # Start new chunk with header
                current_rows = [header]
                current_tokens = self._count_tokens(header) + self._count_tokens(caption)

            # Add row to current chunk
            current_rows.append(row)
            current_tokens += row_tokens

        # Flush remaining chunk
        if len(current_rows) > 1:  # More than just header
            chunk_content = "\n".join(current_rows)
            if caption:
                chunk_content = f"{caption}\n\n{chunk_content}"

            chunks.append(
                ChunkResult(
                    content=chunk_content,
                    token_count=self._count_tokens(chunk_content),
                    section_hierarchy=element.section_hierarchy.copy(),
                    clause_number=self._extract_clause_number(
                        element.section_hierarchy, element.heading
                    ),
                    page_numbers=element.page_numbers.copy(),
                    chunk_type="table",
                    has_overlap=False,
                    metadata=element.metadata.copy(),
                )
            )

        return chunks if chunks else []

    def _add_overlap(self, chunks: list[ChunkResult]) -> list[ChunkResult]:
        """
        Add overlap between adjacent chunks for context continuity.

        Takes the last overlap_tokens from each chunk and prepends
        to the next chunk with a separator.

        Args:
            chunks: List of chunks to add overlap to.

        Returns:
            List of chunks with overlap added.

        Example:
            >>> chunk1 = ChunkResult(content="First chunk", token_count=2)
            >>> chunk2 = ChunkResult(content="Second chunk", token_count=2)
            >>> chunker = HierarchicalChunker()
            >>> result = chunker._add_overlap([chunk1, chunk2])
            >>> result[1].has_overlap
            True
        """
        if len(chunks) <= 1:
            return chunks

        overlapped_chunks: list[ChunkResult] = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            curr_chunk = chunks[i]

            # Get overlap from previous chunk
            overlap_text = truncate_to_tokens(
                prev_chunk.content,
                self.config.overlap_tokens,
                self.config.model,
            )

            # Find where to take overlap from (end of previous chunk)
            # Use last N tokens instead of first N
            prev_tokens = self._count_tokens(prev_chunk.content)
            if prev_tokens > self.config.overlap_tokens:
                # Take from end by splitting and taking suffix
                words = prev_chunk.content.split()
                # Approximate: take last ~20% of words
                overlap_start = max(0, len(words) - len(words) // 5)
                overlap_text = " ".join(words[overlap_start:])
                # Verify it's within token limit
                if self._count_tokens(overlap_text) > self.config.overlap_tokens:
                    overlap_text = truncate_to_tokens(
                        overlap_text,
                        self.config.overlap_tokens,
                        self.config.model,
                    )
            else:
                overlap_text = prev_chunk.content

            # Prepend overlap to current chunk
            new_content = f"{overlap_text}\n\n---\n\n{curr_chunk.content}"
            new_token_count = self._count_tokens(new_content)

            overlapped_chunks.append(
                ChunkResult(
                    content=new_content,
                    token_count=new_token_count,
                    section_hierarchy=curr_chunk.section_hierarchy,
                    clause_number=curr_chunk.clause_number,
                    page_numbers=curr_chunk.page_numbers,
                    chunk_type=curr_chunk.chunk_type,
                    has_overlap=True,
                    metadata=curr_chunk.metadata,
                )
            )

        return overlapped_chunks

    def _merge_small_chunks(self, chunks: list[ChunkResult]) -> list[ChunkResult]:
        """
        Merge chunks under 100 tokens with adjacent chunks.

        Tries merging forward first, then backward as fallback.
        Makes multiple passes until no more merges are possible.

        Args:
            chunks: List of chunks to merge.

        Returns:
            List of chunks with small chunks merged.
        """
        if not chunks:
            return chunks

        min_chunk_size = 100

        # Make multiple passes until stable
        merged = list(chunks)
        changed = True
        max_passes = 5  # Prevent infinite loops
        passes = 0

        while changed and passes < max_passes:
            changed = False
            passes += 1
            new_merged: list[ChunkResult] = []
            i = 0

            while i < len(merged):
                chunk = merged[i]

                # If chunk is large enough, keep it
                if chunk.token_count >= min_chunk_size:
                    new_merged.append(chunk)
                    i += 1
                    continue

                # Try to merge with next chunk first
                merged_forward = False
                if i + 1 < len(merged):
                    next_chunk = merged[i + 1]
                    combined_content = f"{chunk.content}\n\n{next_chunk.content}"
                    combined_tokens = self._count_tokens(combined_content)

                    # Only merge if combined doesn't exceed max
                    if combined_tokens <= self.config.max_tokens:
                        new_merged.append(
                            ChunkResult(
                                content=combined_content,
                                token_count=combined_tokens,
                                section_hierarchy=chunk.section_hierarchy,
                                clause_number=chunk.clause_number or next_chunk.clause_number,
                                page_numbers=list(set(chunk.page_numbers + next_chunk.page_numbers)),
                                chunk_type=chunk.chunk_type,
                                has_overlap=chunk.has_overlap,
                                metadata=chunk.metadata,
                            )
                        )
                        i += 2  # Skip next chunk since we merged it
                        merged_forward = True
                        changed = True
                        continue

                # Try to merge with previous chunk if forward didn't work
                if not merged_forward and new_merged:
                    prev_chunk = new_merged[-1]
                    combined_content = f"{prev_chunk.content}\n\n{chunk.content}"
                    combined_tokens = self._count_tokens(combined_content)

                    # Only merge if combined doesn't exceed max
                    if combined_tokens <= self.config.max_tokens:
                        new_merged[-1] = ChunkResult(
                            content=combined_content,
                            token_count=combined_tokens,
                            section_hierarchy=prev_chunk.section_hierarchy,
                            clause_number=prev_chunk.clause_number or chunk.clause_number,
                            page_numbers=list(set(prev_chunk.page_numbers + chunk.page_numbers)),
                            chunk_type=prev_chunk.chunk_type,
                            has_overlap=prev_chunk.has_overlap,
                            metadata=prev_chunk.metadata,
                        )
                        i += 1
                        changed = True
                        continue

                # Couldn't merge in either direction, keep small chunk
                new_merged.append(chunk)
                i += 1

            merged = new_merged

        return merged

    def _extract_clause_number(
        self, hierarchy: list[str], heading: str
    ) -> str | None:
        """
        Extract clause number from section hierarchy or heading.

        Args:
            hierarchy: Section hierarchy path.
            heading: Section heading text.

        Returns:
            Clause number if found, None otherwise.

        Example:
            >>> chunker = HierarchicalChunker()
            >>> chunker._extract_clause_number(["5", "5.1"], "Requirements")
            '5.1'
            >>> chunker._extract_clause_number([], "5.2.3 Testing")
            '5.2.3'
        """
        # Try to get from hierarchy first
        if hierarchy:
            # Last item in hierarchy is usually the most specific clause number
            last = hierarchy[-1]
            if self._clause_pattern.match(last):
                return last

        # Try to extract from heading
        if heading:
            match = self._clause_pattern.search(heading)
            if match:
                return match.group(1)

        return None
