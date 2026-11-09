---
name: ui-workshop
description: Use when Eddy asks to workshop, rethink, mock up or explore a UI surface or flow ("let's workshop chips", "give me options for", "mock up variations", "this looks weird, rethink it"), or wants to give feedback on an existing comparison, screenshot or mockup page ("add feedback to this page", "let me pick on the page", "I want to give feedback without typing"). Two modes: a full reference led workshop from nothing (decision points, Mobbin references, live HTML mockups with GIFs, wild options, picks, rounds), or a feedback layer added to a page that already exists (pick cards, per item ratings and notes, Copy as prompt).
---

# UI workshop

Eddy reviews; he does not want to restate the method. Every workshop follows this shape unless he says otherwise. Project specific rules (brand tokens, product rules, things the client has rejected) live in the project's CLAUDE.md and memory: read them first and obey them in every option.

## 0. Pick the mode

| Situation | Mode |
|---|---|
| A page or document with the options already exists (a comparison page an agent built, screenshots, a mockup report) and Eddy needs to judge it | **Feedback layer** (below). Do not rebuild or restyle it |
| Nothing exists yet, or he asks to rethink or explore a surface | **Full workshop** (sections 1 to 8) |
| A page exists but it is thin (one idea, no references, no visual per option) and he asked to workshop | Ask in `AskUserQuestion`: "Add feedback to the existing page (Recommended)" or "Run a full workshop from it". The full run keeps the existing page as the "today" capture and as one option |

Either way, Eddy never answers visual choices in the terminal picker or by typing in chat: the page carries the controls.

## Feedback layer (existing page)

1. Read the page. Work out the open decisions (usually one to three) and the items he would rate (each option card, screenshot or variant). Give decisions letters and options codes (`A1`, `A2`), recommended one marked.
2. Add the kit: set `window.WORKSHOP_FEEDBACK` (key, intro prompt, decisions, item selector, where the pick cards go), then paste `feedback-kit.html` from this skill's folder just before `</body>`. Its header comment has the config shape. Give items a `data-label` when headings would not name them clearly (case, width, version).
3. If the page loads images from sibling files, also make a self contained copy (images inlined as JPEG data URIs, under about 10 MB) so a `file://` tab in Dia never shows broken images.
4. Check the script parses (`node --check` on the extracted script), then run `diaopen '<path>'` and report what it printed, including the profile and the tab title. Never say a page is already open.
5. Background Chrome check (fork): pick cards and per item chips render, the bar count updates, Copy as prompt produces text that starts with the intro and names each rated item. Clear the kit's localStorage key afterwards.
6. When he pastes the prompt back: act on the picks and notes. If he asks for more options on a decision, switch to the full workshop for that decision only, starting at section 3.

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
- One self contained HTML page per workshop in the project's reports folder (dated), assets beside it, opened with diaopen in the project's Dia profile.
- Recommendation at the top; a pick control and notes per decision, Like/Okay/Dislike plus notes on every option, **Copy as prompt** and Copy JSON so answers round trip; localStorage inside try/catch. Use `feedback-kit.html` from this skill's folder rather than writing these controls again.
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
