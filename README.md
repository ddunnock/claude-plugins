# Claude Plugins

A collection of plugins that extend Claude's capabilities. Supports two plugin types:

- **Skills**: SKILL.md-based plugins with workflows, domain knowledge, and bundled resources
- **MCPs**: Model Context Protocol servers that provide tools for Claude Desktop

## Directory Structure

```
claude-plugins/
├── skills/                 # Skill plugins
│   ├── documentation-architect/
│   ├── research-opportunity-investigator/
│   ├── specification-refiner/
│   ├── speckit-generator/
│   ├── streaming-output/
│   └── trade-study-analysis/
├── mcps/                   # MCP server plugins
│   └── session-memory/
├── tools/                  # Packaging utilities
│   ├── init_plugin.py      # Create new plugins
│   ├── validate_plugin.py  # Validate plugins
│   ├── package_plugin.py   # Package for distribution
│   └── install_mcp.py      # Install MCPs to ~/.claude/
├── plugin-creator/         # Skill for creating plugins
└── dist/                   # Packaged .plugin files (gitignored)
```

## Plugin Types

### Skills

Skills provide workflows, procedures, and domain knowledge that Claude loads based on context. Each skill has:

- **SKILL.md**: Manifest with frontmatter (name, description) and instructions
- **scripts/**: Optional executable code
- **references/**: Optional documentation
- **assets/**: Optional files for output (templates, images)

### MCPs (Model Context Protocol)

MCPs provide tools that are always available in Claude Desktop. Each MCP has:

- **MCP.md**: Manifest with frontmatter (name, description, type, entry_point)
- **server.py**: MCP server implementation
- **config.json**: Optional configuration

## Quick Start

### Create a New Plugin

```bash
# Create a skill
python tools/init_plugin.py skill my-skill --path skills

# Create an MCP
python tools/init_plugin.py mcp my-mcp --path mcps
```

### Package a Plugin

```bash
python tools/package_plugin.py skills/my-skill
# Creates: my-skill.plugin
```

### Install an MCP

```bash
# From packaged file
python tools/install_mcp.py dist/session-memory.plugin

# From directory (symlink for development)
python tools/install_mcp.py mcps/session-memory --symlink
```

Then add to Claude Desktop config (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "session-memory": {
      "command": "python3",
      "args": ["~/.claude/session-memory/server.py"]
    }
  }
}
```

## Included Plugins

### Skills

| Skill | Description |
|-------|-------------|
| documentation-architect | Transform documentation using Diátaxis framework |
| research-opportunity-investigator | Research and opportunity investigation for protocols |
| specification-refiner | Refine and improve specifications |
| speckit-generator | Generate automation packages from requirements |
| streaming-output | Handle streaming output patterns |
| trade-study-analysis | Systematic trade study using DAU 9-Step Process |

### MCPs

| MCP | Description |
|-----|-------------|
| session-memory | Persistent session memory with searchable storage and checkpoints |

## Requirements

- Python 3.10+
- PyYAML: `pip install pyyaml`
- MCP SDK (for MCPs): `pip install mcp`
