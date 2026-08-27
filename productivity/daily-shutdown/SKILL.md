---
name: daily-shutdown
description: "Run a 2-minute end-of-day shutdown ritual from chat — close open loops, score the day, capture tomorrow's first move, log a 1-line gratitude, surface unfinished pomodoros and follow-ups. Pairs with daily-briefing. Local JSON, cron-ready for 5:30/6/10PM delivery."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, evening, shutdown, reflection, ritual, journaling, daily, automation, gtd]
    related_skills: [daily-briefing, pomodoro-coach, weekly-review, habit-tracker, personal-crm, inbox-triage, decision-journal]
---

# 🌙 Daily Shutdown — 2 分钟下班仪式

> End every day with the discipline of a fighter pilot: close the loops, score the day, write tomorrow's first move. Two minutes today beats two hours tomorrow figuring out where you left off.

---

## Overview

`daily-shutdown` is the **mirror image of `daily-briefing`**. Where the morning brief tells you what today *looks like*, the shutdown tells you what today *was* — and writes tomorrow's opening move into a file your future self will thank you for.

The ritual is deliberately short (2 minutes, 5 questions). Its power is **consistency**, not depth. Done daily, it builds:
- A searchable day-by-day log of what got done
- A rolling "tomorrow's first move" file that the morning brief can read
- Open-loop awareness (you stop forgetting things at midnight)
- A daily energy score to spot burnout weeks early
- One-line gratitude per day (proxies mood, low friction)

| Capability | Description |
|------------|-------------|
| **Open-loop capture** | What didn't get finished today? Carry it forward or drop it |
| **Daily score 1–10** | Energy + output score with optional 1-line reason |
| **Top-3 done list** | Three wins, no matter how small (kills the "nothing happened" feeling) |
| **Tomorrow's first move** | One specific next action, written so Monday-you can read it |
| **Gratitude line** | Single-line appreciation; logged for monthly review |
| **Follow-up surface** | Pulls overdue items from personal-crm & inbox-triage |
| **Pomodoro reflection** | Today's focus minutes vs daily target |
| **Habit check-in** | Which habits were hit/missed today |
| **Auto-archive** | 30-day rolling file, older days compressed to weekly summary |
| **Cron-ready** | Schedule for 5:30PM / 6PM / 10PM — or run on-demand |
| **Privacy-first** | All data local JSON; nothing leaves your machine |

---

## When to Use

- *"Shutdown"* / *"End my day"*
- *"Daily shutdown"* / *"Wrap up today"*
- *"5pm ritual"* / *"Closing time"*
- *"Score my day"* / *"Day score"*
- *"What should I do tomorrow first?"*
- *"Log today's wins"*
- *"下班了" / "收工" / "一天结束了"*
- *"Set a cron to run my shutdown at 6pm every weekday"*
- *"Show me my shutdowns this week"* (queries past logs)
- *"What's been on my gratitude list lately?"*

**Not for:** morning planning (use `daily-briefing`), weekly retrospective (use `weekly-review`), project debriefs longer than 5 minutes (use `meeting-minutes-generator` or `decision-journal`).

---

## Core Workflow

### Step 1 — Init or load today's shutdown file

Create the data directory on first run; load today's file if it exists (idempotent — re-running the shutdown updates the same file).

```bash
DATA=~/.hermes/data/daily-shutdown
mkdir -p "$DATA/logs" "$DATA/weekly"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%H:%M)
FILE="$DATA/logs/$TODAY.json"

# Initialize today's file with defaults if missing
if [ ! -f "$FILE" ]; then
  cat > "$FILE" <<JSON
{
  "date": "$TODAY",
  "shutdown_at": null,
  "day_score": null,
  "score_reason": null,
  "top_3_done": [],
  "open_loops_carried": [],
  "open_loops_dropped": [],
  "tomorrow_first_move": null,
  "gratitude": null,
  "energy_morning": null,
  "energy_evening": null,
  "pomodoro_minutes": null,
  "habits_hit": [],
  "habits_missed": [],
  "follow_ups_overdue": 0,
  "raw_notes": ""
}
JSON
fi
```

