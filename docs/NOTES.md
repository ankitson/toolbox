# Toolbox Notes

## 2026-07-14

### Shared Parakeet transcription skill

#### Goal

Replace an OpenClaw-bundled transcription skill whose hard-coded OpenAI model
could be routed to an incompatible provider with a reusable skill owned in the
shared toolbox.

#### Discovery

- Bifrost request `44733b2a-062e-4649-8e71-08fcf800ba79` used provider `codex`
  and model `gpt-4o-transcribe`; Codex rejected transcription as an unsupported
  operation.
- OpenClaw's bundled `openai-whisper-api` script defaults to that model and does
  not consume its configured `config.model`, so setting only the OpenClaw skill
  config did not affect the multipart request.
- The Parakeet-compatible endpoint may return `{"text":"..."}` even when the
  request asks for plain text.

#### Decision

- Added `skills/parakeet-asr` with a deterministic Parakeet default model while
  keeping the API base, credential, and model override environment-driven so it
  can be reused by any harness mounting toolbox skills.
- The script uses an atomic temporary output, fails on non-2xx responses, and
  unwraps JSON text responses for `.txt` output.
- OpenClaw configuration and deployment remain in devserver; toolbox contains
  no deployment-specific credential.

#### Verification

- Shell syntax and ShellCheck passed.
- OpenClaw discovered the skill from `agents-skills-personal` with all runtime
  requirements satisfied.
- An end-to-end fixture request through OpenClaw's configured environment,
  Bifrost, and Parakeet produced an 871-character plain-text transcript.

## 2026-06-24

### Document work chronology

#### Discovery
- The work logs had drifted into repeated same-day date headers and mixed
  chronological order, especially after append-only updates.
- The `document-work` skill did not state the reverse-chronological,
  one-header-per-day convention.

#### Decision
- Normalize notes and changelog sections by date, latest first.
- Use one `## YYYY-MM-DD` header per day, with same-day work items grouped as
  `###` sections below it.
- Update the `document-work` skill so future agents preserve this structure.

### Chezmoi skill apply safety

#### Discovery
- The chezmoi skill advised agents to run `chezmoi apply --refresh-externals
  --force`, which bypasses chezmoi's overwrite prompts and can discard local
  dotfile edits.
- Running `chezmoi apply` without `--force` can require interactive decisions,
  which is a poor fit for agent environments.

#### Decision
- Treat source-state edits and destination applies as separate phases.
- Require preview plus explicit current-conversation consent before applying
  changes to live dotfiles.
- Prefer targeted `chezmoi apply --no-tty <target...>` after approval, stop if
  chezmoi needs an interactive decision, and reserve `--force` for exact
  target paths the user explicitly approved.

### Network listener range grouping

#### Discovery
- Docker publishes host port ranges as individual socket listeners. A mapping
  like `3000-3100:3000-3100` produces one listener per port and can use distinct
  proxy PIDs for IPv4/IPv6.

#### Decision
- Collapse text report rows for consecutive runs of at least five ports when
  protocol, process name, bind pattern, and notes match.
- Group text report rows by process name by default, with
  `--no-process-groups` available for the protocol/port detail view.
- Keep JSON output uncollapsed so exact per-listener details remain available.

### Network listener audit helper

#### Goal
- Add a portable toolbox command for checking which local services are exposed
  through wildcard binds, LAN/private IPs, Tailscale-only binds, or other
  non-loopback interfaces.

#### Decision
- Use Linux `ss` as the socket source and `ip -j addr show` for interface
  context, so Docker/libvirt bridge addresses are not mistaken for physical LAN
  addresses.
- Keep the helper dependency-free and provide JSON output for follow-up
  automation.

#### Verification
- Added unit coverage for socket parsing, interface classification, and
  Tailscale-only grouping.

## 2026-06-22

### Windows WezTerm SSHMUX freeze tracing

#### Discovery
- A frozen Windows client was still connected to the Linux mux as
  `desktop-win`, PID `64616`, through proxy PID `3151073`.
- Linux-side `wezterm-trace` showed 0 focus transitions during the freeze, so it
  did not match the June 13 PaneFocused storm signature.
