# How to Use: RCCA Master

The RCCA Master skill orchestrates complete 8D (Eight Disciplines) investigations for root cause analysis and corrective action.

## When to Use This Skill

- Conducting formal RCCA/8D investigations
- Customer complaint root cause analysis
- Manufacturing defect investigations
- Field failure analysis
- Quality escape investigations
- Nonconformance analysis

## Quick Start

Simply describe your problem and ask for help with an 8D investigation:

```
I need to investigate a quality issue. We've had 3 customer complaints
about cracked connector housings in the past month. Can you help me
run an 8D investigation?
```

## Workflow Overview

The skill guides you through all 8 disciplines:

| Phase | Purpose | Key Output |
|-------|---------|------------|
| D0 | Initial Assessment | Severity, urgency, complexity classification |
| D1 | Team Formation | Cross-functional team with roles |
| D2 | Problem Definition | 5W2H analysis, IS/IS NOT, problem statement |
| D3 | Containment | Interim actions to protect customer |
| D4 | Root Cause Analysis | Verified root cause(s) |
| D5 | Corrective Action | Permanent corrective actions |
| D6 | Implementation | Action execution and verification |
| D7 | Prevention | Systemic improvements |
| D8 | Closure | Effectiveness verification, lessons learned |

## Example Prompts

### Start a New Investigation
```
Help me start an 8D investigation for a software deployment failure
that caused 2 hours of downtime last Tuesday.
```

### Resume at a Specific Phase
```
We've completed D1-D3 for our connector housing issue. The team is
formed, problem is defined, and containment is in place. Now I need
help with D4 root cause analysis.
```

### Get Tool Recommendations
```
For our recurring PCB solder defect issue, which root cause analysis
tool should we use - 5 Whys, Fishbone, or Pareto?
```

## Integration with Other Skills

RCCA Master automatically invokes specialized skills:

- **problem-definition** → For D2 (5W2H + IS/IS NOT)
- **five-whys-analysis** → For simple/moderate D4 analysis
- **fishbone-diagram** → For brainstorming potential causes
- **pareto-analysis** → For prioritizing defect categories
- **fault-tree-analysis** → For safety-critical/system failures
- **fmea-analysis** → For risk assessment of failure modes

## Python Scripts

### Initialize a Session
```bash
python scripts/initialize_8d.py --interactive
# or
python scripts/initialize_8d.py --id "8D-2025-001" --title "Cracked Connector" --output session.json
```

### Generate Final Report
```bash
python scripts/generate_8d_report.py --input session.json --output report.html
```

### Score Investigation Quality
```bash
python scripts/score_8d.py --file session.json
# or interactive
python scripts/score_8d.py --interactive
```

## Tips for Best Results

1. **Complete D0 first** - Proper assessment drives team composition and tool selection
2. **Don't skip gates** - Each phase has a quality gate checkpoint
3. **Verify root causes** - D4 requires evidence-based verification before proceeding
4. **Document everything** - Use the session JSON to track progress
5. **Close properly** - D8 verification period confirms effectiveness

## Related Resources

- `references/examples.md` - Worked 8D examples
- `references/common-pitfalls.md` - Mistakes to avoid
- `references/quality-rubric.md` - Scoring criteria
- `references/team-formation-guide.md` - Role definitions
- `references/tool-selection-guide.md` - When to use which analysis tool
