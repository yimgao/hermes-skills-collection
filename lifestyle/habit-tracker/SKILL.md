---
name: habit-tracker
description: "Build and track daily habits — define goals, check in daily, monitor streaks, get weekly summaries. All data stored locally in JSON."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, habits, productivity, tracking, streaks, self-improvement]
    related_skills: [fitness-planner, study-planner, personal-expense-tracker]
---

# 🎯 Habit Tracker — 习惯追踪器

> Define daily habits, check in each day, track streaks, and get weekly progress summaries. 定义每日习惯，每日打卡，追踪连续天数，每周获取进展报告。

---

## Overview

This skill turns Hermes into a personal habit tracker. You describe habits you want to build — from "drink 8 glasses of water" and "read 30 minutes" to "leetcode 1 problem" and "meditate 10 minutes" — and Hermes manages the tracking, streak calculation, and progress reporting. All data is stored in a local JSON file under `~/.hermes/habits/`, zero external dependencies.

| Capability | Description |
|------------|-------------|
| **Define habits** | Add new habits with description, frequency, and target |
| **Daily check-in** | Log completion with timestamp |
| **Streak tracking** | Auto-calculate current and longest streaks |
| **Weekly summary** | Aggregated report of completion rate, streaks, trend |
| **Habit management** | List, pause, archive, or delete habits |
| **Data persistence** | All data local in `~/.hermes/habits/habits.json` |

---

## When to Use

- *"I want to start tracking my daily habits"*
- *"I ran 5km today — log it"*
- *"Show me my habit streak"*
- *"What habits am I currently tracking?"*
- *"Give me my weekly habit report"*
- *"I want to add a habit: write 500 words every day"*
- *"Pause my 'morning yoga' habit for this week"*

---

## Core Workflow

### Step 1: Initialize & Define Habits

The first time the user mentions habits, check if `~/.hermes/habits/habits.json` exists. If not, initialize the file:

```bash
mkdir -p ~/.hermes/habits
```

The JSON schema for `habits.json`:

```json
{
  "habits": [
    {
      "id": "hab_001",
      "name": "晨跑 5km",
      "description": "每天早晨跑步5公里",
      "frequency": "daily",
      "target": 1,
      "unit": "次",
      "created_at": "2026-06-24T08:00:00Z",
      "status": "active",
      "logs": {
        "2026-06-24": true,
        "2026-06-23": true,
        "2026-06-22": false
      },
      "current_streak": 2,
      "longest_streak": 7
    }
  ],
  "metadata": {
    "version": 1,
    "last_updated": "2026-06-24T18:00:00Z"
  }
}
```

When the user asks to add a habit, extract from natural language:
- **name**: short name
- **description**: optional details
- **frequency**: daily / weekly / weekday / weekend
- **target**: number per period (default: 1)
- **unit**: unit name (minute, km, pages, etc.)

Generate a unique ID with `date +%s` and write to file.

### Step 2: Daily Check-in

When the user logs a habit today:

1. Parse the habit name or ID from their message
2. Get today's date: `date -u +"%Y-%m-%d"`
3. Set `logs["YYYY-MM-DD"] = true` for that habit
4. Recalculate streaks:
   - **current_streak**: count consecutive `true` going backward from today
   - **longest_streak**: max(current_streak, previous longest_streak)
5. Write back to `habits.json`

Use `jq` for in-place JSON manipulation:

```bash
# Mark habit "hab_001" as done today
TODAY=$(date -u +"%Y-%m-%d")
jq --arg id "hab_001" --arg date "$TODAY" '
(.habits[] | select(.id == $id) | .logs[$date]) = true
' ~/.hermes/habits/habits.json > /tmp/habits_tmp.json && mv /tmp/habits_tmp.json ~/.hermes/habits/habits.json
```

Then recalculate streaks with a Python one-liner:

```python
python3 -c "
import json, sys
with open('$HOME/.hermes/habits/habits.json') as f:
    data = json.load(f)
for h in data['habits']:
    if h['id'] != 'hab_001': continue
    dates = sorted(h['logs'].keys(), reverse=True)
    cur = 0
    for d in dates:
        if h['logs'][d]: cur += 1
        else: break
    h['current_streak'] = cur
    h['longest_streak'] = max(cur, h.get('longest_streak', 0))
data['metadata']['last_updated'] = __import__('datetime').datetime.utcnow().isoformat() + 'Z'
with open('$HOME/.hermes/habits/habits.json','w') as f:
    json.dump(data, f, indent=2)
"
```

### Step 3: Reports & Insights

**List all habits** — read and format:

```bash
jq -r '.habits[] | [.id, .name, .status, (.current_streak|tostring) + " days", (.logs|length|tostring) + " total"] | @tsv' ~/.hermes/habits/habits.json | column -t -s $'\t'
```