- Windows process sampling showed `wezterm-gui.exe` was `Responding=True` but
  consuming roughly one CPU-second per wall-second on a single hot thread.
- Windows was running `wezterm 20260117-154428-05343b38`, while the Linux tool
  reported `20260425-155631-44a8f937`; the local fork keeps the resize dead-loop
  and activate-tab resize fixes on separate branches from the PaneFocused fix.

#### Artifacts
- Linux mux trace:
  `/home/ankit/wezterm_traces/wezterm-trace-20260622-143642.tar.gz`.
- Manual Windows minidump and process evidence:
  `logs/wezterm-windows-freeze-20260622-144023/`.
- Repeatable Windows trace-helper run with fetched minidump:
  `/home/ankit/wezterm_traces/wezterm-win-trace-20260622-145036/`.

#### Decision
- Add a Windows-side SSH trace helper so future freezes can capture process
  samples, thread CPU, logs, optional minidumps, and optional WPR traces without
  hand-written PowerShell.

## 2026-06-19

### Autoresearch skill import

#### Goal
- Add the Autoresearch agent skill to the canonical toolbox skill tree.

#### Decisions
- Use `uditgoenka/autoresearch` instead of `karpathy/autoresearch`.
- Track the upstream `master` branch explicitly because the repository does not
  publish a `main` branch.
- Import the portable skill from `.agents/skills/autoresearch`, which contains
  the `SKILL.md` and companion command/reference markdown files.

#### Verification
- Synced `skills/autoresearch` from upstream commit `166755a2600a`.

### Summarize saved output copies

#### Goal
- Preserve `summarize` stdout for later lookup without changing the normal
  streaming CLI behavior.

#### Decision
- Keep `summarize` as a custom local skill. `skills.toml` remains only for
  external skill sources and generated router bundles.
- Save successful stdout-producing wrapper runs under `/tmp/summarize/`, using
  timestamped Markdown filenames with `summary` or `transcript` in the name.
- Treat `--extract` output as transcript/source output; all other runs are
  summary output.
- Update `skills/summarize/SKILL.md`, `skills/summarize/agents/openai.yaml`, and
  README usage notes so agents and humans know where saved copies land.

## 2026-06-18

### Portable skill router generation

#### Goal
- Add a `skillctl` workflow for turning a related set of installed skills into
  one portable router skill, starting with the Sahil Lavingia minimalist
  entrepreneur skills.

#### Decisions
- Keep `.skillctl-source` as a registry-label ownership marker. It continues to
  contain values like `slavingia`, not repo provenance such as
  `slavingia/skills`; the authoritative repo and path stay in `skills.toml`.
- Add `bin/skillctl router <name>` as the generator interface. It accepts
  explicit installed skill names, `--group <title>` for semantic groupings in
  `skills.sh.json`, and `--source-group <label>` as a fallback for skills copied
  by a glob registry entry.
- Make router sync the default "one visible router" workflow. It bundles
  selected skills into `references/<skill>/instructions.md` and removes their
  top-level active skill directories while preserving provenance in
  `skills.toml`.
- Move router membership and provenance into `skills.toml` router tables. Router
  `absorbs` entries use `repo:path` specs, with `local:path` reserved for
  locally vendored historical sources.
- Add root `skills.sh.json` using the existing Skills.sh grouping convention.
  This file is generated from `skills.toml` routers; `.skillctl-source` remains
  only a sync ownership marker.
- Render the router `SKILL.md` from
  `templates/skillctl/router.SKILL.md` using Python's stdlib
  `string.Template`, keeping the template separate without adding a runtime
  dependency.
- Copy selected skills into `references/<skill-name>/`, rename bundled
  `SKILL.md` files to `instructions.md`, and omit `.skillctl-source` markers
  from the bundled references. This prevents recursive skill scanners from
  discovering bundled references as duplicate skills.
- Generate `skills/minimalist-entrepreneur` from the
  `routers.minimalist-entrepreneur` `skills.toml` table as the first absorbed
  router skill.
