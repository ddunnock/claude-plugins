---
status: resolved
trigger: "Plugin commands `/plugin add` and `/plugin update` not working correctly - returning \"(no content)\" or opening interactive menu instead of performing the expected action."
created: 2026-01-18T12:00:00Z
updated: 2026-01-18T14:30:00Z
---

## Current Focus

hypothesis: CONFIRMED - Wrong marketplace name in command
test: Verified marketplace configuration and installed plugins
expecting: Commands should work with correct marketplace name
next_action: Report findings to user

## Symptoms

expected: `/plugin add speckit-generator@ddunnock-claude-plugins` should install plugin and show "Installed 1 plugin. Restart Claude Code to load new plugins". `/plugin update speckit-generator@ddunnock-claude-plugins` should update the plugin to latest version.
actual: `/plugin add` returns "(no content)" with no action. `/plugin update` opens the interactive CLI menu instead of performing the update.
errors: Shows "(no content)" message or unexpectedly enters interactive menu
reproduction: Run `/plugin add speckit-generator@ddunnock-claude-plugins` or `/plugin update speckit-generator@ddunnock-claude-plugins` in Claude Code
started: Was working recently, now broken

## Eliminated

- hypothesis: Bug in this repository's code
  evidence: This repository is a plugin marketplace, not the Claude Code CLI. The /plugin command is built-in to Claude Code, not defined here.
  timestamp: 2026-01-18T14:18:00Z

## Evidence

- timestamp: 2026-01-18T14:15:00Z
  checked: ~/.claude/plugins/known_marketplaces.json
  found: Marketplace is registered as "dunnock-plugins" with source github repo "ddunnock/claude-plugins"
  implication: The marketplace name in commands should be "dunnock-plugins", NOT "ddunnock-claude-plugins"

- timestamp: 2026-01-18T14:16:00Z
  checked: ~/.claude/plugins/installed_plugins.json
  found: speckit-generator@dunnock-plugins is installed (version 2.1.0, installed 2026-01-18T14:14:37.131Z, commit b5839879a2e0abadd722aa147351542f50a3cabf)
  implication: The plugin system works correctly when using the right marketplace name

- timestamp: 2026-01-18T14:17:00Z
  checked: .claude-plugin/marketplace.json in this repo
  found: marketplace "name" field is "dunnock-plugins"
  implication: User is using incorrect marketplace name in commands

- timestamp: 2026-01-18T14:25:00Z
  checked: ~/.claude/plugins/marketplaces/dunnock-plugins/ git log
  found: Marketplace clone is on commit b583987 (same as current repo)
  implication: Marketplace is up to date

- timestamp: 2026-01-18T14:26:00Z
  checked: ~/.claude/settings.json enabledPlugins
  found: speckit-generator@dunnock-plugins is enabled
  implication: Plugin is fully configured and active

## Resolution

root_cause: User is using incorrect marketplace name in commands. The GitHub repo is "ddunnock/claude-plugins" but the marketplace NAME (defined in .claude-plugin/marketplace.json and used in plugin install commands) is "dunnock-plugins". Using "ddunnock-claude-plugins" causes Claude Code to fail to find the marketplace.

fix: Use correct marketplace name in commands:
- CORRECT: `/plugin add speckit-generator@dunnock-plugins`
- CORRECT: `/plugin update speckit-generator@dunnock-plugins`
- WRONG: `/plugin add speckit-generator@ddunnock-claude-plugins`

verification: Verified that speckit-generator@dunnock-plugins IS already installed and working (installed today at 14:14:37Z with correct version 2.1.0)

files_changed: []

## Notes

This is NOT a bug in the codebase - it's a user input issue. The marketplace naming convention:
- GitHub repo: `ddunnock/claude-plugins` (username/repo)
- Marketplace name: `dunnock-plugins` (defined in .claude-plugin/marketplace.json)

These are different! The marketplace name is what you use with /plugin commands.
