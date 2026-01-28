# Plugin Creator

A Claude Code skill for creating Claude plugins (skills and MCPs).

## What This Skill Does

This skill guides Claude through the process of creating Claude Code plugins. It supports:

- **Skills**: SKILL.md-based plugins with optional scripts, references, and assets
- **MCPs**: Model Context Protocol servers that provide tools to Claude Desktop

## Structure

```
plugin-creator/
├── SKILL.md              # Main skill documentation (loaded when triggered)
├── references/
│   ├── workflows.md      # Workflow patterns (sequential, conditional, etc.)
│   ├── output-patterns.md    # Template and examples patterns
│   └── validation-checklist.md   # Quality checklist before packaging
└── scripts/
    ├── init_skill.py     # Initialize new skill from template
    ├── package_skill.py  # Package skill into .skill file
    └── quick_validate.py # Validate skill structure
```

## Scripts

### init_skill.py

Creates a new skill directory with template files:

```bash
python scripts/init_skill.py <skill-name> --path <directory>

# Example
python scripts/init_skill.py my-new-skill --path skills/
```

### package_skill.py

Validates and packages a skill into a distributable `.skill` file:

```bash
python scripts/package_skill.py <path/to/skill> [output-directory]

# Example
python scripts/package_skill.py skills/my-skill dist/
```

**Requires**: PyYAML (`pip install pyyaml`)

### quick_validate.py

Validates skill structure and frontmatter:

```bash
python scripts/quick_validate.py <skill-directory>
```

Checks:
- SKILL.md exists with valid YAML frontmatter
- Name follows hyphen-case convention (max 64 chars)
- Name matches directory name
- Description exists (max 1024 chars, no angle brackets)
- No reserved words (anthropic, claude) in name

## Key Concepts

**Progressive Disclosure**: Skills use a three-level loading system:
1. Metadata (name + description) - always in context
2. SKILL.md body - when skill triggers
3. Bundled resources - as needed

**Degrees of Freedom**: Match constraints to task fragility:
- High freedom (text guidance) for contextual decisions
- Medium freedom (pseudocode/parameterized scripts) for preferred patterns
- Low freedom (specific scripts) for fragile operations

## Reference Files

| File                      | Purpose                                                 |
|---------------------------|---------------------------------------------------------|
| `workflows.md`            | Sequential, conditional, plan-validate-execute patterns |
| `output-patterns.md`      | Template and examples patterns for consistent output    |
| `validation-checklist.md` | Pre-packaging quality checklist                         |