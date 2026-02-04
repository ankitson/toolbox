---
name: document-work
description: Set up and maintain project documentation following standard conventions. Use at the start of any non-trivial task, when making code changes, or when the user asks to document work.
---

# Document Work

Follow these conventions whenever doing non-trivial work in a project.

## Required Structure

Create if missing: `docs/NOTES.md`, `docs/CHANGELOG.md`, `logs/`, and a `Justfile` when there are repeatable commands.

## docs/NOTES.md

Append-only running log. Add dated entries (`## YYYY-MM-DD — Title`) with goals, key decisions, discoveries, and next steps as you work. Never edit previous entries.

## docs/CHANGELOG.md

Append-only log of code changes. Group by date (`## YYYY-MM-DD`), then by logical change (`### Change Group`). Record what was added/removed/modified and why.

## Scoped Task Documentation

For narrowly scoped tasks (migrations, investigations, one-off projects), create a dedicated `docs/YYYY-MM-DD-task-name/` folder with its own README.md, plans, and artifacts. Keep the top-level NOTES.md and CHANGELOG.md for repo-wide concerns.

## Git Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`). Commit at each logical step, not one giant commit at the end.

## logs/

Store script and service output here. Prefer JSONL structured logging. Use descriptive filenames.
