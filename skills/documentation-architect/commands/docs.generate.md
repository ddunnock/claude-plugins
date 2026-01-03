Execute plan to create documentation.

## Before Starting
Read and internalize the behavioral constraints in `GUARDRAILS.md`.

## Selection Options
- Default: All pending items
- `WBS-001`: Specific item
- `"Phase 1"`: Items in phase
- `--user`: User docs only
- `--dev`: Developer docs only

## Workflow
1. Load plan WBS items
2. Resolve dependencies
3. For each item:
   - Load sources
   - Apply Diátaxis guidelines
   - Generate document
   - **Document Review Loop** (mandatory)
   - Log changes
   - Cascade analysis
   - Update memory files
4. Phase gate check

## Document Review Loop (per document)
```
Generate → Present Review → Collect Feedback
                              ↓
                   [Approved] → Update Memory → Next
                   [Changes] → Apply → Log → Cascade → Re-present
```

## Outputs
- Generated docs in docs/user/ and docs/developer/

## Guardrails
- Mandatory document review loop: every document individually reviewed
- Mandatory change logging: all changes tracked
- Mandatory cascade analysis: cross-document impact assessed
- Idempotent: preserves completed, regenerates pending
