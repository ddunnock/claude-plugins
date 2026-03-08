---
phase: 1
slug: format-engine-server
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-08
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun:test (built into bun) |
| **Config file** | none — bun:test works out of the box |
| **Quick run command** | `bun test` |
| **Full suite command** | `bun test --coverage` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bun test`
- **After every plan wave:** Run `bun test --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | INFR-01 | integration | `bun test tests/server/startup.test.ts` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | INFR-02 | unit | `bun test tests/server/plugin.test.ts` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | FMT-01 | unit | `bun test tests/formats/json.test.ts` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | FMT-02 | unit | `bun test tests/formats/yaml.test.ts` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 1 | FMT-03 | unit | `bun test tests/formats/xml.test.ts` | ❌ W0 | ⬜ pending |
| 01-02-04 | 02 | 1 | FMT-04 | unit | `bun test tests/formats/toml.test.ts` | ❌ W0 | ⬜ pending |
| 01-02-05 | 02 | 1 | FMT-05 | unit | `bun test tests/formats/registry.test.ts` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | SEC-01 | unit | `bun test tests/security/path-validator.test.ts` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 2 | SEC-02 | unit | `bun test tests/security/atomic-write.test.ts` | ❌ W0 | ⬜ pending |
| 01-03-03 | 03 | 2 | SEC-03 | unit | `bun test tests/security/schema-loading.test.ts` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/formats/json.test.ts` — round-trip fidelity for JSON
- [ ] `tests/formats/yaml.test.ts` — round-trip fidelity for YAML, type coercion edge cases
- [ ] `tests/formats/xml.test.ts` — round-trip with attributes, text content
- [ ] `tests/formats/toml.test.ts` — round-trip fidelity for TOML, datetime handling
- [ ] `tests/formats/registry.test.ts` — extension detection, unknown extension error
- [ ] `tests/security/path-validator.test.ts` — traversal, null bytes, encoded chars
- [ ] `tests/security/atomic-write.test.ts` — write completes atomically
- [ ] `tests/server/startup.test.ts` — server starts, tools listed
- [ ] `tests/server/plugin.test.ts` — plugin.json structure valid
- [ ] `bun add -D @types/node` — bun:test is built-in, types needed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Claude Code discovers server via plugin.json | INFR-02 | Requires Claude Code runtime | 1. Add to claude_plugins, 2. Run Claude Code, 3. Verify tool appears |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
