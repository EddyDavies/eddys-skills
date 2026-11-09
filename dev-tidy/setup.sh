#!/bin/bash
# setup.sh: install dev-tidy on this machine, idempotently.
#   1. links bin/dev-tidy into ~/.local/bin
#   2. merges two hooks into ~/.claude/settings.json:
#        PostToolUse(Bash)  dev-tidy hook-post  (records which chat started which wrangler / container)
#        SessionEnd         dev-tidy hook-end   (stops what that chat started, quits OrbStack if empty)
#   3. installs a launchd job running `dev-tidy sweep` every 10 minutes
#      (catches chats closed without a clean exit, e.g. a Herdr tab closed under them)
#   4. links this folder into ~/.claude/skills/dev-tidy
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$ROOT/bin/dev-tidy"
mkdir -p "$HOME/.local/bin" "$HOME/.claude/dev-tidy" "$HOME/Library/LaunchAgents"
ln -sfn "$ROOT/bin/dev-tidy" "$HOME/.local/bin/dev-tidy"
[ -L "$HOME/.claude/skills/dev-tidy" ] || ln -s "$ROOT" "$HOME/.claude/skills/dev-tidy"

python3 - "$HOME/.claude/settings.json" "$HOME/.local/bin/dev-tidy" <<'PY'
import json, sys
path, bin_ = sys.argv[1], sys.argv[2]
s = json.load(open(path))
hooks = s.setdefault("hooks", {})
def ensure(event, matcher, cmd):
    for g in hooks.get(event, []):
        if any(h.get("command", "") == cmd for h in g.get("hooks", [])):
            print(f"ok:       {event} {cmd}"); return
    g = {"hooks": [{"type": "command", "command": cmd, "timeout": 180 if event == "SessionEnd" else 10}]}
    if matcher: g["matcher"] = matcher
    hooks.setdefault(event, []).append(g); print(f"added:    {event} {cmd}")
ensure("PostToolUse", "Bash", f"{bin_} hook-post")
ensure("SessionEnd", None, f"{bin_} hook-end")
json.dump(s, open(path, "w"), indent=2)
PY

PLIST="$HOME/Library/LaunchAgents/com.eddydavies.dev-tidy.plist"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.eddydavies.dev-tidy</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$ROOT/bin/dev-tidy</string><string>sweep</string></array>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
  <key>StartInterval</key><integer>600</integer>
  <key>StandardErrorPath</key><string>$HOME/.claude/dev-tidy/sweep.err</string>
</dict></plist>
EOF
launchctl bootout "gui/$(id -u)/com.eddydavies.dev-tidy" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "launchd:  com.eddydavies.dev-tidy every 10 min"
