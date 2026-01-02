# Script Patterns Reference

## Contents
- Bash script template
- Common utilities (common.sh)
- Pattern 1: Setup/initialization scripts
- Pattern 2: Check/validation scripts
- Pattern 3: Generator scripts
- Pattern 4: Runner/executor scripts
- Python script patterns
- JSON output conventions

## Bash Script Template

```bash
#!/usr/bin/env bash
# [Script Title]
#
# [2-3 sentence description]
#
# Usage: ./script.sh [OPTIONS] [ARGS...]
#
# OPTIONS:
#   --json           Output JSON for command parsing
#   --strict         Enable strict validation
#   --help, -h       Show help
#
# ARGS:
#   [name]           Description
#
# EXAMPLES:
#   ./script.sh                    # Basic usage
#   ./script.sh --json             # JSON output
#   ./script.sh --strict path/     # With args

set -e

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

JSON_MODE=false
STRICT_MODE=false
ARGS=()

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --strict) STRICT_MODE=true ;;
        --help|-h)
            sed -n '2,/^[^#]/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        --*) echo "ERROR: Unknown option '$arg'" >&2; exit 1 ;;
        *) ARGS+=("$arg") ;;
    esac
done

# ============================================================================
# SETUP
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$SCRIPT_DIR/common.sh" ]] && source "$SCRIPT_DIR/common.sh"

# ============================================================================
# MAIN LOGIC
# ============================================================================

main() {
    local status="success"
    local results=()
    local errors=()
    
    # Implementation here
    
    # ========================================================================
    # OUTPUT
    # ========================================================================
    
    if $JSON_MODE; then
        cat << EOF
{
  "status": "$status",
  "results": $(json_array "${results[@]}"),
  "errors": $(json_array "${errors[@]}")
}
EOF
    else
        echo "Results:"
        printf '  %s\n' "${results[@]}"
        [[ ${#errors[@]} -gt 0 ]] && printf 'Errors:\n  %s\n' "${errors[@]}"
    fi
    
    [[ "$status" == "success" ]]
}

main "$@"
```

## Common Utilities (common.sh)

Shared functions for all scripts:

```bash
#!/usr/bin/env bash
# Common utilities for automation scripts

# Logging (respects JSON_MODE)
log_info()    { $JSON_MODE || echo "ℹ️  $*"; }
log_success() { $JSON_MODE || echo "✅ $*"; }
log_warning() { $JSON_MODE || echo "⚠️  $*"; }
log_error()   { $JSON_MODE || echo "❌ $*" >&2; }

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

# Find project root
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        [[ -d "$dir/.claude" || -f "$dir/package.json" || -f "$dir/pyproject.toml" ]] && echo "$dir" && return
        dir="$(dirname "$dir")"
    done
    echo "$PWD"
}

# Check command exists
require_cmd() {
    command -v "$1" >/dev/null 2>&1 || { log_error "Required: $1"; exit 1; }
}
```

## Pattern 1: Setup/Initialization Scripts

Creates directories and initial files.

```bash
#!/usr/bin/env bash
# Initialize .claude automation directory structure
#
# Usage: ./init-automation.sh [OPTIONS]
#
# OPTIONS:
#   --json    Output JSON
#   --force   Overwrite existing

set -e

JSON_MODE=false
FORCE=false

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --force) FORCE=true ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

PROJECT_ROOT=$(find_project_root)
CLAUDE_DIR="$PROJECT_ROOT/.claude"

created=()
existed=()

init_dir() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        existed+=("$dir")
    else
        mkdir -p "$dir"
        created+=("$dir")
    fi
}

main() {
    init_dir "$CLAUDE_DIR/commands"
    init_dir "$CLAUDE_DIR/scripts/bash"
    init_dir "$CLAUDE_DIR/scripts/python"
    init_dir "$CLAUDE_DIR/templates"
    init_dir "$CLAUDE_DIR/memory"
    
    # Copy common.sh if not exists
    if [[ ! -f "$CLAUDE_DIR/scripts/bash/common.sh" ]]; then
        cp "$SCRIPT_DIR/common.sh" "$CLAUDE_DIR/scripts/bash/" 2>/dev/null || true
        created+=("common.sh")
    fi
    
    if $JSON_MODE; then
        cat << EOF
{
  "status": "success",
  "project_root": "$PROJECT_ROOT",
  "created": $(json_array "${created[@]}"),
  "existed": $(json_array "${existed[@]}")
}
EOF
    else
        log_success "Initialized .claude/ structure"
        [[ ${#created[@]} -gt 0 ]] && echo "Created: ${created[*]}"
    fi
}

main
```

## Pattern 2: Check/Validation Scripts

Examines files and reports findings.

