---
name: cold-cache-guard
description: Use when setting up or repairing the cold cache guard (the UserPromptSubmit hook that blocks a message to a big, idle Claude Code chat and offers a fresh-chat paste instead), when its block message, plan-limit numbers or clipboard paste look wrong, or when asked what the ❄ ↻ 📋 block means.
---

# cold-cache-guard: don't rebuild a cold cache by accident

Claude Code's prompt cache expires after its TTL (1 hour on these sessions). The next message to a big chat after that re-bills the whole context as a cache write. On a subscription that costs plan allowance, not money: one message to an idle 300k chat can eat a large share of the 5h window.

The hook catches that message before it is sent, writes restart notes from the transcript for free, and puts a ready paste for a new chat on the clipboard.

## What the block looks like

```
❄ nothing sent · idle 3h 5m · 5h ░░░░░░░░░░ 1% · wk ▓▓▓▓▓▓▓▓░░ 77%

↻  214k  5h 1→18%     wk 77→80%
📋  65k  5h 1→6%      wk 77→78%    ⟨63k+2k⟩

Context: this picks up an earlier session. Read ~/.claude/handoffs/<project>/<stamp>.md first (and any images it lists).
```

Key:

- **❄** the cache is cold and nothing was sent. The bars are your current 5h and weekly plan usage.
- **↻** continue here: send the same message again. The second send always goes through.
- **📋** start fresh: paste the clipboard into a new chat. It holds the Context line and then your message (pasted-text wrappers removed).
- **12→21%** where that limit is now, and where it would land after that path's cache write.
- **⟨63k+2k⟩** a fresh chat's base context (system prompt, tools, CLAUDE.md) plus the notes.
- **🖼 2 saved** images pasted with the blocked message, copied next to the notes so the new chat can open them.

Claude Code then prints your message under "Original prompt:" itself, and indents the whole block. Copy from the clipboard, not the screen.

## How the plan numbers work

Hooks never see plan limits. The statusline does (`rate_limits.five_hour` and `seven_day`), so `hooks/usage-log.sh`, piped from the statusline, logs each change in those percentages next to each session's running list cost to `~/.claude/state/usage-log.jsonl`. The hook compares how far each limit rose with the cost that ran in the same stretches over the last 7 days (skipping stretches with a reset) to get points per unit, then applies it to each path's cache write (tokens × 2 × list input price for a 1h TTL write). Until a limit has moved 3 points it shows `12→?%`.

These are estimates: limits move in whole points, Anthropic doesn't publish their weighting, and parallel chats blur the calibration. The fresh-chat figure is a ceiling, as its base is often already cached by another chat in the project.

## Setup on a new machine (or repair)

1. Run `./setup.sh` from this folder. Idempotent: symlinks `hooks/` into `~/.claude/hooks`, adds the UserPromptSubmit entry to `~/.claude/settings.json` if absent, wires `usage-log.sh` into the statusline (sets it as the statusline when none exists; otherwise prints the one line to add to yours), and symlinks this folder to `~/.claude/skills/cold-cache-guard`.
2. Requires `python3` (stdlib only), `jq` and macOS `pbcopy`.

## Tuning

Env vars: `COLD_CACHE_IDLE_MIN` (default 55), `COLD_CACHE_MIN_TOKENS` (default 200000), `COLD_CACHE_OFF=1` to disable.

## Testing a change

Run the hook by hand against a real transcript with the thresholds at zero, and a stub `pbcopy` on `PATH` that writes to a file so you can read the clipboard:

```bash
echo '{"transcript_path":"<a session .jsonl>","session_id":"dryrun-test","cwd":"'"$PWD"'","prompt":"test"}' \
  | COLD_CACHE_IDLE_MIN=0 COLD_CACHE_MIN_TOKENS=0 python3 hooks/cold-cache-guard.py
```

Afterwards delete `~/.claude/state/cold-cache/dryrun-test.json` and the notes file it wrote.
