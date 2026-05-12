#!/usr/bin/env bash
# PostToolUse hook script — logs every Read of a study-session reference/method
# into ~/study-journal/.session-log/<UTC-date>.jsonl as one JSON line.
#
# Invoked by Claude Code's PostToolUse hook (matcher: "Read") via
# ~/.claude/settings.json. Stdin receives the hook payload as JSON:
#   {"hook_event_name":"PostToolUse","tool_name":"Read",
#    "tool_input":{"file_path":"...","offset":...,"limit":...},
#    "tool_response":{"file":{"filePath":"...","numLines":N,"startLine":1,"totalLines":N}},
#    "session_id":"...", ...}
#
# We only care when file_path matches one of:
#   - <anything>/study-session/references/...
#   - <anything>/study-session/references/methods/...
#   - <anything>/study-session/SKILL.md
#
# Exits silently. PostToolUse cannot block, so failures are non-blocking;
# we redirect errors to /dev/null and exit 0 regardless to avoid noisy hook
# warnings on edge cases (jq missing, log dir unwriteable, etc.).

set +e

input=$(cat)

# Need jq to parse the payload reliably. If jq is missing, fail silent.
if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

tool_name=$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)
if [ "$tool_name" != "Read" ]; then
    exit 0
fi

file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)

if [ -z "$file_path" ]; then
    exit 0
fi

# Match the study-session skill's own files. Use a simple substring grep so it
# tolerates symlinked paths (~/work/claude-skills/study-session, ~/.claude/skills/study-session).
case "$file_path" in
    */study-session/references/methods/*)   kind="method";   rel=${file_path##*/study-session/} ;;
    */study-session/references/*)           kind="reference"; rel=${file_path##*/study-session/} ;;
    */study-session/SKILL.md)               kind="skill";    rel="SKILL.md" ;;
    *)                                       exit 0 ;;
esac

log_dir="$HOME/study-journal/.session-log"
mkdir -p "$log_dir" 2>/dev/null || exit 0

# Local time (system tz, e.g. KST) for filename + ISO8601 entry.
# BSD/macOS `date` doesn't support %:z, so we insert the colon manually.
log_date=$(date +%Y-%m-%d)
ts_raw=$(date "+%Y-%m-%dT%H:%M:%S%z")   # e.g. 2026-05-12T15:04:59+0900
ts="${ts_raw:0:22}:${ts_raw:22}"        # → 2026-05-12T15:04:59+09:00
log_file="$log_dir/$log_date.jsonl"

# Use jq -n to compose a safely-escaped JSON line.
jq -nc \
    --arg t "$ts" \
    --arg kind "$kind" \
    --arg path "$rel" \
    --arg sid "$session_id" \
    '{t:$t, event:"read", kind:$kind, path:$path, session_id:$sid}' \
    >> "$log_file" 2>/dev/null

exit 0
