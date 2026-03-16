#!/usr/bin/env python3
"""
api_logger.py — Anthropic API call logging shim for skill-tester.

Two modes:
  1. --inventory  : Scan a skill directory and output inventory.json
  2. --patch      : Monkey-patch anthropic.Anthropic to log all calls to a JSONL file.
                    Import this module before any skill script that calls the API.

Usage (inventory):
  python scripts/api_logger.py --inventory /path/to/skill --output session/inventory.json

Usage (patch, from Python):
  import api_logger
  api_logger.install(log_path="session/api_log.jsonl")
  # Now import and run the skill script — all API calls will be logged.
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from schemas import API_LOG_ENTRY_SCHEMA
from shared_io import _append_jsonl


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

SCRIPT_EXTS = {".py", ".sh", ".js", ".ts", ".bash"}
DANGEROUS_IMPORTS = {"os.system", "subprocess.call", "eval", "exec", "pickle.loads",
                     "pickle.load", "__import__", "importlib.import_module"}
URL_PATTERN = re.compile(
    r'https?://[^\s\'")\]>]+', re.IGNORECASE
)
SECRET_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|password|token|bearer|auth)\s*=\s*["\'][^"\']{8,}'),
    re.compile(r'(?i)os\.environ\[["\']([A-Z_]{4,})["\']'),
    re.compile(r'sk-[a-zA-Z0-9]{20,}'),
]


def _read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _scan_script(path: Path) -> dict:
    text = _read_text(path) or ""
    lines = text.splitlines()
    findings = {
        "path": str(path),
        "lines": len(lines),
        "urls": list(set(URL_PATTERN.findall(text))),
        "env_vars": [],
        "potential_secrets": [],
        "dangerous_calls": [],
        "calls_anthropic_api": bool(re.search(r'anthropic\.', text)),
    }
    for pat in SECRET_PATTERNS:
        for m in pat.finditer(text):
            findings["potential_secrets"].append({
                "match": m.group(0)[:80],
                "line": text[:m.start()].count("\n") + 1,
            })
    for danger in DANGEROUS_IMPORTS:
        if danger in text:
            findings["dangerous_calls"].append(danger)
    # Extract os.environ accesses
    for m in re.finditer(r'os\.environ\.get\(["\']([^"\']+)["\']|os\.environ\[["\']([^"\']+)["\']', text):
        var = m.group(1) or m.group(2)
        if var:
            findings["env_vars"].append(var)
    return findings


def inventory(skill_path: str, output_path: Optional[str] = None) -> dict:
    """Scan a skill directory and return structured inventory."""
    root = Path(skill_path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Skill path not found: {root}")

    skill_md = root / "SKILL.md"
    frontmatter = {}
    if skill_md.exists():
        text = _read_text(skill_md) or ""
        fm_match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    frontmatter[k.strip()] = v.strip()

    scripts = []
    commands = []
    agents = []
    references = []
    assets = []
    for f in sorted(root.rglob("*")):
        if f.is_file():
            rel = f.relative_to(root)
            rel_str = str(rel)
            if f.suffix in SCRIPT_EXTS:
                scripts.append(_scan_script(f))
            elif rel_str.startswith("commands/") and f.suffix == ".md":
                commands.append(rel_str)
            elif rel_str.startswith("agents/") and f.suffix == ".md":
                agents.append(rel_str)
            elif any(rel_str.startswith(p) for p in ("references/", "refs/")):
                references.append(rel_str)
            elif any(rel_str.startswith(p) for p in ("assets/", "templates/")):
                assets.append(rel_str)

    result = {
        "skill_path": str(root),
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "frontmatter": frontmatter,
        "skill_md_exists": skill_md.exists(),
        "scripts": scripts,
        "commands": commands,
        "agents": agents,
        "references": references,
        "assets": assets,
        "summary": {
            "total_scripts": len(scripts),
            "total_commands": len(commands),
            "total_agents": len(agents),
            "scripts_calling_api": sum(1 for s in scripts if s["calls_anthropic_api"]),
            "total_urls": sum(len(s["urls"]) for s in scripts),
            "potential_secret_count": sum(len(s["potential_secrets"]) for s in scripts),
            "dangerous_call_count": sum(len(s["dangerous_calls"]) for s in scripts),
        },
    }

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result, indent=2))
        print(f"[api_logger] Inventory written to {output_path}", file=sys.stderr)

    return result


# ---------------------------------------------------------------------------
# API Shim
# ---------------------------------------------------------------------------

_LOG_PATH: Optional[str] = None
_CALL_COUNTER = 0


def _log_call(call_id: str, run_id: Optional[str], request: dict,
              response: Any, latency_ms: int, error: Optional[str]):
    if not _LOG_PATH:
        return
    entry = {
        "call_id": call_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id or os.environ.get("SKILL_TESTER_RUN_ID"),
        "request": request,
        "response": response,
        "latency_ms": latency_ms,
        "error": error,
    }
    _append_jsonl(_LOG_PATH, entry, schema=API_LOG_ENTRY_SCHEMA)


_INSTALLED = False


def install(log_path: str, run_id: Optional[str] = None):
    """
    Monkey-patch anthropic.Anthropic and anthropic.AsyncAnthropic so all
    messages.create() calls are logged to `log_path`.
    """
    global _LOG_PATH, _INSTALLED
    if _INSTALLED:
        _LOG_PATH = log_path
        return
    _LOG_PATH = log_path
    _INSTALLED = True
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        import anthropic as _anthropic
    except ImportError:
        print("[api_logger] anthropic package not found — API logging disabled.", file=sys.stderr)
        return

    OrigMessages = _anthropic.resources.Messages

    class LoggingMessages(OrigMessages):
        def create(self, **kwargs):
            global _CALL_COUNTER
            _CALL_COUNTER += 1
            call_id = f"call_{_CALL_COUNTER:04d}_{uuid.uuid4().hex[:6]}"
            request_snapshot = {
                "model": kwargs.get("model"),
                "max_tokens": kwargs.get("max_tokens"),
                "system": (kwargs.get("system") or "")[:500],
                "messages": [
                    {
                        "role": m.get("role"),
                        "content": (
                            m["content"][:300] if isinstance(m.get("content"), str)
                            else str(m.get("content", ""))[:300]
                        ),
                    }
                    for m in (kwargs.get("messages") or [])
                ],
                "temperature": kwargs.get("temperature"),
                "tools": [t.get("name") for t in (kwargs.get("tools") or [])],
            }
            t0 = time.monotonic()
            error = None
            response = None
            try:
                response = super().create(**kwargs)
                response_snapshot = {
                    "id": getattr(response, "id", None),
                    "stop_reason": getattr(response, "stop_reason", None),
                    "usage": {
                        "input_tokens": getattr(getattr(response, "usage", None), "input_tokens", None),
                        "output_tokens": getattr(getattr(response, "usage", None), "output_tokens", None),
                    },
                    "content": [
                        {
                            "type": getattr(b, "type", "unknown"),
                            "text": (getattr(b, "text", "") or "")[:300],
                        }
                        for b in (getattr(response, "content", []) or [])
                    ],
                }
                return response
            except Exception as e:
                error = str(e)
                response_snapshot = None
                raise
            finally:
                latency_ms = int((time.monotonic() - t0) * 1000)
                _log_call(call_id, run_id, request_snapshot,
                          response_snapshot, latency_ms, error)

    # Patch the client class
    _anthropic.resources.Messages = LoggingMessages
    # Also patch on already-instantiated clients if possible
    _anthropic.Anthropic.messages = property(lambda self: LoggingMessages(self))

    print(f"[api_logger] Installed. API calls will be logged to: {log_path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill Tester — API Logger")
    sub = parser.add_subparsers(dest="cmd")

    inv = sub.add_parser("inventory", help="Scan a skill directory")
    inv.add_argument("skill_path", help="Path to skill directory")
    inv.add_argument("--output", "-o", default="session/inventory.json")

    args = parser.parse_args()
    if args.cmd == "inventory":
        result = inventory(args.skill_path, args.output)
        print(json.dumps(result["summary"], indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
