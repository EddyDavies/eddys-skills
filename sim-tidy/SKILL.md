---
name: sim-tidy
description: Use whenever you boot, clone, create or finish with an iOS Simulator, when the Mac is short on RAM or disk, or when asked to clean up, close down, shut down or delete sims. Covers reusing the kept sims, naming and cleaning up clones, and the sim-tidy command (status, shutdown, prune).
---

# sim-tidy

Booted sims hold 2 to 3 GB of RAM each, and every clone holds 2 to 7 GB of disk. This
skill keeps both down.

## What runs on its own (installed by `setup.sh`)

- **PostToolUse(Bash) hook** records which chat last touched which sim (any command
  naming a sim's UDID, `booted`, or a quoted sim name) and which sims an agent
  created with `simctl create` or `clone`.
- **SessionEnd hook** shuts down every booted sim this chat touched last, kills its
  `idb_companion`, and quits Simulator.app when nothing is left booted. It skips a sim
  that another chat touched later, or that a `flutter run` or `xcodebuild` still names.
- **launchd sweep every 2 hours** shuts down sims idle for 2 hours and deletes
  agent-created clones idle for 3 days. Log: `~/.claude/sim-tidy/sweep.log`

A chat killed without a clean exit gets no SessionEnd; the sweep catches it later.

## Rules for agents

1. **Reuse a kept sim before making a new one.** `sim-tidy status` shows them (flag K).
2. **Clone only when you must run in parallel with another chat.** Name it
   `<task> iPhone 16 Pro`, and when the task is done run
   `xcrun simctl shutdown <udid> && xcrun simctl delete <udid>` yourself.
3. **When you finish with a sim, shut it down:** `xcrun simctl shutdown <udid>`.
   Don't leave it booted for the hook to catch.
4. **Never delete a kept sim**, and never `prune --yes` sims you didn't create without
   showing Eddy the dry run first.

## Commands

```
sim-tidy status                       size, state, idle days, K/C flags
sim-tidy shutdown --all               shut every booted sim, quit Simulator.app
sim-tidy prune [--days 3]             dry run of what would be deleted
sim-tidy prune --days 3 --yes         delete them
sim-tidy keep <udid> / unkeep <udid>  protect or release a sim
```
