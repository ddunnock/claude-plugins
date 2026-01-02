#!/usr/bin/env bash
# Validate automation artifacts in .claude directory
#
# Performs the following checks:
#   - Command files: YAML frontmatter, required sections, handoff targets
#   - Scripts: Bash syntax, shellcheck (if available), shebang
#   - Templates: Placeholder consistency
#   - Cross-references: Handoff targets exist, script references valid
#
# Usage: ./validate-automation.sh [OPTIONS] [PATH]
#
# OPTIONS:
#   --json           Output JSON for command parsing
#   --strict         Treat warnings as errors
#   --help, -h       Show help
#
# ARGUMENTS:
#   PATH             Path to .claude directory (default: .claude)
#
# EXAMPLES:
#   ./validate-automation.sh                    # Validate current project
#   ./validate-automation.sh --json             # JSON output
#   ./validate-automation.sh /path/to/.claude   # Specific path

set -e

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

JSON_MODE=false
STRICT_MODE=false
TARGET=""

for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --strict) STRICT_MODE=true ;;
        --help|-h)
            sed -n '2,/^[^#]/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        --*) echo "ERROR: Unknown option '$arg'" >&2; exit 1 ;;
        *) [[ -z "$TARGET" ]] && TARGET="$arg" ;;
    esac
done

# Default to .claude in current directory
[[ -z "$TARGET" ]] && TARGET=".claude"

# ============================================================================
# SETUP
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
log_warning() { $JSON_MODE || echo "⚠️  $*"; }
log_error()   { $JSON_MODE || echo "❌ $*" >&2; }

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

errors=()
warnings=()
info=()
checked_commands=()
checked_scripts=()
checked_templates=()

validate_command() {
    local file="$1"
    local name
    name=$(basename "$file")
    checked_commands+=("$name")
    
    # Check file exists and is readable
    if [[ ! -r "$file" ]]; then
        errors+=("$name: File not readable")
        return
    fi
    
    # Check YAML frontmatter exists
    if ! head -1 "$file" | grep -q "^---$"; then
        errors+=("$name: Missing YAML frontmatter (must start with ---)")
        return
    fi
    
    # Check frontmatter is closed
    local frontmatter_end
    frontmatter_end=$(tail -n +2 "$file" | grep -n "^---$" | head -1 | cut -d: -f1)
    if [[ -z "$frontmatter_end" ]]; then
        errors+=("$name: YAML frontmatter not closed (missing ending ---)")
        return
    fi
    
    # Extract frontmatter for checks
    local frontmatter
    frontmatter=$(head -n $((frontmatter_end + 1)) "$file" | tail -n +2 | head -n -1)
    
    # Check description exists
    if ! echo "$frontmatter" | grep -q "^description:"; then
        errors+=("$name: Missing 'description' in frontmatter")
    fi
    
    # Check for User Input section
    if ! grep -q "## User Input" "$file"; then
        warnings+=("$name: Missing '## User Input' section")
    fi
    
    # Check for $ARGUMENTS reference
    if ! grep -q '\$ARGUMENTS' "$file"; then
        warnings+=("$name: No \$ARGUMENTS reference found")
    fi
    
    # Check handoff targets exist
    local handoffs
    handoffs=$(echo "$frontmatter" | grep -oP 'agent:\s*\K\S+' 2>/dev/null || true)
    for target in $handoffs; do
        # Remove quotes if present
        target=$(echo "$target" | tr -d "'\"")
        local target_file="$(dirname "$file")/${target}.md"
        if [[ ! -f "$target_file" ]]; then
            warnings+=("$name: Handoff target '$target' not found at $target_file")
        fi
    done
    
    # Check for script references
    local script_refs
    script_refs=$(grep -oP '\.claude/scripts/[^`\s]+\.sh' "$file" 2>/dev/null || true)
    for script in $script_refs; do
        # Resolve relative to project root (parent of .claude)
        local project_root
        project_root=$(dirname "$TARGET")
        local script_path="$project_root/$script"
        if [[ ! -f "$script_path" ]]; then
            info+=("$name: Referenced script '$script' not found")
        fi
    done
}

