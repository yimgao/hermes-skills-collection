---
name: home-maintenance-tracker
description: "Log home maintenance tasks by chat — HVAC filters, gutter cleaning, smoke detector batteries, appliance warranties, repair history, seasonal reminders, and annual cost reporting. All data local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, home, maintenance, household, repair, warranty, hvac, appliances, seasonal, reminders, cost-tracking]
    related_skills: [personal-expense-tracker, habit-tracker, subscription-manager, gift-finder]
---

# 🏠 Home Maintenance Tracker（家庭维护追踪器）

> Stop forgetting the smoke detector battery until it beeps at 2am. Track every filter, service, repair, and warranty for everything in your home — and get a seasonal checklist before the next thing breaks.

---

## Overview

A house is a stack of things that need attention on different cadences: furnace filters every 90 days, water heater flush once a year, gutters twice a year, refrigerator coils every 6 months, dryer vent cleaning yearly, roof inspection every 2 years. Most people forget all of them until something fails. This skill turns Hermes into a household maintenance logbook: you describe what you did (*"changed the HVAC filter in the basement, it's a 16x25x1 MERV 11"*) and Hermes stores it, schedules the next due date, tracks cost, flags warranties, and warns you when something is overdue.

| Capability | Description |
|------------|-------------|
| 🔧 Log tasks | Natural language: *"replaced kitchen faucet cartridge, $45 in parts"* |
| 📋 Asset registry | HVAC, water heater, appliances, roof, gutters, smoke/CO detectors, garage door, sprinklers — each with model/serial/install date |
| ⏰ Cadence scheduling | Per-task interval (30/90/180/365/730 days). Auto-compute next due date. |
| 🔔 Overdue alerts | Anything past due date shows in red. Daily/weekly digest via cron. |
| 📜 Warranty tracking | Purchase date + warranty length → expiration date. Flag expiring soon. |
| 💰 Cost log | Parts + labor per task. Annual report: total spent by category. |
| 🗓️ Seasonal playbook | Spring/Summer/Fall/Winter checklist auto-generated for your region |
| 🛠️ Repair history | Per-asset timeline — see every service, repair, replacement |
| 🏷️ Vendor list | Plumber, electrician, HVAC tech — name, phone, last visit, rating |
| 💾 Local storage | All data in `~/.hermes/home/` — no cloud, no leak |

---

## When to Use

- *"I just changed the furnace filter — 16x25x1 MERV 11, $14"*
- *"Set up my home — 2-story, gas furnace, electric water heater, 5-year-old roof"*
- *"What's due this month?"*
- *"My dishwasher died — Model #MDB4100AWW, purchased 2019-08"*
- *"Show me my spring maintenance checklist"*
- *"How much have I spent on home maintenance this year?"*
- *"Add my plumber: Joe's Plumbing, 555-0142, last visit 2026-03-15"*
- *"When does my water heater warranty expire?"*
- *"Schedule dryer vent cleaning — every 12 months"*
- *"Gutters haven't been cleaned in 14 months — am I overdue?"*
- *"我家空调滤网刚换了"*
- *"帮我列个春季维护清单"*
- *"今年家装维修花了多少钱？"*
- *"Smoke detector battery — replace every 6 months"*

---

## Core Workflow

### Step 1: Initialize Home Profile & Asset Registry

On first run, create the data directory and capture a baseline of your home.

```bash
mkdir -p ~/.hermes/home
```

Agent asks 4 setup questions (use sensible defaults if user skips):

1. **Home basics** — year built, square footage, stories, climate zone (used for seasonal recommendations)
2. **Major systems** — furnace/gas/heat pump, water heater (tank/tankless/gas/electric), HVAC type, roof material, gutter style
3. **Appliances** — refrigerator, dishwasher, washer, dryer, oven, microwave, garbage disposal (model + purchase date if known)
4. **Outdoor** — sprinklers, deck, fence, pool, hot tub, EV charger, solar panels

