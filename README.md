# toolbox

Universal portable tooling that follows me everywhere — skills and helper CLIs.

## Layout

- `skills/<name>/` — Claude Code / Codex / Pi skills. `SKILL.md` per skill.
- `bin/<tool>` — portable helper executables. Symlinked into `~/.local/bin/` by
  chezmoi's `run_once_after_link-toolbox-bins.sh` on every machine.
- `AGENTS.md` — universal personal instructions. Exposed to agents through
  `~/.agents` and per-agent symlinks.
- `.skill-lock.json` — provenance for third-party skills installed with the
  `skills` npm package.
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

## Adding a new skill

Skills are plain files. Every agent already sees `skills/` through chezmoi
symlinks, so **committing the files is the only distribution step** — there is no
per-agent installer to run. (We deliberately don't use `npx skills` / similar
multi-agent installers: they fan out copies into each agent's skill dir, which
here are all symlinks to this one directory — they'd fight the symlinks for no
benefit.)

**Authored skill:**

1. Create `skills/<name>/SKILL.md` (`skill-creator` can scaffold one).
2. Commit and push.

**Third-party (vendored) skill:**

1. `just vendor <owner>/<repo> <subpath> <name>` — fetches the skill's directory
   from the repo into `skills/<name>/`. (For a "tool skill" where the repo is a
   CLI and you only want `SKILL.md`, copy the file(s) by hand instead.)
2. Add a row to [`VENDORED.md`](VENDORED.md) recording the source.
3. Commit and push.

Other machines get it on their next `git pull` of this repo (+ a tool install if
the skill wraps a CLI — see VENDORED.md). Nothing runs an installer except your
authoring machine, and even there only `git`.

## Not part of toolbox

- Env-tied bins → live in env repos (`hroot/homeserver/bin/`, etc.).
- Agent runtime memory & knowledge → lives in the `cybernetics` Obsidian vault.
- Container/image config → `devdocker`, `devserver`.

## History

Previously named `clankerpedia`. Renamed to `toolbox` to reflect broader scope (skills +
bins, not just skills).
