# tests/unit/test_cli/test_validate.py
"""Unit tests for validate CLI commands."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from knowledge_mcp.cli.main import app
from knowledge_mcp.cli.validate import (
    _display_results,
    display_validation_summary,
)
from knowledge_mcp.validation.table_validator import ValidationResult

runner = CliRunner()


class TestValidateCommand:
    """Tests for knowledge validate collection command."""

    def test_validate_help(self) -> None:
        """Test help message displays."""
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validation commands" in result.stdout

    def test_validate_collection_help(self) -> None:
        """Test validate collection help message."""
        result = runner.invoke(app, ["validate", "collection", "--help"])
        assert result.exit_code == 0
        assert "Validate critical RCCA tables" in result.stdout
        assert "--verbose" in result.stdout

    @patch("knowledge_mcp.validation.TableValidator")
    @patch("knowledge_mcp.cli.validate._create_searcher_adapter")
    @patch("knowledge_mcp.utils.config.load_config")
    def test_validate_collection_all_pass(
        self,
        mock_load_config: MagicMock,
        mock_create_adapter: MagicMock,
        mock_validator_cls: MagicMock,
    ) -> None:
        """Test validation with all tests passing."""
        # Setup mocks
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config

        mock_searcher = MagicMock()
        mock_create_adapter.return_value = mock_searcher

        # Create passing validation results
        passing_results = [
            ValidationResult(
                table_name="AIAG-VDA Action Priority Matrix",
                passed=True,
                chunks_retrieved=5,
            ),
            ValidationResult(
                table_name="MIL-STD-882E Severity Categories",
                passed=True,
                chunks_retrieved=3,
            ),
            ValidationResult(
                table_name="ISO 9001:2015 CAPA Templates",
                passed=True,
                chunks_retrieved=4,
            ),
        ]

        mock_validator = MagicMock()
        mock_validator.validate_all = AsyncMock(return_value=passing_results)
        mock_validator_cls.return_value = mock_validator

        result = runner.invoke(app, ["validate", "collection", "test_collection"])

        assert result.exit_code == 0
        assert "PASSED" in result.stdout
        assert "3/3" in result.stdout

    @patch("knowledge_mcp.validation.TableValidator")
    @patch("knowledge_mcp.cli.validate._create_searcher_adapter")
    @patch("knowledge_mcp.utils.config.load_config")
    def test_validate_collection_with_failures(
        self,
        mock_load_config: MagicMock,
        mock_create_adapter: MagicMock,
        mock_validator_cls: MagicMock,
    ) -> None:
        """Test validation with some tests failing."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_create_adapter.return_value = MagicMock()

        # Create mixed results
        mixed_results = [
            ValidationResult(
                table_name="AIAG-VDA Action Priority Matrix",
                passed=True,
                chunks_retrieved=5,
            ),
            ValidationResult(
                table_name="MIL-STD-882E Severity Categories",
                passed=False,
                chunks_retrieved=0,
                recommendation="Ingest MIL-STD-882E",
            ),
            ValidationResult(
                table_name="ISO 9001:2015 CAPA Templates",
                passed=False,
                chunks_retrieved=1,
                recommendation="Ingest ISO 9001:2015 Clause 10.2",
            ),
        ]

        mock_validator = MagicMock()
        mock_validator.validate_all = AsyncMock(return_value=mixed_results)
        mock_validator_cls.return_value = mock_validator

        result = runner.invoke(app, ["validate", "collection", "test_collection"])

        assert result.exit_code == 1
        assert "FAILED" in result.stdout
        assert "2/3" in result.stdout
        assert "Recommendations" in result.stdout

    @patch("knowledge_mcp.validation.TableValidator")
    @patch("knowledge_mcp.cli.validate._create_searcher_adapter")
    @patch("knowledge_mcp.utils.config.load_config")
    def test_validate_collection_verbose(
        self,
        mock_load_config: MagicMock,
        mock_create_adapter: MagicMock,
        mock_validator_cls: MagicMock,
    ) -> None:
        """Test verbose output shows detailed checks."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_create_adapter.return_value = MagicMock()

        # Create result with details
        results = [
            ValidationResult(
                table_name="AIAG-VDA Action Priority Matrix",
                passed=True,
                chunks_retrieved=5,
                details={
                    "table_found": True,
                    "severity_scale": True,
                    "occurrence_scale": True,
                    "ap_values": True,
                },
            ),
        ]

        mock_validator = MagicMock()
        mock_validator.validate_all = AsyncMock(return_value=results)
        mock_validator_cls.return_value = mock_validator

        result = runner.invoke(
            app, ["validate", "collection", "test_collection", "--verbose"]
        )

        assert result.exit_code == 0
        assert "Detailed Results" in result.stdout
        assert "table_found" in result.stdout
        assert "severity_scale" in result.stdout

    @patch("knowledge_mcp.cli.validate._create_searcher_adapter")
    @patch("knowledge_mcp.utils.config.load_config")
    def test_validate_collection_connection_error(
        self,
        mock_load_config: MagicMock,
        mock_create_adapter: MagicMock,
    ) -> None:
        """Test error handling for connection failures."""
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        mock_create_adapter.side_effect = ConnectionError("Cannot connect to Qdrant")

        result = runner.invoke(app, ["validate", "collection", "test_collection"])

        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "Cannot connect" in result.stdout


class TestDisplayResults:
    """Tests for result display formatting."""

    def test_display_results_pass_fail_icons(self, capsys: pytest.CaptureFixture) -> None:
        """Test that pass/fail results show correct status."""
        results = [
            ValidationResult(
                table_name="Table A",
                passed=True,
                chunks_retrieved=5,
            ),
            ValidationResult(
                table_name="Table B",
                passed=False,
                chunks_retrieved=0,
            ),
        ]

        _display_results(results, verbose=False)

        captured = capsys.readouterr()
        # Rich console output contains ANSI codes, check for table content
        assert "Table A" in captured.out
        assert "Table B" in captured.out

    def test_display_results_verbose_shows_details(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test verbose mode shows check details."""
        results = [
            ValidationResult(
                table_name="Table A",
                passed=True,
                chunks_retrieved=5,
                details={
                    "check_one": True,
                    "check_two": False,
                },
            ),
        ]

        _display_results(results, verbose=True)

        captured = capsys.readouterr()
        assert "check_one" in captured.out
        assert "check_two" in captured.out


