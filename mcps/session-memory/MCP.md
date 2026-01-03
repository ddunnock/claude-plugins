---
name: session-memory
description: Persistent session memory MCP server for Claude Desktop. Provides categorized event recording, searchable storage (SQLite + FTS5), automatic and manual checkpoints, session handoff summaries, and plugin architecture for skill-specific state tracking. Use when you need to persist session state across conversations for long-running tasks.
type: mcp
entry_point: server.py
dependencies:
  - mcp
config_file: config.json
---

# Session Memory MCP

Persistent session memory for Claude Desktop that survives context limits and session restarts.

## Features

- **Full conversation persistence**: Records all tool calls, decisions, findings, and questions
- **Searchable storage**: Query by category, time range, or keyword (SQLite + FTS5)
- **Hybrid checkpoints**: Auto-checkpoint every 5 minutes + manual checkpoints
- **Session handoff**: Generate markdown summaries for session transfer
- **Plugin architecture**: Skill-specific plugins for speckit-generator and specification-refiner

## Installation

After packaging, install to ~/.claude/ using:

```bash
python tools/install_mcp.py dist/session-memory.plugin
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

## Tools Provided

| Tool | Purpose |
|------|---------|
| `session_init` | Initialize session, optionally with skill/plugin |
| `session_record` | Record categorized event (tool_call, decision, finding, question) |
| `session_query` | Search by category, time range, keyword |
| `session_checkpoint` | Manual checkpoint with summary |
| `session_handoff` | Generate markdown handoff summary |
| `session_resume` | Resume from checkpoint |
| `session_list_checkpoints` | List available checkpoints |
| `session_status` | Current session stats and progress |

## Event Categories

| Category | Description |
|----------|-------------|
| `tool_call` | Tool invocations (Read, Write, Bash, etc.) |
| `tool_response` | Tool results |
| `decision` | Architectural/design decisions |
| `finding` | Analysis results, gaps, issues |
| `question` | Open/answered/deferred questions |
| `phase` | Workflow phase transitions |
| `checkpoint` | Checkpoint events |
| `custom` | Plugin-defined events |

## Plugin Architecture

The MCP includes a plugin system for skill-specific state tracking:

- **GenericPlugin**: Default plugin, tracks event counts and basic progress
- **SpecKitPlugin**: Tracks tasks, phases, commands for speckit-generator
- **SpecRefinerPlugin**: Tracks phases, findings, questions, assumptions for specification-refiner

Custom plugins can be created by extending `SessionPlugin` in `plugins/base.py`.

## Configuration

Edit `config.json`:

```json
{
  "auto_checkpoint_interval_minutes": 5,
  "auto_checkpoint_max_count": 10,
  "events_file": "storage/events.jsonl",
  "index_file": "storage/index.sqlite",
  "checkpoints_dir": "storage/checkpoints",
  "handoffs_dir": "handoffs"
}
```
