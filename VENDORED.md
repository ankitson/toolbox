# Vendored skills — provenance

Third-party skills copied into `skills/`. We vendor the files (commit them) rather
than depend on an installer, so every machine gets them from this repo via git +
the chezmoi symlinks. This table is the only record of where each came from, for
when you want to re-pull upstream.

To update one: re-fetch from the source, copy the files back over `skills/<name>/`,
diff, commit. `just vendor <owner/repo> <subpath> <name>` automates the common case
(a skill that lives in a repo subdirectory).

| Skill | Source repo | Path in repo | Vendored |
|---|---|---|---|
| `grill-me` | github.com/mattpocock/skills | `skills/productivity/grill-me/` | 2026-05-24 |
| `grill-with-docs` | github.com/mattpocock/skills | `skills/engineering/grill-with-docs/` | 2026-05-24 |
| `triage` | github.com/mattpocock/skills | `skills/engineering/triage/` | 2026-05-24 |
| `zoom-out` | github.com/mattpocock/skills | `skills/engineering/zoom-out/` | 2026-05-24 |
| `claude-api` | github.com/anthropics/skills | `claude-api/` | 2026-05-24 |
| `skill-creator` | github.com/anthropics/skills | `skill-creator/` | 2026-05-24 |
| `qmd` | github.com/tobi/qmd | (repo root) | 2026-05-24 |
| `rdt-cli` | github.com/public-clis/rdt-cli | `SKILL.md` + `SCHEMA.md` (root) | 2026-05-29 |

Everything else in `skills/` is authored here (no upstream source).

## Tool dependencies

Some skills wrap a CLI that must be installed separately:

- `rdt-cli` → `uv tool install rdt-cli` (the `rdt` command). Install on any machine
  / container where the skill is used.