class TestDisplayValidationSummary:
    """Tests for condensed validation summary display."""

    def test_summary_all_passed(self, capsys: pytest.CaptureFixture) -> None:
        """Test summary when all validations pass."""
        results = [
            ValidationResult(table_name="Table A", passed=True, chunks_retrieved=5),
            ValidationResult(table_name="Table B", passed=True, chunks_retrieved=3),
        ]

        display_validation_summary(results, "test_collection")

        captured = capsys.readouterr()
        assert "All 2 validations passed" in captured.out

    def test_summary_with_failures(self, capsys: pytest.CaptureFixture) -> None:
        """Test summary shows failed validations with recommendations."""
        results = [
            ValidationResult(table_name="Table A", passed=True, chunks_retrieved=5),
            ValidationResult(
                table_name="Table B",
                passed=False,
                chunks_retrieved=0,
                recommendation="Ingest missing standard",
            ),
        ]

        display_validation_summary(results, "test_collection")

        captured = capsys.readouterr()
        assert "1 of 2 validations failed" in captured.out
        assert "Ingest missing standard" in captured.out


class TestMainAppIncludesValidate:
    """Tests for validate command registration in main app."""

    def test_main_help_shows_validate(self) -> None:
        """Test main app help includes validate command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "validate" in result.stdout

    def test_validate_requires_collection_argument(self) -> None:
        """Test validate collection requires collection name."""
        result = runner.invoke(app, ["validate", "collection"])
        # Typer shows missing argument error
        assert result.exit_code != 0
        assert "Missing argument" in result.output


class TestIngestValidateFlag:
    """Tests for --validate flag on ingest command."""

    def test_ingest_docs_help_shows_validate_flag(self) -> None:
        """Test ingest docs help shows --validate option."""
        result = runner.invoke(app, ["ingest", "docs", "--help"])
        assert result.exit_code == 0
        assert "--validate" in result.stdout
        assert "RCCA table validation" in result.stdout


class TestCollectionNameValidation:
    """Tests for collection name validation."""

    def test_valid_collection_names(self) -> None:
        """Test valid collection names are accepted."""
        from knowledge_mcp.cli.validate import _validate_collection_name

        # Valid names
        assert _validate_collection_name("rcca_standards") == "rcca_standards"
        assert _validate_collection_name("test-collection") == "test-collection"
        assert _validate_collection_name("MyCollection123") == "MyCollection123"
        assert _validate_collection_name("a") == "a"

    def test_invalid_collection_starts_with_number(self) -> None:
        """Test collection name starting with number is rejected."""
        import typer

        from knowledge_mcp.cli.validate import _validate_collection_name

        with pytest.raises(typer.BadParameter) as exc_info:
            _validate_collection_name("123collection")
        assert "must start with a letter" in str(exc_info.value)

    def test_invalid_collection_special_chars(self) -> None:
        """Test collection name with special chars is rejected."""
        import typer

        from knowledge_mcp.cli.validate import _validate_collection_name

        with pytest.raises(typer.BadParameter) as exc_info:
            _validate_collection_name("my.collection")
        assert "letters, numbers, underscores, and hyphens" in str(exc_info.value)

    def test_invalid_collection_too_long(self) -> None:
        """Test collection name over 100 chars is rejected."""
        import typer

        from knowledge_mcp.cli.validate import _validate_collection_name

        long_name = "a" * 101
        with pytest.raises(typer.BadParameter) as exc_info:
            _validate_collection_name(long_name)
        assert "100 characters or less" in str(exc_info.value)


class TestSearcherAdapter:
    """Tests for _SearcherAdapter class."""

    @patch("knowledge_mcp.store.create_store")
    @patch("knowledge_mcp.embed.OpenAIEmbedder")
    def test_adapter_stores_collection(
        self,
        mock_embedder_cls: MagicMock,
        mock_create_store: MagicMock,
    ) -> None:
        """Test adapter stores collection name."""
        from knowledge_mcp.cli.validate import _SearcherAdapter

        mock_config = MagicMock()
        mock_config.openai_api_key = "test-key"

        adapter = _SearcherAdapter(mock_config, "my_collection")

        assert adapter._collection == "my_collection"

    @patch("knowledge_mcp.store.create_store")
    @patch("knowledge_mcp.embed.OpenAIEmbedder")
    @pytest.mark.asyncio
    async def test_adapter_search_returns_chunks(
        self,
        mock_embedder_cls: MagicMock,
        mock_create_store: MagicMock,
    ) -> None:
        """Test adapter search converts store results to KnowledgeChunks."""
        from knowledge_mcp.cli.validate import _SearcherAdapter

        # Setup mocks
        mock_embedder = MagicMock()
        mock_embedder.embed = AsyncMock(return_value=[0.1] * 1536)
        mock_embedder_cls.return_value = mock_embedder

        mock_store = MagicMock()
        mock_store.search.return_value = [
            {
                "id": "chunk-1",
                "content": "Test content",
                "metadata": {
                    "document_id": "doc-1",
                    "document_title": "Test Doc",
                    "document_type": "standard",
                },
            }
        ]
        mock_create_store.return_value = mock_store

        mock_config = MagicMock()
        mock_config.openai_api_key = "test-key"

        adapter = _SearcherAdapter(mock_config, "test_collection")
        results = await adapter.search("test query", "test_collection", n_results=5)

        assert len(results) == 1
        assert results[0].id == "chunk-1"
        assert results[0].content == "Test content"
        assert results[0].document_id == "doc-1"

    @patch("knowledge_mcp.store.create_store")
    @patch("knowledge_mcp.embed.OpenAIEmbedder")
    @pytest.mark.asyncio
    async def test_adapter_warns_on_collection_mismatch(
        self,
        mock_embedder_cls: MagicMock,
        mock_create_store: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test adapter logs warning when search collection differs."""
        import logging

        from knowledge_mcp.cli.validate import _SearcherAdapter

        mock_embedder = MagicMock()
        mock_embedder.embed = AsyncMock(return_value=[0.1] * 1536)
        mock_embedder_cls.return_value = mock_embedder

        mock_store = MagicMock()
        mock_store.search.return_value = []
        mock_create_store.return_value = mock_store

        mock_config = MagicMock()
        mock_config.openai_api_key = "test-key"

        adapter = _SearcherAdapter(mock_config, "collection_a")

        with caplog.at_level(logging.WARNING):
            await adapter.search("test", "collection_b", n_results=5)

        assert "collection_b" in caplog.text
        assert "collection_a" in caplog.text