```bash
#!/usr/bin/env bash
# Validate automation artifacts
#
# Usage: ./validate-automation.sh [OPTIONS] [PATH]
#
# Checks:
#   - Command YAML syntax
#   - Script syntax (shellcheck)
#   - Handoff targets exist
#   - Template placeholder consistency

set -e

JSON_MODE=false
TARGET="${1:-.claude}"

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

errors=()
warnings=()
checked=()

check_command() {
    local file="$1"
    checked+=("$(basename "$file")")
    
    # Check YAML frontmatter exists
    if ! head -1 "$file" | grep -q "^---"; then
        errors+=("$file: Missing YAML frontmatter")
        return
    fi
    
    # Check description exists
    if ! grep -q "^description:" "$file"; then
        errors+=("$file: Missing description in frontmatter")
    fi
    
    # Check handoff targets exist
    local handoffs
    handoffs=$(grep -oP 'agent:\s*\K\S+' "$file" 2>/dev/null || true)
    for target in $handoffs; do
        local target_file="$(dirname "$file")/${target}.md"
        [[ ! -f "$target_file" ]] && warnings+=("$file: Handoff target '$target' not found")
    done
}

check_script() {
    local file="$1"
    checked+=("$(basename "$file")")
    
    # Syntax check
    if ! bash -n "$file" 2>/dev/null; then
        errors+=("$file: Bash syntax error")
    fi
    
    # Shellcheck if available
    if command -v shellcheck >/dev/null 2>&1; then
        local issues
        issues=$(shellcheck -f gcc "$file" 2>/dev/null | wc -l)
        [[ "$issues" -gt 0 ]] && warnings+=("$file: $issues shellcheck issues")
    fi
}

main() {
    # Check commands
    for cmd in "$TARGET"/commands/*.md 2>/dev/null; do
        [[ -f "$cmd" ]] && check_command "$cmd"
    done
    
    # Check scripts
    for script in "$TARGET"/scripts/bash/*.sh 2>/dev/null; do
        [[ -f "$script" ]] && check_script "$script"
    done
    
    local status="success"
    [[ ${#errors[@]} -gt 0 ]] && status="error"
    
    if $JSON_MODE; then
        cat << EOF
{
  "status": "$status",
  "checked": $(json_array "${checked[@]}"),
  "errors": $(json_array "${errors[@]}"),
  "warnings": $(json_array "${warnings[@]}")
}
EOF
    else
        echo "Checked ${#checked[@]} files"
        [[ ${#errors[@]} -gt 0 ]] && printf 'Errors:\n  %s\n' "${errors[@]}"
        [[ ${#warnings[@]} -gt 0 ]] && printf 'Warnings:\n  %s\n' "${warnings[@]}"
        [[ "$status" == "success" ]] && log_success "Validation passed"
    fi
    
    [[ "$status" == "success" ]]
}

main
```

## Pattern 3: Generator Scripts

Creates files from templates or data.

```bash
#!/usr/bin/env bash
# Generate command file from template
#
# Usage: ./generate-command.sh --name NAME [--type TYPE]

set -e

JSON_MODE=false
NAME=""
TYPE="basic"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) JSON_MODE=true; shift ;;
        --name) NAME="$2"; shift 2 ;;
        --type) TYPE="$2"; shift 2 ;;
        *) shift ;;
    esac
done

[[ -z "$NAME" ]] && echo "ERROR: --name required" >&2 && exit 1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

PROJECT_ROOT=$(find_project_root)
OUTPUT="$PROJECT_ROOT/.claude/commands/${NAME}.md"

main() {
    [[ -f "$OUTPUT" ]] && { 
        $JSON_MODE && echo '{"status":"exists","path":"'"$OUTPUT"'"}'
        $JSON_MODE || log_error "File exists: $OUTPUT"
        exit 1
    }
    
    mkdir -p "$(dirname "$OUTPUT")"
    
    cat > "$OUTPUT" << 'TEMPLATE'
---
description: [TODO: Describe what this command does]
handoffs: []
---

## User Input

```text
$ARGUMENTS
```

[Parse user arguments here]

## Purpose

[What this command does and when to use it]

## Workflow

1. **Step 1**: Description

## Completion Criteria

- [ ] Success condition
TEMPLATE

    if $JSON_MODE; then
        echo '{"status":"created","path":"'"$OUTPUT"'","type":"'"$TYPE"'"}'
    else
        log_success "Created: $OUTPUT"
    fi
}

main
```

## Pattern 4: Runner/Executor Scripts

Performs actions with progress output.

```bash
#!/usr/bin/env bash
# Run task with progress tracking
#
# Usage: ./run-task.sh --task TASK_ID [--dry-run]

set -e

JSON_MODE=false
DRY_RUN=false
TASK_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) JSON_MODE=true; shift ;;
        --dry-run) DRY_RUN=true; shift ;;
        --task) TASK_ID="$2"; shift 2 ;;
        *) shift ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

main() {
    log_info "Running task: $TASK_ID"
    
    local status="success"
    local output=""
    local duration_start=$SECONDS
    
    if $DRY_RUN; then
        output="Dry run - would execute task $TASK_ID"
    else
        # Actual execution here
        output="Task $TASK_ID completed"
    fi
    
    local duration=$((SECONDS - duration_start))
    
    if $JSON_MODE; then
        cat << EOF
{
  "status": "$status",
  "task_id": "$TASK_ID",
  "output": "$output",
  "duration_seconds": $duration,
  "dry_run": $DRY_RUN
}
EOF
    else
        echo "$output"
        log_success "Completed in ${duration}s"
    fi
}

main
```

## Python Script Patterns

For complex logic or when Python libraries are needed:

```python
#!/usr/bin/env python3
"""
Script description here.

Usage: python script.py [--json] [args...]
"""

import argparse
import json
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("path", nargs="?", default=".", help="Target path")
    args = parser.parse_args()
    
    results = {"status": "success", "data": []}
    
    try:
        # Implementation here
        target = Path(args.path)
        results["data"] = [str(f) for f in target.glob("*")]
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if results["status"] == "success":
            for item in results["data"]:
                print(f"  {item}")
        else:
            print(f"Error: {results['error']}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
```

## JSON Output Conventions

Standard response structure:

```json
{
  "status": "success|error|warning",
  "message": "Human-readable summary",
  "data": { },
  "errors": [ ],
  "warnings": [ ]
}
```

Commands should parse and handle each status appropriately.
