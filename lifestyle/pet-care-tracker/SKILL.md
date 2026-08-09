---
name: pet-care-tracker
description: "Log pet health & wellness from chat — vaccines, preventatives (flea/heartworm), medications, weight, food, behavior, vet visits for dogs, cats, and other pets. Track multi-pet households, predict life-stage needs, and export vet-ready records. All data local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, pets, dogs, cats, veterinary, vaccines, preventatives, health, weight-tracking, behavior, vet-records, multi-pet]
    related_skills: [symptom-diary, home-maintenance-tracker, personal-expense-tracker, habit-tracker, personal-crm]
---

# 🐾 Pet Care Tracker — 宠物健康与日常护理追踪

> Stop losing the rabies certificate when the groomer asks. Track every vaccine, flea pill, heartworm dose, weight check, vet visit, and behavioral quirk for every animal in your household — and walk into the clinic with a clean, printable history. 用对话记录每只宠物的疫苗、驱虫、用药、体重、行为和就诊记录，从此告别翻箱倒柜找疫苗本。

---

## Overview

Pet ownership is a stack of recurring cadences most people forget until they need them: rabies every 1–3 years, DHPP annually, monthly heartworm, monthly flea/tick, dental cleanings yearly, weight checks quarterly, bloodwork annually for seniors. Multiply that by multiple pets and a household collapses into chaos. This skill turns Hermes into a household pet health logbook: you describe what you did (*"gave Mochi her Heartgard this morning, weighs 12.4 lb"* / *"Mochi ate something weird yesterday, vomited twice, seems fine now"*) and Hermes logs it, schedules the next dose, tracks weight trends, flags overdue preventatives, and exports a vet-ready medical history.

| Capability | Description |
|------------|-------------|
| 🐶 Multi-pet registry | Dogs, cats, rabbits, birds, reptiles — each with breed, age, sex, fixed status, microchip, insurance |
| 💉 Vaccine tracking | Core (rabies/DHPP/FVRCP) + lifestyle (lepto/bordetella/lyme) with certificate refs |
| 🦟 Preventative schedule | Monthly heartworm, flea/tick, dewormer — auto next-due math |
| 💊 Medication log | Prescriptions + OTC + supplements, adherence %, refill alerts |
| ⚖️ Weight & body score | Trend chart, BCS 1-9, vet-flag for >10% change in 30 days |
| 🍽️ Food & nutrition | Brand, kibble/raw/wet, calories/day, allergy notes, transitions |
| 🩺 Vet visit log | Date, clinic, reason, diagnosis, treatment, follow-up |
| 🧠 Behavior journal | Free-form notes — anxiety, reactivity, litter, training milestones |
| 📅 Life-stage playbook | Puppy/kitten → adult → senior → geriatric milestone checklists |
| 💰 Annual cost report | Spend by category: vet, food, preventatives, grooming, insurance |
| 🏥 Vet-ready export | Markdown/PDF medical history for boarding, groomers, emergency clinics |
| 🔔 Overdue alerts | Anything past due shows in red. Cron-friendly weekly digest. |
| 💾 Local storage | All data in `~/.hermes/pets/` — no cloud, no leak |

## When to Use

- *"Add my dog Mochi — Shiba Inu, 3 years old, spayed female, 22 lb, microchip 985112004567890"*
- *"Mochi got her rabies booster today at Dr. Patel's clinic, certificate #R-2026-0418"*
- *"Gave Mochi her monthly Heartgard and NexGard this morning, weighs 22.4 lb"*
- *"Mochi has been scratching a lot since we switched to chicken-free food, log it"*
- *"When is Mochi due for her next DHPP?"*
- *"What preventatives are overdue across all my pets?"*
- *"Log Mochi's vet visit — vomiting twice yesterday, no blood, eating normally now, Dr. said watch for 24h"*
- *"Set up puppy milestones for a new Golden Retriever"*
- *"What's Mochi's weight trend over the last year?"*
- *"Export Mochi's medical history for the boarding stay next month"*
- *"How much did I spend on my pets last year?"*
- *"I just adopted a kitten — name: Bean, DSH, ~10 weeks, unknown vaccine history"*
- *"Mochi needs dental cleaning — schedule reminder for 12 months"*
- *"Show me senior-screening bloodwork checklist for Mochi (she turns 8 next month)"*
- *"我家的猫叫奶油，英短，3岁母猫，上周打了加强疫苗"*
- *"帮我列一下下个月每只宠物的驱虫时间表"*
- *"奶油最近总在沙发尿尿，帮我记下来"*
- *"整理一份奶油的就诊记录给新兽医"*

