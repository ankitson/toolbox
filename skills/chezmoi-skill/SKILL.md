---
name: chezmoi
description: Manage dotfiles with chezmoi safely. Use when working with dotfiles, chezmoi templates, machine-specific configuration, syncing configs across machines, rc files, home-directory configuration, or when the user mentions chezmoi, dotfiles, or configuration management. Prioritize previews and explicit user consent before applying changes because chezmoi can overwrite local files.
allowed-tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - Bash(chezmoi add *)
  - Bash(chezmoi cat *)
  - Bash(chezmoi data *)
  - Bash(chezmoi diff *)
  - Bash(chezmoi execute-template *)
  - Bash(chezmoi managed *)
  - Bash(chezmoi source-path *)
  - Bash(chezmoi status *)
  - Bash(chezmoi unmanaged *)
  - Bash(chezmoi apply --dry-run *)
  - Bash(chezmoi apply --no-tty *)
---

# Chezmoi Dotfiles Management

## Action Guidance

When the user asks about dotfiles or chezmoi operations, implement source-state changes directly when the request is clear. For example, if the user says "make this work on macOS only" or "add my bashrc to chezmoi", update the chezmoi source state instead of only suggesting commands.

Treat applying to the destination directory as a separate, higher-risk step. `chezmoi apply` can overwrite local files, remove files, run scripts, or refresh externals. Do not apply changes to live dotfiles unless the user has approved the exact destination changes in the current conversation.

Always preview significant changes with `chezmoi diff --no-pager`, `chezmoi cat <file>`, `chezmoi status`, or `chezmoi apply --dry-run --verbose` before asking for approval to apply.

## Apply Safety Rules

Use these rules whenever an operation might change files outside the chezmoi source directory:

1. Preview first. Show or summarize the affected paths and whether they will be created, modified, deleted, or run as scripts.
2. Ask for explicit consent before applying. General task intent such as "fix my dotfiles" is not approval to overwrite the user's current files.
3. Apply narrowly. Prefer `chezmoi apply --no-tty <target...>` for the specific target paths the user approved. Avoid all-target `chezmoi apply` unless the user explicitly approved all pending changes.
4. Do not use `--force` by default. `--force` skips chezmoi's overwrite prompts, so it can discard local edits without warning.
5. If `chezmoi apply --no-tty <target...>` fails because chezmoi needs an interactive decision, stop and report the conflict. Do not retry with `--force` automatically.
6. Use `--force` only after the user explicitly approves forcing the exact target paths and understands that local destination changes may be overwritten. If the environment or tool permissions do not allow that command, provide the exact command for the user to run instead.
7. Do not run `chezmoi apply` just to validate a source edit. Use dry runs, diffs, rendered output, and template checks for validation.

## Commands

```bash
chezmoi add <file>                       # Add a destination file to chezmoi source state
chezmoi add --template <file>            # Add a destination file as a template
chezmoi status [target...]               # Show pending changes and local destination edits
chezmoi diff --no-pager [target...]      # Read-only preview of destination changes
chezmoi apply --dry-run --verbose [target...]  # Read-only apply preview
chezmoi cat <file>                       # Preview rendered template output
chezmoi data                             # Show available template variables
chezmoi source-path <file>               # Show source path for a target
chezmoi source-path                      # Show the source directory
chezmoi execute-template '{{ .chezmoi.os }}'  # Test template snippets

# After explicit user approval for the listed targets:
chezmoi apply --no-tty <target...>
```

Do not put `--force` in routine command snippets. If force is truly needed after explicit approval, keep it targeted: `chezmoi apply --force <target...>`.

## File Naming

| Prefix/Suffix | Effect |
|---------------|--------|
| `dot_` | Installed as `.` (`dot_gitconfig` → `~/.gitconfig`) |
| `private_` | Restrictive permissions (600) |
| `executable_` | Executable permissions (755) |
| `.tmpl` | Processed as Go template |
| `symlink_` | Creates symlink |

## Machine-Specific Templates

Convert a static file to a template by renaming with `.tmpl` suffix, then use conditionals:

### By OS
```
{{- if eq .chezmoi.os "darwin" }}
# macOS config
{{- end }}

{{- if eq .chezmoi.os "linux" }}
# Linux config
{{- end }}
```

