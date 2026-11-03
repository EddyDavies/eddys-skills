---
name: neighbour-chats
description: Use when Eddy says "check the neighbours", "who else is on this", "any other chats on this", "find related chats", "what's the chat next door doing", "ask the <name> chat", or wants to know which other Claude chats in Herdr overlap with, depend on, or contradict this one. Lists every other chat with what it is doing, finds the ones on the same work, and reaches them by SendMessage. Requires HERDR_ENV=1.
---

# Neighbour chats

Eddy runs many Claude chats in Herdr tabs. This skill finds the ones related to this chat's work and, when asked, talks to them.

## 1. List the chats

Run the script that sits beside this file (resolve the symlink if needed):

```
python3 ~/.claude/skills/neighbour-chats/chats.py [--here] [--grep <word> ...]
```

- No flags: every other chat, this workspace first. Each row has the workspace and tab, the chat's name, status, folder and branch, idle time, Eddy's last asks and the start of its last reply, its pane id and transcript path.
- `--here`: only this workspace ("the chats next door", "neighbours").
- `--grep`: pass 3 to 6 words naming this chat's work (feature, ticket ids, PR numbers, file or package names, provider). Rows then show mention counts and sort by them.

## 2. Decide which are related

Judge by meaning, not only by word hits. A chat is related when it touches the same feature, ticket, PR, branch, files, or decision, or when it waits on something this chat is doing (or the reverse).

For each likely match, read more before claiming overlap: `herdr agent read <pane> --source recent-unwrapped --lines 150`, or search its transcript with grep. Claims you cannot confirm from its screen or transcript are leads, not facts.

## 3. Report

Short, in this chat:

- **Same work:** the chat (workspace / tab / name), what it is doing, and how it overlaps: duplicate, conflicting, or complementary.
- **Depends on:** chats waiting on this one, or this one on them.
- **Nothing related:** say so in one line.

End with one recommendation: merge, hand off, message, or leave alone.

## 4. Talk to a chat (only when Eddy asks, or to answer his question)

- Use SendMessage with the chat's name as shown in ListAgents. Names in the script's rows match those names.
- Never type into another chat with `herdr agent prompt` or `send-keys`. It can land on top of work in progress.
- Never close, move or rename other chats' tabs unless Eddy asks.
- A hive bee reports to its queen. Message the queen, not the bee, unless Eddy names the bee.
