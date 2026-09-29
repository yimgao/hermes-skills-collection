---
name: quarterly-goals-coach
description: "Plan, track, and ship 90-day OKRs from chat — set 3-5 objectives per quarter with measurable key results, weekly confidence check-ins, milestone-grade progress (0.0-1.0 with traffic-light), at-risk detection, ship-or-kill audit at week 6, and end-of-quarter retrospective that feeds next quarter's plan. Pairs with weekly-review, pomodoro-coach, decision-journal, standup-status-updater, habit-tracker, bookshelf."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, okr, quarterly, goals, planning, focus, accountability, gtd, shipping, milestones, reflection, retrospective]
    related_skills: [weekly-review, pomodoro-coach, decision-journal, standup-status-updater, habit-tracker, bookshelf, daily-briefing, daily-shutdown, draft-tracker]
---

# 🎯 Quarterly Goals Coach — 90 天 OKR 教练

> Set 3-5 outcomes every 90 days. Track confidence weekly. Get unblocked before goals quietly die. Decide at week 6: ship, pivot, or kill. Close the quarter with a retrospective that makes next quarter sharper.

---

## Overview

Most goal systems fail for the same reason: you write ambitious objectives on January 1st, glance at them on January 14th, and never look again until late March when it's too late to course-correct. `quarterly-goals-coach` is the **anti-bystander** system — a 90-day cadence that forces weekly contact with your goals, surfaces silent decay, and gives you permission to abandon goals that aren't working instead of letting them rot.

It works for **any 90-day cycle**: business quarter (Jan/Feb/Mar, etc.), personal-quarter (your birthday to birthday-90), academic term, fiscal half. It is intentionally **opinionated** — 3-5 objectives, each with 2-4 measurable Key Results (KRs), 0.0-1.0 progress scoring, traffic-light status, week-6 mid-quarter audit, and a forced end-of-quarter retrospective that seeds next quarter.

The power isn't the structure — it's the **weekly confidence question**: *"On a 0-10 scale, how confident are you that you'll hit [Objective X]?"* That single number, tracked over 13 weeks, predicts goal completion better than any project plan.

| Capability | Description |
|---|---|
| 🎯 **One-line OKR setup** | `set my Q4 OKRs` — guided 5-question intake, generates full objective+KR tree in 60 seconds |
| 📊 **3-5 Objectives per quarter** | Enforced upper bound — forces ruthless prioritization |
| 📏 **2-4 KRs per Objective** | Each KR is measurable, time-bound, owner-assigned (you/team/external) |
| 🟢🟡🔴 **Traffic-light status** | `on_track` / `at_risk` / `off_track` / `done` / `killed` — auto-derived from progress |
| 📈 **0.0-1.0 progress score** | Per KR, per Objective, per quarter — manual update with audit trail |
| 🔮 **Weekly confidence check-in** | 0-10 self-rating — trend line predicts quarter outcome by week 4 |
| ⏰ **Week-6 mid-quarter audit** | Mandatory ship / pivot / kill decision for each objective |
| 🚨 **Silent-decay detector** | Flags goals with no check-in for 7+ days, declining confidence, or stale KRs |
| 🔁 **KR cadence rules** | Move-the-needle KRs are monthly; counter-style (X of Y) are weekly |
| 🧠 **Blocker surfacing** | One-question weekly: *"What's blocking the most right now?"* — auto-aggregated |
| 🔗 **Cross-skill links** | Pulls focus hours from pomodoro, weekly wins from weekly-review, milestones from standup, reading from bookshelf |
| 📜 **End-of-quarter retro** | 5-question template: kept / killed / new / lessons / next-quarter seed |
| 🔒 **Local-first** | All data in `~/.hermes/goals/` — never uploaded, exportable to JSON / Markdown |

---

## When to Use

