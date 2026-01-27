"""Acquisition tool handlers for Knowledge MCP.

Implements handlers for:
- knowledge_ingest: Trigger document/web ingestion
- knowledge_sources: List/filter knowledge sources
- knowledge_assess: Assess coverage gaps
- knowledge_preflight: Check URL accessibility
- knowledge_acquire: Acquire web content
- knowledge_request: Create acquisition request

All handlers are async and return dict suitable for JSON serialization.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from knowledge_mcp.db.models import AuthorityTier, SourceStatus, SourceType
from knowledge_mcp.db.repositories import AcquisitionRequestRepository, SourceRepository
from knowledge_mcp.ingest import WebIngestor, check_url_accessible
from knowledge_mcp.search import CoverageAssessor, SemanticSearcher

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def handle_ingest(  # noqa: PLR0911
    session: AsyncSession,
    url: str,
    source_type: str = "web",
    authority_tier: str = "tier3",
    title: str | None = None,
) -> dict[str, Any]:
    """Handle knowledge_ingest tool call.

    Creates source record and triggers ingestion if web URL.

    Args:
        session: Database session.
        url: URL or path to ingest.
        source_type: Type (document, web, standard).
        authority_tier: Authority level (tier1, tier2, tier3).
        title: Optional title override.

    Returns:
        Dict with source_id and status.
    """
    try:
        # Validate source type
        try:
            st = SourceType(source_type)
        except ValueError:
            return {"error": f"Invalid source_type: {source_type}", "isError": True}

        # Validate authority tier
        try:
            at = AuthorityTier(authority_tier)
        except ValueError:
            return {"error": f"Invalid authority_tier: {authority_tier}", "isError": True}

        # Create source record
        repo = SourceRepository(session)

        # Check if source already exists
        existing = await repo.get_by_url(url)
        if existing:
            return {
                "source_id": existing.id,
                "status": existing.status.value,
                "message": "Source already exists",
                "already_exists": True,
            }

        # Create new source
        source = await repo.create(
            url=url,
            title=title or url,
            source_type=st,
            authority_tier=at.value,
        )

        # For web sources, trigger ingestion
        if st == SourceType.WEB:
            await repo.update_status(source.id, SourceStatus.INGESTING)

            ingestor = WebIngestor()
            result = await ingestor.ingest(url)

            if result.success:
                await repo.update_status(
                    source.id,
                    SourceStatus.COMPLETE,
                )
                return {
                    "source_id": source.id,
                    "status": "complete",
                    "title": result.title or title,
                    "word_count": result.word_count,
                    "message": "Web content ingested successfully",
                }
            else:
                await repo.update_status(
                    source.id,
                    SourceStatus.FAILED,
                )
                return {
                    "source_id": source.id,
                    "status": "failed",
                    "error": result.error,
                    "isError": True,
                }

        # For documents, mark as pending (ingestion via CLI)
        return {
            "source_id": source.id,
            "status": "pending",
            "message": f"Source created. Run CLI to ingest {source_type} content.",
        }

    except Exception as e:
        logger.exception("Ingest error: %s", e)
        return {"error": str(e), "isError": True}


async def handle_sources(
    session: AsyncSession,
    source_type: str | None = None,
    status: str | None = None,
    authority_tier: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Handle knowledge_sources tool call.

    Lists and filters knowledge sources.

    Args:
        session: Database session.
        source_type: Filter by type.
        status: Filter by status.
        authority_tier: Filter by authority.
        limit: Maximum results.

    Returns:
        Dict with sources list.
    """
    try:
        from sqlalchemy import select

        from knowledge_mcp.db.models import Source

        # Build query
        stmt = select(Source).order_by(Source.created_at.desc()).limit(limit)

        if source_type:
            try:
                st = SourceType(source_type)
                stmt = stmt.where(Source.source_type == st)
            except ValueError:
                return {"error": f"Invalid source_type: {source_type}", "isError": True}

        if status:
            try:
                ss = SourceStatus(status)
                stmt = stmt.where(Source.status == ss)
            except ValueError:
                return {"error": f"Invalid status: {status}", "isError": True}

        if authority_tier:
            try:
                at = AuthorityTier(authority_tier)
                stmt = stmt.where(Source.authority_tier == at)
            except ValueError:
                return {"error": f"Invalid authority_tier: {authority_tier}", "isError": True}

        # Execute query
        result = await session.execute(stmt)
        sources = list(result.scalars().all())

        # Format response
        return {
            "sources": [
                {
                    "id": s.id,
                    "url": s.url,
                    "title": s.title,
                    "source_type": s.source_type.value,
                    "status": s.status.value,
                    "authority_tier": s.authority_tier.value,
                    "chunk_count": s.chunk_count,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sources
            ],
            "total": len(sources),
        }

    except Exception as e:
        logger.exception("Sources error: %s", e)
        return {"error": str(e), "isError": True}


async def handle_assess(
    searcher: SemanticSearcher,
    areas: list[str],
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Handle knowledge_assess tool call.

    Assesses coverage for specified knowledge areas.

    Args:
        searcher: SemanticSearcher instance.
        areas: Knowledge areas to assess.
        threshold: Similarity threshold for coverage.

    Returns:
        Dict with coverage report.
    """
    try:
        from knowledge_mcp.search.coverage import CoverageConfig

        config = CoverageConfig(similarity_threshold=threshold)
        assessor = CoverageAssessor(searcher, config)
        report = await assessor.assess(areas)

        return report.to_dict()

    except Exception as e:
        logger.exception("Assess error: %s", e)
        return {"error": str(e), "isError": True}


async def handle_preflight(
    url: str,
    check_robots: bool = True,  # noqa: ARG001
) -> dict[str, Any]:
    """Handle knowledge_preflight tool call.

    Checks if URL is accessible and respects robots.txt.

    Args:
        url: URL to check.
        check_robots: Whether to check robots.txt (currently not implemented).

    Returns:
        Dict with accessibility status.
    """
    try:
        # Note: check_url_accessible is sync, so we call it directly
        # It only does basic URL validation, not actual network checks
        accessible, error = check_url_accessible(url)

        return {
            "url": url,
            "accessible": accessible,
            "robots_checked": False,  # Basic validation only, no robots.txt check
            "error": error,
        }

    except Exception as e:
        logger.exception("Preflight error: %s", e)
        return {"error": str(e), "isError": True, "accessible": False}


async def handle_acquire(
    session: AsyncSession,
    url: str,
    authority_tier: str = "tier3",
    title: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Handle knowledge_acquire tool call.

    Acquires web content: preflight check, create source, ingest.

    Args:
        session: Database session.
        url: URL to acquire.
        authority_tier: Authority level.
        title: Optional title.
        reason: Why this content is needed.

    Returns:
        Dict with acquisition result.
    """
    try:
        # Preflight check first
        accessible, error = check_url_accessible(url)
        if not accessible:
            return {
                "url": url,
                "acquired": False,
                "error": f"Preflight failed: {error}",
                "isError": True,
            }

        # Ingest the content
        result = await handle_ingest(
            session=session,
            url=url,
            source_type="web",
            authority_tier=authority_tier,
            title=title,
        )

        # Check if ingest succeeded
        if result.get("isError"):
            return {
                "url": url,
                "acquired": False,
                "error": result.get("error"),
                "isError": True,
            }

        return {
            "url": url,
            "acquired": True,
            "source_id": result.get("source_id"),
            "title": result.get("title"),
            "word_count": result.get("word_count"),
            "reason": reason,
        }

    except Exception as e:
        logger.exception("Acquire error: %s", e)
        return {"error": str(e), "isError": True, "acquired": False}


async def handle_request(
    session: AsyncSession,
    url: str,
    reason: str | None = None,
    priority: int = 3,
) -> dict[str, Any]:
    """Handle knowledge_request tool call.

    Creates an acquisition request for later processing.

    Args:
        session: Database session.
        url: URL to request.
        reason: Why this content is needed.
        priority: Request priority (1=highest, 5=lowest).

    Returns:
        Dict with request details.
    """
    try:
        repo = AcquisitionRequestRepository(session)

        # Create request
        request = await repo.create(
            url=url,
            reason=reason or "",
            priority=priority,
        )

        return {
            "request_id": request.id,
            "url": request.url,
            "reason": request.reason,
            "priority": request.priority,
            "status": request.status.value,
            "created_at": request.created_at.isoformat() if request.created_at else None,
            "message": "Acquisition request created",
        }

    except Exception as e:
        logger.exception("Request error: %s", e)
        return {"error": str(e), "isError": True}
