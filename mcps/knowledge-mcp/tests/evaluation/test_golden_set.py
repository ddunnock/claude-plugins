"""Tests for golden test set functionality."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from knowledge_mcp.evaluation.golden_set import (
    GoldenQuery,
    GoldenTestSet,
    run_golden_tests,
)


class TestGoldenTestSet:
    """Tests for GoldenTestSet class."""

    @pytest.fixture
    def sample_queries_file(self) -> Path:
        """Create temporary golden queries file."""
        queries = {
            "queries": [
                {
                    "query": "What is verification?",
                    "expected_in_top_k": ["verification", "testing"],
                    "category": "verification",
                    "difficulty": "easy",
                },
                {
                    "query": "Requirements documentation",
                    "expected_in_top_k": ["requirements", "shall"],
                    "category": "requirements",
                    "difficulty": "medium",
                },
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            yaml.dump(queries, f)
            return Path(f.name)

    def test_load_queries(self, sample_queries_file: Path) -> None:
        """Test loading queries from YAML."""
        golden = GoldenTestSet(sample_queries_file)
        queries = golden.load_queries()

        assert len(queries) == 2
        assert isinstance(queries[0], GoldenQuery)
        assert queries[0].query == "What is verification?"

    def test_evaluate_single_pass(self, sample_queries_file: Path) -> None:
        """Test evaluation when expected content found."""
        golden = GoldenTestSet(sample_queries_file)
        query = golden.load_queries()[0]

        # Retrieved content contains expected terms
        retrieved = [
            "This discusses verification activities",
            "Testing procedures are important",
        ]

        result = golden.evaluate_single(query, retrieved)

        assert result.passed is True
        assert result.recall == 1.0

    def test_evaluate_single_fail(self, sample_queries_file: Path) -> None:
        """Test evaluation when expected content not found."""
        golden = GoldenTestSet(sample_queries_file)
        query = golden.load_queries()[0]

        # Retrieved content doesn't contain expected terms
        retrieved = [
            "Completely unrelated content",
            "Nothing about the topic",
        ]

        result = golden.evaluate_single(query, retrieved)

        assert result.passed is False
        assert result.recall == 0.0

    def test_evaluate_partial_recall(self, sample_queries_file: Path) -> None:
        """Test evaluation with partial recall."""
        golden = GoldenTestSet(sample_queries_file)
        query = golden.load_queries()[0]

        # Retrieved content contains one of two expected terms
        retrieved = [
            "This discusses verification",
            "But not the other term",
        ]

        result = golden.evaluate_single(query, retrieved)

        assert result.recall == 0.5
        assert result.passed is False  # Below 0.8 threshold

    def test_get_summary(self, sample_queries_file: Path) -> None:
        """Test summary statistics calculation."""
        golden = GoldenTestSet(sample_queries_file)
        queries = golden.load_queries()

        results = [
            golden.evaluate_single(queries[0], ["verification testing"]),
            golden.evaluate_single(queries[1], ["unrelated content"]),
        ]

        summary = golden.get_summary(results)

        assert summary["total"] == 2
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["pass_rate"] == 0.5


class TestRunGoldenTests:
    """Tests for run_golden_tests function."""

    @pytest.fixture
    def sample_queries_file(self) -> Path:
        """Create temporary golden queries file."""
        queries = {
            "queries": [
                {
                    "query": "Test query",
                    "expected_in_top_k": ["expected"],
                },
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            yaml.dump(queries, f)
            return Path(f.name)

    def test_run_golden_tests(self, sample_queries_file: Path) -> None:
        """Test running golden tests with mock search function."""
        # Mock search function that returns expected content
        def mock_search(query: str) -> list[dict[str, str]]:
            return [{"content": "This contains expected content"}]

        results, summary = run_golden_tests(
            sample_queries_file,
            mock_search,
            k=5,
        )

        assert len(results) == 1
        assert results[0].passed is True
        assert summary["pass_rate"] == 1.0
