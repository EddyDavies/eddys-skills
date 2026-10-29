#!/usr/bin/env python3
"""Gather raw evidence of unmade decisions and unfinished work for an overnight handoff.

Usage: uv run python gather.py [repo_root] [--days 14]
Every session and worktree carries a tier: "24h" (primary), "48h" (secondary) or "older"
(only kept when it still holds a loose end; listed as stale undecided work).
Prints JSON to stdout. Read only: never changes git, beads or any service.
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("--")]
days = 14
if "--days" in sys.argv:
    days = int(sys.argv[sys.argv.index("--days") + 1])


def tier(ts):
    age = (time.time() - ts) / 3600
    return "24h" if age <= 24 else "48h" if age <= 48 else "older"
root = Path(args[0] if args else os.getcwd()).resolve()


def sh(cmd, cwd=root):
    try:
        r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=60)
        return r.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


out = {"repo": str(root), "generated": time.strftime("%Y-%m-%d %H:%M"), "days": days}

# Git: every worktree, its branch, dirty files, commits not on origin, commits not on main.
main = "main" if sh("git rev-parse --verify -q main") else sh("git symbolic-ref --short refs/remotes/origin/HEAD").replace("origin/", "")
wts = []
for block in sh("git worktree list --porcelain").split("\n\n"):
    path = re.search(r"^worktree (.+)$", block, re.M)
    br = re.search(r"^branch refs/heads/(.+)$", block, re.M)
    if not path:
        continue
    p, b = path.group(1), br.group(1) if br else "(detached)"
    wts.append({
        "path": p,
        "branch": b,
        "dirty": sh("git status --porcelain", cwd=p).splitlines()[:40],
        "unpushed": sh(f"git log --oneline @{{u}}..HEAD 2>/dev/null || git log --oneline origin/{main}..HEAD", cwd=p).splitlines()[:20],
        "not_on_main": [] if b == main else sh(f"git log --oneline {main}..{b}", cwd=p).splitlines()[:20],
        "last_commit": sh("git log -1 --format='%cr %s'", cwd=p),
        "tier": tier(int(sh("git log -1 --format=%ct", cwd=p) or 0)),
    })
out["main_branch"] = main
out["worktrees"] = wts
out["local_branches_not_merged"] = sh(f"git branch --no-merged {main} --format='%(refname:short) %(committerdate:relative)'").splitlines()

# Open PRs and their merge state, if gh works here.
out["prs"] = sh("gh pr list --state open --json number,title,headRefName,mergeable,mergeStateStatus 2>/dev/null")

# Beads, if the repo uses them.
if (root / ".beads").exists():
    out["beads_in_progress"] = sh("bd list --status=in_progress 2>/dev/null")
    out["beads_ready"] = sh("bd ready 2>/dev/null | head -40")
    out["beads_blocked"] = sh("bd blocked 2>/dev/null | head -20")

# Transcripts: every session in this project touched in the window. For each, the user
# messages that asked for later/overnight work, and the last assistant text (where open
# questions and "want me to ...?" offers sit).
proj = Path.home() / ".claude/projects" / re.sub(r"[^A-Za-z0-9]", "-", str(root))
ASK = re.compile(r"overnight|tonight|while i.?m (away|asleep|out)|by (the )?morning|tomorrow|later|keep going|work on", re.I)
OFFER = re.compile(r"\?\s*$|want me to|shall i|should i|do you want|let me know|your call|which (one|option)|before i ", re.I | re.M)
sessions = []
cutoff = time.time() - days * 86400
if proj.exists():
    for f in sorted(proj.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
        if f.stat().st_mtime < cutoff:
            break
        asks, last_text, first_user = [], "", ""
        for line in f.open(errors="ignore"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get("message") or {}
            c = msg.get("content")
            text = c if isinstance(c, str) else " ".join(
                x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text")
            if not text or text.lstrip().startswith("<"):
                continue
            if d.get("type") == "user":
                first_user = first_user or text[:300]
                if ASK.search(text):
                    asks.append({"at": d.get("timestamp", "")[:16], "text": text[:1200]})
            elif d.get("type") == "assistant":
                last_text = text
        t = tier(f.stat().st_mtime)
        open_q = bool(OFFER.search(last_text[-600:]))
        if t == "older" and not (open_q or asks):
            continue
        sessions.append({
            "tier": t,
            "id": f.stem,
            "modified": time.strftime("%m-%d %H:%M", time.localtime(f.stat().st_mtime)),
            "opened_with": first_user,
            "user_asks_for_later_work": asks[-8:],
            "last_assistant_text": last_text[-2500:],
            "ends_with_open_question": open_q,
        })
out["sessions"] = sessions
out["counts"] = {k: sum(1 for x in sessions if x["tier"] == k) for k in ("24h", "48h", "older")}

print(json.dumps(out, indent=1))
