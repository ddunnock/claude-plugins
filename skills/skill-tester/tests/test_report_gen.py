"""Tests for report_gen.py — HTML report generation.

Covers:
  1. Data loading (JSON, JSONL)
  2. Section builders (all 7 sections + summary card)
  3. HTML generation (end-to-end)
  4. Edge cases (missing data, empty sessions, load errors)
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from report_gen import (
    _load_json,
    _load_jsonl,
    load_session,
    _build_summary_card,
    _build_inventory_section,
    _build_scan_results_section,
    _build_prompt_lint_section,
    _build_prompt_review_section,
    _build_api_trace_section,
    _build_script_runs_section,
    _build_security_section,
    _build_code_review_section,
    generate_report,
    _esc,
    _badge,
    _score_color,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_session(tmp_path, files: dict) -> Path:
    """Create a session directory with given JSON files."""
    session = tmp_path / "session"
    session.mkdir()
    for name, data in files.items():
        if isinstance(data, str):
            (session / name).write_text(data, encoding="utf-8")
        else:
            (session / name).write_text(json.dumps(data), encoding="utf-8")
    return session


MINIMAL_INVENTORY = {
    "frontmatter": {"name": "test-skill"},
    "scripts": [{"path": "scripts/foo.py", "lines": 50, "urls": [],
                 "dangerous_calls": [], "potential_secrets": [],
                 "calls_anthropic_api": False}],
    "references": ["references/anti_patterns.md"],
    "summary": {"total_scripts": 1, "scripts_calling_api": 0},
}

MINIMAL_SCAN = {
    "findings": [{"severity": "LOW", "script": "scripts/foo.py",
                  "line": 10, "check_id": "test", "message": "Test finding"}],
    "summary": {"risk_rating": "LOW", "total_findings": 1,
                "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 1, "INFO": 0}},
    "tool_coverage": {"secret_detection": "ran", "bandit": "not-available"},
}

MINIMAL_PROMPT_LINT = {
    "findings": [{"severity": "WARN", "file": "SKILL.md", "line": 5,
                  "category": "INTERACTION", "message": "Test lint finding"}],
    "summary": {"overall": "WARN", "by_severity": {"ERROR": 0, "WARN": 1, "INFO": 0},
                "total_findings": 1, "by_category": {"INTERACTION": 1}},
}

MINIMAL_PROMPT_REVIEW = {
    "prompt_score": {"overall": 7.5, "clarity": 8, "completeness": 7,
                     "consistency": 8, "tool_use_correctness": 7, "agent_design": 8},
    "findings": [{"severity": "WARN", "category": "AMBIGUITY", "issue": "Vague instruction"}],
    "summary": "Good quality with minor ambiguity.",
}

MINIMAL_SECURITY = {
    "findings": [{"severity": "LOW", "script": "foo.py", "line": 1,
                  "category": "STRUCTURAL", "description": "Minor issue"}],
}

MINIMAL_CODE_REVIEW = {
    "overall_score": 8.0,
    "scripts": [{"script": "scripts/foo.py", "score": 8.0,
                 "issues": [{"category": "documentation", "description": "Missing docstring",
                             "suggestion": "Add module docstring"}],
                 "strengths": ["Clean error handling"]}],
    "top_recommendations": [],
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

class TestDataLoading:
    def test_load_json_valid(self, tmp_path):
        """_load_json reads valid JSON file."""
        f = tmp_path / "test.json"
        f.write_text('{"key": "value"}')
        result = _load_json(f)
        assert result == {"key": "value"}

    def test_load_json_missing(self, tmp_path):
        """_load_json returns None for missing file."""
        result = _load_json(tmp_path / "missing.json")
        assert result is None

    def test_load_json_corrupted(self, tmp_path):
        """_load_json returns error dict for corrupted JSON."""
        f = tmp_path / "bad.json"
        f.write_text("{not valid json")
        result = _load_json(f)
        assert "_load_error" in result

    def test_load_jsonl_valid(self, tmp_path):
        """_load_jsonl reads valid JSONL file."""
        f = tmp_path / "test.jsonl"
        f.write_text('{"a": 1}\n{"b": 2}\n')
        result = _load_jsonl(f)
        assert len(result) == 2
        assert result[0]["a"] == 1

    def test_load_jsonl_empty(self, tmp_path):
        """_load_jsonl returns empty list for empty file."""
        f = tmp_path / "empty.jsonl"
        f.write_text("")
        result = _load_jsonl(f)
        assert result == []

    def test_load_jsonl_missing(self, tmp_path):
        """_load_jsonl returns empty list for missing file."""
        result = _load_jsonl(tmp_path / "missing.jsonl")
        assert result == []

    def test_load_session_all_files(self, tmp_path):
        """load_session loads all expected data files."""
        session = _make_session(tmp_path, {
            "inventory.json": MINIMAL_INVENTORY,
            "scan_results.json": MINIMAL_SCAN,
            "prompt_lint.json": MINIMAL_PROMPT_LINT,
            "prompt_review.json": MINIMAL_PROMPT_REVIEW,
            "api_log.jsonl": "",
            "script_runs.jsonl": "",
            "security_report.json": MINIMAL_SECURITY,
            "code_review.json": MINIMAL_CODE_REVIEW,
        })
        data = load_session(str(session))
        assert data["inventory"] is not None
        assert data["scan_results"] is not None
        assert data["prompt_lint"] is not None
        assert data["prompt_review"] is not None
        assert data["security"] is not None
        assert data["code_review"] is not None
        assert "generated_at" in data

    def test_load_session_empty_dir(self, tmp_path):
        """load_session handles empty session directory gracefully."""
        session = tmp_path / "empty_session"
        session.mkdir()
        data = load_session(str(session))
        assert data["inventory"] is None
        assert data["scan_results"] is None
        assert data["prompt_lint"] is None


# ---------------------------------------------------------------------------
# Section builders — None/empty inputs
# ---------------------------------------------------------------------------

class TestSectionBuildersEmpty:
    def test_inventory_none(self):
        assert "No inventory data" in _build_inventory_section(None)

    def test_scan_results_none(self):
        assert "validate_skill.py was not run" in _build_scan_results_section(None)

    def test_prompt_lint_none(self):
        assert "No prompt lint data" in _build_prompt_lint_section(None)

    def test_prompt_review_none(self):
        assert "No prompt review data" in _build_prompt_review_section(None)

    def test_api_trace_empty(self):
        assert "No API calls recorded" in _build_api_trace_section([])

    def test_script_runs_empty(self):
        assert "No script runs recorded" in _build_script_runs_section([])

    def test_security_none(self):
        assert "No security report" in _build_security_section(None)

    def test_code_review_none(self):
        assert "No code review report" in _build_code_review_section(None)


# ---------------------------------------------------------------------------
# Section builders — with data
# ---------------------------------------------------------------------------

class TestSectionBuildersWithData:
    def test_inventory_renders_scripts(self):
        html = _build_inventory_section(MINIMAL_INVENTORY)
        assert "foo.py" in html
        assert "anti_patterns.md" in html

    def test_scan_results_renders_findings(self):
        html = _build_scan_results_section(MINIMAL_SCAN)
        assert "LOW" in html
        assert "Test finding" in html
        assert "secret_detection" in html

    def test_scan_results_clear(self):
        clear_scan = {
            "findings": [],
            "summary": {"risk_rating": "CLEAR"},
            "tool_coverage": {"secret_detection": "ran"},
        }
        html = _build_scan_results_section(clear_scan)
        assert "No deterministic findings" in html

    def test_prompt_lint_renders_findings(self):
        html = _build_prompt_lint_section(MINIMAL_PROMPT_LINT)
        assert "WARN" in html
        assert "Test lint finding" in html

    def test_prompt_review_renders_scores(self):
        html = _build_prompt_review_section(MINIMAL_PROMPT_REVIEW)
        assert "7.5" in html
        assert "Clarity" in html
        assert "AMBIGUITY" in html

    def test_security_renders_findings(self):
        html = _build_security_section(MINIMAL_SECURITY)
        assert "foo.py" in html
        assert "STRUCTURAL" in html

    def test_security_no_findings(self):
        html = _build_security_section({"findings": []})
        assert "No security findings" in html

    def test_code_review_renders_score(self):
        html = _build_code_review_section(MINIMAL_CODE_REVIEW)
        assert "8.0" in html or "8" in html
        assert "foo.py" in html

    def test_api_trace_renders_calls(self):
        calls = [{"call_id": "call_001", "request": {"model": "claude-sonnet-4-6"},
                  "response": {"usage": {"input_tokens": 100, "output_tokens": 50}},
                  "latency_ms": 250, "error": None}]
        html = _build_api_trace_section(calls)
        assert "call_001" in html
        assert "claude-sonnet-4-6" in html

    def test_script_runs_renders_entries(self):
        runs = [{"script": "scripts/foo.py", "run_id": "run_001",
                 "duration_ms": 150, "exit_code": 0, "files_created": ["out.json"],
                 "stdout": "hello", "stderr": ""}]
        html = _build_script_runs_section(runs)
        assert "foo.py" in html
        assert "run_001" in html


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

class TestUtilities:
    def test_esc_html_entities(self):
        assert _esc('<script>alert("xss")</script>') == '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'

    def test_badge_returns_span(self):
        html = _badge("CRITICAL", "#dc2626")
        assert "<span" in html
        assert "CRITICAL" in html

    def test_score_color_ranges(self):
        assert _score_color(9.5) == "#16a34a"  # green
        assert _score_color(7.5) == "#65a30d"  # yellow-green
        assert _score_color(5.5) == "#d97706"  # orange
        assert _score_color(3.0) == "#dc2626"  # red


# ---------------------------------------------------------------------------
# End-to-end report generation
# ---------------------------------------------------------------------------

class TestGenerateReport:
    def test_generates_valid_html(self, tmp_path):
        """generate_report produces valid HTML with all sections."""
        session = _make_session(tmp_path, {
            "inventory.json": MINIMAL_INVENTORY,
            "scan_results.json": MINIMAL_SCAN,
            "prompt_lint.json": MINIMAL_PROMPT_LINT,
            "prompt_review.json": MINIMAL_PROMPT_REVIEW,
            "api_log.jsonl": "",
            "script_runs.jsonl": "",
            "security_report.json": MINIMAL_SECURITY,
            "code_review.json": MINIMAL_CODE_REVIEW,
        })
        output = str(session / "report.html")
        generate_report(str(session), output)

        html = Path(output).read_text()
        assert "<!DOCTYPE html>" in html
        assert "test-skill" in html
        assert "Prompt Lint" in html
        assert "Prompt Review" in html
        assert "Security Audit" in html
        assert "Code Review" in html
        assert "Deterministic Scan" in html

    def test_generates_with_empty_session(self, tmp_path):
        """generate_report handles empty session (all None data)."""
        session = tmp_path / "empty"
        session.mkdir()
        output = str(session / "report.html")
        generate_report(str(session), output)

        html = Path(output).read_text()
        assert "<!DOCTYPE html>" in html
        assert "No inventory data" in html

    def test_report_escapes_html(self, tmp_path):
        """Report escapes HTML in skill names to prevent XSS."""
        inv = dict(MINIMAL_INVENTORY)
        inv["frontmatter"] = {"name": '<img src=x onerror="alert(1)">'}
        session = _make_session(tmp_path, {
            "inventory.json": inv,
            "scan_results.json": MINIMAL_SCAN,
            "prompt_lint.json": MINIMAL_PROMPT_LINT,
            "prompt_review.json": MINIMAL_PROMPT_REVIEW,
            "api_log.jsonl": "",
            "script_runs.jsonl": "",
            "security_report.json": MINIMAL_SECURITY,
            "code_review.json": MINIMAL_CODE_REVIEW,
        })
        output = str(session / "report.html")
        generate_report(str(session), output)

        html = Path(output).read_text()
        # Should be escaped, not raw HTML
        assert '<img src=x' not in html
        assert '&lt;img' in html