- Add absorbed routers for Cloudflare platform skills and agent workflow skills.
  `zoom-out` was removed upstream from `mattpocock/skills`, so its last upstream
  copy from commit `801a01cc7d265e06dd9dbcef5a4c471add05a0b3` is vendored under
  `vendor/skills/mattpocock/zoom-out` and referenced with a `local:` absorb.

## 2026-06-13

### WezTerm bug investigations (moved to the wezterm repo)

The detailed root-cause / reproduction / fix-verification / deployment notes for the
WezTerm bugs worked on this day — PaneFocused notification storm (#4390 / PR #7763),
`adjust_x_size`/`adjust_y_size` resize dead loop (#7765), and mux resize-sync
(attach undersize #5117, drag desync #5142/#3694) — were relocated to the wezterm
fork at `/projects/external-repo/wezterm/investigations/` (fixes on the `fix/*`
branches of `github.com/ankitson/wezterm`). All three fixes are deployed locally
(Mac `wezterm-gui` bundle + Linux `wezterm-mux-server`); durability needs a one-time
`sudo cp ~/wezterm-patched-bin/* /usr/bin/` (now done).

## 2026-06-12

### Docme generated docs listing

#### Discovery
- Toolbox's root `AGENTS.md` was included in the fallback build as `/AGENTS/`, but projects with a root `README.md` skipped the generated all-docs index because the README became the homepage.

#### Decision
- Keep an existing root `README.md` or `index.md` as the homepage.
- Add a separate generated `Docs` listing page for fallback builds with a homepage, using `docs.md` unless that name is already taken.

#### Verification
- Built `/projects/toolbox` in fallback mode and confirmed the generated `/docs/` page links to `/AGENTS/`.

## 2026-06-11

### Docme Markdown site helper

#### Goal
- Add a standalone toolbox command for turning a directory of Markdown files into a quick MkDocs Material site.

#### Decisions
- Name the tool `docme`.
- Keep the tool self-contained: it builds and serves docs, but does not publish to webby.
- Use PEP 723 metadata with `uv run --script` and depend on `mkdocs-material` directly.
- If `mkdocs.yml` or `mkdocs.yaml` exists in the root directory, delegate to it and only override the build output directory.
- Scan all `.md` files recursively from the current directory, capped at depth 3 by default and configurable with `--depth`.
- Stage discovered Markdown files into a temporary MkDocs docs tree, preserving relative paths, so the output directory can safely be anywhere, including `./site`.
- For generated fallback config, use `pymdownx.slugs.slugify` so anchors such as `#ask--semantic-search` match docs that expect GitHub-compatible punctuation handling.
- Suppress Material for MkDocs' MkDocs 2.0 banner via its `NO_MKDOCS_2_WARNING` environment flag inside `docme` subprocesses.
- Include linked local files in fallback mode so images and other assets referenced by Markdown are present in the built site.
- Do not stage files outside the selected root. Rewrite those links to `file://` URLs and report them as skipped to avoid quietly publishing unrelated local files.
- Avoid strict MkDocs builds for ad hoc docs; report skipped links separately instead of aborting on warnings.
- Cap linked non-Markdown files at 25 MiB by default, configurable with `--max-linked-file-size-mib`.
- Use the same default visual baseline as the job-search docs for generated fallback sites: Material theme, slate palette, IBM Plex Sans text, and IBM Plex Mono code.

#### Verification
- Built a scratch Markdown tree with default depth and confirmed a depth-4 file was excluded.
- Rebuilt with `--depth 4` and confirmed the deeper file was included.
- Verified global dotfiles `just docs-deploy` can use `docme build --output <tmp>` and publish that output separately via webby.
- Built `/projects/job-search` and confirmed `docme` uses its `mkdocs.yml`; the previous anchor warnings disappear.
- Built a fallback scratch doc with `Ask — semantic search` and confirmed `#ask--semantic-search` resolves.
- Verified configured and fallback builds no longer print the Material MkDocs 2.0 banner.
- Built `/projects/toolbox` in fallback mode and confirmed linked media/static files are included while outside-root links are reported without aborting.

### Remeddy remote editor launcher

#### Goal
- Turn the remote editor launcher into a generic command that accepts a remote
  desktop SSH host, detects whether it is macOS or Windows, and opens the
  current directory via VS Code Remote-SSH.

#### Decision
- Rename the utility to `remeddy` for "remote editor".
- Use `remeddy <host> [app]` as the main interface. The optional app name
  defaults to `Visual Studio Code - Insiders`.
- Default `--platform` to `auto`. Probe macOS with `/usr/bin/uname -s`, then
  probe Windows with `powershell.exe` if the Unix probe fails.
- Treat VS Code-like apps (`code`, `codium`, `cursor`) as Remote-SSH editors.
  Those receive `--remote ssh-remote+<target> <path>` arguments.
- Treat other apps as ordinary GUI apps. On macOS this means `open -a <app>`;
  on Windows this means launching the executable without Remote-SSH arguments.
- For macOS Remote-SSH editors, use the app CLI from PATH or the normal app
  bundle locations instead of `open -a`, because `open` can simply activate an
  existing editor window and drop the Remote-SSH folder arguments.
- Default macOS Remote-SSH editor launches to `--new-window` unless
  `--reuse-window` is explicitly passed, so an unrelated already-open workspace
  is not reused accidentally.
- Keep explicit `--platform windows|macos` for debugging and dry-run cases where
  probing is not wanted.

## 2026-06-10

### Wined launcher

#### Goal
- Add a small command that can be run from any directory on this Linux machine
  to open that directory in VS Code Insiders running on a remote Windows desktop.
- Name the utility `wined`.

#### Decision
- Use SSH to the Windows host and run a short encoded PowerShell command there.
- Launch the GUI app through a short-lived interactive scheduled task. Direct
  `Start-Process` from Windows OpenSSH can run in the SSH service session and
  never appear on the logged-in desktop.
- Prefer `Code - Insiders.exe` over `code-insiders.cmd`; the batch wrapper can
  leave a foreground terminal window behind when launched from the task.
- Suppress PowerShell progress output and request text output format because
  Windows OpenSSH can otherwise print CLIXML progress records.
- Default the Windows SSH host to `ts-desktop-win`, matching the local SSH
  config, while allowing `CODE_INSIDERS_WINDOWS_HOST` or `--windows-host` to
  override it.
- Use VS Code Remote-SSH's CLI shape: `code-insiders --remote
  ssh-remote+<target> <path>`. The target defaults to this machine's hostname
  and can be overridden with `CODE_INSIDERS_REMOTE_TARGET` or `--remote-target`.
- Preserve the shell's logical `$PWD` when it points at the same directory as
  Python's current working directory, so symlinked project paths remain stable.

## 2026-06-04

### Cloudflare skill bundle

#### Goal
- Add Cloudflare's official Agent Skills to the canonical toolbox skill tree.

#### Discovery
- `cloudflare/skills` is the official upstream and documents compatibility with
  OpenAI Codex.
- The upstream repo has eight actual skill folders under `skills/`: `cloudflare`,
  `agents-sdk`, `durable-objects`, `sandbox-sdk`, `wrangler`, `web-perf`,
  `cloudflare-email-service`, and `workers-best-practices`.
- The README also lists build-agent/build-mcp entries, but those are command
  folders rather than skill folders.

#### Verification
- Added each Cloudflare skill through `bin/skillctl add` so `skills.toml` can
  refresh them later.
- Ran `bin/skillctl check`: 18 external skills, 14 custom skills.

### Summarize CLI wrapper

#### Goal
- Integrate steipete/summarize as a portable CLI helper and agent skill.

#### Decision
- Use `npx -y @steipete/summarize` through `bin/summarize` instead of vendoring a
  binary. This avoids platform-specific artifacts while keeping a stable command
  in the toolbox PATH.
- Keep the integration CLI-only. Do not install or configure daemon/browser
  extension mode unless explicitly requested later.
- Followed the local `agent-scripts` skill style: short quoted description,
  terse operational body, no grammar-heavy skill material.

#### Verification
- Confirmed local Node is v24.13.0 and npm is 11.6.2.
- Ran `bin/summarize --help` outside the sandbox; npm fetched
  `@steipete/summarize` and the CLI printed help successfully.

## 2026-06-03

### Web clipper

#### Goal
- Add a portable tool and skill that saves a URL as Markdown plus local media.
- Test first on the All Things Distributed storage-system article, which should
  produce hundreds of words and multiple images.

#### Discovery
- Steipete's `markdown-converter` skill uses MarkItDown for file/HTML
  conversion, but does not archive webpage media.
- Steipete's `browser-use` skill and `browser-tools.ts` are useful references
  for future rendered-page fallback, but the first implementation should not
  depend on an interactive browser session.
- Steipete's `summarize` CLI handles URLs/files/media and extract-only modes,
  but is summary-oriented rather than a folder-based web archive.

#### Initial design
- Add `bin/web-clip` as a Python CLI.
- Static-fetch public HTML, choose likely article/main content, convert common
  HTML structures to Markdown, download image media, and write `index.md`,
  `source.html`, and `media/`.
- Add `skills/web-clip` so agents know when and how to use it.

#### Verification
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

## 2026-06-02

### Simplified external skill registry

#### Decision
- Replace the broad all-skills manager with a shadcn-style TOML registry.
- `skills.toml` lists external Git sources only. Everything else under `skills/`
  is implicitly custom and edited directly.
- External skills are copied snapshots refreshed by `skillctl sync`.
- Omitted `path` means auto-detect common skill package layouts: repo root,
  `skills/<name>/`, `<name>/`, or the single obvious skill folder.
- Remove generated provenance docs, repo-backed symlinks, local clone caches,
  custom-skill records, revision records, and manager-owned deletion.
- Chezmoi in `devdocker/dotfiles` remains the sole distribution mechanism.

### Resume-session submit handling

#### Discovery
- `wezterm cli send-text` injects text rather than a dedicated key event.
- Sending a Claude Code prompt and `\r` in one write can populate the input box
  without submitting it.

#### Change
- Send prompt text and the submit carriage return as separate direct writes,
  with a short delay so the terminal UI processes them independently.
- Added a focused regression test and `just test-resume-session`.

### Declarative skill manager

#### Goal
- Replace hand-maintained vendored-skill provenance rows with a single
  machine-readable source of truth.
- Support authored skills, portable vendored snapshots, and local repo-backed
  symlinks without taking ownership of distribution.

#### Decisions
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

## 2026-05-29

### Third-party skill management

#### What changed
- Removed the old `sync-skills.py` / `skills.yaml` tarball sync path.
- Evaluated `npx skills` (vercel-labs/skills) and **rejected it** as the manager.
- Settled on: vendor files + commit; `VENDORED.md` tracks provenance.

#### Why not `npx skills`
- It installs into each agent's skill dir (`~/.claude/skills`, `~/.codex/skills`,
  …). Here those are all chezmoi symlinks to this one `skills/` directory, so the
  tool's multi-agent fan-out either writes symlinks-into-the-repo (symlink mode)
  or redundant 4× copies (copy mode) — fighting the symlinks for zero benefit.
- Multi-agent distribution is already solved by the chezmoi symlinks. The only
  thing the CLI added beyond that was fetch-from-GitHub + a lockfile, both of
  which `just vendor` (plain git) + `VENDORED.md` cover without the conflict.
- Removed its `.skill-lock.json` and the `just skills-*` wrappers.

#### Current model
- `/projects/toolbox` is the canonical clone (on the shared `/projects` path, so
  containers see it via the existing bind mount — no per-container clone).
- `~/toolbox` and `~/.agents` are chezmoi symlinks to it; agent skill dirs symlink
  to `skills/`. chezmoi's `run_before_clone-toolbox` clones `/projects/toolbox`
  if absent (no-op when the bind mount already provides it in a container).
- Skills are plain dirs under `skills/`. Committing them IS the distribution.
- Third-party skills: `just vendor <owner/repo> <subpath> <name>` (or hand-copy
  for tool skills like `rdt-cli`), then record in `VENDORED.md`.

#### Follow-up
- Skills that wrap a CLI need the CLI installed separately (see VENDORED.md "Tool
  dependencies"). `rdt-cli` → `uv tool install rdt-cli`.
- Decide whether the untracked `agent-scripts/` clone (steipete reference repo,
  currently gitignored) should be vendored selectively or removed.
