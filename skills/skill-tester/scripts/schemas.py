#!/usr/bin/env python3
"""JSON schemas for skill-tester data files.

Defines field-level schemas used by _validate_json_schema() in shared_io.py.
Each schema maps field names to {"required": bool, "type": type_or_tuple}.

Usage:
    from schemas import MANIFEST_SCHEMA, SCAN_RESULTS_SCHEMA
    from shared_io import _load_json

    manifest = _load_json("manifest.json", schema=MANIFEST_SCHEMA)
"""

NoneType = type(None)

MANIFEST_SCHEMA = {
    "validated_at": {"required": True, "type": str},
    "skill_path": {"required": True, "type": str},
    "session_dir": {"required": True, "type": str},
    "validation": {"required": True, "type": dict},
    "errors": {"required": True, "type": list},
    "warnings": {"required": True, "type": list},
    "report_root": {"required": False, "type": str},
    "mode": {"required": False, "type": str},
}

VALIDATION_DETAIL_SCHEMA = {
    "path_valid": {"required": True, "type": bool},
    "skill_md_present": {"required": True, "type": bool},
    "plugin_json_present": {"required": True, "type": bool},
    "plugin_json_valid": {"required": True, "type": bool},
    "security_md_present": {"required": True, "type": bool},
    "scripts_count": {"required": True, "type": int},
    "sandbox_path": {"required": True, "type": str},
}

SCAN_RESULTS_SCHEMA = {
    "skill_path": {"required": True, "type": str},
    "scanned_at": {"required": True, "type": str},
    "sensitivity": {"required": True, "type": str},
    "tool_coverage": {"required": True, "type": dict},
    "findings": {"required": True, "type": list},
    "summary": {"required": True, "type": dict},
}

INVENTORY_SCHEMA = {
    "skill_path": {"required": True, "type": str},
    "scanned_at": {"required": True, "type": str},
    "frontmatter": {"required": True, "type": dict},
    "skill_md_exists": {"required": True, "type": bool},
    "scripts": {"required": True, "type": list},
    "references": {"required": True, "type": list},
    "assets": {"required": True, "type": list},
    "summary": {"required": True, "type": dict},
}

PROMPT_LINT_SCHEMA = {
    "skill_path": {"required": True, "type": str},
    "linted_at": {"required": True, "type": str},
    "files_analyzed": {"required": True, "type": list},
    "findings": {"required": True, "type": list},
    "summary": {"required": True, "type": dict},
}

PROMPT_REVIEW_SCHEMA = {
    "skill_name": {"required": True, "type": str},
    "reviewed_at": {"required": True, "type": str},
    "findings": {"required": True, "type": list},
    "prompt_score": {"required": True, "type": dict},
    "summary": {"required": True, "type": str},
}

SECURITY_REPORT_SCHEMA = {
    "skill_name": {"required": True, "type": str},
    "reviewed_at": {"required": True, "type": str},
    "findings": {"required": True, "type": list},
    "summary": {"required": True, "type": dict},
}

CODE_REVIEW_SCHEMA = {
    "skill_name": {"required": True, "type": str},
    "reviewed_at": {"required": True, "type": str},
    "overall_score": {"required": True, "type": (int, float)},
    "scripts": {"required": True, "type": list},
    "recommendations": {"required": True, "type": list},
}

SCRIPT_RUN_ENTRY_SCHEMA = {
    "run_id": {"required": True, "type": str},
    "timestamp": {"required": True, "type": str},
    "script": {"required": True, "type": str},
    "exit_code": {"required": True, "type": int},
    "duration_ms": {"required": True, "type": int},
    "stdout": {"required": True, "type": str},
    "stderr": {"required": True, "type": str},
}

API_LOG_ENTRY_SCHEMA = {
    "call_id": {"required": True, "type": str},
    "timestamp": {"required": True, "type": str},
    "run_id": {"required": False, "type": (str, NoneType)},
    "request": {"required": True, "type": dict},
    "latency_ms": {"required": True, "type": int},
    "error": {"required": False, "type": (str, NoneType)},
}