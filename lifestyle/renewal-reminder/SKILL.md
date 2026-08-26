---
name: renewal-reminder
description: "Track every expiration & renewal deadline from chat — passport, visa, driver's license, ID cards, insurance, certifications, domain/SSL, warranties, memberships, permit renewals, and lead-time warnings (e.g. passport < 6 months blocks travel). Proactive reminders, renew-by dates, cost history, document checklist. Local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, renewal, expiration, passport, visa, license, insurance, certification, warranty, domain, ssl, membership, deadline, reminder, document, travel]
    related_skills: [travel-itinerary-planner, car-maintenance-tracker, home-maintenance-tracker, subscription-manager, personal-crm, habit-tracker]
---

# ⏳ Renewal Reminder — 证件与续期到期管理

> Passport expires in 9 months — most countries won't let you in with under 6 months of validity, and renewals take 4–6 weeks. Your driver's license, green card, visa, professional certs, insurance, domain, and warranties all have their own windows. This skill makes Hermes your expiration radar: you mention any document or renewal once, and it tracks the deadline, computes the *renew-by date* (with lead time), reminds you early, and keeps a printable document checklist.

---

## Overview

Every adult silently juggles 20–40 time-bounded items: identity documents (passport, driver's license, state ID, green card, visa), insurance (health, auto, home, renters, umbrella), professional credentials (certifications, licenses, CE credits), financial (CC expirations, AD&D, warranties), digital (domains, SSL certs, hosting renewals), and memberships (gym, warehouse clubs, professional orgs). Missing a window costs money (late fees, re-application, lapsed coverage) or blocks plans (a trip cancelled because the passport is stale). Most people track these in their head and find out too late.

This skill turns Hermes into a renewal radar: log any item once (*"my passport expires 2031-04-20"*), and Hermes computes the safe **renew-by date** using the item's lead time (passports need 4–6 weeks + 6-month travel validity rule; visas vary; domains 30 days), sets tiered reminders, tracks renewal cost history, and produces a one-page document checklist for travel or tax season.

| Capability | Description |
|------------|-------------|
| 🪪 Identity documents | Passport, driver's license, state ID, green card, visa, work permit, birth certificate, social security card — expiry + issuing authority + doc number (stored locally) |
| 🛂 Travel validity rule | Passport must have **6 months validity** for most international travel → auto-alert when inside the 6-month window even if not expired |
| 🏥 Insurance policies | Health, auto, home, renters, umbrella, life, AD&D — coverage period, auto-renew flag, carrier, policy number, premium, deductible |
| 🎓 Professional credentials | Certifications, licenses, CE/CPE credits, background check validity, professional association dues |
| 🔐 Digital assets | Domains (registrar + auto-renew), SSL/TLS certificates, hosting, SaaS contracts, trademark renewals |
| 🏷️ Warranties & memberships | Extended warranties, gym/warehouse memberships, professional orgs, alumni perks — renewal date + cost |
| ⏰ Lead-time-aware reminders | Each item type has a default lead time (renew-by = expiry − lead); overridable per item |
| 📢 Tiered alerting | 90 / 60 / 30 / 14 / 7 days out + overdue; daily digest lists only what's due; cron-ready |
| 💵 Cost history | Log what each renewal cost (and when), spot price hikes, budget next year's renewals |
| 📋 Document checklist | One-page export of all expiring docs — travel-ready or renewal-season checklist |
| 🔔 Life-event linkage | Auto-flag items that block an event: passport/visa for trips, license for rental car, insurance for new home |
| 💾 Local storage | All data in `~/.hermes/renewals/` — no cloud, no leak |

## When to Use

- *"My passport expires 2031-04-20 — add it"*
- *"When should I renew my passport before the Japan trip in March?"*
- *"What's expiring in the next 60 days?"*
- *"Remind me 90 days before my green card renewal window opens"*
- *"I renewed my driver's license — $32, expires 2032-08"*
- *"What documents do I need for the Europe trip?"*
- *"My domain hermes-test.dev renews June 1 — check my SSL too"*
- *"Set up a reminder for my PMP recertification (60 PDUs by Dec)"*
- *"Which of my certs expire this year?"*
- *"我的护照还有 8 个月到期，去泰国来得及吗？"*

## Core Workflow

### Step 1 — Register an item

When the user mentions any expiring document or renewal, extract and persist:

```json
{
  "id": "passport-2026",
  "type": "passport",                    // passport|visa|license|id|insurance|certification|domain|ssl|warranty|membership|other
  "label": "US Passport",
  "holder": "Alex",
  "issuer": "US Dept of State",
  "doc_number": "5xxxxxxx",              // optional, stored locally
  "issue_date": "2021-04-20",
  "expiry_date": "2031-04-20",
  "renew_by": "2031-03-01",              // auto-computed: expiry − lead_time
  "lead_time_days": 50,                  // default by type, overridable
  "auto_renew": false,
  "cost": 130,                           // last known renewal cost
  "notes": "6-month validity rule applies for intl travel",
  "reminder_days": [90, 60, 30, 14, 7], // tiered defaults, overridable
  "created": "2026-08-25",
  "status": "active"                     // active|renewed|expired|archived
}
```

**Default lead times (renew-by = expiry − lead):**

| Type | Default lead time | Notes |
|------|-------------------|-------|
| Passport | 90 days | + 6-month travel validity window check |
| Visa | 60 days | varies by country; ask if unsure |
| Driver's license / ID | 30 days | mail-in or DMV appointment |
| Insurance (all) | 45 days | shop around before auto-renew hits |
| Certification | 60 days | CE credits + application processing |
| Domain | 30 days | registrar grace is NOT guaranteed |
| SSL certificate | 14 days | avoid last-minute browser warnings |
| Warranty | 30 days | claim windows often require notice |
| Membership | 30 days | decide before auto-renew charges |

### Step 2 — Compute windows & validity checks

- **Expiry date** → the hard deadline.
- **Renew-by date** = `expiry_date − lead_time_days`. Reminders fire against renew-by (so you act while there's still time), and status flips to `overdue` past renew-by, `expired` past expiry.
- **Travel validity check**: for passports, if `today + 6 months > expiry_date`, flag `⚠️ travel-blocked — most countries require 6 months validity`. Same for visas with 3-month rule where applicable.
- If the user mentions an upcoming trip (or you can read it from travel-itinerary-planner data), check each trip against all documents: passport validity ≥ 6 months past return date, visa valid, license valid for rental car, insurance covers dates.

### Step 3 — Log renewals & costs

When user reports a renewal, update the item: `status: renewed`, new `expiry_date`, `cost`, `renewal_history` append (date, cost, method). If the cost jumped, flag it: *"Your auto insurance went from $980 to $1,240/yr (+27%) — worth shopping around."*

```json
{
  "renewal_history": [
    { "date": "2026-08-25", "cost": 130, "method": "online", "notes": "renewed 10 months early, standard processing" }
  ]
}
```

### Step 4 — Daily digest (cron-ready)

Each run, compute the three buckets and output a digest:

```
🔴 EXPIRED (3)   — act now
  • US Passport       expired 2026-08-01 (14d ago)
  • SSL hermes-test   expired 2026-08-20 (5d ago)
🟠 OVERDUE renew-by (2) — renew now to avoid lapses
  • Home insurance    renew-by was 2026-08-10
🟡 DUE in 30 days (5) — plan this week
  • Driver's license  renew-by 2026-09-15 (in 21d)
  • Domain .dev       renew-by 2026-09-01 (in 7d)
📦 TRAVEL BLOCKERS — passport has 5 months validity left (need 6)
```

### Step 5 — Document checklist export

Generate `~/.hermes/renewals/checklist-<context>.md`:

- **Travel checklist**: passport (6-mo validity), visa, driver's license (rental car), insurance cards, international driving permit if needed.
- **Renewal season checklist**: everything due in the next 90 days with renew-by dates, estimated cost, and the phone/URL to renew.

## Example Invocations

**1. Log + compute the travel window**

> **User:** My passport expires April 20, 2031 — add it. Also we're booking Thailand for March 2031.
>
> **Agent:** ✅ Logged **US Passport** (holder: Alex, expires 2031-04-20).
> - Renew-by: **2031-03-01** (90-day lead) → reminder set for 2030-12-01, 2031-01-15, 2031-02-01, 2031-02-15, 2031-02-22.
> - 🇹🇭 **Thailand trip (Mar 2031):** passport has **10 months** validity past return date — ✅ meets the 6-month rule. No blockers.
> - Next renewal cost on file: $130 (2021 rate). Want me to add your visa + travel insurance too?

**2. Daily digest, everything on fire**

> **User:** What's expiring soon?
>
> **Agent:**
> ```
> 🔴 EXPIRED: SSL cert for hermes-test.dev (5d ago)
> 🟠 OVERDUE: Home insurance renew-by was Aug 10 — coverage lapsed risk
> 🟡 DUE 30d: Domain .dev (7d), Driver's license (21d), PMP cert (28d)
> 💡 $1,870 of renewals due in next 90 days. Want the checklist?
> ```

**3. Trip blocker discovered**

> **User:** I'm planning a Europe trip in June — check my documents.
>
> **Agent:** ⚠️ **TRAVEL BLOCKER** — your passport expires **2026-11-15**, which is only **5 months** past your return date. Schengen requires 6 months validity.
> - Recommended: renew **now** (renew-by for that trip is 2026-05-01; you have 2 weeks).
> - US expedited passport: ~$190, 2–3 weeks processing. I can track it as a to-do.

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User gives only "expires next year" | Ask for a concrete date or month; store best-effort `expiry_month` and prompt for exact date later |
| Passport 6-month rule forgotten | Always compute `expiry − (return date + 6 months)` for any trip that involves a passport |
| Domain/SSL near-miss | Domains: warn at 30 days, never assume registrar grace. SSL: warn at 14 days, most browsers hard-fail after |
| Auto-renew insurance sneaks up | For policies with `auto_renew: true`, still remind at 45 days so the user can shop rates before it locks |
| Renewal cost inflation invisible | Keep `renewal_history`; when a new cost deviates >15% from last, surface it explicitly |
| Multiple holders (family) | Use the `holder` field; digest groups by holder so you don't show everyone's items to one person |
| Expired items clutter the digest | Move to `status: expired` and keep in a separate section; archive after 90 days unless user says otherwise |
| False sense of "renewed" | After any renewal, update `expiry_date` immediately — a renewed item without a new expiry is still a liability |

## Verification Checklist

- [ ] Register at least 3 different item types (e.g. passport, domain, insurance) and confirm they persist to `~/.hermes/renewals/`
- [ ] Renew-by date computes correctly from a non-default lead time (e.g. SSL 14 days)
- [ ] Travel validity check flags a passport inside the 6-month window
- [ ] Daily digest shows correct buckets (expired / overdue / due-30d / blockers) and nothing missing
- [ ] Renewal log appends to `renewal_history` and updates the item's `expiry_date`
- [ ] Cost deviation >15% triggers an explicit flag
- [ ] Document checklist export generates valid Markdown with all due items
- [ ] No item data leaves the machine (no network calls, no upload)

## Data Sources & Accuracy

- **Expiry dates / lead times**: all dates come from what the user tells you. Default lead times are conservative industry norms (passport 90d, visa 60d, SSL 14d, etc.) and can be overridden per item.
- **Travel validity rules**: the 6-month passport rule is a common international standard (Schengen, Japan, Thailand, etc.) but **not universal** — always advise checking the destination country's embassy site (`travel.state.gov` for US citizens) for the authoritative rule.
- **Renewal costs**: user-reported; used only for budgeting and inflation flags, never fetched from third parties.
- **Domain/SSL**: registrar renewal dates are user-supplied; Hermes does not query WHOIS or certificate transparency by default (privacy-first), but can if the user explicitly asks.
- **Accuracy disclaimer**: this skill is a reminder system, not a legal or financial advisor. Missed reminders are possible — critical documents (passport, visa, license) should be double-checked against the issuing authority.
