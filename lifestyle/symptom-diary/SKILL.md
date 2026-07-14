---
name: symptom-diary
description: "Track daily symptoms, medications, and supplements from chat — log severity 1-10, body system, flares; compute medication adherence; correlate symptoms with food/sleep/weather/stress; export doctor-ready PDF reports. All data local."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, health, symptoms, medication, supplements, chronic-illness, tracking, doctor-report, self-care]
    related_skills: [sleep-tracker, fitness-planner, habit-tracker, personal-crm]
---

# 🩺 Symptom Diary — 症状日记与用药追踪

> Log your symptoms, medications, and supplements by chat. Discover what triggers your flares, never miss a dose, and walk into your next doctor visit with a clean printable report. 用对话记录症状、药物、补充剂，找到触发因素，从不漏服药，并一键导出医生可读的病程报告。

---

## Overview

This skill turns Hermes into a personal symptom & medication journal. You describe how you feel in plain language (*"bad migraine this morning, 7/10, took sumatriptan"*) and Hermes logs severity, body system, medications taken, and adherence. Over time it surfaces correlations (weather, food, sleep, stress → symptoms), tracks adherence to prescriptions, and exports a structured report for your doctor. All data lives locally in `~/.hermes/symptom-diary/`.

| Capability | Description |
|------------|-------------|
| **Symptom logging** | Natural-language entry: severity 1-10, body system, duration, triggers |
| **Medication tracking** | Name, dose, schedule, refill date, prescribing doctor |
| **Supplement tracking** | Vitamins, herbs, OTC — separate from prescriptions |
| **Adherence %** | Did you take it on time? Streaks and missed-dose alerts |
| **Flare detection** | Auto-detect when severity > your baseline + spikes |
| **Correlation engine** | Find your personal triggers (weather, food, sleep, stress, cycle) |
| **Body-system map** | Group symptoms by system (neuro / GI / MSK / respiratory / skin / mood) |
| **Side-effect check** | Cross-reference new symptoms with recently-started meds |
| **Doctor report export** | PDF / Markdown summary with timeline + med list + flare frequency |
| **Refill alerts** | Warn N days before medication runs out |
| **Privacy-first** | All data local, never uploaded, no PHI in cloud APIs |

## When to Use

- *"I have a migraine, 7/10, took sumatriptan 50mg"*
- *"Log my morning: took 200mg modafinil, vitamins D and B12, no side effects"*
- *"Show me this month's symptom report"*
- *"Did I take my meds yesterday?"*
- *"What's my adherence this month?"*
- *"What seems to trigger my headaches?"*
- *"I started feeling dizzy 3 days ago"*
- *"Export my symptom log for my neurologist"*
- *"I think my new medication is causing nausea"*
- *"Add a new prescription: sertraline 50mg, daily"*
- *"Set a refill reminder for my prescription"*
- *"我胃疼3天了，5/10分"*
- *"我需要去复诊，帮我整理一份就诊报告"*

## Core Workflow

### Step 1: Initialize & Set Up Profile

On first mention, create the data directory and ask 3-4 setup questions:

```bash
mkdir -p ~/.hermes/symptom-diary
```

Setup questions (use sensible defaults if user skips):
1. **Track mode**: symptoms only / medications only / both (default: both)
2. **Primary conditions** (optional): e.g., migraine, IBS, ADHD, anxiety — used as context
3. **Severity scale**: 1-10 (default) or 1-5
4. **Time zone**: IANA tz for accurate timestamps

```json
{
  "profile": {
    "name": "User",
    "severity_scale": "1-10",
    "tracked_conditions": ["migraine"],
    "tracked_systems": ["neurological", "gastrointestinal", "musculoskeletal", "mood"],
    "time_zone": "America/Los_Angeles",
    "created_at": "2026-07-13T00:00:00Z",
    "doctor_visits": []
  },
  "medications": [],
  "supplements": [],
  "symptoms": [],
  "adherence_log": [],
  "insights": []
}
```

