---
name: report-deck
description: Optional extra, only when Eddy asks for slides or a deck version of an HTML report, plan or results page. Adds a top-right "Slides" button that opens a phone-friendly slide deck of the headline points, each slide with tap-to-open technical details. Never add it by default.
---

# report-deck

Opt in only. Eddy found the Slides button annoying on every page (26 Oct 2026), so add it only when he asks for slides on a specific page. To remove it from a page, strip the blocks between `<!-- report-deck-css:start -->` and `<!-- report-deck-css:end -->` and between `<!-- report-deck:start -->` and `<!-- report-deck:end -->`.

## What it produces

- A small "Slides" button fixed in the top-right corner of the page.
- Tapping it opens a full-screen deck: one headline per slide, 2 to 4 short points, an optional verdict tag, and collapsible "details" cards for the important technical facts behind that headline.
- Navigation: Next/Back buttons, dots, arrow keys, swipe, Esc to close. `#slides` or `#slides-3` in the URL opens the deck directly.
- Self-contained: CSS, JS and data are inlined, no network. It reads the page's colour tokens (`--bg`, `--fg`, `--muted`, `--line`, `--card`, `--acc`/`--accent`, `--good`/`--warn`/`--bad` and their `bg` variants) when they exist, so it matches the report in light and dark mode.

## How to add it

1. Write the report as usual.
2. Write a deck file next to your scratch files (not into the repo), e.g. `<scratchpad>/<report-name>.deck.json`. A full worked example is `example.deck.json` in this folder. Shape:

```json
{
  "title": "LINE, KakaoTalk, WeChat",
  "slides": [
    {
      "kicker": "Bottom line",
      "title": "All three can host Pally, none as openly as Telegram",
      "tag": { "tone": "good", "text": "LINE first" },
      "points": ["Point one, one line", "Point two"],
      "details": [
        { "label": "Pricing", "body": "<p>HTML allowed: <code>code</code>, lists, links.</p>" }
      ]
    }
  ]
}
```

3. Inject it (idempotent; re-run after every edit to the report or the deck):

```bash
uv run --no-project python ~/.claude/skills/report-deck/inject.py <report.html> <deck.json>
```

4. Open the report as usual (`diaopen '<path>'`).

## Writing the slides

- Slide 1 is the answer: the decision or result in one headline. Last slide is what Eddy must decide or do, phrased as one-line replies he can send.
- One headline per slide, written as a claim ("LINE is the closest fit to Telegram"), not a topic ("LINE").
- Points are the facts he needs at a glance: at most 4, one line each, plain words.
- Details hold the evidence that backs the headline: numbers, limits, costs, what is unverified. Put each fact under the slide it supports, not on a separate appendix slide.
- **Plain words first, everywhere.** Eddy does not want to read code. Explain what a thing does in everyday language; a code name (endpoint, function, file, sha) appears only as a secondary label beside that plain explanation, never on its own. Prefer "Pally checks each linked account for new messages" over "`getupdates` long poll".
- **Show comparisons as tables, quantities as bars.** If a detail compares two or more things across the same attributes, it is a table. If it lists numbers for several groups, it is a bar chart with a sentence saying what the number means and what it implies. Never squash either into a sentence. A plain list of unrelated items stays a bullet list.
- A slide whose headline is itself a comparison carries the table in `visual` (shown on the slide), not hidden in details.
- Tag tone: `good` go, `warn` caution or pilot, `bad` hold or blocked.
- Usually 5 to 9 slides. Every important headline in the report appears.

## Tables, bars and colour

Details and `visual` take HTML. Tables are wrapped for horizontal scroll automatically.

```html
<table>
  <tr><th>Plan</th><th class="n">Per month</th></tr>
  <tr><td>Free</td><td class="n">¥0</td></tr>
</table>

<div class="dk-bars">
  <div class="dk-bar" style="--v:100%"><span>WeChat<small>China, Hong Kong</small></span><i></i><b>155</b></div>
  <div class="dk-bar" style="--v:43%"><span>LINE<small>Japan, Thailand</small></span><i></i><b>67</b></div>
</div>
```

- `class="n"` right-aligns a number column.
- `--v` is the bar length as a percentage of the largest value shown.
- `class="dk-g"`, `dk-w`, `dk-r` colour a cell or word good, caution or bad.
- Same writing rules as the report: no dashes as punctuation, no punctuation right after a path or URL.

## Do not

- Load the deck from a CDN or a separate file; it must survive being opened from disk or shared as one file.
- Hand-paste deck.js into the report; always use `inject.py` so updates to the skill reach every report on re-run.
