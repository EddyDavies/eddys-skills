#!/bin/bash
# PreToolUse(Bash) hook: deny any `open` of an http(s) URL so Claude never
# steals focus by raising a browser. Local files (open report.html) still pass.
cmd=$(jq -r '.tool_input.command // empty')

if printf '%s\n' "$cmd" | grep -qE '(^|[;&|(])[[:space:]]*open[[:space:]]' \
   && printf '%s\n' "$cmd" | grep -qE 'https?://'; then
  cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Never open web URLs with plain open: it steals the user's focus and lands on the wrong desktop. Instead run: diaopen '<url>' which loads the page as a background tab in Dia (no focus steal) in the user's preferred Dia profile and sends a notification. The profile comes from a 'Dia profile: <name>' line in the repo CLAUDE.md, else the user's global ~/.claude/CLAUDE.md, else Dia's active profile; an explicit second argument overrides all of those. If Dia is unavailable, diaopen falls back to the notify+clipboard flow by itself. Opening local files (HTML reports, PDFs) with plain open is still fine."}}
EOF
fi
exit 0
