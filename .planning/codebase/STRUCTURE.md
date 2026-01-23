# Codebase Structure

**Analysis Date:** 2026-01-23

## Directory Layout

```
claude-plugins/
├── skills/                         # Skill plugins (workflow-based)
│   ├── documentation-architect/    # Diátaxis documentation framework
│   ├── research-opportunity-investigator/
│   ├── specification-refiner/      # Spec analysis with SEAMS + Critical Path
│   ├── speckit-generator/          # Implementation → spec generation
│   ├── streaming-output/           # Output streaming patterns
│   ├── streaming-output-mcp/       # Streaming output as MCP
│   └── trade-study-analysis/       # DAU 9-Step trade study process
├── mcps/                           # MCP servers (tool-based)
│   ├── session-memory/             # Persistent session memory server
│   │   ├── server.py               # MCP entry point
│   │   ├── plugins/                # Skill-specific state plugins
│   │   ├── modules/                # Feature modules (optional)
│   │   ├── storage/                # SQLite index, JSONL events
│   │   └── config.json             # Feature toggles, paths
│   ├── knowledge-mcp/              # Knowledge base MCP (if present)
│   └── streaming-output/           # Streaming output MCP
├── tools/                          # Plugin management utilities
│   ├── init_plugin.py              # Create new plugin from template
│   ├── validate_plugin.py          # Validate plugin structure
│   ├── package_plugin.py           # Package plugin to .plugin file
│   └── install_mcp.py              # Install MCP to ~/.claude/
├── plugin-creator/                 # Skill for creating new plugins
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
├── dist/                           # Packaged .plugin files (gitignored)
├── .planning/codebase/             # GSD codebase documentation
├── _references/                    # External references (claude-cookbooks, standards)
└── _examples/                      # Example plugin implementations
```

## Directory Purposes

**skills/:**
- Purpose: Skill plugins providing domain-specific workflows
- Contains: SKILL.md manifests, scripts directories, references, assets
- Key files: Each skill has SKILL.md (frontmatter + workflow instructions)
- Access: Claude loads automatically based on context

**skills/[name]/:**
- `SKILL.md`: Plugin manifest with frontmatter (name, description, trigger conditions) + markdown workflow
- `scripts/`: Executable Python/Bash code for automation (optional)
- `references/`: Documentation and reference material loaded into context (optional)
- `assets/`: Templates, icons, examples used as output (optional, not loaded into context)
- `commands/`: CLI-style commands exposed by skill (optional)
- `hooks/`: Pre/post processing scripts (optional)

**mcps/:**
- Purpose: MCP servers providing tools to Claude Desktop
- Contains: MCP.md manifests, Python server.py, feature modules
- Key files: server.py (entry point), config.json (feature toggles)
- Access: Available globally in Claude Desktop after registration

**mcps/session-memory/:**
- `server.py`: MCP server implementation; handles tool registration and persistence
- `config.json`: Feature configuration (checkpointing interval, paths, API providers)
- `plugins/`: Skill-specific state management (base.py, spec_refiner.py, speckit.py, etc.)
- `modules/`: Optional feature services (embeddings, cloud_sync, learning, entities, document_ingest)
- `storage/`: Persistent data directory (events.jsonl, index.sqlite, checkpoints/, handoffs/)

**tools/:**
- Purpose: CLI utilities for plugin lifecycle management
- Contains: Python scripts (no external frameworks, vanilla Python only)
- Access: Run directly via Python or packaged in distribution

**plugin-creator/:**
- Purpose: Skill for generating new plugins from within Claude
- Location: `plugin-creator/SKILL.md`
- Usage: Claude can invoke to scaffold new skill or MCP structure

**dist/:**
- Purpose: Output directory for packaged .plugin files
- Contains: ZIP archives named `[plugin-name].plugin`
- Contents: MANIFEST.json + plugin directory structure
- Status: Gitignored (generated via `package_plugin.py`)

**_references/:**
- Purpose: External reference material and standards
- Contains: claude-cookbooks (capabilities, patterns), SE standards
- Status: Submodule or vendored; not modified by this project

## Key File Locations

**Entry Points:**

- `skills/*/SKILL.md`: Skill frontmatter defines name, description, trigger conditions
- `mcps/*/MCP.md`: MCP manifest defines type, entry_point (server.py), dependencies
- `mcps/session-memory/server.py`: MCP stdio server entry point
- `tools/init_plugin.py`: Create new plugin
- `tools/package_plugin.py`: Package plugin for distribution
- `tools/install_mcp.py`: Install MCP to Claude Desktop

**Configuration:**

- `mcps/session-memory/config.json`: Feature toggles (embeddings, cloud_sync, learning, entities), paths (storage, checkpoints)
- `mcps/session-memory/.env`: Environment variables for APIs (optional)
- `~/.claude/.env`: Global defaults for API keys
- `~/.config/claude/claude_desktop_config.json`: Claude Desktop MCP registration (written by install_mcp.py)

**Core Logic:**

- `skills/specification-refiner/SKILL.md`: 8-phase specification refinement workflow (Phase 0-8)
- `skills/speckit-generator/SKILL.md`: Convert requirements to automatable spec
- `skills/documentation-architect/SKILL.md`: Diátaxis framework documentation generation
- `mcps/session-memory/server.py`: Session persistence, event recording, checkpoint/handoff generation
- `mcps/session-memory/plugins/base.py`: SessionPlugin abstract base for state management

