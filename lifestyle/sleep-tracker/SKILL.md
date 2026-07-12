---
name: sleep-tracker
description: "Track sleep duration, quality, and patterns from chat — log bedtime/wake time, rate sleep quality, correlate with mood/energy/caffeine, get weekly reports and personalized sleep hygiene tips. All data stored locally."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, sleep, health, wellness, tracking, analytics, self-improvement]
    related_skills: [habit-tracker, fitness-planner, personal-crm]
---

# 😴 Sleep Tracker — 睡眠追踪与分析器

> Log your sleep by chat, get data-driven insights on what affects your rest, and receive personalized sleep hygiene recommendations. 用对话记录你的睡眠，用数据找影响睡眠的因素，获得个性化睡眠建议。

---

## Overview

This skill turns Hermes into a personal sleep coach and analyst. You describe how you slept ("I slept from 11pm to 6:45am, woke up twice, felt tired") and Hermes logs it, correlates sleep quality with daily factors (caffeine, exercise, screen time, stress), tracks trends over weeks and months, and surfaces actionable insights grounded in sleep science. All data lives locally in `~/.hermes/sleep/`.

| Capability | Description |
|------------|-------------|
| **Sleep logging** | Natural-language entry: bedtime, wake time, quality rating, awakenings, naps |
| **Duration calculation** | Auto-compute total sleep time, time in bed, sleep efficiency |
| **Quality scoring** | 1–10 subjective rating + composite quality score (duration + awakenings + rating) |
| **Daily factors** | Log caffeine, alcohol, exercise, screen time, stress, meals before bed |
| **Trend analysis** | 7 / 30 / 90-day rolling averages, week-over-week deltas |
| **Correlation engine** | Find which factors most correlate with poor sleep for *you* personally |
| **Sleep debt** | Track cumulative sleep debt vs target (e.g., 8h baseline) |
| **Weekly report** | Average duration, quality, top disruptors, suggested fixes |
| **Sleep hygiene tips** | Personalized advice from your own data patterns |
| **Privacy-first** | All data local in JSON, never uploaded |

## When to Use

- *"I went to bed at 11:30 and woke up at 7am, felt rested"*
- *"Log my sleep: ~10pm–6am, woke up 3 times, quality 4/10"*
- *"Show me this week's sleep stats"*
- *"What was my average sleep duration last month?"*
- *"How does caffeine affect my sleep?"*
- *"Am I in sleep debt?"*
- *"Give me my sleep report"*
- *"I want to start tracking my sleep"*
- *"Help me fix my sleep schedule"*
- *"为什么我总是睡不好？"*

## Core Workflow

### Step 1: Initialize & Set Targets

On first mention, create the data directory and ask the user 3 setup questions:

```bash
mkdir -p ~/.hermes/sleep
```

Setup questions (use defaults if user skips):
1. **Sleep goal**: how many hours per night? (default: 8)
2. **Bedtime window**: when do you *want* to be asleep? (default: 23:00–07:00)
3. **What to track**: defaults to caffeine, exercise, screen time, stress, alcohol. User can add custom.

```json
{
  "profile": {
    "name": "User",
    "sleep_goal_hours": 8.0,
    "bedtime_target": "23:00",
    "wake_target": "07:00",
    "created_at": "2026-07-11T00:00:00Z",
    "tracked_factors": ["caffeine", "exercise", "screen_time", "stress", "alcohol"]
  },
  "logs": [],
  "factors": [],
  "insights": []
}
```

**Data files**:
- `~/.hermes/sleep/profile.json` — user settings
- `~/.hermes/sleep/sleep_log.json` — daily sleep entries
- `~/.hermes/sleep/factor_log.json` — daily factor entries
- `~/.hermes/sleep/insights.json` — generated insights cache

### Step 2: Log Sleep via Natural Language

Parse the user's freeform sentence and extract:

- **Bedtime** (when they got into bed / fell asleep)
- **Wake time** (when they woke up)
- **Awakenings** (count or none)
- **Quality rating** (1–10 or qualitative: terrible/okay/great)
- **Notes** (anything else: dreams, restlessness, room temp)

Example parses:

```
"I slept 11pm–6:45am, woke twice, quality 6"
→ bedtime: 23:00, wake: 06:45, duration: 7h 45m, awakenings: 2, quality: 6

"Bad night, ~4 hours, felt terrible"
→ duration: 4h, quality: 2, note: "felt terrible"

"Slept like a baby, 8 hours straight"
→ duration: 8h, awakenings: 0, quality: 9
```

Default date = today. If user says "yesterday" or "last night", subtract one day. If time spans past midnight, handle correctly (23:30 → 07:00 = 7h 30m).

Auto-compute and store:

```json
{
  "date": "2026-07-11",
  "bedtime": "23:00",
  "wake_time": "06:45",
  "duration_minutes": 465,
  "awakenings": 2,
  "quality_rating": 6,
  "composite_score": 5.8,
  "notes": ""
}
```

**Composite score formula** (0–10 scale):
```
score = 0.5 * normalize(duration) 
      + 0.3 * normalize(quality_rating)
      + 0.2 * (10 - normalize(awakenings))
```
Normalize each component against the user's own 30-day average, then weight.

### Step 3: Log Daily Factors

Same NLP intake for factors. Each gets its own log line:

```json
{
  "date": "2026-07-11",
  "factor": "caffeine",
  "value": 3,
  "unit": "cups",
  "note": "last cup at 2pm"
}
```

Built-in factors (with units):
- `caffeine` — cups/mg, with timestamp of last intake (ask if omitted)
- `alcohol` — drinks, with bedtime of last drink
- `exercise` — minutes, with intensity (light/moderate/vigorous) and time of day
- `screen_time` — hours before bed (last 2h before bedtime)
- `stress` — 1–10 rating
- `meals` — what & when (especially late dinners)

Custom factors: user can add (e.g., "room temperature", "medication").

### Step 4: Show Reports & Trends

When the user asks for a report, compute:

**Daily snapshot**:
```
2026-07-11 (last night)
  Duration:    7h 45m  (target 8h → -15min)
  Quality:     6/10
  Awakenings:  2
  Score:       5.8
  Debt:        -45 min this week
```

**Weekly report** (last 7 days):
```
  Avg duration: 7h 12m  (▼ 18min vs last week)
  Avg quality:  6.4/10
  Best night:   2026-07-09 (8h 30m, quality 9)
  Worst night:  2026-07-07 (5h 15m, quality 3)
  Sleep debt:   -1h 25m cumulative
```

**Monthly trend** (last 30 days): ASCII sparkline of daily composite scores, average by week, top/bottom 5 days.

### Step 5: Correlation Engine (The Magic)

When the user asks "what affects my sleep?" or after 14+ days of data, run correlations:

For each tracked factor, compute Pearson r between that day's factor value and same-day composite sleep score. Output ranked:

```
📊 What affects YOUR sleep (last 30 days):

  ⚠️  Stress         r = -0.78  ← biggest disruptor
  ⚠️  Screen time    r = -0.65
  ✅  Exercise       r = +0.52  ← biggest improver
  →   Caffeine       r = -0.31
  →   Alcohol        r = -0.18  (only 4 days with data)
```

Interpretation rules:
- |r| > 0.5: strong effect
- |r| 0.3–0.5: moderate
- |r| < 0.3: weak / need more data
- n < 7 days: show "needs more data" instead of correlation

### Step 6: Personalized Recommendations

Generate recommendations from your data + sleep science defaults. Use these evidence-based rules when relevant to the user's data:

| Pattern Observed | Recommendation |
|------------------|----------------|
| High stress + poor sleep | Try 10-min wind-down routine: dim lights, no news, box breathing |
| Caffeine r < -0.4 | Cut off caffeine 8h before bedtime; current cutoff appears too late |
| Screens r < -0.3 | Enable Night Shift / blue-light filter after sunset; phone outside bedroom |
| Alcohol disrupts sleep | Even 1 drink reduces REM; try alcohol-free weekdays |
| Exercise r > +0.3 | Aim for 30+ min daily, finish 3h before bed |
| Inconsistent bedtime (variance > 1h) | Anchor a fixed wake time first; bedtime stabilizes after |
| Sleep debt growing | Take a 20-min nap before 3pm, not later |
| Avg duration < 7h | Move bedtime 30 min earlier for 2 weeks; reassess |

Cache generated insights in `insights.json` with date + source correlation.

## Example Invocations

### Example 1: First-time setup and first log

> **User**: I want to start tracking my sleep.
>
> **Agent**: I'll set up your sleep tracker. Three quick questions:
> 1. How many hours per night do you want to sleep? (default 8)
> 2. What time would you ideally be asleep and wake up?
> 3. Which factors should we track? (default: caffeine, exercise, screen time, stress, alcohol)
>
> **User**: 8 hours, 11pm to 7am, keep the defaults.
>
> **Agent**: Saved your profile to `~/.hermes/sleep/profile.json`. Logged in:
>
> | Setting | Value |
> |---------|-------|
> | Sleep goal | 8.0 hours |
> | Target bedtime | 23:00 |
> | Target wake | 07:00 |
> | Tracked factors | caffeine, exercise, screen time, stress, alcohol |
>
> Ready when you want to log tonight's sleep. You can say things like *"I slept 11pm to 6:45am, woke once, felt okay."*
>
> ---
>
> **User** (next morning): Roughly 10:30 to 6, felt tired, woke up twice.
>
> **Agent**: Logged last night:
>
> | Date | Duration | Quality | Awakenings | Score |
> |------|----------|---------|------------|-------|
> | 2026-07-11 | 7h 30m | 4/10 | 2 | 5.2 |
>
> 30 min under your goal. Want to log any factors for yesterday? (caffeine, exercise, screen time, stress, alcohol)

### Example 2: Three weeks later — discovering patterns

> **User**: What affects my sleep?
>
> **Agent**: Ran correlations on your last 30 days (n=22 sleep logs):
>
> ```
> 📊 What affects YOUR sleep:
>
>   ⚠️  Stress         r = -0.81  ← biggest disruptor (n=22)
>   ⚠️  Screen time    r = -0.67  (n=18)
>   ✅  Exercise       r = +0.58  (n=15)
>   →   Caffeine       r = -0.34  (n=20, borderline)
>   →   Alcohol        r = -0.22  (n=6, need more data)
> ```
>
> **Concrete recommendations from your data**:
>
> 1. **Stress is your #1 disruptor** — on high-stress days (≥7/10) you average 6h 12m vs 7h 48m on low-stress days. Try a 10-min wind-down: dim lights, no phone, slow breathing.
> 2. **Screens >1h before bed cost you ~50 min of sleep.** Move phone outside bedroom or use Night Shift after sunset.
> 3. **Exercise boosts you ~30 min.** You're averaging 4 days/week; aim for 5, but finish 3h before bed.
> 4. **Caffeine cutoff**: your negative correlation suggests cutting off after 1pm (your median last cup is 3pm).
>
> Want me to track how well you stick to these for the next 2 weeks?

### Example 3: Weekly review

