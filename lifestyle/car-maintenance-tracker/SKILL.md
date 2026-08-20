---
name: car-maintenance-tracker
description: "Log vehicle service & ownership from chat — oil changes, tire rotations, brake jobs, battery, registration, insurance renewals, repair history, fuel economy, multi-car households, and recall alerts. Mileage-based + time-based cadence scheduling, dealer-ready service records, local JSON. Privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, car, vehicle, automotive, maintenance, oil-change, tires, brakes, mileage, registration, insurance, fuel-economy, recall, multi-vehicle]
    related_skills: [home-maintenance-tracker, personal-expense-tracker, habit-tracker, reminder-scheduler]
---

# 🚗 Car Maintenance Tracker — 车辆维护与服务追踪

> Stop forgetting the registration renewal until you're late for work. Track every oil change, tire rotation, brake job, battery swap, registration, insurance renewal, fuel fill-up and repair for every car in the household — and walk into the dealership with a clean, printable service history.

---

## Overview

A car is a stack of recurring services on different triggers: oil every 5,000 mi or 6 months, tire rotation every 7,500 mi, brake fluid every 2 years, coolant flush every 5 years, transmission fluid every 30–60k mi, cabin air filter yearly, brake pads every 25–50k mi, battery every 4–6 years, spark plugs every 30–100k mi, timing belt every 60–100k mi. Then there are calendar items: registration renewal (annual/biennial), inspection/emissions (state-dependent), insurance renewal, warranty expiration, and toll/HOV pass expirations. Most owners forget half of them until the car fails or the dashboard reminds them at the worst possible moment. This skill turns Hermes into a household vehicle logbook: you describe what happened (*"rotated the tires on the Civic, odo 47820"*) and Hermes logs it, schedules the next service by mileage and/or time, tracks cost per mile, flags overdue items, and exports a service record any shop will accept.

| Capability | Description |
|------------|-------------|
| 🚙 Multi-vehicle registry | Each car: VIN, make/model/year/trim, license plate, color, purchase date & price, current odometer, garage location |
| 🛢️ Oil & fluid services | Oil change (conventional/synthetic blend/full synthetic), coolant, transmission, brake fluid, power steering, differential — by mileage or date |
| 🔘 Tire & brake log | Rotation, balance, alignment, new set (brand/model/size DOT), brake pad/rotor replacement, TPMS sensor |
| 🔋 Battery & electrical | Battery age, voltage test, alternator test, 12V accessory, hybrid high-voltage battery health |
| ⏰ Mileage-or-time cadences | Schedule by `every N miles` OR `every N months` OR `whichever comes first` — auto-compute next due |
| 📅 Calendar items | Registration, inspection/emissions, insurance renewal, DMV smog, parking pass — pure time-based |
| 💵 Fuel economy tracker | Per-fill MPG (US MPG or L/100km), rolling average per car, anomaly flags |
| 🛠️ Repair history | Free-form repair entries — symptoms, diagnosis, parts, labor, shop, warranty, follow-up |
| 🏷️ Vendor / shop list | Mechanic, dealer, tire shop, detailer — name, phone, address, last visit, rating, hourly rate |
| 📜 Warranty tracking | New car, powertrain, bumper-to-bumper, extended, tire, battery — expiration alerts |
| 🚨 Recall awareness | Year/make/model → known recall campaigns (informational; user verifies via NHTSA) |
| 📊 Cost-per-mile | Total ownership cost ÷ miles driven = $/mi report; category breakdown |
| 🏪 Dealer-ready export | Printable service record in markdown/PDF — accepted by any shop or at resale |
| 🔔 Overdue & upcoming | Anything past due or due in next 30 days; cron-friendly weekly digest |
| 💾 Local storage | All data in `~/.hermes/cars/` — no cloud, no leak |

## When to Use

- *"I just changed the oil on the Civic — 0W-20 full synthetic, $65 at Costco, odo 47820"*
- *"Add my car: 2018 Honda Civic LX, white, VIN 2HGFC2F58JH500000, purchased 2021-03, currently 45000 mi"*
- *"Rotate tires on my truck"*
- *"What's due in the next 30 days across all my cars?"*
- *"My check engine light came on — P0420"*
- *"Show my fuel economy for the last 6 months"*
- *"Add a shop: Joe's Auto, 555-0142, $110/hr, last visit 2026-04-10"*
- *"When does my registration expire?"*
- *"My Civic registration expires in 30 days — remind me"*
- *"Schedule brake fluid flush — every 2 years"*
- *"How much have I spent per mile on my car?"*
- *"Export service history for the Odyssey to give to the buyer"*
- *"我的车刚换了机油"* / *"我的车检下个月到期"*

