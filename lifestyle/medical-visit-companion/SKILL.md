---
name: medical-visit-companion
description: "End-to-end doctor visit companion — pre-visit briefing pack (symptom timeline, medication list, question list), live appointment mode (clear-language question prompts + note-taking), post-visit summary (diagnosis, prescriptions, follow-up plan), lab/imaging result decoder, and appointment+refill reminders. Pairs with symptom-diary. All data local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, health, medical, doctor, visit, appointment, questions, diagnosis, prescription, lab-results, imaging, follow-up, second-opinion, patient-advocacy]
    related_skills: [symptom-diary, sleep-tracker, personal-crm, renewal-reminder, habit-tracker]
---

# 🩺 Medical Visit Companion — 就诊伴侣：从诊前准备到诊后追踪

> Most patients forget 80% of what the doctor says within an hour. They forget questions they meant to ask, don't know how to describe symptoms accurately, leave with vague instructions, and lose the lab report in their email. This skill turns Hermes into a calm, organized advocate on your side of the exam table: **before** the visit you get a one-page briefing pack; **during** the visit you get clear-language prompts and notes; **after** you get a structured follow-up plan with reminders, and you can decode any lab/imaging result on demand.

---

## Overview

This skill is the patient-side counterpart to `symptom-diary`. Where `symptom-diary` logs daily state, this skill handles the **visit lifecycle**: prep → live → follow-up → result decoding → next appointment. Every piece of information stays in `~/.hermes/medical-visits/` as plain Markdown + JSON, fully local and private.

| Capability | Description |
|------------|-------------|
| 📋 **Pre-visit briefing pack** | One-page PDF/Markdown: symptom timeline (pulls from symptom-diary if present), current medications + supplements, allergies, relevant family history, top questions for the doctor, space for vitals the nurse will measure |
| 🗣️ **Clear-language question prompts** | During the visit, ask plain-English (or Chinese) prompts like *"What are the 3 most likely causes?"*, *"What symptoms mean I should come back immediately?"*, *"What are the side effects vs. benefits of this medication?"* — generated as a checklist you can read off your phone |
| ✍️ **Note-taking mode** | Paste what the doctor says; Hermes structures it into S/O/A/P (Subjective/Objective/Assessment/Plan) or SOAP notes, extracts prescriptions and follow-ups |
| 🔬 **Lab result decoder** | Paste CBC / metabolic panel / lipid panel / HbA1c / TSH / imaging report — Hermes explains every flag, what's normal for your age/sex, what to ask the doctor |
| 💊 **Post-visit plan tracker** | New medications (with start/stop dates, dosing, interactions to flag), referrals, imaging orders, lab re-test dates, "watch for X" symptoms |
| 📅 **Appointment + refill reminders** | Auto-reminder 7 days / 1 day before; medication refill countdown; "due for re-check" alerts |
| 🔁 **Second-opinion mode** | Compile all visit notes + labs into a one-page brief to hand a new doctor |
| 🌍 **EN/CN/ES bilingual** | Question prompts and explanations generated in your language |
| 💾 **Local-first privacy** | All data in `~/.hermes/medical-visits/`; nothing leaves your machine |

## When to Use

- *"I have an appointment with Dr. Lee next Tuesday — prep me"*
- *"Help me describe this chest pain to the cardiologist"*
- *"Generate 8 smart questions to ask the gastroenterologist about my IBS"*
- *"The doctor said a bunch of stuff — can you structure it into notes?"*
- *"Decode my CBC — WBC 12.4, RBC 4.1, hemoglobin 13.2…"*
- *"What does my MRI report mean in plain English?"*
- *"I'm starting metformin — what should I watch for?"*
- *"When is my next follow-up and what should I do before then?"*
- *"I need a second opinion — package everything for Dr. Garcia"*
- *"我下周三看骨科，帮我准备"*
- *"帮我解读一下我的甲功报告"*
- *"我忘了医生刚才说了什么，把录音文字整理一下"*

## Core Workflow

### Step 1 — Visit registration

When the user mentions an upcoming appointment, register it:

