# User Documentation Section Template

Use this template for organizing `docs/user/` content following Diataxis framework.

---

## Directory Structure

```
docs/user/
├── getting-started/          # TUTORIALS (Learning-oriented)
│   ├── index.md              # Section overview
│   ├── quickstart.md         # 5-minute first experience
│   ├── installation.md       # Detailed installation options
│   └── first-project.md      # Guided first project
│
├── guides/                   # HOW-TO (Task-oriented)
│   ├── index.md              # Guide directory
│   └── {task-name}.md        # One guide per task
│
├── concepts/                 # EXPLANATION (Understanding-oriented)
│   ├── index.md              # Concepts overview
│   └── {concept-name}.md     # One doc per concept
│
└── reference/                # REFERENCE (Information-oriented)
    ├── index.md              # Reference overview
    ├── configuration.md      # All config options
    └── cli.md                # CLI commands (if applicable)
```

---

## getting-started/quickstart.md Template

```markdown
# Quick Start

Get up and running with {PROJECT_NAME} in 5 minutes.

## Prerequisites

- {Requirement 1}
- {Requirement 2}

## Installation

```bash
{install command}
```

## Your First {Thing}

{Step 1: Do this}

```{language}
// Code for step 1
```

{Step 2: Do this}

```{language}
// Code for step 2
```

## Verify It Works

{How to confirm success}

```bash
{verification command}
```

Expected output:
```
{expected result}
```

## Next Steps

- [Full Installation Guide](installation.md) - More installation options
- [First Project](first-project.md) - Guided walkthrough
- [Guides](../guides/) - How to accomplish specific tasks
```

---

## guides/{task}.md Template

```markdown
# How to {Task Name}

{One sentence describing what this guide helps you accomplish.}

## Prerequisites

- {What you need before starting}
- See: [Related Guide](link) if needed

## Steps

### 1. {First Step}

{Explanation}

```{language}
// Code
```

### 2. {Second Step}

{Explanation}

```{language}
// Code
```

## Verification

{How to confirm the task is complete}

## Common Issues

### {Issue 1}

**Symptom**: {What you see}
**Solution**: {How to fix}

## Related

- [Another Guide](other-guide.md)
- [Relevant Concept](../concepts/concept.md)
```

---

## concepts/{concept}.md Template

```markdown
# {Concept Name}

{Opening paragraph explaining what this concept is and why it matters.}

## Why {Concept}?

{Background and motivation - why does this exist?}

## How It Works

{Explanation of the mechanism or principle.}

### {Sub-topic 1}

{Detailed explanation}

### {Sub-topic 2}

{Detailed explanation}

## In Practice

{Concrete examples of how this concept applies.}

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| {Option 1} | {Benefits} | {Drawbacks} |
| {Option 2} | {Benefits} | {Drawbacks} |

## Related Concepts

- [{Related Concept 1}](related-1.md)
- [{Related Concept 2}](related-2.md)
```

---

## reference/configuration.md Template

```markdown
# Configuration Reference

Complete reference for all configuration options.

## Configuration File

{PROJECT_NAME} uses `{config-file}` for configuration.

```{format}
# Example configuration
{example}
```

## Options

### {Section Name}

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `{key}` | {type} | `{default}` | {description} |
| `{key}` | {type} | `{default}` | {description} |

#### `{option.name}`

{Detailed explanation if needed.}

**Example**:
```{format}
{example}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `{VAR_NAME}` | `{default}` | {description} |

## Configuration Precedence

1. Command-line arguments (highest)
2. Environment variables
3. Configuration file
4. Default values (lowest)
```

---

## Guidelines by Quadrant

### Tutorials (getting-started/)
- Learning-oriented
- Show the user what's possible
- Lead by following, not explaining
- Focus on confidence building

### How-To Guides (guides/)
- Task-oriented
- Solve specific problems
- Assume some knowledge
- Be direct and practical

### Explanation (concepts/)
- Understanding-oriented
- Explain background and context
- Discuss alternatives and trade-offs
- Connect ideas together

### Reference (reference/)
- Information-oriented
- Describe the machinery
- Be accurate and complete
- Consistent structure