**Testing:**

- No test directory present; validation via `validate_plugin.py` only
- Plugin-specific testing would be in individual skill/mcp directories (none currently)

**Memory/State:**

- `analysis-state.md`: Created per specification-refiner session (in project root or session dir)
- Format: Phase tracking, coverage maps (11 categories), clarification sessions, findings, assumptions
- Storage: Persisted per skill invocation; participant in session memory if recording enabled

## Naming Conventions

**Files:**

- Plugin manifests: `SKILL.md` (skills) or `MCP.md` (MCPs)
- Configuration: `config.json` (JSON format)
- Scripts: snake_case with .py extension (e.g., `init_plugin.py`)
- Documentation: UPPERCASE.md for top-level (README.md, SKILL.md, MCP.md)
- Memory files: snake_case.md (e.g., `analysis-state.md`, `traceability-matrix.md`)

**Directories:**

- Plugin directories: hyphen-case (e.g., `specification-refiner`, `session-memory`)
- Feature modules: snake_case (e.g., `cloud_sync.py`, `document_ingest.py`)
- Skill subdirectories: lowercase with underscores (e.g., `scripts/`, `references/`, `assets/`)
- MCP plugin classes: lowercase with underscores (e.g., `spec_refiner.py`, `feature_impl.py`)

**Variables/Classes:**

- Plugin names in manifest frontmatter: hyphen-case (e.g., `name: specification-refiner`)
- Python classes: PascalCase (e.g., `SessionPlugin`, `EmbeddingService`)
- Python functions: snake_case (e.g., `validate_plugin()`, `package_plugin()`)

## Where to Add New Code

**New Skill:**

1. Primary code: `skills/[new-skill-name]/SKILL.md`
   - Frontmatter: name (hyphen-case), description, trigger conditions
   - Workflow: Markdown instructions (phases, gates, patterns)

2. Executable code: `skills/[new-skill-name]/scripts/` (optional)
   - Python scripts: `scripts/*.py`
   - Bash scripts: `scripts/*.sh`

3. Reference documentation: `skills/[new-skill-name]/references/` (optional)
   - Framework docs, API references, patterns
   - Loaded into Claude context as needed

4. Output templates: `skills/[new-skill-name]/assets/` (optional)
   - Markdown templates, images, other assets
   - Used during generation phase; not loaded into context

5. Commands: `skills/[new-skill-name]/commands/` (optional)
   - CLI-style commands that Claude can invoke

**New MCP:**

1. Primary implementation: `mcps/[new-mcp-name]/server.py`
   - Implement MCP stdio server
   - Define tools and resources
   - Handle protocol messages

2. Manifest: `mcps/[new-mcp-name]/MCP.md`
   - Frontmatter: name, description, type, entry_point (server.py)
   - Optional: dependencies, config_file references

3. Configuration: `mcps/[new-mcp-name]/config.json` (optional)
   - Feature toggles, paths, API configuration

4. Optional modules: `mcps/[new-mcp-name]/modules/`
   - Service classes for major features
   - One module per feature (consistent with session-memory pattern)
   - Follow graceful degradation pattern (try import, catch ImportError)

5. Plugins (for session-specific state): `mcps/[new-mcp-name]/plugins/` (optional)
   - Only if MCP tracks stateful skill invocations
   - Inherit from SessionPlugin base class

**New Utility:**

- Location: `tools/[new-util].py`
- Style: Vanilla Python (no external frameworks except pyyaml for manifest parsing)
- Interface: Command-line arguments via argparse or sys.argv
- Pattern: Standalone script with main() function

**Shared Reference Material:**

- Location: External repository (`_references/`)
- Integration: As-is; not modified locally
- Usage: Imported into skill workflows by reference

## Special Directories

**storage/ (MCP):**
- Purpose: Session-local persistent data for MCP server
- Generated: Yes (created at runtime on first invocation)
- Committed: No (gitignored)
- Contents: `events.jsonl` (JSONL event stream), `index.sqlite` (searchable index)
- Structure: `checkpoints/` (auto, manual), `handoffs/` for session transfer

**checkpoints/ (MCP):**
- Purpose: Session savepoints for resumption
- Generated: Yes (every 5 minutes auto, plus manual triggers)
- Contents: JSON checkpoint files with session state, plugin state, event summary
- Cleanup: Manual (no automatic expiration)

**dist/:**
- Purpose: Output directory for packaged plugins
- Generated: Yes (via `package_plugin.py`)
- Committed: No (gitignored)
- Contents: `[plugin-name].plugin` ZIP files
- Each ZIP: MANIFEST.json + plugin directory structure

**.planning/codebase/:**
- Purpose: GSD codebase analysis documents
- Generated: Yes (via `/gsd:map-codebase` orchestrator)
- Committed: Yes (tracked in version control)
- Contents: ARCHITECTURE.md, STRUCTURE.md (this phase); CONVENTIONS.md, TESTING.md (quality phase); CONCERNS.md (concerns phase); STACK.md, INTEGRATIONS.md (tech phase)

---

*Structure analysis: 2026-01-23*
