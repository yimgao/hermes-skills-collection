---
name: standup-status-updater
description: "Generate your daily standup update in 30 seconds — auto-sync from git log, pomodoro focus log, completed tasks, meetings and blockers to produce a Yesterday / Today / Blockers / Ask-for-help update ready to paste into Slack, Teams or async standup. Local-first, works with async (Geekbot/Range) too."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, standup, scrum, agile, daily-status, git, async-work, sync, update, work-log]
    related_skills: [pomodoro-coach, weekly-review, daily-briefing, daily-shutdown, inbox-triage, meeting-minutes-generator, meeting-prep-brief]
---

# ☀️ Standup Status Updater — 每日站会更新生成器

> "Yesterday / Today / Blockers" in 30 seconds, assembled from the work you actually did — not from memory. 把昨天的 git 提交、番茄钟、已完成事项和会议自动拼成一条可直接粘贴的站会更新，不用靠脑子回忆。

---

## Overview

This skill generates a **ready-to-paste daily standup update** from the user's real activity trail. Instead of staring at a blank Slack box every morning, the user says *"generate my standup"* and gets a tight 3-bullet update: what I did yesterday, what I'm doing today, and where I'm blocked.

The skill is a **data aggregator + speech synthesizer**: it reads whatever local activity logs exist (git log, pomodoro blocks, task lists, calendar events, notes) and compresses them into the exact format teams expect — no fluff, no jargon soup, honest blocker reporting.

| Capability | What It Does | How |
|------------|-------------|-----|
| **Yesterday synthesis** | Turns git commits + pomodoros + completed tasks into "what I shipped" bullets | Reads `git log --since`, `~/.hermes/pomodoro/`, task lists |
| **Today plan** | Distills calendar events + open tasks + WIP into a short today-plan | Calendar ICS parse + open-task scan |
| **Blocker detection** | Surfaces stuck items: unmerged PRs >N days, repeated open loops, waiting-on replies | Diff/PR age checks + inbox scan |
| **Async standup mode** | Same content re-formatted for Geekbot / Range / Slack workflow (concise, no @mentions) | Output template switch |
| **Sprint / 1:1 framing** | "Since last standup" (daily) or "since Friday" (Monday) or "this sprint" variants | Time-window presets |
| **Wins & evidence** | Adds one "win" line with concrete evidence (commit hash, PR link) when available | Optional evidence pinning |
| **Blockers with ask** | Every blocker gets a suggested ask: who to ping + what you need | Open-loop + contact mapping |
| **Paste-ready export** | Renders plain-text (Slack) or HTML-list (Teams) or markdown (async) | Format presets |

Everything runs **locally**. No standup data is uploaded anywhere. Git/calendar/pomodoro data never leaves the machine.

---

## When to Use

- *"Generate my standup"* / *"帮我生成今天的站会更新"* — morning, before the daily sync
- *"What should I say at standup today?"* — you have a sync in 5 minutes and no idea what you did
- *"Draft my async standup for Geekbot"* — async team, update due by noon
- *"Monday standup — need to cover Friday's work too"* — weekend gap handling
- *"My standup is in 10 min and I'm blocked on the API review"* — blocker + ask framing
- *"Write my sprint-update for the retro"* — longer-format update, not daily
- *"What did I actually do yesterday?"* — memory jog when you genuinely don't remember
- Any request mentioning **"standup", "站会", "daily status", "scrum update", "async update", "what did I do yesterday", "blockers"**

---

## Core Workflow

### Step 1: Detect the mode and window

Ask (or infer from the trigger) two things before generating:

```bash
# Mode: daily (default) | monday (covers Fri-Sun) | async | sprint | retro
MODE=daily
# Window: how far back to look for "yesterday"
case "$MODE" in
  daily)  SINCE="yesterday" ;;
  monday) SINCE="3 days ago" ;;   # Fri+Sat+Sun
  sprint) SINCE="14 days ago" ;;
esac
```

Quick decision table:

| Trigger word | Mode | "Yesterday" window |
|--------------|------|-------------------|
| "standup", "站会" | daily | last ~24-30h of activity |
| Monday / "covering Friday" | monday | Fri 17:00 → now |
| "Geekbot", "Range", "async" | async | last work session |
| "sprint update", "retro" | sprint | last 1-2 weeks |

**Default daily mode** if nothing indicates otherwise. Confirm with the user only if ambiguous:
> *"Daily standup, covering since yesterday 5pm. Sync from git + pomodoro + calendar? (say 'skip git' to go manual)"*

---

### Step 2: Pull the activity trail (each source optional + auto-skip)

Collect real data in priority order. Any source that is missing/offline is skipped silently — never block the output on a missing source.

**a) Git commits (strongest signal if you code):**

```bash
# In the repo the user was working in yesterday (ask which repo or auto-detect cwd)
git log --since="yesterday 17:00" --pretty=format:"%h %s" --author="$(git config user.name)" 2>/dev/null | head -15
# With stats, if you want evidence:
git log --since="yesterday 17:00" --pretty=format:"%h %s" --shortstat --author="$(git config user.name)" 2>/dev/null | head -25
```

**b) Pomodoro / focus log** (`~/.hermes/pomodoro/log.json` when present):

```python
import json, os
from datetime import datetime, timedelta
p = os.path.expanduser("~/.hermes/pomodoro/log.json")
if os.path.exists(p):
    data = json.load(open(p))
    sessions = [s for s in data if datetime.fromisoformat(s["ended_at"]) >= datetime.now()-timedelta(hours=30)]
    for s in sessions[-8:]:
        print(f"- {s.get('task','?')}  ({s.get('minutes',25)}min, energy {s.get('energy','?')}/10)")
```

**c) Completed tasks / to-dos** — any local task list the user keeps (taskwarrior `task done:today`, a `todo.md`, the `weekly-review` plan file, `daily-shutdown`'s "tomorrow's first move").

**d) Calendar events yesterday + today** (ICS file or `gws` if configured):

```bash
# From an ICS export: list yesterday's and today's events w/ time ranges
# e.g. parse with python icalendar or a lightweight regex on the ICS
# Only summarize: "3 meetings (2h10m) + 1.5h deep work block" — don't paste titles of private meetings
```

**e) Open PRs / waiting-on** (optional; only if a `gh`/`git` remote is present):

```bash
gh pr list --author "@me" --state open 2>/dev/null | head -10   # auto-skip if gh missing
gh pr list --search "review-requested:@me" --state open 2>/dev/null | head -5
```

> ⚠️ **Pitfall**: never auto-run `gh`/`git` against a repo without confirming the cwd is the right repo. If unsure, ask "which repo?" once.

---

### Step 3: Classify each item into the 4 buckets

Bucket the collected items:

| Bucket | Rule | Example |
|--------|------|---------|
| **Done / Shipped** | Commit subject, completed task, finished pomodoro on a deliverable, meeting that produced a decision | "Shipped auth-refactor branch (a3f9c2) — SSO now passes 40/40 tests" |
| **In Progress (WIP)** | Open PR, task with recent activity, "today's first move" from shutdown | "Mid-review on the Stripe webhook handler (#214)" |
| **Planned Today** | Calendar events + remaining tasks + stated intention | "Drafting the Q3 metrics doc; 2pm sync w/ data team" |
| **Blocked / Waiting** | Open loop >2 days, PR awaiting review >3 days, unanswered email flagged in inbox-triage | "Blocked on API contract sign-off from Priya (pinged Tue, no reply)" |

**Compression rules** (the whole point — standups are read in 15 seconds):
- Max **3 done bullets**, **2-3 today bullets**, **1-2 blockers**. Anything beyond that is noise — fold extras into "also: ..." one-liner.
- Use **action verbs**, no hedging: "investigated", "shipped", "unblocked", "drafted", NOT "was working on", "kind of did".
- **No jargon soup**: expand acronyms on first use in the bullet ("CI pipeline" not "CI/CD infra pipeline orchestration layer").
- Meetings count as work only when they **produced a decision or artifact** ("sync w/ design → landed on dark-mode v2 spec"), not "had a meeting".
- If git shows nothing and pomodoro shows nothing, say so honestly in the evidence line rather than inventing work.

