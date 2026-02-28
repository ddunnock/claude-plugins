# /system-dev:init

Create the `.system-dev/` workspace directory with registry subdirectories, empty journal, index, and config files.

## Invocation

```
/system-dev:init
```

No parameters required. Operates on the current project root.

## Workflow

1. **Check for existing workspace**: Look for `.system-dev/` in the project root. If it already exists, warn the user and return without modifying anything.

2. **Create workspace structure**: Run the init script:
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && uv run scripts/init_workspace.py --project-root <PROJECT_ROOT>
   ```

3. **Verify creation**: Confirm all directories and files were created:
   - `.system-dev/registry/components/`
   - `.system-dev/registry/interfaces/`
   - `.system-dev/registry/contracts/`
   - `.system-dev/registry/requirement-refs/`
   - `.system-dev/journal.jsonl` (empty)
   - `.system-dev/index.json` (initial schema)
   - `.system-dev/config.json` (initial config)

4. **Report results**: Display a summary of created paths and any warnings.

## Output Format

```markdown
## Workspace Initialized

Created `.system-dev/` with:
- 4 registry directories (components, interfaces, contracts, requirement-refs)
- Empty journal (journal.jsonl)
- Slot index (index.json)
- Configuration (config.json)

Ready for `/system-dev:create` to add design elements.
```

## Error Handling

- **Workspace exists**: Return warning message, do not overwrite. Suggest using `/system-dev:status` instead.
- **Permission error**: Report the path and permission issue.
- **Disk space**: Report if directory creation fails.
