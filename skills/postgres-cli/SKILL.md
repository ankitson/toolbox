---
name: postgres-cli
description: "Home Postgres: psql queries, garmin, pipeline state, schema, op."
---

# Postgres CLI

Query home Postgres via psql + op. No env setup; password on demand.

## Connect

```bash
PGPASSWORD=$(op read 'op://clankers/local-service/password') \
  psql -h postgres.home.ankitson.com -U postgres -d <db>
```

One-shot SQL:

```bash
PGPASSWORD=$(op read 'op://clankers/local-service/password') \
  psql -h postgres.home.ankitson.com -U postgres -d <db> -At -c "<sql>"
```

Prereq: `OP_SERVICE_ACCOUNT_TOKEN` in env. Auto on agent-devbox + openclaw; host: see [`1password-cli`](../1password-cli/SKILL.md). Never echo `$PGPASSWORD`.

## DBs

- `garmin` — sleep, HR, HRV, stress, body battery, steps, activities. [pipelines/docs/NOTES.md](../../../home/ankit/hroot/devserver/pipelines/docs/NOTES.md).
- `pipeline_dagster` — Dagster orchestrator state.
- `pipeline_dbos` — DBOS user app tables.
- `pipeline_dbos_dbos_sys` — DBOS system; do not touch.
- `pipeline_restate` — Restate engine state.
- `postgres` — admin; instance-level queries.

## Queries

```sql
-- user tables
SELECT schemaname, tablename FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog','information_schema')
  ORDER BY schemaname, tablename;

-- describe table
SELECT column_name, data_type, is_nullable
  FROM information_schema.columns
  WHERE table_schema='public' AND table_name='<table>'
  ORDER BY ordinal_position;

-- row counts top 20
SELECT relname, n_live_tup AS rows
  FROM pg_stat_user_tables
  ORDER BY n_live_tup DESC LIMIT 20;
```

## Version mismatch

Client 16.14, server 17.5. `\l`, `\d+`, some `\d*` meta-commands fail (`column d.daticulocale does not exist`). Use plain SQL above. `\dt`, `\dn`, `\du` work.

## Pointers

- Services inventory: [`homeserver/README.md`](../../../home/ankit/hroot/homeserver/README.md)
- Pipeline schemas: [`pipelines/docs/NOTES.md`](../../../home/ankit/hroot/devserver/pipelines/docs/NOTES.md)
- OP service account: [`1password-cli`](../1password-cli/SKILL.md)