---

### Step 4: Render the update

Output the **paste-ready text** in the requested format. Slack plain-text default:

```text
☀️ STANDUP — Wed 2026-09-09 · mode: daily · synced from git+pomodoro+calendar

✅ Yesterday
• Shipped auth-refactor (a3f9c2) — SSO passes 40/40, PR #211 merged
• Unblocked the CSV export bug — root cause was timezone offset in date parser
• Landed design decision: dark-mode v2 uses system tokens (sync w/ Mia)

🔜 Today
• Mid-review on Stripe webhook handler (#214) — expect to merge by EOD
• Draft Q3 metrics doc (2pm sync w/ data team after)

🚧 Blockers
• Waiting on API contract sign-off from Priya — pinged Tue, no reply yet. Ask: can you approve by tomorrow?
```

**Async / Geekbot mode** (tight, no headers needed if the tool provides them):

```text
Yesterday: Shipped auth-refactor (a3f9c2), unblocked CSV export bug (tz offset).
Today: Finish Stripe webhook review #214, draft Q3 metrics doc.
Blockers: Need API contract sign-off from Priya (pinged Tue).
```

**Teams mode**: render bullets as `•` lines (Teams strips markdown lists inconsistently) — keep it plain.

**Sprint / retro mode**: longer narrative, includes the "win with evidence" line:
> "This sprint I shipped X (PR #211 merged, 40/40 tests), cut CSV export bug rate to ~0, and landed the dark-mode v2 spec. Next sprint: Stripe webhook GA + metrics doc."

---

### Step 5: Offer next actions

- **Has blocker** → "Want me to draft the ping to Priya?" (uses `message-tone-adjuster` / `email-composer`)
- **Async mode** → "Paste this into Geekbot — want it re-trimmed to 3 lines?"
- **Monday** → "Want a Friday→Monday version with the weekend gap called out?"
- **Retro** → "Want the full sprint-narrative version saved to your `weekly-review` file?"

---

## Example Invocations

### Example 1: Daily standup from git + pomodoro

> **User:** generate my standup

**Agent:**
- Mode: daily, window since yesterday 17:00
- Sources found: git log (2 commits in `auth-refactor`), pomodoro log (3 sessions: auth tests 50min, CSV bug 25min, docs 25min), calendar (2pm data sync today)
- Buckets: Done = merged PR #211 + CSV fix; Today = finish webhook review, draft Q3 doc; Blocker = waiting on Priya's contract sign-off
- Renders the plain-text card above (mode: daily)
- Offers to draft the ping to Priya → user accepts → 2-line nudge via message-tone-adjuster

---

### Example 2: Monday standup (covers the weekend)

> **User:** Monday standup, I did a bunch Friday but nothing over the weekend. Also async — paste into Geekbot.

**Agent:**
- Mode: monday (window Fri 17:00→now) + async output
- Git shows Friday's work on the dashboard branch; pomodoro shows nothing Sat/Sun; tasks show "ship v1.3 release notes" open
- Because weekend is empty, adds one explicit line so the team isn't confused:
  > "No commits Sat-Sun (weekend off). Friday: shipped dashboard v1.3 (7 commits). Today: release-note polish + deploy checklist. Blockers: none."
- Renders in tight async format, 3 lines, ready for Geekbot

---

### Example 3: Blocked + needs an ask

> **User:** standup in 10 min, I'm blocked on the API review. What do I say?

**Agent:**
- Mode: daily; blockers bucket prioritized
- Pulls git: `webhook-handler` branch unmerged, last commit 4 days ago; gh shows PR #214 waiting on review (requested from Priya 4 days ago)
- Also pulls open loop from daily-shutdown log: "API contract sign-off" surfaced twice this week → chronic blocker flag
- Renders tight card with blocker first, and the ask made explicit:
  > "Blockers: PR #214 has been waiting on review 4 days — can Priya/backup reviewer take a look today? Everything else on track."
