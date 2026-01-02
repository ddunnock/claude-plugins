#!/usr/bin/env bash
# [Script Title]
#
# [2-3 sentence description of what this script does]
#
# Usage: ./[script-name].sh [OPTIONS] [ARGS...]
#
# OPTIONS:
#   --json           Output JSON for command parsing
#   --strict         Enable strict validation
#   --dry-run        Show what would be done without doing it
#   --help, -h       Show this help message
#
# ARGUMENTS:
#   [ARG_NAME]       [Description of argument]
#
# EXAMPLES:
#   ./[script-name].sh                          # Basic usage
#   ./[script-name].sh --json                   # JSON output for commands
#   ./[script-name].sh --strict path/to/dir     # With options and args

set -e

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

JSON_MODE=false
STRICT_MODE=false
DRY_RUN=false
ARGS=()

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --strict) STRICT_MODE=true ;;
        --dry-run) DRY_RUN=true ;;
        --help|-h)
            sed -n '2,/^[^#]/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        --*)
            echo "ERROR: Unknown option '$arg'. Use --help for usage." >&2
            exit 1
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
done

# ============================================================================
# SETUP
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common utilities if available
if [[ -f "$SCRIPT_DIR/common.sh" ]]; then
    source "$SCRIPT_DIR/common.sh"
else
    # Inline minimal utilities
    log_info()    { $JSON_MODE || echo "ℹ️  $*"; }
    log_success() { $JSON_MODE || echo "✅ $*"; }
    log_warning() { $JSON_MODE || echo "⚠️  $*"; }
    log_error()   { $JSON_MODE || echo "❌ $*" >&2; }
    
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
    
    find_project_root() {
        local dir="$PWD"
        while [[ "$dir" != "/" ]]; do
            [[ -d "$dir/.claude" || -f "$dir/package.json" || -f "$dir/pyproject.toml" ]] && echo "$dir" && return
            dir="$(dirname "$dir")"
        done
        echo "$PWD"
    }
fi

PROJECT_ROOT=$(find_project_root)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# [Add script-specific helper functions here]

# ============================================================================
# MAIN LOGIC
# ============================================================================

main() {
    local status="success"
    local results=()
    local errors=()
    local warnings=()
    
    log_info "Starting [script name]..."
    
    # [TODO: Implement main logic here]
    # 
    # Example structure:
    #
    # # Validate inputs
    # if [[ ${#ARGS[@]} -eq 0 ]]; then
    #     errors+=("No arguments provided")
    #     status="error"
    # fi
    #
    # # Process each item
    # for item in "${ARGS[@]}"; do
    #     if $DRY_RUN; then
    #         log_info "Would process: $item"
    #         results+=("Would process: $item")
    #     else
    #         # Actual processing
    #         results+=("Processed: $item")
    #     fi
    # done
    #
    # # Strict mode checks
    # if $STRICT_MODE && [[ ${#warnings[@]} -gt 0 ]]; then
    #     status="error"
    # fi
    
    # Placeholder implementation
    results+=("Script executed successfully")
    
    # ========================================================================
    # OUTPUT RESULTS
    # ========================================================================
    
    if $JSON_MODE; then
        cat << EOF
{
  "status": "$status",
  "project_root": "$PROJECT_ROOT",
  "strict_mode": $STRICT_MODE,
  "dry_run": $DRY_RUN,
  "results": $(json_array "${results[@]}"),
  "errors": $(json_array "${errors[@]}"),
  "warnings": $(json_array "${warnings[@]}")
}
EOF
    else
        echo "========================================"
        echo "[Script Title] Results"
        echo "========================================"
        echo ""
        echo "Project: $PROJECT_ROOT"
        $DRY_RUN && echo "Mode: DRY RUN"
        $STRICT_MODE && echo "Mode: STRICT"
        echo ""
        
        if [[ ${#results[@]} -gt 0 ]]; then
            echo "Results:"
            printf '  • %s\n' "${results[@]}"
            echo ""
        fi
        
        if [[ ${#warnings[@]} -gt 0 ]]; then
            echo "Warnings:"
            printf '  ⚠ %s\n' "${warnings[@]}"
            echo ""
        fi
        
        if [[ ${#errors[@]} -gt 0 ]]; then
            echo "Errors:"
            printf '  ✗ %s\n' "${errors[@]}"
            echo ""
        fi
        
        if [[ "$status" == "success" ]]; then
            log_success "Completed successfully"
        else
            log_error "Completed with errors"
        fi
    fi
    
    [[ "$status" == "success" ]] && exit 0 || exit 1
}

main "$@"
