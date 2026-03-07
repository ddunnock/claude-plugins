#!/usr/bin/env python3
"""test_script_runner.py — Unit tests for script_runner.py.

Tests cover:
  - Successful script execution and I/O capture
  - Non-zero exit code recording
  - Timeout enforcement
  - JSONL log writing
  - File creation detection
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from script_runner import run_script, summarize_session


def _make_script(content: str) -> Path:
    """Write a temporary Python script.

    Args:
        content: Python source code to write.

    Returns:
        Path to the created script file.
    """
    tmp = Path(tempfile.mkdtemp())
    script = tmp / "test_script.py"
    script.write_text(content, encoding="utf-8")
    return script


class TestRunScript(unittest.TestCase):
    """Tests for run_script()."""

    def test_captures_stdout(self):
        """Should capture stdout from a successful script run."""
        script = _make_script("print('hello world')\n")
        with tempfile.TemporaryDirectory() as session_dir:
            entry = run_script(str(script), session_dir=session_dir)
            self.assertIn("hello world", entry["stdout"])
            self.assertEqual(entry["exit_code"], 0)

    def test_captures_exit_code_on_failure(self):
        """Should record non-zero exit code for failing scripts."""
        script = _make_script("import sys; sys.exit(1)\n")
        with tempfile.TemporaryDirectory() as session_dir:
            entry = run_script(str(script), session_dir=session_dir)
            self.assertEqual(entry["exit_code"], 1)

    def test_captures_stderr(self):
        """Should capture stderr output."""
        script = _make_script("import sys; print('err', file=sys.stderr)\n")
        with tempfile.TemporaryDirectory() as session_dir:
            entry = run_script(str(script), session_dir=session_dir)
            self.assertIn("err", entry["stderr"])

    def test_timeout_enforcement(self):
        """Should record timed_out=True for scripts exceeding timeout."""
        script = _make_script("import time; time.sleep(60)\n")
        with tempfile.TemporaryDirectory() as session_dir:
            entry = run_script(str(script), session_dir=session_dir, timeout=1)
            self.assertTrue(entry["timed_out"])
            self.assertEqual(entry["exit_code"], -1)

    def test_writes_jsonl_log(self):
        """Should append an entry to script_runs.jsonl in the session dir."""
        script = _make_script("print('ok')\n")
        with tempfile.TemporaryDirectory() as session_dir:
            run_script(str(script), session_dir=session_dir)
            log_path = Path(session_dir) / "script_runs.jsonl"
            self.assertTrue(log_path.exists())
            lines = [l for l in log_path.read_text().splitlines() if l.strip()]
            self.assertEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertIn("run_id", entry)
            self.assertIn("exit_code", entry)

    def test_detects_created_files(self):
        """Should detect files created during script execution."""
        tmp = Path(tempfile.mkdtemp())
        script = tmp / "creator.py"
        script.write_text(
            "from pathlib import Path\n"
            "Path('output.json').write_text('{\"ok\": true}')\n"
        )
        with tempfile.TemporaryDirectory() as session_dir:
            entry = run_script(str(script), session_dir=session_dir, cwd=str(tmp))
            self.assertIn("output.json", " ".join(entry["files_created"]))


class TestSummarizeSession(unittest.TestCase):
    """Tests for summarize_session()."""

    def test_empty_session(self):
        """Should return runs=0 for session with no log file."""
        with tempfile.TemporaryDirectory() as session_dir:
            result = summarize_session(session_dir)
            self.assertEqual(result["runs"], 0)

    def test_counts_errors(self):
        """Should count runs with non-zero exit codes as errors."""
        script = _make_script("import sys; sys.exit(1)\n")
        with tempfile.TemporaryDirectory() as session_dir:
            run_script(str(script), session_dir=session_dir)
            summary = summarize_session(session_dir)
            self.assertEqual(summary["errors"], 1)


if __name__ == "__main__":
    unittest.main()
