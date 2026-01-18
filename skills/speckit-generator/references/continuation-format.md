# Continuation Format Reference

Standard format for presenting next steps after command completion. All speckit commands use this format for consistent user experience.

---

## Format Template

After command completion, always present the next logical step using this standardized format:

```markdown
## ▶ Next Up
**{command}: {name}** — {one-line description}
`/{command}`
<sub>`/clear` first → fresh context window</sub>
```

### Format Elements

| Element | Purpose | Example |
|---------|---------|---------|
| `▶ Next Up` | Visual indicator for next action | Always use this exact header |
| `{command}` | The slash command to run | `implement`, `analyze`, `plan` |
| `{name}` | Short descriptive name | "Consistency Check", "Phase 2" |
| `{description}` | One-line explanation | "Verify implementation meets spec" |
| `/clear` reminder | Context management tip | Helps user manage context window |

---

## Why This Format

1. **Consistency**: Users always know where to look for next steps
2. **Clarity**: Command is prominently displayed and easy to copy
3. **Context awareness**: Reminds users to clear context when beneficial
4. **Discoverability**: Users learn the command workflow organically

---

## Command-Specific Next Step Logic

### /init

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| Fresh initialization | Add spec to `speckit/` | Create specification file |
| Spec already exists | `/clarify` | Resolve spec ambiguities |
| Returning project | `/implement --continue` | Resume where you left off |

### /plan

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| Plan approved | `/tasks` | Generate implementation tasks |
| ADRs need review | `/plan --revise` | Update architecture decisions |
| Spec gaps found | `/clarify` | Resolve ambiguities first |

### /tasks

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| Tasks approved | `/implement "Phase 1"` | Start implementation |
| SMART failures | `/tasks --revise` | Fix acceptance criteria |
| Coverage gaps | `/plan --revise` | Update plan for coverage |

### /clarify

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| All resolved | `/plan` or `/tasks` | Continue pipeline |
| More questions | `/clarify` | Continue clarification |
| Spec updated | `/analyze` | Verify consistency |

### /analyze

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| No issues | `/implement` | Proceed with implementation |
| Issues found | Fix issues | Address reported problems |
| Spec drift | `/clarify` | Re-clarify changed requirements |

### /implement

| Completion State | Next Command | Description |
|------------------|--------------|-------------|
| All criteria passed, more tasks | `/implement "Phase [N]"` | Continue remaining phase tasks |
| Any criteria failed | `/implement TASK-XXX` | Retry failed task |
| Phase complete | `/implement "Phase [N+1]"` | Start next phase |
| All phases complete | `/analyze` | Run final consistency check |
| Blocked by dependency | `/implement TASK-XXX` | Resolve blocking task first |

---

## Example Outputs

### After /init

```markdown
## ▶ Next Up
**clarify: Resolve Ambiguities** — Interactive Q&A to clarify specification gaps
`/clarify`
<sub>`/clear` first → fresh context window</sub>
```

### After /plan

```markdown
## ▶ Next Up
**tasks: Generate Tasks** — Create implementation tasks from approved plan
`/tasks`
<sub>`/clear` first → fresh context window</sub>
```

### After /implement (Phase 1 Complete)

```markdown
## ▶ Next Up
**implement: Phase 2** — Continue with user interface components
`/implement "Phase 2"`
<sub>`/clear` first → fresh context window</sub>
```

### After /implement (All Complete)

```markdown
## ▶ Next Up
**analyze: Final Check** — Verify all implementations meet spec requirements
`/analyze`
<sub>`/clear` first → fresh context window</sub>
```

---

*This reference is included by all command workflow files. Update here to change all commands.*
