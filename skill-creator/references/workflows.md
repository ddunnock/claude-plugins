# Workflow Patterns

Use these patterns when skills need structured, multi-step processes.

## Sequential Workflows

For complex tasks, break operations into clear, sequential steps. Provide an overview towards the beginning of SKILL.md:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

## Conditional Workflows

For tasks with branching logic, guide Claude through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

## Plan-Validate-Execute Pattern

For complex or risky operations, separate planning from execution:

```markdown
## Document modification workflow

1. **Plan phase**
   - Analyze the document structure
   - Identify all sections to modify
   - List proposed changes WITHOUT making them
   - Show the plan to the user for approval

2. **Validate phase**
   - Confirm prerequisites are met
   - Verify file permissions and format
   - Check for potential conflicts

3. **Execute phase**
   - Apply changes incrementally
   - Verify each change before proceeding
   - Generate summary of modifications
```

This pattern prevents wasted effort on incorrect approaches and gives users control over significant changes.

## Verifiable Intermediate Outputs

For multi-step processes, design workflows with checkpoints that can be verified:

```markdown
## Data pipeline workflow

1. Extract data → Output: `raw_data.json`
   - Verify: File exists and is valid JSON

2. Transform data → Output: `processed_data.json`
   - Verify: All required fields present

3. Load data → Output: confirmation message
   - Verify: Record count matches source
```

Each step produces an artifact that can be inspected before proceeding.

## Feedback Loops

For quality-critical tasks, include validation and correction cycles:

```markdown
## Report generation workflow

1. Generate initial report
2. Run `validate_report.py` to check:
   - Required sections present
   - Data accuracy
   - Formatting compliance
3. If validation fails:
   - Review error messages
   - Fix identified issues
   - Return to step 2
4. If validation passes:
   - Proceed to delivery
```

Include scripts that can programmatically verify output quality rather than relying solely on manual review.

## Checklists for Complex Tasks

For tasks with many requirements, provide explicit checklists:

```markdown
## Pre-deployment checklist

Before deploying, verify:
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number incremented
- [ ] Changelog entry added
- [ ] Security review completed
- [ ] Stakeholder approval obtained
```

Checklists ensure no steps are forgotten in complex workflows.
