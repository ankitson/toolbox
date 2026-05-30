# Toolbox Changelog

## 2026-05-29

### Skill management cleanup
- Removed the old `sync-skills.py` + `skills.yaml` sync system.
- Evaluated and rejected `npx skills` (vercel-labs/skills) as the manager: it
  installs into per-agent skill dirs, which here are all chezmoi symlinks to this
  one directory — it would fight the symlinks for no gain (multi-agent
  distribution is already solved by the symlinks). Removed its `.skill-lock.json`
  and the `just skills-*` wrappers.
- New flow: skills are plain files under `skills/`; committing them IS the
  distribution. Third-party skills are vendored via `just vendor` (plain git) and
  their sources tracked in `VENDORED.md`.
- Vendored `rdt-cli` (Reddit CLI skill) — requires `uv tool install rdt-cli`.
- `/projects/toolbox` is the canonical clone; `~/toolbox` and `~/.agents` are
  chezmoi symlinks to it; agent skill dirs symlink to `skills/`.
