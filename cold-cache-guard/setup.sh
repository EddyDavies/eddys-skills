#!/bin/bash
# setup.sh: install cold-cache-guard on this machine, idempotently.
#
# What it does:
#   1. Symlinks hooks/ scripts into ~/.claude/hooks
#   2. Adds the UserPromptSubmit hook entry to ~/.claude/settings.json if absent
#   3. Wires usage-log.sh into the statusline: sets it as the statusline when
#      none is configured, otherwise prints the line to add to yours
#   4. Symlinks this skill folder into ~/.claude/skills/cold-cache-guard
#
# Safe to re-run. Existing non-symlink files that differ from the repo copy
# are backed up as <name>.pre-cold-cache-guard.bak before being replaced.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

link() { # link <repo-file> <live-path>
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ -L "$dst" && "$(readlink "$dst")" == "$src" ]]; then
    echo "ok:       $dst"
    return
  fi
  if [[ -e "$dst" && ! -L "$dst" ]] && ! cmp -s "$src" "$dst"; then
    cp "$dst" "$dst.pre-cold-cache-guard.bak"
    echo "backup:   $dst.pre-cold-cache-guard.bak"
  fi
  ln -sf "$src" "$dst"
  echo "linked:   $dst -> $src"
}

for h in cold-cache-guard.py usage-log.sh; do
  link "$ROOT/hooks/$h" "$HOME/.claude/hooks/$h"
done

python3 - "$HOME/.claude/settings.json" <<'PY'
import json, os, sys

path = sys.argv[1]
home = os.path.expanduser("~")
try:
    with open(path) as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}

hooks = settings.setdefault("hooks", {})
changed = False

def has_command(event, needle):
    for group in hooks.get(event, []):
        for h in group.get("hooks", []):
            if needle in h.get("command", ""):
                return True
    return False

if not has_command("UserPromptSubmit", "cold-cache-guard.py"):
    hooks.setdefault("UserPromptSubmit", []).append({"hooks": [{
        "type": "command",
        "command": f"python3 '{home}/.claude/hooks/cold-cache-guard.py'",
        "timeout": 15,
    }]})
    changed = True

status = settings.get("statusLine")
logger = f"{home}/.claude/hooks/usage-log.sh"
if not status:
    settings["statusLine"] = {"type": "command", "command": f"bash '{logger}'"}
    changed = True
    print("statusline: none configured, set to usage-log.sh (logs usage, shows nothing)")
else:
    cmd = os.path.expanduser(status.get("command", ""))
    script = cmd.split()[0].strip("'\"") if cmd else ""
    wired = "usage-log.sh" in cmd
    if not wired and script and os.path.isfile(script):
        wired = "usage-log.sh" in open(script).read()
    if wired:
        print("statusline: ok, already pipes into usage-log.sh")
    else:
        print("statusline: yours doesn't log plan usage yet. Add this line right after it reads stdin into $input:")
        print("  printf '%s' \"$input\" | \"$HOME/.claude/hooks/usage-log.sh\"")

if changed:
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"settings: updated {path}")
else:
    print(f"settings: ok {path}")
PY

mkdir -p "$HOME/.claude/skills"
ln -sfn "$ROOT" "$HOME/.claude/skills/cold-cache-guard"
echo "skill:    ~/.claude/skills/cold-cache-guard -> $ROOT"
