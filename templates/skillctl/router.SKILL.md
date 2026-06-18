---
name: $NAME_JSON
description: $DESCRIPTION_JSON
---

# $TITLE

$SOURCE_NOTE
Use this skill as a portable router for a related skill bundle. Do not read every bundled workflow by default. First identify the user's current job, then read only the relevant reference instruction file or files.

## Routing

| User intent | Read |
| --- | --- |
$ROUTING_ROWS

## Workflow

1. Match the user's request to the narrowest row in the routing table.
2. Read the referenced instruction file before giving substantive guidance.
3. If the request spans multiple workflows, read the smallest useful set of referenced skills.
4. Follow the loaded reference skill instructions as the source of truth for the answer.
