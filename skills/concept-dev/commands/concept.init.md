---
name: concept:init
description: Initialize a concept development session, create workspace, and detect available research tools
---

# /concept:init

Initialize a new concept development session.

## Procedure

### Step 1: Create Workspace

Run the init script to create the `.concept-dev/` workspace:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_session.py "$(pwd)"
```

If a session already exists, report the existing session details and ask:
- [A] Resume existing session (use `/concept:resume`)
- [B] Start fresh (archive existing `.concept-dev/` to `.concept-dev.bak.TIMESTAMP/`)

### Step 2: Detect Research Tools

Probe for available MCP research tools by attempting ToolSearch for each tier:

**Always Available:**
- WebSearch (built-in)
- WebFetch (built-in)

**Tier 1 (Free MCP — probe each):**
- `mcp__crawl4ai` — Deep web crawling
- `mcp__jina` — Document parsing
- `mcp__fetch` — MCP fetch
- `mcp__paper_search` — Academic papers

**Tier 2 (Configurable — probe each):**
- `mcp__tavily` — AI search
- `mcp__semantic_scholar` — Academic API
- `mcp__context7` — Documentation search

**Tier 3 (Premium — probe each):**
- `mcp__exa` — Neural search
- `mcp__perplexity` — Perplexity Sonar

For each tool, attempt a ToolSearch with `select:<tool_name>`. If found, mark as available. Record results in state.json using:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json set-tools --available [list of detected tools]
```

### Step 3: Display Session Banner

Present the initialization summary:

```
===================================================================
CONCEPT DEVELOPMENT SESSION
===================================================================

Session ID: [id]
Workspace: .concept-dev/
State: .concept-dev/state.json

-------------------------------------------------------------------
RESEARCH TOOLS
-------------------------------------------------------------------

Always Available:
  [+] WebSearch
  [+] WebFetch

Tier 1 (Free MCP):
  [+/-] crawl4ai          [detected/not found]
  [+/-] Jina Reader        [detected/not found]
  [+/-] MCP Fetch          [detected/not found]
  [+/-] Paper Search       [detected/not found]

Tier 2 (Configurable):
  [+/-] Tavily             [detected/not found]
  [+/-] Semantic Scholar   [detected/not found]
  [+/-] Context7           [detected/not found]

Tier 3 (Premium):
  [+/-] Exa                [detected/not found]
  [+/-] Perplexity Sonar   [detected/not found]

-------------------------------------------------------------------
PHASES
-------------------------------------------------------------------

  [ ] 1. Spit-Ball        /concept:spitball
  [ ] 2. Problem           /concept:problem
  [ ] 3. Black-Box         /concept:blackbox
  [ ] 4. Drill-Down        /concept:drilldown
  [ ] 5. Document          /concept:document

-------------------------------------------------------------------
Ready. Run /concept:spitball to begin ideation.
===================================================================
```

### Step 4: Prompt for Project Context (Optional)

Ask the user if they want to provide initial project context:

> Would you like to name this concept project and provide a brief description?
> This is optional — you can jump straight to `/concept:spitball` if you prefer.

If the user provides a name/description, update state.json:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json update session project_name "[name]"
```
