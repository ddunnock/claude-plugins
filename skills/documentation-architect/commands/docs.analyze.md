Read-only audit of documentation quality.

## Before Starting
Read and internalize the behavioral constraints in `GUARDRAILS.md`.

## Characteristics
- **Read-only**: Never modifies files
- **Deterministic**: Same input = same output
- **Stable IDs**: Finding IDs consistent across runs

## Checks Performed
- Document quality scores
- Diátaxis coverage matrix
- Broken links, orphan pages
- TODO/placeholder markers
- User journey coverage

## Quality Metrics
| Metric | Weight | Criteria |
|--------|--------|----------|
| Accuracy | 25% | Claims verified, sources cited |
| Clarity | 25% | Scannable, examples present |
| Completeness | 25% | All sections, no TODOs |
| Structure | 25% | Follows quadrant template |

## Outputs
- `docs/_meta/analysis-report.md`

## Guardrails
- Read-only, stable IDs
- Source-grounded findings