**Weekly summary** — calculate last 7 days completion rate:

```python
python3 -c "
import json, sys
from datetime import datetime, timedelta
with open('$HOME/.hermes/habits/habits.json') as f:
    data = json.load(f)
today = datetime.utcnow().date()
week_ago = today - timedelta(days=7)
print('📊 Weekly Habit Report')
print('='*40)
for h in data['habits']:
    if h['status'] != 'active': continue
    done = sum(1 for d in h['logs'] if week_ago <= datetime.strptime(d, '%Y-%m-%d').date() <= today and h['logs'][d])
    total = sum(1 for d in h['logs'] if week_ago <= datetime.strptime(d, '%Y-%m-%d').date() <= today)
    rate = f'{done/total*100:.0f}%' if total > 0 else 'N/A'
    print(f\"  {h['name']}: {done}/{total} ({rate}) 🔥 {h['current_streak']} day streak\")
"
```

**Motivational message** — if a habit has a streak >= 7 days, add a "keep going!" note. If a habit was missed 3+ days this week, suggest adjusting the target.

---

## Example Invocations

### Example 1: Adding a habit and checking in

**User:**
> I want to start tracking my reading habit — read 30 pages of a book every day. Call it "Daily Reading".

**Agent:**
```
[INIT] Initializing habit tracker...
Added habit: Daily Reading
  📖 Target: 30 pages daily
  Status: active
  Streak: 0 days

Tip: Check in daily with "read 30 pages today" or "log Daily Reading".
```

**User (next day):**
> Read my 30 pages today.

**Agent:**
```
✅ Logged "Daily Reading" for 2026-06-25
🔥 Current streak: 1 day
🏆 Longest streak: 1 day
```

### Example 2: Weekly review

**User:**
> How are my habits this week?

**Agent:**
```
📊 Weekly Habit Report (Jun 18 — Jun 24)
========================================
  Daily Reading: 5/7 (71%) 🔥 1 day streak
  Morning Yoga: 3/7 (43%) 🔥 3 day streak
  Water 8 Glasses: 7/7 (100%) 🔥 7 day streak ✅

💡 Morning Yoga: missed 4 days this week. Want to adjust target to 3x/week?
💪 Water 8 Glasses: 7-day streak! Keep it up!
```

### Example 3: Managing habits

**User:**
> Pause my "Morning Yoga" habit for this week, I'm traveling. Also show me all my habits.

**Agent:**
```
⏸️ Paused "Morning Yoga" (resume with "resume Morning Yoga")

📋 All Habits
ID        Name             Status    Streak     Total Logs
hab_001   Daily Reading    active    1 days     8 total
hab_002   Morning Yoga     paused    3 days     15 total
hab_003   Water 8 Glasses  active    7 days     30 total
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User says "log it" without specifying which habit | Ask: "Which habit do you want to log? Your active habits are: Daily Reading, Water 8 Glasses" |
| User logs a habit from yesterday | Use `date -d "yesterday"` to get yesterday's date and log accordingly |
| JSON file gets corrupted | Keep a backup: `cp habits.json habits.json.bak` before each write; on JSON parse error, restore from backup |
| Habit name too vague ("workout") | Ask clarifying questions: "What kind of workout? How many minutes? How many times per week?" |
| User wants to backfill multiple days | Accept range: "log Daily Reading for June 20-23" → iterate and mark all dates |
| Streak breaks due to timezone issues | Always use UTC dates; the "day" boundary is midnight UTC |
| Too many habits reduce tracking accuracy | Recommend max 3-5 active habits at a time; encourage archiving completed or inactive habits |

---

## Verification Checklist

- [ ] `~/.hermes/habits/habits.json` is created on first use
- [ ] Adding a habit generates a unique ID and stores it correctly
- [ ] Daily check-in records the correct date and recalculates streaks
- [ ] Pausing a habit excludes it from weekly summaries but preserves data
- [ ] Weekly summary shows completion rate, streak, and motivational tips
- [ ] Multiple check-ins on the same day for the same habit don't double-count
- [ ] Longest streak is correctly tracked even after current streak breaks
- [ ] Deleting a habit removes it entirely (or archives it with `status: archived`)

---

## Data Sources & Accuracy

- **All data is user-provided** — there are no external data sources. The skill relies entirely on the user's honesty in logging habits.
- **Time is UTC-based** — streaks reset at midnight UTC. If the user crosses timezones, advise them of the UTC boundary.
- **Data is local** — stored at `~/.hermes/habits/habits.json`. No data is sent to any external service.
- **Accuracy of streak calculation**: streaks are recalculated from scratch each time a log is added, ensuring no cumulative drift in streak counts.
