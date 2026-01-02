#!/usr/bin/env bash
# Initialize .claude automation directory structure
#
# Creates the standard directory layout for Claude Code automation:
#   .claude/commands/     - Command markdown files
#   .claude/scripts/bash/ - Bash automation scripts
#   .claude/scripts/python/ - Python automation scripts
#   .claude/templates/    - Output templates
#   .claude/memory/       - Persistent state files
#
# Usage: ./init-automation.sh [OPTIONS] [PROJECT_ROOT]
#
# OPTIONS:
#   --json           Output JSON for command parsing
#   --force          Overwrite existing files
#   --with-examples  Include example files
#   --help, -h       Show help
#
# EXAMPLES:
#   ./init-automation.sh                    # Initialize in current project
#   ./init-automation.sh --json             # JSON output
#   ./init-automation.sh /path/to/project   # Specific project

set -e

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

JSON_MODE=false
FORCE=false
WITH_EXAMPLES=false
PROJECT_ROOT=""

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --force) FORCE=true ;;
        --with-examples) WITH_EXAMPLES=true ;;
        --help|-h)
            sed -n '2,/^[^#]/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        --*) echo "ERROR: Unknown option '$arg'" >&2; exit 1 ;;
        *) [[ -z "$PROJECT_ROOT" ]] && PROJECT_ROOT="$arg" ;;
    esac
done

# ============================================================================
# SETUP
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find project root if not specified
find_project_root() {
    local dir="${1:-$PWD}"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" || -f "$dir/package.json" || -f "$dir/pyproject.toml" || -f "$dir/Cargo.toml" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo "$PWD"
}

[[ -z "$PROJECT_ROOT" ]] && PROJECT_ROOT=$(find_project_root)
CLAUDE_DIR="$PROJECT_ROOT/.claude"

# JSON array helper
json_array() {
    local arr=("$@")
    if [[ ${#arr[@]} -eq 0 ]]; then
        echo "[]"
    else
        local json=""
        for item in "${arr[@]}"; do
            escaped=$(echo "$item" | sed 's/\\/\\\\/g; s/"/\\"/g')
            json="${json}\"${escaped}\","
        done
        echo "[${json%,}]"
    fi
}

log_info()    { $JSON_MODE || echo "ℹ️  $*"; }
log_success() { $JSON_MODE || echo "✅ $*"; }

# ============================================================================
# MAIN LOGIC
# ============================================================================

created=()
existed=()
skipped=()

init_dir() {
    local dir="$1"
    local relative="${dir#$PROJECT_ROOT/}"
    
    if [[ -d "$dir" ]]; then
        existed+=("$relative")
    else
        mkdir -p "$dir"
        created+=("$relative")
    fi
}

write_file() {
    local file="$1"
    local content="$2"
    local relative="${file#$PROJECT_ROOT/}"
    
    if [[ -f "$file" ]] && ! $FORCE; then
        skipped+=("$relative")
        return 1
    fi
    
    echo "$content" > "$file"
    created+=("$relative")
    return 0
}

main() {
    log_info "Initializing .claude/ in $PROJECT_ROOT"
    
    # Create directory structure
    init_dir "$CLAUDE_DIR/commands"
    init_dir "$CLAUDE_DIR/scripts/bash"
    init_dir "$CLAUDE_DIR/scripts/python"
    init_dir "$CLAUDE_DIR/templates"
    init_dir "$CLAUDE_DIR/memory"
    
    # Create common.sh
    write_file "$CLAUDE_DIR/scripts/bash/common.sh" '#!/usr/bin/env bash
# Common utilities for automation scripts

log_info()    { ${JSON_MODE:-false} || echo "ℹ️  $*"; }
log_success() { ${JSON_MODE:-false} || echo "✅ $*"; }
log_warning() { ${JSON_MODE:-false} || echo "⚠️  $*"; }
log_error()   { ${JSON_MODE:-false} || echo "❌ $*" >&2; }

json_array() {
    local arr=("$@")
    if [[ ${#arr[@]} -eq 0 ]]; then
        echo "[]"
    else
        local json=""
        for item in "${arr[@]}"; do
            escaped=$(echo "$item" | sed '\''s/\\/\\\\/g; s/"/\\"/g'\'')
            json="${json}\"${escaped}\","
        done
        echo "[${json%,}]"
    fi
}

find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        [[ -d "$dir/.claude" || -f "$dir/package.json" || -f "$dir/pyproject.toml" ]] && echo "$dir" && return
        dir="$(dirname "$dir")"
    done
    echo "$PWD"
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || { log_error "Required: $1"; exit 1; }
}
' || true
    
    # Create example files if requested
    if $WITH_EXAMPLES; then
        write_file "$CLAUDE_DIR/commands/example.md" '---
description: Example command template - customize or delete
handoffs: []
---

## User Input

```text
$ARGUMENTS
```

## Purpose

This is an example command. Customize it for your workflow.

## Workflow

1. **Step 1**: Description

## Completion Criteria

- [ ] Success condition
' || true
        
        write_file "$CLAUDE_DIR/templates/example-template.md" '# Example Template

<!--
Purpose: Example output template
Updated by: Example command
-->

**Last Updated**: [TIMESTAMP]

---

## Content

| Field | Value |
|-------|-------|
| Item | [PLACEHOLDER] |
' || true
    fi
    
    # Create .gitkeep files for empty directories
    for dir in commands scripts/python templates memory; do
        local gitkeep="$CLAUDE_DIR/$dir/.gitkeep"
        [[ ! -f "$gitkeep" ]] && touch "$gitkeep"
    done
    
    # ========================================================================
    # OUTPUT
    # ========================================================================
    
    local status="success"
    
    if $JSON_MODE; then
        cat << EOF
{
  "status": "$status",
  "project_root": "$PROJECT_ROOT",
  "claude_dir": "$CLAUDE_DIR",
  "created": $(json_array "${created[@]}"),
  "existed": $(json_array "${existed[@]}"),
  "skipped": $(json_array "${skipped[@]}"),
  "with_examples": $WITH_EXAMPLES
}
EOF
    else
        log_success "Initialized .claude/ structure"
        echo ""
        echo "Directory: $CLAUDE_DIR"
        echo ""
        
        if [[ ${#created[@]} -gt 0 ]]; then
            echo "Created:"
            printf '  %s\n' "${created[@]}"
        fi
        
        if [[ ${#existed[@]} -gt 0 ]]; then
            echo "Already existed:"
            printf '  %s\n' "${existed[@]}"
        fi
        
        if [[ ${#skipped[@]} -gt 0 ]]; then
            echo "Skipped (use --force to overwrite):"
            printf '  %s\n' "${skipped[@]}"
        fi
        
        echo ""
        echo "Next steps:"
        echo "  1. Create commands in .claude/commands/"
        echo "  2. Add scripts in .claude/scripts/bash/"
        echo "  3. Define templates in .claude/templates/"
    fi
}

main
