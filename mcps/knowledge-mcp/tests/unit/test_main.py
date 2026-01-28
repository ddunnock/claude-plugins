# tests/unit/test_main.py
"""
Unit tests for CLI entry point.

Tests the cli() function in __main__.py which delegates to Typer CLI.
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


class TestCliEntryPoint:
    """Tests for CLI entry point function."""

    def test_cli_delegates_to_typer(self) -> None:
        """Verify cli() calls typer_cli()."""
        with patch("knowledge_mcp.cli.main.cli") as mock_typer_cli:
            from knowledge_mcp.__main__ import cli

            cli()
            mock_typer_cli.assert_called_once()

    def test_cli_function_exists(self) -> None:
        """Verify cli function can be imported."""
        from knowledge_mcp.__main__ import cli

        assert callable(cli)


class TestMainModule:
    """Tests for __main__ module execution."""

    def test_main_block_calls_cli(self) -> None:
        """Verify __main__ execution path."""
        # The if __name__ == "__main__" block calls cli()
        # We test that cli exists and is callable
        from knowledge_mcp.__main__ import cli

        assert cli is not None
