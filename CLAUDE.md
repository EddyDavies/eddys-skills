# eddys-skills

This repo is the source of truth for Eddy's personal Claude Code skills. Skills are only discovered by Claude Code from `~/.claude/skills/`, so a skill living here does nothing until it is symlinked there.

## Rule: always symlink new skills globally

Whenever a skill directory is added to (or renamed in) this repo, immediately create a matching symlink so it registers:

```bash
ln -s /Users/eddydavies/code/eddys-skills/<skill-name> /Users/eddydavies/.claude/skills/<skill-name>
```

- The real files stay in this repo; `~/.claude/skills/<skill-name>` must be a symlink, never a copy (copies drift).
- On rename: `mv` the repo directory, update the `name:` field in its SKILL.md frontmatter, remove the old symlink, and create a new one.
- On delete: remove both the repo directory and its symlink.
- To verify a skill is wired up: `ls -la ~/.claude/skills/ | grep <skill-name>` should show a symlink into this repo.
