---
name: 1password-cli
description: Use this skill when working with the 1Password CLI (`op` command) for secrets management, retrieving API keys, injecting secrets into development environments, or any task involving 1Password vault operations. Triggers on "1password", "op command", "secrets management", "api keys from vault", "op run", "op read", "service account token".
---

# 1Password CLI Skill

Use this skill when working with the 1Password CLI (`op` command) for secrets management, retrieving API keys, or injecting secrets into development environments.

## Non-interactive use (service account)

`op read 'op://vault/item/field'` works without an interactive signin as long as `OP_SERVICE_ACCOUNT_TOKEN` is exported.

- **Containers (`agent-devbox`, `openclaw`):** token is injected via docker-compose `env_file` (`secrets/{agent-devbox,openclaw}.env`, rendered by `just rs`). `op read` just works.
- **Host shell:** dotfiles' `.bashrc` sources `~/.config/op/service-account.env` if present (chmod 600, hand-managed per machine). To enable: `mkdir -p ~/.config/op && chmod 700 ~/.config/op` then create the file with `export OP_SERVICE_ACCOUNT_TOKEN=ops_…` and `chmod 600`.

Skills that need a secret should prefer `op read` over passing keys via plaintext env files or hardcoding.

## Secret Reference Syntax

Secret references use the URI format: `op://vault/item/[section/]field`

```
op://vault-name/item-name/field-name           # Simple field
op://vault-name/item-name/section/field-name   # Field in a section
op://Private/GitHub/password                   # Example: GitHub password
op://dev/Stripe/publishable-key                # Example: Stripe key
```

## References
- `references/cli.md` (CLI usage)

## Guardrails
- Never paste secrets into logs, chat, or code.
- Prefer op run / op inject over writing secrets to disk.
- If sign-in without app integration is needed, use op account add.

## Troubleshooting
- If a command returns "not signed in", re-run `eval $(op signin)`
- If an item is not found, list vaults `op vault list` and search `op item list --vault "vault-name" | grep "item-name"`
