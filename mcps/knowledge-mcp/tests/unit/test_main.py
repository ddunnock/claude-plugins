# tests/unit/test_main.py
"""
Unit tests for CLI entry point.

Tests the cli() function in __main__.py, including success,
keyboard interrupt, and exception handling paths.
"""

from __future__ import annotations

import sys
from io import StringIO
from unittest.mock import patch


class TestCli:
    """Tests for CLI entry point function."""

    def test_cli_returns_zero_on_success(self) -> None:
        """Verify success exit code."""
        with patch("asyncio.run") as mock_run:
            with patch("knowledge_mcp.server.main") as mock_server_main:
                mock_run.return_value = None
                from knowledge_mcp.__main__ import cli

                result = cli()
                assert result == 0

    def test_cli_returns_130_on_keyboard_interrupt(self) -> None:
        """Verify Ctrl+C handling returns 130."""
        with patch("asyncio.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()
            from knowledge_mcp.__main__ import cli

            result = cli()
            assert result == 130

    def test_cli_returns_1_on_exception(self) -> None:
        """Verify error exit code on exception."""
        with patch("asyncio.run") as mock_run:
            mock_run.side_effect = RuntimeError("Test error")
            from knowledge_mcp.__main__ import cli

            result = cli()
            assert result == 1

    def test_cli_writes_to_stderr_on_interrupt(self) -> None:
        """Verify message written to stderr on Ctrl+C."""
        with patch("asyncio.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()
            stderr_capture = StringIO()
            with patch.object(sys, "stderr", stderr_capture):
                from knowledge_mcp.__main__ import cli

                cli()
            output = stderr_capture.getvalue()
            assert "Interrupted" in output

    def test_cli_writes_to_stderr_on_error(self) -> None:
        """Verify error message written to stderr."""
        with patch("asyncio.run") as mock_run:
            mock_run.side_effect = RuntimeError("Test error message")
            stderr_capture = StringIO()
            with patch.object(sys, "stderr", stderr_capture):
                from knowledge_mcp.__main__ import cli

                cli()
            output = stderr_capture.getvalue()
            assert "Error:" in output
            assert "Test error message" in output

    def test_cli_calls_asyncio_run(self) -> None:
        """Verify asyncio.run is called."""
        with patch("asyncio.run") as mock_run:
            mock_run.return_value = None
            from knowledge_mcp.__main__ import cli

            cli()
            mock_run.assert_called_once()
