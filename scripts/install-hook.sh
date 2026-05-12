#!/usr/bin/env bash
# Register the study-session PostToolUse hook in ~/.claude/settings.json.
#
# Idempotent: re-running replaces the existing Read matcher entry (doesn't
# duplicate). Preserves all other top-level keys, all hook events other than
# PostToolUse, and all PostToolUse matchers other than "Read".

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required. Install with 'brew install jq' (macOS)." >&2
    exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL_HOME="$(dirname "$SCRIPT_DIR")"
HOOK_SCRIPT="$SKILL_HOME/scripts/log_reference_read.sh"
SETTINGS="$HOME/.claude/settings.json"

if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "Error: hook script not found at $HOOK_SCRIPT" >&2
    exit 1
fi

# Use a $HOME-relative command string so the resulting settings.json is
# portable across machines (same user $HOME path on each).
HOOK_CMD='$HOME/.claude/skills/study-session/scripts/log_reference_read.sh'

mkdir -p "$(dirname "$SETTINGS")"
if [ ! -f "$SETTINGS" ]; then
    echo "{}" > "$SETTINGS"
fi

backup="$SETTINGS.bak.$(date +%Y%m%d-%H%M%S)"
cp "$SETTINGS" "$backup"

tmp=$(mktemp)
jq --arg cmd "$HOOK_CMD" '
  .hooks = (.hooks // {})
  | .hooks.PostToolUse = (.hooks.PostToolUse // [])
  | .hooks.PostToolUse = (
      [.hooks.PostToolUse[] | select(.matcher != "Read")]
      + [{matcher: "Read", hooks: [{type: "command", command: $cmd}]}]
    )
' "$SETTINGS" > "$tmp"

if ! python3 -c "import json,sys; json.load(open('$tmp'))" 2>/dev/null; then
    echo "Error: merged settings.json failed to validate — aborting." >&2
    echo "       Original preserved at: $backup" >&2
    rm "$tmp"
    exit 1
fi

mv "$tmp" "$SETTINGS"

echo "✓ Registered PostToolUse(Read) hook in $SETTINGS"
echo "  Command: $HOOK_CMD"
echo "  Backup:  $backup"
echo
echo "Next time the skill (or you) calls Read on a study-session reference/method"
echo "file, a line will be appended to:"
echo "  ~/study-journal/.session-log/<KST-date>.jsonl"
echo
echo "To uninstall: delete the matcher entry from ~/.claude/settings.json by hand,"
echo "or restore from the backup above."
