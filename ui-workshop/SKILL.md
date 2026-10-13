---
name: ui-workshop
description: Use when Eddy asks to workshop, rethink, mock up or explore a UI surface or flow ("let's workshop chips", "give me options for", "mock up variations", "this looks weird, rethink it"). Runs a reference led, multi option design workshop: frame the decision points, pull references (Mobbin first), build live HTML mockups with GIFs of the movement, include wild options, collect picks, and iterate in rounds until a chosen version exists.
---

# UI workshop

Eddy reviews; he does not want to restate the method. Every workshop follows this shape unless he says otherwise. Project specific rules (brand tokens, product rules, things the client has rejected) live in the project's CLAUDE.md and memory: read them first and obey them in every option.

## 1. Frame before drawing
- Write his ask down verbatim at the top of the page. Then restate it as **decision points**: the separate questions actually being decided (for chips: what filters exist, where selected ones live, how H1 and H2 relate, how it moves). One surface often hides three decisions; split them.
- **Capture today**: real screenshots of every screen involved (simulator or live), cropped to the area, with the problem called out. Name each screen with the project's stable screen IDs if a sitemap exists.
- List the **fixed constraints**: product rules, live components to reuse, tokens and fonts, what the backend can and cannot serve today (mark anything that needs new backend as NEW BACKEND).
- Check **consistency**: if the same element appears on several screens, the workshop covers all of them and shows them side by side.

## 2. References (always, before options)
- **Mobbin first**: `mcp__mobbin__search_screens` and `search_flows` (platform ios unless the product is web), several specific queries per decision point. Look at the images, keep the strong ones, cite each by its `mobbin_url`, and download the high res `image_url` into the workshop's assets (links expire). If Mobbin errors, say so and fall back.
- Then named apps from knowledge (say which screen), Pinterest through Eddy's real Chrome only if logged in, and earlier mockups in the repo.
- Put a reference board on the page: each reference, what to steal from it, which option uses it.

## 3. Alternatives
- Per decision point: **at least 5 options**: 3 inside the bell curve (genuinely different directions, never one idea in five colours) and **2 wild but buildable** ones that break the frame.
- When Eddy likes an option, the next round gives **3 variations of it** (different moves, not tweaks), plus how it fits into and evolves from the screens before and after.
- Recommend one per decision point, at the top, with the reason.

## 4. Show, do not describe
- **Live HTML phone mockups** at device size in the real tokens and fonts, built from the live components' look (read the app code), with real content: real product cutouts with the background fully removed (audit them; never use a bad mask), real copy lengths.
- **States**: empty, one, many, error or loading where relevant; light and dark when the app has both.
- **Movement**: every transition, reveal or gesture gets a GIF (Playwright frame stepping from the local HTML, ffmpeg palettegen and paletteuse, under about 1 MB), shown next to its live mockup with a Replay button. Show the screen before and after: what she taps (a ring on the control) and where it lands, both directions (Back).
- Never leave an option as "live only" or a grey box: every option the page asks about has a visual.
- No placeholder handwriting or decoration the project has rejected.

## 5. Each option carries
Label and one line title; the tradeoff in one or two lines; the decision it answers; what it reuses and what it replaces; NEW BACKEND items; the references it drew on.

## 6. The page
- One self contained HTML page per workshop in the project's reports folder (dated), assets beside it, opened with arcopen in the project's Arc space.
- Recommendation at the top; a pick control and notes per decision; **Copy picks as prompt** (and JSON) so answers round trip; localStorage inside try/catch.
- Keep it light: lazy loaded images, no heavy libraries, under about 10 MB; phone width safe, no horizontal scroll. If a page gets big, split it rather than make Eddy wait for it to load.
- Superseded options come off the page once he has picked; keep the record in the bead or an archive page, not in front of him.

## 7. Rounds
- After picks: record decisions (bead notes and project memory), drop what he rejected, iterate on what he chose, and keep **one "chosen version" page** that shows the current flow end to end in order.
- Ask only the genuinely open calls, few per page, each with visuals for every option; settle small calls with a stated default ("going with X unless you say").
- When a decision changes a rule (for example how pieces scale on a card), write it down where future builds will read it.

## 8. Orchestration
- Split independent decision points or surfaces across workers (herd sheepdogs or subagents), one owner per output file, shared assets read only for all but their owner, and a locking helper if several write into one page.
- Mockups only: no app code, no commits, no paid calls, unless Eddy asks. Estimate and cap any paid render.
- Report back in the main chat in a few lines per surface with the page link; never send Eddy to a worker's tab.