## Core Workflow

### Step 1 — Register each vehicle

Before logging services, register the car. Ask for: year, make, model, trim, VIN (optional but recommended), license plate, color, purchase date, purchase price, current odometer, garage spot. Persist as JSON in `~/.hermes/cars/<nickname>/profile.json`.

```json
{
  "id": "civic-2018",
  "nickname": "Civic",
  "year": 2018,
  "make": "Honda",
  "model": "Civic",
  "trim": "LX",
  "vin": "2HGFC2F58JH500000",
  "plate": "7XYZ123",
  "color": "White",
  "purchase_date": "2021-03-15",
  "purchase_price": 18500,
  "current_odometer": 45000,
  "garage_spot": "Driveway-left",
  "notes": "Daily commuter; non-smoker; garage-kept on weekends"
}
```

If the user gives a nickname like "the truck" or "the SUV", canonicalize to a stable `id` slug. Refuse to overwrite existing IDs without confirmation.

### Step 2 — Define the service schedule

For each vehicle, ask which cadence schedule applies. The skill ships a default schedule by **driving condition** (normal / severe) — copy from `references/default-schedules.md`. Common ones:

| Service | Normal interval | Severe interval | Trigger |
|--------|-----------------|-----------------|---------|
| Oil change (synthetic) | 7,500–10,000 mi / 12 mo | 5,000 mi / 6 mo | mi-or-date |
| Tire rotation | 7,500 mi | 5,000 mi | mi |
| Tire balance | as needed | as needed | manual |
| Wheel alignment | 15,000–20,000 mi | 10,000 mi | mi |
| Cabin air filter | 15,000–20,000 mi / 24 mo | 15,000 mi / 12 mo | mi-or-date |
| Engine air filter | 30,000 mi / 36 mo | 15,000 mi / 24 mo | mi-or-date |
| Brake fluid flush | 24 mo | 24 mo | date |
| Coolant flush | 60 mo | 36 mo | date |
| Transmission fluid | 60,000 mi | 30,000 mi | mi |
| Spark plugs (iridium) | 100,000 mi | 60,000 mi | mi |
| Brake pads (front) | inspect 25,000 mi | inspect 15,000 mi | mi+manual |
| Battery test | 12 mo | 6 mo | date |
| Wiper blades | 12 mo | 12 mo | date |
| Registration | per state | per state | date |
| Inspection/emissions | per state | per state | date |
| Insurance renewal | 6–12 mo | 6–12 mo | date |

Let the user override any interval. Store custom cadences in `~/.hermes/cars/<nickname>/schedule.json`.

### Step 3 — Log every service & fill-up

Parse natural language like:

- *"rotated tires Civic 47820 mi"*
- *"oil change Odyssey — 5W-30 synthetic, $72, odo 62100, at Joe's Auto"*
- *"filled up 12.4 gal, 384 mi since last fill"*

Append to `~/.hermes/cars/<nickname>/log.jsonl` (one event per line). Schema:

```json
{
  "ts": "2026-08-18T09:30:00",
  "type": "oil_change",
  "odometer": 47820,
  "vendor": "Costco Tire",
  "parts": [{"name": "0W-20 full synthetic", "qty": 5, "unit_price": 8, "total": 40}],
  "labor_cost": 0,
  "total_cost": 65,
  "notes": "Used Mobil 1; reset maintenance minder"
}
```

For fuel fill-ups compute MPG from `miles_since_last / gallons`. Detect anomalies (MPG drop >15% vs trailing 5-fill average → flag possible issue).

### Step 4 — Compute due dates & overdue

For each scheduled service:

- `next_due_mileage = last_service_mileage + interval_miles` (when trigger is mi)
- `next_due_date = last_service_date + interval_months` (when trigger is date)
- `next_due = whichever_comes_first` (when trigger is mi-or-date)

Compare to current odometer (last logged) and `today`. Bucket each item:

| Status | Rule |
|--------|------|
| ✅ done | logged within current cycle |
| 🟢 upcoming | due in 30+ days / 1,000+ mi |
| 🟡 due_soon | due in 0–30 days / 0–1,000 mi |
| 🔴 overdue | past due date OR odometer exceeds next_due_mileage |

### Step 5 — Cost & efficiency reports

```bash
# All costs across all vehicles
python scripts/report.py --car all --period 2026

# Single vehicle cost-per-mile
python scripts/report.py --car civic-2018 --cost-per-mile

# Fuel economy trend
python scripts/report.py --car civic-2018 --mpg-trend --last 6
```

Report outputs:

