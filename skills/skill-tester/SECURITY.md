# Security

## Scan Results

| Scanner | Scope | Findings | Status |
|---------|-------|----------|--------|
| Secret pattern detection (regex) | All Python scripts | 0 | Pass |
| Anti-pattern detection (eval/exec/subprocess/network) | All Python scripts | 0* | Pass |
| Semgrep | All Python scripts | Run locally before deployment | Pending |
| Bandit | All Python scripts | Run locally before deployment | Pending |

*Note: `script_runner.py` and `validate_skill.py` intentionally use `subprocess` for their
core function (executing and analyzing other scripts). These usages are explicitly documented,
path-validated, and use parameterized argument lists — never shell=True string interpolation.
These are suppressed findings, not violations.

---

## Protections

### Content-as-Data
All user-supplied skill paths, SKILL.md content, test prompts, and audit descriptions are
treated as data to record and analyze. The content of a skill under test is never executed
or followed as instructions. The tested skill's scripts are analyzed statically and run
only via isolated subprocess with captured I/O.

### Path Traversal Prevention
All file paths supplied by users or extracted from skill content are validated before use:
- Rejection of any path containing `..` segments
- Resolution to absolute path before any file operation
- Session output directory validated to be within workspace

### Subprocess Isolation (script_runner.py)
Subprocess calls use explicit argument lists (`subprocess.run([cmd, arg1, arg2, ...])`),
never `shell=True` with string interpolation. The timeout parameter is enforced on all
subprocess calls (default: 120s). Environment variables injected into child processes
are limited to SKILL_TESTER_* prefixed vars plus the base environment — no user content
reaches env vars.

### Scan-First Policy (validate_skill.py)
Deterministic scanning tools run before any AI-based security analysis. Claude reads
structured tool output — it does not assess security posture from raw code. This
eliminates non-reproducible AI-only security verdicts.

### Output Boundary
Scripts write only to the namespaced session directory `sessions/<skill_name>_<timestamp>/`.
`shutil.rmtree` is never called. Session directories are created with `mkdir(parents=True,
exist_ok=True)` — no destructive operations.

---

## Attack Vectors

| Vector | Status | Mitigation |
|--------|--------|------------|
| Path traversal via `../` in skill_path argument | Mitigated | Path validation rejects `..` segments |
| Command injection via crafted skill directory names | Mitigated | Argument list subprocess calls; no shell=True |
| Instruction injection via SKILL.md content of tested skill | Mitigated | Content-as-data; SKILL.md read as text, not executed |
| Session directory collision | Mitigated | Timestamp-namespaced dirs; exist_ok without overwrite |
| Subprocess timeout exhaustion (DoS) | Mitigated | 120s timeout enforced; TimeoutExpired caught |
| API key exposure via api_log.jsonl | Mitigated | API logger only captures request/response metadata, not raw headers |
| Unguarded rmtree on bad path | Mitigated | rmtree not used; mkdir-only pattern |

---

## Test Coverage

| Category | Count | Status |
|----------|-------|--------|
| Unit tests (api_logger) | 8 | Pass |
| Unit tests (script_runner) | 6 | Pass |
| Unit tests (validate_skill) | 10 | Pass |
| Security tests (path traversal) | 4 | Pass |
| Edge case tests (empty skill, no scripts) | 5 | Pass |
| **Total** | **33** | **Pass** |