**Direct triggers:**
- *"Set my Q4 OKRs"* / *"Plan my quarterly goals"*
- *"I want to set 3 goals for the next 90 days"*
- *"Show me my current objectives"*
- *"Update KR 2 to 0.6 progress"*
- *"Weekly check-in" / *"Confidence check-in"*
- *"How am I tracking this quarter?"*
- *"Quarterly status"* / *"Show me my Q3 progress"*
- *"I'm blocked on [X]"* / *"What's blocking my goals?"*
- *"Mid-quarter audit" / *"Ship or kill review"*
- *"Close out Q3"* / *"End-of-quarter retro"*
- *"Set Q4 from my Q3 retro"*
- *"Add a new objective to my current quarter"*
- *"Archive last quarter"*
- *"What's at risk this quarter?"*
- *"Show me my confidence trend"*
- *"给我设一下这个季度的目标"* / *"季度中期复盘"*

**Indirect triggers (Hermes should ask):**
- User starts a new week with "let me plan" → *"Want to run a 30s check-in on your quarter goals?"*
- User asks "should I take this on?" during week 7+ → *"How does this fit your current quarter?"*
- User reports finishing a major piece of work → *"Does this count toward a KR? Want me to update?"*
- During `weekly-review`, prompt for confidence rating per active objective
- During `daily-briefing`, surface the lowest-confidence objective as "the one to protect today"

**Don't use when:**
- The user wants daily habits (use `habit-tracker` — quarterly goals ≠ habits)
- The user wants a 1-day or 1-month plan (use `weekly-review` or `study-planner`)
- The user wants project-level task tracking (use a TODO system — OKRs ≠ todos)
- The goal is operational (< 1 week to complete) — quarterly is the wrong cadence

---

## Core Workflow

### Step 1 — Detect Storage & Initialize Quarter

```bash
GOALS_DIR=~/.hermes/goals
CURRENT_QUARTER=$GOALS_DIR/current.json
HISTORY_DIR=$GOALS_DIR/history
RETROS=$GOALS_DIR/retros

mkdir -p "$GOALS_DIR" "$HISTORY_DIR" "$RETROS"
[ -f "$CURRENT_QUARTER" ] || echo '{}' > "$CURRENT_QUARTER"
```

**Quarter ID format:** `YYYY-QN` (e.g., `2026-Q4`) — auto-detected from today's date, or user can name any 90-day window (`H2-launch`, `Birthday-90`, `Soccer-season`).

**One-line setup** (`set my Q4 OKRs`):

The agent asks 5 questions in one message, then generates the full plan:

```
1. What 3-5 outcomes do you want true by day 90?
2. For each outcome, what 2-4 numbers will prove it happened?
3. Who owns each one? (you, team, partner, vendor)
4. What's the #1 risk that could kill this quarter?
5. What are you willing to STOP doing to make room?
```

The agent then writes `current.json` with the parsed structure:

```json
{
  "quarter_id": "2026-Q4",
  "title": "Q4 2026",
  "start_date": "2026-10-01",
  "end_date": "2026-12-31",
  "created_at": "2026-09-23T...",
  "status": "active",
  "objectives": [
    {
      "id": "obj-1",
      "title": "Launch v2 of product to 1,000 paying users",
      "why": "We need $30k MRR by Jan to extend runway",
      "owner": "me",
      "status": "on_track",
      "progress": 0.3,
      "krs": [
        {
          "id": "kr-1-1",
          "description": "Ship beta to 50 design partners",
          "type": "counter",
          "current": 12,
          "target": 50,
          "unit": "design partners",
          "cadence": "weekly",
          "owner": "me",
          "due_date": "2026-11-15",
          "progress": 0.24
        },
        {
          "id": "kr-1-2",
          "description": "Hit $20k MRR from v2",
          "type": "number",
          "current": 0,
          "target": 20000,
          "unit": "USD",
          "cadence": "monthly",
          "owner": "me",
          "due_date": "2026-12-31",
          "progress": 0.0
        }
      ]
    }
  ],
  "risk_register": [
    "Lead engineer leaving before beta ships"
  ],
  "stopped": [
    "Daily LinkedIn posts (was: build audience)"
  ],
  "checkins": [
    {"week": 1, "date": "2026-10-05", "confidence": 7, "blocker": "waiting on design"}
  ],
  "mid_quarter_audit": null,
  "retro": null
}
```

