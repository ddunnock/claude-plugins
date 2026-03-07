#!/usr/bin/env python3
"""
script_runner.py — Execute skill scripts with full I/O capture for skill-tester.

Records stdout, stderr, exit code, timing, and files created per script invocation.
Optionally installs the API logging shim before execution.

Usage:
  python scripts/script_runner.py \\
    --script path/to/script.py \\
    --args "--input foo.json --output bar.html" \\
    --session-dir session/ \\
    --run-id run_001 \\
    [--stdin "some input"] \\
    [--capture-api] \\
    [--env KEY=VALUE ...]

Or run all scripts discovered in a skill:
  python scripts/script_runner.py \\
    --skill-path /path/to/skill \\
    --prompt "User test prompt text" \\
    --session-dir session/ \\
    [--capture-api]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SCRIPT_EXTS = {".py", ".sh", ".js", ".ts"}
SESSION_SCRIPT_LOG = "script_runs.jsonl"


def _snapshot_dir(path: Path) -> set:
    """Return set of file paths currently under `path`."""
    if not path.exists():
        return set()
    return {str(f.relative_to(path)) for f in path.rglob("*") if f.is_file()}


def run_script(
    script_path: str,
    args: list[str] | None = None,
    stdin_data: Optional[str] = None,
    session_dir: str = "session",
    run_id: Optional[str] = None,
    extra_env: dict | None = None,
    capture_api: bool = False,
    cwd: Optional[str] = None,
    timeout: int = 120,
) -> dict:
    """
    Execute a script and capture all observable behavior.

    Returns a dict matching the script_runs.jsonl schema.
    """
    script = Path(script_path).resolve()
    session = Path(session_dir)
    session.mkdir(parents=True, exist_ok=True)

    run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
    api_log_path = str(session / "api_log.jsonl")

    # Build environment
    env = os.environ.copy()
    env["SKILL_TESTER_RUN_ID"] = run_id
    env["SKILL_TESTER_SESSION_DIR"] = str(session.resolve())
    if capture_api:
        env["SKILL_TESTER_API_LOG"] = api_log_path
    if extra_env:
        env.update(extra_env)

    # Choose interpreter
    tmpdir = None
    suffix = script.suffix.lower()
    if suffix == ".py":
        cmd = [sys.executable]
        if capture_api:
            # Inject the shim as a -c preamble via PYTHONSTARTUP trick
            shim_path = Path(__file__).parent / "api_logger.py"
            if shim_path.exists():
                startup = (
                    f"import sys; sys.path.insert(0, '{shim_path.parent}'); "
                    f"import api_logger; api_logger.install('{api_log_path}', run_id='{run_id}')"
                )
                # Write startup file to temp
                tmpdir = tempfile.mkdtemp()
                startup_file = Path(tmpdir) / "sitecustomize.py"
                startup_file.write_text(startup)
                env["PYTHONPATH"] = tmpdir + os.pathsep + env.get("PYTHONPATH", "")
        cmd.append(str(script))
    elif suffix in {".sh", ".bash"}:
        cmd = ["bash", str(script)]
    elif suffix in {".js", ".ts"}:
        cmd = ["node", str(script)]
    else:
        cmd = [str(script)]

    if args:
        cmd.extend(args)

    working_dir = Path(cwd) if cwd else script.parent
    pre_files = _snapshot_dir(working_dir)

    t0 = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()

    try:
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(working_dir),
            timeout=timeout,
        )
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
        timed_out = False
    except subprocess.TimeoutExpired as e:
        exit_code = -1
        stdout = (e.stdout or b"").decode("utf-8", errors="replace")
        stderr = (e.stderr or b"").decode("utf-8", errors="replace") + f"\n[TIMEOUT after {timeout}s]"
        timed_out = True
    except FileNotFoundError as e:
        exit_code = -2
        stdout = ""
        stderr = f"[ERROR] Could not launch script: {e}"
        timed_out = False
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)

    duration_ms = int((time.monotonic() - t0) * 1000)

    post_files = _snapshot_dir(working_dir)
    files_created = sorted(post_files - pre_files)

    entry = {
        "run_id": run_id,
        "timestamp": started_at,
        "script": str(script),
        "args": args or [],
        "stdin": stdin_data,
        "stdout": stdout[:10_000],   # cap at 10k chars
        "stderr": stderr[:5_000],
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "timed_out": timed_out,
        "files_created": files_created,
        "env_vars_injected": list((extra_env or {}).keys()),
        "capture_api_enabled": capture_api,
    }

    log_path = session / SESSION_SCRIPT_LOG
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def run_skill_scripts(
    skill_path: str,
    prompt: str,
    session_dir: str = "session",
    capture_api: bool = True,
    timeout: int = 120,
) -> list[dict]:
    """
    Discover and run all scripts in a skill directory for a given prompt.

    Each script is invoked with --help as a safe dry-run to capture its
    interface. The prompt is passed via the SKILL_TESTER_PROMPT env var
    for scripts that opt in to reading it.

    Returns a list of run entries.
    """
    root = Path(skill_path).resolve()
    scripts = sorted(
        f for f in root.rglob("*")
        if f.is_file() and f.suffix.lower() in SCRIPT_EXTS
        and "test" not in f.parts  # skip test dirs
    )

    if not scripts:
        print(f"[script_runner] No scripts found in {root}", file=sys.stderr)
        return []

    print(f"[script_runner] Found {len(scripts)} script(s) to analyze.", file=sys.stderr)
    results = []
    for i, script in enumerate(scripts):
        run_id = f"run_{i+1:03d}_{script.stem}"
        print(f"[script_runner] Running {script.relative_to(root)} ...", file=sys.stderr)
        entry = run_script(
            script_path=str(script),
            args=["--help"],   # dry-run: capture help/usage text without side effects
            session_dir=session_dir,
            run_id=run_id,
            extra_env={"SKILL_TESTER_PROMPT": prompt},
            capture_api=capture_api,
            cwd=str(root),
            timeout=timeout,
        )
        results.append(entry)
        status = "✓" if entry["exit_code"] == 0 else f"✗ (exit {entry['exit_code']})"
        print(f"  {status} {entry['duration_ms']}ms", file=sys.stderr)

    return results


def summarize_session(session_dir: str) -> dict:
    """Summarize all script runs from a session's JSONL log."""
    log = Path(session_dir) / SESSION_SCRIPT_LOG
    if not log.exists():
        return {"runs": 0}

    runs = []
    with open(log, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    runs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    return {
        "runs": len(runs),
        "total_duration_ms": sum(r.get("duration_ms", 0) for r in runs),
        "errors": sum(1 for r in runs if r.get("exit_code", 0) != 0),
        "timeouts": sum(1 for r in runs if r.get("timed_out", False)),
        "files_created": sorted({f for r in runs for f in r.get("files_created", [])}),
        "scripts": list({r["script"] for r in runs}),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill Tester — Script Runner")
    sub = parser.add_subparsers(dest="cmd")

    # Single script mode
    single = sub.add_parser("run", help="Run a single script")
    single.add_argument("script", help="Path to script")
    single.add_argument("--args", nargs="*", default=[])
    single.add_argument("--stdin", default=None)
    single.add_argument("--session-dir", default="session")
    single.add_argument("--run-id", default=None)
    single.add_argument("--capture-api", action="store_true")
    single.add_argument("--timeout", type=int, default=120)
    single.add_argument("--env", nargs="*", default=[],
                        metavar="KEY=VALUE", help="Extra env vars")

    # Skill mode
    skill_cmd = sub.add_parser("skill", help="Run all scripts in a skill")
    skill_cmd.add_argument("skill_path")
    skill_cmd.add_argument("--prompt", default="Test prompt")
    skill_cmd.add_argument("--session-dir", default="session")
    skill_cmd.add_argument("--capture-api", action="store_true")
    skill_cmd.add_argument("--timeout", type=int, default=120)

    # Summarize mode
    summ = sub.add_parser("summary", help="Summarize a session")
    summ.add_argument("--session-dir", default="session")

    args = parser.parse_args()

    if args.cmd == "run":
        extra_env = dict(e.split("=", 1) for e in (args.env or []) if "=" in e)
        entry = run_script(
            script_path=args.script,
            args=args.args or None,
            stdin_data=args.stdin,
            session_dir=args.session_dir,
            run_id=args.run_id,
            extra_env=extra_env or None,
            capture_api=args.capture_api,
            timeout=args.timeout,
        )
        print(json.dumps(entry, indent=2))

    elif args.cmd == "skill":
        results = run_skill_scripts(
            args.skill_path,
            prompt=args.prompt,
            session_dir=args.session_dir,
            capture_api=args.capture_api,
            timeout=args.timeout,
        )
        print(json.dumps(summarize_session(args.session_dir), indent=2))

    elif args.cmd == "summary":
        print(json.dumps(summarize_session(args.session_dir), indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
