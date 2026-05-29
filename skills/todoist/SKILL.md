---
name: todoist
description: "Todoist tasks: read, add, complete, reschedule; preserve recurring rules; REST + Sync via op."
---

# Todoist

Todoist via `curl` + unified `/api/v1/` (REST + Sync). Token via `op`. **Hard rule on recurring tasks below — read before any update.**

## Auth

```bash
TODOIST_API_TOKEN=$(op read 'op://clankers/todoist/password')
H="Authorization: Bearer $TODOIST_API_TOKEN"
```

Prereq: `OP_SERVICE_ACCOUNT_TOKEN` in env (auto on agent-devbox + openclaw; host: see [`1password-cli`](../1password-cli/SKILL.md)). Never echo `$TODOIST_API_TOKEN`.

## ⚠️ Hard rule — recurring tasks

**NEVER PATCH `due_string` on a task where `due.is_recurring == true`.** The `POST /api/v1/tasks/{id}` endpoint re-parses natural language and replaces the entire `due` block — destroys rules like "every other Tuesday and Friday". Confirmed bug pattern in Doist/todoist-ai #279.

Before any update on a recurring task, first GET it and route by intent:

```bash
# check recurring first
curl -s -H "$H" "https://api.todoist.com/api/v1/tasks/$ID" | jq '{string:.due.string, is_recurring:.due.is_recurring, date:.due.date}'
```

Intent routing:

| Intent | Endpoint | Notes |
|---|---|---|
| "I did this one; advance to next" | `POST /api/v1/tasks/{id}/close` | Canonical. Advances due, preserves rule. No body. |
| "Move this one instance only; don't change rule" | `POST /api/v1/sync` with `item_update` (preserve fields) | See [Reschedule one instance](#reschedule-one-instance) below. |
| "Permanently stop recurrence" | `POST /api/v1/tasks/{id}/complete` | Explicit. Ask user to confirm before calling. |
| "Change the rule (e.g. weekly → daily)" | `POST /api/v1/tasks/{id}` with `due_string` | OK on non-recurring or when intentionally rewriting the rule. Confirm. |

## Reads

List endpoints return `{"results": [...], "next_cursor": ...}` — use `jq '.results[]'`.

```bash
# active tasks
curl -s -H "$H" "https://api.todoist.com/api/v1/tasks" | jq '.results[]'

# filter
curl -s -H "$H" "https://api.todoist.com/api/v1/tasks?filter=today" | jq '.results[]'
curl -s -H "$H" "https://api.todoist.com/api/v1/tasks?project_id=$PID" | jq '.results[]'

# one task (bare object, no .results wrapper)
curl -s -H "$H" "https://api.todoist.com/api/v1/tasks/$ID" | jq

# projects, sections, labels
curl -s -H "$H" "https://api.todoist.com/api/v1/projects" | jq '.results[]'
curl -s -H "$H" "https://api.todoist.com/api/v1/labels" | jq '.results[]'
```

## Add

```bash
# minimal
curl -s -H "$H" -H "Content-Type: application/json" \
  -X POST "https://api.todoist.com/api/v1/tasks" \
  -d '{"content":"Buy milk"}'

# with due, project, labels
curl -s -H "$H" -H "Content-Type: application/json" \
  -X POST "https://api.todoist.com/api/v1/tasks" \
  -d '{"content":"Pay rent","due_string":"every 1st","priority":4,"project_id":"'"$PID"'","labels":["finance"]}'
```

`due_string` on **create** is fine — it sets the recurrence rule fresh.

## Complete / advance one occurrence

```bash
# safest: advances recurring tasks correctly, completes non-recurring
curl -s -H "$H" -X POST "https://api.todoist.com/api/v1/tasks/$ID/close"
```

Use for "I did today's instance of laundry-every-friday." Returns 204 on success.

## Reschedule one instance

To move only this occurrence without re-parsing the rule, use **Sync API**, copy the existing `due` block, change only `date`:

```bash
# 1. read existing due
DUE=$(curl -s -H "$H" "https://api.todoist.com/api/v1/tasks/$ID" \
  | jq -c '{string:.due.string, date:"YYYY-MM-DD", is_recurring:.due.is_recurring, timezone:.due.timezone, lang:(.due.lang // "en")}')

# 2. build sync command, replace date
NEW_DATE="2026-06-15"
DUE_NEW=$(echo "$DUE" | jq --arg d "$NEW_DATE" '.date=$d')

# 3. post sync item_update
UUID=$(uuidgen)
CMD=$(jq -nc --arg id "$ID" --argjson due "$DUE_NEW" --arg uuid "$UUID" '
  [{type:"item_update", uuid:$uuid, args:{id:$id, due:$due}}]
')
curl -s -H "$H" -X POST "https://api.todoist.com/api/v1/sync" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --arg cmds "$CMD" '{commands:($cmds|fromjson)}')"
```

This preserves `string` (the recurrence rule), `is_recurring`, `timezone`, `lang`. Only `date` changes. Reference: [Doist/todoist-mcp `reschedule-tasks.ts`](https://github.com/Doist/todoist-mcp/blob/main/src/tools/reschedule-tasks.ts) (PR #382).

## Permanently complete a recurring task (stop the rule)

Explicit, destructive — **ask user to confirm**:

```bash
curl -s -H "$H" -X POST "https://api.todoist.com/api/v1/tasks/$ID/complete"
```

## Update non-recurring task

```bash
curl -s -H "$H" -H "Content-Type: application/json" \
  -X POST "https://api.todoist.com/api/v1/tasks/$ID" \
  -d '{"content":"new content","due_string":"tomorrow"}'
```

If the task may be recurring, GET first and route per the table above.

## Delete

```bash
curl -s -H "$H" -X DELETE "https://api.todoist.com/api/v1/tasks/$ID"
```

## Pointers

- Unified `/api/v1/` docs: https://developer.todoist.com/api/v1/ (REST v2 + Sync v9 endpoints both 410 as of 2026)
- Doist issue that motivated the safe-reschedule fix: https://github.com/Doist/todoist-ai/issues/279
- Reference implementation: https://github.com/Doist/todoist-mcp/blob/main/src/tools/reschedule-tasks.ts
- OP service account: [`1password-cli`](../1password-cli/SKILL.md)