```json
// ~/.hermes/home/assets.json
{
  "version": 1,
  "home": {
    "year_built": 1998,
    "sqft": 2200,
    "stories": 2,
    "climate_zone": "5A",  // IECC climate zone for seasonal playbook
    "region": "US-Northeast",
    "created_at": "2026-07-20"
  },
  "assets": [
    {
      "id": "ast-2026-07-20-001",
      "category": "hvac",
      "name": "Carrier Gas Furnace",
      "model": "59TN6",
      "serial": "3498X12920",
      "install_date": "2018-09-12",
      "warranty_expires": "2033-09-12",
      "warranty_years": 15,
      "location": "Basement utility room",
      "custom_cadence_days": 365,
      "last_serviced": "2025-10-04",
      "next_due": "2026-10-04",
      "notes": "Annual tune-up every fall before heating season"
    },
    {
      "id": "ast-2026-07-20-002",
      "category": "water_heater",
      "name": "Bradford White 50gal Gas",
      "model": "RG250T6N",
      "serial": "BW18294736",
      "install_date": "2016-06-22",
      "warranty_expires": "2026-06-22",  // ⚠️ EXPIRED or about to expire
      "warranty_years": 10,
      "location": "Basement",
      "custom_cadence_days": 365,
      "last_serviced": "2025-04-10",
      "next_due": "2026-04-10",
      "notes": "Annual anode rod check + flush"
    },
    {
      "id": "ast-2026-07-20-003",
      "category": "appliance",
      "name": "Whirlpool Dishwasher",
      "model": "WDF520PADM",
      "serial": "F529184",
      "install_date": "2019-08-15",
      "warranty_expires": "2020-08-15",
      "warranty_years": 1,
      "location": "Kitchen",
      "custom_cadence_days": null,
      "last_serviced": null,
      "next_due": null,
      "notes": "No scheduled maintenance, run until failure"
    }
  ]
}
```

**Default cadence by asset type:**

| Asset type | Default cadence | Task |
|------------|-----------------|------|
| HVAC filter | 90 days | Replace filter |
| HVAC system | 365 days | Professional tune-up |
| Water heater (tank) | 365 days | Flush + anode rod check |
| Water heater (tankless) | 365 days | Descale + filter clean |
| Smoke detector battery | 180 days | Replace battery (test monthly) |
| CO detector | 1825 days (5y) | Replace unit |
| Gutter clean | 180 days | Clear debris |
| Roof inspection | 730 days | Visual check + flashing |
| Dryer vent clean | 365 days | Clear lint |
| Refrigerator coils | 180 days | Vacuum condenser coils |
| Range hood filter | 90 days | Soak + degrease |
| Garbage disposal | 90 days | Clean with ice + citrus |
| Sprinkler blowout | 365 days | Winterize (cold climates) |
| Deck reseal | 730 days | Stain/seal wood |
| HVAC condensate line | 180 days | Pour vinegar to clear algae |
| Sump pump | 180 days | Test by pouring water |
| Caulk inspection (bath) | 365 days | Inspect + re-caulk if needed |
| Garage door lubrication | 180 days | Lubricate rollers/hinges |

User can override cadence per asset.

### Step 2: Log a Maintenance Task

User says *"$45 to replace kitchen faucet cartridge today"* or *"Gutter cleaning done — paid Joe's Plumbing $180"*. Agent parses:

- **Asset** — match to existing asset (or ask if ambiguous); create new asset if none exists
- **Task type** — *replace*, *clean*, *inspect*, *repair*, *install*, *service*
- **Date** — default today
- **Cost** — extract number; default 0
- **Parts** — optional itemized list
- **Vendor** — match to vendor list (or ask)
- **Notes** — anything else

```json
// Appended to ~/.hermes/home/tasks.json
{
  "version": 1,
  "tasks": [
    {
      "id": "tsk-2026-07-20-001",
      "asset_id": "ast-2026-07-20-003",
      "asset_name": "Whirlpool Dishwasher",
      "task": "Repair — replace drain pump",
      "date": "2026-07-20",
      "cost": 142.50,
      "currency": "USD",
      "parts": [
        { "name": "Drain pump assembly", "sku": "WPW10348269", "cost": 87.00 },
        { "name": "Hose clamp", "cost": 4.50 }
      ],
      "labor_cost": 51.00,
      "vendor_id": "vnd-2026-03-15-001",
      "vendor_name": "Joe's Plumbing",
      "diy": false,
      "notes": "Was leaving standing water at cycle end. Pump impeller was cracked.",
      "logged_at": "2026-07-20T14:32:00Z"
    }
  ]
}
```

After logging, the agent updates `assets.json`:
- Sets `last_serviced = 2026-07-20`
- Recomputes `next_due = 2026-07-20 + cadence_days`
- Emits a confirmation with cost tally and next due date

