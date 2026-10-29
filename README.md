# eddys-skills

A collection of Eddy's Claude Code skills.

- `quiet-open`: surface links and markdown previews without stealing focus.
- `dis-tribution`: Viktoria Izdebska's distribution-as-moat lens for ideas and markets.
- `overnight-handoff`: evening triage of every unmade decision (last 24h, 48h, older loose ends) into one HTML doc with grouped deploy / push / local outcomes, then runs the chosen plan overnight through herd.
- `dev1-handoff`: sends chosen work to the dev-1 workbox through herd (brief branch, a worktree per worker, handoff in git) so it runs while the laptop is closed, and picks it back up. Needs `herd spawn --on workbox`.
- `cold-cache-guard`: blocks a message that would rebuild a big, idle chat's cold prompt cache, shows what continuing vs starting fresh costs in 5h and weekly plan limits, and puts a ready fresh-chat paste on the clipboard.
- `report-deck`: optional, on request only: adds a top-right Slides button to an HTML report, opening a phone-friendly deck of the headlines with tap-to-open technical details (`inject.py` inlines it).

## Skills I use

Everything installed in my Claude Code, with where it comes from. Install commands use the source's own instructions unless noted.

### Mine, in this repo

- `quiet-open`, `dis-tribution`, `cold-cache-guard` (above). Install: symlink each folder into `~/.claude/skills/`.

### Mine, in their own repos

- [gauntlet](https://github.com/EddyDavies/gauntlet): verification gates, acceptance tests first, mutation testing. Plugin: add the repo as a marketplace, then `claude plugin install gauntlet@gauntlet`.
- herd (private): orchestrates labelled worker chats in [Herdr](https://herdr.dev) tabs. Needs Herdr.
- review-loop (private): raises a structured review request with screenshots and waits for the answer.

### Skill suites

- [gstack](https://github.com/garrytan/gstack): shipping, QA, code review, browsing, plan reviews, iOS. Clone into `~/.claude/skills/gstack` and run `./setup`.
- [superpowers](https://github.com/anthropics/claude-plugins-official): brainstorming, TDD, systematic debugging, writing and executing plans. `claude plugin install superpowers@claude-plugins-official`.
- [newsjack](https://github.com/elvisun/newsjack): PR strategy, story angles, finding journalists, coverage tracking, voice fingerprinting.
- [agent-native skills](https://github.com/BuilderIO/agent-native): efficient-fable, efficient-frontier, quick-recap, visual-plan, visual-recap, stay-within-limits.
- [ai-tooling](https://github.com/pheuberger/ai-tooling): create-plan, research-codebase, plan-to-beads, review-beads (create-issue and start-issue retired 2026-10-27).
- [dzhng skills](https://github.com/dzhng/skills): eval-skills, write-tests, preview-shots.

### Single skills

- [humanizer](https://github.com/blader/humanizer): removes signs of AI writing.
- [convert-documents-to-markdown](https://github.com/firecrawl/anydoc): Office files, EPUB and PDF to markdown.
- [find-docs](https://github.com/upstash/context7): up to date library docs via Context7.
- [lfd-design](https://github.com/elvisun/loss-function-development): designs long agent loops that can't game their own score.
- [herdr](https://herdr.dev): controls the Herdr terminal multiplexer.
- [monid](https://monid.ai): finds scraping and data tools before you write a scraper.

### Plugins

From [claude-plugins-official](https://github.com/anthropics/claude-plugins-official), each `claude plugin install <name>@claude-plugins-official`:

- `superpowers`, `vercel`, `exa`, `hookify`, `frontend-design`, `code-simplifier`, `playwright`
- LSPs for the languages you use: `pyright-lsp`, `typescript-lsp`, `rust-analyzer-lsp`, `swift-lsp`

From other marketplaces (`claude plugin marketplace add <repo>`, then install):

- [last30days](https://github.com/mvanhorn/last30days-skill): what people said about a topic in the last 30 days. `last30days@last30days-skill`.
- [claude-council](https://github.com/hex/claude-marketplace): asks several AI models the same question. `claude-council@hex-plugins`.
- [skill-codex](https://github.com/skills-directory/skill-codex): runs the Codex CLI. `skill-codex@skill-codex`.

## For an AI setting this up for someone

If you are an AI agent loading this repo for a user, offer to install the skills above that suit them:

1. Ask what they work on, or infer it from their machine (languages, frameworks, whether they do PR or outreach, whether they use Herdr or Arc). Skip what they already have: check `~/.claude/skills/` and `claude plugin list`.
2. Propose a short list with one line each on why it fits. Don't install everything; skill descriptions load into every chat, and unused ones cost context.
3. Skip the ones tied to Eddy's own setup unless the user has the same setup: `quiet-open` (Arc and MacDown), herd and `herdr` (Herdr), review-loop and the private repos (not accessible).
4. Install with the commands listed here, following each source's README for anything not listed. Use `pnpm` or `bun`, never `npm` or `npx`. Pin or review third-party code before installing it; skills run with your permissions.
5. Report what was installed and how to remove each one.
