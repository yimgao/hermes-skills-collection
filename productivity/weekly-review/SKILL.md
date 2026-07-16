---
name: weekly-review
description: "GTD-style weekly review from chat — guided 7-step reflection (open loops, wins, lessons, role goals, next-week rocks, inbox zero, gratitude). Pulls from habits, pomodoros, tasks, calendar. Produces a markdown report and an updated next-week plan. All data local."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, gtd, weekly-review, reflection, planning, second-brain, journaling]
    related_skills: [pomodoro-coach, habit-tracker, personal-crm, sleep-tracker, personal-expense-tracker]
---

# 🗓️ Weekly Review — 周回顾与下周计划

> A guided 30–45 minute weekly review in your terminal. The single highest-leverage habit for anyone practicing Getting Things Done. 把每周日 30 分钟的 GTD 周回顾从「想起来就焦虑」变成「自动跑完」的对话流程。

## Overview

Weekly Review turns Hermes into a personal GTD coach. Every Sunday (or whenever you choose), the skill walks you through the canonical 7-step review, **pulls in your last 7 days of data** from related skills (pomodoros, habits, expenses, contacts), and produces a structured markdown report + an updated next-week plan. Output is local Markdown; nothing leaves your machine.

| Capability | Description |
|------------|-------------|
| **Guided 7-step review** | Open loops → wins → lessons → role goals → next-week rocks → inbox zero → gratitude |
| **Auto data pull** | Aggregates the past 7 days from pomodoro, habit, expense, sleep, and CRM skills when present |
| **Open-loop capture** | All unfinished tasks, projects, and "someday/maybe" items surfaced and triaged |
| **Role-based goals** | Track weekly outcomes across life roles (work, health, family, learning, side-project) |
| **Next-week rocks** | Force-rank top 3 outcomes for the upcoming week with measurable criteria |
| **Inbox-zero check** | Process every captured thought from the week into a project, next-action, calendar, or someday/maybe |
| **Mood & energy score** | 1–10 self-rating at start and end, with delta tracked over time |
| **Markdown report** | Saves `~/.hermes/weekly-review/2026-W28.md` (ISO week) for archival and search |
| **Trends view** | 4/12-week rolling summaries: completion rate, recurring lessons, role balance drift |
| **Privacy-first** | Everything in local Markdown, no cloud sync |

## When to Use

- *"Run my weekly review"*
- *"Start a guided weekly review"*
- *"I just finished my last pomodoro of the week — let's do the review"*
- *"Pull up my review for last week"*
- *"Show me my 4-week trend"*
- *"What keeps showing up as an open loop?"*
- *"What were my wins this week?"*
- *"Help me plan next week"*
- *"Sunday review time"*
- *"周回顾"*
- *"帮我做周复盘"*
- *"这周完成得怎么样？下周怎么安排？"*

## Core Workflow

### Step 1: Initialize & Load Last Week's Context

On first use, create the data directory and the profile file.

```bash
mkdir -p ~/.hermes/weekly-review
touch ~/.hermes/weekly-review/profile.json
touch ~/.hermes/weekly-review/INDEX.md
```

`profile.json` captures:
```json
{
  "name": "User",
  "review_day": "Sunday",
  "review_time": "18:00",
  "roles": ["Work", "Health", "Family", "Learning", "Side-project", "Finance", "Relationships"],
  "rock_target": 3,
  "week_format": "ISO",
  "language": "auto",
  "integrations": {
    "pomodoro": "~/.hermes/pomodoro",
    "habit": "~/.hermes/habits",
    "expense": "~/.hermes/expenses",
    "sleep": "~/.hermes/sleep",
    "crm": "~/.hermes/crm"
  }
}
```

Then determine the current ISO week and load context for the **last 7 days**:

```bash
# Current ISO week
date +"%G-W%V-%u"

# Look for prior weekly review
ls -t ~/.hermes/weekly-review/*.md | head -1
```

