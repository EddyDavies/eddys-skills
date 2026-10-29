---
name: dev1-handoff
description: Use when Eddy wants work to carry on while his laptop is closed or moving, e.g. "push it to dev-1", "build it on the dev server", "send it to the workbox", "so I can move my laptop", or when an overnight run must survive the Mac sleeping; also when picking up what dev-1 pushed ("what did dev-1 do", "pull dev-1's work").
---

# dev-1 handoff

dev-1 (Hetzner, `ssh dev-1`, herdr machine `workbox`) keeps working when the Mac sleeps. It has
Claude Code, git with GitHub access, and the project toolchains. It has **no simulator, no Mac
memory, no deploy credentials, and no SendMessage back to the Mac**. So everything dev-1 needs
travels in git, and everything it produces comes back in git.

Three modes: **Triage** (choose what goes), **Send** (brief and launch), **Pickup** (bring it back).

## Triage

Same doc as overnight-handoff (REQUIRED BACKGROUND: overnight-handoff), with one extra test per
item. An item can go to dev-1 only if it needs none of: a simulator or device, a deploy or live
write, secrets that live only on the Mac, a metered spend over the cap, or a decision still open.
Those items stay on the Mac's list. dev-1 items have one outcome group: **push branch and stop**.

## Send

1. **Brief branch.** Push `docs/<topic>-brief-<YYYYMMDD>` cut from main, holding
   `docs/briefs/<topic>-<YYYYMMDD>/BRIEF.md` and a `refs/` folder with copies of anything it
   cites from git-ignored places (`reports/`, mockups, screenshots). BRIEF.md sections:
   0 why; 0b Eddy's decisions (override everything below); 1 sources of truth; 2 house rules
   for dev-1 (no sim, no deploy, no force-push, push and stop); 3 the work, item by item;
   4 verification dev-1 can run (analyze, tests, goldens); 5 what to push and where;
   6 report format; 7 still open (take the reversible default, log it).
   The brief is self-contained: no "see memory", no Mac paths. Write nothing secret into it.
   Read it once for contradictions (e.g. a rule demanding a sim check dev-1 cannot do).
2. **One worktree and branch per worker** on dev-1 (`~/code/<repo>/.claude/worktrees/<label>`,
   branch `<prefix>/<topic>-<label>-<date>`). Never two workers in one checkout.
3. **Launch through herd. Always.** REQUIRED SUB-SKILL: herd-shepherd. Spawn each sheepdog on the
   workbox with `herd spawn --on workbox ...`. If this herd has no `--on`, stop and tell Eddy
   verbatim; do not hand-roll tmux, raw `herdr agent start`, or a pasted prompt instead.
4. **Handoff is in git.** Each worker ends by committing `HANDOFF.md` at its worktree root
   (built, not built, defaults taken, test results, open questions) and pushing its branch.
5. Before Eddy closes the lid, confirm each sheepdog is running on dev-1 (`herd status`), and
   tell him the branch names to expect.

## Pickup

`git fetch`, list the expected branches, read each `HANDOFF.md`, then hand the remaining
Mac-only steps (sim pass, merge, deploy, TestFlight) to overnight-handoff's grouped outcomes,
or straight to Eddy if he is awake. Close the sheepdogs once their branches are read.

## Red flags

| Thought | Reality |
|---|---|
| "I'll just paste a prompt into dev-1" | Herd or nothing; an unmanaged worker is invisible in the morning. |
| "It's in reports/, dev-1 can read it" | reports/ is git-ignored. Copy it into the brief's refs/. |
| "See the test accounts in memory" | dev-1 has no memory. Inline it, or keep the item on the Mac. |
| "All workers can share the clone" | They stash and amend over each other. One worktree each. |
| "dev-1 can deploy it at the end" | dev-1 pushes and stops. The Mac deploys and verifies. |
