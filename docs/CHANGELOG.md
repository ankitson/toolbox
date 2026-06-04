# Toolbox Changelog

## 2026-06-04

### Summarize CLI integration
- Added `bin/summarize`, a Node 24+ preflight wrapper around
  `npx -y @steipete/summarize`.
- Added `skills/summarize` with terse CLI-only usage guidance for agents.
- Added `just summarize` and README usage examples.

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

## 2026-06-02

### Declarative skill manager
- Added `skills.json` as the source of truth for custom, vendored, and
  repo-backed skills.
- Added `bin/skillctl` to add, sync, remove, list, validate, and document skills.
- Replaced manual edits to `VENDORED.md` with generated provenance docs.
- Replaced the destructive one-off `just vendor` recipe with `just skills-*`
  manager commands.
- Added local-Git regression coverage for custom, vendored, and repo-backed
  workflows and overwrite guardrails.
- Documented the ownership boundary: `devdocker/dotfiles` chezmoi wiring handles
  distribution; toolbox only manages canonical skill contents and provenance.

## 2026-06-02

### Resume-session submit handling
- Changed `bin/resume-session` to send scheduled prompt text and the submit
  carriage return separately, with a short delay between writes.
- Added a regression test and a `just test-resume-session` command.

### Simplify skill registry
- Replaced `skills.json` with `skills.toml`, listing external Git sources only.
- Reduced `bin/skillctl` to add, sync, list, and check copied snapshots.
- Removed generated `VENDORED.md`, repo-backed symlinks, clone caches, custom
  skill records, revision records, and manager-owned deletion.
- Treat every unlisted directory under `skills/` as an ordinary custom skill.
- Added repo-only `skillctl add owner/repo` support with default-path detection
  for root skills, `skills/<name>/`, `<name>/`, and single-skill repos.

### Web clipper
- Added `bin/web-clip`, a URL-to-Markdown folder clipper that stores `index.md`,
  fetched `source.html`, and downloaded image media.
- Added `skills/web-clip` with usage guidance for clipping/archive requests.
- Added a `just web-clip <url> [output]` recipe.
- Added file-URL test coverage and optional Playwright `--browser` mode for
  JavaScript-rendered pages.
- Verified the required All Things Distributed article, Python docs, and an AWS
  blog smoke case.