### Step 3: Reports, Alerts & Seasonal Playbook

#### 3a. What's Due This Month

User asks *"What's due in the next 30 days?"*. Agent scans `assets.json` and groups by urgency:

```text
HOME MAINTENANCE  ·  2026-07-20 (next 30 days)
─────────────────────────────────────────────────
🔴 OVERDUE (2)
  • Bradford White Water Heater  — anode rod check  · was due 2026-04-10  · 101 days late
  • Carrier Furnace filter       — replace filter    · was due 2026-07-12  · 8 days late

🟡 DUE THIS WEEK (0)
  (none)

🟢 DUE THIS MONTH (1)
  • Refrigerator coils          — vacuum condenser   · due 2026-07-28  · in 8 days

📅 UPCOMING (next 30 days) (3)
  • Smoke detector batteries    — replace            · due 2026-08-15
  • Garbage disposal clean      — ice + citrus       · due 2026-08-22
  • Range hood filter soak      — degrease           · due 2026-08-25

💰 Cost this month so far:  $142.50  (1 task)
```

#### 3b. Seasonal Playbook

User asks *"What should I do this fall?"* or the cron weekly-digest auto-generates it. The agent pulls from climate-zone templates + the user's actual asset list:

```text
🍂 FALL PLAYBOOK  ·  2026  (Climate Zone 5A — cold winter)
─────────────────────────────────────────────────
Outdoor:
  [ ] Clean gutters (before leaves finish falling)
  [ ] Schedule furnace tune-up (heating season starts in 4-6 weeks)
  [ ] Disconnect & store garden hoses
  [ ] Drain & shut off exterior faucets (freeze risk)
  [ ] Winterize sprinkler system (blowout)
  [ ] Inspect roof for missing/damaged shingles

Indoor:
  [ ] Replace HVAC filter (heating season = heavy use)
  [ ] Test smoke + CO detectors
  [ ] Reverse ceiling fans to clockwise (push warm air down)
  [ ] Clean dryer vent thoroughly
  [ ] Check weatherstripping on doors/windows

Recommended timing:
  Early Sep  →  gutter clean, furnace tune-up
  Mid Sep    →  sprinkler blowout
  Late Sep   →  weatherstripping, smoke detector batteries
  Oct 1      →  HVAC filter swap
```

The agent tailors this by **only including tasks you have**. If you don't have a pool, the pool closing checklist is omitted.

#### 3c. Annual Cost Report

User asks *"How much did I spend on home maintenance this year?"*. Agent groups `tasks.json` by category and asset:

```text
HOME MAINTENANCE SPEND  ·  2026 YTD
─────────────────────────────────────────────────
HVAC               $  187.00   ███░░░░░░░  22%
  Furnace tune-up         $145.00
  Filter (×2)              $42.00
Plumbing           $  322.50   █████░░░░░  37%
  Dishwasher drain pump  $142.50
  Faucet cartridge         $45.00
  Water heater flush      $135.00
Appliances         $  142.50   ██░░░░░░░░  16%
  (above)
Outdoor            $  180.00   ███░░░░░░░  21%
  Gutter cleaning (×2)   $180.00
Other              $   45.00   █░░░░░░░░░   5%
─────────────────────────────────────────────────
TOTAL YTD          $  877.00  (across 11 tasks)

vs. 2025 YTD:      $1,043.00  (↓ 16%)
Avg per month:     $  109.63
Most expensive:    Plumbing  ($322.50)
Most frequent:     Filters  (4 logged)
```

#### 3d. Asset Repair History

User asks *"Tell me everything about my water heater"*. Agent shows the timeline:

```text
WATER HEATER HISTORY  ·  Bradford White 50gal Gas
─────────────────────────────────────────────────
2016-06-22  Installed (replaced failed 2005 unit)        $890  · Joe's Plumbing
2017-04-10  Annual flush                                  $95  · Joe's Plumbing
2018-04-22  Annual flush                                  $95  · Self (DIY)
2019-05-03  Replaced thermocouple (no hot water)         $35  · Self (DIY)
2020-04-15  Annual flush                                  $95  · Joe's Plumbing
2021-09-08  Replaced heating element (top)             $145  · Self (DIY)
2022-04-20  Annual flush                                  $95  · Self (DIY)
2023-05-12  Annual flush + anode rod check (anode 60% worn)  $95  · Joe's Plumbing
2024-04-08  Annual flush                                  $95  · Self (DIY)
2025-04-10  Annual flush                                  $95  · Self (DIY)
⚠️ 2026-04-10  Annual flush — OVERDUE 101 days
─────────────────────────────────────────────────
Total spent (10 years): $1,735
Avg annual cost:        $173.50
Unit age:               10 years 1 month (typical lifespan 10-15y)
Warranty status:        EXPIRED 2026-06-22  ⚠️
💡 Budget for replacement in 1-3 years. Current anode rod health unknown.
```