## Core Workflow

### Step 1: Initialize Household & Pet Profile

On first mention, create the data directory and ask 3-5 setup questions:

```bash
mkdir -p ~/.hermes/pets
```

Setup questions (use sensible defaults if user skips):

1. **How many pets?** Loop over each to collect:
   - Name
   - Species (dog / cat / rabbit / bird / reptile / other)
   - Breed (or "DSH/DMH mix" for cats, "mixed breed" for dogs)
   - Sex + spayed/neutered status
   - Birthdate (or estimated age)
   - Current weight
   - Microchip number (optional)
   - Insurance provider (optional)
2. **Household vet**: primary clinic name, phone, address (optional)
3. **Time zone**: IANA tz for accurate scheduling

```json
// ~/.hermes/pets/household.json
{
  "version": 1,
  "created_at": "2026-08-08",
  "time_zone": "America/Los_Angeles",
  "primary_vet": {
    "name": "Sunset Animal Hospital",
    "phone": "555-0142",
    "address": "1200 Sunset Blvd, Los Angeles, CA",
    "vet_name": "Dr. Patel"
  },
  "emergency_vet": {
    "name": "ASPCA ER",
    "phone": "555-0911"
  }
}
```

```json
// ~/.hermes/pets/mochi.json (one file per pet)
{
  "id": "pet-2026-08-08-001",
  "name": "Mochi",
  "species": "dog",
  "breed": "Shiba Inu",
  "sex": "female",
  "spayed": true,
  "birthdate": "2023-04-12",
  "age_at_creation_years": 3.3,
  "current_weight_lb": 22.4,
  "ideal_weight_lb": 23.0,
  "body_condition_score": 5,
  "microchip": "985112004567890",
  "insurance": {
    "provider": "Trupanion",
    "policy_id": "TP-9182374",
    "deductible_usd": 250
  },
  "color_markings": "sesame, white markings",
  "lifestyle": {
    "indoor_only": false,
    "outdoor_access": "fenced yard + leash walks",
    "other_pets_in_house": ["pet-2026-08-08-002"],
    "allergies_known": ["chicken (mild itching)"],
    "chronic_conditions": []
  },
  "life_stage": "adult_young",   // computed: puppy|adult_young|adult_mature|senior|geriatric
  "created_at": "2026-08-08",
  "deceased": false
}
```

**Data files**:
- `~/.hermes/pets/household.json` — primary vet, emergency vet, time zone
- `~/.hermes/pets/{pet-name-slug}.json` — full profile + all logs (one per pet, scaled OK to ~5MB)
- `~/.hermes/pets/{pet-name-slug}.schedule.json` — derived due dates (regenerated on demand)
- `~/.hermes/pets/reports/` — generated vet reports and annual cost summaries
- `~/.hermes/pets/index.json` — pointer map `pet-name → file`

> **Why one file per pet?** Multi-pet households are common (US dog-owning households average 1.7 dogs; cats 1.8 cats). One file per pet keeps size manageable and makes exports per-pet trivial.

### Step 2: Parse Natural-Language Logs

Pet owners rarely speak in JSON. Parse freeform text and extract:

- **Action type**: vaccine | preventative | medication | vet_visit | weight | food | behavior | grooming | dental | other
- **Subject**: which pet (default: the one most recently mentioned, or ask)
- **Date / time**: explicit ("today", "yesterday", "last Tuesday") or inferred
- **Details**: dose, weight, vaccine brand, vet name, diagnosis, etc.

Example parses:

```
"Gave Mochi her Heartgard and NexGard this morning, 22.4 lb"
→ action: preventative, pet: mochi,
  items: [
    {name: "Heartgard Plus", dose: "1 chew (up to 25 lb)", frequency: "monthly"},
    {name: "NexGard", dose: "1 chew (10-24 lb)", frequency: "monthly"}
  ],
  weight_lb: 22.4,
  recorded_at: morning

"Mochi got her rabies booster today, certificate R-2026-0418, Dr. Patel"
→ action: vaccine, pet: mochi,
  vaccine: rabies_3yr (booster),
  certificate_id: "R-2026-0418",
  vet: "Dr. Patel",
  next_due: 2029-08-08

"Creamy has been peeing on the couch since Sunday, log it"
→ action: behavior, pet: creamy,
  behavior: inappropriate_urination,
  onset: 2026-08-03,
  frequency: ongoing,
  suspected_triggers: ["stress", "UTI"],
  flagged_for_vet: true

"Mochi ate something weird yesterday, vomited twice, seems fine now"
→ action: vet_visit_self_care, pet: mochi,
  symptoms: ["vomiting x2"],
  onset: yesterday,
  resolution: self-resolved,
  severity: low
```

Auto-store with stable schema:

```json
{
  "id": "log-2026-08-08-001",
  "pet_id": "pet-2026-08-08-001",
  "timestamp": "2026-08-08T08:15:00-07:00",
  "action": "preventative",
  "items": [
    {
      "product": "Heartgard Plus",
      "type": "heartworm",
      "dose": "1 chew",
      "weight_band": "up to 25 lb",
      "next_due": "2026-09-08"
    },
    {
      "product": "NexGard",
      "type": "flea_tick_oral",
      "dose": "1 chew",
      "weight_band": "10-24 lb",
      "next_due": "2026-09-08"
    }
  ],
  "weight_lb": 22.4,
  "notes": ""
}
```

**Product auto-classification dictionary** (top brands → category):
- `Heartgard / Interceptor / ProHeart` → heartworm
- `NexGard / Bravecto / Simparica / Frontline / Advantage / Seresto` → flea_tick
- `Drontal / Panacur / Fenbendazole` → dewormer
- `Apoquel / Cytopoint` → anti-itch
- `Carprofen / Meloxicam / Gabapentin` → prescription NSAID/neuro
- `Frontline Plus / Revolution / Advantage Multi` → combo (heartworm + flea)

### Step 3: Vaccine & Preventative Cadence Engine

When a vaccine or preventative is logged, compute the next due date from species + product rules:

| Product / Vaccine | Species | Interval | Notes |
|-------------------|---------|----------|-------|
| Rabies (1-year) | dog/cat | 365 days | Many US states mandate this interval; puppy initial: 16 weeks |
| Rabies (3-year) | dog/cat | 1095 days | After first booster, vet can certify 3-year |
| DHPP / FVRCP | dog/cat | 365 days | Core combo vaccine |
| Leptospirosis | dog | 365 days | Lifestyle — rural/water exposure |
| Bordetella | dog | 180 days | Required by most boarding/grooming |
| Canine Influenza | dog | 365 days | Lifestyle — social dogs |
| Lyme | dog | 365 days | Endemic regions only |
| FeLV | cat | 365 days | Outdoor/door-cat only; annual until adult |
| Heartworm monthly | dog/cat | 30 days | Strict — lapses >45 days require retest |
| Flea/tick monthly | dog/cat | 30 days | Some brands (Bravecto) are 90 days |
| Dewormer | dog/cat | 90 days | Or per stool-sample result |

Engine output (regenerated on demand into `*.schedule.json`):

```json
// ~/.hermes/pets/mochi.schedule.json
{
  "generated_at": "2026-08-08T08:20:00-07:00",
  "pet_id": "pet-2026-08-08-001",
  "upcoming": [
    {
      "item": "Heartgard Plus",
      "category": "heartworm",
      "next_due": "2026-09-08",
      "days_until_due": 31,
      "overdue": false
    },
    {
      "item": "NexGard",
      "category": "flea_tick",
      "next_due": "2026-09-08",
      "days_until_due": 31,
      "overdue": false
    },
    {
      "item": "Rabies (3-yr booster)",
      "category": "vaccine",
      "next_due": "2029-08-08",
      "days_until_due": 1095,
      "certificate_id": "R-2026-0418"
    },
    {
      "item": "DHPP annual",
      "category": "vaccine",
      "next_due": "2027-06-12",
      "days_until_due": 308,
      "overdue": false
    }
  ],
  "overdue": [],
  "this_month": ["Heartgard Plus", "NexGard"]
}
```

