---
name: hypercontext
description: Spatial context awareness. Renders session state as ASCII map — threads, heat, files, tools, runway. Self-awareness as UX.
version: 0.3
status: documented
---

# Hypercontext — Spatial Context Awareness

You already know your own context. This skill gives you a way to show it.

`/hypercontext` — full map | `/hypercontext compact` — for continuation prompts | `/hypercontext threads` | `/hypercontext heat`

## Example

```
╔══════════════════════════════════════════════════════════════════════╗
║  HYPERCONTEXT — session 2026-01-29 21:30                             ║
║  ctx ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░ ~50% (100k/200k)            ║
║  ▁▂▃▅▆▆▇▇█ velocity ─────────────────── runway: ~100k                ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  THREADS                               HEAT                          ║
║  ┌───────────────────┐                 ████ Site deploy              ║
║  │ Site Deploy       │                 ███░ SKILL refinement         ║
║  │  ├── HTML      ✓  │                 ██░░ DNS setup                ║
║  │  ├── Deploy    ✓  │                 █░░░ UX consult               ║
║  │  └── SSL       ~  │                                               ║
║  └────────┬──────────┘                                               ║
║           │                                                          ║
║  ┌────────v──────────┐  ┌───────────────────┐                        ║
║  │ DNS Config        │  │ Skill Refinement  │                        ║
║  │  ├── CNAME     ✓  │  │  ├── Protocol  ✓  │                        ║
║  │  └── Apex      x  │  │  └── Compress  ~  │                        ║
║  └───────────────────┘  └───────────────────┘                        ║
║                                                                      ║
║  FILES TOUCHED           TOOLS USED          SYSTEMS                 ║
║  index.html      ◆      Bash  ████████ 34   Win (here)  ✓            ║
║  SKILL.md        ◆      Read  ████     12   Cloudflare  ✓            ║
║  upload-to-kv.js ◇      Edit  ███       9   Namecheap   ✓            ║
║  worker.js       ◇      Task  ██        5   KV Store    ✓            ║
║                         Write █         3                            ║
║                                                                      ║
║  DECISIONS                              OPEN                         ║
║  ✓ .sh as primary domain                ? Apex TLS via CF DNS        ║
║  ✓ Terminal-forward layout              ? OG card verification       ║
║  ✓ KV for skill serving                 ? Compact mode testing       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

That's it. Render YOUR session. Introspect honestly — real threads, real files, real counts.

## How

- **Context bar**: `▓`=used `░`=remaining. 35-char bar, 200k total. Estimate: `5000 + (turns × 2000) + (files_read × 2000) + (skills × 2000)`. Round to nearest 5%.
- **Velocity**: `▁▂▃▄▅▆▇█` sparkline, left=early right=recent. One char per turn (group if >12). Ramp `▁`→`█` by activity per turn. Short early sparklines are honest.
- **Threads**: 3-6 boxes. `✓`done `~`wip `x`blocked `·`not-started `*`idea. Top blocks bottom (`│v`); side-by-side for parallel.
- **Heat**: 4-char fill bars ranked by recency. `████`=hot `░░░░`=stale. Pure recency — no importance guessing.
- **Files**: `◆`=modified `◇`=read-only. Last 2-3 path segments, modified first.
- **Tools**: `█` bars scaled to max_count/8, round to nearest (min 1). Count after bar. Descending.
- **Systems**: `✓`=contacted this session `░`=unknown. Only relevant systems.
- **Decisions/Open**: One line each, ~35 chars max.

## Color

Default is monochrome. To emit color, use `echo -e` with ANSI codes via Bash. The human sees color; your tool output won't reflect it — that's expected.

```
Frame/borders    \033[90m  (gray)
Header           \033[1;36m (bold cyan)
Context filled   \033[32m  (green)
Context empty    \033[90m  (gray)
Velocity         \033[34m  (blue)
Heat ████ hot    \033[31m  (red)
Heat ███░ warm   \033[33m  (yellow)
Heat █░░░ stale  \033[90m  (gray)
✓ done           \033[32m  (green)
? open           \033[33m  (yellow)
◆ modified       \033[33m  (yellow)
◇ read-only      \033[90m  (gray)
Tool bars        \033[36m  (cyan)
Reset            \033[0m
```

Each `echo -e` line wraps content between color code and `\033[0m` reset.

## Compact Mode

`/hypercontext compact` — dense markdown for continuation-prompt.md, no ASCII boxes:

```
# Hypercontext — {date} {time}
ctx: ~{pct}% | runway: ~{remaining} | turns: {count}
## Threads — 1. {thread}: {status}
## Files — {file}: {change}
## Decided — {decision}
## Open — {question}
## Next — {action}
## Paths — {path}
```

## The Rule

Don't hallucinate. Every thread, file, tool count, and system status must reflect what actually happened in this session. The map is only useful if it's true. Above ~70% → run compact for a continuation prompt.

```
         }@{@}@{@}@{@}
       @{@}@{@}@{@}@{@}@{
      @}@{@}@{@}@{@}@{@}@{@}
     @{@}@@@@@@@@@@@@@@@@{@}@{
     @@@@@                @@@@@
     @@  ┌──────┐ ┌──────┐  @@
     @@  │  ·   │─│  ·   │  @@   "curls get claudes
     @@  └──────┘ └──────┘  @@    with skills"
      @@        /\         @@
       @\      ‾‾‾‾       /@
         `-.    ||    .-'
              `'||`'
```