```json
{
  "id": "visit-2026-09-02-cardiologist",
  "type": "specialist",                    // primary_care | specialist | urgent_care | telehealth | lab | imaging | dental | vision | mental_health
  "specialty": "cardiology",
  "doctor": "Dr. Sarah Lee",
  "facility": "Pacific Heart Center",
  "address": "1234 Bay St, Suite 500",
  "date": "2026-09-02",
  "time": "14:30",
  "reason": "palpitations and occasional chest tightness, 3 weeks",
  "is_new_patient": false,
  "referral_from": "Dr. Chen (primary care, 2026-08-20)",
  "questions_to_ask": [],                  // populated in Step 2
  "reminder_days_before": [7, 1],
  "status": "scheduled"                    // scheduled|completed|cancelled|no_show
}
```

Store under `~/.hermes/medical-visits/visits.json`. Also create `~/.hermes/medical-visits/personal-health-profile.json` (one-time, populated interactively):

```json
{
  "name": "Alex",
  "dob": "1988-03-15",
  "sex": "F",
  "height_cm": 165,
  "weight_kg": 62,
  "blood_type": "O+",
  "allergies": ["penicillin (hives)", "shellfish"],
  "chronic_conditions": ["hypothyroidism"],
  "current_medications": [
    {"name": "levothyroxine", "dose": "50mcg", "frequency": "daily AM", "started": "2020-04", "prescriber": "Dr. Chen"}
  ],
  "current_supplements": ["vitamin D 2000 IU", "omega-3"],
  "past_surgeries": [{"year": 2018, "procedure": "appendectomy"}],
  "family_history": [
    {"relation": "father", "condition": "atrial fibrillation, dx age 60"},
    {"relation": "mother", "condition": "type 2 diabetes"}
  ],
  "primary_doctor": "Dr. Chen, Palo Alto Medical Foundation",
  "pharmacy": "CVS #4521, 555 University Ave",
  "insurance": {"plan": "Anthem PPO", "member_id": "ABC123456"}
}
```

**First time:** if `personal-health-profile.json` doesn't exist, run a brief onboarding chat to populate it. Offer a `--skip` flag and a template for the user to fill in themselves.

### Step 2 — Pre-visit briefing pack (7-day window)

When the user says *"prep me for my [specialty] visit on [date]"*, generate `briefing-{visit_id}.md`:

```markdown
# 📋 Visit Briefing — Dr. Sarah Lee, Cardiology
**Date:** Tuesday, 2026-09-02, 2:30 PM
**Reason:** Palpitations & occasional chest tightness (3 weeks)
**Location:** Pacific Heart Center, 1234 Bay St, Suite 500

## 🩺 Symptom Timeline (last 14 days)
| Date | Symptom | Severity 1-10 | Duration | Notes |
|------|---------|--------------|----------|-------|
| 09-01 | palpitations | 6 | ~10 min | after coffee, no exercise |
| 08-28 | palpitations | 7 | ~15 min | woke me at 3 AM |
| 08-24 | chest tightness | 4 | ~5 min | after climbing stairs |
| ... | | | | |

## 💊 Bring This List
**Medications:** levothyroxine 50mcg daily AM
**Supplements:** vitamin D 2000 IU, omega-3
**Allergies:** ⚠️ penicillin (hives), shellfish

## 👪 Family History to Mention
- Father: atrial fibrillation, dx age 60
- Mother: type 2 diabetes

## 🎯 Top Questions to Ask (prioritized)
1. **What's the most likely cause of my palpitations given my thyroid history?**
2. **Do I need an ECG / Holter monitor / event recorder today or ordered separately?**
3. **Are my symptoms dangerous — when should I go to the ER instead of waiting?**
4. **Could any of my medications or supplements be contributing?**
5. **What's the threshold for medication vs. watchful waiting?**
6. **Are there lifestyle changes (caffeine, sleep, stress) worth trying first?**
7. **When should I follow up if symptoms don't improve?**

## 📝 Vitals the nurse will measure
Prepare: blood pressure (recent home readings?), heart rate, weight, height

## 🗒️ Notes During the Visit
[ leave this section blank to fill in during the appointment ]
```

**How to generate this:**
1. Pull symptoms from `~/.hermes/symptom-diary/symptoms.json` if it exists; otherwise ask the user to describe recent symptoms in chat
2. Pull medications, allergies, family history from `personal-health-profile.json`
3. Generate specialty-specific questions (see Step 4 below)
4. Save the briefing as both Markdown and a clean PDF (use `pandoc` if available, otherwise keep as MD)

