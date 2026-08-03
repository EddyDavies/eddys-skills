#!/bin/bash
# setup.sh: install the quiet-open flow on this machine, idempotently.
#
# What it does:
#   1. Symlinks bin/ scripts (arcopen, mdrefresh, mdpreview) into ~/.local/bin
#   2. Symlinks hooks/ scripts into ~/.claude/hooks
#   3. Merges the two required hook entries into ~/.claude/settings.json:
#      PreToolUse(Bash) block-browser-open, PostToolUse(Write|Edit) mdrefresh
#   4. Symlinks this skill folder into ~/.claude/skills/quiet-open
#
# What it deliberately does NOT do: edit ~/.claude/CLAUDE.md. Prose merges
# are not safe to script; see snippets/claude-md-rules.md and add the
# bullets yourself (or have Claude merge them) if they are missing.
#
# Safe to re-run. Existing non-symlink files that differ from the repo copy
# are backed up as <name>.pre-quiet-open.bak before being replaced.
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
    cp "$dst" "$dst.pre-quiet-open.bak"
    echo "backup:   $dst.pre-quiet-open.bak"
  fi
  ln -sf "$src" "$dst"
  echo "linked:   $dst -> $src"
}

for b in arcopen mdrefresh mdpreview; do
  link "$ROOT/bin/$b" "$HOME/.local/bin/$b"
done
for h in block-browser-open.sh notify-web-ready.sh; do
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

# PreToolUse(Bash): deny plain `open` of http(s) URLs
if not has_command("PreToolUse", "block-browser-open.sh"):
    pre = hooks.setdefault("PreToolUse", [])
    bash_group = next((g for g in pre if g.get("matcher") == "Bash"), None)
    if bash_group is None:
        bash_group = {"matcher": "Bash", "hooks": []}
        pre.append(bash_group)
    bash_group["hooks"].append({
        "type": "command",
        "command": f"bash '{home}/.claude/hooks/block-browser-open.sh'",
        "timeout": 10,
    })
    changed = True

# PostToolUse(Write|Edit): auto-refresh MacDown for markdown edits
if not has_command("PostToolUse", "mdrefresh"):
    hooks.setdefault("PostToolUse", []).insert(0, {
        "matcher": "Write|Edit",
        "hooks": [{
            "type": "command",
            "command": (
                "jq -r '.tool_input.file_path // .tool_response.filePath // empty' "
                "| { read -r f; case \"$f\" in *.md|*.markdown) "
                f"{home}/.local/bin/mdrefresh \"$f\" ;; esac; }} 2>/dev/null || true"
            ),
            "timeout": 15,
            "async": True,
            "statusMessage": "Refreshing MacDown preview",
        }],
    })
    changed = True

if changed:
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"settings: updated {path}")
else:
    print(f"settings: ok {path}")
PY

mkdir -p "$HOME/.claude/skills"
ln -sfn "$ROOT" "$HOME/.claude/skills/quiet-open"
echo "skill:    ~/.claude/skills/quiet-open -> $ROOT"

echo
echo "Done. Remaining manual step: ensure the bullets in"
echo "  $ROOT/snippets/claude-md-rules.md"
echo "are present in ~/.claude/CLAUDE.md (see that file for why)."