> **User**: Show me this week's sleep report.
>
> **Agent**:
>
> **Week of Jul 6 – Jul 12, 2026**
>
> | Metric | This Week | Last Week | Δ |
> |--------|-----------|-----------|---|
> | Avg duration | 7h 18m | 6h 42m | ▲ 36m |
> | Avg quality | 6.8/10 | 5.9/10 | ▲ 0.9 |
> | Sleep debt | -38 min | -2h 12m | ▲ 1h 34m |
> | Best night | Jul 9 (8h 15m, 9/10) | | |
> | Worst night | Jul 7 (5h 30m, 3/10) | | |
>
> **Score trend**:
> ```
> Jul  6  7  8  9  10 11 12
>  ▂   ▅  ▃  ▇  ▆  ▅  ▆
> ```
>
> **Insight**: your worst night (Jul 7) was tied to a 9/10 stress day + 4 alcoholic drinks. Best night (Jul 9) had 0 caffeine after noon and a 40-min run. Keep going.

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User says "I slept badly" without numbers | Prompt: approximate duration? any awakenings? quality 1–10? Don't fabricate zeros. |
| Bedtime 23:30 → wake 00:30 (next day) | Don't compute 23h sleep. Detect cross-midnight by wake_time < bedtime → add 24h. |
| User logs the same day twice | Detect by date; ask "you already logged last night at 7h 45m. Replace or add another entry?" |
| Correlations with n < 7 | Show "needs more data" not a misleading r value |
| Factor logged on wrong date | Factor timestamp defaults to "today"; for events ask "yesterday afternoon / this morning?" |
| User wants import from Apple Health / Fitbit | Note: this skill is manual-entry only. Suggest export + format conversion via `format-converter` skill |
| User asks if data is private | Confirm: all in `~/.hermes/sleep/`, no API calls, never leaves your machine |
| Sleep debt calculation confusion | Sleep debt = sum of (target - actual) over last 7 days. Negative = behind. Positive = surplus. |
| Time zones / DST changes | Always store in local time + IANA tz in profile. Don't use UTC for display. |

## Verification Checklist

Before claiming the skill works, verify:

- [ ] `~/.hermes/sleep/` directory is created on first run
- [ ] `profile.json`, `sleep_log.json`, `factor_log.json` exist with valid JSON
- [ ] Bedtime/wake parsing handles cross-midnight (23:30 → 07:00 = 7h 30m)
- [ ] Duration is auto-computed and matches `bedtime → wake_time`
- [ ] Quality rating 1–10 stored as integer, validated against range
- [ ] Composite score formula reproducible from raw inputs
- [ ] Weekly report math matches a manual check on the JSON logs
- [ ] Correlation engine produces |r| ≤ 1.0 and flags low-n cases
- [ ] At least 14 days of data needed before showing correlation results
- [ ] Sleep debt math: target - actual summed over rolling 7 days
- [ ] All timestamps stored in local time with IANA zone
- [ ] No external API calls — all commands run offline
- [ ] Can regenerate any historical report from logs

## Data Sources & Accuracy

This skill is **fully local-first**. No external APIs, no telemetry, no remote processing.

**What powers the analysis**:
- **Sleep duration / awakenings** → user-reported, validated against bedtime→wake math
- **Composite score** → weighted formula, documented in Step 2 above
- **Correlations** → Pearson r, computed via Python stdlib (`statistics` module) or inline formula
- **Recommendations** → drawn from public sleep science (CDC, NSF, AASM guidelines), filtered by user's own correlation evidence

**Accuracy caveats**:
- Manual entry is less precise than wearables; estimates within ±15 min are acceptable
- Self-reported awakenings often undercount brief micro-awakenings
- Stress is subjective; pair with consistent 1–10 usage over time
- Correlations ≠ causation — "caffeine r=-0.4" means caffeine *correlates* with poor sleep in this data, not proof it causes it
- Recommendations are educational, not medical advice; users with sleep disorders (suspected apnea, chronic insomnia) should consult a clinician

**Storage path**: `~/.hermes/sleep/` — survives across Hermes sessions, owned by user, deletable anytime.

---

## 🤝 Integration Tips

- **With `habit-tracker`**: track "consistent bedtime" as a habit; sleep-tracker becomes the measurement of whether it works.
- **With `fitness-planner`**: log evening workouts as factors; check if they improve sleep quality.
- **With `personal-crm`**: log social/late-night events as factors; check if late socializing affects sleep.
- **Cron-ready**: schedule a weekly report every Sunday at 9pm summarizing the week.

---

*Sleep is the foundation. Track it, improve it.*