**Heartworm lapse rule**: if 30-day monthly dose is missed by >45 days, flag as `lapsed: true` and warn that most vets require a negative antigen retest before restarting. This is the #1 preventable fatal disease in US dogs — never go silent on this one.

### Step 4: Weight & Body Condition Tracking

Weights are entered whenever measured (vet visit, at-home scale, grooming appointment). Plot trends, flag concerning changes.

```json
{
  "pet_id": "pet-2026-08-08-001",
  "weights": [
    {"date": "2025-09-12", "lb": 22.0, "source": "vet"},
    {"date": "2025-12-04", "lb": 23.1, "source": "home_scale", "notes": "winter coat"},
    {"date": "2026-04-18", "lb": 22.8, "source": "groomer"},
    {"date": "2026-08-08", "lb": 22.4, "source": "home_scale"}
  ]
}
```

**Trend analysis** (computed on demand):

```
📈 Mochi weight trend (12 months)
  Range: 22.0 → 23.1 lb (Δ +0.4 lb)
  Best-fit slope: −0.02 lb/month  (stable)
  Last check vs prior: −0.4 lb (mild loss, within normal)
  Body condition score: 5/9 (ideal)
  🟢 Status: STABLE
```

**Flags**:
- `> 10% change in 30 days` → ⚠️ VET — sudden weight loss in cats especially is an emergency (hepatic lipidosis risk)
- `BCS > 6/9` → ⚠️ overweight, suggest portion/activity review
- `BCS < 4/9` → ⚠️ underweight

### Step 5: Vet Visit Log

Every clinic visit becomes a structured record. Parse free text or guided form:

```
"Mochi vet visit — vomiting twice 8/7, ate grass, no blood,
Dr. Patel said give Pepcid 5mg for 3 days, watch 24h"
```

```json
{
  "id": "visit-2026-08-08-001",
  "pet_id": "pet-2026-08-08-001",
  "date": "2026-08-07",
  "clinic": "Sunset Animal Hospital",
  "vet": "Dr. Patel",
  "reason": "acute_vomiting",
  "history": "ate grass in yard, vomited twice within 4 hours",
  "exam_findings": "abdomen soft, no pain, hydration OK, T=101.8°F",
  "diagnosis": "dietary_indiscretion",
  "treatments": [
    {"item": "Pepcid AC (famotidine)", "dose": "5mg PO BID x 3 days"},
    {"item": "bland diet (boiled chicken + rice) x 48h"}
  ],
  "follow_up": "if not resolved in 24h or any new symptom, return",
  "cost_usd": 145,
  "notes": "owner reports normal energy and appetite this morning"
}
```

`cost_usd` feeds the annual cost report (Step 8).

### Step 6: Behavior Journal

Free-form notes — this is the most under-recorded area of pet care and the most valuable when a behaviorist asks.

```json
{
  "id": "behav-2026-08-08-001",
  "pet_id": "pet-2026-08-08-002",
  "date": "2026-08-03",
  "behavior": "inappropriate_urination",
  "location": "living room couch",
  "frequency": "2x since Sunday",
  "context": "started 2 days after we moved the litter box to the laundry room",
  "severity": "moderate",
  "flagged_for_vet": true,
  "suspected_triggers": ["litter_box_relocation", "UTI"],
  "vet_followup_scheduled": "2026-08-10"
}
```

After 3+ behavior entries, surface pattern detection:

```
🧠 Behavior pattern: Creamy (cat)
  inappropriate_urination x3 since 2026-08-03
  common factor: litter box moved to laundry room 2026-08-02
  → VET check + restore original box location, then re-introduce move
```

### Step 7: Life-Stage Playbook

Compute life stage from birthdate and species. Different stages have different milestone checklists:

| Species | Puppy/Kitten | Adult | Senior | Geriatric |
|---------|--------------|-------|--------|-----------|
| Dog | 0–1 yr | 1–7 yr (size-dependent) | 7–10 yr (varies by breed) | 10+ yr |
| Cat | 0–1 yr | 1–7 yr | 7–11 yr | 11+ yr |
| Rabbit | 0–1 yr | 1–5 yr | 5–8 yr | 8+ yr |