**The "Stop List"** — questions 5 — is the most under-used and most powerful. By forcing you to name what you're abandoning to make room, you create real focus instead of aspirational goals on top of an unchanged calendar.

### Step 2 — Weekly Check-In Loop

Every week, the user runs **`weekly check-in`** or `confidence check-in`. The agent walks through:

```
1. For each Objective, rate confidence 0-10 you'll hit it
2. Update each KR (current value + auto-progress)
3. Name the #1 blocker across all objectives
4. Mark "shipped" / "killed" / "no change" status per Objective
5. (optional) Add a note for the week
```

The agent writes to `checkins[]`:

```json
{
  "week": 4,
  "date": "2026-10-26",
  "confidence": {
    "obj-1": 6,
    "obj-2": 8,
    "obj-3": 3
  },
  "kr_updates": {
    "kr-1-1": {"current": 28, "progress": 0.56},
    "kr-1-2": {"current": 4200, "progress": 0.21}
  },
  "blocker": "API rate limits choking onboarding flow",
  "notes": "Shipped onboarding v2, conversion still low",
  "status_changes": {
    "obj-3": "at_risk"
  }
}
```

**Traffic-light rules** (auto-derived, user can override):

| Status | Criteria |
|---|---|
| `on_track` 🟢 | Confidence ≥ 6, progress ≥ expected pace (week / 13), no status change requested |
| `at_risk` 🟡 | Confidence 4-5 OR progress < expected pace by ≥ 0.1, OR no check-in for 7+ days |
| `off_track` 🔴 | Confidence ≤ 3, OR progress < 0.5 × expected pace, OR explicitly flagged |
| `done` ✅ | All KRs at progress 1.0 |
| `killed` ⬛ | Explicitly abandoned via mid-quarter audit |

**Expected pace formula:** `week_number / 13` (13 weeks per quarter). At week 6, expected pace is 0.46. If your progress is 0.20, you're slipping.

### Step 3 — Mid-Quarter Audit (Week 6)

Week 6 is the **decision week**. The agent forces this prompt:

```
🚦 MID-QUARTER AUDIT — 6 weeks down, 7 to go

For each Objective, you must pick one:

A) 🚀 SHIP — on track, keep going
B) 🔄 PIVOT — change the KR or scope, but keep the goal
C) 💀 KILL — abandon, learn, free up the time

Current state:
  obj-1 "Launch v2 to 1k users" — confidence 6, progress 0.45 [on_track]
  obj-2 "Run a sub-2hr half marathon" — confidence 4, progress 0.30 [at_risk]
  obj-3 "Read 12 books" — confidence 8, progress 0.50 [on_track]
  obj-4 "Hire senior engineer" — confidence 3, progress 0.20 [off_track]
```

The agent then updates `mid_quarter_audit`:

```json
{
  "date": "2026-11-12",
  "decisions": {
    "obj-1": {"decision": "ship", "rationale": "Pace is right, no changes"},
    "obj-2": {"decision": "pivot", "rationale": "Injured knee, switching to 10K goal"},
    "obj-3": {"decision": "ship", "rationale": "On pace"},
    "obj-4": {"decision": "kill", "rationale": "Market too tight, defer to Q1"}
  },
  "lessons": [
    "Don't hire for roles when comp band is unrealistic",
    "Injuries need earlier intervention, not later"
  ]
}
```

The **"kill" option is sacred**. Most goal systems have no exit ramp, so dead goals eat alive goals' oxygen. This audit forces the conversation 7 weeks before the deadline when there's still time to redirect.

### Step 4 — End-of-Quarter Retrospective

Triggered by **`close out Q3`** or auto-prompted at week 13. The agent runs the 5-question retro:

```
1. 🏆 What did you actually SHIP this quarter?
2. 💀 What did you KILL? (even if unintentionally)
3. 🆕 What NEW thing emerged that wasn't planned?
5. 📖 Lessons — what would you tell past-you in week 1?
7. 🌱 SEEDS — what should next quarter carry forward?
```

Output written to `retros/2026-Q3-retro.md` AND seeds `2026-Q4` with carried-forward objectives (auto-flagged as "carried from Q3").

