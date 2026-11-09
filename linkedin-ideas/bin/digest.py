#!/usr/bin/env python3
"""Build compact digests of Claude Code sessions for the linkedin-ideas job.

Reads ~/.claude/projects/*/*.jsonl, keeps what the user typed plus the last
thing the assistant said in each session, and writes chunked markdown digests.
Hive worker sessions collapse to one line per queen and day.

usage: digest.py --since YYYY-MM-DD [--until YYYY-MM-DD] --out DIR [--chunk-chars N]
                 [--seen FILE] [--record FILE] [--exclude-cwd TEXT]
--seen skips session ids listed in FILE; --record writes the ids it digests to FILE.
Prints the paths of the chunk files it wrote, one per line.
"""
import argparse, glob, json, os, re, sys

SKIP_PREFIXES = ("<", "Caveat", "This session is being continued", "[Request interrupted")
BEE = re.compile(r'hive bee named "([^"]+)".*?queen.s SendMessage name is "([^"]+)"', re.S)


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(x.get("text", "") for x in content
                         if isinstance(x, dict) and x.get("type") == "text")
    return ""


def clean(s, n):
    s = re.sub(r"<system-reminder>.*?</system-reminder>", "", s, flags=re.S)
    s = re.sub(r"<pasted_content[^>]*>", "[pasted] ", s)
    s = re.sub(r"</pasted_content[^>]*>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:n] + ("…" if len(s) > n else "")


def read_session(path, since, until):
    prompts, last_reply, start, cwd = [], "", None, None
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("isSidechain") or d.get("isMeta"):
                continue
            t = d.get("type")
            if t not in ("user", "assistant"):
                continue
            ts = (d.get("timestamp") or "")[:10]
            if start is None and ts:
                start = ts
                if start < since or (until and start > until):
                    return None
            cwd = cwd or d.get("cwd")
            txt = text_of(d.get("message", {}).get("content"))
            if not txt.strip():
                continue
            if t == "user":
                s = txt.strip()
                if s.startswith(SKIP_PREFIXES):
                    continue
                prompts.append(clean(s, 600))
            else:
                last_reply = txt
    if not start or not prompts:
        return None
    m = BEE.search(prompts[0])
    if m:
        return {"date": start, "bee": m.group(1), "queen": m.group(2)}
    return {"date": start, "cwd": cwd, "prompts": prompts,
            "reply": clean(last_reply, 900), "id": os.path.basename(path)[:8]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until")
    ap.add_argument("--out", required=True)
    ap.add_argument("--chunk-chars", type=int, default=110_000)
    ap.add_argument("--seen")
    ap.add_argument("--record")
    ap.add_argument("--exclude-cwd", action="append", default=["linkedin-ideas"])
    a = ap.parse_args()
    seen = set()
    if a.seen and os.path.exists(a.seen):
        seen = set(open(a.seen).read().split())
    new_ids = []
    home = os.path.expanduser("~")
    sessions, bees = [], {}
    for f in glob.glob(os.path.join(home, ".claude/projects/*/*.jsonl")):
        sid = os.path.basename(f)[:-6]
        if sid in seen:
            continue
        s = read_session(f, a.since, a.until)
        if not s or any(x in (s.get("cwd") or "") for x in a.exclude_cwd):
            continue
        new_ids.append(sid)
        if "bee" in s:
            bees.setdefault((s["date"], s["queen"]), []).append(s["bee"])
        else:
            sessions.append(s)

    blocks = []
    for s in sessions:
        where = (s["cwd"] or "?").replace(home, "~")
        body, used = [], 0
        for p in s["prompts"]:
            if used > 2500:
                body.append("- (more prompts omitted)")
                break
            body.append(f"- {p}")
            used += len(p)
        reply = f"\n  Last reply: {s['reply']}" if s["reply"] else ""
        blocks.append((s["date"], f"### {s['date']} · {where} · {s['id']}\n" + "\n".join(body) + reply + "\n"))
    for (date, queen), names in bees.items():
        blocks.append((date, f"### {date} · hive workers under \"{queen}\"\n- {', '.join(sorted(set(names)))}\n"))
    blocks.sort(key=lambda b: b[0])

    os.makedirs(a.out, exist_ok=True)
    chunks, cur, size = [], [], 0
    for b in blocks:
        if size + len(b[1]) > a.chunk_chars and cur:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(b)
        size += len(b[1])
    if cur:
        chunks.append(cur)
    for i, c in enumerate(chunks, 1):
        p = os.path.join(a.out, f"digest-{a.since}-{i:02d}-of-{len(chunks):02d}.md")
        with open(p, "w") as fh:
            fh.write(f"# Claude session digest {c[0][0]} to {c[-1][0]}\n\n" + "\n".join(b[1] for b in c))
        print(p)
    if a.record:
        with open(a.record, "w") as fh:
            fh.write("".join(i + "\n" for i in new_ids))
    print(f"{len(sessions)} sessions, {sum(len(v) for v in bees.values())} hive workers, "
          f"{len(chunks)} chunks", file=sys.stderr)


if __name__ == "__main__":
    main()
