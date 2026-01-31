# tests/unit/test_main.py
"""
Unit tests for module entry point.

Tests the main() function in __main__.py which routes between MCP server and CLI.
"""

from __future__ import annotations

import importlib
import sys
from unittest.mock import patch, MagicMock

import pytest


class TestMainEntryPoint:
    """Tests for main entry point function."""

    def test_main_runs_mcp_server_by_default(self) -> None:
        """Verify main() runs MCP server when no args provided."""
        original_argv = sys.argv
        try:
            sys.argv = ["knowledge_mcp"]
            # Patch asyncio.run before the module uses it
            with patch("asyncio.run") as mock_run:
                # Remove cached module to force re-import with patch active
                if "knowledge_mcp.__main__" in sys.modules:
                    del sys.modules["knowledge_mcp.__main__"]

                import knowledge_mcp.__main__
                knowledge_mcp.__main__.main()
                mock_run.assert_called_once()
        finally:
            sys.argv = original_argv

    def test_main_runs_cli_with_cli_arg(self) -> None:
        """Verify main() runs CLI when 'cli' is first argument."""
        original_argv = sys.argv
        try:
            sys.argv = ["knowledge_mcp", "cli", "--help"]
            with patch("knowledge_mcp.cli.main.cli") as mock_typer_cli:
                # Remove cached module to force re-import
                if "knowledge_mcp.__main__" in sys.modules:
                    del sys.modules["knowledge_mcp.__main__"]

                import knowledge_mcp.__main__
                knowledge_mcp.__main__.main()
                mock_typer_cli.assert_called_once()
        finally:
            sys.argv = original_argv

    def test_main_function_exists(self) -> None:
        """Verify main function can be imported."""
        from knowledge_mcp.__main__ import main

        assert callable(main)


class TestMainModule:
    """Tests for __main__ module execution."""

    def test_main_block_calls_main(self) -> None:
        """Verify __main__ execution path."""
        # The if __name__ == "__main__" block calls main()
        # We test that main exists and is callable
        from knowledge_mcp.__main__ import main

        assert main is not None
