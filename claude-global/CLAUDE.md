# Global Instructions

This file is public: `~/.claude/CLAUDE.md` is a symlink to `~/code/eddys-skills/claude-global/CLAUDE.md`, which is pushed to a public GitHub repo. Never write secrets, tokens, emails, phone numbers, client names or private details into it; put those in a project CLAUDE.md or memory instead.

## Python

- Always use `uv` instead of `pip`, `pip install`, `python -m venv`, or `virtualenv`.
- Use `uv run` to execute Python scripts (e.g. `uv run python script.py`).
- Use `uv add` instead of `pip install` to add dependencies.
- Use `uv init` instead of `python -m venv` to set up new projects.
- Use `uv sync` to install dependencies from pyproject.toml / uv.lock.
- When creating requirements.txt or similar, note that the user manages deps via uv — generate a pyproject.toml instead.

## Node / JavaScript

### Supply-chain security
Every JS project ships with hardened pnpm/bun config (cooldown, blocked exotic subdeps, strict build allowlist) — see memory `js-supply-chain-hardening` for the snippets and TanStack-class attack fingerprint.

## How I work

I work exclusively through Claude Code and agents. I review; I don't write. This means:

- **Manual labor is never a valid path forward.** Don't propose "drag these into place," "hand-edit these files," "click through this tool one by one," or any other option whose effort lives in my hands rather than yours. Those options are closed. If a task can be done by code, it must be done by code — even when the manual version sounds shorter on paper.
- **Calibrate effort estimates around what Claude Code can write, not what a solo human writing every line could ship.** Forking a plugin, adding a toolbar with custom layouts, parsing frontmatter into coordinates, scripting bulk edits across a vault — these are afternoon tasks with me driving, not week-long projects. Don't pad estimates to make manual options "feel" comparable.
- **When two paths look similar but one involves manual downstream work, the code-only path always wins.** Even if the upfront code is more, the lifetime cost of manual labor is higher — and the manual one drifts the moment the data changes.
- **If you catch yourself saying "this is just 30 minutes of clicking" — stop. That's a smell.** Propose the code instead.

## Paid APIs / spending

- **Exception: nothing in this section applies under `~/code/pally/`.** See that folder's `CLAUDE.md`.
- **Estimate cost before any call to an API that charges money.** This covers metered APIs (LLM providers, scraping/enrichment services, search APIs, GetLeads wallet scrapes, Apify actors, cloud services billed per use) and anything that consumes prepaid credits with a cash value. Before making the call(s), work out the expected cost from the provider's pricing and the volume involved (per-request price × number of requests, tokens × token price, credits × credit value), and state the estimate.
- **Hard cap: never spend more than $2 without checking with me first.** If the estimated cost of an operation (or the running total of a batch/loop within a task) would exceed $2, stop before spending and confirm that the spend matches what I actually want: show the estimated cost, what it buys, and any cheaper alternative (smaller sample, cached data, free tier). Only proceed after I approve.
- **Under $2, still say what it cost.** Small spends don't need pre-approval, but report the actual or estimated cost so I can see it.
- **When cost can't be estimated, treat it as over the cap.** If pricing is unknown or the volume is open-ended (unbounded pagination, retry loops, per-result billing you can't predict), ask before spending rather than guessing.

## New skills

