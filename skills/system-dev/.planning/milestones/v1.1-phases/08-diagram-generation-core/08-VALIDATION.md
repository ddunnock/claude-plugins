---
phase: 8
slug: diagram-generation-core
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-07
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pyproject.toml |
| **Quick run command** | `python -m pytest tests/test_diagram_generator.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -x -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_diagram_generator.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | DIAG-01 | unit | `pytest tests/test_diagram_generator.py -k "test_d2"` | ❌ W0 | ⬜ pending |
| 08-01-02 | 01 | 1 | DIAG-02 | unit | `pytest tests/test_diagram_generator.py -k "test_mermaid"` | ❌ W0 | ⬜ pending |
| 08-01-03 | 01 | 1 | DIAG-06 | unit | `pytest tests/test_diagram_generator.py -k "test_gap"` | ❌ W0 | ⬜ pending |
| 08-01-04 | 01 | 1 | DIAG-03 | integration | `pytest tests/test_diagram_generator.py -k "test_slot_write"` | ❌ W0 | ⬜ pending |
| 08-02-01 | 02 | 1 | DIAG-04 | unit | `pytest tests/test_diagram_generator.py -k "test_schema"` | ❌ W0 | ⬜ pending |
| 08-02-02 | 02 | 1 | DIAG-09 | integration | `pytest tests/test_diagram_generator.py -k "test_preservation"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_diagram_generator.py` — stubs for DIAG-01, DIAG-02, DIAG-03, DIAG-04, DIAG-06, DIAG-09
- [ ] Test fixtures for mock view handoff data (sections, edges, gaps arrays)
- [ ] Test fixtures for mock SlotAPI instance

*Existing pytest infrastructure covers framework needs.*

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
