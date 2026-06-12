---
name: commit-sweep
description: "Commit uncommitted work spanning multiple repos: discover changed repos, group by feature, preview msg+diff and gate each commit. Trigger: commit/organize/clean up/sweep changes across >1 repo, per-feature commits, review diffs before committing, commit after a multi-repo session. Not for a single trivial commit with message already given."
---

# commit-sweep

Multi-repo commit organizer. Uncommitted work across repos -> grouped feature commits, each gated by msg+diff preview.

Why: cross-repo work interleaves. Good history groups by intent (shared tool + its adopters = one story, N commits). Recover that; nothing commits unseen.


# Guardrails

- No push. ever. user's call.
- No discard: no `checkout --` / `restore` / `clean` / `stash drop`. only add + commit.
- Respect `.gitignore`. never `-f` ignored paths.
- Secrets never staged w/o explicit ok: `*.env` `*.pem` `id_*` `*token*` `*secret*` `*.key` `service-account*`.
- Ambiguous -> ask. wrong commit x N repos = N x cleanup.

## Flow

1. Discover: `scripts/find-changed-repos.py [ROOT] [--exclude SUBSTR ...]`. JSON per changed repo: path, branch, counts, in_progress. ROOT default `~/hroot`. clean repos omitted.
2. Scope (critical): root may hold dozens — vendored/forks/archives/scratch. user rarely means all. show compact list; propose default excludes (`external-repo/`, `vendor/`, `archive/`, non-user origin, single-junk-file repos); `--exclude` to trim; lean to repos user actually worked in. get yes before staging.
3. Read diffs: `git -C R diff` / `--staged` / `status --porcelain`. grasp the story, not filenames. skim untracked.
4. Group: feature = one intent (what it accomplishes). cross-repo same intent = 1 feature -> 1 commit/repo, parallel msgs, kept adjacent. unrelated changes same repo = separate commits. don't collapse two stories into "it's all in R/".
5. Order: foundational/shared first, docs/cleanup last, cross-repo sets together. show numbered list as orientation (not a gate).
6. Gate each commit, before staging: show repo+branch (flag `main`), proposed msg, diff for exactly its paths (`git -C R diff -- PATHS`; untracked shown as new). big/generated diff -> `--stat` + excerpt, offer full. then wait: `approve` / `edit msg` / `split` / `skip` / `stop`. stage only at approve -> skip/stop leaves tree as found. date commit to mtime when clear (see Commit date). derive PATHS from `git status --porcelain`, not memory; after commit confirm no feature files left dangling (a left-behind file = likely a missed path).
7. Wrap: recap per repo (commit subjects) + what left uncommitted (skipped/junk/flagged secrets). remind: nothing pushed; review via `git -C R log`/`show`.

## Entangled file (common, dangerous)

your change + user's unrelated in-flight work in one file. whole-file commit buries their unfinished work under your msg. don't.

Split hunks (no interactive `add -p` here; patch + `apply --cached` does it):

- `scripts/stage-hunks.py R FILE --list`   # numbered hunks
- `scripts/stage-hunks.py R FILE 1 3`      # stage only those
- `git -C R commit -m "..."`               # NO pathspec -> only staged hunks land

Cautions: nothing pre-staged first (`git diff --cached`); too interleaved -> split into finer hunks.

Two of *your own* features tangled in the same hunks: just pick the better-fitting commit. split = your-work-vs-other-work, not hairsplitting your own.

## Commit date

Match commit date to the change's mtime when clear — so history reflects when work happened, not when swept.

- `D=$(scripts/clear-mtime.py R PATHS...)` -> if set: `GIT_AUTHOR_DATE=@$D GIT_COMMITTER_DATE=@$D git -C R commit -m "..."`. unset (exit 1): commit normally (now).
- clear = staged paths' mtimes within one window (default 6h); helper returns the newest. scattered (old file + fresh file) -> not clear -> now.
- hunk-split commit: pass the file; its mtime = latest edit, fine.
- never fabricate: only mtime-date when clear; otherwise now.

## Message: Conventional Commits

- `type(scope): summary` — imperative, lowercase, ≤~72, no period.
- types: `feat fix docs refactor chore test build ci perf style`. scope optional.
- body (blank line, wrapped) only when *why* isn't obvious: problem / tradeoff / gotcha. no padding.
- cross-repo feature -> parallel msgs.

Ex (1 feature, 3 repos): toolbox `feat(bin): add render-secrets for op-templated secrets`; devserver + homeserver `refactor(justfile): render secrets via shared render-secrets`.

Ex (split unrelated in 1 repo): `feat(systemd): run opencode + codex as user services` + `docs(readme): fix broken install link`.

## Edge cases

- detached HEAD (`branch:"HEAD"`): flag, confirm before commit.
- merge/rebase/cherry-pick in progress (`in_progress` set): don't stack; user resolves first.
- pre-staged changes: fold into relevant preview, not blind commit.
- submodules: scanner stops at outer repo; don't commit inside unless asked. submodule pointer bump = ALWAYS its own commit, never mixed with other changes (`chore: bump <name> submodule`).
- empty scope after filter: say so, stop. don't widen alone.
