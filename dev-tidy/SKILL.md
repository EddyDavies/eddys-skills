---
name: dev-tidy
description: Use whenever you start a wrangler dev server, start or run a Docker / OrbStack container (local Postgres, bridges, compose stacks), finish a test or proof run that used one, or when the Mac is short on RAM. Covers stopping what you started, the automatic cleanup, and the dev-tidy command (status, sweep, keep).
---

# dev-tidy

Every `wrangler dev` holds 80 to 200 MB and outlives the chat that started it (Claude's
background shells hand it to launchd, so it never dies with the chat). OrbStack's VM
holds about 3 GB while any container runs. This skill keeps both down.

## What runs on its own (installed by `setup.sh`)

- **PostToolUse(Bash) hook** records which chat ran a `wrangler ... dev` (cwd and port)
  or a `docker run|start|restart|exec|compose up` (cwd and command), and that chat's
  claude process.
- **SessionEnd hook** kills the wrangler servers that chat started, stops containers no
  other live chat used, and runs `orbctl stop` when no container is left.
- **launchd sweep every 10 minutes** catches chats that died without a clean exit (a
  Herdr tab closed under them, a crash): an owner chat whose claude process is gone
  counts as ended. It also kills unowned orphaned wrangler servers older than 6h, stops
  crash looping containers, stops containers with no connection to their ports for 45
  min, and quits OrbStack after 15 min with nothing running. Log: `~/.claude/dev-tidy/sweep.log`

Servers you start yourself in a terminal (parent is your shell) are never touched.

## Rules for agents

1. **Stop what you started as soon as the test or proof is done**, before you report
   back; don't leave it for the hooks. `kill <pid>` the wrangler you started (or stop
   its background task), and `docker stop <name>` the container you started.
2. **Reuse a running server or container** before starting another; check
   `dev-tidy status` first. Never start a second wrangler for the same folder.
3. If OrbStack is stopped, `docker start <name>` (or `orbctl start`) brings it back in
   a few seconds; stopping is cheap to undo, so don't keep things up "just in case".
4. If Eddy needs a container kept up, `dev-tidy keep <name>`.

## Commands

```
dev-tidy status               each server and container: owner chat, idle, verdict
dev-tidy sweep --dry-run      what the next sweep would stop
dev-tidy sweep                apply it now
dev-tidy keep <name> / unkeep <name>
```