If integrations exist, auto-aggregate (this is the *value multiplier*):
```bash
# Total focus hours last week
jq -r 'select(.date >= "2026-07-08") | .duration_minutes' \
  ~/.hermes/pomodoro/sessions.jsonl 2>/dev/null | \
  awk '{s+=$1} END {printf "%.1f hours\n", s/60}'

# Habit completion rate
jq -r 'select(.week == "2026-W28") | .completion_rate' \
  ~/.hermes/habits/weekly.json 2>/dev/null

# Sleep average
jq -r 'select(.date >= "2026-07-08") | .hours' \
  ~/.hermes/sleep/log.jsonl 2>/dev/null | \
  awk '{s+=$1; n++} END {printf "%.1f hrs/night\n", s/n}'

# Spending
jq -r 'select(.date >= "2026-07-08") | .amount' \
  ~/.hermes/expenses/log.jsonl 2>/dev/null | \
  awk '{s+=$1} END {printf "$%.2f\n", s}'
```

**If integrations are missing**, fall back to asking the user a single concise question per metric and accept numeric free-form. Never fabricate data.

### Step 2: Run the 7-Step Guided Review

Present one step at a time. Use short prompts. Allow the user to type `skip`, `back`, or `quit`. Show progress (e.g. `Step 3 of 7`).

**Step 1 — Clear the decks (open loops).** *"What's still on your mind? Anything you started and didn't finish, or any nagging thought?"* Capture every item. Don't filter yet.

**Step 2 — Wins.** *"What went well this week, even small things?"* Force 3 minimum. People under-count wins.

**Step 3 — Lessons.** *"What did you learn? What would you do differently?"* Two columns: *What happened* → *What I'll change*.

**Step 4 — Role check (1–10 per role).** Score each role defined in `profile.json`. Roles under 5 get a follow-up: *"Why is Health a 4? What would move it to a 6?"*

**Step 5 — Choose 3 next-week rocks.** Rocks are outcomes, not tasks. Format: `Verb + measurable result + deadline`. Example: *"Ship the pricing page draft by Friday EOD"* — not *"work on pricing."*

**Step 6 — Inbox zero.** For every open-loop from Step 1, force a destination:
- ✅ Done / no action
- 📁 Project → add to project list with a next action
- ▶️ Next action → calendar or todo
- 📅 Calendar → schedule specific time
- 💭 Someday/maybe → defer with date

**Step 7 — Gratitude & one-word summary.** Three lines of gratitude + a single word for the week (e.g. "reset", "ship", "connect").

### Step 3: Write the Report & Update Plan

Save the report to `~/.hermes/weekly-review/{ISO-week}.md` and append a row to `INDEX.md`:

```markdown
# Weekly Review — 2026-W28 (Jul 6 – Jul 12)

> One-word: **ship**
> Mood: 6 → 8 (+2)

## 📊 Auto-pulled metrics
| Metric | Value | vs. last week |
|--------|-------|---------------|
| Focus hours | 14.2 | +2.1 |
| Pomodoros | 34 | +5 |
| Habit completion | 78% | -4% |
| Sleep avg | 7.1 hrs | +0.3 |
| Spending | $312.50 | -$45 |
| CRM touchpoints | 4 | +1 |

## 🔁 Open loops (12)
1. Finish the contract review for Acme — *next action: email Sarah by Mon 10am*
2. …

## 🏆 Wins
- Shipped the Q3 launch page 2 days early
- Hit the gym 4× this week (target was 3)
- Reconnected with Marcus after 8 months

## 🧠 Lessons
| What happened | What I'll change |
|---------------|------------------|
| Lost 2 hours to "research" rabbit hole on Wednesday | Time-box exploration to 30 min, then commit |
| Skipped Wednesday workout | Move it to morning, block calendar |

## 🎭 Role check
| Role | Score | Δ | Note |
|------|-------|---|------|
| Work | 8 | +1 | Launch went well |
| Health | 7 | 0 | Solid week |
| Family | 5 | -2 | Need Sunday dinner |
| Learning | 4 | -1 | Didn't read at all |

## 🪨 Next-week rocks (top 3)
1. **Ship v2 pricing experiment** — by Fri 17:00
2. **Reconnect with 3 dormant contacts** — by Wed
3. **Read 1 book chapter** — by Sun

## 📥 Inbox-zero destinations
- 5 → done
- 4 → projects (added next actions)
- 2 → calendar (scheduled)
- 1 → someday/maybe (Q4 revisit)

## 🙏 Gratitude
- Saturday morning walk with no phone
- Alex covering for me on Tuesday
- Finishing the launch deck without panic
```