#### 3e. Warranty Expiration Watch

Auto-flagged in weekly digest. Agent computes `days_until_warranty_expires` for every asset:

```text
WARRANTY WATCH  ·  as of 2026-07-20
─────────────────────────────────────────────────
🔴 EXPIRED (1)
  • Bradford White Water Heater  — expired 2026-06-22  (28 days ago)

🟡 EXPIRING SOON (within 90 days) (0)
  (none)

🟢 COVERED (≥90 days remaining) (4)
  • Carrier Furnace          — until 2033-09-12  (7.2y remaining)
  • KitchenAid Refrigerator  — until 2027-03-01  (8mo remaining)
  • Whirlpool Dishwasher     — until 2020-08-15  (expired, see above)
  • Roof (shingles)          — until 2034-05-20  (8yr remaining — 50yr material warranty)
```

---

## Example Invocations

### Example 1: First-Time Setup

> **User:** Help me set up home maintenance tracking. I have a 1998 colonial, 2200 sqft, gas furnace, electric water heater, 5-year-old asphalt roof.
>
> **Agent:** Got it. I'll create the home profile and seed it with the typical cadence for your setup. **Climate zone?** (I default to Northeast US — change if not you.)
>
> **User:** Yeah, Boston area.
>
> **Agent:** Climate Zone 5A. Initialized. Now let me capture your major systems. **HVAC?**
>
> **User:** Carrier gas furnace, model 59TN6, installed 2018, professional tune-up every fall.
>
> **Agent:** ✓ Logged `Carrier Gas Furnace` — install 2018-09-12, annual cadence, next due 2026-10-04 (since last serviced 2025-10-04).
>
> **Next: water heater?**
>
> **User:** Bradford White 50gal gas, installed 2016, 10-year warranty.
>
> **Agent:** ✓ Logged `Bradford White 50gal Gas`. ⚠️ Heads up: warranty **expires 2026-06-22** — already expired 28 days ago. Worth knowing. Annual flush was due 2026-04-10 (101 days overdue).
>
> **Next: appliances? (refrigerator, dishwasher, washer, dryer, etc.)**
>
> **User:** Whirlpool dishwasher (2019, no extended warranty). LG washer (2022). Samsung dryer (2021). KitchenAid fridge (2024, 3-year warranty).
>
> **Agent:** ✓ Logged all 4.
>
> **Last: outdoor? (gutters, sprinklers, deck, etc.)**
>
> **User:** Gutters, no sprinklers, no deck yet (saving up).
>
> **Agent:** ✓ Gutters added — bi-annual cadence, last cleaned 2024-09 → next due 2025-03 → **already overdue**. Spring window passed; schedule for fall.
>
> **Your first "What's due" report:**
>
> ```text
> 🔴 OVERDUE (3)
>   • Water heater flush       (101 days late)
>   • Furnace filter           (depends on filter age)
>   • Gutters                  (depends on when last cleaned)
>
> 🟢 DUE NEXT 30 DAYS
>   • Refrigerator coils      — due 2026-07-28
>
> ⚠️ WARRANTY EXPIRED
>   • Water heater            — 28 days ago
> ```
>
> Want me to set up a weekly Sunday digest reminder via cron?

### Example 2: Log a Task

> **User:** Just changed the HVAC filter — 16x25x1 MERV 11, $14 from Amazon.
>
> **Agent:** ✓ Logged to `Carrier Gas Furnace`:
> - **Task:** Replace filter (16x25x1 MERV 11)
> - **Date:** 2026-07-20
> - **Cost:** $14.00
> - **Source:** Amazon
>
> **Schedule updated:**
> - Last serviced: 2026-07-20
> - Next due: **2026-10-18** (90 days)
>
> 📊 Furnace filter spend YTD: $42 (3 changes @ $14).
>
> Anything else while you're in there? Want me to log the thermostat battery too?

