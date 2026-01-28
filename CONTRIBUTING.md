# Contributing to Claude Plugins

Thank you for your interest in contributing to Claude Plugins! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Creating New Plugins](#creating-new-plugins)
- [Git Workflow](#git-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Code Style](#code-style)

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [PyYAML](https://pypi.org/project/PyYAML/) for YAML processing
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) for MCP server development

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dunnock/claude-plugins.git
   cd claude-plugins
   ```

2. Install dependencies for MCP servers:
   ```bash
   cd mcps/session-memory
   pip install -e .
   ```

3. Configure environment variables as needed (see individual plugin READMEs).

## Project Structure

### Skills

Skills are located in the `skills/` directory. Each skill follows this structure:

```
skills/<skill-name>/
├── .claude-plugin/
│   └── plugin.json      # Plugin manifest
├── SKILL.md             # Main skill instructions (loaded by Claude)
├── scripts/             # Optional automation scripts
├── references/          # Optional reference documents
└── assets/              # Optional images, diagrams, etc.
```

#### plugin.json

```json
{
  "name": "skill-name",
  "description": "Brief description of what the skill does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  },
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "skills": {
    "skill-name": "SKILL.md"
  }
}
```

#### SKILL.md

The main skill file that Claude loads. Should include:

- Clear description of the skill's purpose
- Step-by-step instructions or workflow
- Examples where appropriate
- Any constraints or considerations

### MCP Servers

MCP servers are located in the `mcps/` directory:

```
mcps/<server-name>/
├── .claude-plugin/
│   └── plugin.json      # Plugin manifest with mcpServers config
├── src/
│   └── <package>/
│       ├── __init__.py
│       ├── __main__.py
│       └── server.py    # MCP server implementation
├── tests/
├── pyproject.toml
└── README.md
```

## Creating New Plugins

Use the plugin initialization tool:

```bash
python tools/init_plugin.py <plugin-name> --type skill
# or
python tools/init_plugin.py <plugin-name> --type mcp
```

This creates the necessary directory structure and template files.

### Skill Development Tips

1. **Be specific**: Skills work best when they have a clear, focused purpose
2. **Include examples**: Show Claude what good output looks like
3. **Structure workflows**: Break complex tasks into numbered steps
4. **Reference external resources**: Link to relevant documentation or standards

### MCP Server Development Tips

1. **Follow MCP SDK patterns**: Use the official SDK for consistency
2. **Implement proper error handling**: Return structured error responses
3. **Document tools thoroughly**: Include descriptions for all tool parameters
4. **Add type hints**: Use Python type hints throughout

## Git Workflow

### Branch Naming

Use descriptive branch names with prefixes:

```
feature/<description>    # New features
fix/<description>        # Bug fixes
docs/<description>       # Documentation updates
refactor/<description>   # Code refactoring
chore/<description>      # Maintenance tasks
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `style`: Code style changes (formatting, etc.)

Examples:
```
feat(rcca-master): add fishbone diagram integration
fix(session-memory): handle empty checkpoint names
docs(readme): update installation instructions
test(knowledge-mcp): add semantic search tests
```

### Pull Requests

1. Create a feature branch from `main`
2. Make your changes with clear commits
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a pull request with a clear description

## Testing Guidelines

### Skills

Skills should be tested manually by:

1. Installing the plugin in Claude Code
2. Invoking the skill with various inputs
3. Verifying the output matches expectations

### MCP Servers

MCP servers should have automated tests:

```bash
cd mcps/<server-name>
pytest --cov=src --cov-report=term-missing
```

Aim for:
- 80% line coverage minimum
- Unit tests for core logic
- Integration tests for MCP tool handlers

## Code Style

### Python

- Use type hints for all function signatures
- Follow PEP 8 guidelines
- Use docstrings for public functions and classes
- Run `ruff` for linting:
  ```bash
  ruff check .
  ruff format .
  ```

### Markdown

- Use ATX-style headers (`#`, `##`, etc.)
- Include code blocks with language identifiers
- Keep lines under 100 characters where practical

## Questions?

If you have questions about contributing, please open an issue on GitHub.

---

Thank you for contributing!
