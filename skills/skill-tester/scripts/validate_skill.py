#!/usr/bin/env python3
"""validate_skill.py — Deterministic security and structural scanner for Claude skills.

Runs four check categories in fixed order:
  1. Secret pattern detection (regex — always available)
  2. SAST tools (Semgrep, Bandit — if installed; INFO finding if absent)
  3. Anti-pattern checks (eval/exec/subprocess/network)
  4. Structural validation (SKILL.md compliance)

Must complete before any AI-based security analysis (Rule B9/B14).
Output goes to <session_dir>/scan_results.json.

Usage:
  python3 scripts/validate_skill.py \\
    --skill-path /path/to/skill \\
    --session-dir sessions/my-skill_20260101_120000 \\
    [--sensitivity strict|standard|lenient]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_EXTS = {".py", ".sh", ".js", ".ts", ".bash"}

SECRET_PATTERNS = [
    (re.compile(r'sk-[a-zA-Z0-9]{20,}'), "Anthropic API key pattern"),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), "GitHub personal access token"),
    (re.compile(r'xoxb-[a-zA-Z0-9\-]{50,}'), "Slack bot token"),
    (re.compile(r'AKIA[0-9A-Z]{16}'), "AWS access key ID"),
    (re.compile(r'(?i)(password|passwd|secret|api_key|apikey|auth_token)\s*=\s*["\'][^"\']{8,}["\']'),
     "Hardcoded credential assignment"),
    (re.compile(r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----'), "Private key material"),
]

ANTI_PATTERNS = [
    (re.compile(r'\beval\s*\('), "AP-dangerous-eval", "eval() usage — dynamic code execution"),
    (re.compile(r'\bexec\s*\('), "AP-dangerous-exec", "exec() usage — dynamic code execution"),
    (re.compile(r'pickle\.loads?\s*\('), "AP-pickle", "pickle.loads/load() — unsafe deserialization"),
    (re.compile(r'yaml\.load\s*\((?!.*SafeLoader)'), "AP-yaml-unsafe", "yaml.load() without SafeLoader"),
    (re.compile(r'subprocess\.[a-z]+\(.*shell\s*=\s*True'), "AP-shell-true", "subprocess with shell=True"),
    (re.compile(r'os\.system\s*\('), "AP-os-system", "os.system() usage"),
    (re.compile(r'__import__\s*\('), "AP-dyn-import", "__import__() — dynamic module loading"),
    (re.compile(r'ctypes'), "AP-ctypes", "ctypes usage — native code execution"),
    (re.compile(r'requests\.(get|post|put|delete|patch)\s*\((?!.*anthropic)'),
     "AP-network-requests", "requests network call to non-Anthropic endpoint"),
    (re.compile(r'urllib\.request\.(urlopen|urlretrieve)\s*\('),
     "AP-network-urllib", "urllib network call"),
    (re.compile(r'socket\.socket\s*\('), "AP-network-socket", "raw socket connection"),
]

REQUIRED_STRUCTURAL = [
    ("SKILL.md", "SKILL.md file present"),
    (".claude-plugin/plugin.json", "plugin.json manifest present"),
    ("SECURITY.md", "SECURITY.md documentation present"),
]

SKILL_MD_SECTIONS = [
    ("<security", "SKILL.md contains <security> block"),
    ("<paths", "SKILL.md contains <paths> block"),
    ("<workflow", "SKILL.md contains <workflow> block"),
    ("<behavior", "SKILL.md contains <behavior> block"),
]


# ---------------------------------------------------------------------------
# Finding builder
# ---------------------------------------------------------------------------

_finding_counter = 0


def _reset_counter() -> None:
    """Reset the finding counter. Used by tests for deterministic IDs."""
    global _finding_counter
    _finding_counter = 0


def _finding(
    check_id: str,
    severity: str,
    category: str,
    script: str,
    message: str,
    line: Optional[int] = None,
    snippet: Optional[str] = None,
    source: str = "deterministic",
) -> dict:
    """Build a standardized finding dict.

    Args:
        check_id: Short identifier for the check that produced this finding.
        severity: One of CRITICAL, HIGH, MEDIUM, LOW, INFO.
        category: One of SECRETS, INJECTION, DANGEROUS_IMPORTS, NETWORK,
            FILE_SYSTEM, PERMISSIONS, DEPENDENCY, STRUCTURAL.
        script: Relative path to the script with the finding.
        message: Human-readable description of the finding.
        line: Source line number, or None.
        snippet: Code snippet (max 3 lines), or None.
        source: Always "deterministic" for this scanner.

    Returns:
        Finding dict matching the scan_results.json schema.
    """
    global _finding_counter
    _finding_counter += 1
    return {
        "finding_id": f"SCAN-{_finding_counter:03d}",
        "check_id": check_id,
        "source": source,
        "severity": severity,
        "category": category,
        "script": script,
        "line": line,
        "snippet": snippet,
        "message": message,
    }


# ---------------------------------------------------------------------------
# Check 1: Secret pattern detection
# ---------------------------------------------------------------------------

def check_secrets(skill_root: Path) -> list:
    """Scan all scripts for hardcoded secrets using regex patterns.

    Args:
        skill_root: Resolved path to the skill directory.

    Returns:
        List of finding dicts for any matched secret patterns.
    """
    findings = []
    for script_path in sorted(skill_root.rglob("*")):
        if script_path.suffix not in SCRIPT_EXTS or not script_path.is_file():
            continue
        rel = str(script_path.relative_to(skill_root))
        try:
            text = script_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"[validate_skill] Cannot read {rel}: {e}", file=sys.stderr)
            continue
        lines = text.splitlines()
        for pattern, description in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line_num = text[: match.start()].count("\n") + 1
                snippet = lines[line_num - 1].strip()[:120] if line_num <= len(lines) else None
                findings.append(_finding(
                    check_id="secret-pattern",
                    severity="CRITICAL",
                    category="SECRETS",
                    script=rel,
                    message=f"{description} — matched at line {line_num}",
                    line=line_num,
                    snippet=snippet,
                ))
    return findings


# ---------------------------------------------------------------------------
# Check 2: SAST tools (Semgrep / Bandit)
# ---------------------------------------------------------------------------

def _run_tool(cmd: list, cwd: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run an external tool as a subprocess with timeout.

    Args:
        cmd: Command and arguments as a list (no shell=True).
        cwd: Working directory for the subprocess.
        timeout: Maximum execution time in seconds.

    Returns:
        Tuple of (exit_code, stdout, stderr).
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"[TIMEOUT after {timeout}s]"
    except FileNotFoundError:
        return -2, "", f"[NOT FOUND: {cmd[0]}]"
    except OSError as e:
        return -3, "", f"[OS ERROR: {e}]"


def check_sast(skill_root: Path) -> list:
    """Run Semgrep and Bandit if available; record INFO finding if absent.

    Args:
        skill_root: Resolved path to the skill directory.

    Returns:
        List of finding dicts from SAST tools plus availability notices.
    """
    findings = []
    scripts_dir = str(skill_root / "scripts")

    # Semgrep
    semgrep_available = shutil.which("semgrep") is not None
    if semgrep_available:
        tmp_fd = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp_out = tmp_fd.name
        tmp_fd.close()
        rc, stdout, stderr = _run_tool(
            ["semgrep", "--config=auto", "scripts/", "--json", "-o", tmp_out],
            cwd=str(skill_root),
        )
        if rc not in (-2, -3) and Path(tmp_out).exists():
            try:
                semgrep_data = json.loads(Path(tmp_out).read_text())
                for result in semgrep_data.get("results", []):
                    findings.append(_finding(
                        check_id="semgrep",
                        severity="MEDIUM",
                        category="INJECTION",
                        script=result.get("path", "unknown"),
                        message=f"[Semgrep] {result.get('check_id', '?')}: {result.get('extra', {}).get('message', '')}",
                        line=result.get("start", {}).get("line"),
                        snippet=result.get("extra", {}).get("lines", "")[:120],
                    ))
            except (json.JSONDecodeError, OSError):
                pass
            finally:
                try:
                    Path(tmp_out).unlink(missing_ok=True)
                except OSError:
                    pass
    else:
        findings.append(_finding(
            check_id="semgrep-availability",
            severity="INFO",
            category="STRUCTURAL",
            script="scripts/",
            message="Semgrep not installed — SAST scan skipped. Install: pip install semgrep",
        ))

    # Bandit
    bandit_available = shutil.which("bandit") is not None
    if bandit_available:
        rc, stdout, stderr = _run_tool(
            ["bandit", "-r", "scripts/", "-f", "json"],
            cwd=str(skill_root),
        )
        if rc not in (-2, -3):
            try:
                bandit_data = json.loads(stdout)
                severity_map = {"HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
                for result in bandit_data.get("results", []):
                    sev = severity_map.get(result.get("issue_severity", "LOW"), "LOW")
                    findings.append(_finding(
                        check_id="bandit",
                        severity=sev,
                        category="DANGEROUS_IMPORTS",
                        script=result.get("filename", "unknown"),
                        message=f"[Bandit] {result.get('test_id', '?')}: {result.get('issue_text', '')}",
                        line=result.get("line_number"),
                        snippet=result.get("code", "")[:120],
                    ))
            except (json.JSONDecodeError, KeyError):
                pass
    else:
        findings.append(_finding(
            check_id="bandit-availability",
            severity="INFO",
            category="STRUCTURAL",
            script="scripts/",
            message="Bandit not installed — Python SAST scan skipped. Install: pip install bandit",
        ))

    return findings


# ---------------------------------------------------------------------------
# Check 3: Anti-pattern detection
# ---------------------------------------------------------------------------

def check_anti_patterns(skill_root: Path) -> list:
    """Scan all scripts for known dangerous code patterns.

    Args:
        skill_root: Resolved path to the skill directory.

    Returns:
        List of finding dicts for each matched anti-pattern.
    """
    findings = []
    # Scripts exempt from subprocess checks (they use it intentionally)
    subprocess_exempt = {"script_runner.py", "validate_skill.py"}

    for script_path in sorted(skill_root.rglob("*")):
        if script_path.suffix not in SCRIPT_EXTS or not script_path.is_file():
            continue
        rel = str(script_path.relative_to(skill_root))
        basename = script_path.name
        try:
            text = script_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()

        for pattern, check_id, description in ANTI_PATTERNS:
            # Apply subprocess exemption for scripts that use it intentionally
            if check_id in ("AP-shell-true",) and basename in subprocess_exempt:
                continue
            # Apply network exemption for api_logger (calls Anthropic intentionally)
            if "network" in check_id and basename == "api_logger.py":
                continue

            for match in pattern.finditer(text):
                line_num = text[: match.start()].count("\n") + 1
                snippet = lines[line_num - 1].strip()[:120] if line_num <= len(lines) else None
                # Determine severity
                if check_id in ("AP-dangerous-eval", "AP-dangerous-exec", "AP-shell-true"):
                    sev = "HIGH"
                    cat = "INJECTION"
                elif check_id in ("AP-pickle", "AP-yaml-unsafe", "AP-dyn-import"):
                    sev = "MEDIUM"
                    cat = "DANGEROUS_IMPORTS"
                elif "network" in check_id:
                    sev = "MEDIUM"
                    cat = "NETWORK"
                else:
                    sev = "LOW"
                    cat = "DANGEROUS_IMPORTS"

                findings.append(_finding(
                    check_id=check_id,
                    severity=sev,
                    category=cat,
                    script=rel,
                    message=description,
                    line=line_num,
                    snippet=snippet,
                ))

    return findings


# ---------------------------------------------------------------------------
# Check 4: Structural validation
# ---------------------------------------------------------------------------

def check_structure(skill_root: Path) -> list:
    """Validate SKILL.md structure and required file presence.

    Args:
        skill_root: Resolved path to the skill directory.

    Returns:
        List of finding dicts for structural compliance gaps.
    """
    findings = []

    # Required files
    for filename, description in REQUIRED_STRUCTURAL:
        fpath = skill_root / filename
        if not fpath.exists():
            findings.append(_finding(
                check_id="missing-required-file",
                severity="HIGH",
                category="STRUCTURAL",
                script=filename,
                message=f"Required file missing: {filename} — {description}",
            ))

    # SKILL.md section checks
    skill_md = skill_root / "SKILL.md"
    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            content = ""

        for tag, description in SKILL_MD_SECTIONS:
            if tag not in content:
                findings.append(_finding(
                    check_id="missing-skill-section",
                    severity="MEDIUM",
                    category="STRUCTURAL",
                    script="SKILL.md",
                    message=f"Required XML section missing: {tag} — {description}",
                ))

        # Version check
        if "version:" not in content:
            findings.append(_finding(
                check_id="missing-version",
                severity="LOW",
                category="STRUCTURAL",
                script="SKILL.md",
                message="SKILL.md frontmatter missing 'version' field",
            ))

        # Bare relative path check
        bare_paths = re.findall(r'python scripts/[a-zA-Z0-9_]+\.py', content)
        if bare_paths:
            findings.append(_finding(
                check_id="bare-relative-paths",
                severity="MEDIUM",
                category="STRUCTURAL",
                script="SKILL.md",
                message=(
                    f"Bare relative paths found in SKILL.md ({len(bare_paths)} occurrences). "
                    "Use ${CLAUDE_PLUGIN_ROOT}/scripts/ instead."
                ),
            ))

    return findings


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_scan(skill_path: str, session_dir: str, sensitivity: str = "standard") -> dict:
    """Execute all four scan phases and write scan_results.json.

    Args:
        skill_path: Path to the skill directory to scan.
        session_dir: Session directory where scan_results.json will be written.
        sensitivity: One of strict, standard, lenient.

    Returns:
        The scan results dict that was written to disk.

    Raises:
        FileNotFoundError: If skill_path does not exist.
        ValueError: If skill_path contains '..' segments.
    """
    # Validate path
    if ".." in Path(skill_path).parts:
        raise ValueError(f"Path traversal rejected: {skill_path}")
    skill_root = Path(skill_path).resolve()
    if not skill_root.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_root}")

    session = Path(session_dir)
    session.mkdir(parents=True, exist_ok=True)

    all_findings = []
    tool_coverage = {}

    print("[validate_skill] Phase 1/4: Secret pattern detection...", file=sys.stderr)
    secret_findings = check_secrets(skill_root)
    all_findings.extend(secret_findings)
    tool_coverage["secret_detection"] = "ran"
    print(f"  {len(secret_findings)} finding(s)", file=sys.stderr)

    print("[validate_skill] Phase 2/4: SAST tools (Semgrep/Bandit)...", file=sys.stderr)
    sast_findings = check_sast(skill_root)
    all_findings.extend(sast_findings)
    tool_coverage["semgrep"] = "ran" if shutil.which("semgrep") else "not-available"
    tool_coverage["bandit"] = "ran" if shutil.which("bandit") else "not-available"
    print(f"  {len(sast_findings)} finding(s)", file=sys.stderr)

    print("[validate_skill] Phase 3/4: Anti-pattern checks...", file=sys.stderr)
    ap_findings = check_anti_patterns(skill_root)
    all_findings.extend(ap_findings)
    tool_coverage["anti_pattern_checks"] = "ran"
    print(f"  {len(ap_findings)} finding(s)", file=sys.stderr)

    print("[validate_skill] Phase 4/4: Structural validation...", file=sys.stderr)
    struct_findings = check_structure(skill_root)
    all_findings.extend(struct_findings)
    tool_coverage["structural_validation"] = "ran"
    print(f"  {len(struct_findings)} finding(s)", file=sys.stderr)

    # Build summary
    by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for f in all_findings:
        sev = f.get("severity", "INFO")
        if sev in by_severity:
            by_severity[sev] += 1

    risk_rating = "CLEAR"
    for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if by_severity[level] > 0:
            risk_rating = level
            break

    result = {
        "skill_path": str(skill_root),
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "sensitivity": sensitivity,
        "tool_coverage": tool_coverage,
        "findings": all_findings,
        "summary": {
            "total_findings": len(all_findings),
            "by_severity": by_severity,
            "risk_rating": risk_rating,
        },
    }

    output_path = session / "scan_results.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"[validate_skill] scan_results.json written to {output_path} "
        f"— risk_rating: {risk_rating}",
        file=sys.stderr,
    )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Skill Tester — Deterministic Security Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Runs secret detection, SAST, anti-pattern checks, and structural\n"
            "validation. Must complete before AI-based security analysis (Rule B9)."
        ),
    )
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--session-dir", required=True, help="Session directory for output")
    parser.add_argument(
        "--sensitivity",
        choices=["strict", "standard", "lenient"],
        default="standard",
        help="Minimum severity to surface (strict=MEDIUM+, standard=HIGH+, lenient=CRITICAL)",
    )

    args = parser.parse_args()

    try:
        result = run_scan(args.skill_path, args.session_dir, args.sensitivity)
        summary = result["summary"]
        print(json.dumps(summary, indent=2))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
