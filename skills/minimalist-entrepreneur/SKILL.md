---
name: "minimalist-entrepreneur"
description: "Route Minimalist Entrepreneur requests. Skills for Sahil Lavingia-style minimalist business workflows: finding a community, validating ideas, processizing, building MVPs, pricing, selling to first customers, marketing, growing sustainably, reviewing decisions, and defining company values."
---

# Minimalist Entrepreneur

Generated from skills.toml router `minimalist-entrepreneur`.

Use this skill as a portable router for a related skill bundle. Do not read every bundled workflow by default. First identify the user's current job, then read only the relevant reference instruction file or files.

## Routing

| User intent | Read |
| --- | --- |
| Help define company values and culture for a minimalist business. Use when someone is setting up their company culture, preparing to hire, or wanting to codify what their company stands for. | `references/company-values/instructions.md` |
| Help identify and evaluate communities to build a minimalist business around. Use when someone is looking for a business idea, trying to find their community, or wondering where to start as an entrepreneur. | `references/find-community/instructions.md` |
| Create a strategy for selling to your first 100 customers using the minimalist entrepreneur playbook. Use when someone has a product and needs to find customers, or is struggling with early sales. | `references/first-customers/instructions.md` |
| Evaluate business decisions through the lens of sustainable, profitable growth. Use when someone is making decisions about spending, hiring, fundraising, or scaling their business. | `references/grow-sustainably/instructions.md` |
| Create a minimalist marketing plan focused on building an audience through content, not ads. Use when someone has product-market fit (~100 customers) and wants to scale with marketing, or needs a content strategy. | `references/marketing-plan/instructions.md` |
| Review any business decision, plan, or strategy through the minimalist entrepreneur lens. Use when someone wants a gut-check on a business decision, wants to simplify their approach, or needs to decide between options. | `references/minimalist-review/instructions.md` |
| Guide building a minimum viable product the minimalist entrepreneur way — manual first, then processized, then productized. Use when someone is ready to build their first product or struggling with scope. | `references/mvp/instructions.md` |
| Help figure out pricing for a product or service using minimalist entrepreneur principles. Use when someone is setting prices, considering price changes, or struggling with what to charge. | `references/pricing/instructions.md` |
| Turn a product idea into a manual-first process you can start delivering today. Use when you have an idea and want to figure out how to deliver value by hand before writing any code. | `references/processize/instructions.md` |
| Validate a business idea using the minimalist entrepreneur framework. Use when someone has a business idea and wants to test if it's worth pursuing before building anything. | `references/validate-idea/instructions.md` |

## Workflow

1. Match the user's request to the narrowest row in the routing table.
2. Read the referenced instruction file before giving substantive guidance.
3. If the request spans multiple workflows, read the smallest useful set of referenced skills.
4. Follow the loaded reference skill instructions as the source of truth for the answer.
