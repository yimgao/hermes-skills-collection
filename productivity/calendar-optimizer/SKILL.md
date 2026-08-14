---
name: calendar-optimizer
description: "Analyze calendar patterns from chat or ICS — meeting load, focus-time fragmentation, no-meeting days, batch-able admin, deep-work window suggestions. Local analysis, optional Google Calendar read."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, calendar, meetings, focus-time, time-management, scheduling, optimization, weekly-review]
    related_skills: [pomodoro-coach, daily-briefing, weekly-review, decision-journal]
---

# 🗓️ Calendar Optimizer — 日历优化师

> Analyze your meeting calendar and reclaim deep-work time. 分析你的会议日历，找回深度工作时间。

---

## Overview

Calendar Optimizer turns Hermes into a personal calendar analyst. Paste an `.ics` export, drop a JSON event list, or read your Google Calendar — and get a quantified view of *how your week is actually structured*. The skill flags meeting overload, fragmentation, low-density days you can protect for deep work, and admin tasks that could be batched into one window. All analysis runs locally; nothing leaves your machine.

| Capability | Description |
|------------|-------------|
| **ICS / JSON ingestion** | Parse standard `.ics` exports or structured event arrays |
| **Google Calendar read** *(optional)* | Pull the last N days via `gws calendar` if available |
| **Meeting-load analysis** | Total meeting hours, % of work week in meetings, week-over-week trend |
| **Fragmentation score** | Count of context switches per day; >6 fragments = high churn |
| **Focus-time calculator** | Uninterrupted blocks ≥90 min flagged, <30 min gaps flagged as "lost time" |
| **Day-of-week heat-map** | Which day is meeting-heavy? Which day is best for deep work? |
| **No-meeting-day detector** | Days with zero scheduled calls — protect as focus days |
| **Batch-able meeting finder** | Group meetings by topic/attendee; suggest consolidating on one anchor day |
| **Deep-work window recommender** | Based on historical meeting density, suggest specific hours to block |
| **Recurring-time-sink detection** | Flag weekly meetings that have had <2 attendees / 0 agenda items |
| **Weekly / monthly trend** | Compare this week vs last week, last 4 weeks, last 12 weeks |
| **Privacy-first** | Local JSON cache; can run fully offline from a pasted ICS |

---

## When to Use

- *"Analyze my calendar this week — how much meeting load do I have?"*
- *"What's my fragmentation score?"*
- *"Which day of the week should I block for deep work?"*
- *"Show me meetings I can batch together"*
- *"What recurring meetings are time sinks?"*
- *"Pull my last 30 days of Google Calendar and find focus-time gaps"*
- *"Plan my ideal week: 3 deep-work days + 2 meeting days + Friday admin"*
- *"Is my fragmentation getting worse vs last month?"*
- *"Generate a report to share with my manager about meeting load"*

---

## Core Workflow

### Step 1 — Ingest the calendar

**Choose one of three input modes:**

```bash
# A) Paste an .ics export (recommended for offline / privacy)
hermes > "Analyze ~/Downloads/calendar-export.ics for the last 30 days"

# B) Paste JSON event list
hermes > "Here's my calendar as JSON:" [then paste array]

# C) Read from Google Calendar via gws (requires `gws calendar` CLI auth)
hermes > "Pull my Google Calendar for the last 30 days and analyze"
```

**Mode A — ICS parsing (zero deps):**

```python
# scripts/parse_ics.py — pure Python stdlib, no external deps
import re
from datetime import datetime, timedelta
from pathlib import Path

def parse_ics(path: str) -> list[dict]:
    """Parse RFC 5545 iCalendar into a list of events."""
    text = Path(path).read_text(encoding="utf-8")
    events = []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.S):
        def get(field):
            m = re.search(rf"^{field}[;:](.*)$", block, re.M)
            return m.group(1).strip() if m else ""
        # Folded lines (RFC 5545 §3.1: line continuation starts with space)
        raw_lines = block.splitlines()
        unfolded = []
        for line in raw_lines:
            if line.startswith((" ", "\t")) and unfolded:
                unfolded[-1] += line[1:]
            else:
                unfolded.append(line)
        body = "\n".join(unfolded)
        def get2(field):
            m = re.search(rf"^{field}[;:](.*)$", body, re.M)
            return m.group(1).strip() if m else ""
        try:
            dtstart = datetime.fromisoformat(get2("DTSTART").replace("Z", "+00:00"))
            dtend   = datetime.fromisoformat(get2("DTEND").replace("Z", "+00:00"))
        except ValueError:
            continue
        events.append({
            "uid":      get2("UID"),
            "summary":  get2("SUMMARY"),
            "organizer":get2("ORGANIZER"),
            "start":    dtstart,
            "end":      dtend,
            "duration_min": int((dtend - dtstart).total_seconds() / 60),
            "attendees": get2("ATTENDEE").count("mailto:") if get2("ATTENDEE") else 0,
        })
    return events
```