### Step 5 — Cross-Skill Integration

The skill passively enriches other skills and vice versa:

| Trigger | Pulls / Pushes |
|---|---|
| `weekly-review` | Pulls active objectives; pushes confidence rating back |
| `daily-briefing` | Surfaces lowest-confidence objective as "the one to protect today" |
| `pomodoro-coach` | Optional: tag pomodoros with KR-id; weekly focus-hour totals per KR |
| `standup-status-updater` | Includes "Quarter goal progress" line |
| `decision-journal` | One-click: convert a decision into a new Objective |
| `habit-tracker` | Habits can be explicit KRs (e.g., "Workout 3×/week" → KR) |
| `bookshelf` | "Read 12 books" → auto-creates a counter-style KR |
| `daily-shutdown` | Optional: prompt "did you advance any KR today?" |

**One-command sync example:**

```
sync: pull this week's pomodoros into KR-1-1 progress
```

→ Reads `~/.hermes/pomodoro/sessions.json`, filters tags matching the Objective, sums focus hours, suggests a confidence nudge if focus hours dropped.

---

## Example Invocations

### Example 1 — First-time setup

> **User:** set my Q4 OKRs

> **Agent:**
> Let's build your Q4. Five quick questions:
>
> 1. **What 3-5 outcomes do you want TRUE by Dec 31?**
>    (examples: ship product v2, hit $30k MRR, run sub-2hr half marathon, hire senior eng, write book proposal)
>
> 2. **For each, what 2-4 numbers will prove it happened?**
>
> 3. **Who owns each — you, team, vendor, partner?**
>
> 4. **What's the #1 risk that could kill this quarter?**
>
> 5. **What are you willing to STOP doing to make room?**

> **User:**
> 1. Ship product v2 beta. Hit $20k MRR. Read 12 books. Run a sub-2hr half marathon. Write book proposal.
> 2. v2: 50 design partners signed, $20k MRR. Reading: 12 books. Half: < 2hr. Proposal: 5 chapters drafted.
> 3. All me.
> 4. Burnout, knee injury, getting stuck on the proposal.
> 5. Stop daily LinkedIn posts, stop saying yes to podcast guest spots, drop the Wednesday night poker game.

> **Agent:**
> Done. Your Q4 plan:

```
🎯 Q4 2026 — 90 days starting Oct 1

OBJ 1: Ship product v2 to 1,000 paying users
  └ KR 1.1: 50 design partners signed [0/50, weekly counter]
  └ KR 1.2: $20k MRR [0/20k, monthly]

OBJ 2: Read 12 books
  └ KR 2.1: 12 books finished [0/12, weekly counter]

OBJ 3: Sub-2hr half marathon
  └ KR 3.1: Race < 2:00:00 on Nov 13 [milestone]

OBJ 4: Ship book proposal (5 chapters drafted)
  └ KR 4.1: 5 chapters drafted [0/5, bi-weekly]

🛑 STOPPED to make room: daily LinkedIn, podcast yes, Wednesday poker

🚨 Risk register: burnout / knee / proposal block

Saved to ~/.hermes/goals/2026-Q4.json
Schedule weekly check-ins? [Sun 8pm / Mon 9am / skip]
```

### Example 2 — Week 4 check-in

> **User:** weekly check-in

> **Agent:**
> 4 weeks down, 9 to go. Quick round:

```
OBJ 1 — "Ship product v2 to 1k users"   [🟢 on_track, progress 0.45]
  KR 1.1 design partners: 12 → ? (target 50)
  KR 1.2 MRR: $0 → ? (target $20k)
  Confidence 0-10?

OBJ 2 — "Read 12 books"                [🟢 on_track, progress 0.33]
  Books finished: 0 → ? (target 12)
  Confidence?

OBJ 3 — "Sub-2hr half marathon"        [🟡 at_risk, progress 0.50]
  Race < 2hr: still on?
  Confidence?

OBJ 4 — "Ship book proposal"           [🔴 off_track, progress 0.10]
  Chapters drafted: 0 → ?
  Confidence?

🚧 #1 blocker across all?
📝 Anything to flag (status changes, kills)?
```

