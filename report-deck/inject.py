"""Inline the report deck into an HTML report.

Usage: uv run --no-project python inject.py <report.html> <deck.json>

Idempotent: re-running replaces the previous deck block. Fails loud on a bad deck.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
START, END = "<!-- report-deck:start -->", "<!-- report-deck:end -->"
CSS_START, CSS_END = "<!-- report-deck-css:start -->", "<!-- report-deck-css:end -->"


def validate(deck: dict) -> None:
    slides = deck.get("slides")
    if not isinstance(slides, list) or not slides:
        sys.exit("deck.json: 'slides' must be a non-empty list")
    for i, s in enumerate(slides, 1):
        if not s.get("title"):
            sys.exit(f"deck.json: slide {i} has no title")
        tag = s.get("tag")
        if tag and tag.get("tone") not in {"good", "warn", "bad"}:
            sys.exit(f"deck.json: slide {i} tag tone must be good, warn or bad")
        for d in s.get("details", []):
            if not d.get("label") or not d.get("body"):
                sys.exit(f"deck.json: slide {i} has a detail without label or body")


def strip_block(html: str, start: str, end: str) -> str:
    return re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?", "", html, flags=re.S)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    report, deck_path = Path(sys.argv[1]), Path(sys.argv[2])
    html = report.read_text()
    deck = json.loads(deck_path.read_text())
    validate(deck)
    if "</head>" not in html or "</body>" not in html:
        sys.exit(f"{report}: needs </head> and </body>")

    html = strip_block(strip_block(html, START, END), CSS_START, CSS_END)
    css = (HERE / "deck.css").read_text()
    js = (HERE / "deck.js").read_text()
    data = json.dumps(deck, ensure_ascii=False, indent=1).replace("</", "<\\/")

    html = html.replace("</head>", f"{CSS_START}\n<style>\n{css}</style>\n{CSS_END}\n</head>", 1)
    block = (
        f'{START}\n<script type="application/json" id="deck-data">\n{data}\n</script>\n'
        f"<script>\n{js}</script>\n{END}\n"
    )
    html = html.replace("</body>", block + "</body>", 1)
    report.write_text(html)
    print(f"deck injected: {len(deck['slides'])} slides into {report}")


if __name__ == "__main__":
    main()