### Step 2 — Pull context from partner skills (parallel reads)

Read whatever data exists; gracefully skip missing files. This is the "smart" part of the shutdown — the agent answers most questions automatically before asking the user.

```bash
# Pomodoro data (if exists)
POMO=$(jq -r --arg t "$TODAY" '.days[$t] // null' \
  ~/.hermes/data/pomodoro-coach/state.json 2>/dev/null)

# Habit tracker
HABITS=$(jq -r --arg t "$TODAY" '.days[$t] // null' \
  ~/.hermes/data/habit-tracker/state.json 2>/dev/null)

# Inbox follow-ups (count of messages with reply_later > 3 days old)
FOLLOWUPS=$(jq '[.messages[] | select(.bucket=="reply_later") | \
  select((.added_at | fromdate) < (now - 259200))] | length' \
  ~/.hermes/data/inbox-triage/state.json 2>/dev/null)

# Open pomodoros that didn't close
OPEN_POMOS=$(jq '[.days[$TODAY].blocks[]? | select(.status=="open")] | length' \
  ~/.hermes/data/pomodoro-coach/state.json 2>/dev/null || echo 0)

echo "pomodoro_minutes: $POMO"
echo "open_pomodoros: $OPEN_POMOS"
echo "follow_ups_overdue: $FOLLOWUPS"
```

Then ask the user **at most 5 questions** (in this exact order — the order matters, from easiest to hardest):

1. **"Top 3 done today?"** (free text or list)
2. **"Anything open to carry forward or drop?"** (free text, agent suggests drops from open loops)
3. **"Day score 1–10, and why?"** (single number + optional short reason)
4. **"Tomorrow's first move?"** (one specific action, ideally ≤15 min)
5. **"One-line gratitude?"** (single line)

If the user just types *"shutdown"* with no detail, run a **fast mode** (1 minute): write score=7, top-3=["(skipped — fast mode)"], tomorrow="(review yesterday's unfinished)", gratitude="(skipped)". The point is the ritual, not perfection.

### Step 3 — Write the shutdown file

```bash
# Build JSON from user responses (agent does this conversationally)
cat > "$FILE" <<JSON
{
  "date": "$TODAY",
  "shutdown_at": "$NOW",
  "day_score": ${SCORE:-null},
  "score_reason": "${REASON//\"/\\\"}",
  "top_3_done": [$(printf '"%s",' "${DONE[@]}" | sed 's/,$//')],
  "open_loops_carried": [$(printf '"%s",' "${CARRY[@]}" | sed 's/,$//')],
  "open_loops_dropped": [$(printf '"%s",' "${DROP[@]}" | sed 's/,$//')],
  "tomorrow_first_move": "${NEXT//\"/\\\"}",
  "gratitude": "${GRAT//\"/\\\"}",
  "energy_morning": ${EM:-null},
  "energy_evening": ${EE:-null},
  "pomodoro_minutes": ${POMO_MIN:-null},
  "habits_hit": [$(printf '"%s",' "${HIT[@]}" | sed 's/,$//')],
  "habits_missed": [$(printf '"%s",' "${MISS[@]}" | sed 's/,$//')],
  "follow_ups_overdue": ${FOLLOWUPS:-0},
  "raw_notes": "${NOTES//\"/\\\"}"
}
JSON

echo "✅ Shutdown logged: $FILE"
```

### Step 4 — Update tomorrow's "first move" pointer

Maintain a separate pointer file the morning brief can read:

```bash
cat > ~/.hermes/data/daily-shutdown/tomorrow.json <<JSON
{
  "for": "$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d 'tomorrow' +%Y-%m-%d)",
  "first_move": "${NEXT//\"/\\\"}",
  "carried_open_loops": [$(printf '"%s",' "${CARRY[@]}" | sed 's/,$//')]
}
JSON
```

If `daily-briefing` is installed, it should pick this up via its related_skills list and surface it as the #1 morning priority.

### Step 5 — Roll up weekly summary (Sunday only)