**Mode C — Google Calendar:**

```bash
# Read last 30 days as JSON
gws calendar events list --from "$(date -v-30d +%Y-%m-%d)" --to "$(date +%Y-%m-%d)" --json > cache/calendar-30d.json
```

Cache raw events to `~/.hermes/calendar-optimizer/events-{YYYY-MM-DD}.json` so multiple analyses run against the same snapshot.

---

### Step 2 — Compute calendar metrics

```python
# scripts/metrics.py — pure stdlib, depends on parsed events from Step 1
from collections import Counter, defaultdict
from datetime import timedelta

WORK_START = 9   # 09:00
WORK_END   = 18  # 18:00
DEEP_WORK_MIN = 90  # uninterrupted block ≥90 min
BATCH_WINDOW_MIN = 30  # gaps ≤30 min between meetings = fragmentation

def compute_metrics(events: list[dict], workdays_only: bool = True) -> dict:
    """Compute fragmentation, focus-time, and meeting-load metrics."""
    # Bucket events by local date
    by_day = defaultdict(list)
    for e in events:
        if workdays_only and e["start"].weekday() >= 5:
            continue
        by_day[e["start"].date()].append(e)

    daily = []
    for day, evs in sorted(by_day.items()):
        evs.sort(key=lambda x: x["start"])
        meeting_min = sum(e["duration_min"] for e in evs)

        # Fragmentation: gaps between meetings ≤30 min count as context churn
        gaps = []
        for i in range(len(evs) - 1):
            gap_min = (evs[i+1]["start"] - evs[i]["end"]).total_seconds() / 60
            if 0 < gap_min <= BATCH_WINDOW_MIN:
                gaps.append(gap_min)
        fragmentation = len(gaps)

        # Focus windows: gaps ≥90 min between (or before/after) meetings
        focus_blocks = []
        if evs:
            # Start of workday gap
            if evs[0]["start"].hour >= WORK_START:
                first_gap = (evs[0]["start"] - evs[0]["start"].replace(
                    hour=WORK_START, minute=0)) .total_seconds() / 60
                if first_gap >= DEEP_WORK_MIN:
                    focus_blocks.append(first_gap)
            # Inter-meeting gaps
            for i in range(len(evs) - 1):
                g = (evs[i+1]["start"] - evs[i]["end"]).total_seconds() / 60
                if g >= DEEP_WORK_MIN:
                    focus_blocks.append(g)
            # End-of-day gap
            last_end = evs[-1]["end"]
            eod = evs[-1]["start"].replace(hour=WORK_END, minute=0)
            if last_end < eod:
                tail = (eod - last_end).total_seconds() / 60
                if tail >= DEEP_WORK_MIN:
                    focus_blocks.append(tail)

        work_day_min = (WORK_END - WORK_START) * 60
        daily.append({
            "date":              day.isoformat(),
            "weekday":           day.strftime("%A"),
            "meeting_min":       meeting_min,
            "meeting_pct":       round(100 * meeting_min / work_day_min, 1),
            "fragmentation":     fragmentation,
            "focus_blocks":      len(focus_blocks),
            "focus_min_total":   int(sum(focus_blocks)),
            "longest_focus_min": int(max(focus_blocks)) if focus_blocks else 0,
            "n_meetings":        len(evs),
        })

    # Weekly rollup
    by_week = defaultdict(list)
    for d in daily:
        iso_week = d["date"][:10]  # rough bucketing; refine w/ iso calendar
        by_week[iso_week].append(d)
    weekly = []
    for wk, days in sorted(by_week.items()):
        weekly.append({
            "week_start": wk,
            "total_meeting_min": sum(d["meeting_min"] for d in days),
            "avg_fragmentation": round(sum(d["fragmentation"] for d in days) / max(1, len(days)), 1),
            "total_focus_min":   sum(d["focus_min_total"] for d in days),
        })

    # Day-of-week heat-map
    dow = defaultdict(lambda: {"meet": 0, "focus": 0, "n": 0})
    for d in daily:
        dow[d["weekday"]]["meet"] += d["meeting_min"]
        dow[d["weekday"]]["focus"] += d["focus_min_total"]
        dow[d["weekday"]]["n"] += 1
    heatmap = []
    for day_name, v in dow.items():
        n = max(1, v["n"])
        heatmap.append({
            "weekday": day_name,
            "avg_meeting_pct": round(100 * v["meet"] / (n * (WORK_END - WORK_START) * 60), 1),
            "avg_focus_min":   round(v["focus"] / n, 1),
            "n_days":          v["n"],
        })
    heatmap.sort(key=lambda x: ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(x["weekday"]))

    return {
        "daily":          daily,
        "weekly":         weekly,
        "weekday_heatmap": heatmap,
        "summary": {
            "total_events":        len(events),
            "workdays_analyzed":   len(daily),
            "avg_meeting_pct":     round(sum(d["meeting_pct"] for d in daily) / max(1, len(daily)), 1),
            "avg_fragmentation":   round(sum(d["fragmentation"] for d in daily) / max(1, len(daily)), 1),
            "no_meeting_days":     sum(1 for d in daily if d["n_meetings"] == 0),
        },
    }
```

