---
phase: 7
slug: view-quality-handoff
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-07
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing) |
| **Config file** | pyproject.toml or implicit |
| **Quick run command** | `python3 -m pytest tests/test_view_assembler.py -x -q` |
| **Full suite command** | `python3 -m pytest tests/ -q` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/test_view_assembler.py tests/test_view_integration.py -x -q`
- **After every plan wave:** Run `python3 -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | VIEW-09 | unit | `pytest -x -k "deterministic or snapshot_hash"` | No - W0 | pending |
| 07-01-02 | 01 | 1 | VIEW-03 | unit | `pytest -x -k "density or rank"` | No - W0 | pending |
| 07-01-03 | 01 | 1 | VIEW-03 | unit | `pytest -x -k "rank and sort"` | No - W0 | pending |
| 07-01-04 | 01 | 1 | VIEW-03 | unit | `pytest -x -k "ranking_override"` | No - W0 | pending |
| 07-02-01 | 02 | 2 | VIEW-04 | unit | `pytest -x -k "edge"` | No - W0 | pending |
| 07-02-02 | 02 | 2 | VIEW-04 | unit+integration | `pytest -x -k "metadata or handoff"` | No - W0 | pending |
| 07-02-03 | 02 | 2 | VIEW-11 | unit | `pytest -x -k "log"` | No - W0 | pending |
| 07-02-04 | 02 | 2 | VIEW-12 | unit | `pytest -x -k "perf"` | No - W0 | pending |
| 07-02-05 | 02 | 2 | VIEW-09 | integration | `pytest -x -k "deterministic and integration"` | No - W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_view_assembler.py` — stubs for density scoring, edge extraction, deterministic sort
- [ ] `tests/test_view_assembler.py` — stubs for structured logging (caplog), performance, ranking override
- [ ] `schemas/view.json` — must be updated BEFORE code to avoid additionalProperties rejection

*Existing infrastructure covers framework and fixtures.*

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
