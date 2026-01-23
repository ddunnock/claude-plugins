# Architecture

**Analysis Date:** 2026-01-23

## Pattern Overview

**Overall:** Multi-plugin platform with two plugin types (Skills and MCPs) managed through a unified packaging and distribution system.

**Key Characteristics:**
- Skills: SKILL.md-based workflows with domain knowledge, executable scripts, and templates
- MCPs: Python-based Model Context Protocol servers providing runtime tools to Claude Desktop
- Shared packaging infrastructure: Validation, packaging (.plugin zip format), installation utilities
- Plugin registry structure for discovery and configuration
- State management via memory files (analysis-state.md) for stateful skills

## Layers

**Plugin Definition Layer:**
- Purpose: Define what each plugin does and how to invoke it
- Location: `skills/*/SKILL.md`, `mcps/*/MCP.md`
- Contains: YAML frontmatter (name, description, entry points) + markdown instructions
- Depends on: None (declarative)
- Used by: Plugin validator, packager, installer

**Skill Runtime Layer:**
- Purpose: Execute domain-specific workflows with persistent memory
- Location: `skills/*/` directories (scripts, references, assets, commands)
- Contains: Markdown workflows, Python scripts, reference documentation, templates
- Depends on: Session memory MCP, Claude Desktop environment
- Used by: Claude during contextual skill loading

**MCP Server Layer:**
- Purpose: Provide tools and resources for Claude Desktop
- Location: `mcps/*/server.py`, `mcps/*/plugins/`, `mcps/*/modules/`
- Contains: MCP SDK implementation, tool definitions, optional feature modules
- Depends on: MCP SDK, feature libraries (OpenAI, Cloudflare)
- Used by: Claude Desktop via stdio protocol

**Feature Modules (MCP Layer):**
- Purpose: Provide optional capabilities (embeddings, cloud sync, learning, entities)
- Location: `mcps/session-memory/modules/*`
- Contains: Service classes for specialized features
- Depends on: External APIs (OpenAI, Cloudflare), database
- Used by: Session memory server with graceful degradation

**Plugin Infrastructure Layer:**
- Purpose: Package, validate, distribute plugins
- Location: `tools/*`, `dist/`
- Contains: Python CLI tools (init_plugin.py, validate_plugin.py, package_plugin.py, install_mcp.py)
- Depends on: PyYAML, zipfile
- Used by: Developers packaging/installing plugins

**Storage Layer:**
- Purpose: Persist session events, checkpoints, learning
- Location: `mcps/session-memory/storage/`
- Contains: SQLite index, JSONL event logs, checkpoint files
- Depends on: sqlite3, filesystem
- Used by: Session memory server for durability

## Data Flow

**Plugin Creation Flow:**

1. Developer runs `init_plugin.py` → Creates SKILL.md or MCP.md template
2. Developer populates manifest frontmatter (name, description, type, entry_point)
3. Developer adds scripts/references/assets (skills) or Python implementation (MCPs)
4. Plugin directory structure complete

**Plugin Packaging Flow:**

1. Developer runs `package_plugin.py <plugin-dir>`
2. → Calls `validate_plugin()` to verify structure
3. → Extracts frontmatter from manifest
4. → Creates .plugin zip file with MANIFEST.json + all plugin files
5. → Output: `dist/plugin-name.plugin`

**Plugin Installation Flow (MCP):**

1. User/developer runs `install_mcp.py dist/plugin.plugin` or `--symlink`
2. → Extracts or symlinks to `~/.claude/plugin-name/`
3. → Updates Claude Desktop config (`~/.config/claude/claude_desktop_config.json`)
4. → MCP available next Claude Desktop restart

**Skill Loading Flow (Runtime):**

1. Claude Desktop context manager loads plugin for conversation
2. → Reads SKILL.md from skills directory
3. → Parses frontmatter: name, description, WHEN to trigger
4. → Adds markdown workflow to Claude's context
5. → Loads scripts from scripts/ directory (optional executable code)
6. → Loads references from references/ directory
7. → Templates from assets/ available for generation

**Session Memory Flow (Stateful Skills):**

1. Skill calls `session_init()` with skill_name (e.g., "specification-refiner")
2. → Session memory server creates session and loads plugin
3. → Plugin determines initial state based on skill type
4. → Events recorded as skill progresses (records, decisions, findings)
5. → Auto-checkpoint every 5 minutes or manual checkpoint via CLI
6. → On next invocation: Resume context generated from events + state
7. → Session persists across context window boundaries

**State Management:**

- Memory File: `analysis-state.md` created per skill session
- Location: Project root (or session-specific path)
- Contents: Phase tracking, coverage maps, question tracking, findings, assumptions
- Update: Atomic writes after each phase/clarification
- Resumption: Parsed from file on session_resume() call

## Key Abstractions