### Step 3 — Live appointment mode

During the visit, the user can either:
- **Dictate/paste** what the doctor says after the visit, or
- **Run live mode** where they ask questions one at a time and Hermes prompts them with the next question on their list

**Live question prompts** (generated based on specialty + reason):

| Specialty | Sample "smart" questions to ask |
|-----------|-------------------------------|
| Cardiology | "What's the difference between benign palpitations and AFib in my case?" |
| Dermatology | "Is this lesion worth a biopsy? What changes would make it urgent?" |
| Orthopedics | "What does the MRI actually show — is surgery inevitable or can PT help first?" |
| Gastroenterology | "If it's IBS, what's the stepwise treatment plan and when do we re-evaluate?" |
| Mental health | "How will we measure progress — what does 'better' look like in 4 weeks?" |
| Primary care | "Which of my vaccines and screenings are overdue?" |

For each question, also generate **3 plain-language follow-ups** so the patient can drill down:

```
Q: What are the side effects of this medication?
  → 1. What % of patients get each side effect?
  → 2. Which side effects mean I should stop immediately?
  → 3. Is there an alternative with fewer side effects?
```

### Step 4 — Post-visit note structuring (SOAP)

When the user pastes raw notes / dictation / recording transcript, structure into SOAP:

```markdown
# Visit Note — 2026-09-02, Cardiology
**Patient:** Alex (F, 38)
**Provider:** Dr. Sarah Lee, Pacific Heart Center

## S — Subjective
- Chief complaint: palpitations x 3 weeks, occasional chest tightness
- Frequency: ~3 episodes/week, mostly evenings, lasting 5-15 min
- Triggers: caffeine, sleep deprivation, sometimes none
- Associated: mild lightheadedness, no syncope
- Relevant history: hypothyroidism on levothyroxine (TSH normal 2026-06)

## O — Objective
- BP 128/82, HR 88 (in office), regular rhythm
- ECG: NSR, no acute ST changes
- Labs ordered: TSH, CBC, BMP, troponin

## A — Assessment
- Likely benign premature ventricular contractions (PVCs)
- Rule out atrial fibrillation, thyroid re-check
- Differential: anxiety, caffeine, thyroid, structural

## P — Plan
1. **24-hr Holter monitor** — schedule at front desk, wear for 24h
2. **TSH re-check** — go to lab today if possible
3. **Reduce caffeine** to <1 cup/day for 2 weeks as a trial
4. **No new medications** today — review Holter results in 1 week
5. **Red flags to come back immediately:** sustained palpitations >30 min, syncope, chest pain with shortness of breath

## 💊 New Prescriptions
(none today)

## 📅 Follow-up
- Holter results review: 2026-09-09 (call)
- Office re-check: 2026-09-23 (in person)
- If symptoms worsen before then: call nurse line, don't wait
```

Save as `notes-{visit_id}.md`. Extract structured data into `visits.json`:

```json
{
  "id": "visit-2026-09-02-cardiologist",
  "diagnosis": ["suspected PVCs", "thyroid re-check ordered"],
  "prescriptions": [],
  "labs_ordered": ["TSH", "CBC", "BMP", "troponin"],
  "imaging_ordered": [],
  "referrals": [],
  "follow_up_date": "2026-09-23",
  "warning_signs": ["sustained palpitations >30 min", "syncope", "chest pain + SOB"],
  "instructions": ["caffeine <1 cup/day for 2 weeks", "schedule Holter at front desk"],
  "completed": "2026-09-02"
}
```

### Step 5 — Lab / imaging result decoder

When the user pastes a lab report (CBC, BMP, lipid, HbA1c, TSH, urinalysis) or imaging report (X-ray, MRI, CT, ultrasound), Hermes:

1. **Parses** each value into a structured table (test, result, unit, reference range, flag if out)
2. **Explains in plain language** what each abnormal value means — using reference ranges appropriate for the patient's age/sex from `personal-health-profile.json`
3. **Severity-tags** each abnormal: 🟢 mildly off (often normal variant), 🟡 notably off (discuss with doctor), 🔴 critical (call doctor today)
4. **Generates 3-5 questions** the patient should ask the doctor about the abnormal findings
5. **Suggests** lifestyle/diet factors that can move each value (without diagnosing)

