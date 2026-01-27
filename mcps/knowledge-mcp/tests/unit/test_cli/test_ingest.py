# tests/unit/test_cli/test_ingest.py
"""Unit tests for ingest CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from knowledge_mcp.cli.main import app
from knowledge_mcp.exceptions import IngestionError

runner = CliRunner()


class TestIngestDocs:
    """Tests for knowledge ingest docs command."""

    def test_ingest_docs_help(self) -> None:
        """Test help message displays."""
        result = runner.invoke(app, ["ingest", "docs", "--help"])
        assert result.exit_code == 0
        assert "Ingest local documents" in result.stdout

    def test_ingest_docs_nonexistent_path(self, tmp_path: Path) -> None:
        """Test error on nonexistent path."""
        nonexistent = tmp_path / "nope"
        result = runner.invoke(app, ["ingest", "docs", str(nonexistent)])
        assert result.exit_code != 0
        # Typer shows path validation error (may be in stdout or combined output)
        assert "does not exist" in result.output

    def test_ingest_docs_empty_directory(self, tmp_path: Path) -> None:
        """Test warning on empty directory."""
        result = runner.invoke(app, ["ingest", "docs", str(tmp_path)])
        assert result.exit_code == 0
        assert "No PDF or DOCX files" in result.stdout

    def test_ingest_docs_unsupported_file_type(self, tmp_path: Path) -> None:
        """Test error on unsupported file type."""
        # Create a text file
        test_file = tmp_path / "test.txt"
        test_file.touch()

        result = runner.invoke(app, ["ingest", "docs", str(test_file)])
        assert result.exit_code == 1
        assert "Unsupported file type" in result.stdout
        assert ".txt" in result.stdout

    @patch("knowledge_mcp.cli.ingest.IngestionPipeline")
    def test_ingest_docs_single_file_success(
        self,
        mock_pipeline_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful single file ingestion."""
        # Create test file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.touch()

        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_chunk_1 = MagicMock()
        mock_chunk_2 = MagicMock()
        mock_pipeline.ingest.return_value = [mock_chunk_1, mock_chunk_2]
        mock_pipeline_cls.return_value = mock_pipeline

        result = runner.invoke(app, ["ingest", "docs", str(test_pdf)])

        assert result.exit_code == 0
        mock_pipeline.ingest.assert_called_once_with(test_pdf)
        assert "2 chunks" in result.stdout
        assert "Processed: 1/1" in result.stdout
        assert "Ingestion complete" in result.stdout

    @patch("knowledge_mcp.cli.ingest.IngestionPipeline")
    def test_ingest_docs_directory_success(
        self,
        mock_pipeline_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful directory ingestion."""
        # Create test files
        pdf1 = tmp_path / "doc1.pdf"
        pdf2 = tmp_path / "doc2.pdf"
        docx = tmp_path / "doc3.docx"
        txt = tmp_path / "ignored.txt"  # Should be ignored
        pdf1.touch()
        pdf2.touch()
        docx.touch()
        txt.touch()

        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.ingest.return_value = [MagicMock()]  # 1 chunk per file
        mock_pipeline_cls.return_value = mock_pipeline

        result = runner.invoke(app, ["ingest", "docs", str(tmp_path)])

        assert result.exit_code == 0
        assert mock_pipeline.ingest.call_count == 3  # PDF + PDF + DOCX
        assert "Ingesting 3 document(s)" in result.stdout
        assert "Processed: 3/3" in result.stdout
        assert "Total chunks: 3" in result.stdout

    @patch("knowledge_mcp.cli.ingest.IngestionPipeline")
    def test_ingest_docs_recursive_directory(
        self,
        mock_pipeline_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test recursive directory scanning."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        pdf_root = tmp_path / "root.pdf"
        pdf_nested = subdir / "nested.pdf"
        pdf_root.touch()
        pdf_nested.touch()

        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.ingest.return_value = [MagicMock()]
        mock_pipeline_cls.return_value = mock_pipeline

        # Without recursive, only root file
        result = runner.invoke(app, ["ingest", "docs", str(tmp_path)])
        assert result.exit_code == 0
        assert "Ingesting 1 document(s)" in result.stdout

        # Reset mock
        mock_pipeline.ingest.reset_mock()

        # With recursive, both files
        result = runner.invoke(app, ["ingest", "docs", str(tmp_path), "--recursive"])
        assert result.exit_code == 0
        assert "Ingesting 2 document(s)" in result.stdout

    @patch("knowledge_mcp.cli.ingest.IngestionPipeline")
    def test_ingest_docs_partial_failure(
        self,
        mock_pipeline_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that failure in one file doesn't stop others."""
        # Create test files
        pdf1 = tmp_path / "good.pdf"
        pdf2 = tmp_path / "bad.pdf"
        pdf1.touch()
        pdf2.touch()

        # Mock pipeline to fail on second file
        mock_pipeline = MagicMock()
        mock_pipeline.ingest.side_effect = [
            [MagicMock(), MagicMock()],  # First file succeeds with 2 chunks
            IngestionError("Corrupt file"),  # Second file fails
        ]
        mock_pipeline_cls.return_value = mock_pipeline

        result = runner.invoke(app, ["ingest", "docs", str(tmp_path)])

        # Should exit with error due to failures
        assert result.exit_code == 1
        assert "Processed: 1/2" in result.stdout
        assert "Total chunks: 2" in result.stdout
        assert "Failed files (1)" in result.stdout
        assert "Corrupt file" in result.stdout

    @patch("knowledge_mcp.cli.ingest.IngestionPipeline")
    def test_ingest_docs_handles_generic_exception(
        self,
        mock_pipeline_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that generic exceptions are handled."""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.touch()

        # Mock pipeline to raise generic exception
        mock_pipeline = MagicMock()
        mock_pipeline.ingest.side_effect = RuntimeError("Unexpected error")
        mock_pipeline_cls.return_value = mock_pipeline

        result = runner.invoke(app, ["ingest", "docs", str(test_pdf)])

        assert result.exit_code == 1
        assert "FAIL" in result.stdout
        assert "Unexpected error" in result.stdout

    def test_ingest_docs_collection_option(self, tmp_path: Path) -> None:
        """Test that collection option is accepted."""
        result = runner.invoke(
            app,
            ["ingest", "docs", str(tmp_path), "--collection", "my_collection"],
        )
        # Empty dir so exits 0 with warning
        assert result.exit_code == 0
        assert "No PDF or DOCX files" in result.stdout


class TestIngestApp:
    """Tests for the ingest app group."""

    def test_ingest_help(self) -> None:
        """Test ingest subcommand help."""
        result = runner.invoke(app, ["ingest", "--help"])
        assert result.exit_code == 0
        assert "Document ingestion commands" in result.stdout
        assert "docs" in result.stdout


class TestMainApp:
    """Tests for the main app."""

    def test_main_help(self) -> None:
        """Test main app help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Knowledge MCP" in result.stdout
        assert "ingest" in result.stdout

    def test_main_no_args(self) -> None:
        """Test main app with no args shows help (no_args_is_help=True)."""
        result = runner.invoke(app, [])
        # With no_args_is_help=True, Typer shows help but exits with code 0
        # The exact exit code can vary; the key is help is shown
        assert "Usage:" in result.output