Auto-generated playbook (run on demand or cron monthly):

```
🐶 Mochi life-stage: adult_young (3.4 yr)
  ✅ Completed (puppy stage):
     • DHPP series (3 doses)
     • Rabies 1-yr
     • Spay at 8 mo
     • Initial microchip
  📋 Recommended this year:
     • DHPP annual — DUE 2026-06-12 (overdue 57 days) ⚠️
     • Heartworm test (annual, spring) — DONE 2026-04-08 ✅
     • Bordetella (boarding) — DONE 2026-05-20 ✅
  🩺 Senior prep (when Mochi turns 7):
     • Annual bloodwork (CBC, chem, urinalysis)
     • Dental cleaning under anesthesia
     • Baseline radiographs for arthritis
```

### Step 8: Annual Cost Report

Aggregate `cost_usd` from vet visits + user-entered expenses (food, preventatives, grooming, insurance premiums).

```json
{
  "year": 2026,
  "household_total_usd": 3214,
  "by_category": {
    "vet_visits": {"usd": 612, "share": "19%"},
    "food": {"usd": 720, "share": "22%"},
    "preventatives": {"usd": 384, "share": "12%"},
    "medications": {"usd": 92, "share": "3%"},
    "grooming": {"usd": 480, "share": "15%"},
    "insurance_premium": {"usd": 720, "share": "22%"},
    "boarding_daycare": {"usd": 156, "share": "5%"},
    "other": {"usd": 50, "share": "2%"}
  },
  "per_pet": {
    "mochi": 2142,
    "creamy": 1072
  }
}
```

Pair with the existing `personal-expense-tracker` skill for unified tax/insurance deduction tracking.

### Step 9: Vet-Ready Medical History Export

When the user says *"export for vet"*, *"boarding record"*, *"groomer needs vaccine proof"*, or *"new clinic transfer"*, generate a structured document.

**Markdown** (default):

```markdown
# Medical History — Mochi
**Species**: Dog (Shiba Inu, female spayed)
**DOB**: 2023-04-12 (3 yr)
**Microchip**: 985112004567890
**Owner**: [redacted on export]
**Generated**: 2026-08-08

## Vaccines
| Date | Vaccine | Certificate # | Vet | Next due |
|------|---------|---------------|-----|----------|
| 2023-06-20 | Rabies (1-yr) | R-2023-1198 | Dr. Lee | 2024-06-20 |
| 2024-06-15 | Rabies (3-yr) | R-2024-0987 | Dr. Lee | 2027-06-15 |
| 2026-04-08 | DHPP | D-2026-0418 | Dr. Patel | 2027-04-08 |
| 2026-04-08 | Bordetella | B-2026-0418 | Dr. Patel | 2026-10-08 |

## Preventatives (last 12 months)
| Date | Product | Dose | Next due |
|------|---------|------|----------|
| 2026-08-08 | Heartgard Plus | up to 25 lb | 2026-09-08 |
| 2026-08-08 | NexGard | 10-24 lb | 2026-09-08 |
| ... | ... | ... | ... |

## Medications & Supplements
| Started | Name | Dose | Active | Purpose |
|---------|------|------|--------|---------|
| 2024-09 | Apoquel | 16mg daily | yes | seasonal allergies |

## Vet Visits
| Date | Reason | Diagnosis | Treatment | Cost |
|------|--------|-----------|-----------|------|
| 2026-08-07 | acute vomiting | dietary indiscretion | Pepcid + bland diet | $145 |
| 2026-04-08 | annual exam | healthy | DHPP, bordetella, heartworm test | $214 |

## Weight History
2025-09: 22.0 lb | 2025-12: 23.1 lb | 2026-04: 22.8 lb | 2026-08: 22.4 lb
Trend: stable | BCS: 5/9

## Allergies / Chronic Conditions
- Chicken (mild itching) — diet-controlled

## Behavioral Notes
[optional, user-controlled — separate export toggle]

---
Generated by hermes/pet-care-tracker · keep confidential
```

**PDF export**: optional via `pandoc` or `reportlab` if installed. Default to Markdown so user can print from any editor.

### Step 10: Overdue Digest (Cron-Ready)

A weekly cron-friendly summary across all pets:

```
🐾 Weekly pet digest — week of 2026-08-04

✅ Given on schedule (8/8)
  Mochi: Heartgard + NexGard (8/8), Bordetella due 10/8
  Creamy: Revolution (8/5)

⚠️ OVERDUE
  Mochi: DHPP annual — 57 days overdue ⚠️ SCHEDULE ASAP
  Bean (kitten): FVRCP #2 — 4 days overdue

📅 Coming up this month
  2026-08-15 — Bean: dewormer #2
  2026-08-20 — Creamy: 6-month wellness check
  2026-09-08 — Mochi + Creamy: monthly preventatives
```

## Example Invocations

### Example 1: Multi-Pet Setup + First Vaccine

> **User**: I just adopted a kitten — name Bean, domestic shorthair, ~10 weeks, female, not spayed yet, no vaccine history. Also add my dog Mochi — Shiba Inu, 3 years old, 22 lb, microchip 985112004567890. Both patients of Sunset Animal Hospital, Dr. Patel.

> **Agent**:
> ```
> 🐾 Setting up two-pet household…
> Created:
>   ✅ Bean (kitten, ~10 wk, DSH, female intact)
>   ✅ Mochi (Shiba Inu, 3 yr, female spayed, 22 lb)
> Primary vet: Sunset Animal Hospital, Dr. Patel
>
> 📋 Bean — kitten milestones (auto-generated):
>   • FVRCP series — start now (3 doses, 3-4 wk apart)
>   • FeLV — series recommended for new cat until adult
>   • Rabies — at 16 weeks
>   • Spay — typically 4-6 mo (ask vet)
>   • Dewormer — every 2 wk until 12 wk
> 📋 Mochi — life-stage: adult_young
>   • DHPP annual due 2026-06-12 — OVERDUE 57 days ⚠️
>   • Heartworm monthly — next due 2026-08-08
>
> Want me to log Bean's first vet visit when you go?
> ```

### Example 2: Routine Monthly Preventative + Weight

> **User**: Gave Mochi her Heartgard and NexGard this morning, she weighs 22.4.

> **Agent**:
> ```
> 💊 Logged: Mochi — 2026-08-08
>   ✅ Heartgard Plus  (heartworm monthly)
>   ✅ NexGard         (flea/tick monthly)
>   ⚖️ Weight: 22.4 lb (−0.4 from 22.8 lb on 4/18)
>
> 📅 Next due: 2026-09-08 (31 days)
> 🐈 Creamy — also due for Revolution around 8/12. Log when you do it.
> ⚠️ Mochi DHPP annual still 57 days overdue. Schedule with Dr. Patel?
> ```

### Example 3: Vet Visit + Auto-Export

> **User**: Mochi vomited twice yesterday after eating grass in the yard. Took her to Dr. Patel — she said dietary indiscretion, gave Pepcid 5mg twice daily for 3 days, bland diet 48 hours. Cost $145. Also export Mochi's full medical history for the boarding stay on 9/15.

