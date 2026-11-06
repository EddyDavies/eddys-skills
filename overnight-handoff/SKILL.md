---
name: overnight-handoff
description: Use when Eddy is wrapping up for the evening or handing work over to run unattended, e.g. "overnight", "tonight", "while I'm asleep", "by the morning", "end of day", "tidy up before bed", "/overnight-handoff", or when he pastes a block starting OVERNIGHT RUN.
---

# Overnight handoff

Overnight work fails in the same few ways: a chat ends its turn on a question nobody answers
until morning, work sits finished in a worktree that was never merged, pushed or deployed,
"I'll do X" is said and never queued, or a worker's handoff arrives and nothing acts on it.
The goal of the evening pass is to get a decision on as much as possible before Eddy sleeps,
then run those decisions through a hive without stopping.

Two modes. Pick by the message:
- **Triage** (default; any evening/overnight trigger): build the decision doc. Do no work.
- **Run** (message starts `OVERNIGHT RUN`): execute the pasted plan through hive.

## Triage

1. Gather: `uv run python ~/.claude/skills/overnight-handoff/gather.py <repo> > <scratchpad>/gather.json`.
   Every worktree, unmerged branch, open PR, bead and session comes back with a tier:
   `24h` (primary focus), `48h` (secondary), `older` (up to 14 days, only where a loose end
   remains). Give the JSON to a subagent to read the transcripts; keep its conclusions.
2. Add what only this chat knows: open questions, "want me to...?" offers, deferred work,
   hive bees still open or with unread handoffs (`hive status`), deploys not verified.
3. Make one item per unmade decision or unfinished piece. Each item carries:
   - **What** (one line) and **Context**: session id, worktree, branch, bead, PR, file:line;
     what is done, what is verified (tests, build, deploy API check), what is not; any spend.
   - **Tier** from gather.
   - **Bucket**, one of: `ready` (done and verified, only the outcome step left), `overnight`
     (can finish unattended with every decision already made), `forward` (someone else acts:
     client, Andy, another chat; include the draft), `wait` (needs Eddy or an outside event;
     say what unblocks it), `drop`.
   - **Outcome**, one of: `deploy` (live: functions, rules, hosting, TestFlight), `push` (merged
     and pushed, not deployed), `local` (committed only), `none`.
   An item with one open choice is `wait`, with the question written out and the recommended
   answer preselected, so Eddy decides it by leaving it.
4. Write `<repo>/reports/overnight-handoff-<YYYYMMDD>.html` (or `~/code/reports/` with no repo):
   - Top: counts per bucket and per tier, and a red banner if `$HERDR_ENV` is not 1 (Run needs hive).
   - **Outcome groups**, one section each for `deploy`, `push`, `local`, `none`. Each group says
     in one line what approving it does ("deploy:hub, verify via API, TestFlight build") and has
     one approve toggle for the whole group. Under it, the `ready` and `overnight` items going
     to that outcome, each with a checkbox (unchecked drops it from the group) and a small
     select to move it to another outcome. Eddy decides the group, not each item.
   - **Forward**, **Wait**, then **Older loose ends** (the `older` tier, compact), each card
     with a bucket select, any preset question, and a notes box. Drafts for `forward` are copyable.
   - A sticky **Copy as prompt** button emits `OVERNIGHT RUN <date> <repo>`, then per approved
     group `GROUP <outcome>: [id] what, [id] what`, then `FORWARD`, `WAIT` answers and notes.
     Unapproved groups and unchecked items are left out. Choices persist in localStorage (try/catch).
5. Follow the project's report and dashboard rules, `diaopen` it, end with one line:
   counts per bucket and the path.

## Run

The pasted block is the authority. Eddy has chosen; do not ask again.
- **Always hive.** REQUIRED SUB-SKILL: hive-queen. Check `echo $HERDR_ENV` is 1, then
  `hive init "overnight <date>"`. If hive refuses or is unavailable, say so verbatim and stop;
  never fall back to subagents or a solo run.
- If the Mac will sleep (the block says `LID CLOSED`, or Eddy says the laptop is going),
  bees run on dev-1: REQUIRED SUB-SKILL: dev1-handoff. Mac-only steps (sim, deploy)
  wait for the morning pickup. Triage asks this as a top-of-doc toggle and emits the flag.
- One bee per independent item (or per tight cluster in the same files), each briefed
  with the item's context, its outcome, and the project's rules for that outcome (deploy
  verification, staged-file audit, never force-push, spend caps). Bees do the work up to
  the outcome step; the queen verifies and does pushes and deploys, grouped by outcome.
- `forward`: write the drafts into the report. Send nothing external unless the project allows it.
- A new decision mid-run: take the reversible option, log it as a morning question, keep going.
  A blocked item: record why, move on. Never end the turn while bees are open or items
  remain; keep a ScheduleWakeup or Monitor running so their handoffs get read.
- Finish by updating the same report (and the project dashboard): per item, done and verified
  with evidence, done unverified, or blocked with the reason; morning questions at the top.

## Red flags

| Thought | Reality |
|---|---|
| "I'll ask Eddy which he prefers" (during Run) | He is asleep. Pick the reversible one and log it. |
| "Hive isn't up, I'll just use subagents" | Overnight always runs on hive. Report and stop. |
| "Done in the worktree" | Not done until the group's outcome happened and was verified. |
| "Waiting for the bee" then ending the turn | Schedule a wakeup; an ended turn does nothing all night. |
| "Too small to list" / "too old to list" | Those are what turn up undone in the morning. Older tier gets a line. |
| An `overnight` item with a choice still open | It is `wait` with a preset answer. |
