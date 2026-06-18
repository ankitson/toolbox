---
name: opportunity-finder
description: "Find unique opportunities for a field or person using Exa search: fellowships, mentorship programs, summer research programs, grants, open calls, labs, professors, departments, accelerators, residencies, internships, and under-the-radar paths. Use whenever the user wants opportunities like Google Summer of Code, Summer of Open Research, academic labs, university departments, research mentors, niche programs, or a sourced opportunity map for a topic."
---

# Opportunity Finder

Find actionable, non-obvious opportunities around a topic, discipline, career direction, research area, or person. Bias toward opportunities the user can actually pursue: programs with applications, mentors to contact, labs doing relevant work, departments with aligned faculty, grants, fellowships, open calls, communities, and repeatable discovery routes.

## Tool Restriction

Use `web_search_advanced_exa` as the primary search tool.

Do not use basic Exa search for this workflow unless `web_search_advanced_exa` is unavailable. The advanced tool is important because opportunity research depends on date filters, domain targeting, categories, and query variation.

If the runtime exposes tools with server prefixes, call the Exa tool as `exa:web_search_advanced_exa`.

## Keep Search Volume Out of Main Context

When subagents or Task agents are available, do the search work in agents:

- Each agent runs a focused Exa search bundle.
- Each agent deduplicates and scores its own results.
- Each agent returns compact JSON or short markdown with sources.
- The main context merges the distilled outputs.

Use separate agents for distinct lanes, such as:

- Programs and fellowships
- Professors and labs
- Departments and centers
- Grants, residencies, open calls, and competitions
- Community-run or under-the-radar opportunities

If subagents are unavailable, run smaller batches directly and summarize before continuing.

## Start by Framing the Search

Extract or ask for the minimum useful constraints:

- Topic or area: e.g. open research, AI safety, human-computer interaction, computational biology, climate tech
- User profile: student, independent researcher, engineer, artist, founder, high schooler, international applicant, etc.
- Geography: remote, country, region, visa constraints, university affiliation needs
- Time horizon: now, next semester, summer, yearly cycle, rolling
- Output need: quick shortlist, comprehensive map, professor contact list, application plan

If the user is vague, make a reasonable first pass and label assumptions. Do not block on details unless eligibility would change the search substantially.

## Search Strategy

Generate 2-4 query variations per lane. Exa returns different results for different phrasings, so vary the angle rather than only the keywords.

Good query families:

- `"summer research program" "[topic]" students application`
- `"mentorship program" "[topic]" open source research`
- `"fellowship" "[topic]" independent researcher application`
- `"undergraduate research" "[topic]" lab professor university`
- `"research group" "[topic]" "prospective students"`
- `"center" "[topic]" university faculty research`
- `"grant" OR "microgrant" "[topic]" open call`
- `"residency" "[topic]" application`
- `"Google Summer of Code" "[topic]" organizations ideas`
- `"Summer of Open Research" "[topic]" mentors`

Use domain targeting to dig into likely opportunity sources:

- University sites: `includeDomains` such as `["mit.edu", "stanford.edu", "berkeley.edu"]`
- Program directories: domains for known organizers, foundations, and open-source ecosystems
- Government or foundation grants: `.gov`, `nsf.gov`, `nih.gov`, `wellcome.org`, `mozilla.org`, etc.
- Open-source programs: `summerofcode.withgoogle.com`, `github.com`, foundation websites

Use date filters for current-cycle opportunities:

- `startPublishedDate` for recently announced programs, open calls, and application windows
- `startCrawlDate` when pages are old but may have been refreshed recently
- Avoid date filters for evergreen university department or professor discovery unless freshness matters

## Categories and Filters

Use Exa categories intentionally:

- `category: "people"` for professors, mentors, lab leads, public LinkedIn-style profiles
- `category: "company"` only for organizations, foundations, startups, nonprofits, and program hosts
- `category: "news"` for recent announcements and new cohorts
- `category: "research paper"` for finding active researchers through recent papers
- No category with `type: "auto"` for broad program pages, university pages, and mixed results

