---
name: agentsview-api
description: Query, search, and export coding-agent session transcripts from a local AgentsView instance over HTTP. Use when you need to find sessions by text content, download a full session transcript, or programmatically access session metadata and messages.
---

# AgentsView HTTP API Reference

AgentsView stores all coding-agent session data in a local SQLite DB and exposes REST API endpoints. Default URL is the Tailscale-reachable public endpoint, which works from any machine on the network; override with `AGENTSVIEW_URL` (e.g. `http://agentsview:8080` inside the devbox docker network, `http://localhost:8080` when running on the host of the agentsview container).

## Variables

```bash
AGENTSVIEW_URL="${AGENTSVIEW_URL:-https://agentsview.dev.ankitson.com}"
AGENTSVIEW_DB="${AGENTSVIEW_DB:-}"  # set to SQLite path for local queries
```

## List / Search Sessions

### `GET /api/v1/sessions`

Query parameters:
- `search` — full-text search across all message content
- `agent` — filter by agent (claude, opencode, codex, gemini, etc.)
- `project` — filter by project name
- `limit` — page size (default ~50)
- `cursor` — pagination cursor from previous response

Examples:

```bash
# Search all sessions mentioning "birdclaw"
curl -s "$AGENTSVIEW_URL/api/v1/sessions?search=birdclaw"

# Get latest Claude Code sessions
curl -s "$AGENTSVIEW_URL/api/v1/sessions?agent=claude&limit=5"

# Filter by project
curl -s "$AGENTSVIEW_URL/api/v1/sessions?project=homeserver"
```

Response includes `sessions[]` with metadata (message_count, token usage, outcome, health_score, timestamps) and a `next_cursor` for pagination. The `total` field gives the total matching count.

## Get Session Details

### `GET /api/v1/sessions/{id}`

```bash
curl -s "$AGENTSVIEW_URL/api/v1/sessions/$SESSION_ID"
```

Returns the session metadata object (same shape as items in the list endpoint).

## Download Full Transcript

### `GET /api/v1/sessions/{id}/messages`

Returns all messages in JSON array form, ordered by `ordinal`.

```bash
# Full transcript as JSON
curl -s "$AGENTSVIEW_URL/api/v1/sessions/$SESSION_ID/messages"
```

Each message has:
- `role` — "user" | "assistant" | "system"
- `content` — the message text (includes tool calls, bash commands, etc.)
- `timestamp` — ISO 8601
- `ordinal` — sequence number
- `has_thinking`, `has_tool_use` — boolean flags
- `model`, `token_usage`, etc.

### Format as plain-text transcript

```bash
curl -s "$AGENTSVIEW_URL/api/v1/sessions/$SESSION_ID/messages" \
  | jq -r '.[] | "## \(.role) (\(.timestamp))\n\n\(.content)\n"' \
  > transcript.md
```

## Local SQLite (faster for large exports)

If `AGENTSVIEW_DB` is set to the SQLite DB path, query directly:

```bash
sqlite3 "$AGENTSVIEW_DB" \
  "SELECT '## ' || role || x'0a' || x'0a' || content \
   FROM messages \
   WHERE session_id = '$SESSION_ID' \
   ORDER BY ordinal" \
  > transcript.md
```

If the DB path is unknown, common locations include:
- Docker named volume: inspect `docker volume inspect <name>` to find the mount point
- Default local install: check `agentsview server --help` or look for `sessions.db` under the data directory passed at startup