**Data files**:
- `~/.hermes/symptom-diary/profile.json` — user settings & conditions
- `~/.hermes/symptom-diary/medications.json` — prescriptions (name, dose, schedule, prescriber)
- `~/.hermes/symptom-diary/supplements.json` — OTC, vitamins, herbs
- `~/.hermes/symptom-diary/symptoms.json` — dated symptom entries
- `~/.hermes/symptom-diary/adherence_log.json` — daily check / missed-dose ledger
- `~/.hermes/symptom-diary/insights.json` — generated correlation cache
- `~/.hermes/symptom-diary/reports/` — generated doctor-report files

### Step 2: Log Symptoms via Natural Language

Parse the user's freeform sentence and extract:

- **Symptom** (free text, normalized to canonical form e.g. "migraine", "fatigue", "nausea")
- **Severity** (1-10, or qualitative: mild/moderate/severe → mapped to 3/6/9)
- **Body system** (auto-classified: neurological / GI / MSK / respiratory / skin / mood / cardiac / other)
- **Duration** (how long, or "ongoing" / "intermittent")
- **Triggers** (suspected: weather, food, stress, poor sleep, cycle)
- **Relief** (what helped: rest, water, medication, ice, none)
- **Notes** (anything else: time of day, context)

Example parses:

```
"Bad migraine, 7/10, took sumatriptan"
→ symptom: migraine, severity: 7, system: neurological,
  relief_med: sumatriptan

"Stomach has been upset since lunch, 4/10"
→ symptom: nausea, severity: 4, system: GI,
  onset: lunch, pattern: persistent

"Joint pain in both knees, stiffness 30 min in the morning, 5/10"
→ symptom: joint_pain, severity: 5, system: musculoskeletal,
  location: knees (bilateral), pattern: morning_stiffness_30min
```

Auto-classify body system via keyword dictionary (headache/migraine/dizzy/tinnitus → neurological; nausea/vomiting/diarrhea/constipation/bloating → GI; etc.) — fall back to "other" + ask user to confirm.

Auto-store:

```json
{
  "id": "2026-07-13-001",
  "date": "2026-07-13",
  "timestamp": "2026-07-13T09:15:00-07:00",
  "symptom": "migraine",
  "severity": 7,
  "body_system": "neurological",
  "duration": "ongoing",
  "triggers_suspected": ["stress", "poor_sleep"],
  "relief_taken": ["sumatriptan"],
  "notes": "started after standup meeting"
}
```

**Side-effect heuristic**: when a new symptom appears within 14 days of starting a new medication, auto-flag as `possible_side_effect: true` and surface in next report.

### Step 3: Manage Medications & Supplements

**Add prescription** via NL or guided form:

```
"Add prescription: sertraline 50mg, once daily in the morning,
started July 1, prescribed by Dr. Lee"
```

```json
{
  "id": "med-001",
  "name": "sertraline",
  "brand_name": "Zoloft",
  "dose_mg": 50,
  "dose_unit": "mg",
  "schedule": {
    "frequency": "daily",
    "times": ["08:00"],
    "with_food": true
  },
  "started_at": "2026-07-01",
  "prescriber": "Dr. Lee",
  "purpose": "anxiety",
  "refill_date": "2026-08-15",
  "pills_remaining": 18,
  "active": true,
  "side_effects_watched": ["nausea", "insomnia", "fatigue"]
}
```

**Add supplement** similar shape, but `prescriber` optional and `purpose` is the user's own goal (energy / sleep / immunity).

**Stop / pause medication**: set `active: false`, archive in `medications.json` with `stopped_at` and `stopped_reason`. Preserves history for reports.

**Refill tracking**: subtract from `pills_remaining` based on `schedule.frequency`; auto-warn when ≤ 7 days of supply remain. Optionally write a note to a refill-todo file.

### Step 4: Daily Adherence Check

Two complementary intake modes:

**(a) Inline logging**: when user logs a symptom, ask *"did you take all your scheduled meds this morning?"* — quick yes/no/partial.

**(b) Morning/evening check-in** (cron-friendly):

```
"Good morning! Today's meds scheduled:
  - sertraline 50mg (08:00)
  - vitamin D 2000 IU (08:00)
Confirm with 'all taken' or list what you missed."
```

Compute adherence:

