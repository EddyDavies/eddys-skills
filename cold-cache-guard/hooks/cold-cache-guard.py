"""UserPromptSubmit hook: stop a big chat from rebuilding a cold prompt cache.

When the last reply is older than the cache TTL and the context is large, the
next message would re-bill the whole context at cache-write price. This hook
blocks that message (no API call), writes restart notes from the transcript
for free, and copies a paste for a new chat to the clipboard: a pointer to the
notes, then the blocked message. The block shows what each path costs as a
move in your 5h and weekly plan limits, calibrated from usage-log.sh.

Sending the same session another message after a block lets it through, so
you can always choose to continue.

Tune with env vars: COLD_CACHE_IDLE_MIN (default 55), COLD_CACHE_MIN_TOKENS
(default 200000), COLD_CACHE_OFF=1 to disable.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

IDLE_MIN = float(os.environ.get("COLD_CACHE_IDLE_MIN", "55"))
MIN_TOKENS = int(os.environ.get("COLD_CACHE_MIN_TOKENS", "200000"))
STATE_DIR = Path.home() / ".claude" / "state" / "cold-cache"
HANDOFF_DIR = Path.home() / ".claude" / "handoffs"
# Anthropic list input $/MTok by model family; only a common unit, never shown.
INPUT_PRICE = {"fable": 10, "opus": 5, "sonnet": 2, "haiku": 1}
# Written by usage-log.sh from the statusline: plan % used alongside each session's running cost.
USAGE_LOG = Path.home() / ".claude" / "state" / "usage-log.jsonl"


def plan_rates():
    """Plan % per list dollar for the 5h and weekly limits, from the statusline's usage log.

    Walks the log in time order, summing each session's cost growth, and pairs it
    with how far each limit's % rose. A stretch where a % fell (a reset) is dropped.
    Returns ({"h5": rate, "d7": rate}, latest reading); a rate is None until it has
    seen at least 3 points of movement.
    """
    rows = []
    try:
        with open(USAGE_LOG) as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        return {}, None
    rows = [r for r in rows if r.get("ts") and r.get("cost") is not None]
    rows.sort(key=lambda r: r["ts"])
    if not rows:
        return {}, None
    cutoff = rows[-1]["ts"] - 7 * 86400
    rates = {}
    for lim in ("h5", "d7"):
        cost_by_sid, prev_pct, pending, d_pct, d_usd = {}, None, 0.0, 0.0, 0.0
        for r in rows:
            sid, cost, pct = r.get("sid"), r["cost"], r.get(lim)
            before = cost_by_sid.get(sid)
            cost_by_sid[sid] = cost
            if before is not None and cost > before and r["ts"] >= cutoff:
                pending += cost - before
            if pct is None:
                continue
            if prev_pct is not None and pct >= prev_pct and r["ts"] >= cutoff:
                if pct > prev_pct:
                    d_pct += pct - prev_pct
                    d_usd += pending
                    pending = 0.0
            else:
                pending = 0.0
            prev_pct = pct
        rates[lim] = d_pct / d_usd if d_pct >= 3 and d_usd > 0 else None
    return rates, rows[-1]


def unwrap_pastes(text):
    """Drop the <pasted_content id=...> wrappers Claude Code puts round pasted text.

    The hook sees them in the prompt, but pasted into a new chat they would arrive
    as literal tags around the text instead of as a paste.
    """
    return re.sub(r"</?pasted_content\b[^>]*>\n?", "", text)


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fmt_idle(minutes):
    m = int(minutes)
    if m < 60:
        return f"{m} min"
    h, m = divmod(m, 60)
    if h < 24:
        return f"{h}h {m}m"
    d, h = divmod(h, 24)
    return f"{d}d {h}h"


def text_of(content):
    if isinstance(content, str):
        return content
    parts = []
    for c in content or []:
        if isinstance(c, dict) and c.get("type") == "text":
            parts.append(c.get("text", ""))
    return "\n".join(parts)


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("isSidechain"):
                continue
            rows.append(r)
    return rows


def git(cwd, *args):
    try:
        return subprocess.run(
            ["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except Exception:
        return ""


def unsent_images(rows, hook):
    """Pasted images saved to disk for the blocked prompt but never sent.

    Claude Code writes each paste to <tmp>/claude-<uid>/<project>/<session>/images/N.png
    at paste time; N matches imagePasteIds on the transcript message that sent it.
    A blocked prompt never reaches the transcript and up-arrow history keeps no
    images, so anything not in a sent message would be lost.
    """
    sid = hook.get("session_id", "")
    project = Path(hook.get("transcript_path", "")).parent.name
    dirs = [Path(f"/private/tmp/claude-{os.getuid()}") / project / sid / "images"]
    dirs += list(Path("/private/tmp").glob(f"claude-*/*/{sid}/images"))
    img_dir = next((d for d in dirs if d.is_dir()), None)
    if not img_dir:
        return []
    sent = set()
    for r in rows:
        for i in r.get("imagePasteIds") or []:
            sent.add(str(i))
    return sorted(
        (p for p in img_dir.iterdir() if p.is_file() and p.stem not in sent),
        key=lambda p: p.stat().st_mtime,
    )


def write_handoff(rows, hook, ctx, idle_min):
    cwd = hook.get("cwd") or os.getcwd()
    sid = hook.get("session_id", "unknown")
    prompts, replies, files = [], [], []
    for r in rows:
        msg = r.get("message") or {}
        if r.get("type") == "user" and not r.get("isMeta"):
            t = text_of(msg.get("content")).strip()
            if t and not t.startswith("<"):
                prompts.append(t)
        elif r.get("type") == "assistant":
            t = text_of(msg.get("content")).strip()
            if t:
                replies.append(t)
            for c in msg.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    p = (c.get("input") or {}).get("file_path")
                    if p and c.get("name") in ("Write", "Edit", "NotebookEdit") and p not in files:
                        files.append(p)

    slug = cwd.strip("/").replace("/", "-") or "root"
    out_dir = HANDOFF_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    out = out_dir / f"{stamp}-{sid[:8]}.md"

    images = []
    for i, src in enumerate(unsent_images(rows, hook), 1):
        dst = out_dir / f"{stamp}-{sid[:8]}-image-{i}{src.suffix}"
        shutil.copy2(src, dst)
        images.append(dst)

    lines = [
        f"# Restart context ({stamp})",
        "",
        f"- Project: `{cwd}`",
        f"- Old session: `{sid}` (resume with `claude --resume {sid}`, but that rebuilds the cache)",
        f"- Context when parked: ~{ctx // 1000}k tokens, idle {idle_min:.0f} min",
        f"- Branch: `{git(cwd, 'branch', '--show-current') or 'n/a'}`",
        "",
    ]
    # The blocked message itself travels in the paste, not here, so a new chat sees it once.
    if images:
        lines += ["## Images pasted with the next message", "",
                  "Open each with the Read tool:", ""]
        lines += [f"- `{p}`" for p in images] + [""]
    lines += [
        "## Recent requests (oldest first)",
        "",
    ]
    for p in prompts[-12:]:
        lines += ["- " + p[:600].replace("\n", " "), ""]
    lines += ["## Last replies", ""]
    for t in replies[-3:]:
        lines += [t[:3000], "", "---", ""]
    if files:
        lines += ["## Files written or edited", ""] + [f"- `{p}`" for p in files[-40:]] + [""]
    status = git(cwd, "status", "--short")
    if status:
        lines += ["## git status at park time", "", "```", status[:4000], "```", ""]
    out.write_text("\n".join(lines))
    return out, images


def main():
    if os.environ.get("COLD_CACHE_OFF") == "1":
        return
    hook = json.load(sys.stdin)
    tp = hook.get("transcript_path")
    if not tp or not os.path.exists(tp):
        return
    rows = load(tp)
    last = next(
        (r for r in reversed(rows)
         if r.get("type") == "assistant" and (r.get("message") or {}).get("usage")),
        None,
    )
    if not last:
        return
    u = last["message"]["usage"]
    ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
           + u.get("cache_creation_input_tokens", 0))
    idle_min = (datetime.now(timezone.utc) - parse_ts(last["timestamp"])).total_seconds() / 60
    if idle_min < IDLE_MIN or ctx < MIN_TOKENS:
        return

    # Second message after a block: the user chose to continue, let it through.
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = STATE_DIR / f"{hook.get('session_id', 'unknown')}.json"
    if state.exists():
        try:
            prev = json.loads(state.read_text())
        except ValueError:
            prev = {}
        if prev.get("blocked_after") == last["timestamp"]:
            state.unlink()
            images = prev.get("images") or []
            if images:
                # Up-arrow drops pasted images; hand their saved copies to the model.
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "The user's previous attempt at this message was blocked by the "
                        "cold cache guard, and resending dropped the images they had "
                        "pasted with it. Open these with the Read tool before answering, "
                        "and treat them as part of this message:\n"
                        + "\n".join(images)
                    ),
                }}))
            return

    out, images = write_handoff(rows, hook, ctx, idle_min)
    state.write_text(json.dumps({
        "blocked_after": last["timestamp"],
        "handoff": str(out),
        "images": [str(p) for p in images],
    }))
    # The paste for a new chat: a pointer to the notes, then the blocked message.
    # Claude Code already echoes the message under the block ("Original prompt:"),
    # so the block shows only the pointer and the clipboard carries both.
    notes = str(out).replace(str(Path.home()), "~", 1)
    asked = unwrap_pastes(hook.get("prompt", "")).strip()
    pointer = f"Context: this picks up an earlier session. Read {notes} first (and any images it lists)."
    restart = f"{pointer}\n\n{asked}" if asked else (
        f"Read {notes} (and any images it lists) and continue from where that session left off.")
    try:
        subprocess.run(["pbcopy"], input=restart, text=True, timeout=3)
    except Exception:
        pass

    # Rough token count of the notes (~4 chars per token): what a fresh chat starts from.
    notes_k = max(1, round(out.stat().st_size / 4 / 1000))
    # Base context (system prompt, tools, CLAUDE.md, skills) from this session's first turn.
    first = next((r for r in rows
                  if r.get("type") == "assistant" and (r.get("message") or {}).get("usage")), last)
    fu = first["message"]["usage"]
    base_k = (fu.get("input_tokens", 0) + fu.get("cache_read_input_tokens", 0)
              + fu.get("cache_creation_input_tokens", 0)) // 1000
    # Both paths write their context to a 1h cache at 2x the input price (list $/MTok).
    # Dollars are only the common unit; what's shown is the share of plan limits.
    model = (last["message"].get("model") or "").lower()
    in_price = next((p for k, p in INPUT_PRICE.items() if k in model), 5)
    rates, now_usage = plan_rates()

    def usd(k):
        return k * 1000 * in_price * 2 / 1e6

    def bar(pct):
        n = max(0, min(10, round(pct / 10)))
        return "▓" * n + "░" * (10 - n)

    def lands(k, lim):
        # "now→after%" for one limit; "?" until the usage log has calibrated it.
        now = now_usage.get(lim) if now_usage else None
        if now is None:
            return "?"
        if not rates.get(lim):
            return f"{now}→?%"
        return f"{now}→{min(100, round(now + usd(k) * rates[lim]))}%"

    def resets(lim):
        # " ↺2h14m" for the 5h window, " ↺Thu 09:00" for the week; "" when unknown.
        at = now_usage.get(f"{lim}_reset") if now_usage else None
        if not at:
            return ""
        left = at - datetime.now(timezone.utc).timestamp()
        if left <= 0:
            return " ↺done"
        if lim == "h5" or left < 86400:
            return f" ↺{fmt_idle(left / 60)}"
        return f" ↺{datetime.fromtimestamp(at).strftime('%a %H:%M')}"

    fresh_k = base_k + notes_k
    head = f"❄ nothing sent · idle {fmt_idle(idle_min)}"
    if now_usage:
        head += (f" · 5h {bar(now_usage['h5'])} {now_usage['h5']}%{resets('h5')}"
                 f" · wk {bar(now_usage['d7'])} {now_usage['d7']}%{resets('d7')}")
    if images:
        head += f" · 🖼 {len(images)} saved"

    # ↻ resend here, 📋 paste the block below into a new chat (it's on the clipboard).
    # 📋 renders two columns wide, so it gets one space where ↻ gets two.
    w = len(str(max(ctx // 1000, fresh_k)))
    resend = f"↻  {ctx // 1000:>{w}}k  5h {lands(ctx // 1000, 'h5'):<9} wk {lands(ctx // 1000, 'd7')}"
    paste = (f"📋 {fresh_k:>{w}}k  5h {lands(fresh_k, 'h5'):<9} wk {lands(fresh_k, 'd7'):<9}"
             f" ⟨{base_k}k+{notes_k}k⟩")

    # The paste block goes last and flush left so it can be selected cleanly.
    print(json.dumps({
        "decision": "block",
        "reason": f"{head}\n\n{resend}\n{paste}\n\n{pointer}",
    }))


if __name__ == "__main__":
    main()
