Create implementation plans from specification files. Hierarchical for complex/multi-domain specs.

## Usage
- `/speckit.plan` - Plan from all specs
- `/speckit.plan spec.md` - Plan from specific spec
- `/speckit.plan --all` - Force regenerate all plans

## Workflow

1. **Locate specs** - Find spec files in .claude/resources/
2. **Assess complexity** - Single domain vs multi-domain
3. **Generate plans** - Create plan.md (and domain plans if complex)
4. **Validate** - Check plan completeness and consistency

## Output Structure

**Simple (single domain)**:
```
.claude/resources/
├── spec.md
└── plan.md
```

**Complex (multi-domain)**:
```
.claude/resources/
├── spec.md
├── plan.md              # Master plan with domain references
└── plans/
    ├── domain-a-plan.md
    ├── domain-b-plan.md
    └── domain-c-plan.md
```

## Plan Content

Plans contain:
- Requirements mapping (which spec sections covered)
- Architecture decisions
- Implementation approach (phases, NOT tasks)
- Verification strategy
- Notes for task generation

Plans do NOT contain:
- Individual tasks (that's /speckit.tasks)
- Implementation code
- Detailed how-to instructions

## Complexity Detection

| Indicator | Simple | Complex |
|-----------|--------|---------|
| Domains | Single | Multiple distinct |
| Page count | <10 pages | >10 pages |
| Stakeholder count | 1-2 | 3+ |

User can override detection.

## Idempotency
- Detects existing plans
- Offers update or regenerate
- Preserves manual edits with warning
