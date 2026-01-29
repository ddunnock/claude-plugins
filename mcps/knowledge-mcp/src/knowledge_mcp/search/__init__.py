# src/knowledge_mcp/search/__init__.py
"""Search and retrieval module for Knowledge MCP.

This module provides search functionality including semantic search,
hybrid search, reranking, and metadata filtering for the knowledge base.

Example:
    >>> from knowledge_mcp.search import SemanticSearcher, SearchResult
    >>> from knowledge_mcp.embed import OpenAIEmbedder
    >>> from knowledge_mcp.store import QdrantStore
    >>>
    >>> embedder = OpenAIEmbedder(api_key="...")
    >>> store = QdrantStore(config)
    >>> searcher = SemanticSearcher(embedder, store)
    >>> results = await searcher.search("system requirements", n_results=10)

For reranking support (requires optional dependencies):
    >>> from knowledge_mcp.search import Reranker
    >>> reranker = Reranker(provider="local")
    >>> reranked = await reranker.rerank("query", results, top_n=5)
"""

from __future__ import annotations

from knowledge_mcp.search.citation import CitationFormatter, format_citation
from knowledge_mcp.search.coverage import (
    CoverageAssessor,
    CoverageConfig,
    CoverageGap,
    CoveragePriority,
    CoverageReport,
    CoveredArea,
    assess_knowledge_coverage,
)
from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.semantic_search import SemanticSearcher

__all__: list[str] = [
    "SearchResult",
    "SemanticSearcher",
    "format_citation",
    "CitationFormatter",
    "CoverageAssessor",
    "CoverageConfig",
    "CoverageGap",
    "CoveragePriority",
    "CoverageReport",
    "CoveredArea",
    "assess_knowledge_coverage",
]

# Optional reranker import (requires 'rerank' or 'local' extras)
try:
    from knowledge_mcp.search.reranker import Reranker

    __all__.append("Reranker")
except ImportError:
    # Reranker not available - cohere or sentence-transformers not installed
    pass
