---
phase: 9
slug: diagram-templates-quality
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-07
---

# Phase 9 — Validation Strategy

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
| 09-01-01 | 01 | 1 | DIAG-07 | unit | `pytest tests/test_diagram_generator.py -k "template_registry"` | ❌ W0 | ⬜ pending |
| 09-01-02 | 01 | 1 | DIAG-07 | unit | `pytest tests/test_diagram_generator.py -k "template_loading"` | ❌ W0 | ⬜ pending |
| 09-01-03 | 01 | 1 | DIAG-07 | unit | `pytest tests/test_diagram_generator.py -k "template_rendering"` | ❌ W0 | ⬜ pending |
| 09-01-04 | 01 | 1 | DIAG-07 | integration | `pytest tests/test_diagram_generator.py -k "template_override"` | ❌ W0 | ⬜ pending |
| 09-02-01 | 02 | 2 | DIAG-05 | unit | `pytest tests/test_diagram_generator.py -k "abstraction"` | ❌ W0 | ⬜ pending |
| 09-02-02 | 02 | 2 | DIAG-08 | unit | `pytest tests/test_diagram_generator.py -k "determinism"` | ❌ W0 | ⬜ pending |
| 09-02-03 | 02 | 2 | DIAG-10 | unit | `pytest tests/test_diagram_generator.py -k "logging"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_diagram_generator.py` — add test stubs for template registry, abstraction layers, determinism, and logging
- [ ] Jinja2 dependency available in test environment

*Existing test infrastructure (pytest, conftest) covers framework needs.*

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
