# How to Use: Pareto Analysis

The Pareto Analysis skill applies the 80/20 rule to identify the vital few causes driving the majority of problems, with chart generation, cumulative analysis, and prioritization guidance.

## When to Use This Skill

- Prioritizing which defects/issues to address first
- When you have categorical data with counts/costs
- Identifying the "vital few" vs "trivial many"
- Resource allocation decisions
- Before deep-diving with 5 Whys (analyze top categories)

## Quick Start

Provide your data and request a Pareto analysis:

```
Help me do a Pareto analysis on our defect data:
- Scratches: 45 occurrences
- Dents: 32 occurrences
- Discoloration: 28 occurrences
- Cracks: 15 occurrences
- Other: 10 occurrences
```

## The 80/20 Principle

Pareto analysis typically reveals that:
- **~20% of causes** account for **~80% of effects**
- Focus on the vital few for maximum impact
- The "trivial many" can be addressed later or accepted

## Example Prompts

### Basic Analysis
```
Create a Pareto chart for customer complaint categories:
Late delivery (87), Wrong item (45), Damaged (38), Missing parts (22), Other (18)
```

### Cost-Weighted Analysis
```
Do a Pareto analysis weighted by cost:
- Rework: 120 occurrences × $50 each
- Scrap: 45 occurrences × $200 each
- Returns: 30 occurrences × $150 each
- Warranty: 15 occurrences × $500 each
```

### With Trend Comparison
```
Compare this month's Pareto to last month's:
This month: A=50, B=40, C=30, D=20
Last month: A=60, B=25, C=35, D=15
```

### Identify Vital Few
```
Given this defect data, which categories should we focus our
8D investigation on? [provide data]
```

## Analysis Phases

| Phase | Activity | Output |
|-------|----------|--------|
| 1 | Scope definition | What to measure, time period |
| 2 | Data collection | Categorized counts or costs |
| 3 | Chart construction | Sorted bars + cumulative line |
| 4 | Analysis | Identify vital few (typically top 2-3) |
| 5 | Documentation | Report with recommendations |

## Measurement Types

| Type | When to Use | Example |
|------|-------------|---------|
| **Frequency** | Count matters most | Defect occurrences |
| **Cost** | Financial impact key | Warranty costs |
| **Time** | Duration matters | Downtime hours |
| **Weighted** | Multiple factors | Frequency × Severity |

## Python Scripts

### Generate Pareto Chart (SVG)
```bash
python scripts/generate_chart.py --file data.json --output pareto.svg
```

### Generate Report
```bash
python scripts/generate_report.py --file data.json --format html --output report.html
```

### Calculate Statistics
```bash
python scripts/calculate_stats.py --file data.json
# Output: cumulative %, vital few identification, recommendations
```

## Reading the Chart

```
100% ─────────────────────────────●
                              ●
 80% ─────────────────────●
                      ●
 60% ─────────────●
              ●
 40% ─────●
      ●
 20% ●
     ├────┬────┬────┬────┬────┤
     Cat A  B    C    D    E
     [===][===][==][=][=]  ← Bars (frequency)

     ● Cumulative line
     ─── 80% threshold
```

**Vital Few**: Categories before the cumulative line crosses 80%

## Quality Checklist

- [ ] Categories are mutually exclusive
- [ ] Data covers representative time period
- [ ] Measurement type matches business need
- [ ] "Other" category is <10% of total
- [ ] Top 2-3 categories identified for action

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Too many categories | Chart is cluttered | Combine small categories into "Other" |
| Wrong measurement | Frequency when cost matters | Choose measurement type deliberately |
| "Other" too large | Hides important causes | Break down "Other" further |
| Single snapshot | Misses trends | Compare multiple time periods |

## Integration with Other Tools

**Pareto → Fishbone → 5 Whys**:
1. Pareto identifies top categories
2. Fishbone brainstorms causes within top categories
3. 5 Whys drills to root cause

## Related Resources

- `references/interpretation-guide.md` - Reading Pareto charts
- `references/data-collection-tips.md` - Getting good data
- `assets/chart-template.svg` - Blank template
