#!/bin/bash
set -uo pipefail
# check-git.sh
# Validates git is available and project is in a git repository.
# Called during /speckit.init to ensure checkpoint/revert will work.
#
# Returns JSON:
# - {"status": "continue", "git_version": "...", "is_repo": true/false}
# - {"status": "block", "reason": "..."} if git not available

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo '{"status": "block", "reason": "Git is not installed. Please install git to enable checkpoint/revert functionality. See https://git-scm.com/downloads"}'
    exit 0
fi

# Get git version
GIT_VERSION=$(git --version 2>/dev/null | sed 's/git version //')

# Check if we're in a git repository
IS_REPO=false
REPO_ROOT=""
if git rev-parse --git-dir &> /dev/null; then
    IS_REPO=true
    REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
fi

# Check for uncommitted changes
UNCOMMITTED_COUNT=0
if [ "$IS_REPO" = true ]; then
    UNCOMMITTED_COUNT=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
fi

# Build response
cat << EOF
{
  "status": "continue",
  "git_version": "$GIT_VERSION",
  "is_repo": $IS_REPO,
  "repo_root": "$REPO_ROOT",
  "uncommitted_changes": $UNCOMMITTED_COUNT,
  "message": "Git available. $([ "$IS_REPO" = true ] && echo "Repository detected." || echo "Not in a git repository - will offer to initialize.")"
}
EOF