If today is Sunday (`date +%u == 7`), run an automatic rollup:

```bash
if [ "$(date +%u)" = "7" ]; then
  WEEK_FILE="$DATA/weekly/$(date +%Y-W%V).md"
  {
    echo "# Week $(date +%Y-W%V) — Daily Shutdown Summary"
    echo
    echo "## Day scores"
    jq -r '.days[].day_score // empty' ~/.hermes/data/daily-shutdown/state.json 2>/dev/null \
      | tail -7
    echo
    echo "## Top carries (most-repeated open loops)"
    jq -s '[.[].open_loops_carried[]?] | group_by(.) | sort_by(-length) | .[0:5][] | "\(.[0]) — \(length) days"' \
      $DATA/logs/*.json 2>/dev/null
    echo
    echo "## Gratitude samples"
    jq -r '.gratitude // empty' $DATA/logs/*.json 2>/dev/null | tail -7
  } > "$WEEK_FILE"
  echo "📅 Weekly summary: $WEEK_FILE"
fi
```

### Step 6 — (Optional) Set up a cron

```bash
hermes cron add daily-shutdown \
  --schedule "30 17 * * 1-5" \
  --prompt "Run my daily shutdown" \
  --destination terminal
```

Common schedules:
- `"30 17 * * 1-5"` — 5:30PM weekdays (pre-commute home)
- `"0 18 * * *"` — 6PM every day
- `"0 22 * * *"` — 10PM every day (deep-night reflective version)

---

## Example Invocations

### Example 1 — First-time shutdown with full context

> **User:** Shutdown
>
> **Agent:** 🌙 It's `2026-08-26 17:34`. Quick context I pulled:
> • Pomodoro: 142 min focused today (target was 180 — slightly under)
> • Open loops from inbox-triage: 4 messages waiting >3 days
> • Habits hit: gym, reading, hydrate. Missed: meditate.
> • Last shutdown score: 8
>
> 5 questions, ~2 min:
> 1. **Top 3 done?** — You wrote back Sarah, shipped the v2 brief, and ran 4km.
> 2. **Open loops to carry / drop?** — Carry: Stripe contract review (deadline Fri). Drop: rewrite legacy docs (not this quarter).
> 3. **Day score?** — 7. Solid output but two meetings killed flow.
> 4. **Tomorrow's first move?** — 9AM: send Stripe redline to legal (≤15 min).
> 5. **Gratitude?** — Sunset on the way home was absurd.
>
> Logging…
> ✅ `~/.hermes/data/daily-shutdown/logs/2026-08-26.json` written
> ✅ `tomorrow.json` updated — `daily-briefing` will surface the Stripe redline at 7AM
> 📊 Week-35 average score: 7.4 (last 7 days)

### Example 2 — Fast mode (no detail)

> **User:** shutdown
>
> **Agent:** 🌙 Fast shutdown? I'll log: score 7, no detail, tomorrow TBD. Type "real" for full mode, or just say "done" to commit.
>
> **User:** done
>
> **Agent:** ✅ Logged fast shutdown. `daily-briefing` will prompt you tomorrow at 7AM for a real one.

### Example 3 — Looking back

> **User:** Show me my shutdowns this week
>
> **Agent:**
>
> | Day | Score | First move (next AM) | Gratitude |
> |---|---|---|---|
> | Mon | 8 | Pitch deck outline | First coffee in the garden |
> | Tue | 6 | Investor email reply | Lunch with Maya |
> | Wed | 9 | Stripe redline | Team shipped the v2 |
> | Thu | 7 | Spec review | Long run in the rain |
> | Fri | ? | — | — |
>
> Average: 7.5. Energy dipped Tue (lowest score) — want to see what was different?

### Example 4 — Setting up the cron

> **User:** Run my shutdown every weekday at 5:30pm
>
> **Agent:** ✅ Added cron: `daily-shutdown` at `30 17 * * 1-5`, delivered to terminal. First run: tomorrow 5:30PM. Skip days: weekends (use `weekly-review` Sunday instead).

---

## Common Pitfalls