### By hostname
```
{{- if hasPrefix .chezmoi.hostname "work-" }}
# work machine config
{{- end }}
```

### By environment variable
```
{{- if env "WORK_ENV" }}
# when WORK_ENV is set
{{- end }}
```

### Combined conditions
```
{{- if or (eq .chezmoi.os "darwin") (env "WORK_ENV") }}
# macOS or when WORK_ENV is set
{{- end }}
```

## Escaping Nested Templates

When the target file itself uses `{{ }}` syntax (like mise, Jinja2, or Tera templates), escape the braces so chezmoi doesn't process them as Go template syntax:

```
SOME_VAR = "{{ "{{" }}env.OTHER_VAR{{ "}}" }}"
```

This renders as `SOME_VAR = "{{env.OTHER_VAR}}"` in the output. The `{{ "{{" }}` and `{{ "}}" }}` are Go template expressions that output literal brace characters.

## Removing Files

Use `.chezmoiremove` to clean up dotfiles that chezmoi should remove from your system:

```bash
chezmoi source-path
# Edit <source-dir>/.chezmoiremove with file-editing tools.
chezmoi diff --no-pager
```

After previewing removals, ask the user to approve the exact deletion list before applying. Prefer a targeted `chezmoi apply --no-tty <target...>` when possible. If removals require an all-target apply, state that clearly and wait for explicit approval.

### Template-based removal (`.chezmoiremove.tmpl`)

Conditionally remove files based on system variables:

```
{{- if eq .chezmoi.os "darwin" }}
~/.linux-only-config
{{- end }}

{{- if not (env "WORK_ENV") }}
~/.work-config
{{- end }}
```

The file is always processed as a template, even without the `.tmpl` extension.

## External Dependencies

Manage external git repos in `.chezmoiexternal.toml`:

```toml
[".zsh/plugins/some-plugin"]
    type = "git-repo"
    url = "https://github.com/user/some-plugin.git"
    refreshPeriod = "168h"
```

Do not force-refresh externals as part of routine applies. `--refresh-externals=always` can perform network updates and change cached external content. Use it only when the user specifically asks to refresh externals, and preview or explain the expected effect first.

## Workflow: Converting Static File to Template

When converting a static config to machine-specific template:

1. Read the current file to understand its contents
2. Identify machine-specific values (paths, hostnames, environment-specific settings)
3. Run `chezmoi add --template <file>` to add as template
4. Use `chezmoi source-path <file>` to locate the template source, then edit it with file-editing tools to add conditionals (see "Machine-Specific Templates")
5. Preview with `chezmoi cat <file>` to verify rendering on this machine
6. Preview destination changes with `chezmoi diff --no-pager <file>` or `chezmoi apply --dry-run --verbose <file>`
7. Ask for explicit user approval before applying to the destination
8. If approved, apply narrowly with `chezmoi apply --no-tty <file>`

## Gotchas

1. **Removing managed files**: Use `.chezmoiremove` to clean up files (see "Removing Files" section)
2. **Preview templates and destination changes**: Run `chezmoi cat <file>` for rendered templates and `chezmoi diff --no-pager <file>` for destination changes
3. **Interactive prompts**: In agent environments, interactive prompts can block. Use `chezmoi apply --no-tty <target...>` only after approval. If it cannot proceed non-interactively, stop and ask the user rather than forcing.
4. **Local destination edits**: Chezmoi prompts when a target has changed since chezmoi last wrote it. That prompt protects user edits; do not bypass it without explicit approval.
5. **Interactive editors**: `chezmoi edit` can open an editor. In agent environments, prefer `chezmoi source-path <target>` and normal file-editing tools.
6. **Template errors**: Use `chezmoi execute-template '{{ .chezmoi.os }}'` to test template snippets

## Troubleshooting

**Template syntax errors**: Test small snippets with `chezmoi execute-template '{{ .chezmoi.os }}'`

**File not applying**: Check `chezmoi status <file>` and `chezmoi diff --no-pager <file>` to see what changes are pending. If apply needs a prompt, report the conflict instead of forcing.

**External not refreshing**: The refresh period might not have elapsed. Ask before using `--refresh-externals=always`, because it can perform network updates and change external content.

**Permission errors**: Verify file has correct prefix (`private_` for 600, `executable_` for 755)