Append to `INDEX.md`:
```
| 2026-W28 | ship | 6→8 | 14.2h | 78% | 3/3 rocks | [report](./2026-W28.md) |
```

### Step 4: Offer Follow-ups (Optional)

After saving, offer:
- *"Generate a printable PDF of this review"* → call `pdf-toolkit` skill
- *"Convert this week's lessons into flashcards"* → call `flashcard-generator` skill
- *"Schedule a check-in for next Wednesday to see if rocks 1 is on track"*
- *"Show me a 4-week trend report"*

The 4-week trend is computed by reading the last 4 `INDEX.md` rows:
```bash
tail -4 ~/.hermes/weekly-review/INDEX.md | \
  awk -F'|' '{print $4, $5}'  # focus hours, habit %
```

## Example Invocations

### 1. User runs a full Sunday review

> **User**: Sunday review time.
>
> **Agent**: Welcome to your weekly review for **2026-W28 (Jul 6 – Jul 12)**. Last review was 2026-W27, scored 7→8. Auto-pulled from your other skills:
> - 14.2 focus hours (↑2.1)
> - 34 pomodoros
> - 78% habit completion (↓4%)
> - 7.1 hr sleep avg
> - $312 spending
>
> Step 1 of 7 — **Open loops**: what's still on your mind, unfinished, or nagging? Free-form, list as many as you want.
>
> **User**: pricing page draft, owe Sarah a contract reply, plant needs repotting, sign up for marathon, call mom, finish Tax docs.
>
> **Agent**: Got 6 loops logged. Step 2 of 7 — **Wins**: list 3, even small ones.
>
> **User**: launched the page, 4 workouts, reconnected with Marcus.
>
> **Agent**: Nice. Step 3 — **Lessons**: what would you do differently?
>
> **User**: Wednesday I went down a 2-hour rabbit hole on payment processors. Block that next time.
>
> **Agent**: Logged. Step 4 — **Role check**. Score 1–10 for: Work, Health, Family, Learning, Side-project, Finance, Relationships.
>
> **User**: W7 H7 F4 L4 S6 F5 R6
>
> **Agent**: Family at 4 — what would move it to 6?
>
> **User**: Sunday dinner, no phones.
>
> **Agent**: Step 5 — **3 next-week rocks**. Format: *verb + measurable result + deadline*.
>
> **User**: 1. Ship pricing v2 by Fri 17:00. 2. Reconnect with 3 dormant contacts by Wed. 3. Read 1 book chapter by Sun.
>
> **Agent**: Step 6 — **Inbox zero** for the 6 loops. Destination for each?
>
> **User**: 1 project, 2 next-action, 1 calendar Sun 6pm, 1 someday Q4 marathon, 1 done (tax).
>
> **Agent**: Step 7 — **Gratitude & one word**. Three gratitudes + one word.
>
> **User**: Saturday walk no phone, Alex covering Tuesday, finished deck without panic. Word: ship.
>
> **Agent**: Report saved to `~/.hermes/weekly-review/2026-W28.md`. INDEX updated. Want me to schedule a Wed check-in on rock 1, or convert your lessons into flashcards?
>
> **User**: Convert lessons to flashcards.
>
> **Agent**: Loading `flashcard-generator` skill with 2 lessons: (1) time-box exploration to 30 min, (2) morning workouts block calendar.

### 2. User just wants a quick 4-week trend

> **User**: Show me my 4-week trend.
>
> **Agent**: Reading the last 4 weekly reviews from `~/.hermes/weekly-review/INDEX.md`:
>
> | Week | Word | Mood | Focus hrs | Habit % | Rocks hit |
> |------|------|------|-----------|---------|-----------|
> | W28 | ship | 6→8 | 14.2 | 78% | 3/3 |
> | W27 | reset | 5→7 | 12.1 | 82% | 2/3 |
> | W26 | grind | 4→5 | 18.4 | 71% | 3/3 |
> | W25 | connect | 7→8 | 9.6 | 88% | 1/3 |
>
> Trends:
> - **Focus hours trending up** (W25→W28: +47%)
> - **Habit completion slipped** since W26 — your sleep dipped in W28, may correlate
> - **Rocks hit rate: 75%** — consistent executor, but W25 was a write-off
> - **One-word arc**: connect → grind → reset → ship (productive progression)
>
> Suggest: protect a lighter "ship" cadence next week to keep habit % climbing.