**Plugin Type Abstraction:**
- Purpose: Provide unified interface for two distinct plugin types
- Examples: `tools/validate_plugin.py` detects type via manifest presence
- Pattern: Detect SKILL.md (skill) vs MCP.md (mcp) vs server.py (legacy mcp)
- Benefits: Single toolchain, consistent validation, future plugin type support

**SessionPlugin Base Class:**
- Purpose: Define interface for skill-specific session state management
- Examples: `mcps/session-memory/plugins/spec_refiner.py`, `mcps/session-memory/plugins/speckit.py`
- Pattern: Plugins implement abstract methods (get_state_schema, calculate_progress, generate_resumption_context)
- Benefits: Extensible state handling, skill-specific progress metrics, resumption context generation

**Feature Module Architecture (MCP):**
- Purpose: Optional services with graceful degradation
- Examples: EmbeddingService, CloudSyncService, LearningService, KnowledgeGraph
- Pattern: Try import → catch ImportError → continue without feature
- Benefits: Reduced coupling, optional API keys, standalone operation

**Package Format (.plugin):**
- Purpose: Distributable, versionable plugin archive
- Examples: specification-refiner.plugin, session-memory.plugin
- Pattern: ZIP file containing MANIFEST.json + plugin directory structure
- Benefits: Single file distribution, metadata attached, preserves directory layout

## Entry Points

**Skill Entry Point:**
- Location: `skills/[name]/SKILL.md` frontmatter contains `description` with trigger conditions
- Triggers: Context-based (Claude evaluates if skill applies to user request)
- Responsibilities: Load domain knowledge, provide step-by-step workflow, generate outputs

**MCP Server Entry Point:**
- Location: `mcps/[name]/MCP.md` frontmatter `entry_point` or `mcps/[name]/server.py`
- Triggers: Claude Desktop startup (via config), tools always available
- Responsibilities: Register tools, handle requests via MCP protocol, manage state

**CLI Entry Points (Tools):**
- `tools/init_plugin.py`: Create new plugin from template
- `tools/validate_plugin.py`: Validate plugin structure and metadata
- `tools/package_plugin.py`: Package plugin into .plugin file
- `tools/install_mcp.py`: Install MCP to ~/.claude/ and register with Claude Desktop

**Session Memory Entry Points:**
- `session_init(skill_name)`: Start tracking session for specific skill
- `session_record(category, type, data)`: Log event during session
- `session_checkpoint()`: Explicit checkpoint creation
- `session_query(category, query_string)`: Search session events
- `session_resume()`: Generate resumption context for new session

## Error Handling

**Strategy:** Graceful degradation with informative error messages; blocking validation prevents invalid packaged plugins.

**Patterns:**

**Plugin Validation Errors:**
- Location: `tools/validate_plugin.py` catches structure violations
- Examples: Missing SKILL.md/MCP.md, invalid name format (must be hyphen-case), reserved word check
- Handling: Print error message, exit with code 1, block packaging
- Recovery: Developer fixes manifest/structure and re-runs validation

**MCP Startup Errors:**
- Location: `mcps/session-memory/server.py` load feature modules
- Examples: OpenAI API key missing, Cloudflare credentials invalid
- Handling: Feature disabled (graceful), server continues with core functionality
- Recovery: Optional dependencies available but not required; provide env vars to enable

**Session State Errors:**
- Location: `mcps/session-memory/plugins/` state serialization
- Examples: Invalid state schema, corrupted checkpoint data
- Handling: Log error, initialize fresh state, continue session
- Recovery: Checkpoint data survives; previous events remain queryable

**Database Corruption:**
- Location: `mcps/session-memory/server.py` database operations
- Examples: SQLite index corruption
- Handling: Fallback to JSONL event log; rebuild index on next checkpoint
- Recovery: No event loss; index rebuild transparent to caller

## Cross-Cutting Concerns

**Logging:**
- Approach: Skill workflows use structured event logging via `session_record()` in MCP server
- Pattern: Every significant action (decision, question, finding) recorded with category/type
- Location: `mcps/session-memory/storage/events.jsonl` (JSONL format for streaming)

**Validation:**
- Approach: Mandatory plugin validation before packaging
- Pattern: `validate_plugin()` checks manifest presence, frontmatter structure, naming conventions
- Location: `tools/validate_plugin.py` (used by `package_plugin.py`)
- Enforcement: Packaging fails if validation fails; cannot distribute invalid plugins

**Authentication:**
- Approach: Environment variables for API credentials (OpenAI, Cloudflare)
- Pattern: Load from .env files (project root, ~/.claude/.env) with precedence
- Location: `mcps/session-memory/server.py` loads from dotenv on startup
- Fallback: Features disabled if credentials missing; server continues

**Configuration:**
- Approach: JSON config file per plugin (optional), environment variables global
- Pattern: `mcps/session-memory/config.json` defines feature toggles, paths, API models
- Extensibility: Feature modules read config on init; support enable/disable per feature
- Location: Config loaded from plugin directory on server startup

---

*Architecture analysis: 2026-01-23*
