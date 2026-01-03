Establish documentation foundation for this project.

## Before Starting
Read and internalize the behavioral constraints in `GUARDRAILS.md`.

## Workflow
1. Check existing state (docs/, .claude/memory/docs-*.md)
2. Detect project type (library, CLI, app, service)
3. Create docs/ structure with Diátaxis layout
4. Create documentation memory files
5. Present summary and next steps

## Outputs to Create
```
docs/
├── index.md
├── user/
│   ├── getting-started/
│   ├── guides/
│   ├── concepts/
│   └── reference/
├── developer/
│   ├── architecture/
│   ├── contributing/
│   └── reference/api/
└── _meta/
    ├── inventory.md
    ├── plan.md
    └── progress.md

.claude/memory/
├── docs-constitution.md
├── docs-terminology.md
└── docs-sources.md
```

## Guardrails
- No assumptions without approval
- No proceeding without confirmation
- Idempotent: skips existing, updates changed, preserves customizations

After completion, suggest `/docs.inventory` as next step.
