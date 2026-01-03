Create documentation plan (Work Breakdown Structure).

## Before Starting
Read and internalize the behavioral constraints in `GUARDRAILS.md`.

## Modes
- Default: Plan from inventory
- `--from-speckit`: Use speckit artifacts as input

## Workflow
1. Load inventory
2. Analyze sources for documentation needs
3. Map to Diátaxis quadrants
4. Design target structure
5. Create prioritized WBS
6. Define phases and gates

## WBS Item Structure
```markdown
| ID | Document | Quadrant | Priority | Sources | Dependencies |
|----|----------|----------|----------|---------|--------------|
| WBS-001 | quickstart.md | Tutorial | HIGH | SRC-001 | None |
| WBS-002 | authentication.md | How-To | HIGH | SRC-002,SRC-003 | WBS-001 |
```

## Outputs
- `docs/_meta/plan.md`

## Guardrails
- No assumptions without approval
- No proceeding without confirmation
- Idempotent: detects existing, offers update/regenerate

After completion, suggest `/docs.generate` as next step.
