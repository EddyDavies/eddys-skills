---
name: slack-messages
description: Use whenever Eddy asks to Slack, DM, ping or message someone on Slack, post in a Slack channel, or reply in a Slack thread. Drafts the message, shows the exact draft in chat, and sends through the Slack MCP only after Eddy approves that text.
---

# slack-messages: show the draft, then send

Eddy always sees the exact text before a Slack message goes out. No exceptions: not for one liners, not when he approved an earlier message, not for a follow-up in the same thread.

## Steps

1. **Find the Slack tools.** Run ToolSearch with `+slack` (and `slack send message`). Use the Slack MCP (a claude.ai Slack connector or a `slack` server). Never switch to Chrome, Pally or another app to send without saying so first.
   - If no Slack MCP is connected, say so in one line and still show the draft, so Eddy can connect Slack or copy it (`claude mcp list` shows what is connected).
2. **Find the recipient or channel** with the MCP's user or channel search. If two people match, ask which one in the `AskUserQuestion` picker.
3. **Draft it.** Default to brief: a few short sentences, the point in the first line, links in full. Eddy's writing rules apply: no dashes as punctuation, no punctuation straight after a URL. Slack renders `*bold*` and bullet lists; skip headings.
4. **Show the draft** in chat as plain lines under a `Draft:` label, with a blank line before and after, and no blockquote, quote marks or indentation. Name the recipient or channel above it.
5. **Ask in the picker:** "Send this Slack message to <recipient>?" with `Send as drafted (Recommended)` and `Don't send`. Eddy edits by typing into Other; redraft, show the new draft, and ask again.
6. **Send exactly the approved text.** If anything changes after approval (wording, recipient, thread), show it and ask again.
7. **Report** what was sent, to whom, and the message link if the tool returns one.
