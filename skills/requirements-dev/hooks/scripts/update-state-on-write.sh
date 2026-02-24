#!/usr/bin/env bash
# Auto-update state.json when .requirements-dev/*.md artifacts are written.
#
# Called by PostToolUse hook when Write targets .requirements-dev/*.md files.
# Updates the session's artifact tracking in state.json.
#
# Security model:
#   - Triggered only by Write tool matching **/.requirements-dev/*.md (hook matcher)
#   - Input path is validated: must contain only safe characters (alphanumeric,
#     hyphens, underscores, dots, slashes)
#   - Only known artifact filenames are handled (case statement whitelist)
#   - All variables are quoted to prevent word splitting / globbing

set -euo pipefail

WRITTEN_PATH="${1:-}"
SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"

# Validate input path contains only safe characters
# Allow: alphanumeric, hyphens, underscores, dots, forward slashes, spaces
if [[ "$WRITTEN_PATH" =~ [^a-zA-Z0-9_./\ -] ]]; then
    echo "Error: Path contains unexpected characters, skipping." >&2
    exit 0
fi

# Reject empty path
if [[ -z "$WRITTEN_PATH" ]]; then
    exit 0
fi

# Resolve the state file relative to the written path's directory
# Handle both relative (.requirements-dev/FOO.md) and absolute (/path/to/.requirements-dev/FOO.md) paths
if [[ "$WRITTEN_PATH" == /* ]]; then
    # Absolute path — derive project root from path
    PROJECT_DIR="${WRITTEN_PATH%%/.requirements-dev/*}"
    STATE_FILE="$PROJECT_DIR/.requirements-dev/state.json"
else
    STATE_FILE=".requirements-dev/state.json"
fi

# Only proceed if state file exists
if [ ! -f "$STATE_FILE" ]; then
    exit 0
fi

# Only proceed if the written file is in .requirements-dev/
if [[ "$WRITTEN_PATH" != .requirements-dev/* ]] && [[ "$WRITTEN_PATH" != */.requirements-dev/* ]]; then
    exit 0
fi

# Extract filename
FILENAME=$(basename "$WRITTEN_PATH")

# Map artifact filenames to phases and artifact keys (whitelist only)
case "$FILENAME" in
    REQUIREMENTS-SPECIFICATION.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact deliver "$WRITTEN_PATH" --key specification_artifact 2>/dev/null || true
        ;;
    TRACEABILITY-MATRIX.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact deliver "$WRITTEN_PATH" --key traceability_artifact 2>/dev/null || true
        ;;
    VERIFICATION-MATRIX.md)
        python3 "$SCRIPTS_DIR/update_state.py" --state "$STATE_FILE" set-artifact deliver "$WRITTEN_PATH" --key verification_artifact 2>/dev/null || true
        ;;
esac
