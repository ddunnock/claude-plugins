# Verification Matrix

## Document Information
- **Project:** {{project_name}}
- **Version:** {{version}}
- **Date:** {{date}}

## Requirements by Verification Method

### Test
| Requirement ID | Statement | Test Type | Success Criteria | Responsible | Status |
|---------------|-----------|-----------|------------------|-------------|--------|
{{#each test_requirements}}
| {{id}} | {{statement}} | {{test_type}} | {{success_criteria}} | {{responsible}} | {{status}} |
{{/each}}

### Analysis
| Requirement ID | Statement | Analysis Method | Success Criteria | Responsible | Status |
|---------------|-----------|----------------|------------------|-------------|--------|
{{#each analysis_requirements}}
| {{id}} | {{statement}} | {{analysis_method}} | {{success_criteria}} | {{responsible}} | {{status}} |
{{/each}}

### Inspection
| Requirement ID | Statement | Inspection Type | Success Criteria | Responsible | Status |
|---------------|-----------|----------------|------------------|-------------|--------|
{{#each inspection_requirements}}
| {{id}} | {{statement}} | {{inspection_type}} | {{success_criteria}} | {{responsible}} | {{status}} |
{{/each}}

### Demonstration
| Requirement ID | Statement | Demo Scenario | Success Criteria | Responsible | Status |
|---------------|-----------|--------------|------------------|-------------|--------|
{{#each demonstration_requirements}}
| {{id}} | {{statement}} | {{demo_scenario}} | {{success_criteria}} | {{responsible}} | {{status}} |
{{/each}}

## V&V Status Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Planned | {{planned_count}} | {{planned_pct}}% |
| In Progress | {{in_progress_count}} | {{in_progress_pct}}% |
| Passed | {{passed_count}} | {{passed_pct}}% |
| Failed | {{failed_count}} | {{failed_pct}}% |
| Waived | {{waived_count}} | {{waived_pct}}% |
