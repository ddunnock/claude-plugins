"""RAG evaluation metrics wrapper using RAGAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def evaluate_retrieval_only(
    queries: list[str],
    retrieved_contexts: list[list[str]],
    expected_in_results: list[list[str]],
) -> dict[str, float]:
    """
    Evaluate retrieval quality without LLM generation.

    This is a lightweight evaluation that doesn't require LLM calls.
    Measures recall@k: what fraction of expected results appear in retrieved.

    Args:
        queries: User queries.
        retrieved_contexts: Retrieved document chunks per query.
        expected_in_results: Expected content/clauses that should appear.

    Returns:
        Dict with recall_at_k scores.
    """
    recalls = []
    for expected, retrieved in zip(expected_in_results, retrieved_contexts, strict=True):
        if not expected:
            recalls.append(1.0)  # No expectations = pass
            continue

        # Count how many expected items appear in retrieved
        hits = sum(
            1 for exp in expected
            if any(exp.lower() in ctx.lower() for ctx in retrieved)
        )
        recall = hits / len(expected) if expected else 0.0
        recalls.append(recall)

    return {
        "recall_at_k": sum(recalls) / len(recalls) if recalls else 0.0,
        "queries_evaluated": len(queries),
        "queries_passing": sum(1 for r in recalls if r >= 0.8),
    }


def evaluate_rag_triad(
    queries: list[str],
    retrieved_contexts: list[list[str]],
    ground_truths: list[str],
    answers: list[str],
) -> dict[str, float]:
    """
    Evaluate RAG system using RAG Triad metrics via RAGAS.

    Note: This requires LLM calls and is more expensive. Use for
    periodic deep evaluation, not every test run.

    Args:
        queries: User queries.
        retrieved_contexts: Retrieved document chunks per query.
        ground_truths: Expected answers (for context recall).
        answers: Generated answers (for faithfulness check).

    Returns:
        Dict with context_precision, faithfulness, answer_relevancy scores.

    Raises:
        ImportError: If ragas is not installed.
    """
    try:
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            faithfulness,
        )
        from datasets import Dataset
    except ImportError as e:
        raise ImportError(
            "ragas and datasets required for RAG Triad evaluation. "
            "Install with: poetry install --with dev"
        ) from e

    dataset = Dataset.from_dict({
        "question": queries,
        "contexts": retrieved_contexts,
        "ground_truth": ground_truths,
        "answer": answers,
    })

    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
        ],
    )

    # Extract scores from result
    scores = {
        "context_precision": float(result["context_precision"]),
        "faithfulness": float(result["faithfulness"]),
        "answer_relevancy": float(result["answer_relevancy"]),
    }

    # Calculate overall score
    scores["overall_score"] = sum(scores.values()) / len(scores)

    return scores
