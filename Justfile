# Toolbox helpers.
#
# Skills are plain files under skills/<name>/. Every agent sees them through
# chezmoi symlinks (~/.{claude,codex,opencode}/skills + ~/.pi/agent/skills +
# ~/.agents all point at skills/ here). So there's no per-agent install step —
# committing the files IS the distribution. Third-party skills are vendored;
# their sources are recorded in VENDORED.md.

# Vendor a third-party skill from a GitHub repo subdirectory into skills/<name>.
# For "tool skills" where the repo is a CLI and you only want SKILL.md (e.g.
# rdt-cli), copy the files by hand instead. Record the source in VENDORED.md after.
vendor repo subpath name:
  #!/usr/bin/env bash
  set -euo pipefail
  tmp=$(mktemp -d)
  git clone --depth 1 "https://github.com/{{repo}}.git" "$tmp"
  rm -rf "skills/{{name}}"
  cp -r "$tmp/{{subpath}}" "skills/{{name}}"
  rm -rf "$tmp" "skills/{{name}}/.git"
  echo "Vendored {{repo}}/{{subpath}} -> skills/{{name}}."
  echo "Now: add a row to VENDORED.md, review, commit."

# List skills (directory names — every one is live via the symlinks).
list:
  @ls -1 skills/
