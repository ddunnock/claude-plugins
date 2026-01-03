Walk codebase, sync documentation with implementation reality.

## Before Starting
Read and internalize the behavioral constraints in `GUARDRAILS.md`.

Documentation drifts from reality during implementation. This command bridges that gap by treating code as source of truth.

## Modes
- Default: Incremental sync (changed files)
- `--walkthrough`: Full code exploration
- `--component auth`: Specific component

## Workflow
1. Code walkthrough (analyze implementation)
2. Extract reality (APIs, configs, behavior)
3. Compare to existing documentation
4. Generate discrepancy report
5. Present update options per finding:
   - **Auto-update**: Apply simple fixes
   - **Manual review**: Complex changes
   - **Skip**: Acknowledge, don't change
   - **Code issue**: Doc is correct, code needs fix
6. Update memory files with code snapshot

## Discrepancy Types
| Type | Severity | Example |
|------|----------|---------|
| MISSING | HIGH | Public API not documented |
| INCORRECT | HIGH | Doc says 201, code returns 200 |
| OUTDATED | MEDIUM | References deprecated endpoint |
| UNDOCUMENTED | MEDIUM | Public function lacks docstring |

## Outputs
- `docs/_meta/sync-report.md`
- `.claude/memory/docs-codebase-snapshot.md`
- Updated documentation

## Guardrails
- Always safe, produces comparison, user chooses updates
- No assumptions without approval
