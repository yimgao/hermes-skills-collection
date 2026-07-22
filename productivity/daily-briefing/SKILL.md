---
name: daily-briefing
description: "Generate a personalized morning briefing — today's calendar, weather, top tasks, habit streak, sleep recovery, watchlist moves, news pulse, focus windows, and a suggested schedule. Cron-ready for 6–7AM delivery, also on-demand by chat."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, morning, briefing, dashboard, daily, planning, automation, orchestrator]
    related_skills: [pomodoro-coach, habit-tracker, sleep-tracker, personal-crm, weekly-review, net-worth-tracker, web-clipper, financial-market-research]
---

# 🌅 Daily Briefing — 个性化晨间简报

> Hermes greets you at 7AM with everything you need to know about today — weather, calendar, top 3 priorities, sleep recovery score, habit streak, watchlist movers, headlines, and an AI-suggested time-blocked schedule. On-demand or cron-delivered.

---

## Overview

`daily-briefing` is a **morning orchestration skill**. It pulls from weather APIs, your local data lake (sleep, habits, expenses, CRM, todos, bookmarks), and live feeds (stocks, news, calendar) to produce one focused report — short enough to read in 60 seconds, smart enough to save 30 minutes of morning tab-opening.

| Capability | Description |
|------------|-------------|
| **Weather snapshot** | Current temp, condition, hourly forecast, rain alert, UV/air quality |
| **Calendar digest** | Today's events in chronological order, conflict detection, prep notes for each |
| **Top 3 priorities** | Pulled from open tasks / last weekly-review "rocks" / yesterday's unfinished pomodoros |
| **Sleep recovery score** | Combine sleep-tracker hours vs 7-day baseline → recommend caffeine & workout intensity |
| **Habit streak status** | Which habits are due today, current streaks, at-risk streaks |
| **Watchlist movers** | Pre-market & after-hours moves for tickers you track |
| **News pulse** | 3–5 headlines from saved RSS / categories you care about |
| **CRM follow-ups** | People in your network due for a touch (7d / 30d / 90d buckets) |
| **Focus window suggestion** | Based on pomodoro peak-hour analysis, suggest 2 protected deep-work blocks |
| **Time-blocked schedule** | Generate an 8-hour suggested day plan, edit-able |
| **Cron-ready** | Schedule for 6:30/7:00/7:30AM and deliver to email/Slack/terminal |
| **Privacy-first** | All personal data stays local; only public APIs (weather, news, stocks) are queried |

---

## When to Use

- *"Morning briefing"*
- *"What's today look like?"*
- *"Give me my daily brief"*
- *"Plan my Tuesday"*
- *"Schedule my morning"*
- *"Brief me — I'm starting work"*
- *"Set up a daily brief at 7AM every weekday"*
- *"Make my brief shorter — only calendar + top 3"*
- *"Add TSLA to my watchlist for the morning brief"*
- *"今天的简报"* / *"给我今天的安排"*
- *"早上 7 点提醒我开会"*（即触发 cron 设置）

---

## Core Workflow

### Step 1 — Gather personal data (local reads)

Hermes reads from your local skill data lakes in parallel. Skip missing ones gracefully.

```bash
# Sleep last night + 7-day baseline
ls ~/.hermes/sleep-tracker/ 2>/dev/null
# Habits status + streaks
ls ~/.hermes/habits/ 2>/dev/null
# Open todos / unfinished pomodoros from yesterday
ls ~/.hermes/pomodoro/ 2>/dev/null
# CRM follow-up due dates
ls ~/.hermes/personal-crm/ 2>/dev/null
# Net-worth snapshot (optional quarterly mention)
ls ~/.hermes/net-worth/ 2>/dev/null
# Web bookmarks you starred
ls ~/.hermes/web-clipper/ 2>/dev/null
```