Example output:

```markdown
# 🔬 CBC Decoded — drawn 2026-09-02
| Test | Your Value | Reference Range | Flag | Meaning |
|------|-----------|-----------------|------|---------|
| WBC | 12.4 ×10⁹/L | 4.0-11.0 | 🔴 high | infection, inflammation, or stress response — call doctor today |
| RBC | 4.1 ×10¹²/L | 3.9-5.2 (F) | 🟢 normal | healthy oxygen-carrying capacity |
| Hemoglobin | 13.2 g/dL | 12.0-15.5 (F) | 🟢 normal | no anemia |
| Hematocrit | 39% | 36-46 (F) | 🟢 normal | matches hemoglobin |
| Platelets | 245 ×10⁹/L | 150-400 | 🟢 normal | healthy clotting |

## ⚠️ Critical Findings (1)
- **WBC elevated at 12.4** — most often means your body is fighting something (infection, inflammation, sometimes stress/cortisol). At this level + palpitations, your cardiologist will likely want to know if you've had recent illness, dental work, or new medications.

## 🎯 Questions for Dr. Lee
1. Does the elevated WBC change your interpretation of my palpitations?
2. Should we order a differential or repeat in 1 week?
3. Could my levothyroxine dose be affecting this?
4. Do I need any additional workup before starting treatment?

## 🍎 Lifestyle Factors That Move WBC
(many factors; only your doctor can interpret in your context — these are general)
- Recent illness / vaccination / dental work → transient elevation
- Smoking → chronic mild elevation
- Stress / intense exercise → acute elevation
```

**Important disclaimer (always included):** *"I'm not your doctor. This decoder explains what each value means in general terms, not what it means for you specifically. Always discuss abnormal results with your provider."*

### Step 6 — Follow-up + reminders

Maintain `~/.hermes/medical-visits/reminders.json`:

```json
{
  "active": [
    {"date": "2026-09-09", "type": "call_clinic", "reason": "Holter results review with Dr. Lee", "visit_id": "visit-2026-09-02-cardiologist"},
    {"date": "2026-09-23", "type": "office_visit", "reason": "Cardiology re-check", "visit_id": "visit-2026-09-02-cardiologist"},
    {"date": "2026-10-15", "type": "lab", "reason": "Repeat TSH", "related_to": "visit-2026-09-02-cardiologist"},
    {"date": "2026-10-01", "type": "refill", "reason": "Levothyroxine refill (last bottle 2026-08-28)", "medication": "levothyroxine 50mcg"}
  ]
}
```

**Daily / cron checks:**
- 7 days before any scheduled visit → *"Reminder: cardiology appointment next Tue 9/2 at 2:30 PM. Want me to refresh your briefing pack?"*
- 1 day before → *"Reminder: tomorrow at 2:30 PM — Pacific Heart Center, Suite 500. Bring your medication list."*
- Lab/imaging due dates → auto-flag
- Refill countdowns based on dosage (e.g. 30-day supply → alert at day 23)

### Step 7 — Second-opinion packaging

When the user wants a second opinion, compile everything into `second-opinion-brief.md`:

```markdown
# Second-Opinion Brief — for Dr. Garcia, Cardiology
**Patient:** Alex (F, 38), DOB 1988-03-15
**Insurance:** Anthem PPO, member ABC123456
**Primary:** Dr. Chen, PAMF

## 📅 Visits on File
- 2026-09-02: Dr. Lee (cardiology) — palpitations workup, SOAP attached
- 2026-08-20: Dr. Chen (PCP) — initial referral, attached

## 🔬 Labs on File
- 2026-09-02: CBC (WBC elevated), TSH, BMP, troponin — full report attached
- 2026-06-15: TSH 2.1 (normal)

## 🖼️ Imaging on File
- (none yet — Holter pending)

## 💊 Current Medications
- Levothyroxine 50mcg daily AM

## 🎯 Specific Questions for Second Opinion
1. Given normal TSH but elevated WBC and palpitations, do you agree with watchful waiting?
2. Should the Holter be 48-hour instead of 24-hour given symptom frequency?
3. Are there structural causes (echo?) you'd want to rule out first?
```

