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
