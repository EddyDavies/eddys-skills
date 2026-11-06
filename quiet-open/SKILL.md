---
name: quiet-open
description: Use when setting up or repairing Eddy's no-focus-steal open flow on a machine (diaopen background Dia tabs, mdpreview/mdrefresh MacDown preview, link-blocking hook), when diaopen/arcopen/mdrefresh/mdpreview are missing or broken, or when asked how Claude should surface web links or markdown previews.
---

# quiet-open: surface links and previews without stealing focus

Everything Claude opens for Eddy must not steal focus or switch desktops. This folder is the canonical, shareable home of that flow; live paths are symlinks into it, so edits made here (or at the live paths) land in git.

## The flow

- **Web links and HTML artifacts:** never `open <url>`. Run `diaopen '<url-or-path>' [profile|active]` instead: it creates a background tab in Dia via AppleScript (Dia is never activated) and sends a notification; clicking it runs `diafocus`, which brings Dia forward on that tab. Profile precedence: explicit argument, then a `Dia profile: <name>` line in the nearest CLAUDE.local.md / CLAUDE.md / AGENTS.md walking up from cwd, then the same line in the global `~/.claude/CLAUDE.md` (the personal default), then Dia's active profile. A legacy `Arc space: <name>` line is still read when a file has no `Dia profile:` line. Profile names match case-insensitively; an unknown name falls back to the active profile. An unpinned tab already showing the page is reloaded instead of duplicated. Falls back to `notify-web-ready.sh` (notification plus URL on clipboard) when Dia is unavailable. `arcopen` is a symlink to `diaopen`, kept so old references keep working. The `block-browser-open.sh` PreToolUse hook enforces this by denying plain `open` of http(s) URLs.
- **Markdown to review:** `mdpreview <file.md>` opens it in MacDown, preview pane only. A PostToolUse hook on Write|Edit runs `mdrefresh` on any edited `.md`, so an open MacDown document reloads automatically when Claude edits the file (close and reopen under the hood, no focus steal, skipped if the document has unsaved edits).
- **PDFs and images:** plain `open <path>` is fine and expected.

## Setup on a new machine (or repair)

1. Run `./setup.sh` from this folder. Idempotent: symlinks `bin/` into `~/.local/bin`, `hooks/` into `~/.claude/hooks`, merges the two hook entries into `~/.claude/settings.json` if absent, and symlinks this folder to `~/.claude/skills/quiet-open`. Differing pre-existing files are backed up as `*.pre-quiet-open.bak`.
2. Merge the bullets from `snippets/claude-md-rules.md` into `~/.claude/CLAUDE.md` if they are missing (prose merge, so it is not scripted).
3. First `diaopen` use on a new machine triggers a one-time macOS Automation prompt (terminal controlling Dia); approve it. Same for MacDown on first `mdrefresh`.

## Requirements and quirks

- Requires: Dia, MacDown, `jq`, `python3`, `terminal-notifier` optional (all standard on Eddy's machines). Ghostty gets OSC 777 notifications when a tty is present; otherwise `display notification` is used.
- Dia scripting (tested Nov 2026): profiles are elements of a window and play the role Arc spaces did. `make new tab` inside a non-active profile switches Dia's visible profile, so diaopen makes the tab in the active profile and then `move`s it, which leaves the profile alone. `focus` (tab or profile) raises Dia and steals focus, so diaopen only calls it when Dia is already frontmost (to put back the tab you were looking at, which Dia changes when the new tab is moved away). There is no `reload` command; setting a tab's URL to itself reloads it. Never name an AppleScript variable `at` (reserved word, gives a confusing syntax error).
- MacDown: never use its `save` AppleScript command (hangs). Its scripting `text` setter does not re-render the preview, which is why mdrefresh closes and reopens. Iterate over documents by index after bulk-fetching `file of documents`; `repeat with d in documents` errors.
- Editing the scripts: edit either the repo copies or the live paths; they are the same files via symlink. Commit in `~/code/eddys-skills` afterwards.
