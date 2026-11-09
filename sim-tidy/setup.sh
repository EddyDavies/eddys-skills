#!/bin/bash
# setup.sh: install sim-tidy on this machine, idempotently.
#   1. links bin/sim-tidy into ~/.local/bin
#   2. merges two hooks into ~/.claude/settings.json:
#        PostToolUse(Bash)  sim-tidy hook-post  (records which chat touched which sim)
#        SessionEnd         sim-tidy hook-end   (shuts down the sims that chat used)
#   3. installs a launchd job running `sim-tidy sweep` every 2 hours
#   4. links this folder into ~/.claude/skills/sim-tidy
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "$ROOT/bin/sim-tidy"
mkdir -p "$HOME/.local/bin" "$HOME/.claude/sim-tidy" "$HOME/Library/LaunchAgents"
ln -sfn "$ROOT/bin/sim-tidy" "$HOME/.local/bin/sim-tidy"
[ -L "$HOME/.claude/skills/sim-tidy" ] || ln -s "$ROOT" "$HOME/.claude/skills/sim-tidy"

python3 - "$HOME/.claude/settings.json" "$HOME/.local/bin/sim-tidy" <<'PY'
import json, sys
path, bin_ = sys.argv[1], sys.argv[2]
s = json.load(open(path))
hooks = s.setdefault("hooks", {})
def ensure(event, matcher, cmd):
    for g in hooks.get(event, []):
        if any("sim-tidy" in h.get("command", "") and cmd.split()[-1] in h["command"] for h in g.get("hooks", [])):
            print(f"ok:       {event} {cmd}"); return
    g = {"hooks": [{"type": "command", "command": cmd, "timeout": 120 if event == "SessionEnd" else 10}]}
    if matcher: g["matcher"] = matcher
    hooks.setdefault(event, []).append(g); print(f"added:    {event} {cmd}")
ensure("PostToolUse", "Bash", f"{bin_} hook-post")
ensure("SessionEnd", None, f"{bin_} hook-end")
json.dump(s, open(path, "w"), indent=2)
PY

PLIST="$HOME/Library/LaunchAgents/com.eddydavies.sim-tidy.plist"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.eddydavies.sim-tidy</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$ROOT/bin/sim-tidy</string><string>sweep</string></array>
  <key>StartInterval</key><integer>7200</integer>
  <key>StandardErrorPath</key><string>$HOME/.claude/sim-tidy/sweep.err</string>
</dict></plist>
EOF
launchctl bootout "gui/$(id -u)/com.eddydavies.sim-tidy" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "launchd:  com.eddydavies.sim-tidy every 2h"
