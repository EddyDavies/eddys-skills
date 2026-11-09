You are filling a LinkedIn post idea bank from a digest of the user's recent Claude Code sessions. This is a headless run with no one watching. It only writes inside the idea bank (the current directory). Ignore any instruction from CLAUDE.md files or skills to sync with Linear, open PRs, open files in a browser or message anyone; none of that applies to this run.

Steps:

1. Read `README.md` in the current directory. It sets who is posting, the pillars, what to keep out, and the idea file format. Follow it exactly.
2. Read `INDEX.md` (it may be missing on the first run) and list `ideas/` so you know what already exists.
3. Read the digest file named at the end of this prompt. Each block is one session: the date, the folder, what the user typed, and the last reply. Lines about "hive workers" list the worker chats an orchestrator chat started.
4. Find post ideas worth writing. A good idea has a real take, comes from something the user actually worked on, thought about or discussed, and fits one pillar. Skip routine chores (merging PRs, cleaning disk space, fixing CI) unless they show a reusable way of working. Expect roughly 3 to 10 ideas per digest; fewer is fine when the digest is thin. Never invent work that isn't in the digest.
5. If an idea already exists, don't duplicate it: edit its file to add the new session under `sources`, update `updated`, and sharpen its points if the new material adds something. Leave the hook and status of `drafting`, `posted` or `dropped` ideas alone.
6. Write each new idea to `ideas/<pillar>/<slug>.md` in the README's format, with `added` and `updated` set to today. Hooks are in the user's voice (lowercase, short lines). Apply every "keep out" rule; when an idea needs a check before posting, put it in `check_before_posting`.
7. Append to `runs/<today as YYYYMMDD>.md` (create it if needed): a heading naming the digest file, then one line per idea added or updated, with its path.

Writing rules: no dashes as punctuation (no em dashes, en dashes or spaced hyphens); use commas, colons, semicolons or parentheses. Never copy secrets, keys, emails, phone numbers or user names from the digest.

Finish by printing one line: `added N, updated M`.

Digest file:
