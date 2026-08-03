---
name: quiet-open
description: Use when setting up or repairing Eddy's no-focus-steal open flow on a machine (arcopen background Arc tabs, mdpreview/mdrefresh MacDown preview, link-blocking hook), when arcopen/mdrefresh/mdpreview are missing or broken, or when asked how Claude should surface web links or markdown previews.
---

# quiet-open: surface links and previews without stealing focus

Everything Claude opens for Eddy must not steal focus or switch desktops. This folder is the canonical, shareable home of that flow; live paths are symlinks into it, so edits made here (or at the live paths) land in git.

## The flow

- **Web links:** never `open <url>`. Run `arcopen '<url>' [space|active]` instead: it creates a background tab in Arc via AppleScript (Arc is never activated) and sends a notification. Space precedence: explicit argument, then an `Arc space: <name>` line in the nearest CLAUDE.md walking up from cwd, then the same line in the global `~/.claude/CLAUDE.md` (the personal default), then Arc's active space. Nothing is hardcoded in the script. The `Arc space:` line must contain only the space name after the colon. Falls back to `notify-web-ready.sh` (notification plus URL on clipboard) when Arc is unavailable. The `block-browser-open.sh` PreToolUse hook enforces this by denying plain `open` of http(s) URLs.
- **Markdown to review:** `mdpreview <file.md>` opens it in MacDown, preview pane only. A PostToolUse hook on Write|Edit runs `mdrefresh` on any edited `.md`, so an open MacDown document reloads automatically when Claude edits the file (close and reopen under the hood, no focus steal, skipped if the document has unsaved edits).
- **Local artifacts (HTML, PDFs, images):** plain `open <path>` is fine and expected.

## Setup on a new machine (or repair)

1. Run `./setup.sh` from this folder. Idempotent: symlinks `bin/` into `~/.local/bin`, `hooks/` into `~/.claude/hooks`, merges the two hook entries into `~/.claude/settings.json` if absent, and symlinks this folder to `~/.claude/skills/quiet-open`. Differing pre-existing files are backed up as `*.pre-quiet-open.bak`.
2. Merge the bullets from `snippets/claude-md-rules.md` into `~/.claude/CLAUDE.md` if they are missing (prose merge, so it is not scripted).
3. First `arcopen` use on a new machine triggers a one-time macOS Automation prompt (terminal controlling Arc); approve it. Same for MacDown on first `mdrefresh`.

## Requirements and quirks

- Requires: Arc, MacDown, `jq`, `python3` (all standard on Eddy's machines). Ghostty gets OSC 777 notifications when a tty is present; otherwise `display notification` is used.
- Arc's AppleScript can stall after long app uptime (AppleEvent timeouts even on `version`); `open -g -a Arc` plus a few minutes, or an Arc restart, recovers it. arcopen already degrades to notify+clipboard when that happens.
- MacDown: never use its `save` AppleScript command (hangs). Its scripting `text` setter does not re-render the preview, which is why mdrefresh closes and reopens. Iterate over documents by index after bulk-fetching `file of documents`; `repeat with d in documents` errors.
- Editing the scripts: edit either the repo copies or the live paths; they are the same files via symlink. Commit in `~/code/eddys-skills` afterwards.