```
adherence_% = (doses_taken / doses_scheduled) × 100
             over a rolling window (default 30 days)
```

Streaks: longest current streak of 100% adherence, broken-streak alerts.

```json
{
  "date": "2026-07-13",
  "scheduled": [
    {"med_id": "med-001", "name": "sertraline", "scheduled_time": "08:00", "taken": true,  "actual_time": "08:15"},
    {"med_id": "med-002", "name": "vitamin D",  "scheduled_time": "08:00", "taken": true,  "actual_time": "08:15"}
  ],
  "missed": [],
  "adherence_today": 1.0
}
```

### Step 5: Detect Flares & Patterns

**Flare definition** (user-tunable, default):
- A symptom's severity is > user's 30-day mean + 1.5 standard deviations, OR
- A previously-absent symptom appears ≥ 3 times in 7 days, OR
- Severity ≥ 8 on a single day for any tracked condition

When a flare is detected, mark entries with `flare: true` and group into a "flare episode" with start/end dates, peak severity, and what the user did for relief.

Show:

```
⚠️ FLARE DETECTED: migraine
  2026-07-10 to 2026-07-13 (4 days)
  Peak severity: 9/10 on 2026-07-12
  Episodes: 6
  Average baseline (last 60 days): 3.2/10
  Triggers co-occurring: stress ≥7/10 on 3 of 4 days, sleep <6h on 2 days
```

### Step 6: Correlation Engine

After 21+ days of data, run correlations per symptom against:

| Factor | Source |
|--------|--------|
| Sleep duration / quality | `sleep-tracker` data (if available, else ask) |
| Stress rating | user-entered 1-10 |
| Weather | local temp, pressure, humidity (optional, via `wttr.in` or local input) |
| Caffeine / alcohol | `sleep-tracker` factors or user input |
| Menstrual cycle | user-entered phase (optional) |
| New medications | date when a med was started (look for side-effect pattern) |

Output ranked:

```
📊 What seems to trigger YOUR migraines (last 60 days, n=34):

  ⚠️  Poor sleep      r = +0.72  ← biggest trigger
  ⚠️  Stress ≥ 7/10   r = +0.58
  →   Barometric drop  r = +0.31  (n=12, weak)
  →   Skipped meal     r = +0.18  (n=8, need more data)
  ✅  Exercise day     r = -0.41  ← biggest protector
```

Interpretation rules:
- |r| > 0.5: strong effect (high confidence)
- |r| 0.3–0.5: moderate (suggestive)
- |r| < 0.3: weak / insufficient data
- n < 10: show "needs more data" instead of r value

### Step 7: Doctor-Ready Report

When user says *"export report"*, *"for my doctor"*, or *"for my appointment"*, generate a structured file in `~/.hermes/symptom-diary/reports/`. Choose format by user request:

**Markdown** (default — easy to print, paste into email, or convert to PDF):

```markdown
# Symptom & Medication Report
**Patient**: [name from profile]
**Date range**: 2026-06-13 to 2026-07-13 (30 days)
**Generated**: 2026-07-13

## Active Medications
| Medication | Dose | Schedule | Started | Prescriber |
|------------|------|----------|---------|------------|
| sertraline | 50 mg | daily 08:00 | 2026-07-01 | Dr. Lee |
| sumatriptan | 50 mg | PRN | 2020-03-15 | Dr. Patel |

## Active Supplements
- Vitamin D 2000 IU daily
- Magnesium glycinate 400 mg nightly

## Symptom Frequency (30 days)
| Symptom | Days | Avg severity | Peak | Trend |
|---------|------|--------------|------|-------|
| Migraine | 11 | 5.4/10 | 9/10 (Jul 12) | ↑ 30% vs prior 30d |
| Fatigue | 18 | 4.1/10 | 7/10 | → |
| Nausea | 4 | 3.0/10 | 5/10 | ↓ |

## Adherence
- 30-day adherence: 89% (8 missed doses out of 75 scheduled)
- Longest streak: 14 days

## Flares
- **2026-07-10 to 2026-07-13**: migraine flare (peak 9/10, 4 days)

## Notable Patterns
- Migraines 72% more frequent on sleep <6h nights
- Nausea appeared 5 days after starting sertraline (2026-07-06)
- Adherence drops on weekends (75% vs 95% weekdays)

## Patient-Reported Triggers
- Stress (high-confidence)
- Poor sleep (high-confidence)
- Skipped meals (moderate)

## Notes
[summarized notes from the period]
```