> **User:** KR 1.1 now 28 partners, KR 1.2 at $4.2k. Books: 4 done. Half: still going, 9.1mi long run yesterday. Proposal: 1 chapter drafted. Confidence: 7, 9, 6, 2. Blocker: proposal — I keep dodging it.

> **Agent:**
> Logged. Updated picture:

```
OBJ 1 🟢 conf 7, progress 0.45, pace on
OBJ 2 🟢 conf 9, 4/12 books ✓ ahead
OBJ 3 🟢 conf 6 (raised from 🟡) — long run is solid
OBJ 4 🔴 conf 2, 1/5 chapters — at-risk getting worse

📉 OBJ 4 warning: progress 0.20 vs expected pace 0.31
   + confidence declined from week 2 (was 4) → now 2
   + blocker name: "proposal — keeps getting dodged"

💡 Suggest: this Sunday's pomodoro block, hard 90min on chapter 2.
   If chapter 2 doesn't move by next check-in, flag for kill in mid-quarter audit (Week 6).
```

### Example 3 — Mid-quarter audit, week 6

> **User:** mid-quarter audit

> **Agent:**
> 🚦 WEEK 6 — 7 weeks left. Decision time per objective:

```
OBJ 1 — "Ship product v2"             conf 7, prog 0.62 [🟢]
OBJ 2 — "Read 12 books"                conf 9, prog 0.66 [🟢]  (8/12)
OBJ 3 — "Sub-2hr half marathon"        conf 6, prog 0.85 [🟢]  (race is Nov 13!)
OBJ 4 — "Book proposal 5 chapters"     conf 2, prog 0.30 [🔴]  (1.5/5)

Pick one per objective:
A) 🚀 SHIP — keep going, no changes
B) 🔄 PIVOT — change scope or KR
C) 💀 KILL — abandon, capture lesson
```

> **User:** Ship 1, 2, 3. Kill 4 — the proposal was a stretch goal and I'm not blocked enough to want it.

> **Agent:**
> Recorded. Mid-quarter audit:

```
2026-Q4 mid-quarter audit (Nov 12):

✅ obj-1 SHIP — on track, beta launches week 9
✅ obj-2 SHIP — 8/12 books, will likely over-deliver
✅ obj-3 SHIP — race is week 7, taper is on
⬛ obj-4 KILL — was a stretch, freeing 4hrs/week back

🎁 You just freed 4 hours/week for 7 weeks. Want to add a replacement objective?
   Suggestions based on your existing KRs:
   - "Hit $25k MRR instead of $20k" (stretch obj-1 KR)
   - "Write 1 Substack post per week"
   - "Ship 1 side feature you keep deferring"

Lessons captured:
  - Don't take on stretch goals without a tested outline
  - 1 chapter in 6 weeks = signal to kill, not push
```

---

## Common Pitfalls

| Problem | Solution |
|---|---|
| User sets 8 objectives "because they're all important" | Enforce the 3-5 cap. Push back: *"If everything is a priority, nothing is. Pick the 3 that, if achieved, would make this quarter a win."* |
| KRs are vague ("improve product", "be healthier") | Force measurability. Rewrite: *"Improve product"* → "NPS ≥ 40 (from 22)". "Be healthier" → "Workout 3×/week for 13 weeks". |
| User updates progress without KR current values | Auto-derive progress from `current / target` for counter/number KRs; require explicit progress for milestone KRs. |
| Confidence stays at 7-8 even when progress falls | Decay alert: if progress < expected pace for 2+ weeks but confidence ≥ 7, prompt: *"Your progress says one thing and your confidence another. Which is real?"* |
| User abandons weekly check-ins after week 2 | Silent-decay detector flags this at week 3. After week 4 missed, push: *"Your quarter is dying from neglect, not difficulty. 5 min to check in?"* |
| User wants to keep a clearly dead goal "just in case" | Mid-quarter audit forces the conversation. If killed in audit but user keeps it "just in case," auto-flag with `[zombie]` tag and stop counting toward quarter progress. |
| Confusing OKRs with todos | Reframe: *"OKRs are outcomes. Todos are tasks. A todo for obj-1 might be 'schedule 5 design-partner calls' — that's the work; the KR is the result."* |
| User adds new objectives mid-quarter constantly | Cap mid-quarter additions at 1 (replacing a killed one). Beyond that, push to next quarter. |
| End-of-quarter retro skipped, user starts new quarter cold | Retro is mandatory to seed new quarter. The skill refuses to create a new quarter without a closed retro on the previous one (unless user explicitly says "skip retro"). |
| User confuses quarter calendar with personal cycle | Allow custom quarter naming: `H2-launch`, `Run-Q4-marathon`, `Birthday-90`. Just enforce 90-day window and weekly check-ins. |
| Same KR across multiple quarters with no progress | Detect repeat KRs (e.g., "hit $X MRR" appearing 3 quarters in a row). Surface: *"This is the 3rd quarter with this KR. What's different now? Or is it time to admit it?"* |
| Goals decay into busywork with no real outcomes | Quarterly retro's "Lessons" section forces the question: *"Which of your KRs actually moved the needle vs. were just measurable?"* — bias toward outcome-style KRs. |

