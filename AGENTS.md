<!-- Composed by `just agents` (bin/frag) from context/templates/AGENTS.md.j2.
     Edit this template or context/fragments/*.md — do NOT edit AGENTS.md directly. -->
# Security: Secrets & Credentials
- NEVER output passwords, API keys, tokens, secrets, or credentials of any kind in messages, tool calls, tool results, thinking traces, or any other output. This includes in log output, error messages, debug info, or any content that could be visible to users or persisted.
- When displaying or returning results that contain secrets, redact them (e.g., `sk-****...****`).
- If you need to reference a secret, say "the API token" or "the credential" — never the actual value.
- When checking environment variables or config files for debugging, mask or truncate any secret values before displaying them.

# Documentation and work-logging
- See the document-work skill

# Scripting
- Prefer python or typescript/javascript over bash. Avoid bash unless absolutely necessary or its a very simple script
- When appropriate, create a Justfile with commonly used commands and keep it up to date.

# Tasks
- Use subagents to break down difficult tasks

# Programming Language Guidance

## Python
- Prefer `uv` over other tools
- Prefer PEP 723 inline metadata for dependencies in small scripts, and use a `pyproject.toml` file for more complex projects

## Javascript
- Prefer `bun` and typescript over other tools

<!-- BEGIN generated: env (per-host ~/AGENTS.env.md) -->
# Environment: homeserver host

You are running on Ankit's homeserver (the host, not a container). Docker, the host
filesystem, and `/projects` are directly available. Containers run under `docker
compose` from `/home/ankit/hroot/{devserver,homeserver}/docker-compose*.yml`.

Path index - look here first:
user root: /home/ankit/hroot
homeserver: /home/ankit/hroot/homeserver
devserver: /home/ankit/hroot/devserver
projects: /home/ankit/hroot/projects (or /projects - symlink)

<!-- END generated: env -->

<!-- BEGIN generated: index (~/hroot/allplace/wiki/INDEX.md) -->
# INDEX

## Network
All devices on Tailscale, addressed via short names.

## Devices
- `desktop-linux` — homeserver + dev box; RTX 2070 SUPER (8 GB VRAM) — runs the audio models (speaches, audiocpp)
- `desktop-win` — Windows PC + ML model server; RTX 5080 (16 GB VRAM) — runs the LLMs (Unsloth/llama-server)
- `m2book` — personal MacBook (client)

## Hostnames
Domains point to Tailscale IPs, caddy reverse proxies
- `*.home.ankitson.com`, `*.dev.ankitson.com` → desktop-linux
- `*.win.ankitson.com` → desktop-win

## Services
See Caddyfiles and Docker compose files for active services.
- desktop-linux: `~/hroot/homeserver/`, `~/hroot/devserver/`
- desktop-win: Caddyfile in `~/Documents/docs-root/projects/code/win-models/`

## Paths

### desktop-linux
- `~/hroot` — real home directory
- `~/hroot/homeserver`, `~/hroot/devserver` — Docker services
- `/projects/devdocker/dotfiles` — chezmoi dotfiles (shared across all machines)
- `~/hroot/allplace` — personal Obsidian vault (PARA); the only place notes are written
- `~/hroot/allplace/wiki` — cross-project engineering knowledge base (process, learning, evals, this index)
- `~/hroot/cybernetics` — OpenClaw agent operating memory (SOUL/MEMORY/daily logs; agents manage it)
- `/projects` → `~/hroot/projects` — active dev projects

### desktop-win
- `~/Documents/docs-root/projects/code/` — active dev projects
- `~/Documents/docs-root/projects/code/win-models/` — ML models, Caddy server

### m2book
- `~/Documents/docs-root/projects/code/` — active dev projects (shared Synology drive w/ desktop-win)
<!-- END generated: index -->

# Knowledge & Task Routing
Where written things go:
1. About one repo's code → that repo's `docs/` (dies with the repo)
2. Everything else worth writing down → the `allplace` Obsidian vault: `~/hroot/allplace/wiki/` for durable engineering knowledge (process, learnings, evals, machine index), elsewhere in the vault only for personal/narrative notes. Agents write only under `wiki/` and `agents/` there.
3. To-dos → beads (`bd`) where a project has it — never markdown TODO checklists
4. Agent runtime memory (OpenClaw) → `~/hroot/cybernetics`; agents manage it, humans don't write there

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:970c3bf2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->
## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the `beads` skill at `.agents/skills/beads/SKILL.md` (project install) or `~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking; do not create markdown TODO lists.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory files.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.
<!-- END BEADS CODEX SETUP -->