This brief respects patient privacy: names, member IDs, and full addresses are local-only fields; the user can decide what to include or redact.

## Example Invocations

### Example 1 — Cardiologist prep

```
User: I have an appointment with Dr. Lee the cardiologist next Tuesday at 2:30 — palpitations and chest tightness for 3 weeks. Help me prep.

Hermes:
[INFO] Loading ~/.hermes/medical-visits/personal-health-profile.json — found.
[INFO] Loading ~/.hermes/symptom-diary/symptoms.json — last 14 days of palpitations entries found.
[EXEC] Generating briefing pack for visit-2026-09-02-cardiologist…

📋 Visit Briefing — Dr. Sarah Lee, Cardiology
   Tue 2026-09-02, 2:30 PM @ Pacific Heart Center, Suite 500

   Symptom Timeline (last 14 days):
   09-01  palpitations  6/10  ~10 min  after coffee
   08-28  palpitations  7/10  ~15 min  woke at 3 AM
   08-24  chest tightness  4/10  ~5 min  climbing stairs
   [4 more entries from symptom-diary]

   Top 7 Questions to Ask (ranked by impact):
   1. Most likely cause given my thyroid history?
   2. ECG / Holter / event recorder today or ordered?
   3. Symptoms that mean go to ER vs. wait?
   4. Could levothyroxine or supplements contribute?
   5. Meds vs. watchful waiting — threshold?
   6. Lifestyle (caffeine, sleep) worth trying first?
   7. When to follow up if no improvement?

   Saved to: ~/.hermes/medical-visits/briefing-visit-2026-09-02-cardiologist.md
   Reminder set: 7 days out (2026-08-26) and 1 day out (2026-09-01)

Want me to print this as a clean PDF? (pandoc available — yes/no)
```

### Example 2 — Live visit note structuring

```
User: Ok I just got out. The doctor said: palpitations likely benign PVCs, ordered a 24-hour Holter monitor, told me to schedule at front desk. Wants TSH re-check today. Says reduce caffeine to less than one cup a day for two weeks. No new meds. Follow up in person in 3 weeks on the 23rd. Red flags — sustained palpitations over 30 minutes, fainting, or chest pain with shortness of breath — come back immediately.

Hermes:
[EXEC] Structuring notes into SOAP for visit-2026-09-02-cardiologist…

# Visit Note — 2026-09-02, Cardiology
**Patient:** Alex (F, 38)
**Provider:** Dr. Sarah Lee, Pacific Heart Center

## S — Subjective
- Chief complaint: palpitations x 3 weeks, occasional chest tightness
- (pulled from your pre-visit briefing — kept consistent)

## O — Objective
- (captured during exam — fill in vitals if you have them)

## A — Assessment
- Likely benign PVCs; rule out AFib; thyroid re-check

## P — Plan
1. ✅ Schedule 24-hr Holter at front desk
2. ✅ TSH re-check today
3. ✅ Reduce caffeine to <1 cup/day × 2 weeks (trial)
4. ✅ No new medications
5. 📞 Follow-up office visit: 2026-09-23
6. 🚨 Red flags → call nurse line / ER immediately

## 📅 Auto-scheduled reminders:
- 2026-09-09: Call clinic for Holter results review
- 2026-09-23: Office re-check (in 21 days)

Saved: ~/.hermes/medical-visits/notes-visit-2026-09-02-cardiologist.md
Updated: visits.json + reminders.json
```

### Example 3 — Lab decoder