validate_script() {
    local file="$1"
    local name
    name=$(basename "$file")
    checked_scripts+=("$name")
    
    # Check file exists and is readable
    if [[ ! -r "$file" ]]; then
        errors+=("$name: File not readable")
        return
    fi
    
    # Check shebang
    local shebang
    shebang=$(head -1 "$file")
    if [[ ! "$shebang" =~ ^#! ]]; then
        warnings+=("$name: Missing shebang (e.g., #!/usr/bin/env bash)")
    fi
    
    # Bash syntax check
    if ! bash -n "$file" 2>/dev/null; then
        local syntax_error
        syntax_error=$(bash -n "$file" 2>&1 | head -1)
        errors+=("$name: Bash syntax error - $syntax_error")
        return
    fi
    
    # Shellcheck if available
    if command -v shellcheck >/dev/null 2>&1; then
        local sc_errors sc_warnings
        sc_errors=$(shellcheck -S error -f gcc "$file" 2>/dev/null | wc -l)
        sc_warnings=$(shellcheck -S warning -f gcc "$file" 2>/dev/null | wc -l)
        
        [[ "$sc_errors" -gt 0 ]] && errors+=("$name: $sc_errors shellcheck errors")
        [[ "$sc_warnings" -gt 0 ]] && warnings+=("$name: $sc_warnings shellcheck warnings")
    else
        info+=("shellcheck not installed - skipping advanced lint")
    fi
    
    # Check for set -e
    if ! grep -q "^set -e" "$file"; then
        info+=("$name: Consider adding 'set -e' for error handling")
    fi
    
    # Check for --json support (recommended)
    if ! grep -q -- "--json" "$file"; then
        info+=("$name: Consider adding --json option for command integration")
    fi
}

validate_template() {
    local file="$1"
    local name
    name=$(basename "$file")
    checked_templates+=("$name")
    
    # Check file exists and is readable
    if [[ ! -r "$file" ]]; then
        errors+=("$name: File not readable")
        return
    fi
    
    # Extract placeholders
    local placeholders
    placeholders=$(grep -oE '\[[A-Z_]+\]' "$file" | sort -u)
    
    # Check for common required placeholders
    if [[ -n "$placeholders" ]]; then
        info+=("$name: Found placeholders: $(echo $placeholders | tr '\n' ' ')")
    fi
    
    # Check for HTML comments (documentation)
    if ! grep -q "<!--" "$file"; then
        info+=("$name: Consider adding <!-- comments --> for update guidance")
    fi
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

main() {
    # Verify target exists
    if [[ ! -d "$TARGET" ]]; then
        if $JSON_MODE; then
            echo '{"status":"error","message":"Directory not found: '"$TARGET"'","errors":[],"warnings":[]}'
        else
            log_error "Directory not found: $TARGET"
        fi
        exit 1
    fi
    
    log_info "Validating: $TARGET"
    
    # Validate commands
    if [[ -d "$TARGET/commands" ]]; then
        for cmd in "$TARGET"/commands/*.md 2>/dev/null; do
            [[ -f "$cmd" ]] && validate_command "$cmd"
        done
    fi
    
    # Validate bash scripts
    if [[ -d "$TARGET/scripts/bash" ]]; then
        for script in "$TARGET"/scripts/bash/*.sh 2>/dev/null; do
            [[ -f "$script" ]] && validate_script "$script"
        done
    fi
    
    # Validate templates
    if [[ -d "$TARGET/templates" ]]; then
        for template in "$TARGET"/templates/*.md 2>/dev/null; do
            [[ -f "$template" ]] && validate_template "$template"
        done
    fi
    
    # Determine status
    local status="success"
    [[ ${#errors[@]} -gt 0 ]] && status="error"
    $STRICT_MODE && [[ ${#warnings[@]} -gt 0 ]] && status="error"
    
    # ========================================================================
    # OUTPUT
    # ========================================================================
    
    local total_checked=$((${#checked_commands[@]} + ${#checked_scripts[@]} + ${#checked_templates[@]}))
    
    if $JSON_MODE; then
        cat << EOF
{
  "status": "$status",
  "target": "$TARGET",
  "strict_mode": $STRICT_MODE,
  "summary": {
    "commands": ${#checked_commands[@]},
    "scripts": ${#checked_scripts[@]},
    "templates": ${#checked_templates[@]},
    "total": $total_checked
  },
  "errors": $(json_array "${errors[@]}"),
  "warnings": $(json_array "${warnings[@]}"),
  "info": $(json_array "${info[@]}"),
  "checked": {
    "commands": $(json_array "${checked_commands[@]}"),
    "scripts": $(json_array "${checked_scripts[@]}"),
    "templates": $(json_array "${checked_templates[@]}")
  }
}
EOF
    else
        echo "========================================"
        echo "Automation Validation Report"
        echo "========================================"
        echo ""
        echo "Target: $TARGET"
        echo "Strict mode: $STRICT_MODE"
        echo ""
        echo "Checked:"
        echo "  Commands:  ${#checked_commands[@]}"
        echo "  Scripts:   ${#checked_scripts[@]}"
        echo "  Templates: ${#checked_templates[@]}"
        echo ""
        
        if [[ ${#errors[@]} -gt 0 ]]; then
            echo "ERRORS (${#errors[@]}):"
            printf '  ✗ %s\n' "${errors[@]}"
            echo ""
        fi
        
        if [[ ${#warnings[@]} -gt 0 ]]; then
            echo "WARNINGS (${#warnings[@]}):"
            printf '  ⚠ %s\n' "${warnings[@]}"
            echo ""
        fi
        
        if [[ ${#info[@]} -gt 0 ]]; then
            echo "INFO (${#info[@]}):"
            printf '  ℹ %s\n' "${info[@]}"
            echo ""
        fi
        
        if [[ "$status" == "success" ]]; then
            log_success "Validation passed"
        else
            log_error "Validation failed"
            echo ""
            echo "Fix errors before proceeding."
        fi
    fi
    
    [[ "$status" == "success" ]]
}

main
