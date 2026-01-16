#!/bin/bash
# track-task-update.sh
# Tracks task status updates for post-implementation hook verification.
# Logs updates to a session file for verification at stop hook.
#
# Environment variables from Claude Code:
# - CLAUDE_TOOL_INPUT: JSON with file_path and content
# - CLAUDE_SESSION_ID: Current session identifier
#
# Returns JSON:
# - {"status": "continue"} always (tracking only, doesn't block)

# Session tracking directory
TRACKING_DIR="${HOME}/.claude/speckit-sessions"
mkdir -p "$TRACKING_DIR"

# Get session ID or generate one
SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
SESSION_FILE="$TRACKING_DIR/$SESSION_ID.json"

# Initialize session file if needed
if [[ ! -f "$SESSION_FILE" ]]; then
    echo '{
  "session_id": "'"$SESSION_ID"'",
  "started": "'"$(date -Iseconds)"'",
  "tasks_updated": [],
  "status_updated": false,
  "implementation_started": false
}' > "$SESSION_FILE"
fi

# Parse tool input to determine what was updated
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-{}}"
FILE_PATH=$(echo "$TOOL_INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')

if [[ -z "$FILE_PATH" ]]; then
    # No file path found, just continue
    echo '{"status": "continue"}'
    exit 0
fi

# Track updates based on file type
if [[ "$FILE_PATH" == *"-tasks.md" ]]; then
    # Task file updated - extract task IDs from content if possible
    TIMESTAMP=$(date -Iseconds)

    # Update session tracking
    python3 - "$SESSION_FILE" "$FILE_PATH" "$TIMESTAMP" << 'PYTHON' 2>/dev/null || true
import json
import sys

session_file = sys.argv[1]
file_path = sys.argv[2]
timestamp = sys.argv[3]

try:
    with open(session_file, 'r') as f:
        data = json.load(f)
except:
    data = {"tasks_updated": [], "implementation_started": False, "status_updated": False}

# Track that implementation work is happening
data["implementation_started"] = True

# Add this file to updated list if not already there
if file_path not in data.get("tasks_updated", []):
    data.setdefault("tasks_updated", []).append(file_path)

data["last_task_update"] = timestamp

with open(session_file, 'w') as f:
    json.dump(data, f, indent=2)
PYTHON

elif [[ "$FILE_PATH" == *"project-status.md" ]]; then
    # Status file updated
    python3 - "$SESSION_FILE" << 'PYTHON' 2>/dev/null || true
import json
import sys
from datetime import datetime

session_file = sys.argv[1]

try:
    with open(session_file, 'r') as f:
        data = json.load(f)
except:
    data = {}

data["status_updated"] = True
data["status_update_time"] = datetime.now().isoformat()

with open(session_file, 'w') as f:
    json.dump(data, f, indent=2)
PYTHON

fi

# Always continue - this is just tracking
echo '{"status": "continue"}'
