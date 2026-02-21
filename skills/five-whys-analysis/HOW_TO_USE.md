# How to Use: Five Whys Analysis

The Five Whys Analysis skill conducts rigorous iterative root cause analysis with evidence validation, quality scoring, and countermeasure development.

## When to Use This Skill

- Simple to moderate complexity problems
- Single causal chain investigations
- Quick root cause identification
- Problems with clear cause-effect relationships
- As a drill-down after Fishbone or Pareto analysis

## Quick Start

State your problem and ask to run 5 Whys:

```
Help me run a 5 Whys analysis. Problem: "Customer order #12345
shipped 3 days late."
```

## How It Works

The skill guides you through iterative "Why?" questioning:

```
Problem: Order shipped 3 days late
  Why? → Warehouse didn't receive pick ticket on time
    Why? → Order wasn't released from ERP until Day 3
      Why? → Credit hold wasn't cleared
        Why? → Credit team wasn't notified of payment
          Why? → Payment notification process is manual
            ROOT CAUSE: No automated payment-to-credit notification
```

## Example Prompts

### Basic Analysis
```
Run a 5 Whys on: "The website was down for 2 hours yesterday."
```

### With Evidence Requirements
```
Help me do a rigorous 5 Whys analysis with evidence verification
for each step. Problem: "3 PCBs failed electrical test on Line 2."
```

### Continue an Existing Chain
```
I've gotten to "Why #3: The sensor wasn't calibrated" but I'm stuck.
Help me continue the analysis.
```

### Verify a Root Cause
```
I think the root cause is "lack of training." Help me verify if
this is truly the root cause or just a contributing factor.
```

## Quality Criteria

Each "Why" answer should be:

| Criterion | Good | Bad |
|-----------|------|-----|
| **Logical** | Directly causes the previous | Skips steps |
| **Specific** | Names exact thing | Vague or general |
| **Verifiable** | Can check with data/evidence | Opinion only |
| **Actionable** | Something you can change | External/uncontrollable |

## Validation Tests

The skill applies these tests:

1. **Therefore Test**: Read chain backwards with "therefore"
2. **Evidence Test**: Is each link supported by facts?
3. **Depth Test**: Did we reach process/system level?
4. **Actionability Test**: Can we control the root cause?

## Python Scripts

### Score an Analysis
```bash
python scripts/score_analysis.py --interactive
# or
python scripts/score_analysis.py --json '{"problem_definition": 4, "causal_chain_logic": 5, "evidence_basis": 3, "root_cause_depth": 4, "actionability": 4, "countermeasures": 3}'
```

### Generate Report
```bash
python scripts/generate_report.py --file analysis.json --output report.html
```

## Common Pitfalls

| Pitfall | Example | Solution |
|---------|---------|----------|
| Stopping too early | "Operator made a mistake" | Ask why the system allowed the mistake |
| Jumping to solution | "Need more training" | That's a solution, not a cause |
| Multiple causes per Why | "A and B caused it" | Split into separate chains |
| Person-blame | "John didn't check" | Focus on process, not person |
| Circular logic | A→B→C→A | Each step must be distinct |

## Scoring Dimensions

| Dimension | Weight | Focus |
|-----------|--------|-------|
| Problem Definition | 15% | Clarity of starting point |
| Causal Chain Logic | 25% | Logical connections |
| Evidence Basis | 20% | Factual support |
| Root Cause Depth | 20% | System/process level |
| Actionability | 10% | Within control |
| Countermeasures | 10% | Action quality |

**Passing score**: 70/100

## Related Resources

- `references/examples.md` - Worked examples
- `references/validation-tests.md` - How to verify root causes
- `assets/report-template.html` - Report template
