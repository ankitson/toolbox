# Toolbox Changelog

## 2026-06-19

### Summarize output copies
- Changed `bin/summarize` to stream stdout as before while saving successful
  stdout-producing runs under `/tmp/summarize/`.
- Added timestamped saved-file names that distinguish summaries from
  `--extract` transcript/source output.
- Updated the summarize skill guidance, OpenAI agent metadata, and README usage
  notes to mention saved output copies.
- Added focused regression coverage for saved stdout copies and a
  `just summarize-test` helper.

## 2026-06-18

### Skill router generation
- Added `bin/skillctl router` to generate a portable router skill from installed
  skills by explicit skill names, `skills.sh.json` group titles, or glob
  source-group labels.
- Added `skills.toml` router tables with `absorbs = ["repo:path"]` entries as
  the authoritative source for bundled skill provenance.
- Added generated root `skills.sh.json` output using the existing Skills.sh
  grouping convention.
- Added `templates/skillctl/router.SKILL.md`, rendered with stdlib
  `string.Template`, so router wording lives outside the Python CLI.
- Added `just skills-router` and README examples for explicit, group-based, and
  source-group router generation.
- Made `skillctl sync` sync standalone sources first, then materialize all
  routers and absorb their component skills from the active top-level skill
  tree by default.
- Changed bundled router references from nested `SKILL.md` files to
  `instructions.md`, preventing recursive skill scanners from showing duplicate
  skills.
- Added `skills/minimalist-entrepreneur`, generated from the
  `Minimalist Entrepreneur` group with ten absorbed reference skills.
- Added absorbed `cloudflare` and `agent-workflows` routers. `zoom-out` is kept
  via a local vendored copy from historical upstream commit
  `801a01cc7d265e06dd9dbcef5a4c471add05a0b3`.
- Added regression coverage for router generation, copied references, source
  marker exclusion, explicit skill selection, `skills.sh.json` groups, and
  overwrite/absorb protection.

## 2026-06-15

### Serializd review fixes
- Fixed `review-add` failing with `500 Internal Server Error`: Serializd's
  `reviews/add` endpoint requires both `backdate` and `rating`, but the payload
  builder stripped any field that was unset. `backdate` is now always sent,
  defaulting to the current time (bare dates like `2024-01-15` are expanded to a
  full ISO 8601 datetime).
- Made `--rating` required for `review-add` and stopped silently sending a `0`;
  an explicit `--rating 0` is still accepted and recorded as "unrated".
- Forced every review the CLI writes to be logged (`is_log` is no longer
  user-toggleable). Unlogged reviews never appear in the diary or logged-episode
  lists, so they can't be found, updated, or deleted from any Serializd surface —
  the CLI no longer creates that orphaned state. Removed the `--log`/`--no-log`
  flags accordingly.
- Improved HTTP error reporting across all requests: errors now include the
  method, URL, status, reason, and server response body, and flag `5xx` as a
  server-side failure and `429` as rate limiting.

## 2026-06-11

### Remeddy remote editor launcher
- Renamed the utility to `bin/remeddy`.
- Changed the CLI to `remeddy <host> [app]`, defaulting the app to
  `Visual Studio Code - Insiders`.
- Added remote OS auto-detection over SSH, probing macOS with `uname` and
  Windows with `powershell.exe`.
- Split app handling between Remote-SSH editors and generic GUI apps, so
  commands like `remeddy m2book Spotify` launch the app without VS Code flags.
- Changed macOS launch behavior to use the `code-insiders` CLI and default to a
  new window, avoiding `open -a` activating an unrelated existing workspace.
- Added Windows, macOS, app override, and platform override regression coverage.

## 2026-06-10

### Wined launcher
- Added `bin/wined`, which SSHes to a Windows host and starts VS Code
  Insiders with a Remote-SSH window pointed at the current machine and directory.
- Changed launch behavior to use a short-lived interactive scheduled task so
  the app appears in the logged-in Windows desktop session.
- Preferred the GUI `Code - Insiders.exe` over `code-insiders.cmd` to avoid
  leaving a foreground terminal window behind.
- Suppressed PowerShell CLIXML progress noise from Windows OpenSSH.
- Added focused unit coverage for command construction and argument validation.
- Added `just test-wined` for the focused regression test.

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

## 2026-06-04

### Cloudflare skills
- Added Cloudflare's official external skills from `cloudflare/skills`.
- Registered `cloudflare`, `agents-sdk`, `durable-objects`, `sandbox-sdk`,
  `wrangler`, `web-perf`, `cloudflare-email-service`, and
  `workers-best-practices` in `skills.toml`.
- Copied the skill folders into `skills/` so the existing Codex skills symlink
  can discover them.

## 2026-06-11

### Docme
- Added `bin/docme`, a PEP 723 `uv run --script` tool for building or serving a quick MkDocs Material site from Markdown files.
- `docme` scans all `.md` files under the current directory up to depth 3 by default; `--depth` and `--root` make the scan configurable.
- `docme build --output DIR` writes the built site to a configurable output directory and does not know about webby or deployment.
- `docme` uses an existing `mkdocs.yml`/`mkdocs.yaml` in the root directory before falling back to generated Markdown staging.
- Generated fallback config uses the `pymdownx.slugs.slugify` GitHub-compatible slugifier so hand-written anchors with punctuation resolve.
- `docme` sets `NO_MKDOCS_2_WARNING=true` for MkDocs subprocesses to suppress Material's MkDocs 2.0 banner while preserving normal build output.
- Fallback staging now includes local files linked from Markdown, using symlinks where possible and copies as a fallback.
- `docme` no longer runs MkDocs in strict mode; skipped missing, outside-root, or over-size linked files are reported separately.
- Added a configurable linked-file size cap, defaulting to 25 MiB via `--max-linked-file-size-mib`.
- Generated fallback sites default to Material's slate palette with IBM Plex Sans text and IBM Plex Mono code fonts.

## 2026-06-12

### Docme
- Generated fallback sites now always include a `Docs` listing page.
- When a project already has a root `README.md` or `index.md`, `docme` keeps that homepage and writes the listing to `docs.md` or the next available fallback name.

## 2026-06-19

### Autoresearch skill
- Added `skills/autoresearch` from `uditgoenka/autoresearch` at upstream commit
  `166755a2600a`.
- Registered the external source in `skills.toml` with `ref = "master"` and
  `path = ".agents/skills/autoresearch"` so future `skillctl sync` runs can
  refresh it.
