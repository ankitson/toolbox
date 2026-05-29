---
name: postgres-cli
description: Query Ankit's home Postgres database from any agent environment using psql + the 1Password service account. Use when you need to inspect garmin data, pipeline orchestrator state, or any other Postgres-backed dataset on the home network.
---

# Postgres CLI Skill

The home Postgres instance lives on the homeserver (`postgres.home.ankitson.com:5432`) and is reachable from any container/host on the LAN or Tailscale. `psql` ships in the devbox image; `op` is available in every agent context. No env vars to set up — the password is fetched on demand via the 1Password service account.

## Connection details

| Field | Value |
|---|---|
| Host | `postgres.home.ankitson.com` |
| Port | `5432` |
| User | `postgres` |
| Password | `op read 'op://clankers/local-service/password'` |
| Server version | 17.5 |

Prerequisite: `OP_SERVICE_ACCOUNT_TOKEN` in env. Already true in `agent-devbox`/`openclaw` containers; on host shells see [`1password-cli`](../1password-cli/SKILL.md).

## Connect

```bash
PGPASSWORD=$(op read 'op://clankers/local-service/password') \
  psql -h postgres.home.ankitson.com -U postgres -d <db>
```

For one-off queries:
```bash
PGPASSWORD=$(op read 'op://clankers/local-service/password') \
  psql -h postgres.home.ankitson.com -U postgres -d <db> -At -c "SELECT ..."
```

For an interactive session, export `PGPASSWORD` once at the shell:
```bash
export PGPASSWORD=$(op read 'op://clankers/local-service/password')
psql -h postgres.home.ankitson.com -U postgres -d <db>
```
**Don't echo `$PGPASSWORD`** in logs/output — redact when reporting.

## Databases

| Database | What's in it |
|---|---|
| `garmin` | Garmin Connect ingest — sleep, heart rate, HRV, stress, body battery, steps, activities, derived rollups. See [pipelines/docs/NOTES.md](../../../home/ankit/hroot/devserver/pipelines/docs/NOTES.md) for the schema. |
| `pipeline_dagster` | Dagster orchestrator state (asset materializations, runs, logs). |
| `pipeline_dbos` | DBOS workflow runtime — user app tables. |
| `pipeline_dbos_dbos_sys` | DBOS system schema (do not touch from queries). |
| `pipeline_restate` | Restate workflow engine state. |
| `postgres` | Default admin DB. Use for `SELECT datname FROM pg_database` and other instance-level queries. |

## Common queries

```sql
-- list user tables
SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') ORDER BY schemaname, tablename;

-- describe a table (avoid \d in psql 16 client vs server 17 — use this instead)
SELECT column_name, data_type, is_nullable
  FROM information_schema.columns
  WHERE table_schema='public' AND table_name='<table>'
  ORDER BY ordinal_position;

-- row counts per table in current DB
SELECT relname, n_live_tup AS rows
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC LIMIT 20;
```

## Version mismatch gotcha

Client is `psql 16.14`, server is `17.5`. **`\l`, `\d+`, and some other introspection meta-commands fail** with `column d.daticulocale does not exist` because the client emits SQL for postgres 16 catalogs. Workarounds:

- Use plain SQL (the `SELECT` queries above) instead of `\` meta-commands.
- `\dt`, `\dn`, `\du` mostly still work.
- A full fix would be a psql 17 client; not worth it for now.

## Pointers

- Homeserver service inventory: [`/home/ankit/hroot/homeserver/README.md`](../../../home/ankit/hroot/homeserver/README.md)
- Pipeline schemas + ingest details: [`/home/ankit/hroot/devserver/pipelines/docs/NOTES.md`](../../../home/ankit/hroot/devserver/pipelines/docs/NOTES.md)
- Service account pattern: [`1password-cli`](../1password-cli/SKILL.md)