**PDF** (use `pandoc` or `pdf-toolkit` skill if available, else instruct user):

```bash
pandoc reports/2026-07-13-report.md -o reports/2026-07-13-report.pdf
```

Filename: `~/.hermes/symptom-diary/reports/{date}-symptom-report.md`

### Step 8: Refill & Appointment Reminders

When a medication's `refill_date` is within 7 days, surface:

```
💊 Refill alert: sertraline 50mg — 5 days of pills remaining (refill by Aug 15)
```

When user mentions an upcoming appointment, ask for date + doctor + reason; save to `profile.doctor_visits[]` and prepare a tailored report 1 day before.

## Example Invocations

### Example 1: First-time setup and first log

> **User**: I want to start tracking my symptoms and medications.
>
> **Agent**: I'll set up your symptom diary. Quick setup:
> 1. What are you mainly tracking? (symptoms / medications / both — default both)
> 2. Any specific conditions? (e.g., migraine, IBS, ADHD, anxiety)
> 3. Severity scale: 1-10 (default) or 1-5?
> 4. Your time zone (for accurate timestamps)?
>
> **User**: Both. I have chronic migraines and anxiety. 1-10. PST.
>
> **Agent**: Profile saved. `~/.hermes/symptom-diary/profile.json` initialized with:
>
> | Setting | Value |
> |---------|-------|
> | Tracked conditions | migraine, anxiety |
> | Severity scale | 1-10 |
> | Time zone | America/Los_Angeles |
> | Body systems tracked | neuro, mood, GI (default) |
>
> Add your active medications now, or just say things like *"I have a migraine, 7/10, took sumatriptan"* to log symptoms.
>
> ---
>
> **User** (next morning): Woke up with a migraine, 6/10, no aura. Took sumatriptan 50mg at 7am. Slept poorly — maybe 5 hours.
>
> **Agent**: Logged 2026-07-13:
>
> | Field | Value |
> |-------|-------|
> | Symptom | migraine (no aura) |
> | Severity | 6/10 |
> | System | neurological |
> | Relief | sumatriptan 50mg @ 07:00 |
> | Suspected triggers | poor sleep |
>
> Adherence check for today — you have **sertraline 50mg** scheduled at 08:00. Taken? (yes / no / skipped)

### Example 2: Three weeks later — discovering a side effect

