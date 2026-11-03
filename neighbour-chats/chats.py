#!/usr/bin/env python3
"""List the other Claude chats in this Herdr session and what each is doing.

    chats.py                     every other chat, this workspace first
    chats.py --here              only chats in this chat's workspace
    chats.py --grep vault login  also count how often each chat's recent
                                 transcript mentions these words
    chats.py --json              machine-readable

For each chat: workspace and tab, its name, status, folder and git branch,
how long since it last wrote, Eddy's last messages to it and the start of
its last reply. Reads only the tail of each transcript, so it stays fast with
dozens of chats. Read-only: it never types into another chat.
"""

import argparse
import glob
import json
import os
import subprocess
import sys
import time

TAIL_BYTES = 1_500_000


def herdr(*args):
    p = subprocess.run(["herdr", *args], capture_output=True, text=True, timeout=30)
    if p.returncode:
        sys.exit("herdr %s failed: %s" % (" ".join(args), p.stderr.strip() or p.stdout.strip()))
    return json.loads(p.stdout)["result"]


def branch(cwd):
    if not cwd:
        return ""
    p = subprocess.run(["git", "-C", cwd, "branch", "--show-current"], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def transcript(session):
    if not session:
        return None
    found = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % session))
    return found[0] if found else None


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def tail_lines(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(max(0, size - TAIL_BYTES))
        data = f.read().decode("utf-8", "replace")
    lines = data.splitlines()
    return lines[1:] if size > TAIL_BYTES else lines


def digest(path, words):
    users, replies, hits = [], [], {w: 0 for w in words}
    for line in tail_lines(path):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("isMeta") or d.get("isSidechain") or d.get("type") not in ("user", "assistant"):
            continue
        t = text_of(d.get("message", {}).get("content")).strip()
        if not t:
            continue
        low = t.lower()
        for w in words:
            hits[w] += low.count(w.lower())
        if d["type"] == "user" and not t.startswith(("<", "Caveat:", "Another Claude session")):
            users.append(t)
        elif d["type"] == "assistant":
            replies.append(t)
    return users[-3:], (replies[-1] if replies else ""), hits


def short(t, n):
    t = " ".join(t.split())
    return t if len(t) <= n else t[: n - 1] + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--here", action="store_true", help="only this workspace")
    ap.add_argument("--grep", nargs="+", default=[], help="count mentions of these words")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if os.environ.get("HERDR_ENV") != "1":
        sys.exit("not inside Herdr")
    # HERDR_PANE_ID goes stale once a chat's tab is moved; Herdr still
    # resolves it, so ask for the live pane instead of comparing the env value.
    current = herdr("pane", "current", "--current")["pane"]
    me, my_ws = current["pane_id"], current["workspace_id"]
    workspaces = {w["workspace_id"]: w.get("label") or w["workspace_id"] for w in herdr("workspace", "list")["workspaces"]}
    tabs = {t["tab_id"]: t.get("label") or "" for t in herdr("tab", "list")["tabs"]}

    rows = []
    for p in herdr("pane", "list")["panes"]:
        if not p.get("agent") or p["pane_id"] == me:
            continue
        if a.here and p["workspace_id"] != my_ws:
            continue
        session = (p.get("agent_session") or {}).get("value")
        path = transcript(session)
        users, reply, hits = digest(path, a.grep) if path else ([], "", {})
        age = int(time.time() - os.path.getmtime(path)) if path else None
        rows.append({
            "name": p.get("terminal_title_stripped") or "",
            "workspace": workspaces.get(p["workspace_id"], p["workspace_id"]),
            "tab": tabs.get(p["tab_id"], ""),
            "pane_id": p["pane_id"],
            "same_workspace": p["workspace_id"] == my_ws,
            "status": p.get("agent_status"),
            "cwd": p.get("foreground_cwd") or p.get("cwd"),
            "branch": branch(p.get("foreground_cwd") or p.get("cwd")),
            "idle_min": None if age is None else age // 60,
            "transcript": path,
            "last_asks": users,
            "last_reply": reply,
            "hits": hits,
        })

    rows.sort(key=lambda r: (not r["same_workspace"], -sum(r["hits"].values()), r["idle_min"] if r["idle_min"] is not None else 1e9))
    if a.json:
        print(json.dumps(rows, indent=1))
        return

    print("%d other chats (this workspace first%s)\n" % (len(rows), ", then by mentions" if a.grep else ""))
    for r in rows:
        mark = "*" if r["same_workspace"] else " "
        hit = "  mentions: " + ", ".join("%s %d" % kv for kv in r["hits"].items()) if a.grep else ""
        idle = "?" if r["idle_min"] is None else ("%dm" % r["idle_min"] if r["idle_min"] < 120 else "%dh" % (r["idle_min"] // 60))
        print("%s [%s / %s] %s  (%s, idle %s, %s%s)%s" % (
            mark, r["workspace"], r["tab"], r["name"], r["status"], idle,
            os.path.basename(r["cwd"] or ""), (" @ " + r["branch"]) if r["branch"] else "", hit))
        for u in r["last_asks"]:
            print("    asked: %s" % short(u, 160))
        if r["last_reply"]:
            print("    said:  %s" % short(r["last_reply"], 220))
        print("    pane %s  transcript %s\n" % (r["pane_id"], r["transcript"] or "not found"))


if __name__ == "__main__":
    main()
