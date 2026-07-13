---
name: pomodoro-coach
description: "Run Pomodoro / deep work sessions from chat — start/stop timers, log focus blocks, track distractions, identify your peak hours, get daily and weekly focus reports. All data stored locally in JSON."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, focus, pomodoro, deep-work, time-management, timer, analytics]
    related_skills: [habit-tracker, sleep-tracker, project-scaffolder]
---

# 🍅 Pomodoro Coach — 番茄钟与深度工作教练

> Start focus sessions by chat, log every block, and learn when you do your best work. 通过对话启动专注时段，记录每一个番茄钟，找到你最高效的工作时段。

---

## Overview

Pomodoro Coach turns Hermes into a personal focus coach. You say *"start a 25-minute focus session on the Q3 report"*, the timer runs, you log distractions and energy at the end, and over time the skill builds a personal profile of **when, what, and how** you focus best. All data lives locally in `~/.hermes/pomodoro/`.

| Capability | Description |
|------------|-------------|
| **Quick start timer** | `start a pomodoro on <task>` — instant 25/5 cycle, no setup |
| **Custom durations** | 15/25/50/90-minute focus blocks, 5/10/15-minute breaks |
| **Task tagging** | Tag sessions with project/category (`work`, `writing`, `coding`, `study`) |
| **Energy & focus rating** | 1–10 self-rating after each block, optional notes |
| **Distraction log** | Log what broke your focus (Slack, email, hunger) for pattern analysis |
| **Streak tracking** | Consecutive days with ≥N pomodoros, weekly/monthly totals |
| **Peak-hour detection** | Find your personal best focus hours (e.g., "9–11am Tuesdays") |
| **Daily / weekly reports** | Total focus time, completed pomodoros, completion rate |
| **Calendar-aware** | Honors existing work blocks, suggests focus windows |
| **Privacy-first** | All data in local JSON, never uploaded |

---

## When to Use

- *"Start a 25-minute pomodoro on the launch deck"*
- *"Begin a 90-minute deep work block"*
- *"Run 4 pomodoros, 15-min breaks"*
- *"End my session — 7/10 focus, 2 distractions"*
- *"How many pomodoros did I do this week?"*
- *"When am I most productive?"*
- *"Show me my focus report"*
- *"Cancel my current timer"*
- *"I'm in a flow state, extend by 15 minutes"*
- *"Set up pomodoro defaults: 50/10"*
- *"今天完成 8 个番茄钟，状态不错"*
- *"What broke my focus most often this month?"*

---

## Core Workflow

### Step 1: Initialize & Set Defaults

On first use, create the data directory and capture the user's preferences:

```bash
mkdir -p ~/.hermes/pomodoro
```

Setup questions (accept defaults if skipped):
1. **Focus duration**: 25 (default), 15, 50, 90, or custom
2. **Break duration**: 5 (default), 10, 15
3. **Long break after**: 4 pomodoros → 20-min break (default)
4. **Auto-start next block?** No (default) — user must confirm, so they can step away
5. **What tags/categories** to track: work, coding, writing, study, admin, personal
6. **Daily target**: 8 pomodoros/day (default)

```json
{
  "profile": {
    "name": "User",
    "focus_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 20,
    "pomodoros_per_cycle": 4,
    "auto_start_next": false,
    "daily_target": 8,
    "tags": ["work", "coding", "writing", "study", "admin"],
    "created_at": "2026-07-12T00:00:00Z"
  },
  "sessions": [],
  "distractions": [],
  "active_timer": null
}
```

**Data files**:
- `~/.hermes/pomodoro/profile.json` — user preferences
- `~/.hermes/pomodoro/sessions.json` — completed focus blocks
- `~/.hermes/pomodoro/distractions.json` — distraction log entries
- `~/.hermes/pomodoro/active.json` — currently running timer (deleted on stop)

### Step 2: Start, Run, and Log Sessions

**Starting a session** — parse the user's request:

```
User: "start a 25-min pomodoro on the Q3 report, tag work"
→ focus_minutes: 25, task: "Q3 report", tag: "work", start_time: now()
```

Use Hermes' `terminal` tool with a background process to run the actual timer — DO NOT block. The user can keep chatting.

**Running a timer** (background):

