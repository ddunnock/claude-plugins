# Session Memory MCP Server

Persistent session memory for Claude Desktop that survives context limits and session restarts.

## Features

- **Full conversation persistence**: Records all tool calls, decisions, findings, and questions
- **Searchable storage**: Query by category, time range, or keyword (SQLite + FTS5)
- **Hybrid checkpoints**: Auto-checkpoint every 5 minutes + manual checkpoints
- **Session handoff**: Generate markdown summaries for session transfer
- **Plugin architecture**: Skill-specific plugins for speckit-generator and specification-refiner

## Installation

1. Ensure Python 3.10+ is installed
2. Install MCP SDK:
   ```bash
   pip install mcp
   ```

3. Add to Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json` or similar):
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

4. Restart Claude Desktop

## Usage

### Initialize a Session

```
session_init(skill_name="specification-refiner")
```

### Record Events

```
# Record a decision
session_record(
    category="decision",
    type="architecture",
    data={
        "title": "Use JWT for authentication",
        "rationale": "Stateless, scalable"
    }
)

# Record a finding
session_record(
    category="finding",
    type="gap",
    data={
        "severity": "HIGH",
        "description": "Missing error handling"
    }
)

# Record a question
session_record(
    category="question",
    type="clarification",
    data={
        "question": "Should we support OAuth?",
        "status": "open"
    }
)
```

### Query Events

```
# Get all decisions
session_query(category="decision")

# Search by keyword
session_query(keyword="authentication")

# Time range query
session_query(time_range={"after": "2025-01-01T00:00:00Z"})
```

### Create Checkpoints

```
# Manual checkpoint
session_checkpoint(name="pre-refactor", summary="About to restructure auth module")

# Auto-checkpoints happen every 5 minutes automatically
```

### Generate Handoff

```
# Create handoff summary when session is ending
session_handoff()
```

### Resume from Checkpoint

```
# Resume from latest
session_resume(use_latest=True)

# Resume from specific checkpoint
session_resume(checkpoint_name="pre-refactor")
```

### Check Status

```
session_status()
```

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

## Plugins

### Generic (Default)

Works with any skill. Tracks event counts and basic progress.

### SpecKit (speckit-generator)

Tracks:
- Commands (init, plan, tasks, implement)
- Task status (completed, pending, blocked, failed)
- Clarification sessions
- Findings

### Spec Refiner (specification-refiner)

Tracks:
- Phases (ASSESS, INGEST, ANALYZE, PRESENT, ITERATE, SYNTHESIZE, OUTPUT)
- Mode (SIMPLE/COMPLEX)
- Iterations
- Questions (open, answered, deferred)
- Findings by severity
- Assumptions

## Storage Structure

```
~/.claude/session-memory/
├── server.py              # MCP server
├── config.json            # Configuration
├── plugins/               # Plugin modules
├── storage/
│   ├── events.jsonl       # Append-only event log
│   ├── index.sqlite       # SQLite index for queries
│   └── checkpoints/
│       ├── auto/          # Rolling auto-checkpoints (max 10)
│       └── manual/        # Persistent manual checkpoints
└── handoffs/              # Generated handoff summaries
```

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

## Creating Custom Plugins

1. Create a new file in `plugins/`
2. Extend `SessionPlugin` base class
3. Implement required methods:
   - `name`: Plugin identifier
   - `supported_skills`: List of skill names
   - `get_state_schema`: JSON Schema for state
   - `calculate_progress`: Progress calculation
   - `generate_resumption_context`: Resumption logic

See `plugins/speckit.py` or `plugins/spec_refiner.py` for examples.