Important Exa restrictions:

- With `category: "company"`, do not use domain filters or date filters.
- With `category: "people"`, keep filters minimal.
- `includeText` and `excludeText` should be single-item arrays.
- Prefer `type: "auto"` unless the user explicitly wants fast scouting.

## Opportunity Lanes

Search across at least three lanes unless the user requests a narrow target.

### Programs

Look for structured programs with dates, mentors, and application pages:

- Summer research programs
- Open-source mentorship programs
- Fellowships
- Internships
- Visiting researcher programs
- Residencies
- Scholar programs
- Student competitions
- Hackathons with longer-term mentorship

### People

Find people who might unlock opportunities:

- Professors running relevant labs
- Program directors
- Principal investigators
- Open-source maintainers mentoring projects
- Department administrators for undergraduate or visiting research
- Fellowship alumni who can explain the path

Favor people with recent activity, clear topic alignment, and a plausible contact route.

### Institutions

Find departments, centers, and labs:

- University departments with multiple aligned faculty
- Research centers and institutes
- Interdisciplinary labs
- Open-source foundations
- Nonprofits and think tanks
- Government labs or public-interest research groups

### Backdoors

Look for less obvious routes:

- Conference student volunteer programs
- Workshop mentoring tracks
- Reading groups with project pipelines
- Lab seminars that welcome visitors
- Open calls in adjacent fields
- Community grants
- Maintainer calls for contributors
- Public datasets or benchmark challenges that attract mentors

## Scoring

Score each candidate 1-5 on:

- Fit: matches the user's area and profile
- Actionability: has a clear next step, application, email, or project idea
- Uniqueness: not just the obvious top result
- Timeliness: current or likely recurring soon
- Leverage: could connect the user to mentors, institutions, funding, or durable credentials

Flag uncertainty instead of overstating. If eligibility, deadline, funding, or location is unclear, say so and cite the source.

## Output Format

For short requests, return a compact shortlist:

1. Opportunity name - type, why it fits, next step, deadline/status, source
2. Opportunity name - type, why it fits, next step, deadline/status, source
3. Opportunity name - type, why it fits, next step, deadline/status, source

For deeper research, use this structure:

## Opportunity Map

Briefly summarize the strongest pattern you found and the search assumptions.

## Best Bets

List 5-12 high-fit opportunities. For each:

- Name
- Type
- Why it fits
- Who it is for
- Timing or deadline status
- Next action
- Source URL

## People and Labs

List professors, mentors, labs, or departments worth contacting. Include:

- Name or lab
- Institution
- Topic fit
- Contact path or next action
- Source URL

## Under-the-Radar Paths

List weird, adjacent, or less competitive routes. Explain why each might be overlooked.

## Search Notes

Include query lanes searched, important gaps, stale pages, uncertain eligibility, and what to search next if the user wants a second pass.

## Examples

### Find open research opportunities

User: "Find opportunities like Summer of Open Research for independent AI research."

Search lanes:

- AI research mentorship programs
- Open-source research fellowships
- Independent researcher grants
- University labs accepting visitors
- AI safety and open science communities

Output should include named programs, current application status where available, mentor or organizer contacts, and recurring-cycle notes.

### Find university mentors

User: "Find professors and departments for computational social science in Canada."

Search lanes:

- Canadian university computational social science labs
- Recent papers in computational social science with Canadian affiliations
- Faculty pages with prospective student language
- Interdisciplinary data science, sociology, policy, and HCI departments

Output should group by university and prioritize faculty with explicit student, RA, or prospective-student pages.

### Find open-source mentorship paths

User: "Find GSoC-like opportunities for Rust and distributed systems."

Search lanes:

- Google Summer of Code organizations with Rust or distributed systems ideas
- Outreachy, LFX Mentorship, Major League Hacking Fellowship, and foundation programs
- GitHub repositories with mentorship labels or project idea lists
- Maintainer posts and foundation calls for contributors

Output should include program names, project idea pages, eligibility constraints, and what to do this week.