```bash
# Pseudo: write start time + duration to active.json, then sleep
NOW=$(date -u +%s)
DURATION_MIN=25
END=$(($NOW + $DURATION_MIN * 60))
cat > ~/.hermes/pomodoro/active.json <<EOF
{
  "task": "Q3 report",
  "tag": "work",
  "start_time": "$NOW",
  "end_time": "$END",
  "focus_minutes": 25
}
EOF
# Wait for duration in background, then notify
sleep $((DURATION_MIN * 60)) && echo "🍅 Pomodoro complete: Q3 report"
```

> **CRITICAL**: Always use `terminal(background=true, notify_on_complete=true)` — never block the main session. The user must remain free to chat during a focus block.

**Ending / logging a session** — when the user says "end session" or "done", prompt for:

1. **Focus rating** (1–10): how well did you focus?
2. **Distractions** (optional): anything that broke your flow?
3. **Note** (optional): what did you accomplish?

Append to `sessions.json`:

```json
{
  "id": "pomodoro-2026-07-12-001",
  "task": "Q3 report",
  "tag": "work",
  "start_time": "2026-07-12T09:00:00Z",
  "end_time": "2026-07-12T09:25:00Z",
  "planned_minutes": 25,
  "actual_minutes": 25,
  "focus_rating": 7,
  "distractions": ["Slack message", "Coffee refill"],
  "note": "Finished section 2, blocked on numbers",
  "completed": true
}
```

**Cancelling** — `cancel timer` deletes `active.json` and asks if the user wants to log a partial session.

### Step 3: Analyze & Report

**Daily report** (`show today's focus`):

```
📅 2026-07-12 — Focus Report
─────────────────────────────
🍅 Pomodoros:     6 / 8 target
⏱️  Focus time:   2h 30m
🔥 Streak:        4 days
📊 Avg focus:     7.8 / 10
⚠️  Top distraction: Slack (3x)

By tag:
  work    ████░░░░░░  4
  writing ██░░░░░░░░  2

Time-of-day:
  09–11   ⭐⭐⭐⭐⭐  (avg 8.5)
  14–16   ⭐⭐⭐      (avg 6.2)
```

**Weekly report** — same metrics aggregated over 7 days, with week-over-week deltas.

**Peak-hour analysis** — group sessions by hour-of-day, compute average focus rating per bucket, surface top 3 windows:

```python
# Aggregated over 30+ days
peak_hours = sessions.groupby(sessions.start_time.dt.hour)['focus_rating'].mean()
# Output: 9–11am Tue/Wed highest, 14–16pm lowest
```

Use Hermes' `terminal` to run a small Python script against `sessions.json` for analytics — no external deps.

---

## Example Invocations

### Example 1: Morning focus session

> **User**: start a 25-min pomodoro on the launch deck, tag work
>
> **Agent**:
> ```
> [EXEC] Timer started
> 🍅 Focus block: "launch deck" (work)
> ⏱️  25 minutes — ends at 09:32
> 💡 Tip: close Slack, phone face-down
>
> I won't block — chat with me anytime. I'll notify you when it's done.
> ```

> **User**: *(25 min later, gets a notification)*
>
> **Agent**:
> ```
> 🍅 Block complete! Log it?
> 1. Focus rating (1–10):
> 2. Any distractions?
> 3. Note (optional):
> ```

> **User**: 7, got a slack dm and refilled coffee
>
> **Agent**:
> ```
> [INFO] Logged: 25m @ 7/10, 2 distractions
> 📊 Today: 1/8 pomodoros · 25m focus
> 🔜 Break 5m, then back to it? (y/n)
> ```

### Example 2: Deep work block with extension

> **User**: i need 90 min of deep work on the auth refactor
>
> **Agent**:
> ```
> [EXEC] Deep work mode: 90 minutes
> 🎯 Task: auth refactor
> 🔕 Auto-start next: off (good — protect the block)
> ⏱️  Ends at 14:32
> ```

> **User**: im in flow, extend 15 more
>
> **Agent**:
> ```
> [EXEC] Extended +15 min — ends at 14:47
> 🎉 Flow state logged. Don't break it — keep going.
> ```

> **User**: done. 9/10. hit a clean abstraction
>
> **Agent**:
> ```
> [INFO] Logged: 105m @ 9/10
> ⭐ Excellent focus — top 10% this month
> 📊 Today: 2/8 · 130m total
> 🏆 Streak: 4 days
> ```