---

### Step 3 — Generate the report + recommendations

Hermes reads the metrics and surfaces specific, actionable insights:

```
═══════════════════════════════════════════════════════════════════
   CALENDAR OPTIMIZER REPORT — last 30 days
═══════════════════════════════════════════════════════════════════

OVERVIEW
  Workdays analyzed:        22
  Total meetings:           87
  Avg % of week in meetings: 41.3%        [HIGH — industry med ~28%]
  Avg fragmentation score:  4.2 / day    [HIGH — >4 = context churn]
  No-meeting days found:    3            [consider protecting as focus days]

DAY-OF-WEEK HEAT MAP
            meeting %     focus min/day   verdict
  Mon         52%              38         ⚠ overloaded
  Tue         61%              22         ⚠⚠ overloaded
  Wed         38%              95         ✓ good focus day
  Thu         49%              51         ~ mixed
  Fri         18%             142         ✓✓ best deep-work day

RECOMMENDATIONS

1. PROTECT FRIDAY AS NO-MEETING-DAY
   Currently: 18% meeting load, 142 min/day avg focus. ⚠ If you book ANY
   recurring meeting, schedule it Mon-Thu, not Fri.

2. CONSOLIDATE TUESDAY MEETINGS
   Tuesday has 5× worse fragmentation than Wed. Suggestion: rename all
   "anytime this week" 30-min syncs → "Tuesday batch-day 14:00–15:30".

3. REVIEW RECURRING 1:1s WITH NO AGENDA
   Detected 4 recurring 1:1s where the past 8 meetings had <3 attendees
   and zero agenda items in the title or invite body:
     • "Sync" with Alex Chen       (Mondays 10:00)
     • "Catch up" with Priya Iyer  (Thursdays 11:00)
     • ...

4. RECLAIM 09:00–10:30 WEDNESDAY AS DEEP WORK
   Wed 09:00–10:30 is currently free 78% of weeks → block it as standing
   focus time (90-min pomodoro session, "Wed deep-work AM").

5. BATCH ALL <15-MIN "ASKS" INTO ONE 14:00 ADMIN WINDOW
   You have 9 different <15-min meetings across the week. Consolidate into
   a daily 14:00–14:30 open admin slot.
═══════════════════════════════════════════════════════════════════
```

The recommendations engine logic (the "judgment" layer above the metrics):

| Signal | Threshold | Recommendation |
|--------|-----------|----------------|
| Day-of-week meeting % > 50% AND ≥3 weeks stable | high | "Move recurring meetings off this day" |
| Day-of-week meeting % < 25% AND ≥3 weeks stable | low | "Protect as no-meeting-day" |
| Fragmentation > 6/day on ≥3 days/week | high churn | "Batch small meetings into 14:00 admin" |
| Recurring meeting with <3 attendees avg + no agenda text | time sink | "Kill or restructure: <name>" |
| Gap ≥90 min on same weekday ≥70% of weeks | protectable | "Block this as deep-work window" |
| Same-topic recurring meetings (cosine cluster) | clusterable | "Consolidate into 1 weekly anchor" |
| Week-over-week meeting % rising >10% for 3 weeks | trend up | "Schedule a meeting-purge intervention" |