```
User: Can you decode my CBC? WBC 12.4, RBC 4.1, Hgb 13.2, Hct 39%, platelets 245.

Hermes:
[INFO] Loading personal-health-profile.json — Alex (F, 38).
[EXEC] Parsing CBC report against age/sex-appropriate reference ranges.

# 🔬 CBC Decoded — drawn 2026-09-02

| Test | Your Value | Reference (F 30-45) | Flag | Plain English |
|------|-----------|---------------------|------|---------------|
| WBC | 12.4 ×10⁹/L | 4.0-11.0 | 🔴 high | infection / inflammation / stress response |
| RBC | 4.1 ×10¹²/L | 3.9-5.2 | 🟢 normal | healthy |
| Hgb | 13.2 g/dL | 12.0-15.5 | 🟢 normal | no anemia |
| Hct | 39% | 36-46 | 🟢 normal | tracks Hgb |
| Platelets | 245 ×10⁹/L | 150-400 | 🟢 normal | healthy clotting |

⚠️ 1 critical finding: WBC 12.4 — call Dr. Lee today.

🎯 Questions for Dr. Lee:
1. Does elevated WBC change your interpretation of my palpitations?
2. Should we order a WBC differential?
3. Could my levothyroxine dose be relevant?
4. Repeat in 1 week or sooner?

⚠️ I'm not your doctor — this is general info, not a diagnosis. Always discuss abnormal results with your provider.

Saved: ~/.hermes/medical-visits/lab-decodes/cbc-2026-09-02.md
Linked to: visit-2026-09-02-cardiologist
```

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User pastes lab values with no units | Ask for units or assume standard (CBC in ×10⁹/L or ×10³/µL — flag ambiguity in report) |
| User describes visit in mixed languages | SOAP note structure handles mixed input — translate key terms to one canonical language for the saved note |
| Patient profile doesn't exist yet | Run 5-7 onboarding questions in one go; offer template file for users who prefer to fill it manually |
| Doctor gives contradictory info (e.g. two diagnoses) | Surface the contradiction explicitly in the note: *"Doctor mentioned both X and Y — clarify which one is the working diagnosis?"* |
| Patient mentions symptoms that sound urgent (chest pain + shortness of breath + syncope) | **Always** include an immediate ER/nurse-line recommendation in bold, even if the user is mid-prep. Never delay urgent triage. |
| User wants to share notes with another doctor | Second-opinion mode redacts by default; remind user to verify what they're sharing |
| Lab result is from a different patient / pasted wrong | Confirm with user before saving — don't overwrite previous lab decode |
| Patient has 10+ active medications | Drug interaction check is out of scope — recommend pharmacist or prescribing doctor, don't attempt it |
| Multiple upcoming visits in same week | Generate separate briefing packs; cross-reference if same specialist or related |
| User says "I had a doctor appointment" without details | Probe gently: *"When, with whom, for what?"* — don't fabricate details |

## Verification Checklist

- [ ] `personal-health-profile.json` exists and is populated (or template handed to user)
- [ ] Each upcoming visit has a registered entry in `visits.json` with date, doctor, specialty, reason
- [ ] Pre-visit briefing pack generated ≥ 7 days before appointment when possible
- [ ] Briefing includes symptom timeline (from symptom-diary or interview), medication list, allergies, top questions
- [ ] Top questions are specialty-specific (not generic "how are you feeling?")
- [ ] Post-visit SOAP note saved within 24h of appointment
- [ ] Prescriptions, labs ordered, follow-up date, red flags all extracted into structured data
- [ ] Reminders.json updated with all follow-up dates
- [ ] Lab/imaging decodes always include a "not a diagnosis" disclaimer
- [ ] Critical findings (🔴) trigger an immediate "call doctor today" message
- [ ] Second-opinion brief redacts by default and reminds user to verify
- [ ] No PHI leaves the local machine — never log medical details to cloud services, telemetry, or analytics
- [ ] All times in user's local timezone; reference ranges match patient's age/sex
- [ ] Backup reminder: medical-visit files are irreplaceable — suggest user backup `~/.hermes/medical-visits/` to encrypted USB monthly

## Data Sources & Accuracy

This skill does **not** call any medical API. All interpretations come from:
- **Standard reference ranges** baked into the skill (CBC, BMP, lipid, HbA1c, TSH, UA) — sourced from Mayo Clinic, LabCorp, Quest public reference docs (compiled into `references/reference-ranges.md` in this skill)
- **Plain-language explanations** generated by the LLM from those references — always labeled as general info, never diagnosis
- **Specialty question templates** derived from common patient-advocacy checklists (AHRQ "Questions to Ask Your Doctor", Cleveland Clinic patient guides)

**Disclaimer (load-bearing):** This skill is a *patient-advocacy and organization* tool. It does **not** diagnose, prescribe, or replace medical judgment. Every clinical interpretation should be confirmed with the treating provider. Critical findings always route to "call your doctor" not "AI says it's fine." Local-first by design: your health data never leaves your machine.