- **Annual cost report**: by category (oil, tires, brakes, registration, insurance, repairs, fuel), year-over-year delta.
- **Cost-per-mile**: `(purchase_price + lifetime_maintenance + lifetime_fuel) / lifetime_miles`.
- **Fuel economy**: trailing 5-fill, 30-fill, lifetime MPG with min/max/stddev.
- **Upcoming due list**: sorted by days/mi remaining.
- **Warranty watch**: any warranty expiring within 90 days.

### Step 6 — Dealer-ready export

Generate a clean service record:

```bash
python scripts/export.py --car civic-2018 --format markdown --out civic-history.md
python scripts/export.py --car civic-2018 --format html --out civic-history.html
```

Sections (auto-generated): vehicle info → service log (chronological) → fuel economy summary → cost summary → notes. Print or share file with shop or prospective buyer.

---

## Example Invocations

### Example 1 — First-time setup

> **User:** Help me track maintenance on my two cars. A 2018 Honda Civic (daily driver, 45k mi) and a 2014 Toyota Sienna (family hauler, 98k mi).
>
> **Hermes:** [INFO] Registering 2 vehicles.
>
> ```bash
> mkdir -p ~/.hermes/cars/civic-2018 ~/.hermes/cars/sienna-2014
> ```
>
> Created `civic-2018` (2018 Honda Civic LX, white, plate 7XYZ123, garage-spot Driveway-left, current 45,000 mi) and `sienna-2014` (2014 Toyota Sienna LE, plate 5ABC987, current 98,000 mi). Both loaded with **normal-driving** schedule. Want to mark either as **severe** (towing, dusty, <10 mi trips, extreme temps)? Severe intervals shorten oil/tire/filter cycles. Tell me:
> - Civic: VIN, purchase date & price, exact trim, any dealer service history you want to backfill?
> - Sienna: same fields.
>
> I'll create the schedules and show what's due in the next 30 days.

### Example 2 — Logging a service

> **User:** Just changed oil on the Civic — 0W-20 full synthetic, $58 at Costco, odo 47820.
>
> **Hermes:** [EXEC] Logging oil change.
>
> ```json
> {"ts": "2026-08-18T09:30","type":"oil_change","odometer":47820,
>  "vendor":"Costco Tire","parts":[{"name":"Mobil 1 0W-20","qty":5,"unit_price":8.4,"total":42}],
>  "labor_cost":16,"total_cost":58,"notes":"Reset maintenance minder"}
> ```
>
> Saved to `~/.hermes/cars/civic-2018/log.jsonl`.
>
> Next oil change due at **57,500 mi** or **2027-08-18** (whichever first). Current odometer 47,820 → **9,680 mi / 365 days** remaining. ✅ on schedule.
>
> Anything else? *"rotate tires"*, *"fill up 11.8 gal, 412 mi"*, or *show upcoming*.

### Example 3 — Upcoming check + export

> **User:** What's due across both cars in the next 60 days?
>
> **Hermes:**
>
> | Car | Item | Due | Status |
> |-----|------|-----|--------|
> | Civic | Registration renewal | 2026-09-30 | 🟡 due_soon (43 d) |
> | Civic | Insurance renewal | 2026-10-12 | 🟢 upcoming (55 d) |
> | Civic | Tire rotation | 50,000 mi | 🟡 due_soon (2,180 mi) |
> | Sienna | Brake fluid flush | 2026-10-04 | 🟡 due_soon (47 d) |
> | Sienna | Inspection/emissions | 2026-11-15 | 🟢 upcoming (89 d) |
> | Sienna | Battery test | 2026-12-01 | 🟢 upcoming (105 d) |
>
> Total upcoming spend estimate: **~$420** (reg $180, insurance $0 paid yet, brake fluid DIY $30, tire rotation $80, inspection $45, battery test $0 DIY).
>
> Want me to export the Civic's full service history as Markdown to share with a buyer? Just say *"export civic service history"*.

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Odometer goes *backwards* (odometer swap, new cluster, typo) | Always compare new odometer to last logged; if lower by >100 mi, **pause and confirm** — likely a swap, not a rollback |
| User says *"oil change"* but didn't specify car | If only 1 vehicle → assume it. If multiple → **ask** before logging |
| Synthetic vs conventional oil confused | Default to **full synthetic** for cars 2010+; ask for older cars. Confirm the viscosity grade (0W-20, 5W-30, etc.) matches what's printed on the cap |
| Service interval guessed (no manual) | Use OEM-recommended conservative values; **mark source**: `oem`, `dealer`, `industry-standard`. Never invent numbers. If unsure, flag as `[estimate]` |
| Fuel economy computed from partial tank | Reject fill-ups with `gallons < 60% of tank capacity` OR MPG >2× trailing average; don't pollute the rolling average |
| Tire size unclear (e.g., "205/55R16") | Confirm with user; wrong size on a new tire set voids the speedometer + void warranty |
| Calendar items vary wildly by state | For registration/inspection/emissions: ask user. **Don't** hard-code state rules — they change yearly |
| Warranty expired vs service covered | Track warranty end-date; in cost report, mark warranty-covered repairs as `warranty_covered: true` and exclude from out-of-pocket cost-per-mile |
| Recall list is incomplete / outdated | Use informational placeholder; **always** tell user to verify at https://www.nhtsa.gov/recalls with their VIN. Do not auto-claim "no recalls" |
| Multi-vehicle household with shared garage | Use stable `id` slugs (`civic-2018`, `sienna-2014`), not nicknames ("the car"); nicknames can be changed without breaking data |
| Mileage-only schedule but only date is logged | Default to computing miles from last odometer reading + average daily miles. Flag with `[extrapolated]` |
| Import from dealer service record (PDF/image) | Use `screenshot-to-report` or `pdf-toolkit` skill first; never OCR raw image inline — extract text, then parse |