> **User**: I think my sertraline is making me nauseous. Started about a week ago.
>
> **Agent**: Let me check. Cross-referencing `symptoms.json` × `medications.json`:
>
> **Nausea episodes since starting sertraline (2026-07-01)**: 8 episodes over 21 days (38% of days).
> **Nausea episodes before sertraline**: 1 in the prior 60 days.
>
> Onset: nausea first appeared 2026-07-06, **5 days after starting sertraline**. This matches the typical SSRI GI-adjustment window (days 5-14).
>
> | Date | Symptom | Severity | Notes |
> |------|---------|----------|-------|
> | 2026-07-06 | nausea | 3 | mild, after breakfast |
> | 2026-07-09 | nausea | 5 | lasted 2h |
> | 2026-07-12 | nausea | 6 | morning, before meds |
>
> ⚠️ **Possible side effect** flagged. Recommendation: report to Dr. Lee. Common strategies:
> - Take sertraline with food (you're currently taking on empty stomach at 08:00)
> - Temporary nausea often resolves in 2-3 weeks
>
> Want me to draft a message to your doctor, or add a note to your next appointment report?
>
> **User**: Draft the message.
>
> **Agent** *(drafts email to Dr. Lee's office with timeline, severity trend, and proposed discussion points)*.

### Example 3: Preparing for a doctor visit

> **User**: I have an appointment with Dr. Lee on July 18. Help me prepare a report.
>
> **Agent**: Got it. Generating report for 2026-06-18 to 2026-07-18 (30 days). Saving to `~/.hermes/symptom-diary/reports/2026-07-13-report.md`.
>
> ```
> # Symptom & Medication Report
> **Patient**: User
> **Date range**: 2026-06-18 to 2026-07-18 (30 days)
> **Prepared for**: Dr. Lee appointment 2026-07-18
>
> ## Active Medications
> | Medication | Dose | Schedule | Started | Adherence (30d) |
> |------------|------|----------|---------|-----------------|
> | sertraline | 50 mg | daily 08:00 | 2026-07-01 | 88% |
> | sumatriptan | 50 mg | PRN (avg 4x/wk) | 2020-03-15 | n/a |
>
> ## Active Supplements
> - Vitamin D 2000 IU daily
> - Magnesium glycinate 400 mg nightly
>
> ## Symptom Frequency (30 days)
> | Symptom | Days | Avg severity | Peak | Trend |
> |---------|------|--------------|------|-------|
> | Migraine | 14 | 5.8/10 | 9/10 (Jul 12) | ↑ |
> | Nausea | 8 | 4.5/10 | 6/10 | ↑ (new, post-sertraline) |
> | Fatigue | 12 | 4.0/10 | 6/10 | → |
>
> ## Notable Patterns
> - **Nausea new since sertraline start**: 5-day delay from med start
> - **Migraine peaks**: correlated with sleep <6h (r = +0.72)
> - **Weekend adherence drop**: 75% vs 95% weekdays
>
> ## Questions for Dr. Lee
> 1. Nausea timeline consistent with SSRI GI adjustment? Continue or dose-titrate?
> 2. Sumatriptan use 4×/wk — discuss preventive option?
> 3. Migraine-sleep link — sleep study referral?
> ```
>
> Open in your favorite editor, or convert to PDF with:
> `pandoc reports/2026-07-13-report.md -o reports/2026-07-13-report.pdf`
>
> Want me to add this to your `profile.doctor_visits[]` with a reminder 1 day before the appointment?

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User describes multiple symptoms in one message | Parse each: "I have a headache 6/10, nausea 4/10, and I'm exhausted" → 3 separate log entries with same timestamp. |
| User says "took my meds" without specifying which | Don't guess. Ask: "which ones — sertraline, vitamin D, or all of them?" |
| Severity scale is 1-5 in profile but user says "7" | Convert or ask. Better: enforce the configured scale in prompts. |
| Time-zone confusion across travel | Always store in local time + IANA tz. Detect travel: "I flew to NYC" → ask if tz should change. |
| User logs same symptom 3×/day | Allow multiple entries/day — track duration and pattern. Don't dedupe. |
| Correlation flagged for new med → symptom | Use 5-21 day window; some side effects emerge late. Don't over-fit. |
| User wants to import from Apple Health / Fitbit | Out of scope. Note: manual entry only. Suggest `format-converter` skill to import CSV. |
| Missed dose without explicit "no" | Adherence shows "unknown" not 0%. Don't fabricate missed doses. |
| Adherence math: PRN (as-needed) meds | Exclude from adherence denominator. PRN = *event*, not schedule. |
| Refill math: user changes dose | Update `pills_remaining` math when schedule or dose changes; warn "previous refill calc invalid, reset?" |
| Doctor-report reveals user-identifiable data | Confirm with user before exporting. All export to local path, no cloud. |
| User says "I want to stop sertraline" | **Hard stop**: do not edit prescription. Always say: "Talk to your prescriber before stopping. I can log that you want to discuss discontinuation at your next visit." |
| Multiple prescriptions for same med | Detect duplicate name + dose. Prompt: "sertraline 50mg is already in your list. Edit, replace, or add as separate (e.g., different brand)?" |
| "I have a migraine" vs "I have a tension headache" | Distinct canonical forms; if unsure, ask: "is this your usual migraine pattern or different?" |
| Cycle / menstruation correlation without explicit user opt-in | Privacy-sensitive. Always ask once: "would you like to track cycle phase for correlations?" — store as boolean, never required. |

## Verification Checklist

Before claiming the skill works, verify:

- [ ] `~/.hermes/symptom-diary/` created on first run
- [ ] `profile.json`, `medications.json`, `supplements.json`, `symptoms.json` all valid JSON
- [ ] NL symptom parser correctly extracts: name, severity, system, duration, triggers
- [ ] Body system auto-classification has a working keyword dictionary with "other" fallback
- [ ] Severity 1-10 stored as integer, validated against range
- [ ] Multiple symptoms in one message → multiple log entries
- [ ] Cross-midnight timestamps handled (e.g., woke at 2am with migraine)
- [ ] Adherence % correct: taken / scheduled × 100, PRN excluded
- [ ] Streak counter resets on first missed dose
- [ ] Flare detection uses 30-day mean + 1.5 SD threshold (or user-configured)
- [ ] Side-effect heuristic: new symptom within 14 days of new med → `possible_side_effect: true`
- [ ] Correlation engine requires n ≥ 10 to show r value, otherwise "needs more data"
- [ ] Doctor report generates valid Markdown with all required sections
- [ ] Doctor report file is saved to `reports/` directory with date in filename
- [ ] Refill warning fires when pills_remaining ≤ 7 days of supply
- [ ] Stopping a medication requires user confirmation and never silently edits
- [ ] Cycle tracking is opt-in only, never assumed
- [ ] No external API calls; all data local; no PHI in any system telemetry
- [ ] Time zone is IANA format, stored with every timestamp
- [ ] All numbers reproducible from raw `symptoms.json` + `adherence_log.json`

## Data Sources & Accuracy

This skill is **fully local-first**. No cloud sync, no third-party APIs, no PHI in telemetry.

**What powers the analysis**:
- **Symptom data** → user-entered via natural language
- **Body system classification** → built-in keyword dictionary (curated, transparent)
- **Adherence math** → simple ratio, fully transparent
- **Correlations** → Pearson r via Python stdlib (`statistics`) or inline formula
- **Side-effect heuristic** → time-window rule (5-21 days post med-start), based on common SSRI/stimulant patterns from public prescribing info
- **Doctor report** → Markdown, optionally rendered to PDF by `pandoc` (which the user installs; skill doesn't require it)

**Accuracy caveats**:
- **Manual entry is the source of truth** — there's no wearable-grade precision. Severity is subjective; users should aim for consistent 1-10 use over time (e.g., always "your worst recent migraine = 10", "fully functional = 1").
- **Self-classified body system** can be wrong; the keyword dictionary is a guide, not a diagnosis. Always confirm with the user on first log of an unfamiliar symptom.
- **Correlations are not causation**. "Sleep <6h correlates with migraine" does not prove sleep deprivation *causes* your migraines — only that they co-occur in your data.
- **Side-effect heuristic is suggestive, not diagnostic**. Nausea 5 days after starting sertraline is *consistent with* SSRI GI-adjustment, not proof. Always defer to prescriber.
- **Drug-interaction checking is NOT in scope**. This skill does not check for interactions between meds. Use a pharmacist or dedicated interaction tool for that.
- **Educational use only**. Not a medical device. Not a substitute for clinical advice. If symptoms are severe, sudden, or worsening, advise the user to contact a clinician.

**Storage path**: `~/.hermes/symptom-diary/` — survives across Hermes sessions, owned by user, deletable anytime. Doctor reports are written only to a user-confirmed local path; no email or upload is performed automatically.

---

## 🤝 Integration Tips

- **With `sleep-tracker`**: pull sleep duration / quality to correlate with symptom onset. (Read-only — skill never modifies sleep data.)
- **With `fitness-planner`**: log evening workouts as a factor; check if they correlate with reduced pain or improved energy.
- **With `habit-tracker`**: track "took all meds" as a daily habit; symptom-diary measures whether adherence is *actually* happening.
- **With `personal-crm`**: save a doctor contact (name, specialty, last visit, next visit) — link the appointment date to the doctor report.
- **Cron-ready**: schedule a daily 9pm check-in *"any symptoms to log? meds taken?"* and a weekly Sunday summary. A monthly auto-export to `reports/` makes doctor visits effortless.

---

*Your body is the most important dataset you own. Track it, see the patterns, and bring the data to your next visit.*
