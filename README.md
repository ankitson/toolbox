# toolbox

Universal portable tooling that follows me everywhere — skills and helper CLIs.

## Layout

- `skills/<name>/` — Claude Code / Codex / Pi skills. `SKILL.md` per skill.
- `bin/<tool>` — portable helper executables. Symlinked into `~/.local/bin/` by
  chezmoi's `run_once_after_link-toolbox-bins.sh` on every machine.
- `AGENTS.md` — universal personal instructions. Exposed to agents through
  `~/.agents` and per-agent symlinks.
- `skills.toml` — external skill sources copied into the canonical tree.
- `bin/skillctl` — adds, refreshes, lists, and validates external snapshots.
- `docs/` — notes and changelog for maintenance decisions.

## How it reaches machines

`/projects/toolbox` is the canonical clone. The
[`devdocker/dotfiles`](https://github.com/ankitson/devdocker) repo bootstraps that
clone if missing and wires local paths:

- `~/toolbox` → `/projects/toolbox`
- `~/.agents` → `/projects/toolbox`
- `~/.{claude,codex,opencode}/skills` and `~/.pi/agent/skills` → `~/toolbox/skills`
- `~/.local/bin/<tool>` → `~/toolbox/bin/<tool>` for executable files in `bin/`

Agent containers that need this repo bind-mount `/projects/toolbox` directly at
`/home/ankit/toolbox` and `/home/ankit/.agents`, so they do not depend on baked
image symlinks.

## Adding a new bin

1. Drop the executable in `bin/`, `chmod +x`, commit, push.
2. `chezmoi apply` on each target machine (or wait for the next periodic apply).
3. The tool is now on PATH everywhere.

If the tool is env-tied (only makes sense on the homeserver, only in the devbox
container, etc.), it doesn't belong here — put it in the env's own repo.

## Managing skills

Distribution is a separate concern: `devdocker/dotfiles` chezmoi wiring exposes
this canonical `skills/` tree to every agent runtime. `skillctl` only refreshes
external snapshots.

[`skills.toml`](skills.toml) lists external sources. Any directory under
`skills/` that is not listed there is custom and edited directly in this repo.

Common operations:

```sh
just skills-list
just skills-check
just skills-test
just skills-sync                         # refresh every external skill
just skills-sync qmd                     # refresh selected skills
just skills-add vercel-labs/agent-browser
just skills-add qmd tobi/qmd skills/qmd  # explicit name/repo/path fallback
```

For selected-file imports or pinned refs, call `bin/skillctl` directly:

```sh
bin/skillctl add rdt-cli public-clis/rdt-cli --file SKILL.md --file SCHEMA.md
bin/skillctl add example owner/repo path/to/skill --ref v1.0.0
```

Summarize URLs, files, media, or stdin through the steipete CLI without
installing its daemon/browser extension:

```sh
just summarize "https://example.com" --plain
bin/summarize "/path/to/file.pdf" --length long --plain
```

When no path is provided, `skillctl` looks for the same common layouts used by
skill package repos: repo root `SKILL.md`, `skills/<name>/SKILL.md`,
`<name>/SKILL.md`, or the only skill folder in the repo. If a repo has multiple
skills and none matches the name, pass the path explicitly.

Commit `skills.toml` and refreshed skill contents. Chezmoi remains the only
distribution mechanism. Skills that wrap a CLI still need that CLI installed
separately; for example, `rdt-cli` requires `uv tool install rdt-cli`.

`skills/.system/` is not managed by `skillctl`: Codex owns and updates that
hidden subtree.

## Not part of toolbox

- Env-tied bins → live in env repos (`hroot/homeserver/bin/`, etc.).
- Agent runtime memory & knowledge → lives in the `cybernetics` Obsidian vault.
- Container/image config → `devdocker`, `devserver`.

## History

Previously named `clankerpedia`. Renamed to `toolbox` to reflect broader scope (skills +
bins, not just skills).