Read latest entries. Compute:
- **Sleep recovery** = last_night_hours / 7day_avg_hours → score 0–100
- **Habit streak warnings** = streaks ≥7 days that you haven't checked in today
- **CRM hot** = contacts with `next_followup ≤ today`
- **Top 3 candidates** = union of (open todos, yesterday's unfinished pomodoros, weekly-review "rocks" for this week)

### Step 2 — Fetch live data (public APIs)

Run in parallel — these are independent:

```bash
# Weather (free, no key)
curl -s "wttr.in/{CITY}?format=j1" | jq '.current_condition[0] | {temp_C, FeelsLikeC, weatherDesc, humidity}'

# Watchlist — read user's tickers (default: ~/.hermes/daily-briefing/watchlist.json)
# Each ticker: symbol, shares (optional), alert_threshold_pct
# Use yfinance CLI or Stooq CSV: curl -s "https://stooq.com/q/l/?s={ticker}&f=sd2t2ohlcv&h&e=csv"

# News pulse — from web-clipper saved RSS URLs or skill-internal list:
#   - user-provided RSS in ~/.hermes/daily-briefing/feeds.txt
#   - default starter feeds: Hacker News front page, Ars Technica, Bloomberg Markets

# Calendar (if user has google-workspace configured)
#   gws calendar today --json
```

### Step 3 — Synthesize the brief

Use a fixed, scannable layout. **Target: ≤600 words, skimmable in 60s.**

```text
🌅 TUESDAY 21 JUL 2026 · DAY 187

┌── WEATHER ──────────────────────────────────┐
│ Shanghai · 28°C ☁️  feels 31° · 71% humid    │
│ PM rain expected 15:00–18:00. UV 7 (high).   │
│ Air: AQI 68 (moderate).                     │
└─────────────────────────────────────────────┘

┌── TODAY'S CALENDAR (4 events) ─────────────┐
│ 09:00  Standup           [15m, Zoom]        │
│ 11:00  Design review     [60m, prep: deck]  │
│ 14:00  ⚠️  Investor call  [30m]  ← rain comm │
│ 17:30  Gym               [45m]              │
└─────────────────────────────────────────────┘

┌── TOP 3 PRIORITIES ────────────────────────┐
│ 1. Finish Q3 forecast model  (was 50% yesterday)
│ 2. Send Sarah the contract  (CRM due 3d)
│ 3. Reply to Acme proposal   (open 2d)
└─────────────────────────────────────────────┘

┌── RECOVERY & HABITS ───────────────────────┐
│ Sleep: 6.2h (avg 7.1) → RECOVERY 72/100    │
│   💧 Go easy on caffeine, skip hard workout  │
│ Habits: ✓ Meditation  ✓ Workout(M/T/Th)    │
│   ⚠️ Reading streak 12d — log today!        │
└─────────────────────────────────────────────┘

┌── WATCHLIST (3 movers >2%) ───────────────┐
│ NVDA  +3.4%  ($112.40)   pre-market news    │
│ TSLA  −2.1%  ($218.10)   delivery miss      │
│ BTC   +1.8%  ($67,200)                     │
└─────────────────────────────────────────────┘

┌── NEWS PULSE (3) ──────────────────────────┐
│ • Fed minutes signal September pause        │
│ • Stripe IPO rumors resurface               │
│ • Your saved: "YC opens W26 batch"          │
└─────────────────────────────────────────────┘

┌── NETWORK ─────────────────────────────────┐
│ Due today: Sarah K. (last talked 21d)       │
│ This week: 3 contacts need touch            │
└─────────────────────────────────────────────┘

┌── 🎯 SUGGESTED SCHEDULE ───────────────────┐
│ 09:00–09:15  Standup                       │
│ 09:15–11:00  🧠 DEEP WORK: Q3 forecast     │
│             (your peak focus window)        │
│ 11:00–12:00  Design review                 │
│ 12:00–13:00  Lunch + walk                  │
│ 13:00–14:00  🧠 DEEP WORK: contract email │
│ 14:00–14:30  Investor call                 │
│ 14:30–17:00  Acme proposal + admin         │
│ 17:30–18:15  Gym                           │
└─────────────────────────────────────────────┘

⚡ Quick actions:
  • "schedule this" → write to calendar
  • "skip focus blocks" → remove
  • "add TSLA to watchlist"
  • "make this 7 days a week at 7AM"
```

### Step 4 — Persist + (optional) deliver

```bash
# Always save — useful for the day, deletable anytime
mkdir -p ~/.hermes/daily-briefing/
echo "$(date +%Y-%m-%d) $WEEKDAY" >> ~/.hermes/daily-briefing/history.tsv
# Move generated brief to:
~/.hermes/daily-briefing/$(date +%Y-%m-%d).md
```

For cron delivery, hand off to `cron-pipeline-builder`:

```bash
# ~/.hermes/cron/daily-briefing.sh
#!/usr/bin/env bash
hermes -s daily-briefing <<< "Generate today's morning brief and print it"
# or send via email:
# hermes -s email-composer <<< "Send my brief to me@x.com as plain text"
```

### Step 5 — Learn from feedback (week 2+)

After 7 days, ask: *"How accurate were your peak-focus suggestions? Want to recalibrate?"*
Persist: `~/.hermes/daily-briefing/feedback.jsonl` with `{date, weather_used, schedule_followed_pct, top3_completed, sleep_score}`. Use this for monthly personalization.

---

## Example Invocations

### Example 1 — First run, on-demand
> **User:** Morning briefing
>
> **Agent:**
> 1. Detects no config yet at `~/.hermes/daily-briefing/` → asks 3 onboarding questions in one shot:
>    - "City for weather?" (default: geolocate IP → Shanghai)
>    - "Ticker watchlist?" (default: empty)
>    - "Calendar source?" (none / `gws calendar` / iCloud CalDAV)
> 2. Writes `~/.hermes/daily-briefing/config.json`
> 3. Pulls sleep from sleep-tracker, habits, todos, weather, news
> 4. Prints the scannable brief above in ≤600 words

### Example 2 — Cron daily delivery
> **User:** Give me my daily brief at 7AM every weekday, deliver to my email
>
> **Agent:**
> 1. Writes `~/.hermes/cron/daily-briefing.sh` wrapper (uses skill's content)
> 2. Registers cron: `0 7 * * 1-5 ~/.hermes/cron/daily-briefing.sh`
> 3. First run is Monday 7:00 → brief lands in inbox before you open your eyes
> 4. Daily failure retries up to 3× via cron-pipeline-builder watchdog

### Example 3 — Pre-meeting micro-brief
> **User:** Brief me — I have a 14:00 investor call about Series A
>
> **Agent:** Compresses the morning brief to one calendar-focused variant:
> - Today's remaining events + prep needed
> - 3-line company research on the investor (LinkedIn headline, fund stage, recent investments)
> - Talking points from your last weekly-review "open loop"
> - Output as 5-screen swipe-card on phone

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Brief is too long** — 1500 words, takes 5min to read | Enforce hard cap: ≤600 words; ruthlessly cut news to 3 headlines; collapse weather to one line; kill any "motivational quote" filler |
| **Brief is too noisy** — 12 bullet sections | Default to 6 sections (Weather, Calendar, Top 3, Recovery, Watchlist, Schedule). Let user opt INTO extras via config |
| **Missing local skill data** — first run, no sleep/habits | Don't error. Just skip section + label "(no data yet — set up sleep-tracker to enable)". Brief still works |
| **Weather API flakes** — wttr.in rate-limit | Add `WTTR_TIMEOUT=3` env var; cache by hour with `mkdir -p ~/.cache/wttr && curl -o ...cache/$DATE-$HOUR.json`; fall back to local date |
| **Calendar pulls empty** — `gws calendar` not configured | Show "no calendar source configured — paste today's events?" + accept paste-in as substitute |
| **Watchlist stale** — user changed tickers last week but config not updated | At end of brief, show inline reminder: *"Update watchlist? `watchlist edit`"* |
| **Cron fires while you're traveling in another TZ** — briefing shows wrong city weather | Cron job reads `~/.hermes/daily-briefing/config.json` → if `travel_mode=true`, asks "set new city?" or auto-IP geolocates once per day |
| **Brief regenerated twice** — overlapping cron jobs | Use `flock -n ~/.lock/daily-briefing.lock` in wrapper script to prevent overlap |
| **Noisy news at 7AM** — finance/alarmist headlines ruin the morning | Maintain allow-list in `~/.hermes/daily-briefing/categories.json`; default excludes "opinion", "rumor", "meme stocks" |
| **First-time setup friction** — 8 questions blocks adoption | Reduce to 3 Qs (city, watchlist, calendar). Defer all else to "edit later" |
| **News sources pull paywalled content** | Catch 403, show only the headline from RSS, link out, do not attempt login |

---

## Verification Checklist

Before delivering any brief, confirm:

- [ ] Date, weekday, day-of-year correct
- [ ] Weather retrieved within last 30 min (cache check)
- [ ] All calendar events for *today in user's TZ* listed in chronological order
- [ ] Top 3 priorities are non-trivial (not "check email" filler)
- [ ] Sleep recovery uses last night (not 2-nights-ago)
- [ ] Watchlist filters by user's alert threshold (default ±2%)
- [ ] News headlines are from user's allow-listed sources
- [ ] Suggested schedule respects all calendar events (no overlaps)
- [ ] Total word count ≤600
- [ ] Cron deliveries include date in subject: `[Brief] Tue 21 Jul`
- [ ] Config file writable; brief persisted to `~/.hermes/daily-briefing/YYYY-MM-DD.md`
- [ ] Quick-actions block present at end so user can iterate in one turn

---

## Data Sources & Accuracy

| Source | What it provides | Frequency | Reliability |
|--------|------------------|-----------|-------------|
| **wttr.in** | Current + hourly weather | Every brief, cached 60min | High — server-backed by worldweatheronline; ±1°C typical |
| **Stooq / Yahoo Finance** | Watchlist quotes | Every brief, cached 15min during market hours | Medium — 15-min delayed free tier; refresh via yfinance for real-time if configured |
| **local sleep-tracker JSON** | Sleep hours, quality | Updated nightly by user | High — user-controlled; only as accurate as last entry |
| **local habit-tracker JSON** | Streaks, due-today habits | Real-time | High |
| **local pomodoro-coach JSON** | Yesterday's focus completion, peak hours | Real-time | High |
| **local personal-crm JSON** | Follow-up due dates | Real-time | High — depends on user logging |
| **Google Calendar via `gws`** | Today's events | Live | High — requires OAuth at setup |
| **User-saved RSS / web-clipper** | News pulse, saved articles | Live at run time | Varies by source quality |
| **investor/contact lookup** | 3-line background for pre-meeting brief | Live at run time | Medium — LinkedIn headlines only, no scraping |

**Privacy posture:** All personal data is on disk in `~/.hermes/`. Public APIs (weather, finance, news) are queried without credentials in default config. Calendar OAuth is opt-in and scoped read-only. Brief output is never transmitted off the user's machine unless an explicit `deliver-to: email` is configured.