The day-of-week verdict (± bands) reads off the heatmap directly. The recommendations text is templated so you can copy-paste into your manager conversation, retro, or personal action plan.

---

## Example Invocations

### Example 1 — Pull from Google Calendar and analyze

> **User:** Pull my last 30 days from Google Calendar. How much of my week is in meetings, and which day should I protect as a focus day?

> **Hermes:**
> ```
> [EXEC] gws calendar events list --from 2025-07-14 --to 2025-08-13 --json > cache/cal.json
> [INFO] 87 events parsed across 22 workdays
>
> OVERVIEW
>   Avg meeting load:       41.3% of work week
>   Avg fragmentation:      4.2 context switches/day
>   No-meeting days found:  3
>
> DAY HEATMAP
>   Mon  52% meet / 38 min focus   ⚠ overloaded
>   Tue  61% meet / 22 min focus   ⚠⚠ overload
>   Wed  38% meet / 95 min focus   ✓ good
>   Thu  49% meet / 51 min focus   ~
>   Fri  18% meet / 142 min focus  ✓✓ best focus day
>
> RECOMMENDATION
>   1. Block Fri as no-meeting-day. You already have 142 min/day focus
>      potential — protect it.
>   2. Move Tuesday's <30-min syncs into one 14:00–15:30 batch window.
>   3. Recurring "catch up" with Priya (Th 11:00) — 0 agenda items for 4
>      weeks, avg 2 attendees. Cancel or restructure.
>
> Full report: ~/.hermes/calendar-optimizer/report-2025-08-13.md
> ```

### Example 2 — Paste ICS, ask for focus-time windows

> **User:** Here's my calendar export: [uploads calendar.ics]. Find me the best deep-work windows.

> **Hermes:**
> ```
> [EXEC] scripts/parse_ics.py ~/Downloads/calendar.ics → 142 events
> [EXEC] scripts/metrics.py → metrics.json
>
> DEEP-WORK WINDOWS (≥90 min uninterrupted, recurring ≥70% of weeks)
>
>   1. Wed 09:00–10:30     (recurs 4/4 weeks)   ✓ PROTECT
>   2. Fri 09:00–12:00     (recurs 3/4 weeks)   ✓✓ DEEP-WORK ANCHOR
>   3. Thu 15:00–16:30     (recurs 3/4 weeks)   ✓ PROTECT
>
> FRAGMENTATION HOTSPOTS
>
>   Tue 10:00–12:00: 4 meetings across 120 min, longest gap 22 min
>   Thu 14:00–15:30: 3 meetings across 90 min, 0 gap
>
> SUGGESTION
>   Set "Focus Time" / "Out of Office" calendar holds on:
>     Wed 09:00–10:30 (recurring)
>     Fri 09:00–12:00 (recurring)
>   Decline Tue/Thu 14:00 meetings unless critical; offer async update.
> ```

### Example 3 — Track fragmentation over time

> **User:** Has my calendar fragmentation gotten worse since I started the new role 8 weeks ago?

