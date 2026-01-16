# Reference

**Information-oriented** documentation that provides technical descriptions of the machinery.

## Purpose

Reference documentation describes what things are and how they work. It's designed for users who know what they're looking for and need accurate, complete information.

## Writing Guidelines

- **Be consistent**: Use the same structure for similar items
- **Be complete**: Document all options, parameters, and behaviors
- **Be accurate**: Keep docs in sync with the actual implementation
- **Be concise**: State facts without instructional narrative
- **Organize logically**: Group related items; use alphabetical order within groups

## Template for API/Function Reference

```markdown
# [Function/API Name]

[One-line description]

## Signature

`function_name(param1, param2, options)`

## Parameters

| Name     | Type   | Required  | Description                 |
|----------|--------|-----------|-----------------------------|
| `param1` | string | Yes       | [Description]               |
| `param2` | number | No        | [Description]. Default: `0` |

## Returns

[Return type and description]

## Example

[Minimal working example]

## Notes

- [Important behavior or edge cases]
```

## Template for Configuration Reference

```markdown
# [Configuration Section]

## Options

### `option_name`

- **Type**: string
- **Default**: `"default_value"`
- **Description**: [What this option controls]

### `another_option`

- **Type**: boolean
- **Default**: `false`
- **Description**: [What this option controls]
```

## Contents

- **[Architecture Reference](interface-requirements-specification.md)** - Complete project structure, CLI, MCP servers, daemon, and IDE integration