| Problem | Solution |
|---|---|
| Shutdown takes 20 minutes — it's not the point | Strict 2-min cap. Use `weekly-review` for depth. |
| User has no energy for 5 questions at 6PM | **Fast mode**: log everything as null/empty, skip the ritual, return tomorrow |
| Tomorrow's first move is vague ("work on project X") | Push for one **specific** action: "Send Sarah the v2 by 9:30AM, 5 min." |
| Open loops pile up forever | Cap at 5 carries. Anything older than 14 days → drop or escalate to a project. |
| Day score is inflated (always 8–10) | Look at energy_morning vs energy_evening delta. A 3+ drop = real stress signal. |
| Gratitude becomes rote ("family, health, work") | Force specifics: *the exact thing*, today. "Sarah's laugh at lunch" beats "friends." |
| Forgetting to set up the cron | Default: prompt user to schedule it on first shutdown. Don't be shy. |
| Data lives only locally — what if disk dies? | Recommend `~/hermes-sync` rsync to encrypted external; or skip if user has Time Machine. |
| Running shutdown twice in one day | Idempotent — re-running overwrites same date file. Confirm before destructive overwrite if entries differ. |
| Confusing shutdown with weekly review | Shutdown = daily 2-min. Weekly = 30-min Sunday GTD. Different cadence, different depth. |
| Tracking "what I should have done" vs "what I did" | Top-3 is **dones**, not todos. The discipline is celebrating completion. |

---

## Verification Checklist

Before claiming shutdown worked, verify:

- [ ] `~/.hermes/data/daily-shutdown/logs/YYYY-MM-DD.json` exists for today
- [ ] File contains `shutdown_at` field with HH:MM timestamp
- [ ] `day_score` is a number 1–10 (or null for fast mode)
- [ ] `top_3_done` has 1–3 items
- [ ] `tomorrow_first_move` is non-empty for non-fast mode
- [ ] `tomorrow.json` written with `first_move` field
- [ ] If Sunday: weekly rollup file written to `weekly/YYYY-Www.md`
- [ ] Idempotent: re-running same day doesn't crash, doesn't duplicate
- [ ] No external API calls; only local file reads from partner skills
- [ ] Cron schedule registered (if user opted in)

---

## Data Sources & Accuracy

This skill is **almost entirely local-first** by design. The only "data sources" are:

1. **User-provided responses** — the 5 ritual questions. Treated as ground truth.
2. **Local partner-skill JSON files** — read-only, optional:
   - `~/.hermes/data/pomodoro-coach/state.json` — today's focus minutes, open blocks
   - `~/.hermes/data/habit-tracker/state.json` — habit hit/miss
   - `~/.hermes/data/inbox-triage/state.json` — overdue reply count
   - `~/.hermes/data/personal-crm/state.json` — overdue touch-ups (not yet pulled in)
3. **Local clock** — `date` command for timestamp; no NTP needed.

**Accuracy notes:**
- **Day score is subjective** — it's a mood/output proxy, not a measurement. Use trend, not absolute values.
- **Carry/drop accuracy** — depends on user honesty. The skill surfaces what was logged; it doesn't infer from calendar.
- **Weekly rollup** is purely arithmetic over local files. 100% reproducible.
- **No telemetry leaves the machine.** The agent never sends shutdown data anywhere unless user explicitly configures a sync destination.

---

## Pairing Matrix

| Pairs with | How |
|---|---|
| `daily-briefing` | Morning brief pulls `tomorrow.json`'s `first_move` and surfaces it as priority #1 |
| `pomodoro-coach` | Reads today's focus minutes; suggests score calibration if minutes were unusually low/high |
| `habit-tracker` | Pre-fills habits_hit/missed so user just confirms |
| `weekly-review` | Sunday shutdown hands off the week; weekly-review reads 7 days of scores + gratitudes |
| `inbox-triage` | Surfaces overdue reply count so user notices creeping debt |
| `personal-crm` | (Future) Pulls overdue touch-ups; "you haven't talked to Sarah in 47 days" |

---

## License

MIT — fork, modify, sell. If you make it better, send a PR.