### Example 3: Annual Cost Review

> **User:** How much have I spent on home maintenance this year? I feel like it's a lot.
>
> **Agent:** Pulling from your log... You have 11 tasks logged in 2026 totaling **$877.00**.
>
> ```text
> Plumbing       $322.50  (37%)  ← dishwasher pump + faucet
> HVAC           $187.00  (22%)  ← tune-up + filters
> Outdoor        $180.00  (21%)  ← gutter cleaning × 2
> Other          $187.50  (21%)
> ```
>
> You're averaging **$109.63/month**. For a 1998 home, that's actually **below the national median of $2,000/year** for maintenance spend. So you're doing fine — most of that is one-time repair (dishwasher pump).
>
> 💡 **Heads up:** your water heater is 10 years old and warranty expired. Typical lifespan is 10-15 years. Start budgeting $1,200-1,800 for replacement in the next 1-3 years. Want me to add a savings goal in your expense tracker?

### Example 4: Seasonal Playbook Request

> **User:** What should I do before winter?
>
> **Agent:** Generating your **Fall 2026 playbook** (Zone 5A, Boston area)...
>
> ```text
> 🍂 FALL PLAYBOOK  ·  Before first frost (mid-October typical)
> ────────────────────────────────────────────────
> URGENT (do in next 3 weeks)
>   [ ] Schedule furnace tune-up (wait times book up in October)
>   [ ] Clean gutters (leaves still falling — do it once more before freeze)
>   [ ] Order replacement furnace filter (run out mid-winter = cold house)
>
> BEFORE FIRST FREEZE (mid-October)
>   [ ] Disconnect & drain outdoor hose bibs
>   [ ] Reverse ceiling fans clockwise (warm air recirculation)
>   [ ] Test sump pump (pour a bucket — should kick on)
>   [ ] Inspect roof from ground (missing shingles, exposed flashing)
>
> LATE FALL (November)
>   [ ] Replace smoke + CO detector batteries
>   [ ] Clean dryer vent (winter = heavy use, lint buildup = fire risk)
>   [ ] Caulk check around windows + exterior doors
>   [ ] Replace HVAC filter before deep cold
>
> OPTIONAL (saves money long-term)
>   [ ] Insulate attic hatch (30 min, $15, big heat-loss fix)
>   [ ] Install smart thermostat (programmable savings ~$180/yr)
> ```
>
> Cross-referencing your assets: ✅ All tasks above apply to your home — no items skipped. Want me to convert these into tasks with due dates and a cron reminder schedule?

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User says *"I changed the filter"* but no asset exists yet | Ask once: *"Which HVAC unit? Basement furnace or upstairs heat pump?"*. Don't auto-create a default. |
| Cost logged but currency unclear (`$14` vs `¥14` vs `€14`) | Detect from prior tasks in `tasks.json`; default to `home.currency` if set, else USD. Show currency in confirmation. |
| Task logged but no asset match (user mentions "dishwasher" but no dishwasher in registry) | Create new asset entry on the fly with minimal info, ask 2 follow-ups. Don't block the log. |
| Seasonal playbook includes tasks user doesn't have (pool, sprinklers) | Always intersect the climate-zone template with the user's actual `assets[]`. Skip missing categories silently or with a one-line note. |
| Warranty dates missing — user says *"I bought it in 2020"* | Default warranty to 1 year for unstated (manufacturer default). Ask if extended warranty purchased separately. |
| Cadence overdue years (not just days) | Cap display at "**4.2 years late**" — don't say "1527 days". Use years if > 365. |
| Vendor name typed differently each time (*"Joe's Plumbing"* vs *"Joes Plumbing"* vs *"Joe's Plumb"*) | Fuzzy match existing vendors; if similarity > 0.85, use existing. Otherwise create new + ask user to confirm. |
| User logs *cost* but it was a gift / covered by warranty / insurance | Note in `notes` and offer `cost_out_of_pocket: true|false` flag — annual report can show both. |
| DIY vs pro confused | Add `diy: bool` per task. Annual report can split DIY savings: *"You saved ~$340 doing 4 tasks yourself vs. hiring out."* |
| Multiple tasks same day same asset | Allow but require explicit confirm: *"You logged a furnace filter swap and a furnace tune-up same day — confirm both? Or was the filter part of the tune-up?"* |
| First-time user with zero history | Seed 5-7 typical maintenance tasks as "starting points" the user can edit/delete. Don't start with empty state. |
| Annual report with no tasks | Show zero-state message: *"No tasks logged in 2026 yet. Start by telling me what you've done this year — even small things like changing batteries or testing detectors count."* |