- Offers the ping draft → writes a 2-line nudge for Priya + suggests CC'ing the backup reviewer

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User's cwd isn't the repo they worked in yesterday | Auto-detect only if `git rev-parse` succeeds in cwd; otherwise ask "which repo?" once, cache the answer |
| Empty git log (no commits yesterday) but user did real work (meetings, docs, ops) | Never fake it — say "no commits, here's what pomodoro/calendar show" and let the user fill the gap |
| Over-long standup (10 bullets) | Enforce compression: max 3 done / 3 today / 2 blockers; extras collapse into "also: ..." |
| Copying internal meeting titles into standup | Summarize meetings as "sync w/ X → decision Y", never paste the raw calendar title of a private/1:1 meeting |
| User mentions blocking but has no ask | Every blocker needs an ask: who + what + deadline. If the ask is missing, prompt for it |
| Async tools have character limits | Geekbot/Range read best ≤3 lines each section; offer a trimmed variant automatically in async mode |
| Monday standup shows empty weekend and team wonders | Add an explicit "no commits Sat-Sun (weekend)" line — honesty beats silence |
| Git author mismatch (work vs personal email) | Match `--author` against all the user's known emails, or drop the filter and let the user skim |
| Blocker is >5 days old and user keeps re-reporting it | Flag it as a chronic blocker and suggest escalating (reassign, ask manager, or drop scope) — don't just re-paste it |
| User pastes raw git output full of noise | Compress: "7 commits on dashboard v1.3" — not 7 commit subjects |
| `gh` CLI not installed / no remote | Skip PR enrichment silently; the base git+pomodoro path still works |

---

## Verification Checklist

- [ ] Mode + time window resolved (daily / monday / async / sprint)
- [ ] At least 2 data sources attempted (git, pomodoro, tasks, calendar) — missing ones skipped, not fatal
- [ ] Every "done" bullet is backed by evidence (commit, task, session) — nothing invented
- [ ] Meetings summarized as decision/artifact, not raw titles
- [ ] Buckets present: done ≤3, today ≤3, blockers ≤2
- [ ] Every blocker has an explicit ask (who + what + when)
- [ ] Weekends / no-work gaps called out honestly
- [ ] Output is paste-ready in the right format (plain / async / teams / retro)
- [ ] No private or confidential info leaked into the update
- [ ] Next-action offers given (ping draft, trim for async, retro version)

---

## Data Sources & Accuracy

| Source | Used For | Local / Network | Notes |
|--------|----------|-----------------|-------|
| `git log --since` (in user's repo) | Done/WIP bullets with commit hashes | Local | Requires correct repo; author-filtered |
| `~/.hermes/pomodoro/log.json` | Focus-session evidence | Local | Present only if pomodoro-coach used |
| Task lists (taskwarrior / todo.md / shutdown log) | Today plan + open loops | Local | Multiple formats tolerated |
| Calendar ICS / `gws` | Meeting-aware framing | Local (or network if gws) | Summarize, don't quote titles verbatim |
| `gh pr list` | PR-age blocker detection | Network, opt-in | Auto-skip if `gh` missing / not authed |
| User's chat input | Manual fill for anything logs miss | — | The user is always the final editor |

**Accuracy caveats:**

- The skill **aggregates and compresses** — it does not invent work. Anything that isn't in a log or stated by the user stays out of the update.
- Commit messages are treated as user-authored evidence; if the user's commit history is sloppy the standup will read sloppy too. Suggest better commit messages via `changelog-generator` conventions.
- "Waiting on Priya" claims require the user to confirm the contact is actually the right owner — the skill can't know the org chart.
- Best results come from using the companion skills consistently: `pomodoro-coach` for focus evidence, `daily-shutdown` for open loops + tomorrow's first move, `inbox-triage` for waiting-on emails, `meeting-minutes-generator` for decision trails. Garbage in → garbage out; the trail is only as good as the logging habit.
