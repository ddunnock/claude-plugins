"""
Evaluation framework for RAG quality assessment.

This package provides:
- Golden test set management
- RAG Triad metrics (context relevance, faithfulness, answer relevance)
- CLI reporting for evaluation results
"""

from __future__ import annotations

from knowledge_mcp.evaluation.golden_set import (
    GoldenQuery,
    GoldenTestResult,
    GoldenTestSet,
    run_golden_tests,
)
from knowledge_mcp.evaluation.metrics import evaluate_retrieval_only
from knowledge_mcp.evaluation.reporter import (
    print_evaluation_summary,
    print_golden_results,
)

__all__ = [
    "GoldenQuery",
    "GoldenTestResult",
    "GoldenTestSet",
    "run_golden_tests",
    "evaluate_retrieval_only",
    "print_evaluation_summary",
    "print_golden_results",
]
