# How to Use: Fishbone Diagram

The Fishbone Diagram skill creates Ishikawa (Cause-and-Effect) diagrams for structured brainstorming of potential causes, with category frameworks, prioritization, and visual output.

## When to Use This Skill

- Brainstorming all possible causes of a problem
- Team-based root cause sessions
- When multiple cause categories may contribute
- Before narrowing down with 5 Whys or Pareto
- Visualizing cause-effect relationships

## Quick Start

Describe your problem and request a fishbone analysis:

```
Help me create a fishbone diagram for: "High scrap rate on
injection molding line 4."
```

## Category Frameworks

### 6Ms (Manufacturing)
- **Man** - People, skills, training
- **Machine** - Equipment, tools, maintenance
- **Method** - Procedures, work instructions
- **Material** - Raw materials, components
- **Measurement** - Gauges, inspection, data
- **Mother Nature** - Environment, conditions

### 8Ps (Service/Process)
- **People** - Staff, skills, availability
- **Process** - Procedures, workflow
- **Product** - Service/product delivered
- **Place** - Location, facilities
- **Price** - Cost factors
- **Promotion** - Communication, information
- **Physical Evidence** - Tangible elements
- **Policies** - Rules, regulations

### 4Ss (Service)
- **Surroundings** - Environment
- **Suppliers** - External inputs
- **Systems** - IT, processes
- **Skills** - Capabilities

### Custom Categories
You can define problem-specific categories.

## Example Prompts

### Manufacturing Problem
```
Create a fishbone diagram using 6Ms for: "Surface finish defects
on machined parts."
```

### Service Problem
```
Help me build an 8Ps fishbone for: "Customer wait times exceed
15 minutes at our service desk."
```

### With Team Input
```
I have a team brainstorming session. Guide us through building
a fishbone for "Software deployment failures" and help us
prioritize the causes.
```

### Drill Down on a Branch
```
In our fishbone, "Machine" has several causes. Help me drill
deeper into "Spindle vibration" with sub-causes.
```

## Workflow Phases

| Phase | Activity | Output |
|-------|----------|--------|
| 1 | Define problem | Clear effect statement |
| 2 | Select categories | 6Ms, 8Ps, 4Ss, or custom |
| 3 | Brainstorm causes | Primary causes per category |
| 4 | Drill sub-causes | 2-3 levels of "why" |
| 5 | Prioritize | Multi-voting or ranking |
| 6 | Document | Diagram + report |

## Python Scripts

### Generate SVG Diagram
```bash
python scripts/generate_diagram.py --file fishbone_data.json --output diagram.svg
```

### Generate HTML Report
```bash
python scripts/generate_report.py --file fishbone_data.json --format html --output report.html
```

### Interactive Session
```bash
python scripts/run_session.py --interactive
```

## Prioritization Methods

After brainstorming, prioritize causes using:

1. **Multi-voting** - Each person gets N votes to distribute
2. **Impact/Likelihood Matrix** - Plot causes on 2x2
3. **Pareto Integration** - If data exists, use Pareto analysis
4. **SME Ranking** - Expert judgment scoring

## Quality Checklist

- [ ] Problem statement is specific and neutral
- [ ] Categories are appropriate for domain
- [ ] Each category has 3-7 potential causes
- [ ] Sub-causes drill at least 2 levels
- [ ] Team has prioritized top 3-5 causes
- [ ] Priority causes have evidence or data support

## Tips for Effective Sessions

1. **Use a facilitator** - Someone to guide, not contribute
2. **No criticism during brainstorm** - Capture all ideas first
3. **Build on others' ideas** - "And also..." not "But..."
4. **Time-box categories** - 5-7 minutes each
5. **Vote silently** - Avoid groupthink in prioritization

## Visual Output

The skill generates:
- **SVG diagram** - Clean vector graphic
- **HTML report** - Full documentation with prioritization
- **JSON data** - Structured data for further analysis

## Related Resources

- `references/category-guide.md` - When to use which framework
- `references/facilitation-tips.md` - Running effective sessions
- `assets/diagram-template.svg` - Blank template
