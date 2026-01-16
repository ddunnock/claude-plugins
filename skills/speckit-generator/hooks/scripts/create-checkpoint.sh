#!/bin/bash
# create-checkpoint.sh
# Creates a git checkpoint (tag) before implementation begins.
# Called before /speckit.implement executes any tasks.
#
# Environment variables:
# - CLAUDE_TASK_SELECTION: The task selector (e.g., "TASK-001", "Phase 1")
#
# Returns JSON:
# - {"status": "continue", "checkpoint": "...", "stashed": true/false}
# - {"status": "block", "reason": "..."} if checkpoint cannot be created

# Verify we're in a git repository
if ! git rev-parse --git-dir &> /dev/null; then
    echo '{"status": "block", "reason": "Not in a git repository. Run /speckit.init first to set up git."}'
    exit 0
fi

# Generate checkpoint name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CHECKPOINT_NAME="speckit-checkpoint-$TIMESTAMP"
TASK_SELECTION="${CLAUDE_TASK_SELECTION:-implementation}"

# Check for uncommitted changes
STASHED=false
STASH_NAME=""
if git status --porcelain | grep -q .; then
    STASH_NAME="speckit-pre-implement-stash-$TIMESTAMP"
    if git stash push -m "$STASH_NAME" &> /dev/null; then
        STASHED=true
    else
        # If stash fails, try to commit instead
        git add -A &> /dev/null
        if git commit -m "speckit: Pre-implementation checkpoint for $TASK_SELECTION" &> /dev/null; then
            STASHED=false
        else
            echo '{"status": "block", "reason": "Cannot create checkpoint: uncommitted changes exist and cannot be stashed or committed."}'
            exit 0
        fi
    fi
fi

# Create the checkpoint tag
if ! git tag -a "$CHECKPOINT_NAME" -m "Pre-implementation checkpoint for $TASK_SELECTION" &> /dev/null; then
    # Tag might already exist, try with timestamp suffix
    CHECKPOINT_NAME="${CHECKPOINT_NAME}-$(date +%N | cut -c1-4)"
    if ! git tag -a "$CHECKPOINT_NAME" -m "Pre-implementation checkpoint for $TASK_SELECTION" &> /dev/null; then
        echo '{"status": "block", "reason": "Failed to create checkpoint tag. Check git permissions."}'
        exit 0
    fi
fi

# Get current commit for reference
COMMIT_SHA=$(git rev-parse --short HEAD)

# Output success
cat << EOF
{
  "status": "continue",
  "checkpoint": "$CHECKPOINT_NAME",
  "commit": "$COMMIT_SHA",
  "stashed": $STASHED,
  "stash_name": "$STASH_NAME",
  "task_selection": "$TASK_SELECTION",
  "revert_command": "/speckit.revert $CHECKPOINT_NAME",
  "message": "Checkpoint created. Safe to proceed with implementation."
}
EOF
