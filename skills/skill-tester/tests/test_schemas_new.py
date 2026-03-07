"""Tests for the 6 new schemas added in v0.5.0.

Covers validation pass/fail cases for:
  PROMPT_LINT_SCHEMA, PROMPT_REVIEW_SCHEMA, SECURITY_REPORT_SCHEMA,
  CODE_REVIEW_SCHEMA, SCRIPT_RUN_ENTRY_SCHEMA, API_LOG_ENTRY_SCHEMA
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from schemas import (
    PROMPT_LINT_SCHEMA,
    PROMPT_REVIEW_SCHEMA,
    SECURITY_REPORT_SCHEMA,
    CODE_REVIEW_SCHEMA,
    SCRIPT_RUN_ENTRY_SCHEMA,
    API_LOG_ENTRY_SCHEMA,
)
from shared_io import _validate_json_schema


# ---------------------------------------------------------------------------
# PROMPT_LINT_SCHEMA
# ---------------------------------------------------------------------------

def test_prompt_lint_schema_valid():
    data = {
        "skill_path": "/path/to/skill",
        "linted_at": "2026-03-07T12:00:00Z",
        "files_analyzed": ["SKILL.md"],
        "findings": [],
        "summary": {"total_findings": 0},
    }
    assert _validate_json_schema(data, PROMPT_LINT_SCHEMA) == []


def test_prompt_lint_schema_missing_required():
    data = {"skill_path": "/path"}
    errors = _validate_json_schema(data, PROMPT_LINT_SCHEMA)
    assert len(errors) == 4  # missing linted_at, files_analyzed, findings, summary


def test_prompt_lint_schema_wrong_type():
    data = {
        "skill_path": "/path",
        "linted_at": "2026-03-07T12:00:00Z",
        "files_analyzed": "not a list",
        "findings": [],
        "summary": {},
    }
    errors = _validate_json_schema(data, PROMPT_LINT_SCHEMA)
    assert len(errors) == 1
    assert "files_analyzed" in errors[0]


# ---------------------------------------------------------------------------
# PROMPT_REVIEW_SCHEMA
# ---------------------------------------------------------------------------

def test_prompt_review_schema_valid():
    data = {
        "skill_name": "test-skill",
        "reviewed_at": "2026-03-07T12:00:00Z",
        "findings": [{"severity": "WARN", "issue": "test"}],
        "prompt_score": {"overall": 8},
        "summary": "Good quality skill.",
    }
    assert _validate_json_schema(data, PROMPT_REVIEW_SCHEMA) == []


def test_prompt_review_schema_missing_required():
    data = {"skill_name": "test"}
    errors = _validate_json_schema(data, PROMPT_REVIEW_SCHEMA)
    assert len(errors) == 4


def test_prompt_review_schema_summary_wrong_type():
    data = {
        "skill_name": "test",
        "reviewed_at": "2026-03-07",
        "findings": [],
        "prompt_score": {},
        "summary": 123,  # should be str
    }
    errors = _validate_json_schema(data, PROMPT_REVIEW_SCHEMA)
    assert len(errors) == 1
    assert "summary" in errors[0]


# ---------------------------------------------------------------------------
# SECURITY_REPORT_SCHEMA
# ---------------------------------------------------------------------------

def test_security_report_schema_valid():
    data = {
        "skill_name": "test-skill",
        "reviewed_at": "2026-03-07T12:00:00Z",
        "findings": [],
        "summary": {"risk_rating": "CLEAR"},
    }
    assert _validate_json_schema(data, SECURITY_REPORT_SCHEMA) == []


def test_security_report_schema_missing_required():
    data = {"skill_name": "test"}
    errors = _validate_json_schema(data, SECURITY_REPORT_SCHEMA)
    assert len(errors) == 3


# ---------------------------------------------------------------------------
# CODE_REVIEW_SCHEMA
# ---------------------------------------------------------------------------

def test_code_review_schema_valid_int_score():
    data = {
        "skill_name": "test-skill",
        "reviewed_at": "2026-03-07T12:00:00Z",
        "overall_score": 8,
        "scripts": [],
        "recommendations": ["Use type hints"],
    }
    assert _validate_json_schema(data, CODE_REVIEW_SCHEMA) == []


def test_code_review_schema_valid_float_score():
    data = {
        "skill_name": "test-skill",
        "reviewed_at": "2026-03-07T12:00:00Z",
        "overall_score": 7.5,
        "scripts": [],
        "recommendations": [],
    }
    assert _validate_json_schema(data, CODE_REVIEW_SCHEMA) == []


def test_code_review_schema_string_score_rejected():
    data = {
        "skill_name": "test-skill",
        "reviewed_at": "2026-03-07T12:00:00Z",
        "overall_score": "8",  # should be int or float
        "scripts": [],
        "recommendations": [],
    }
    errors = _validate_json_schema(data, CODE_REVIEW_SCHEMA)
    assert len(errors) == 1
    assert "overall_score" in errors[0]


def test_code_review_schema_missing_required():
    data = {"skill_name": "test"}
    errors = _validate_json_schema(data, CODE_REVIEW_SCHEMA)
    assert len(errors) == 4


# ---------------------------------------------------------------------------
# SCRIPT_RUN_ENTRY_SCHEMA
# ---------------------------------------------------------------------------

def test_script_run_entry_schema_valid():
    data = {
        "run_id": "run_001",
        "timestamp": "2026-03-07T12:00:00Z",
        "script": "/path/to/script.py",
        "exit_code": 0,
        "duration_ms": 150,
        "stdout": "Hello\n",
        "stderr": "",
    }
    assert _validate_json_schema(data, SCRIPT_RUN_ENTRY_SCHEMA) == []


def test_script_run_entry_schema_missing_required():
    data = {"run_id": "run_001", "timestamp": "2026-03-07"}
    errors = _validate_json_schema(data, SCRIPT_RUN_ENTRY_SCHEMA)
    assert len(errors) == 5  # missing script, exit_code, duration_ms, stdout, stderr


def test_script_run_entry_schema_wrong_exit_code_type():
    data = {
        "run_id": "run_001",
        "timestamp": "2026-03-07",
        "script": "test.py",
        "exit_code": "0",  # should be int
        "duration_ms": 100,
        "stdout": "",
        "stderr": "",
    }
    errors = _validate_json_schema(data, SCRIPT_RUN_ENTRY_SCHEMA)
    assert len(errors) == 1
    assert "exit_code" in errors[0]


# ---------------------------------------------------------------------------
# API_LOG_ENTRY_SCHEMA
# ---------------------------------------------------------------------------

def test_api_log_entry_schema_valid():
    data = {
        "call_id": "call_0001_abc123",
        "timestamp": "2026-03-07T12:00:00Z",
        "run_id": "run_001",
        "request": {"model": "claude-sonnet-4-6"},
        "latency_ms": 500,
        "error": None,
    }
    assert _validate_json_schema(data, API_LOG_ENTRY_SCHEMA) == []


def test_api_log_entry_schema_valid_without_optional():
    data = {
        "call_id": "call_0001",
        "timestamp": "2026-03-07T12:00:00Z",
        "request": {"model": "claude-sonnet-4-6"},
        "latency_ms": 200,
    }
    # run_id and error are optional
    assert _validate_json_schema(data, API_LOG_ENTRY_SCHEMA) == []


def test_api_log_entry_schema_null_run_id():
    data = {
        "call_id": "call_0001",
        "timestamp": "2026-03-07T12:00:00Z",
        "run_id": None,
        "request": {},
        "latency_ms": 100,
        "error": None,
    }
    assert _validate_json_schema(data, API_LOG_ENTRY_SCHEMA) == []


def test_api_log_entry_schema_missing_required():
    data = {"call_id": "call_0001"}
    errors = _validate_json_schema(data, API_LOG_ENTRY_SCHEMA)
    assert len(errors) == 3  # missing timestamp, request, latency_ms


def test_api_log_entry_schema_wrong_latency_type():
    data = {
        "call_id": "call_0001",
        "timestamp": "2026-03-07",
        "request": {},
        "latency_ms": "500",  # should be int
    }
    errors = _validate_json_schema(data, API_LOG_ENTRY_SCHEMA)
    assert len(errors) == 1
    assert "latency_ms" in errors[0]
