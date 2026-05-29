# toolbox

Universal portable tooling that follows me everywhere — skills and helper CLIs.

## Layout

- `skills/<name>/` — Claude Code / Codex / Pi skills. `SKILL.md` per skill.
- `bin/<tool>` — portable helper executables. Symlinked into `~/.local/bin/` by
  chezmoi's `run_once_after_link-toolbox-bins.sh` on every machine.
- `AGENTS.md` — universal personal instructions. Cloned to `~/.agents/AGENTS.md` and
  symlinked into `~/.claude/`, `~/.codex/`, `~/.pi/agent/`.
- `agent-scripts/`, `sync-skills.py`, `skills.yaml` — pipeline that pulls in
  third-party skills from other GitHub repos.

## How it reaches machines

A single `.chezmoiexternal.toml` entry in
[`devdocker/dotfiles`](https://github.com/ankitson/devdocker) clones this repo into
`~/.agents/`. `chezmoi apply`:

- Symlinks `~/.claude/AGENTS.md`, `~/.codex/AGENTS.md`, `~/.pi/agent/AGENTS.md` →
  `~/.agents/AGENTS.md` (universal instructions).
- Symlinks `~/.local/bin/<tool>` → `~/.agents/bin/<tool>` for every executable in
  `bin/`.

## Adding a new bin

1. Drop the executable in `bin/`, `chmod +x`, commit, push.
2. `chezmoi apply` on each target machine (or wait for the next periodic apply).
3. The tool is now on PATH everywhere.

If the tool is env-tied (only makes sense on the homeserver, only in the devbox
container, etc.), it doesn't belong here — put it in the env's own repo.

## Adding a new skill

1. For a skill you author: drop it under `skills/<name>/SKILL.md`, commit, push.
2. For a third-party skill: add it to `skills.yaml`, run `just sync-skills`.

## Not part of toolbox

- Env-tied bins → live in env repos (`hroot/homeserver/bin/`, etc.).
- Agent runtime memory & knowledge → lives in the `cybernetics` Obsidian vault.
- Container/image config → `devdocker`, `devserver`.

## History

Previously named `clankerpedia`. Renamed to `toolbox` to reflect broader scope (skills +
bins, not just skills).
