"""Offline sync manager for Knowledge MCP.

Syncs PostgreSQL source metadata to ChromaDB for offline operation.
Enables graceful degradation when database is unavailable.

Strategy from research:
- Sync minimal metadata only (source_id, url, type, authority_tier)
- Store as ChromaDB metadata attached to source documents
- Accept reduced functionality offline (no complex queries)

Example:
    >>> sync_manager = OfflineSyncManager(config)
    >>> await sync_manager.sync_sources(session)
    >>> status = await sync_manager.get_status()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class SyncStatus(str, Enum):
    """Sync state between PostgreSQL and ChromaDB."""

    SYNCED = "synced"
    PENDING = "pending"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class SyncState:
    """Current sync state."""

    status: SyncStatus
    last_sync: datetime | None = None
    sources_synced: int = 0
    error_message: str | None = None
    is_online: bool = True


@dataclass
class OfflineSyncConfig:
    """Configuration for offline sync."""

    chromadb_path: Path = field(default_factory=lambda: Path("./collections/chromadb"))
    metadata_collection: str = "sources_metadata"
    sync_interval_seconds: int = 300  # 5 minutes
    batch_size: int = 100


class OfflineSyncManager:
    """Manages synchronization between PostgreSQL and ChromaDB.

    Provides:
    - Source metadata sync to ChromaDB
    - Online/offline state detection
    - Graceful degradation when database unavailable
    """

    def __init__(self, config: OfflineSyncConfig | None = None):
        """Initialize sync manager.

        Args:
            config: Sync configuration. Uses defaults if None.
        """
        self.config = config or OfflineSyncConfig()
        self._state = SyncState(status=SyncStatus.PENDING)
        self._chroma_client: Any | None = None

    def _get_chroma_client(self) -> Any:
        """Lazy-load ChromaDB client."""
        if self._chroma_client is None:
            import chromadb

            self._chroma_client = chromadb.PersistentClient(path=str(self.config.chromadb_path))
        return self._chroma_client

    def _get_metadata_collection(self) -> Any:
        """Get or create metadata collection."""
        client = self._get_chroma_client()
        return client.get_or_create_collection(
            name=self.config.metadata_collection, metadata={"purpose": "offline_source_metadata"}
        )

    async def check_database_connection(self, session_factory: Any) -> bool:
        """Check if PostgreSQL is accessible.

        Args:
            session_factory: Async session factory from db/engine.py

        Returns:
            True if database is accessible.
        """
        try:
            async with session_factory() as session:
                from sqlalchemy import text

                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.warning(f"Database connection check failed: {e}")
            return False

    async def sync_sources(self, session: AsyncSession) -> SyncState:
        """Sync source metadata from PostgreSQL to ChromaDB.

        Args:
            session: Active database session.

        Returns:
            Current sync state after operation.
        """
        from sqlalchemy import select

        from knowledge_mcp.db.models import Source

        try:
            # Query all sources
            stmt = select(Source).order_by(Source.id)
            result = await session.execute(stmt)
            sources = list(result.scalars().all())

            # Get ChromaDB collection
            collection = self._get_metadata_collection()

            # Sync in batches
            synced = 0
            for i in range(0, len(sources), self.config.batch_size):
                batch = sources[i : i + self.config.batch_size]

                # Prepare data for ChromaDB
                ids = [f"source_{s.id}" for s in batch]
                documents = [s.url for s in batch]  # URL as document
                metadatas = [
                    {
                        "source_id": s.id,
                        "url": s.url,
                        "title": s.title or "",
                        "source_type": s.source_type.value if s.source_type else "",
                        "status": s.status.value if s.status else "",
                        "authority_tier": s.authority_tier.value if s.authority_tier else "",
                        "synced_at": datetime.now(UTC).isoformat(),
                    }
                    for s in batch
                ]

                # Upsert to ChromaDB
                collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                )
                synced += len(batch)

            self._state = SyncState(
                status=SyncStatus.SYNCED,
                last_sync=datetime.now(UTC),
                sources_synced=synced,
                is_online=True,
            )
            logger.info(f"Synced {synced} sources to ChromaDB")
            return self._state

        except Exception as e:
            self._state = SyncState(
                status=SyncStatus.ERROR,
                error_message=str(e),
                is_online=False,
            )
            logger.error(f"Sync failed: {e}")
            return self._state

    def get_offline_sources(
        self,
        source_type: str | None = None,
        authority_tier: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query sources from ChromaDB offline store.

        Args:
            source_type: Filter by source type.
            authority_tier: Filter by authority tier.
            limit: Maximum results to return.

        Returns:
            List of source metadata dicts.
        """
        collection = self._get_metadata_collection()

        # Build where clause
        where = {}
        if source_type:
            where["source_type"] = source_type
        if authority_tier:
            where["authority_tier"] = authority_tier

        # Query ChromaDB
        results = collection.get(
            where=where if where else None,
            limit=limit,
            include=["metadatas", "documents"],
        )

        # Format results
        sources: list[dict[str, Any]] = []
        if results and results.get("metadatas"):
            metadatas = results["metadatas"]
            for metadata in metadatas:
                source_dict: dict[str, Any] = {
                    "id": metadata.get("source_id"),
                    "url": metadata.get("url"),
                    "title": metadata.get("title"),
                    "source_type": metadata.get("source_type"),
                    "status": metadata.get("status"),
                    "authority_tier": metadata.get("authority_tier"),
                }
                sources.append(source_dict)

        return sources

    def get_state(self) -> SyncState:
        """Get current sync state."""
        return self._state

    def is_offline_mode(self) -> bool:
        """Check if operating in offline mode."""
        return not self._state.is_online
