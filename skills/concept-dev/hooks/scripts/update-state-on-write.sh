#!/usr/bin/env bash
# Auto-update state.json when .concept-dev/*.md artifacts are written.
#
# Called by PostToolUse hook when Write targets .concept-dev/*.md files.
# Updates the session's last_updated timestamp.

set -euo pipefail

WRITTEN_PATH="${1:-}"
SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"

# Resolve the state file relative to the written path's directory
# Handle both relative (.concept-dev/FOO.md) and absolute (/path/to/.concept-dev/FOO.md) paths
if [[ "$WRITTEN_PATH" == /* ]]; then
    # Absolute path — derive project root from path
    PROJECT_DIR=$(echo "$WRITTEN_PATH" | sed 's|/\.concept-dev/.*||')
    STATE_FILE="$PROJECT_DIR/.concept-dev/state.json"
else
    STATE_FILE=".concept-dev/state.json"
fi

# Only proceed if state file exists
if [ ! -f "$STATE_FILE" ]; then
    exit 0
fi

# Only proceed if the written file is in .concept-dev/
if [[ "$WRITTEN_PATH" != .concept-dev/* ]] && [[ "$WRITTEN_PATH" != */.concept-dev/* ]]; then
    exit 0
fi

# Extract filename
FILENAME=$(basename "$WRITTEN_PATH")

# Map artifact filenames to phases and artifact keys
case "$FILENAME" in
    IDEAS.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact spitball "$WRITTEN_PATH" 2>/dev/null || true
        ;;
    PROBLEM-STATEMENT.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact problem "$WRITTEN_PATH" 2>/dev/null || true
        ;;
    BLACKBOX.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact blackbox "$WRITTEN_PATH" 2>/dev/null || true
        ;;
    DRILLDOWN.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact drilldown "$WRITTEN_PATH" 2>/dev/null || true
        ;;
    CONCEPT-DOCUMENT.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact document "$WRITTEN_PATH" --key concept_doc_artifact 2>/dev/null || true
        ;;
    SOLUTION-LANDSCAPE.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact document "$WRITTEN_PATH" --key solution_landscape_artifact 2>/dev/null || true
        ;;
esac
