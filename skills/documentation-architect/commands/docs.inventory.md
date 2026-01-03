Catalog and classify documentation sources.

## Before Starting
Read and internalize the behavioral constraints in `GUARDRAILS.md`.

## Workflow
1. Scan source locations (.claude/resources/, codebase, uploads)
2. Classify by type (SPEC, ADR, RFC, CODE, DOC)
3. Map to Diátaxis quadrants
4. Estimate token counts for chunking
5. Identify coverage gaps

## Source Types
| Type | Description | Example |
|------|-------------|---------|
| SPEC | Requirements, features | requirements.md, PRD |
| ADR | Architecture decisions | ADR-001-auth.md |
| RFC | Proposals, designs | RFC-002-api.md |
| CODE | Docstrings, comments | Python/TS files |
| DOC | Existing documentation | README, guides |

## Outputs
- `docs/_meta/inventory.md`
- Updated `docs-sources.md`

## Guardrails
- No assumptions without approval
- Source-grounded content: every claim cites its source
- Idempotent: re-scans, updates registry, adds new, never removes

After completion, suggest `/docs.plan` as next step.
