"""Integration tests for hybrid search demonstrating FR-3.2 improvements."""

from unittest.mock import AsyncMock

import pytest

from knowledge_mcp.search.bm25 import BM25Searcher
from knowledge_mcp.search.hybrid import HybridSearcher
from knowledge_mcp.search.models import SearchResult
from knowledge_mcp.search.semantic_search import SemanticSearcher


@pytest.mark.integration
class TestHybridSearchIntegration:
    """Integration tests demonstrating hybrid search improvements over pure semantic."""

    @pytest.fixture
    def technical_corpus(self) -> list[dict[str, str]]:
        """
        Create a technical corpus with precise terminology.

        This corpus tests FR-3.2: hybrid retrieval should boost exact keyword
        matches (e.g., "traceability matrix", "SHALL requirement") that might
        not rank highly in pure semantic search.
        """
        return [
            {
                "id": "doc1",
                "content": "The System Requirements Review (SRR) evaluates completeness of requirements.",
            },
            {
                "id": "doc2",
                "content": "A requirements traceability matrix (RTM) maps requirements to design and test cases.",
            },
            {
                "id": "doc3",
                "content": "Verification methods include test, analysis, inspection, and demonstration.",
            },
            {
                "id": "doc4",
                "content": "The system SHALL maintain traceability between requirements and verification results.",
            },
            {
                "id": "doc5",
                "content": "Requirements validation ensures the system solves the right problem.",
            },
        ]

    @pytest.fixture
    def mock_semantic_searcher(self, technical_corpus: list[dict[str, str]]) -> AsyncMock:
        """
        Create a mock semantic searcher with simulated semantic similarity.

        For the query "traceability matrix", we simulate semantic search ranking
        by general concept similarity (not exact keyword match). This shows how
        semantic search might miss exact technical terms.
        """
        searcher = AsyncMock(spec=SemanticSearcher)

        async def mock_search(query: str, n_results: int = 10, **kwargs) -> list[SearchResult]:
            """Mock semantic search with simulated similarity scores."""
            # Simulate semantic search ranking by concept similarity
            if "traceability" in query.lower():
                # For "traceability" queries, simulate semantic ranking
                # Semantic might rank "requirements" docs higher due to conceptual similarity
                return [
                    SearchResult(
                        id="doc1",
                        content=technical_corpus[0]["content"],
                        score=0.78,  # High semantic similarity (mentions "requirements")
                    ),
                    SearchResult(
                        id="doc5",
                        content=technical_corpus[4]["content"],
                        score=0.75,  # High semantic similarity (mentions "requirements")
                    ),
                    SearchResult(
                        id="doc2",
                        content=technical_corpus[1]["content"],
                        score=0.65,  # Lower score despite exact keyword match
                    ),
                    SearchResult(
                        id="doc4",
                        content=technical_corpus[3]["content"],
                        score=0.62,  # Lower score despite exact keyword match
                    ),
                ]
            elif "verification" in query.lower():
                # For "verification" queries
                return [
                    SearchResult(
                        id="doc1",
                        content=technical_corpus[0]["content"],
                        score=0.70,  # Related to review process
                    ),
                    SearchResult(
                        id="doc3",
                        content=technical_corpus[2]["content"],
                        score=0.68,  # Exact match for "verification"
                    ),
                    SearchResult(
                        id="doc4",
                        content=technical_corpus[3]["content"],
                        score=0.65,  # Mentions verification results
                    ),
                ]
            # Default: return all docs with decreasing scores
            return [
                SearchResult(
                    id=technical_corpus[i]["id"],
                    content=technical_corpus[i]["content"],
                    score=0.8 - i * 0.1,
                )
                for i in range(min(n_results, len(technical_corpus)))
            ]

        searcher.search.side_effect = mock_search
        return searcher

    @pytest.fixture
    def bm25_searcher(self, technical_corpus: list[dict[str, str]]) -> BM25Searcher:
        """Create a BM25 searcher with indexed corpus."""
        searcher = BM25Searcher()
        searcher.build_index(technical_corpus)
        return searcher

    @pytest.fixture
    def hybrid_searcher(
        self,
        mock_semantic_searcher: AsyncMock,
        bm25_searcher: BM25Searcher,
    ) -> HybridSearcher:
        """Create a hybrid searcher combining mocked semantic and real BM25."""
        return HybridSearcher(mock_semantic_searcher, bm25_searcher)

    @pytest.mark.asyncio
    async def test_hybrid_improves_keyword_match_ranking(
        self,
        hybrid_searcher: HybridSearcher,
        mock_semantic_searcher: AsyncMock,
    ) -> None:
        """
        Test that hybrid search improves ranking for exact keyword matches.

        This demonstrates FR-3.2: BM25 contribution should boost documents
        containing exact technical terms ("traceability matrix") above
        documents that are semantically similar but lack the exact term.
        """
        # Arrange
        query = "traceability matrix"

        # Act - Hybrid search
        hybrid_results = await hybrid_searcher.search(query, n_results=5)

        # Also get pure semantic results for comparison
        semantic_results = await mock_semantic_searcher.search(query, n_results=5)

        # Assert - Hybrid search should rank exact keyword matches higher
        assert len(hybrid_results) > 0

        # Find positions of docs with exact keyword matches
        doc2_hybrid_pos = next(
            (i for i, r in enumerate(hybrid_results) if r.id == "doc2"), None
        )
        doc4_hybrid_pos = next(
            (i for i, r in enumerate(hybrid_results) if r.id == "doc4"), None
        )

        doc2_semantic_pos = next(
            (i for i, r in enumerate(semantic_results) if r.id == "doc2"), None
        )

        # doc2 contains "traceability matrix" - exact match for both keywords
        # In pure semantic, it ranks 3rd (position 2)
        # In hybrid, it should rank at least as high due to BM25 boost
        assert doc2_semantic_pos == 2  # Verify semantic baseline
        assert doc2_hybrid_pos is not None
        assert doc2_hybrid_pos <= doc2_semantic_pos  # At least as good or better

        # doc4 contains "traceability" - partial match should also appear
        assert doc4_hybrid_pos is not None

    @pytest.mark.asyncio
    async def test_hybrid_combines_semantic_and_lexical_signals(
        self,
        hybrid_searcher: HybridSearcher,
    ) -> None:
        """
        Test that hybrid search combines both semantic understanding and exact matching.

        Hybrid search should:
        1. Find documents with exact keyword matches (BM25 strength)
        2. Find semantically similar documents (semantic strength)
        3. Rank documents appearing in both lists highest (RRF fusion)
        """
        # Arrange
        query = "traceability"

        # Act
        results = await hybrid_searcher.search(query, n_results=5)

        # Assert
        assert len(results) > 0

        # Documents with "traceability" keyword should appear
        result_ids = [r.id for r in results]
        assert "doc2" in result_ids  # "requirements traceability matrix"
        assert "doc4" in result_ids  # "SHALL maintain traceability"

        # Results should have RRF scores (hybrid fusion happened)
        assert all(r.score > 0 for r in results)

    @pytest.mark.asyncio
    async def test_hybrid_handles_technical_terminology(
        self,
        hybrid_searcher: HybridSearcher,
    ) -> None:
        """
        Test that hybrid search handles technical terms better than pure semantic.

        Technical terms like "RTM" (requirements traceability matrix) benefit
        from keyword matching since they may not have strong semantic embeddings.
        """
        # Arrange
        query = "verification methods"

        # Act
        results = await hybrid_searcher.search(query, n_results=5)

        # Assert
        assert len(results) > 0

        # doc3 mentions "verification methods" - should rank highly
        result_ids = [r.id for r in results]
        assert "doc3" in result_ids

    @pytest.mark.asyncio
    async def test_hybrid_search_end_to_end(
        self,
        hybrid_searcher: HybridSearcher,
    ) -> None:
        """
        End-to-end test of hybrid search demonstrating complete workflow.

        This test verifies the complete hybrid retrieval pipeline:
        1. Query submitted
        2. Semantic search executes (mocked)
        3. BM25 search executes (real)
        4. Results merged via RRF
        5. Top-k results returned
        """
        # Arrange
        query = "requirements traceability"
        n_results = 3

        # Act
        results = await hybrid_searcher.search(query, n_results=n_results)

        # Assert
        assert len(results) <= n_results
        assert all(isinstance(r, SearchResult) for r in results)
        assert all(hasattr(r, "id") for r in results)
        assert all(hasattr(r, "content") for r in results)
        assert all(hasattr(r, "score") for r in results)

        # Verify results are ordered by score descending
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
