# Global CLAUDE.md rules for the quiet-open flow

These bullets belong in `~/.claude/CLAUDE.md` under the "Output format" section. `setup.sh` cannot merge prose safely, so add them by hand (or have Claude merge them) if they are missing. Keep them in sync with the live file; the live file wins on conflict.

```markdown
- **`open <path>` after generating** so I can review it without hunting.
- **Never open web links (`http://`/`https://` URLs) with plain `open`.** Raising a browser steals my focus and lands on the wrong desktop in my multi-desktop layout. Instead run `arcopen '<url>'`: it loads the page as a background tab in Arc (no focus steal, no desktop switch) and sends a desktop notification that the page is ready. The tab lands in my "vibe coding" space by default; a project CLAUDE.md can override that with a line like `Arc space: content`, and an explicit second argument (`arcopen '<url>' 'projects'`, or `'active'` for the current space) overrides both. If Arc is not available, arcopen falls back to `notify-web-ready.sh` (notification plus URL on the clipboard) on its own. A PreToolUse hook enforces this by blocking any `open` of an http(s) URL. This only applies to actual URLs, not local file artifacts (HTML reports, PDFs, images); those keep using plain `open <path>` per the rule above.
- **Open markdown plans/specs/docs with `mdpreview <file>`, not `open`.** Any `.md` you produce or want me to review — implementation plans, design specs (e.g. `docs/superpowers/specs/*.md`), research notes, anything plan-like — surface it with `mdpreview <file>` so it renders. `mdpreview` opens the file in MacDown with the editor pane collapsed (preview only); it takes one file per call. Use plain `open` only for non-markdown artifacts (HTML, PDFs, images).
```
