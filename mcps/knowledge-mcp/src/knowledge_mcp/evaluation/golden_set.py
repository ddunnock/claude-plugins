"""Golden test set management for RAG evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    pass


@dataclass
class GoldenQuery:
    """Single golden test query."""

    query: str
    expected_in_top_k: list[str]
    category: str = "general"
    difficulty: str = "medium"
    sources: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class GoldenTestResult:
    """Result of a single golden test."""

    query: str
    expected: list[str]
    retrieved: list[str]
    recall: float
    passed: bool


class GoldenTestSet:
    """
    Manages golden test queries for RAG evaluation.

    Loads queries from YAML file, runs against search engine,
    calculates recall@k metrics.

    Args:
        queries_file: Path to YAML file with golden queries.
        k: Number of results to check (top-k).
        pass_threshold: Minimum recall to pass (default 0.8).

    Example:
        >>> golden = GoldenTestSet(Path("data/golden_queries.yml"))
        >>> queries = golden.load_queries()
        >>> results = golden.evaluate(searcher)
    """

    def __init__(
        self,
        queries_file: Path,
        k: int = 5,
        pass_threshold: float = 0.8,
    ) -> None:
        """Initialize golden test set."""
        self.queries_file = queries_file
        self.k = k
        self.pass_threshold = pass_threshold
        self._queries: list[GoldenQuery] | None = None

    def load_queries(self) -> list[GoldenQuery]:
        """
        Load golden queries from YAML file.

        Returns:
            List of GoldenQuery objects.

        Raises:
            FileNotFoundError: If queries file doesn't exist.
        """
        if self._queries is not None:
            return self._queries

        with open(self.queries_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._queries = [
            GoldenQuery(
                query=q["query"],
                expected_in_top_k=q.get("expected_in_top_k", []),
                category=q.get("category", "general"),
                difficulty=q.get("difficulty", "medium"),
                sources=q.get("sources", []),
                notes=q.get("notes", ""),
            )
            for q in data.get("queries", [])
        ]

        return self._queries

    def evaluate_single(
        self,
        golden: GoldenQuery,
        retrieved_content: list[str],
    ) -> GoldenTestResult:
        """
        Evaluate single query against retrieved results.

        Args:
            golden: Golden query with expectations.
            retrieved_content: Retrieved text chunks.

        Returns:
            GoldenTestResult with pass/fail status.
        """
        # Check how many expected items appear in retrieved
        hits = sum(
            1 for exp in golden.expected_in_top_k
            if any(exp.lower() in ctx.lower() for ctx in retrieved_content)
        )

        recall = hits / len(golden.expected_in_top_k) if golden.expected_in_top_k else 1.0
        passed = recall >= self.pass_threshold

        return GoldenTestResult(
            query=golden.query,
            expected=golden.expected_in_top_k,
            retrieved=retrieved_content[:self.k],
            recall=recall,
            passed=passed,
        )

    def get_summary(self, results: list[GoldenTestResult]) -> dict[str, float | int]:
        """
        Get summary statistics from test results.

        Args:
            results: List of test results.

        Returns:
            Dict with pass_rate, avg_recall, total, passed, failed.
        """
        if not results:
            return {
                "pass_rate": 0.0,
                "avg_recall": 0.0,
                "total": 0,
                "passed": 0,
                "failed": 0,
            }

        passed = sum(1 for r in results if r.passed)
        avg_recall = sum(r.recall for r in results) / len(results)

        return {
            "pass_rate": passed / len(results),
            "avg_recall": avg_recall,
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
        }


def run_golden_tests(
    golden_file: Path,
    search_fn: callable,
    k: int = 5,
) -> tuple[list[GoldenTestResult], dict[str, float | int]]:
    """
    Run golden tests against a search function.

    Args:
        golden_file: Path to golden queries YAML.
        search_fn: Function that takes query string, returns list of result dicts
                   with 'content' key.
        k: Number of results to retrieve.

    Returns:
        Tuple of (results list, summary dict).
    """
    golden_set = GoldenTestSet(golden_file, k=k)
    queries = golden_set.load_queries()

    results = []
    for query in queries:
        # Run search
        search_results = search_fn(query.query)

        # Extract content from results
        retrieved_content = [
            r.get("content", str(r))
            for r in search_results[:k]
        ]

        # Evaluate
        result = golden_set.evaluate_single(query, retrieved_content)
        results.append(result)

    summary = golden_set.get_summary(results)
    return results, summary
