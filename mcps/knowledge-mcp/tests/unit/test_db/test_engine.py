"""Unit tests for database engine module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCreateEngineAndSessionFactory:
    """Tests for engine creation."""

    def test_creates_engine_with_config(self) -> None:
        """Test engine is created with correct settings."""
        from knowledge_mcp.utils.config import KnowledgeConfig

        config = KnowledgeConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/test",
            database_pool_size=20,
            database_max_overflow=10,
            database_echo=True,
        )

        with patch("knowledge_mcp.db.engine.create_async_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine

            from knowledge_mcp.db.engine import create_engine_and_session_factory

            engine, factory = create_engine_and_session_factory(config)

            # Verify create_async_engine was called once
            mock_create.assert_called_once()

            # Check the call arguments
            call_args = mock_create.call_args
            assert call_args[0][0] == "postgresql+asyncpg://user:pass@localhost/test"

            call_kwargs = call_args[1]
            assert call_kwargs["pool_size"] == 20
            assert call_kwargs["max_overflow"] == 10
            assert call_kwargs["pool_pre_ping"] is True
            assert call_kwargs["echo"] is True
            assert call_kwargs["pool_recycle"] == 3600

    def test_creates_engine_with_defaults(self) -> None:
        """Test engine creation with default config values."""
        from knowledge_mcp.utils.config import KnowledgeConfig

        config = KnowledgeConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/test",
        )

        with patch("knowledge_mcp.db.engine.create_async_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine

            from knowledge_mcp.db.engine import create_engine_and_session_factory

            engine, factory = create_engine_and_session_factory(config)

            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["pool_size"] == 15  # Default
            assert call_kwargs["max_overflow"] == 10  # Default
            assert call_kwargs["echo"] is False  # Default

    def test_raises_on_missing_database_url(self) -> None:
        """Test that missing database_url raises ValueError."""
        from knowledge_mcp.utils.config import KnowledgeConfig

        config = KnowledgeConfig(database_url="")

        from knowledge_mcp.db.engine import create_engine_and_session_factory

        with pytest.raises(ValueError, match="database_url is required"):
            create_engine_and_session_factory(config)

    def test_session_factory_configured_correctly(self) -> None:
        """Test session factory configuration."""
        from knowledge_mcp.utils.config import KnowledgeConfig

        config = KnowledgeConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/test",
        )

        with patch("knowledge_mcp.db.engine.create_async_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine

            with patch("knowledge_mcp.db.engine.async_sessionmaker") as mock_sessionmaker:
                mock_factory = MagicMock()
                mock_sessionmaker.return_value = mock_factory

                from knowledge_mcp.db.engine import create_engine_and_session_factory

                engine, factory = create_engine_and_session_factory(config)

                # Verify async_sessionmaker was called with correct args
                mock_sessionmaker.assert_called_once()
                call_args = mock_sessionmaker.call_args

                # Check that expire_on_commit is False (critical for async)
                assert call_args[1]["expire_on_commit"] is False


class TestGetSession:
    """Tests for session context manager."""

    @pytest.mark.asyncio
    async def test_commits_on_success(self) -> None:
        """Test session commits on successful exit."""
        mock_session = AsyncMock()
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        from knowledge_mcp.db.engine import get_session

        async with get_session(mock_factory) as session:
            assert session is mock_session

        # Verify commit was called
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self) -> None:
        """Test session rolls back on exception."""
        mock_session = AsyncMock()
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        from knowledge_mcp.db.engine import get_session

        with pytest.raises(ValueError, match="Test error"):
            async with get_session(mock_factory) as session:
                raise ValueError("Test error")

        # Verify rollback was called
        mock_session.rollback.assert_awaited_once()

        # Verify commit was NOT called
        mock_session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_session_can_be_used(self) -> None:
        """Test that session can execute operations."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        from knowledge_mcp.db.engine import get_session

        async with get_session(mock_factory) as session:
            await session.execute("SELECT 1")

        # Verify operation was called
        mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_multiple_operations_before_commit(self) -> None:
        """Test multiple operations can be performed before commit."""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        from knowledge_mcp.db.engine import get_session

        async with get_session(mock_factory) as session:
            session.add("object1")
            await session.flush()
            session.add("object2")
            await session.flush()

        # Verify all operations were called
        assert mock_session.add.call_count == 2
        assert mock_session.flush.await_count == 2
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exception_during_operation(self) -> None:
        """Test exception during operation triggers rollback."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=RuntimeError("Database error"))
        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        from knowledge_mcp.db.engine import get_session

        with pytest.raises(RuntimeError, match="Database error"):
            async with get_session(mock_factory) as session:
                await session.execute("SELECT 1")

        # Verify rollback was called
        mock_session.rollback.assert_awaited_once()
        mock_session.commit.assert_not_awaited()
