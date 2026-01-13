# Session Memory MCP Server

Persistent session memory for Claude Desktop that survives context limits and session restarts.

## Features

- **Full conversation persistence**: Records all tool calls, decisions, findings, and questions
- **Searchable storage**: Query by category, time range, or keyword (SQLite + FTS5)
- **Hybrid checkpoints**: Auto-checkpoint every 5 minutes + manual checkpoints
- **Session handoff**: Generate markdown summaries for session transfer
- **Plugin architecture**: Skill-specific plugins for speckit-generator and specification-refiner

## Installation

### Via Claude Code Plugin Marketplace (Recommended)

1. Enable the plugin in Claude Code settings
2. The MCP server is automatically configured

### Manual Installation

1. Ensure Python 3.10+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
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

## Environment Variables

The server automatically loads environment variables from `.env` files (requires `python-dotenv`):

| Priority | Location | Use Case |
|----------|----------|----------|
| 1 (highest) | Explicit env vars | CI/CD, MCP config `env` block |
| 2 | Project `.env` | Project-specific overrides |
| 3 (lowest) | `~/.claude/.env` | Global defaults |

### Supported Variables

```bash
# OpenAI - for semantic search embeddings (optional)
OPENAI_API_KEY=sk-your-key

# Cloudflare - for cloud sync (optional)
CF_ACCOUNT_ID=your-account-id
CF_API_TOKEN=your-api-token
CF_D1_DATABASE_ID=your-d1-database-id
CF_R2_BUCKET=your-r2-bucket-name
```

### Example `~/.claude/.env`

```bash
# Global defaults for all projects
OPENAI_API_KEY=sk-your-openai-key
CF_ACCOUNT_ID=your-cloudflare-account-id
CF_API_TOKEN=your-cloudflare-api-token
CF_D1_DATABASE_ID=your-d1-database-id
```

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

## Optional Features

All optional features degrade gracefully if dependencies are missing.

### Semantic Search (Embeddings)

Search session events using natural language with OpenAI embeddings.

**Setup:**
1. Install OpenAI SDK: `pip install openai`
2. Set `OPENAI_API_KEY` in your `.env` file
3. Enable in `config.json`:
   ```json
   "features": {
     "embeddings": {
       "enabled": true,
       "api_key_env": "OPENAI_API_KEY"
     }
   }
   ```

**Usage:**
```
session_semantic_search(query="authentication decisions", limit=5)
```

### Cloud Sync (Cloudflare D1)

Sync session data across devices using Cloudflare D1 (SQLite) and R2 (objects).

**Setup:**

1. Install httpx: `pip install httpx`

2. Create a Cloudflare API token with permissions:
   - `Account` → `D1` → `Edit`
   - `Account` → `Workers R2 Storage` → `Edit` (optional)

3. Create a D1 database:
   ```bash
   npx wrangler d1 create session-memory-sync
   ```

4. Add credentials to `~/.claude/.env`:
   ```bash
   CF_ACCOUNT_ID=your-account-id
   CF_API_TOKEN=your-api-token
   CF_D1_DATABASE_ID=your-database-id
   ```

5. Enable in `config.json`:
   ```json
   "features": {
     "cloud_sync": {
       "enabled": true,
       "account_id_env": "CF_ACCOUNT_ID",
       "api_token_env": "CF_API_TOKEN",
       "d1_database_id_env": "CF_D1_DATABASE_ID"
     }
   }
   ```

**Usage:**
```
sync_status()           # Check sync status
sync_push()             # Push local changes to cloud
sync_pull()             # Pull cloud changes to local
```

### Cross-Session Learning

Store and retrieve reusable patterns across sessions.

**Usage:**
```
# Search for relevant learnings
session_learn(query="error handling patterns", min_confidence=0.7)

# Create a new learning
learning_create(
    category="pattern",
    title="Retry with exponential backoff",
    description="Use exponential backoff for transient failures",
    confidence=0.8
)
```

### Knowledge Graph (Entities)

Track relationships between files, functions, decisions, and concepts.

**Usage:**
```
# Create an entity
entity_create(entity_type="function", name="handleAuth", qualified_name="src/auth.ts:handleAuth")

# Link entities
entity_link(source="handleAuth", target="JWT", relation_type="uses")

# Query the graph
entity_query(entity_type="function", related_to="authentication")
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
