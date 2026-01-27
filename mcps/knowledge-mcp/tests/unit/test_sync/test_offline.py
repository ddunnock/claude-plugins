"""Unit tests for OfflineSyncManager."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from knowledge_mcp.sync.offline import (
    OfflineSyncConfig,
    OfflineSyncManager,
    SyncState,
    SyncStatus,
)


class TestSyncStatus:
    """Tests for SyncStatus enum."""

    def test_enum_values(self) -> None:
        """Test all status values exist."""
        assert SyncStatus.SYNCED == "synced"
        assert SyncStatus.PENDING == "pending"
        assert SyncStatus.OFFLINE == "offline"
        assert SyncStatus.ERROR == "error"


class TestSyncState:
    """Tests for SyncState dataclass."""

    def test_default_values(self) -> None:
        """Test default state values."""
        state = SyncState(status=SyncStatus.PENDING)
        assert state.status == SyncStatus.PENDING
        assert state.last_sync is None
        assert state.sources_synced == 0
        assert state.is_online is True

    def test_custom_values(self) -> None:
        """Test state with custom values."""
        now = datetime.now(UTC)
        state = SyncState(
            status=SyncStatus.SYNCED,
            last_sync=now,
            sources_synced=42,
            is_online=True,
        )
        assert state.sources_synced == 42
        assert state.last_sync == now


class TestOfflineSyncConfig:
    """Tests for OfflineSyncConfig."""

    def test_default_values(self) -> None:
        """Test default configuration."""
        config = OfflineSyncConfig()
        assert config.metadata_collection == "sources_metadata"
        assert config.sync_interval_seconds == 300
        assert config.batch_size == 100

    def test_custom_values(self) -> None:
        """Test custom configuration."""
        config = OfflineSyncConfig(
            chromadb_path=Path("/tmp/test"),
            batch_size=50,
        )
        assert config.chromadb_path == Path("/tmp/test")
        assert config.batch_size == 50


class TestOfflineSyncManager:
    """Tests for OfflineSyncManager class."""

    @pytest.fixture
    def temp_chromadb_path(self):
        """Create temporary directory for ChromaDB."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_chromadb_path: Path) -> OfflineSyncManager:
        """Create manager with temp storage."""
        config = OfflineSyncConfig(chromadb_path=temp_chromadb_path)
        return OfflineSyncManager(config)

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        manager = OfflineSyncManager()
        assert manager.config is not None
        assert manager.get_state().status == SyncStatus.PENDING

    def test_init_custom_config(self, temp_chromadb_path: Path) -> None:
        """Test initialization with custom config."""
        config = OfflineSyncConfig(chromadb_path=temp_chromadb_path)
        manager = OfflineSyncManager(config)
        assert manager.config.chromadb_path == temp_chromadb_path

    def test_get_state(self, manager: OfflineSyncManager) -> None:
        """Test get_state returns current state."""
        state = manager.get_state()
        assert isinstance(state, SyncState)
        assert state.status == SyncStatus.PENDING

    def test_is_offline_mode_initially(self, manager: OfflineSyncManager) -> None:
        """Test is_offline_mode returns False initially."""
        # Initial state has is_online=True
        assert manager.is_offline_mode() is False

    @pytest.mark.asyncio
    async def test_check_database_connection_success(
        self, manager: OfflineSyncManager
    ) -> None:
        """Test database connection check succeeds."""
        # Mock session factory
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=MagicMock())

        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await manager.check_database_connection(mock_factory)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_database_connection_failure(
        self, manager: OfflineSyncManager
    ) -> None:
        """Test database connection check fails gracefully."""
        # Mock session factory that raises
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(
            side_effect=Exception("Connection refused")
        )

        result = await manager.check_database_connection(mock_factory)
        assert result is False

    def test_get_offline_sources_empty(self, manager: OfflineSyncManager) -> None:
        """Test get_offline_sources with empty collection."""
        # Initialize collection
        manager._get_metadata_collection()

        sources = manager.get_offline_sources()
        assert sources == []

    def test_get_offline_sources_with_data(self, manager: OfflineSyncManager) -> None:
        """Test get_offline_sources returns synced data."""
        # Manually add data to collection
        collection = manager._get_metadata_collection()
        collection.upsert(
            ids=["source_1"],
            documents=["https://example.com"],
            metadatas=[
                {
                    "source_id": 1,
                    "url": "https://example.com",
                    "title": "Test",
                    "source_type": "web",
                    "status": "complete",
                    "authority_tier": "tier2",
                }
            ],
        )

        sources = manager.get_offline_sources()
        assert len(sources) == 1
        assert sources[0]["url"] == "https://example.com"
        assert sources[0]["source_type"] == "web"

    def test_get_offline_sources_with_filter(
        self, manager: OfflineSyncManager
    ) -> None:
        """Test get_offline_sources with type filter."""
        collection = manager._get_metadata_collection()
        collection.upsert(
            ids=["source_1", "source_2"],
            documents=["https://web.com", "file://doc.pdf"],
            metadatas=[
                {
                    "source_id": 1,
                    "url": "https://web.com",
                    "source_type": "web",
                    "authority_tier": "tier2",
                    "title": "",
                    "status": "",
                },
                {
                    "source_id": 2,
                    "url": "file://doc.pdf",
                    "source_type": "document",
                    "authority_tier": "tier1",
                    "title": "",
                    "status": "",
                },
            ],
        )

        web_sources = manager.get_offline_sources(source_type="web")
        assert len(web_sources) == 1
        assert web_sources[0]["source_type"] == "web"