> **Agent**:
> ```
> 🩺 Logged vet visit: Mochi — 2026-08-07
>   Reason: acute vomiting x2 after grass ingestion
>   Diagnosis: dietary indiscretion
>   Treatment: Pepcid AC 5mg BID x 3d, boiled chicken + rice x 48h
>   Follow-up: if not resolved in 24h, return
>   Cost: $145
>
> 💊 Auto-added medication: Pepcid AC 5mg BID x 3 days
>   Active: yes
>   Refill: not needed (3-day course)
>   Reminder: stop date 2026-08-10
>
> 📄 Generating boarding export…
>   File: ~/.hermes/pets/reports/mochi-boarding-2026-09-15.md
>   Includes: vaccines + certificate IDs, preventatives, weight,
>             allergies, last vet visit, behavioral notes (toggle: ON)
>
>   [open file]
> ```

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User says "gave the dog his pill" but multiple dogs exist | Ask which pet; never guess. Default to the one most recently mentioned, then confirm. |
| Heartworm monthly lapse > 45 days | Flag `lapsed: true` and recommend antigen retest. Never silently restart — most vets will not refill without a negative test. |
| Vaccine brand vs schedule mismatch (e.g. user reports rabies but no certificate) | Log the vaccine but mark `certificate_id: pending` and prompt for it. Vet clinics require proof, not memory. |
| Weight unit ambiguity (lb vs kg) | Confirm once at setup; never auto-convert silently. Cats are usually weighed in lb in US, rabbits in kg — species hint helps. |
| Senior pet suddenly loses weight | Auto-flag > 5% loss in 30 days. Cats especially: hepatic lipidosis can develop in <72h of not eating — surface as urgent, not advisory. |
| Rabies 1-yr vs 3-yr confusion | Look at `certificate_id` and date. Default to 1-yr on first vaccine; 3-yr after vet-certified booster. Confirm with user. |
| Pet renamed mid-stream (e.g. "Bean" becomes "Beans") | Don't rename the file. Store `aliases: ["Beans", "Beanie"]` and match both. Keep stable `pet_id`. |
| Multi-pet "I gave them their heartworm" — plural log | Write one entry per pet, not one combined entry. Otherwise schedule drift compounds. |
| Behavior note vs medical note | Behavior journal for normal-life stuff (litter, training). Vet visit log for anything with a clinical outcome. Don't merge. |
| User wants to delete a deceased pet | Set `deceased: true` + `deceased_at` rather than deleting. Preserves medical history in case of audit/insurance claim. |
| Brand new puppy with unknown vaccine history | Treat as overdue for everything. Schedule from "today" not from birthdate. Owner usually gets a starter record from breeder/shelter. |
| Cat indoor-only lifestyle still gets heartworm | Optional but increasingly recommended in US South. Don't skip silently — note "lifestyle: indoor, region: high-prevalence" and surface as discussion with vet. |

## Verification Checklist

- [ ] On first mention, agent asks setup questions before writing data
- [ ] Pet files written to `~/.hermes/pets/{pet-slug}.json`, never to project dir
- [ ] Schedule recomputed when any vaccine or preventative is logged
- [ ] Overdue items surface in next digest within 24h of lapse
- [ ] Weight trend chart regenerates from raw points, not stored derived values
- [ ] Vet export excludes owner PII unless explicitly included (default: redact)
- [ ] Multi-pet log entry creates one record per pet, not one combined record
- [ ] Heartworm lapse > 45 days auto-flags, never silently auto-reschedules
- [ ] Deceased pet preserved with `deceased: true`, not deleted
- [ ] All cat weight-loss > 5%/30d flagged as urgent, not advisory
- [ ] Annual cost report pulls from raw `cost_usd` fields, not user-typed totals
- [ ] Index file (`index.json`) updated whenever a pet file is added/renamed
- [ ] Files survive Hermes restart (no in-memory state required)
- [ ] Exports go to `~/.hermes/pets/reports/` with timestamped filenames

## Data Sources & Accuracy

| Data | Source | Accuracy / Caveat |
|------|--------|-------------------|
| Vaccine intervals | AAHA 2023 canine vaccination guidelines, AAFP feline guidelines | Generally accepted standard; state law may mandate shorter intervals for rabies (e.g. NY requires annual even after 3-yr cert) |
| Preventative product categories | Manufacturer labels (Boehringer Ingelheim / Merck / Zoetis) | Doses are weight-banded — verify with current product insert; brands reformulate periodically |
| Life-stage thresholds | AAHA / AAFP senior care guidelines (dog senior = last 25% of expected lifespan) | Varies dramatically by breed — giant breeds senior earlier than toy breeds. Refine per breed when known. |
| Weight change thresholds (>5% cat, >10% dog) | Veterinary internal medicine literature | Cat figure is conservative — many clinics flag >5% as needing workup. |
| Heartworm lapse rule (45 days) | American Heartworm Society guidelines | Some clinics require 6-mo retest after 6-mo lapse; conservative default. |
| Behavior trigger hypotheses | Veterinary behavior literature + ASPCA positioning | Suggestions are hypotheses, not diagnoses. Never auto-prescribe. |
| Cost categories | Common US pet ownership spending surveys (APPA 2023) | Numbers are average benchmarks; do not present as personalized financial advice. |

**Privacy stance**: All pet data lives locally in `~/.hermes/pets/`. No vet clinic, insurance, or microchip registry API is contacted unless the user explicitly opts in. This skill is a logbook, not a medical device — recommendations are organizational, not diagnostic.