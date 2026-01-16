#!/bin/bash
set -uo pipefail
# check-init-state.sh
# Validates that a project has been initialized with /speckit.init
# before running other speckit commands.
#
# Returns JSON:
# - {"status": "continue"} if initialized
# - {"status": "block", "reason": "..."} if not initialized

# Find project root by looking for .claude directory
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.claude" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Main check
PROJECT_ROOT=$(find_project_root)

if [[ -z "$PROJECT_ROOT" ]]; then
    echo '{"status": "block", "reason": "No .claude directory found. Run /speckit.init first to initialize project."}'
    exit 0
fi

CLAUDE_DIR="$PROJECT_ROOT/.claude"
MEMORY_DIR="$CLAUDE_DIR/memory"
CONSTITUTION="$MEMORY_DIR/constitution.md"
STATUS_FILE="$MEMORY_DIR/project-status.md"

# Check for required files
missing=()

if [[ ! -f "$CONSTITUTION" ]]; then
    missing+=("constitution.md")
fi

if [[ ! -d "$MEMORY_DIR" ]]; then
    missing+=("memory directory")
fi

if [[ ${#missing[@]} -gt 0 ]]; then
    echo "{\"status\": \"block\", \"reason\": \"Project not fully initialized. Missing: ${missing[*]}. Run /speckit.init first.\"}"
    exit 0
fi

# Check if project-status.md exists (optional but recommended)
if [[ ! -f "$STATUS_FILE" ]]; then
    echo '{"status": "continue", "warning": "project-status.md not found. Consider running /speckit.init to create it."}'
    exit 0
fi

# All checks passed
echo '{"status": "continue"}'
