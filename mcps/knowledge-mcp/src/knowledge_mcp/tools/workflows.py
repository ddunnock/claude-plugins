"""Workflow tool handlers for Knowledge MCP.

Implements handlers for workflow-specific search tools:
- knowledge_rcca: Root Cause Corrective Action analysis
- knowledge_trade: Trade study comparison
- knowledge_explore: Multi-facet topic exploration
- knowledge_plan: Project planning support

All handlers return JSON-serializable dict suitable for MCP responses.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from knowledge_mcp.search.strategies.explore import ExploreStrategy
from knowledge_mcp.search.strategies.plan import PlanStrategy
from knowledge_mcp.search.strategies.rcca import RCCAStrategy
from knowledge_mcp.search.strategies.trade_study import TradeStudyStrategy
from knowledge_mcp.search.workflow_search import WorkflowSearcher

if TYPE_CHECKING:
    from knowledge_mcp.search.semantic_search import SemanticSearcher

logger = logging.getLogger(__name__)


async def handle_rcca(
    searcher: SemanticSearcher,
    query: str,
    n_results: int = 10,
    score_threshold: float = 0.0,
    project_id: str | None = None,
) -> dict[str, Any]:
    """Handle knowledge_rcca tool call.

    Performs RCCA (Root Cause Corrective Action) search optimized for
    failure analysis workflows.

    Args:
        searcher: SemanticSearcher instance.
        query: Failure symptom or issue description.
        n_results: Maximum results to return.
        score_threshold: Minimum similarity score.
        project_id: Optional project ID for query capture.

    Returns:
        Dict with RCCA-structured results including symptoms,
        root causes, and resolutions.
    """
    try:
        strategy = RCCAStrategy()
        workflow = WorkflowSearcher(searcher, strategy)

        results = await workflow.search(
            query=query,
            params={"project_id": project_id} if project_id else {},
            n_results=n_results,
            score_threshold=score_threshold,
        )

        return results

    except Exception as e:
        logger.exception("RCCA search error: %s", e)
        return {
            "error": str(e),
            "result_type": "error",
            "isError": True,
        }


async def handle_trade(
    searcher: SemanticSearcher,
    query: str,
    alternatives: list[str] | None = None,
    criteria: list[str] | None = None,
    n_results: int = 20,
    score_threshold: float = 0.0,
    project_id: str | None = None,
) -> dict[str, Any]:
    """Handle knowledge_trade tool call.

    Performs trade study search for comparing alternatives against criteria.

    Args:
        searcher: SemanticSearcher instance.
        query: Decision context or problem statement.
        alternatives: List of alternatives to compare.
        criteria: List of evaluation criteria.
        n_results: Maximum results to return.
        score_threshold: Minimum similarity score.
        project_id: Optional project ID for query capture.

    Returns:
        Dict with alternatives grouped by criteria, including evidence
        and quantitative data.
    """
    try:
        strategy = TradeStudyStrategy()
        workflow = WorkflowSearcher(searcher, strategy)

        params: dict[str, Any] = {}
        if alternatives:
            params["alternatives"] = alternatives
        if criteria:
            params["criteria"] = criteria
        if project_id:
            params["project_id"] = project_id

        results = await workflow.search(
            query=query,
            params=params,
            n_results=n_results,
            score_threshold=score_threshold,
        )

        return results

    except Exception as e:
        logger.exception("Trade study search error: %s", e)
        return {
            "error": str(e),
            "result_type": "error",
            "isError": True,
        }


async def handle_explore(
    searcher: SemanticSearcher,
    query: str,
    facets: list[str] | None = None,
    n_results: int = 20,
    score_threshold: float = 0.0,
    project_id: str | None = None,
) -> dict[str, Any]:
    """Handle knowledge_explore tool call.

    Performs multi-facet exploration for comprehensive topic understanding.

    Args:
        searcher: SemanticSearcher instance.
        query: Topic or concept to explore.
        facets: Specific facets to search (overrides defaults).
        n_results: Maximum results to return.
        score_threshold: Minimum similarity score.
        project_id: Optional project ID for query capture.

    Returns:
        Dict with results organized by facets (definitions, examples,
        standards, best_practices).
    """
    try:
        strategy = ExploreStrategy()
        workflow = WorkflowSearcher(searcher, strategy)

        params: dict[str, Any] = {}
        if facets:
            params["facets"] = facets
        if project_id:
            params["project_id"] = project_id

        results = await workflow.search(
            query=query,
            params=params,
            n_results=n_results,
            score_threshold=score_threshold,
        )

        return results

    except Exception as e:
        logger.exception("Explore search error: %s", e)
        return {
            "error": str(e),
            "result_type": "error",
            "isError": True,
        }


async def handle_plan(
    searcher: SemanticSearcher,
    query: str,
    categories: list[str] | None = None,
    n_results: int = 20,
    score_threshold: float = 0.0,
    project_id: str | None = None,
) -> dict[str, Any]:
    """Handle knowledge_plan tool call.

    Performs planning-focused search for project support workflows.

    Args:
        searcher: SemanticSearcher instance.
        query: Planning question or topic.
        categories: Specific categories to search (overrides defaults).
        n_results: Maximum results to return.
        score_threshold: Minimum similarity score.
        project_id: Optional project ID for query capture.

    Returns:
        Dict with results organized by planning categories (templates,
        risks, lessons_learned, precedents).
    """
    try:
        strategy = PlanStrategy()
        workflow = WorkflowSearcher(searcher, strategy)

        params: dict[str, Any] = {}
        if categories:
            params["categories"] = categories
        if project_id:
            params["project_id"] = project_id

        results = await workflow.search(
            query=query,
            params=params,
            n_results=n_results,
            score_threshold=score_threshold,
        )

        return results

    except Exception as e:
        logger.exception("Plan search error: %s", e)
        return {
            "error": str(e),
            "result_type": "error",
            "isError": True,
        }
