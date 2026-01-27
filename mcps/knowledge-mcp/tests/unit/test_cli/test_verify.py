# tests/unit/test_cli/test_verify.py
"""Unit tests for verify CLI command."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from knowledge_mcp.cli.main import app

runner = CliRunner()


class TestVerifyCommand:
    """Tests for knowledge verify command."""

    def test_verify_help(self) -> None:
        """Test help message displays."""
        result = runner.invoke(app, ["verify", "--help"])
        assert result.exit_code == 0
        assert "Validate collection health" in result.stdout

    @patch("knowledge_mcp.utils.config.load_config")
    @patch("knowledge_mcp.store.create_store")
    def test_verify_success(
        self,
        mock_create_store: MagicMock,
        mock_load_config: MagicMock,
    ) -> None:
        """Test successful verification."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.embedding_dimensions = 1536
        mock_config.versioned_collection_name = "test_collection_v1"
        mock_load_config.return_value = mock_config

        mock_store = MagicMock()
        mock_store.get_stats.return_value = {
            "collection_name": "test_collection_v1",
            "total_chunks": 100,
            "indexed_vectors": 100,
            "config": {
                "vector_size": 1536,
                "hybrid_enabled": True,
            },
        }
        mock_create_store.return_value = mock_store

        result = runner.invoke(app, ["verify"])

        assert result.exit_code == 0
        assert "100" in result.stdout  # total chunks
        assert "Verification complete" in result.stdout

    @patch("knowledge_mcp.utils.config.load_config")
    @patch("knowledge_mcp.store.create_store")
    def test_verify_embeddings_match(
        self,
        mock_create_store: MagicMock,
        mock_load_config: MagicMock,
    ) -> None:
        """Test embedding dimension verification passes."""
        mock_config = MagicMock()
        mock_config.embedding_dimensions = 1536
        mock_config.versioned_collection_name = "test_collection_v1"
        mock_load_config.return_value = mock_config

        mock_store = MagicMock()
        mock_store.get_stats.return_value = {
            "collection_name": "test_collection_v1",
            "total_chunks": 100,
            "indexed_vectors": 100,
            "config": {
                "vector_size": 1536,
                "hybrid_enabled": False,
            },
        }
        mock_create_store.return_value = mock_store

        result = runner.invoke(app, ["verify", "--embeddings"])

        assert result.exit_code == 0
        assert "OK" in result.stdout
        assert "Dimensions match" in result.stdout

    @patch("knowledge_mcp.utils.config.load_config")
    @patch("knowledge_mcp.store.create_store")
    def test_verify_embeddings_mismatch(
        self,
        mock_create_store: MagicMock,
        mock_load_config: MagicMock,
    ) -> None:
        """Test embedding dimension mismatch fails."""
        mock_config = MagicMock()
        mock_config.embedding_dimensions = 1536  # Expected
        mock_config.versioned_collection_name = "test_collection_v1"
        mock_load_config.return_value = mock_config

        mock_store = MagicMock()
        mock_store.get_stats.return_value = {
            "collection_name": "test_collection_v1",
            "total_chunks": 100,
            "indexed_vectors": 100,
            "config": {
                "vector_size": 384,  # Actual - mismatch!
                "hybrid_enabled": False,
            },
        }
        mock_create_store.return_value = mock_store

        result = runner.invoke(app, ["verify", "--embeddings"])

        assert result.exit_code == 1
        assert "MISMATCH" in result.stdout
        assert "1536" in result.stdout  # expected
        assert "384" in result.stdout  # actual

    @patch("knowledge_mcp.utils.config.load_config")
    @patch("knowledge_mcp.store.create_store")
    def test_verify_connection_error(
        self,
        mock_create_store: MagicMock,
        mock_load_config: MagicMock,
    ) -> None:
        """Test connection error handling."""
        mock_config = MagicMock()
        mock_config.versioned_collection_name = "test_collection_v1"
        mock_load_config.return_value = mock_config
        mock_create_store.side_effect = Exception("Connection refused")

        result = runner.invoke(app, ["verify"])

        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "Connection refused" in result.stdout

    @patch("knowledge_mcp.utils.config.load_config")
    @patch("knowledge_mcp.store.create_store")
    def test_verify_custom_collection(
        self,
        mock_create_store: MagicMock,
        mock_load_config: MagicMock,
    ) -> None:
        """Test verification with custom collection name."""
        mock_config = MagicMock()
        mock_config.embedding_dimensions = 1536
        mock_config.versioned_collection_name = "default_collection"
        mock_load_config.return_value = mock_config

        mock_store = MagicMock()
        mock_store.get_stats.return_value = {
            "collection_name": "my_custom_collection",
            "total_chunks": 50,
            "indexed_vectors": 50,
            "config": {
                "vector_size": 1536,
                "hybrid_enabled": False,
            },
        }
        mock_create_store.return_value = mock_store

        result = runner.invoke(app, ["verify", "-c", "my_custom_collection"])

        assert result.exit_code == 0
        assert "my_custom_collection" in result.stdout
        assert "Verification complete" in result.stdout

    @patch("knowledge_mcp.utils.config.load_config")
    @patch("knowledge_mcp.store.create_store")
    def test_verify_short_flags(
        self,
        mock_create_store: MagicMock,
        mock_load_config: MagicMock,
    ) -> None:
        """Test short flags -c and -e work correctly."""
        mock_config = MagicMock()
        mock_config.embedding_dimensions = 1536
        mock_config.versioned_collection_name = "default_collection"
        mock_load_config.return_value = mock_config

        mock_store = MagicMock()
        mock_store.get_stats.return_value = {
            "collection_name": "test_collection",
            "total_chunks": 25,
            "indexed_vectors": 25,
            "config": {
                "vector_size": 1536,
                "hybrid_enabled": True,
            },
        }
        mock_create_store.return_value = mock_store

        result = runner.invoke(app, ["verify", "-c", "test_collection", "-e"])

        assert result.exit_code == 0
        assert "OK" in result.stdout
        assert "Dimensions match" in result.stdout
