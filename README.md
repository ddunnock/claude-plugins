# Claude Plugins

A collection of plugins that extend Claude's capabilities. Supports two plugin types:

- **Skills**: SKILL.md-based plugins with workflows, domain knowledge, and bundled resources
- **MCPs**: Model Context Protocol servers that provide tools for Claude Desktop

## Directory Structure

```
claude-plugins/
├── skills/                 # Skill plugins (18 skills)
│   ├── concept-dev/
│   ├── documentation-architect/
│   ├── fault-tree-analysis/
│   ├── fishbone-diagram/
│   ├── five-whys-analysis/
│   ├── fmea-analysis/
│   ├── kepner-tregoe-analysis/
│   ├── pareto-analysis/
│   ├── plugin-creator/
│   ├── problem-definition/
│   ├── rcca-master/
│   ├── requirements-dev/
│   ├── research-opportunity-investigator/
│   ├── specification-refiner/
│   ├── speckit-generator/
│   ├── streaming-output/
│   ├── streaming-output-mcp/
│   └── trade-study-analysis/
├── mcps/                   # MCP server plugins
│   ├── knowledge-mcp/
│   └── session-memory/
├── tools/                  # Packaging utilities
│   ├── init_plugin.py      # Create new plugins
│   ├── validate_plugin.py  # Validate plugins
│   ├── package_plugin.py   # Package for distribution
│   └── install_mcp.py      # Install MCPs to ~/.claude/
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

- **.claude-plugin/plugin.json**: Manifest with name, description, and server configuration
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

#### Root Cause Analysis & Quality (8 skills)

| Skill | Description |
|-------|-------------|
| rcca-master | Orchestrate RCCA investigations using 8D methodology with integrated tool selection |
| problem-definition | 5W2H and IS/IS NOT analysis for precise problem statements |
| five-whys-analysis | Root cause analysis with guided questioning and quality scoring |
| fishbone-diagram | Ishikawa cause-and-effect diagrams with 6Ms/8Ps/4Ss categories |
| pareto-analysis | 80/20 Rule analysis for prioritizing vital few causes |
| kepner-tregoe-analysis | KT Problem Solving and Decision Making (Situation/Problem/Decision/Potential Problem Analysis) |
| fault-tree-analysis | Boolean logic analysis for system failure pathways and minimal cut sets |
| fmea-analysis | Failure Mode and Effects Analysis (DFMEA/PFMEA) using AIAG-VDA methodology |

#### Specification & Documentation (4 skills)

| Skill | Description |
|-------|-------------|
| speckit-generator | Project specification and task management with PLANS taxonomy, ADR decisions, SMART criteria, anti-pattern detection |
| specification-refiner | SEAMS framework analysis with sequential clarification and multi-phase workflow |
| documentation-architect | Transform documentation using the Diátaxis framework |
| research-opportunity-investigator | Research and opportunity investigation for protocols |

#### Concept & Requirements Development (2 skills)

| Skill | Description |
|-------|-------------|
| concept-dev | NASA Phase A concept development lifecycle: ideation, problem definition, black-box architecture, drill-down with gap analysis, and document generation with cited research |
| requirements-dev | INCOSE-compliant requirements development with hybrid quality checking (16 deterministic + 9 semantic rules), verification planning, bidirectional traceability, and ReqIF export |

#### Decision Support (1 skill)

| Skill | Description |
|-------|-------------|
| trade-study-analysis | Systematic trade study using DAU 9-Step Process with sensitivity analysis |

#### Output & Streaming (2 skills)

| Skill | Description |
|-------|-------------|
| streaming-output | Stream long-form content to markdown files with resume capability |
| streaming-output-mcp | Stream structured content to SQLite with multi-format export (Markdown, HTML, JSON, YAML, CSV) |

#### Development (1 skill)

| Skill | Description |
|-------|-------------|
| plugin-creator | Generate Claude plugins from user prompts with documentation and testing |

### MCPs

| MCP | Description |
|-----|-------------|
| session-memory | Persistent session memory with searchable storage, checkpoints, semantic search, and cloud sync |
| knowledge-mcp | Semantic search over systems engineering standards (IEEE, INCOSE, ISO) with RAG capabilities |

## Requirements

- Python 3.10+
- PyYAML: `pip install pyyaml`
- MCP SDK (for MCPs): `pip install mcp`
