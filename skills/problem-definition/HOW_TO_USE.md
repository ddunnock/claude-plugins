# How to Use: Problem Definition

The Problem Definition skill guides structured problem analysis using 5W2H and IS/IS NOT frameworks to create clear, measurable problem statements.

## When to Use This Skill

- Starting any root cause investigation
- Writing D2 sections of 8D reports
- Defining scope for quality investigations
- Clarifying vague problem descriptions
- Avoiding embedded causes or solutions in problem statements

## Quick Start

Describe your problem and ask for help defining it:

```
Help me define this problem: "The machine keeps breaking down and
production is behind schedule."
```

## Framework Overview

### 5W2H Analysis

| Dimension | Question |
|-----------|----------|
| WHAT | What object/product? What defect/failure? |
| WHERE | Where geographically? Where on the object? |
| WHEN | When did it start? When in the lifecycle? |
| WHO | Who is affected? Who detected it? |
| HOW | How was it detected? |
| HOW MUCH | Magnitude? Frequency? Trend? |

### IS / IS NOT Analysis

Sharpens focus by contrasting what IS happening with what IS NOT:

| IS | IS NOT |
|-----|--------|
| Part A fails | Part B (similar) doesn't fail |
| Line 3 only | Lines 1, 2, 4 unaffected |
| After 6 months | Not in first 6 months |

## Example Prompts

### Full Problem Definition
```
I need to define this problem for an 8D: "Customers are complaining
about our product quality." Help me work through 5W2H and IS/IS NOT.
```

### Validate Existing Statement
```
Is this problem statement good? "The assembly line has issues because
operators aren't following the work instructions properly."
```

### Improve a Vague Statement
```
Make this more specific: "There are too many defects in production."
```

### Focus on Deviation
```
Help me write a deviation statement. Expected: 99.5% yield.
Actual: 94.2% yield on PCB assembly line 3.
```

## Anti-Patterns to Avoid

The skill will flag these issues:

| Anti-Pattern | Example | Problem |
|--------------|---------|---------|
| Embedded cause | "...because of operator error" | Assumes cause before investigation |
| Embedded solution | "...needs more training" | Jumps to solution |
| Person-blame | "John forgot to..." | Blames individual, not system |
| Vague terms | "sometimes", "many", "issues" | Not measurable |

## Python Scripts

### Validate a Problem Statement
```bash
python scripts/validate_statement.py "Your problem statement here"
# or from file
python scripts/validate_statement.py --file definition.json
```

### Generate a Report
```bash
python scripts/generate_report.py --file definition.json --format html --output report.html
python scripts/generate_report.py --file definition.json --format markdown
```

### Score Definition Quality
```bash
python scripts/score_analysis.py --interactive
# or with JSON
python scripts/score_analysis.py --json '{"completeness": 4, "specificity": 3, "measurability": 4, "neutrality": 5}'
```

## Quality Criteria

A good problem statement:

- [ ] **Specific** - Names exact product, location, timeframe
- [ ] **Measurable** - Includes quantities, percentages, counts
- [ ] **Bounded** - Clear scope via IS/IS NOT
- [ ] **Neutral** - No embedded cause, solution, or blame
- [ ] **Deviation-based** - States expected vs. actual

## Example Output

**Before**: "The machine keeps breaking down"

**After**: "CNC Mill #3 in Building A experienced 7 unplanned stops due to spindle bearing failure between Jan 15-31, 2025, resulting in 14 hours of downtime. Expected: 0 unplanned stops. Similar mills (#1, #2, #4) had 0 spindle failures in the same period."

## Related Resources

- `references/5w2h-guide.md` - Detailed dimension guidance
- `references/is-isnot-examples.md` - IS/IS NOT examples by domain
