# Recall Awareness — Disclaimer & Workflow

## What this skill does NOT do

The Car Maintenance Tracker does **not** query NHTSA, manufacturer databases, or any third-party recall API. It does not auto-detect open recalls against your VIN, and it explicitly does not warrant that any recall data it surfaces is complete, current, or accurate.

## Why

Recall campaigns are issued continuously — sometimes years after a vehicle's first sale. A complete recall check requires:

1. The exact 17-character VIN (not just year/make/model)
2. A live query against NHTSA's `vpic.nhtsa.dot.gov` API or the manufacturer portal
3. Reconciliation with manufacturer-specific TSBs (Technical Service Bulletins), which are separate from recalls

This skill stores VIN and year/make/model for *your* logging purposes only. It does not perform live recall lookups.

## What you should do

For each vehicle you track, **once per year** (or whenever you buy a used car):

1. Visit **https://www.nhtsa.gov/recalls**
2. Enter the 17-character VIN
3. Note any open recall campaigns, including:
   - **Recall number** (e.g., `23V-456`)
   - **Component** affected (e.g., Takata airbag inflator)
   - **Remedy status** (repaired / open / not yet available)
4. If open, schedule the free repair with an authorized dealer
5. Log the recall in your vehicle's notes (use the "recall watch" entry type):

```json
{"ts": "2026-08-18","type":"recall_open","recall_id":"23V-456",
 "component":"airbag inflator","status":"open",
 "fix_scheduled":"2026-09-15","dealer":"Honda of Springfield"}
```

6. After the repair:

```json
{"ts": "2026-09-15","type":"recall_closed","recall_id":"23V-456",
 "dealer":"Honda of Springfield","warranty":true,"cost":0}
```

## TSBs (Technical Service Bulletins)

TSBs are **not** recalls — they're manufacturer-issued repair procedures for known issues that don't rise to safety-recall level. They're useful for diagnosing weird symptoms, but they don't entitle you to free repairs outside warranty.

Useful TSB sources:

- https://www.nhtsa.gov/vehicle/2018/HONDA/CIVIC (example)
- Manufacturer dealer service portals
- Paid databases: Identifix, AllData, Mitchell1

## Free recall services

| Service | URL | Notes |
|---------|-----|-------|
| NHTSA Recall Lookup | https://www.nhtsa.gov/recalls | Authoritative; free; VIN-based |
| NHTSA VIN Decoder | https://vpic.nhtsa.dot.gov/decoder/ | Free; basic vehicle specs |
| SaferCar.gov | https://www.safercar.gov | Same NHTSA data; mobile-friendly |
| Manufacturer recall portals | Toyota.com/recall, Honda.com/recalls, etc. | Same data; sometimes better UX |

The skill recommends you bookmark your manufacturer page and check **once per year per vehicle** at minimum.

---

## Liability

The Car Maintenance Tracker is a logging tool, not a compliance tool. Tracking your own service is your responsibility. Failure to respond to a recall notice (which manufacturers mail to registered owners) is the owner's responsibility, not the tool's. This skill provides awareness prompts only.