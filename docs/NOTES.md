# Toolbox Notes

## 2026-06-04 — Summarize CLI wrapper

### Goal
- Integrate steipete/summarize as a portable CLI helper and agent skill.

### Decision
- Use `npx -y @steipete/summarize` through `bin/summarize` instead of vendoring a
  binary. This avoids platform-specific artifacts while keeping a stable command
  in the toolbox PATH.
- Keep the integration CLI-only. Do not install or configure daemon/browser
  extension mode unless explicitly requested later.
- Followed the local `agent-scripts` skill style: short quoted description,
  terse operational body, no grammar-heavy skill material.

### Verification
- Confirmed local Node is v24.13.0 and npm is 11.6.2.
- Ran `bin/summarize --help` outside the sandbox; npm fetched
  `@steipete/summarize` and the CLI printed help successfully.

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

## 2026-06-02 — Resume-session submit handling

### Discovery
- `wezterm cli send-text` injects text rather than a dedicated key event.
- Sending a Claude Code prompt and `\r` in one write can populate the input box
  without submitting it.

### Change
- Send prompt text and the submit carriage return as separate direct writes,
  with a short delay so the terminal UI processes them independently.
- Added a focused regression test and `just test-resume-session`.

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

## 2026-06-03 — Web clipper

### Goal
- Add a portable tool and skill that saves a URL as Markdown plus local media.
- Test first on the All Things Distributed storage-system article, which should
  produce hundreds of words and multiple images.

### Discovery
- Steipete's `markdown-converter` skill uses MarkItDown for file/HTML
  conversion, but does not archive webpage media.
- Steipete's `browser-use` skill and `browser-tools.ts` are useful references
  for future rendered-page fallback, but the first implementation should not
  depend on an interactive browser session.
- Steipete's `summarize` CLI handles URLs/files/media and extract-only modes,
  but is summary-oriented rather than a folder-based web archive.

### Initial design
- Add `bin/web-clip` as a Python CLI.
- Static-fetch public HTML, choose likely article/main content, convert common
  HTML structures to Markdown, download image media, and write `index.md`,
  `source.html`, and `media/`.
- Add `skills/web-clip` so agents know when and how to use it.

### Verification
- Local file fixture: Markdown conversion, image download/rewrite, figure
  captions, links, lists, code, and source HTML preservation.
- Browser fixture: Playwright-rendered JavaScript page clips correctly outside
  the sandbox; the sandbox itself blocks Chromium launch.
- Required article:
  `allthingsdistributed.com/2023/07/building-and-operating-a-pretty-big-storage-system.html`
  clipped to ~6.6k words and 9 downloaded images with no mojibake.
- Extra smoke checks:
  `docs.python.org/3/library/urllib.parse.html` clipped to ~5.7k words;
  `aws.amazon.com/blogs/aws/amazon-s3-update-strong-read-after-write-consistency/`
  clipped to ~700 words and 2 images.
