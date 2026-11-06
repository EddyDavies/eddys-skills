# eddys-skills

A collection of Eddy's Claude Code skills.

- `quiet-open`: surface links and markdown previews without stealing focus.
- `dis-tribution`: Viktoria Izdebska's distribution-as-moat lens for ideas and markets.
- `overnight-handoff`: evening triage of every unmade decision (last 24h, 48h, older loose ends) into one HTML doc with grouped deploy / push / local outcomes, then runs the chosen plan overnight through hive.
- `dev1-handoff`: sends chosen work to the dev-1 workbox through hive (brief branch, a worktree per worker, handoff in git) so it runs while the laptop is closed, and picks it back up. Needs `hive spawn --on workbox`.
- `cold-cache-guard`: blocks a message that would rebuild a big, idle chat's cold prompt cache, shows what continuing vs starting fresh costs in 5h and weekly plan limits, and puts a ready fresh-chat paste on the clipboard.
- `neighbour-chats`: say "check the neighbours" or "who else is on this" and the chat lists every other Claude chat in Herdr with what it is doing, picks out the ones on the same work, and messages them on request (`chats.py` does the listing).
- `report-deck`: optional, on request only: adds a top-right Slides button to an HTML report, opening a phone-friendly deck of the headlines with tap-to-open technical details (`inject.py` inlines it).
- `sim-tidy`: shuts iOS Simulators down when the chat that used them ends (SessionEnd hook plus a 2 hourly launchd sweep), deletes agent clones idle 3 days, and `sim-tidy status|prune` for the rest. Run `setup.sh` to install.
- `clear-claude-groups`: deletes the saved Chrome tab groups named "Claude" that Claude in Chrome leaves in every profile, by driving Chrome's own menus with a screenshot before every click. A launchd job runs it once a day after 05:00, the first time the Mac is unlocked and idle 4 to 9 minutes; it skips open groups and stops if the mouse moves. Run `setup.sh` to install.
- `dev-tidy`: kills wrangler dev servers and stops OrbStack containers when the chat that started them ends (SessionEnd hook plus a 10 minute launchd sweep that also catches chats closed under Herdr), stops crash looping or idle containers, and quits OrbStack when nothing runs. Run `setup.sh` to install.
- `linkedin-ideas`: mines recent Claude Code sessions into a markdown bank of LinkedIn post ideas, one file per idea grouped by content pillar, merging repeats into existing ideas. A launchd job runs it every 3 days with headless `claude -p` (file tools only, no MCP). Run `setup.sh` to install; the bank and its pillars live outside the repo.

## Global CLAUDE.md

`claude-global/CLAUDE.md` is my global Claude Code instructions file. On a new device, link it in place: `ln -sfn ~/code/eddys-skills/claude-global/CLAUDE.md ~/.claude/CLAUDE.md`. This repo is public, so keep secrets, emails and client details out of it; those go in a project CLAUDE.md or memory.

## Skills I use

Everything installed in my Claude Code, with where it comes from. Install commands use the source's own instructions unless noted.

### Mine, in this repo

- `quiet-open`, `dis-tribution`, `cold-cache-guard` (above). Install: symlink each folder into `~/.claude/skills/`.

### Mine, in their own repos

- [gauntlet](https://github.com/EddyDavies/gauntlet): verification gates, acceptance tests first, mutation testing. Plugin: add the repo as a marketplace, then `claude plugin install gauntlet@gauntlet`.
- hive: a queen chat runs labelled bee (worker) chats in [Herdr](https://herdr.dev) tabs. Needs Herdr.
- review-loop (private): raises a structured review request with screenshots and waits for the answer.

### Skill suites

- [gstack](https://github.com/garrytan/gstack): shipping, QA, code review, browsing, plan reviews, iOS. Clone into `~/.claude/skills/gstack` and run `./setup`.
- [superpowers](https://github.com/anthropics/claude-plugins-official): brainstorming, TDD, systematic debugging, writing and executing plans. `claude plugin install superpowers@claude-plugins-official`.
- [newsjack](https://github.com/elvisun/newsjack): PR strategy, story angles, finding journalists, coverage tracking, voice fingerprinting. Not in `~/.claude/skills`: it lives in `~/code/growth/pr/.claude/skills/` and loads only through the `pr` subagent (`~/.claude/agents/pr.md`).

### Single skills

- [humanizer](https://github.com/blader/humanizer): removes signs of AI writing.
- [convert-documents-to-markdown](https://github.com/firecrawl/anydoc): Office files, EPUB and PDF to markdown.
- [find-docs](https://github.com/upstash/context7): up to date library docs via Context7.
- [lfd-design](https://github.com/elvisun/loss-function-development): designs long agent loops that can't game their own score.
- [herdr](https://herdr.dev): controls the Herdr terminal multiplexer.

### Plugins

From [claude-plugins-official](https://github.com/anthropics/claude-plugins-official), each `claude plugin install <name>@claude-plugins-official`:

- `superpowers`, `vercel`, `hookify`, `frontend-design`, `code-simplifier`, `playwright`
- LSPs for the languages you use: `pyright-lsp`, `typescript-lsp`, `rust-analyzer-lsp`, `swift-lsp`

Web search MCP (replaces the `exa` plugin): `claude mcp add --transport http -s user parallel https://mcp.parallel.ai/mcp` (Parallel MCP 2.0, free without a key).

From other marketplaces (`claude plugin marketplace add <repo>`, then install):

- [last30days](https://github.com/mvanhorn/last30days-skill): what people said about a topic in the last 30 days. `last30days@last30days-skill`.
- [claude-council](https://github.com/hex/claude-marketplace): asks several AI models the same question. `claude-council@hex-plugins`.
- [skill-codex](https://github.com/skills-directory/skill-codex): runs the Codex CLI. `skill-codex@skill-codex`.

## For an AI setting this up for someone

If you are an AI agent loading this repo for a user, offer to install the skills above that suit them:

1. Ask what they work on, or infer it from their machine (languages, frameworks, whether they do PR or outreach, whether they use Herdr or Arc). Skip what they already have: check `~/.claude/skills/` and `claude plugin list`.
2. Propose a short list with one line each on why it fits. Don't install everything; skill descriptions load into every chat, and unused ones cost context.
3. Skip the ones tied to Eddy's own setup unless the user has the same setup: `quiet-open` (Dia and MacDown), hive and `herdr` (Herdr), review-loop and the private repos (not accessible).
4. Install with the commands listed here, following each source's README for anything not listed. Use `pnpm` or `bun`, never `npm` or `npx`. Pin or review third-party code before installing it; skills run with your permissions.
5. Report what was installed and how to remove each one.