### 3. User wants to revisit an open loop

> **User**: What keeps showing up as an open loop?
>
> **Agent**: Mining `~/.hermes/weekly-review/*.md` for recurring open-loop items across W23–W28 (6 weeks):
>
> | Loop | Weeks appeared | Last disposition |
> |------|---------------|------------------|
> | "Sign up for marathon" | W23, W24, W25, W26, W27, W28 | Someday/maybe (Q4) — **stuck in someday for 6 weeks** |
> | "Call mom" | W24, W26, W28 | Next action — keeps slipping |
> | "Tax docs" | W27, W28 | Done in W28 ✓ |
> | "Read book chapter" | W25, W27, W28 | Rock in W28 — first time committed |
>
> Recommendation: the marathon has been parked in someday for 6 weeks. Either commit (sign up this week) or delete it. Same for "call mom" — make it a recurring calendar event every Sunday.

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User dumps 30 open loops with no triage | Force Step 6 (inbox zero) on every loop; without triage the review has no value |
| User writes tasks instead of outcomes as rocks | Push back: "Ship the v2 by Friday" is a rock, "work on v2" is not. Reframe until outcome + measurable + deadline |
| Auto-pulled data is missing or stale | Show "(no pomodoro data this week)" honestly; never invent metrics. Ask the user a single number instead |
| Mood score drift is hidden by averaging | Always show start→end delta, and color the trend (green = improving, red = slipping) |
| Review takes >60 minutes | Default to 7 steps but allow `quick` mode: skip gratitude, compress role check to top 3 roles only |
| User says "nothing happened this week" | Force at least 3 wins. Reframe: "did you eat? sleep? survive Monday?" — wins exist, they just feel small |
| INDEX.md gets corrupted | Rebuild from the per-week `.md` files using a one-liner awk over each file's frontmatter |
| ISO week math off for week 53 / year boundary | Use `date +"%G-W%V"` not custom logic; trust the OS |

## Verification Checklist

- [ ] `~/.hermes/weekly-review/` directory exists
- [ ] `profile.json` initialized with user's roles and review day
- [ ] Each review saved as `{ISO-week}.md` (e.g. `2026-W28.md`)
- [ ] INDEX.md has a row for every completed review
- [ ] 7 steps all completed (or user explicitly skipped a step)
- [ ] Open loops are triaged into destinations, not just listed
- [ ] 3 next-week rocks follow `verb + measurable + deadline` format
- [ ] Auto-pulled metrics are shown with vs.-last-week delta
- [ ] Mood score is recorded as start→end with delta
- [ ] One-word summary captured
- [ ] Optional follow-ups (PDF, flashcards, calendar) are offered but not forced

## Data Sources & Accuracy

| Source | Path | Used for |
|--------|------|----------|
| **Pomodoro Coach** (optional) | `~/.hermes/pomodoro/sessions.jsonl` | Focus hours, pomodoro count, by-tag breakdown |
| **Habit Tracker** (optional) | `~/.hermes/habits/weekly.json` | Completion %, longest streak, broken streaks |
| **Personal Expense** (optional) | `~/.hermes/expenses/log.jsonl` | Total spend, top 3 categories |
| **Sleep Tracker** (optional) | `~/.hermes/sleep/log.jsonl` | Hours/night avg, sleep debt |
| **Personal CRM** (optional) | `~/.hermes/crm/contacts.json` | Touchpoints, dormant contacts, follow-ups due |
| **User input** | chat | Wins, lessons, role scores, rocks, gratitude, one-word |

**Accuracy principles**:
- **Auto-pulled numbers are exact** (they're from local files). Show them with confidence.
- **Self-reported scores (mood, role ratings) are subjective** — show them as-is, don't average across weeks without labeling.
- **One-word summaries are interpretive** — never auto-generate; always user-typed.
- **Open-loop recurrence is computed** by string-matching across files; warn the user that fuzzy matches can miss semantic duplicates ("workout" vs "gym" vs "exercise").
- **Never invent** missed weeks, fake metrics, or hallucinated trends. If a week is missing, show "no data for W26" and continue.
- **Privacy**: all data stays in `~/.hermes/weekly-review/`. The skill never makes network calls; the only external lookups are the local file reads from optional integrations.
