#!/bin/bash
set -uo pipefail
# check-checkpoint.sh
# Validates that checkpoints exist before allowing revert.
# Called before /speckit.revert executes.
#
# Environment variables:
# - CLAUDE_CHECKPOINT_TARGET: Specific checkpoint to revert to (optional)
#
# Returns JSON:
# - {"status": "continue", "checkpoints": [...], "target": "..."}
# - {"status": "block", "reason": "..."} if no checkpoints exist

# Verify we're in a git repository
if ! git rev-parse --git-dir &> /dev/null; then
    echo '{"status": "block", "reason": "Not in a git repository. Cannot revert."}'
    exit 0
fi

# List all speckit checkpoints
CHECKPOINTS=$(git tag -l "speckit-checkpoint-*" --sort=-creatordate 2>/dev/null)

if [ -z "$CHECKPOINTS" ]; then
    echo '{"status": "block", "reason": "No speckit checkpoints found. Nothing to revert to. Checkpoints are created automatically before /speckit.implement runs."}'
    exit 0
fi

# Get checkpoint count
CHECKPOINT_COUNT=$(echo "$CHECKPOINTS" | wc -l | tr -d ' ')

# Get most recent checkpoint
LATEST_CHECKPOINT=$(echo "$CHECKPOINTS" | head -1)

# Get target checkpoint if specified
TARGET="${CLAUDE_CHECKPOINT_TARGET:-$LATEST_CHECKPOINT}"

# Verify target checkpoint exists
if ! git rev-parse "$TARGET" &> /dev/null; then
    echo "{\"status\": \"block\", \"reason\": \"Checkpoint '$TARGET' not found. Use /speckit.revert --list to see available checkpoints.\"}"
    exit 0
fi

# Get checkpoint details
CHECKPOINT_DATE=$(git log -1 --format="%ci" "$TARGET" 2>/dev/null)
CHECKPOINT_MSG=$(git tag -l -n1 "$TARGET" 2>/dev/null | sed "s/^$TARGET[[:space:]]*//")

# Get files that would be affected
FILES_CHANGED=$(git diff --name-only HEAD "$TARGET" 2>/dev/null | wc -l | tr -d ' ')

# Build checkpoint list (limited to 5 most recent)
CHECKPOINT_LIST=$(echo "$CHECKPOINTS" | head -5 | while read tag; do
    date=$(git log -1 --format="%ci" "$tag" 2>/dev/null | cut -d' ' -f1,2)
    echo "    {\"tag\": \"$tag\", \"date\": \"$date\"}"
done | paste -sd ',' -)

cat << EOF
{
  "status": "continue",
  "checkpoint_count": $CHECKPOINT_COUNT,
  "target": "$TARGET",
  "target_date": "$CHECKPOINT_DATE",
  "target_message": "$CHECKPOINT_MSG",
  "files_to_revert": $FILES_CHANGED,
  "latest_checkpoint": "$LATEST_CHECKPOINT",
  "recent_checkpoints": [
$CHECKPOINT_LIST
  ],
  "message": "Checkpoint '$TARGET' found. Ready to revert."
}
EOF
