---
phase: 2
slug: schema-registry-file-operations
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-08
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun:test |
| **Config file** | none — uses bun test defaults |
| **Quick run command** | `bun test` |
| **Full suite command** | `bun test` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bun test`
- **After every plan wave:** Run `bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | SCHM-01 | unit | `bun test src/schemas/__tests__/registry.test.ts` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | SCHM-02 | unit | `bun test src/schemas/__tests__/registry.test.ts` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | SCHM-04 | unit | `bun test src/schemas/__tests__/registry.test.ts` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | SCHM-03 | integration | `bun test src/schemas/__tests__/discovery.test.ts` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | FILE-01 | integration | `bun test src/server/__tests__/tools-phase2.test.ts` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | FILE-02 | integration | `bun test src/server/__tests__/tools-phase2.test.ts` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 2 | FILE-03 | unit | `bun test src/server/__tests__/tools-phase2.test.ts` | ❌ W0 | ⬜ pending |
| 02-02-04 | 02 | 2 | FILE-04 | integration | `bun test src/server/__tests__/tools-phase2.test.ts` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/schemas/__tests__/registry.test.ts` — stubs for SCHM-01, SCHM-02, SCHM-04
- [ ] `src/schemas/__tests__/discovery.test.ts` — stubs for SCHM-03
- [ ] `src/server/__tests__/tools-phase2.test.ts` — stubs for FILE-01, FILE-02, FILE-03, FILE-04
- [ ] `src/schemas/__tests__/merge-patch.test.ts` — stubs for RFC 7386 merge patch logic

*Existing test infrastructure from Phase 1 covers framework setup (bun:test already configured).*

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
