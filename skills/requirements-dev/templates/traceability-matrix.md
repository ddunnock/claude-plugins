# Traceability Matrix

## Document Information
- **Project:** {{project_name}}
- **Version:** {{version}}
- **Date:** {{date}}

## Forward Traceability (Need to Requirement)

| Need ID | Need Statement | Requirement IDs | Coverage |
|---------|---------------|-----------------|----------|
{{#each needs}}
| {{id}} | {{statement}} | {{requirement_ids}} | {{coverage_status}} |
{{/each}}

## Backward Traceability (Requirement to Need)

| Requirement ID | Requirement Statement | Parent Need | Source |
|---------------|----------------------|-------------|--------|
{{#each requirements}}
| {{id}} | {{statement}} | {{parent_need}} | {{source}} |
{{/each}}

## Verification Traceability (Requirement to V&V)

| Requirement ID | V&V Method | Success Criteria | Status |
|---------------|------------|------------------|--------|
{{#each requirements}}
| {{id}} | {{vv_method}} | {{success_criteria}} | {{vv_status}} |
{{/each}}

## Coverage Summary

| Metric | Value |
|--------|-------|
| Total Needs | {{total_needs}} |
| Needs with Requirements | {{needs_covered}} |
| Orphan Requirements | {{orphan_count}} |
| Coverage Percentage | {{coverage_pct}}% |

## Gap Analysis

### Uncovered Needs
{{#each uncovered_needs}}
- **{{id}}:** {{statement}}
{{/each}}

### Orphan Requirements (no parent need)
{{#each orphan_requirements}}
- **{{id}}:** {{statement}}
{{/each}}