---

## Verification Checklist

Before claiming the skill works end-to-end:

- [ ] First-run setup creates `~/.hermes/goals/` with `current.json`, `history/`, `retros/`
- [ ] 5-question intake generates a valid quarter JSON with 3-5 objectives and 2-4 KRs each
- [ ] "Stop List" (question 5) is captured in `stopped[]` and surfaced in retro
- [ ] Weekly check-in updates `checkins[]` with confidence per objective, KR current values, blocker
- [ ] Traffic-light status auto-computes from confidence + progress vs expected pace
- [ ] Week-6 mid-quarter audit prompt fires automatically (manual command works)
- [ ] SHIP / PIVOT / KILL decisions save with rationale
- [ ] KILL frees calendar awareness (optional: notify `pomodoro-coach` to de-prioritize)
- [ ] End-of-quarter retro writes to `retros/{quarter}-retro.md`
- [ ] Retro "seeds" auto-suggest carry-forward objectives for next quarter
- [ ] Cross-skill hooks: `weekly-review` reads active objectives; `standup-status-updater` includes quarter line
- [ ] Silent-decay detector flags missed check-ins (7d+) and declining confidence (2+ weeks)
- [ ] Repeat-KR detector surfaces goals appearing in ≥ 2 consecutive quarters
- [ ] All data stays local in `~/.hermes/goals/` — never uploaded
- [ ] Export to Markdown for accountability partner / coach / team meeting

---

## Data Sources & Accuracy

- **All data is user-provided.** The skill does not pull from external sources for goal-setting itself — it's a coaching tool, not an intelligence tool.
- **Calendar/date math** uses system `date` for week-of-quarter calculation. Expected pace formula: `current_week / 13` (assumes 13-week quarter; adjustable to 12 for fiscal calendars).
- **Confidence scoring** is purely user self-report. No calibration curve is applied — that's a deliberate choice. The agent suggests calibration prompts but never auto-adjusts the user's number.
- **KR progress** for `counter` and `number` types is auto-derived from `current / target`. For `milestone` and `binary` KRs, the user provides explicit progress.
- **Status traffic-lights** are deterministic rules:
  - `done` if all KRs at 1.0
  - `killed` if marked in mid-quarter audit or retro
  - `off_track` if confidence ≤ 3 OR (progress < 0.5 × expected_pace for 2+ weeks)
  - `at_risk` if confidence 4-5 OR (progress < expected_pace for 2+ weeks)
  - `on_track` otherwise
- **No personal data leaves the machine.** `~/.hermes/goals/` is local JSON. Export to Markdown is opt-in and user-initiated.
- **Historical quarters** are kept in `history/{quarter-id}.json` and never modified. This is the audit trail — useful for year-end reflections.
- **No "best practices" database.** The skill is a forcing function for the user, not an authority. If a goal doesn't fit the 3-5 / 2-4 / measurable / 90-day structure, the skill pushes back instead of working around it.

---