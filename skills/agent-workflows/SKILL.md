---
name: "agent-workflows"
description: "Route Agent Workflows requests. Skills for structured agent collaboration workflows: planning grill sessions, documentation-backed grilling, issue triage, and zooming out for broader context."
---

# Agent Workflows

Generated from skills.toml router `agent-workflows`.

Use this skill as a portable router for a related skill bundle. Do not read every bundled workflow by default. First identify the user's current job, then read only the relevant reference instruction file or files.

## Routing

| User intent | Read |
| --- | --- |
| A relentless interview to sharpen a plan or design. | `references/grill-me/instructions.md` |
| A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. | `references/grill-with-docs/instructions.md` |
| Move issues and external PRs through a state machine of triage roles — categorise, verify, grill if needed, and write agent-ready briefs. | `references/triage/instructions.md` |
| Ask the agent to zoom out a level and map the relevant modules and callers using the project's domain language. | `references/zoom-out/instructions.md` |

## Workflow

1. Match the user's request to the narrowest row in the routing table.
2. Read the referenced instruction file before giving substantive guidance.
3. If the request spans multiple workflows, read the smallest useful set of referenced skills.
4. Follow the loaded reference skill instructions as the source of truth for the answer.
