# Toolbox Notes

## 2026-05-29 — Third-party skill management

### What changed
- Removed the old `sync-skills.py` / `skills.yaml` tarball sync path.
- Evaluated `npx skills` (vercel-labs/skills) and **rejected it** as the manager.
- Settled on: vendor files + commit; `VENDORED.md` tracks provenance.

### Why not `npx skills`
- It installs into each agent's skill dir (`~/.claude/skills`, `~/.codex/skills`,
  …). Here those are all chezmoi symlinks to this one `skills/` directory, so the
  tool's multi-agent fan-out either writes symlinks-into-the-repo (symlink mode)
  or redundant 4× copies (copy mode) — fighting the symlinks for zero benefit.
- Multi-agent distribution is already solved by the chezmoi symlinks. The only
  thing the CLI added beyond that was fetch-from-GitHub + a lockfile, both of
  which `just vendor` (plain git) + `VENDORED.md` cover without the conflict.
- Removed its `.skill-lock.json` and the `just skills-*` wrappers.

### Current model
- `/projects/toolbox` is the canonical clone (on the shared `/projects` path, so
  containers see it via the existing bind mount — no per-container clone).
- `~/toolbox` and `~/.agents` are chezmoi symlinks to it; agent skill dirs symlink
  to `skills/`. chezmoi's `run_before_clone-toolbox` clones `/projects/toolbox`
  if absent (no-op when the bind mount already provides it in a container).
- Skills are plain dirs under `skills/`. Committing them IS the distribution.
- Third-party skills: `just vendor <owner/repo> <subpath> <name>` (or hand-copy
  for tool skills like `rdt-cli`), then record in `VENDORED.md`.

### Follow-up
- Skills that wrap a CLI need the CLI installed separately (see VENDORED.md "Tool
  dependencies"). `rdt-cli` → `uv tool install rdt-cli`.
- Decide whether the untracked `agent-scripts/` clone (steipete reference repo,
  currently gitignored) should be vendored selectively or removed.

## 2026-06-02 — Declarative skill manager

### Goal
- Replace hand-maintained vendored-skill provenance rows with a single
  machine-readable source of truth.
- Support authored skills, portable vendored snapshots, and local repo-backed
  symlinks without taking ownership of distribution.

### Decisions
- `devdocker/dotfiles` chezmoi wiring remains the sole distribution layer.
- `skills.json` declares managed skills. `bin/skillctl` materializes external
  sources, validates the live tree, and generates `VENDORED.md`.
- `custom` skills remain tracked directories authored here.
- `vendored` skills remain tracked copies suitable for `git pull` portability.
- Existing vendored snapshots predate source-commit tracking, so their initial
  manifest revisions are explicitly `unknown` until deliberately refreshed.
- `repo` skills point into ignored `.skill-repos/` local checkouts and require a
  local `skillctl sync` after cloning toolbox on a new machine.
- Leave `skills/.system/` outside the manifest because Codex owns that hidden
  subtree and updates it independently.

## 2026-06-02 — Simplified external skill registry

### Decision
- Replace the broad all-skills manager with a shadcn-style TOML registry.
- `skills.toml` lists external Git sources only. Everything else under `skills/`
  is implicitly custom and edited directly.
- External skills are copied snapshots refreshed by `skillctl sync`.
- Omitted `path` means auto-detect common skill package layouts: repo root,
  `skills/<name>/`, `<name>/`, or the single obvious skill folder.
- Remove generated provenance docs, repo-backed symlinks, local clone caches,
  custom-skill records, revision records, and manager-owned deletion.
- Chezmoi in `devdocker/dotfiles` remains the sole distribution mechanism.