### Example 3: Weekly review

> **User**: show me this week's focus report
>
> **Agent**:
> ```
> 📅 Week of 2026-07-07 — Focus Report
> ─────────────────────────────────────
> 🍅 Pomodoros:    34 (vs 28 last week, +21% 🔥)
> ⏱️  Focus time:  14h 10m
> 📊 Avg focus:    7.4 / 10
> 🎯 Hit target:   5/7 days
>
> By tag:
>   coding  ████████░░  18
>   work    ██████░░░░  12
>   writing ██░░░░░░░░   4
>
> ⚠️  Top distractions:
>   1. Slack       12×
>   2. Email        7×
>   3. Phone        4×
>
> ⭐ Peak windows (your data):
>   Tue 09–11   avg 8.7
>   Wed 09–11   avg 8.5
>   Thu 14–16   avg 7.9
>
> 💡 Suggestion: protect Tue/Wed 9–11am for deep work.
> ```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Timer blocks the chat session | Always use `terminal(background=true, notify_on_complete=true)` — never run `sleep` in the foreground |
| User starts a 2nd pomodoro while one is running | Detect existing `active.json`, ask: "you have a session running on X. End it first?" |
| Sessions.json grows huge over months | Archive sessions older than 90 days to `sessions.archive.json` yearly; keep analytics fast |
| User wants to "undo" a logged session | Store sessions with `id`; support `delete session p2026-07-12-003` |
| Time zones: user travels, logs from different zones | Store all timestamps in UTC (`date -u`), convert to local for display |
| User complains timer "drifted" — sleep isn't exact | Use `date` for start/end epoch, compute actual duration; never trust `sleep` alone for accuracy |
| Cron-driven focus reminders | Use `cron-pipeline-builder` to schedule "start pomodoro?" nudge at user's peak hours |
| Battery dies / laptop sleeps mid-session | On resume, detect that `active.json` end_time is in the past — ask user if they want to log partial or discard |
| User wants to track multiple projects simultaneously | Support a single active timer at a time; multi-tasking breaks the pomodoro model — politely refuse |

---

## Verification Checklist

Before claiming the session is logged, verify:

- [ ] `~/.hermes/pomodoro/` directory exists
- [ ] `profile.json` has the user's chosen focus_minutes, break_minutes, daily_target
- [ ] Active timer is launched with `terminal(background=true, notify_on_complete=true)` — NOT blocking
- [ ] `active.json` contains task, tag, start_time (UTC), end_time (UTC), focus_minutes
- [ ] On completion, user is asked for focus rating (1–10) before logging
- [ ] Session is appended to `sessions.json` with a unique `id` (`pomodoro-YYYY-MM-DD-NNN`)
- [ ] Streak is recalculated: any day with ≥1 completed pomodoro extends the streak
- [ ] Daily target progress is reflected: "X/8 pomodoros today"
- [ ] Distractions are logged as a separate array on the session object
- [ ] Analytics queries use Python (stdlib only: `json`, `datetime`, `statistics`, `collections`)
- [ ] No external API calls — all data local
- [ ] When reporting peak hours, require ≥5 sessions in that bucket to surface (avoid noise)

---

## Data Sources & Accuracy

**All data is user-generated, captured live via chat.** No external services.

| Data | Source | Accuracy notes |
|------|--------|----------------|
| Session duration | `date -u +%s` start, `date -u +%s` end | ±1 second, drift-free |
| Focus rating | Self-reported 1–10 | Subjective; aggregate trends over 30+ sessions are reliable |
| Distractions | Self-logged | User may forget — undercount; offer prompt at end of every block |
| Peak hours | Grouped hour-of-day × focus_rating | Need ≥30 sessions for stable patterns; show "needs more data" if <30 |
| Streak | Consecutive days with ≥1 completed pomodoro | Reset at midnight in user's local TZ |
| Weekly completion | `len(sessions in last 7d) / (daily_target × 7)` | Pure division; no inference |

**No third-party APIs.** No telemetry. No upload. The skill never leaves the local machine.

**Calibration tip**: After 30 days, run a Python analysis on `sessions.json` to compare claimed focus ratings against actual output (if the user logs notes). Patterns like "I always rate 9 but produce little" are signal, not noise.