- **Every new personal skill goes in `~/code/eddys-skills/<skill-name>/`**, never straight into `~/.claude/skills/`. Then symlink it: `ln -s ~/code/eddys-skills/<skill-name> ~/.claude/skills/<skill-name>` (the repo's own CLAUDE.md has the rename and delete rules). Add a line for it to that repo's README. Project-specific skills that belong to a client repo are the only exception.
- **Every skill for Pally work goes in `personal-agent/skills/` through a PR**, written for the whole team (no hardcoded Eddy login, name or paths). `~/code/pally/pally-skills` is retired. See `~/code/pally/CLAUDE.md` "Skills".

## PostHog

- **All PostHog work goes through the `posthog` subagent** (`~/.claude/agents/posthog.md`), in every project: queries, experiments, flags, replays, dashboards, surveys, SDK health. Never call `mcp__posthog__exec` from the main chat, and never read `~/.claude/posthog-skills/` yourself; the agent does both. Pass it the project id, the question, and pointers to any project memory about the PostHog setup.
- The PostHog plugin is disabled on purpose (its 164 skills cluttered every chat). Don't re-enable it; the skills live in `~/.claude/posthog-skills/` for the agent.

## Cloudflare

- **All Cloudflare work goes through the `cloudflare` subagent** (`~/.claude/agents/cloudflare.md`), in every project: Workers, Pages, D1/KV/R2, DNS, redirect and WAF rules, custom domains, wrangler deploys. Never call `mcp__cloudflare__*` from the main chat, and never read `~/.claude/cloudflare-skills/` yourself; the agent does both. Pass it the repo, the zone or project, and the task.
- The official `cloudflare` plugin is deliberately not installed; its skills live in `~/.claude/cloudflare-skills/` for the agent.

## Namecheap

- **Hard rule: never delete anything in Namecheap that can't be undone without asking me first, every time.** This covers deleting DNS records (`mcp__namecheap__dns_records_delete`), overwriting the record set (`dns_records_save` replaces the whole host list, so any record left out is deleted), deleting or replacing contacts, and anything else that destroys data I can't get back. Before the call, read the current state, show me exactly what will be removed, and wait for an explicit yes in chat for that specific action. A general "go ahead", an earlier approval, or "keep going" does not count. If in doubt whether something is reversible, treat it as irreversible and ask.

## Pally (last resort before giving up)

- **Before telling me something can't be found or reached, ask Pally.** If you've genuinely run out of routes (a tool or MCP is disconnected, the Chrome extension shows no browsers, a page needs my login, a search comes back empty, you don't know a fact about me, my accounts, people or history), send the task to Pally with `mcp__pally__message_pally` in plain words with every detail, and use its reply. Only report "couldn't find it" after Pally has also come up empty, and say that you tried it.
- This doesn't override the routing rules above (PostHog, Cloudflare, Granola subagents, Chrome profile selection); Pally is the fallback when those routes are blocked, not a replacement for them.

## Playwright

- **Headless Playwright work goes through the `playwright` subagent** (`~/.claude/agents/playwright.md`), which starts its own Playwright MCP only while it runs. The `playwright` plugin is disabled on purpose so its server doesn't sit idle in every session; don't re-enable it. The Chrome rule below still applies: logged-in browsing is Claude in Chrome, never this agent.

## Check builds in Chrome, in the background

- **After building or changing anything that renders in a browser (a page, component, app screen, HTML report, deploy), check it in my real Chrome before saying it works.** Don't wait to be asked, and don't stop at "it compiles" or "tests pass".
- **Always do it in the background.** Hand the check to a background subagent (`subagent_type: "fork"`) so the chat keeps going; it reports back when done. The fork follows the Chrome profile rules below, opens a new tab with `tabs_create_mcp` (never reuses or focuses my tabs, never raises the Chrome window or switches desktop), loads the local or preview URL, takes a screenshot, reads console errors and failed network requests, clicks through the changed flow, then closes its tab.
- The fork's report says what it checked, what broke (exact console errors, failing requests, screenshots with full paths), and what it could not check. Fix what it finds, then run the check again.
- If the Chrome extension isn't connected, say so in one line and carry on; don't block the build on it or fall back to another browser.

## Granola

- **All Granola work goes through the `granola` subagent** (`~/.claude/agents/granola.md`), in every project. "Last meeting", "review meeting" and "review granola" all mean: delegate to it. Pass the repo you are in (`git rev-parse --show-toplevel`, or "no repo"), which meeting if not the latest, and any focus. It pulls the full transcript, splits the work into what Eddy builds (frontend, backend), what the client owns (growth, content, ops) and what Eddy must follow up on, and writes one HTML file `<repo>/reports/granola-<name>-<date>.html` with mockups inline, in the repo the meeting is about (never anywhere else; if no repo clearly fits it reports candidates and I ask Eddy, then rerun it with the answer), opens it, and records attendees against the repo in `~/.claude/granola/attendee-repos.json`. Never call `mcp__granola__*` from the main chat.

## Git / Pull Requests

- **Whenever a PR is in a conflicting state, at least propose to fix the merge conflicts.** Whenever you touch a branch that has an open PR — checking it out, reviewing it, pushing to it, looking at its CI, anything — first check `gh pr view <num> --json mergeable,mergeStateStatus`. If it reports `CONFLICTING` / `DIRTY`, surface that to me and offer to merge `origin/<base>` and resolve the conflicts before doing the work I asked for. Don't quietly leave a PR un-mergeable. This applies even when conflict resolution wasn't part of the original request — flag it, propose the fix, then proceed.
- Resolve conflicts by merging the base branch into the feature branch (preserving the PR's commit history). Don't rebase a pushed PR branch unless I explicitly ask — force-pushing rewrites history that reviewers may already be looking at.
- **Before every commit, audit the staged file list.** Run `git diff --cached --stat` (or read the `Changes to be committed` block from `git status`) and account for every path: did I create or intend to modify this in the current session? If no — unstage it (`git restore --staged <path>`) and figure out where it came from (another session's scratch, a generated artifact, IDE droppings, a missing `.gitignore` entry). This matters most when you used `git add -A` / `git add .`, but applies equally when staging by name — the failure mode is *not looking*, not the flag.

## Git worktrees

- **Every worktree lives inside a folder whose name ends in `.noindex`**, so Spotlight (and Raycast file search, which reads the Spotlight index) never indexes it. Default location: `<parent of repo>/worktrees.noindex/<name>`, unless a project CLAUDE.md names another folder.
- A project may name a plain path such as `worktree/` or `.claude/worktrees/`: that path is a symlink to a `.noindex` sibling (`worktree -> worktree.noindex`). Create worktrees through the named path as usual. If the named folder is a real directory and not yet a symlink, rename it to `<name>.noindex` and leave a symlink at the old path before adding the worktree.
- **Nothing `.noindex` ever goes into a repo.** `~/.config/git/ignore` (global, applies to every repo) ignores `*.noindex` and `.claude/worktrees`, so never add these to a repo's `.gitignore`, `.git/info/exclude` or a commit.
- Remove a worktree with `git worktree remove` (no `--force`) once its PR merges or closes.

## When writing code

- **Read before you write.** Before adding code to a file, read its exports, the immediate caller, and any obvious shared utilities. Duplicate functions and conflicting helpers almost always come from skipping this.
- **Fail loud.** "Migration completed" is wrong if records were silently skipped. "Tests pass" is wrong if any were skipped. Surface uncertainty rather than hiding it — silent partial successes are the most expensive bug class.
- **State assumptions; don't guess.** If multiple interpretations of a request exist, name them rather than picking silently. Stop and ask when something is unclear instead of running with a guess.
- **Surgical changes only.** Touch only what the task requires. Don't "improve" adjacent code, comments, or formatting. Don't refactor what isn't broken. Clean up only what your own changes orphaned.
- **Checkpoint multi-step work.** After each significant step in a multi-step task, restate what was done, what's verified, and what's left. Don't continue from a state you can't describe back.

## Output format

- **Default to HTML, not markdown, for standalone deliverables.** Reports, specs, plans, option comparisons, explorations, research synthesis, code-review writeups, design mockups, interactive editors — all HTML. Markdown stays for: in-repo docs (READMEs, CLAUDE.md, contributor docs), Obsidian-vault notes (especially anywhere frontmatter / Juggl / graph rendering is load-bearing), very short outputs, and anywhere downstream tooling expects `.md`. When in doubt, ask which.
- **Save artifacts alongside the work they describe** — in the project they pertain to (`<project>/reports/`, `<project>/docs/`, or beside the file under review), not in a global dumping ground. Date the filename when the artifact captures a point-in-time view (e.g. `premortem-report-20260504.html`).
- **Surface it after generating** so I can review it without hunting: an HTML artifact goes to `arcopen '<path>'` (a background Arc tab in my space, no focus steal); PDFs and images use plain `open <path>`. One deliberate open per deliverable, not per intermediate file.
- **Never open web links (`http://`/`https://` URLs) with plain `open`.** Raising a browser steals my focus and lands on the wrong desktop in my multi-desktop layout. Instead run `arcopen '<url>'`: it loads the page as a background tab in Arc (no focus steal, no desktop switch) and sends a desktop notification that the page is ready. The tab lands in my default Arc space, set by the `Arc space:` line below; a project CLAUDE.md can override that with its own `Arc space: <name>` line, and an explicit second argument (`arcopen '<url>' 'projects'`, or `'active'` for the current space) overrides both. If no `Arc space:` line exists anywhere, the active space is used. If Arc is not available, arcopen falls back to `notify-web-ready.sh` (notification plus URL on the clipboard) on its own. A PreToolUse hook enforces this by blocking any `open` of an http(s) URL. This applies to real URLs and to local HTML artifacts (both go through `arcopen`); PDFs and images keep using plain `open <path>` per the rule above.
- Arc space: code
- **Open markdown plans/specs/docs with `mdpreview <file>`, not `open`.** Any `.md` you produce or want me to review — implementation plans, design specs (e.g. `docs/superpowers/specs/*.md`), research notes, anything plan-like — surface it with `mdpreview <file>` so it renders. `mdpreview` opens the file in MacDown with the editor pane collapsed (preview only); it takes one file per call. Use `arcopen` for HTML and plain `open` for PDFs and images.
- **Reach for interactivity when it earns its keep** — sliders/knobs for tuning, draggable cards for triage, "copy as JSON" / "copy as prompt" buttons to round-trip the result back into Claude. Don't add UI for a static report.
- **Data always goes in a dashboard on a webpage, and I always get it opened.** Whenever a result is data (records, matches, lists of people or companies, counts, metrics, comparisons), build an interactive HTML dashboard: headline numbers as tiles at the top, a searchable, filterable, sortable table of every row, and a chart where it helps. Save it beside the work (`<project>/reports/<topic>-dashboard-<YYYYMMDD>.html`), open it with `arcopen`, and rebuild it whenever the data changes. Never show data only as terminal tables, markdown tables, CSVs or a static report; the chat reply is a short summary that points to the dashboard.
- **No slide version by default.** Don't add the `report-deck` Slides button or deck to HTML reports unless I ask for slides on that page. Make the page itself readable on a phone instead (headline first, short sections).
- **"Chrome" or "the browser" means my real Chrome, through the Claude in Chrome extension.** When I ask you to open Chrome, log in somewhere, or browse as me, use the `mcp__claude-in-chrome__*` tools on my logged-in Chrome. Never launch a separate browser that isn't logged in as me (Playwright or Puppeteer Chromium, a headed persistent profile, gstack browse, a fresh Chrome profile) as a fallback for that. If the extension isn't connected, stop, tell me, and let me fix it (e.g. click the extension icon or restart Chrome); don't route around it. I can explicitly override this for a given task ("use Playwright for this"), but never choose the non-logged-in browser automatically. Headless scraping of public pages with no login needed (Ad Library, public sites) is still fine.
- **Pick the Chrome browser by Google profile, on purpose, before the first browser action.** Several Chrome profiles connect at once (named only "Browser 1", "Browser 2"), and the one preselected for the session is often wrong; never trust it, even when the tool says no question is needed.
  1. Work out the target account: the account or profile I named in my request wins; otherwise run `chrome-profile` (in `~/.local/bin`), which reads a `Chrome profile: <email>` line from the nearest CLAUDE.md walking up, then matches the current folder and its parent against Chrome's profiles (e.g. a work folder → the work account's email). If it exits 1, ask me which account, showing its list.
  2. Run `list_connected_browsers`. Look up each deviceId in `~/.claude/chrome/browser-profiles.json` (deviceId → email). For any unknown deviceId, `select_browser` it, open a new tab to `https://myaccount.google.com`, read the signed-in email, close the tab, and record it in that file.
  3. `select_browser` the deviceId whose email matches the target, then start the task. If none matches, tell me which accounts are connected and stop.
  4. A login wall on a site I use daily means the wrong browser was picked: redo step 2 before anything else.
- **Don't commit large generated HTML into shared branches without flagging it.** HTML diffs are noisy and review-hostile — keep these as local artifacts, or push to a separate publish location (gh-pages, S3) if they need to be shareable.

## Writing style

- **Never use dashes as punctuation in any output.** No em dashes (`—`), no en dashes (`–`), no hyphens used as sentence punctuation (` - `). This applies everywhere: prose, chat replies, code comments, docs, and generated artifacts (proposals, reports, HTML). Use semicolons, commas, colons, or parentheses instead. Hyphens inside compound words (e.g. "multi-site") and markdown list markers are fine.
- **Never put punctuation straight after an email address, URL, path or other copyable value.** I copy these out, and a trailing full stop, comma or bracket gets copied with them. Wrong: `One to hello@example.com.` Right: `One to hello@example.com` (drop the full stop), or restructure so the value isn't last in the sentence, or put it in backticks or on its own line.
- **Never put text I will copy inside a markdown blockquote (`>`).** Emails, WhatsApp messages, DMs, posts, replies, any draft meant to be pasted somewhere else: the quote bar renders nicely in the terminal but gets copied along with the text. Write the draft as plain unindented lines under a short label (e.g. `Draft:`), with a blank line before and after, and no list markers, quote marks or indentation around it. Several drafts get one label each. Blockquotes stay fine for text I only read, such as quoting a source.