---

## Verification Checklist

Before claiming a task is logged or report is correct, verify:

- [ ] Every task references a valid `asset_id` (or creates a new asset)
- [ ] `cost` is non-negative number; currency set per task
- [ ] `date` is ISO `YYYY-MM-DD` and not in the future (unless explicitly scheduled)
- [ ] After log: `asset.last_serviced = task.date` and `asset.next_due = task.date + cadence_days`
- [ ] `next_due` is recomputed, not preserved from old value
- [ ] Annual report totals sum across all `tasks` filtered by `date` within year
- [ ] Warranty expiration computed from `install_date + warranty_years`; not stored directly (it's derived — flag if mismatch)
- [ ] Overdue = `next_due < today AND last_serviced != next_due`
- [ ] "Expiring soon" warranty = `0 < days_until_expiry ≤ 90`
- [ ] "Expired" warranty = `days_until_expiry ≤ 0`
- [ ] Seasonal playbook intersects with user's actual asset list (no phantom items)
- [ ] Vendor names use stable IDs; fuzzy match handles typos
- [ ] All file paths under `~/.hermes/home/` — no other directories written
- [ ] If paired with `personal-expense-tracker`, offer to push annual maintenance total into "home" category

---

## Data Sources & Accuracy

| Source | Used for | Accuracy |
|--------|----------|----------|
| User chat input | All task logs, asset details, costs | 100% authoritative (it's *your* home) |
| `~/.hermes/home/assets.json` | Asset registry + cadence scheduling | Local-only |
| `~/.hermes/home/tasks.json` | Maintenance history + cost log | Local-only |
| `~/.hermes/home/vendors.json` | Plumber / electrician / HVAC tech contacts | Local-only |
| User-stated install dates | Warranty expiration math | Accurate IF user remembers correctly |
| Climate-zone templates (built-in) | Seasonal playbook content | Generic — adjust for your microclimate |
| Default cadence table (built-in) | New-asset scheduling | Industry-standard recommendations; user can override |

**This skill does NOT:**

- Connect to smart-home devices (Nest, Ecobee, Hue) for auto-detection
- Schedule real contractor appointments (no ServiceTitan / HomeAdvisor integration)
- Auto-pull receipts from email or bank statements
- Predict failure dates or run ML on your repair history
- Require any account credentials

**Privacy:** All data lives in `~/.hermes/home/`. The agent never transmits it. To back up, copy the directory. To wipe, delete it.

---

## Cron Integration (Optional)

Pair with `cron-pipeline-builder` for weekly digests:

```bash
# ~/.hermes/cron/home-digest.sh
#!/bin/bash
# Every Sunday at 8am — generate weekly digest
hermes -s home-maintenance-tracker "Generate my weekly home digest: \
  - What's overdue (red) \
  - What's due in the next 14 days \
  - Any warranties expiring in the next 90 days \
  - Cost this month so far. \
  Use assets.json + tasks.json + vendors.json."
```

```yaml
# ~/.hermes/cron/jobs.yaml
- name: home-digest-weekly
  schedule: "0 8 * * 0"
  command: ~/.hermes/cron/home-digest.sh
  notify: true

- name: home-seasonal-prep
  # First Sunday of Sep, Dec, Mar, Jun — seasonal playbook delivery
  schedule: "0 8 1-7 */3 *"
  command: ~/.hermes/cron/home-seasonal.sh
  notify: true
```

---

## Related Skills

- **personal-expense-tracker** — push annual maintenance spend into "home" category for unified budget view
- **subscription-manager** — some home services are recurring (pest control, lawn care, HVAC service plan)
- **habit-tracker** — track monthly habits like "test smoke detectors" alongside personal habits
- **gift-finder** — when a tool/hardware gift is needed (drill, ladder, stud finder), surface options
- **net-worth-tracker** — log home value + mortgage separately; this skill tracks maintenance *on* the home, not the home itself
- **report-formatter** — pretty-print annual cost reports for sharing with spouse / accountant