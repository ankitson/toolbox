---
name: 1password-cli
description: Use this skill when working with the 1Password CLI (`op` command) for secrets management, retrieving API keys, injecting secrets into development environments, or any task involving 1Password vault operations. Triggers on "1password", "op command", "secrets management", "api keys from vault", "op run", "op read", "service account token".
---

# 1Password CLI Skill

Use this skill when working with the 1Password CLI (`op` command) for secrets management, retrieving API keys, or injecting secrets into development environments.

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