> **Hermes:**
> ```
> [EXEC] Load cache weeks 1–4 (legacy role) vs weeks 5–8 (new role)
>
> COMPARISON
>                         weeks 1–4    weeks 5–8    change
>   Meeting %                28%          41%       +13pp   ⚠
>   Fragmentation/day        2.1          4.2       +2.1   ⚠⚠
>   Avg meeting length       32 min       24 min     -8 min ~
>   No-meeting days/wk       1.5          0.75      -0.75  ⚠
>
> INSIGHT
>   Your meeting load and fragmentation both roughly doubled in the new
>   role. Average meeting length got shorter — that's the fragmentation
>   signal: you're in more, shorter meetings.
>
> NEXT 2 WEEKS
>   1. Mark Friday as recurring focus block (reclaim no-meeting day)
>   2. Audit the 4 new recurring meetings you added — anything cancelable?
>   3. Batch remaining small syncs into Tue/Thu 14:00 admin window
>
> I'll re-run this in 2 weeks to confirm the trend reversed.
> ```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Google Calendar auth fails — `gws calendar` returns 401 | The skill should fall back to asking the user to paste an `.ics` export from Google Calendar → Settings → Import & Export → Export |
| ICS file has timezones that look off | Use `datetime.fromisoformat(s.replace("Z","+00:00"))` and convert to local time before bucketing into "Mon/Tue/..." — otherwise Monday's overnight events leak into Sunday |
| User has 0 events for a week (vacation, leave) | Exclude weeks where `n_events < 3` from trend stats; flag them explicitly so the user knows they skew the average |
| User works weekends and Mon = meeting day, Sun = focus day | `WORK_START`/`WORK_END` and weekday labels are configurable — prompt the user once on first run or store in `~/.hermes/calendar-optimizer/profile.json` |
| Recurring meeting has hundreds of events | Deduplicate by `(summary, day_of_week, time)` so each weekly recurring meeting counts once in trend stats, not 52 times |
| Single 8-hour block misinterpreted as 8 fragmented meetings | Treat events with same `summary` and adjacent start/end as one continuous block; merge before computing fragmentation |
| User asks about "last month" — does that mean last 30 days or last calendar month? | Default to last 30 days; explicitly ask "calendar-month (Apr 1–30) or rolling 30 days?" only for month-over-month comparisons |
| Personal events mixed with work | Filter by calendar name (`WORK_CALENDAR`) or ask the user to pick which .ics export — most calendars let you export a single sub-calendar |
| `DTSTART;VALUE=DATE` (all-day events) breaks duration calc | All-day events have no `DTEND` (or end-of-day exclusive); treat all-day as `meeting_min = 0` (not counted toward meeting load) |
| Privacy — user doesn't want any data uploaded | Default to fully local: ICS file → local parse → local metrics → local Markdown report. Only invoke `gws` if user explicitly opts in |

---

## Verification Checklist

- [ ] Parsed events count = exported events count (sanity check `len(events)` against ICS `BEGIN:VEVENT` count)
- [ ] Total meeting minutes ÷ work-day minutes ≈ average meeting % (catches mis-bucketed weekend events)
- [ ] Each "deep-work window" recommendation appears ≥70% of weeks in the data (not just one lucky week)
- [ ] No-meeting days detected are *actually* zero meetings, not "zero non-recurring meetings"
- [ ] The fragmentation score lines up with the user's gut feel — show them the raw daily breakdown so they can spot-check
- [ ] If pulling from Google Calendar, the dates captured match the dates the user remembers having meetings on
- [ ] Output report is written to `~/.hermes/calendar-optimizer/report-{YYYY-MM-DD}.md` so subsequent runs accumulate history
- [ ] All recommendations are dated and copy-pastable into a personal action plan or 1:1 with manager
- [ ] Week-over-week comparison only spans ≥2 weeks of data — flag explicitly when not enough history
- [ ] User was asked which sub-calendar / dataset to analyze if multiple exist (work vs personal vs family)

---

## Data Sources & Accuracy

| Source | What it provides | Accuracy |
|--------|------------------|----------|
| ICS export (RFC 5545) | All event metadata: title, organizer, attendees, start/end, recurrence | Same as your calendar — depends on export accuracy |
| Google Calendar via `gws calendar` | Same as ICS, but live; respects OAuth scopes you granted | Bounded by gws token permissions |
| Pasted JSON event list | User-typed; can be subset of full calendar | Wholly user-controlled |
| Local cache `~/.hermes/calendar-optimizer/events-{date}.json` | Re-usable across multiple analyses on same dataset | Snapshot accuracy — re-pull for live changes |

**Accuracy boundaries:**

- Calendar Optimizer analyzes **only what you give it**. If you paste a personal-calendar `.ics` and ask "what's my meeting load", the answer reflects personal events, not work. Always ask the user to scope which dataset.
- "Fragmentation" is a *relative* metric — useful for week-over-week and user-vs-team comparison, but the absolute number depends on how you split/merge adjacent meetings. The skill defaults to "anything in your work hours with <30 min gap counts as fragmentation".
- "Best deep-work day" requires ≥3 weeks of data to be trustworthy. With <3 weeks, output is flagged as "early signal, low confidence".
- Recurring-meeting "time sink" detection uses simple heuristics (attendee count, agenda keywords) — false positives happen, especially for 1:1s that are genuinely valuable. Always pair the recommendation with a human review checkbox.
- The skill makes no network calls by default. It can run fully offline against a pasted `.ics`. This is intentional — your calendar reveals a lot about your work, role, and network.
