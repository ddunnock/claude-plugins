"""Golden tests for INCOSE deterministic quality rules.

Each test provides a requirement statement and asserts the expected
violations (or absence thereof). Tests are grouped by rule ID.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from quality_rules import Violation, check_requirement, check_rule, list_rules


def _has_violation(violations: list[Violation], rule_id: str) -> bool:
    return any(v.rule_id == rule_id for v in violations)


def _get_violation(violations: list[Violation], rule_id: str) -> Violation | None:
    return next((v for v in violations if v.rule_id == rule_id), None)


# --- R7: Vague terms ---

def test_r7_flags_appropriate():
    vs = check_requirement("The system shall provide appropriate error handling")
    v = _get_violation(vs, "R7")
    assert v is not None
    assert "appropriate" in v.matched_text.lower()


def test_r7_clean_statement():
    vs = check_requirement("The system shall provide structured error responses")
    assert not _has_violation(vs, "R7")


def test_r7_flags_several():
    vs = check_requirement("Several modules shall be loaded")
    v = _get_violation(vs, "R7")
    assert v is not None
    assert "several" in v.matched_text.lower()


# --- R8: Escape clauses ---

def test_r8_flags_where_possible():
    vs = check_requirement("The system shall, where possible, cache results")
    assert _has_violation(vs, "R8")


def test_r8_clean_statement():
    vs = check_requirement("The system shall cache all query results")
    assert not _has_violation(vs, "R8")


# --- R9: Open-ended clauses ---

def test_r9_flags_including_but_not_limited_to():
    vs = check_requirement("The system shall support formats including but not limited to JSON")
    assert _has_violation(vs, "R9")


def test_r9_clean_statement():
    vs = check_requirement("The system shall support JSON, XML, and CSV formats")
    assert not _has_violation(vs, "R9")


# --- R19: Combinators ---

def test_r19_flags_double_shall_and():
    vs = check_requirement("The system shall log errors and shall send alerts")
    assert _has_violation(vs, "R19")


def test_r19_clean_compound_object():
    vs = check_requirement("The system shall log errors and warnings")
    assert not _has_violation(vs, "R19")


def test_r19_flags_double_shall_or():
    vs = check_requirement("The system shall respond or shall queue the request")
    assert _has_violation(vs, "R19")


# --- R24: Pronouns ---

def test_r24_flags_it():
    vs = check_requirement("It shall respond within 200ms")
    assert _has_violation(vs, "R24")


def test_r24_clean_statement():
    vs = check_requirement("The API Gateway shall respond within 200ms")
    assert not _has_violation(vs, "R24")


# --- R26: Absolutes ---

def test_r26_flags_always():
    vs = check_requirement("The system shall always be available")
    v = _get_violation(vs, "R26")
    assert v is not None
    assert "always" in v.matched_text.lower()


def test_r26_clean_statement():
    vs = check_requirement("The system shall maintain 99.9% availability")
    assert not _has_violation(vs, "R26")


# --- R2: Passive voice ---

def test_r2_flags_passive():
    vs = check_requirement("Errors shall be logged by the system")
    assert _has_violation(vs, "R2")


def test_r2_clean_active_voice():
    vs = check_requirement("The system shall log errors")
    assert not _has_violation(vs, "R2")


def test_r2_whitelist_green():
    vs = check_requirement("The indicator shall be green when ready")
    assert not _has_violation(vs, "R2")


def test_r2_whitelist_open():
    vs = check_requirement("The port shall be open for connections")
    assert not _has_violation(vs, "R2")


# --- R20: Purpose phrases ---

def test_r20_flags_in_order_to():
    vs = check_requirement("The system shall cache results in order to improve latency")
    assert _has_violation(vs, "R20")


# --- R21: Parentheses ---

def test_r21_flags_parentheses():
    vs = check_requirement("The system shall return status codes (200, 404, 500)")
    assert _has_violation(vs, "R21")


# --- R15/R17: Logical and/or ---

def test_r15_flags_and_or():
    vs = check_requirement("The system shall accept JSON and/or XML")
    assert _has_violation(vs, "R15")


# --- R16: Negatives ---

def test_r16_flags_not():
    vs = check_requirement("The system shall not expose internal errors")
    assert _has_violation(vs, "R16")


# --- R10: Superfluous infinitives ---

def test_r10_flags_be_able_to():
    vs = check_requirement("The system shall be able to process 1000 requests")
    assert _has_violation(vs, "R10")


# --- R35: Temporal dependencies ---

def test_r35_flags_before():
    vs = check_requirement("The cache shall be invalidated before serving new data")
    assert _has_violation(vs, "R35")


# --- R32: Universal quantifiers ---

def test_r32_flags_every():
    vs = check_requirement("Every endpoint shall require authentication")
    assert _has_violation(vs, "R32")


# --- check_rule ---

def test_check_rule_returns_violation():
    v = check_rule("It shall respond", "R24")
    assert v is not None
    assert v.rule_id == "R24"


def test_check_rule_returns_none_for_clean():
    v = check_rule("The API shall respond", "R24")
    assert v is None


# --- list_rules ---

def test_list_rules_returns_all():
    rules = list_rules()
    rule_ids = {r.rule_id for r in rules}
    assert "R7" in rule_ids
    assert "R2" in rule_ids
    assert "R19" in rule_ids
    assert len(rules) >= 15


# --- CLI ---

def test_cli_check_returns_json():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quality_rules.py"),
         "check", "It shall be appropriate"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0


def test_cli_check_clean_returns_empty():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quality_rules.py"),
         "check", "The API Gateway shall respond within 200ms"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data == []


def test_cli_check_all_processes_registry(tmp_path):
    registry = {
        "requirements": [
            {"id": "REQ-001", "statement": "The system shall be appropriate"},
            {"id": "REQ-002", "statement": "The API shall respond within 200ms"},
        ]
    }
    reg_file = tmp_path / "reqs.json"
    reg_file.write_text(json.dumps(registry))
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quality_rules.py"),
         "check-all", "--registry", str(reg_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "REQ-001" in data
    assert len(data["REQ-001"]) > 0  # "appropriate" should flag
    assert "REQ-002" in data


def test_cli_rules_lists_all():
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quality_rules.py"),
         "rules"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) >= 15