---

## Verification Checklist

Before claiming setup is complete, run:

```bash
python scripts/verify.py --root ~/.hermes/cars
```

Manual checks:

- [ ] At least one vehicle registered with VIN, plate, current odometer, purchase date
- [ ] Schedule.json created for each vehicle with cadence rule per service
- [ ] log.jsonl appends one JSON event per service (valid JSON, required fields)
- [ ] `report.py upcoming --days 60` returns sorted list with correct status buckets
- [ ] `report.py cost-per-mile --car civic-2018` returns numeric value with formula shown
- [ ] `export.py --format markdown` produces file with: vehicle info, log table, totals, fuel summary
- [ ] Overdue items appear in red (status 🔴); due_soon in yellow (🟡)
- [ ] No PII (VIN, plate, address) printed in chat — only in local file outputs
- [ ] Multi-vehicle command (`--car all`) correctly aggregates across `~/.hermes/cars/*/log.jsonl`
- [ ] Round-trip test: log an oil change → query upcoming → shows new next-due mileage/date

---

## Data Sources & Accuracy

**Local user data** is the source of truth for vehicle profile, schedule, log, and vendor list. The skill ships three reference files with industry-standard defaults:

- `references/default-schedules.md` — normal + severe driving intervals for ~30 common services
- `references/state-renewals.md` — registration/inspection cadences by US state (informational, user verifies)
- `references/recall-disclaimer.md` — guidance that recall data is not authoritative; user must verify at NHTSA by VIN

**No external API calls** are made by default. Mileage and date math is computed locally from logged events. Fuel economy, cost-per-mile, and due-date projections are all derived arithmetic.

**Accuracy caveats** (printed in every report footer):

1. **Schedule intervals are conservative defaults** — your owner's manual is authoritative. Override any interval with `--interval` flag or edit `schedule.json`.
2. **State-specific calendar items** (registration grace periods, emissions counties, inspection stations) change yearly. Verify with your state's DMV before relying on this skill for compliance.
3. **Recall awareness is informational only.** Always verify at https://www.nhtsa.gov/recalls with the vehicle's VIN.
4. **Fuel-economy anomalies** can be driving-style, weather, or mechanical. The skill flags them but does not diagnose; consult a mechanic for persistent drops.
5. **Service records are only as complete as what's logged.** If you bought the car used, backfill any dealer records you have; otherwise the cost-per-mile will be understated.

**Privacy:** All vehicle data — VIN, license plate, service history — stays in `~/.hermes/cars/` on the local machine. Nothing is uploaded. The skill never makes outbound HTTP requests unless the user explicitly invokes an online recall/parts lookup, and even then no personal data is sent.

---

## See Also

- [references/default-schedules.md](references/default-schedules.md) — Normal & severe service intervals
- [references/state-renewals.md](references/state-renewals.md) — Registration & inspection cadence by US state
- [scripts/verify.py](scripts/verify.py) — Verify data integrity across all vehicles
- [scripts/report.py](scripts/report.py) — Upcoming, cost-per-mile, MPG reports
- [scripts/export.py](scripts/export.py) — Dealer-ready service record export
- [templates/schedule.json](templates/schedule.json) — Default schedule template
- [templates/profile.json](templates/profile.json) — Vehicle profile template

> **Related skills:** `home-maintenance-tracker` (appliances & house systems), `personal-expense-tracker` (overall spend), `habit-tracker` (recurring checks), `reminder-scheduler` (cron-style due-date alerts).