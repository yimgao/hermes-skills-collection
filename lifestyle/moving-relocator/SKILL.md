---
name: moving-relocator
description: "Plan any move end-to-end from chat — apartment swap, house purchase, long-distance cross-country, international relocation. Generates 8-week (default) or compressed 4-week timeline, decluttering plan, packing inventory by room, label/color system, mover vs. DIY vs. hybrid comparison, 3 moving-day checklists (move-out / transit / move-in), address-change sweep across 30+ services, utility setup (electric/gas/water/internet) at origin and destination, school/medical/pet transfer packets, hidden-cost audit, deposit-protection playbook. Adapts to household size (studio → 5BR), distance (local <50mi → cross-country 3000mi → international), and budget."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [moving, relocation,搬家,搬家清单,搬家攻略,declutter, packing, movers, address-change, utilities, international-relocation, household, real-estate-transition,搬家预算,搬家打包]
    related_skills: [renewal-reminder, personal-crm, gift-finder, weekly-meal-planner, pantry-manager, party-planner, lost-item-recovery, travel-itinerary-planner, subscription-manager]
---

# 🚚 Moving Relocator — 搬家攻略 / 搬迁规划

> Don't move blind. Tell Hermes your move date, origin, destination, household size, and distance — get a complete 4-to-8-week plan: declutter, inventory, packing, mover quotes, utility setup, address changes, day-of checklists, and post-move wrap-up. Works for **local**, **long-distance**, and **international** moves; apartments, houses, and offices.

---

## Overview

Moving is consistently ranked in the top 3 most stressful life events. Most of that stress isn't the physical labor — it's the **350-line checklist** that lives in your head: which utility when, who do you change the address with, what's the deposit-protection clause, where do the pets go on moving day.

This skill turns *"I'm moving August 15th, Boston → Austin, 2BR, with a cat"* into a complete, executable plan with date-stamped tasks, dollar-aware budgets, and checkboxes your partner can also use.

| Capability | What It Produces |
|---|---|
| **Move profile** | Distance band, household size, services to set up, deadline math |
| **8-week timeline** | T-minus task list, two weekends / week cadence, gift-back schedule |
| **Decluttering plan** | KonMari-style 5-pile system + donation / sell / toss routing |
| **Inventory + label system** | Color-per-room boxes, QR-style room codes, fragile/sealable, content sketch |
| **Packing plan** | 10-box-per-day targets, what NOT to pack, hazardous item list |
| **Mover quote comparison** | DIY / hybrid / full-service comparison + 11 hidden-fee flags |
| **Day-of checklists** | Move-out, transit-day, move-in — three printable 1-pagers |
| **Utility setup** | Electric / gas / water / internet / trash — origin disconnect + destination connect |
| **Address change sweep** | 30+ services (USPS, DMV, banks, employer, subscriptions) with channels |
| **School / medical / vet transfer** | Records request packet + timing |
| **Hidden-cost audit** | Movers upcharge, lease break, pet transport, mileage, deposits — typical surprise buckets |
| **Deposit-protection playbook** | How to maximize return — pre-move photo record, what landlords always deduct |
| **International add-on** | Customs forms, import duties, pet import, currency / banking, shipping-vs-air-vs-container |

---

## When to Use

- User asks: *"I'm moving August 15, Boston to Austin — help me plan the whole thing"*
- User asks: *"Just signed a lease for Sept 1, how do I prep for moving day?"*
- User asks: *"I'm downsizing from a 3BR house to a 1BR apartment — what do I do with all this stuff?"*
- User asks: *"We're relocating from Shanghai to Singapore for work — what do I need to know?"*
- User asks: *"Got 3 mover quotes, can you help me compare without getting scammed?"*
- User asks: *"帮我整理一下搬家清单，月底前要搬完"*
- User asks: *"I have 4 weeks to move across the country — is that enough time?"*
- User asks: *"What utilities do I need to set up at my new place before move-in day?"*
- User asks: *"Help me write a goodwill letter for my security deposit return"*
- User asks: *"How do I move with 2 cats and a dog across 3 states?"*

---

## Core Workflow

### Step 1: Intake — Lock the 10 Critical Variables

Ask (or infer from prompt) the minimum needed to generate a tailored plan. If the user gives nothing, propose sensible defaults and confirm.

| Variable | Required | Description | Default |
|---|---|---|---|
| `move_date` | ✅ Yes | Target move-in day | — |
| `origin` | ✅ Yes | City / address (or just city) | — |
| `destination` | ✅ Yes | City / address (or just city) | — |
| `household_size` | ✅ Yes | Studio / 1BR / 2BR / 3BR / 4BR+ / office | 2BR |
| `occupants` | ❌ No | Adults, children (with ages), pets (type/count) | 1 adult, no kids/pets |
| `distance_band` | ✅ Yes | `local` (<50mi), `regional` (<500mi), `long-distance` (>500mi), `international` | Derived from origin/destination |
| `budget_total` | ❌ No | Move-related spend (USD/CNY/EUR) | $1,500 USD local / $4,000+ long-distance |
| `services_choice` | ❌ No | `diy` / `hybrid` / `full-service` / `pod` / `shipping-container` | Hybrid |
| `time_off` | ❌ No | Paid days off available for the move | 2 days |
| `helpers` | ❌ No | Friends / family helping? On move day? | None |
| `vehicle` | ❌ No | Personal vehicle(s)? Need to ship one? | None |
| `deposit_return_goal` | ❌ No | Prioritize getting full deposit back? | Yes |

**Distance auto-classification:**

```text
local        → same metro, ≤50 mi        → truck rental ($50-150)
regional     → 50–500 mi                  → pod or small mover ($400-1,200)
long-distance→ 500–3,000 mi, same country → full-service or truck rental+hotel ($2k-6k)
international→ cross-border               → shipping container / air freight ($4k-15k+)
```

If `move_date - today` < 6 weeks → switch to **compressed timeline** (4-week sprint, skip some declutter passes, prioritize perishables and address changes).

If `distance_band = international` → trigger **customs / visa / pet import** branch immediately.

### Step 2: Generate the Master Timeline

Generate an **8-week countdown** as the default, **6-week** if time allows, **4-week** if compressed. Tasks have date stamps relative to `move_date`.

#### Full 8-Week Plan

**T-8 weeks: Foundation**

- [ ] Confirm lease-out date / closing date on new place
- [ ] Book movers (or reserve truck / pod) — 3 written quotes minimum
- [ ] Set up a `moving-budget.md` (use `personal-expense-tracker` if available)
- [ ] Open a "move" email label or folder — capture every receipt, contract, estimate

**T-7 weeks: Declutter — Pass 1 (clothes / books)**

- [ ] KonMari-style: keep only what sparks joy; route to **Donate / Sell / Toss / Give-to-friend**
- [ ] Schedule Salvation Army / Goodwill pickup, or list 5 highest-value items on Facebook Marketplace / Craigslist / 小红书二手
- [ ] Pull 1 box of "maybe" → label and date → decision deadline

**T-6 weeks: Declutter — Pass 2 (kitchen / garage / storage)**

- [ ] Kitchen: discard duplicate utensils, single-use gadgets, expired pantry
- [ ] Garage / storage: schedule dumpster rental if needed ($200-400)
- [ ] Begin **inventory tracking** in `moving-inventory.csv`: room | item | value | keep/sell/donate | fragile?
- [ ] Document **high-value items** with photos + serial numbers (for insurance later)

**T-5 weeks: Address changes — first wave**

- [ ] **USPS mail forwarding** — set online, start date = move_date+1 (US only)
- [ ] Driver's license / state ID — book DMV appointment at destination (some states require within 10-30 days of residency)
- [ ] Voter registration update
- [ ] Insurance (auto / renters / home / health) address updates — call or app
- [ ] Bank / credit card / investment account — set mailing + billing address
- [ ] Employer / payroll / HR
- [ ] Subscription services — use `subscription-manager` to enumerate; one-by-one update address

**T-4 weeks: Bookings & logistics**

- [ ] Confirm mover quote in writing — signed contract, not just estimate
- [ ] Order supplies: boxes (~$1.50-3 ea), tape, bubble wrap, mattress bags, wardrobe boxes
- [ ] Reserve elevator on move day (apartment buildings: usually must be booked 2-4 weeks out)
- [ ] Pet transport plan — see Step 6 if applicable
- [ ] School transfer — see Step 6 if applicable
- [ ] **Set up utilities at destination** — see Step 5
- [ ] Schedule utility disconnects at origin

**T-3 weeks: Packing — non-essentials**

- [ ] Books, off-season clothes, decor, rarely used kitchenware
- [ ] Aim: 8-12 boxes per session, label BOTH SIDES with room + content summary
- [ ] Use the **color-coded room system**:

```text
🟥 Red    → Kitchen
🟧 Orange → Living / Family room
🟨 Yellow → Master bedroom
🟩 Green  → Kids' bedrooms
🟦 Blue   → Bathroom
🟪 Purple → Office / Study
⬛ Black   → Garage / Storage
⬜ White   → Fragile (always)
```

- [ ] **Hazardous / restricted items** — DO NOT pack: paint, propane, aerosols, lithium batteries, perishables, plants (long-distance), valuables (jewelry / cash / original docs — carry on person)

**T-2 weeks: Packing — partial essentials + paperwork**

- [ ] Half of kitchen (low-use), books, photos, art
- [ ] Pull out and consolidate all **important documents**: passport, birth certificate, vehicle title, insurance policies, financial records — keep together, hand-carry on move day
- [ ] Notify any final subscriptions / services / forwarding from old address

**T-1 week: Packing — final**

- [ ] All remaining except items in "open-first" kit (see below)
- [ ] Disassemble furniture the movers won't move (bed frame, desk — take photo of how it goes back together)
- [ ] Take dated **photo documentation** of EVERY room's condition — protects deposit + insurance claim (use phone camera with timestamp visible, or video walk-through)

**T-1 day: Pack the "Open-First" Kit**

A single bin you put on top of / last-in of the truck, containing everything needed the first 24-48 hours without unpacking:

```
- Toilet paper, hand soap, paper towels
- Sheet set for each bed (1 only)
- Towels (2)
- Phone chargers, power strip
- Basic tool kit (screwdriver, allen keys, box cutter, scissors)
- Trash bags
- Snacks, water bottles, instant coffee/tea
- One pot, one pan, spatula, knife, cutting board, can opener
- Pet supplies (if applicable)
- First aid kit
- All-important documents folder
- Pens + notepad for first-day notes (where to find the breaker, mailbox key, etc.)
```

**T-0 (move day): 3 checklists**

See Step 3.

**T+1 to T+7: Post-move wrap-up**

- [ ] Confirm utility connections actually worked on day 0 (log into account, test water heater, run microwave)
- [ ] Mail forwarding sanity check — anything critical arriving at old address?
- [ ] Update vehicle registration / driver's license within state-required window
- [ ] New bank / credit union branch visit (set up local accounts if moving state)
- [ ] Doctor / dentist / vet — transfer records if not done pre-move
- [ ] Schedule any final repairs / cleaning at origin within lease's notice window
- [ ] **Deposit-return follow-up**: if landlord doesn't return deposit within state-required deadline, send formal demand letter (template in Step 7)

### Step 3: Generate the 3 Move-Day Checklists

Produce **3 distinct printable checklists**, each ~20-40 lines, each optimized for one phase:

#### Move-Out Day (origin)

```text
□ Take timestamped photos of EVERY room (walls, floors, fixtures, appliances)
□ Strip beds, pack linens last
□ Defrost freezer if applicable (24h+ lead time)
□ Disconnect washer/dryer hoses, secure cords
□ Set thermostat to "auto" / leave fridge open slightly
□ Lock all windows, take final meter reads if not auto-submitted
□ Final trash run
□ Hand keys to landlord / property manager / realtor — get receipt (text/email OK)
□ Walk-through with landlord if required — TAKE PHOTOS during walkthrough
□ Hand over any mailbox keys, fobs, parking permits
```

#### Transit Day (in between, if long-distance or international)

```text
□ Hotel confirmation printed
□ Phone chargers / power bank fully charged
□ Food, water, prescriptions for travelers + pets
□ Driver's license + insurance card in wallet
□ Route mapped (avoid low-clearance bridges for tall trucks — if rental)
□ Cash for tolls / tipping movers (10-15% is standard if not on invoice)
□ Pet comfort: carriers, leash, water, quiet corner of vehicle
□ Take rest stops every 2 hours
```

#### Move-In Day (destination)

```text
□ Locate breaker panel, water shut-off, gas shut-off — write down locations
□ Test every light switch, every outlet (cheap outlet tester $10)
□ Run water in every fixture, flush every toilet — check for leaks
□ Test heating + cooling BEFORE moving boxes in
□ Confirm fridge / freezer temperature settles (4°C fridge, -18°C freezer)
□ Inspect EVERY box with visible damage — photograph BEFORE opening; document any damage inside
□ If any damaged box contains damaged goods → note on mover's delivery receipt (this is how you file a claim)
□ Stage boxes by room-color before unpacking
□ Unpack "open-first" kit immediately
□ Verify all keys / fobs work — test garage door, mailbox, common entries
□ Take a "condition at move-in" photo set — for future deposit disputes
```

### Step 4: Mover Comparison Framework

When the user has 2-3 mover quotes, run this analysis:

| Decision Axis | DIY (truck rental) | POD / Container | Hybrid (you pack, they drive) | Full-service |
|---|---|---|---|---|
| **Typical cost (2BR, 500mi)** | $400-800 | $1,200-2,500 | $2,000-4,000 | $3,500-7,000 |
| **Effort from you** | Pack + drive + unload | Pack + load/unload | Load + unload | Nothing |
| **Risk of damage** | High (you drive, you pack) | Medium | Low | Lowest |
| **Time to load** | 4-8 hours + drive | Same as DIY, but they drive | 3-5 hours | 2-4 hours |
| **Best for** | Local moves, minimalists, students | Long-distance on a budget | Time-poor but want some savings | Anyone with back issues / no time / high-value goods |

**11 hidden-fee flags to scan in any mover contract:**

1. Stair fees per flight (often $50-150 each)
2. Long-carry fees (truck can't park close)
3. Shuttle fee (truck too big for your street)
4. Bulky-item fees (piano, safe, treadmill)
5. Packing materials billed separately — and they overcharge
6. Weekend / month-end upcharge
7. Storage-in-transit if there's a gap
8. Fuel surcharge (often 8-15%)
9. Insurance: released-value coverage is FREE but only covers $0.60/lb/item — full-value coverage is +1-3% of declared value
10. Tip expected on top of quote (10-15% if they worked hard)
11. Cancellation / reschedule fees — read the small print for weather clauses

**Red-flag phrases:**

> "Binding estimate subject to re-weight"
> "Additional fees may apply"
> "Quote valid 7 days only" (extreme)

→ These often = bait-and-switch on move day. Get 3 quotes and **demand a binding or not-to-exceed estimate in writing**.

### Step 5: Utility Setup — Origin vs Destination

#### Origin (Disconnect Schedule)

| Service | When to disconnect | How |
|---|---|---|
| Electric | Day-of move or day-after | Call provider, request final-read date |
| Gas | Day-after move (so pilot stays lit) | Provider schedules tech visit if needed |
| Water | Day-after move (sewer + leak risk) | Often auto-billed final month |
| Internet | Day-of or day-before (avoid overlap) | Some providers require 30-day notice |
| Trash / recycling | Final pickup day before move | City service — usually no action |
| Renter's insurance | Day-of move out | Set cancel date = move-out day |
| Parking / HOA | End of month | Cancel / transfer to next party |

#### Destination (Connect Schedule)

| Service | When to call | Connection lead time |
|---|---|---|
| Electric | T-2 weeks | Usually 1-3 business days (sometimes same-day) |
| Gas | T-2 weeks, sometimes requires tech visit | 1-7 days |
| Water | T-1 week | Often 1-3 business days |
| Internet | **T-3 weeks** (most painful) | 5-14 days, install tech may need access |
| Trash / recycling | Auto on move-in, register address | 1 day |
| Renter's insurance | Bind BEFORE first night | Same-day online |

**Pro tip:** Internet is the single biggest planning miss. Order fiber/cable at T-3 weeks minimum, and have a **mobile hotspot backup** for the gap week because self-installation often fails due to outlet / ONT-box issues.

### Step 6: Special Packets — Schools, Medical, Pets

#### School Transfer (kids K-12)

- [ ] Request **official records** from current school — 2 weeks lead time
- [ ] Immunization records (most districts require up-to-date TDap / MMR / Varicella)
- [ ] New school enrollment proof of residency (lease + utility bill)
- [ ] Birth certificate + prior school records → for enrollment appointment
- [ ] IEP / 504 plan transfer if applicable
- [ ] Bus route / carpool arrangements at destination

#### Medical Transfer (chronic care)

- [ ] 30-day medication overlap (refill BEFORE the move)
- [ ] Request medical records (most states use a standard release form)
- [ ] Find new providers at destination — primary care, specialists, pharmacy with transfer
- [ ] If moving state — recheck formulary (covered meds may change)
- [ ] Durable medical equipment (CPAP / wheelchair / oxygen) — movers won't transport; bring with you

#### Pet Transfer (dogs/cats/reptiles/etc)

- [ ] Vet visit 10 days before move (within-state) — health certificate required for **air travel** and **most interstate moves**
- [ ] Interstate: USDA-accredited vet exam, APHIS 7001 form for some states
- [ ] International: rabies titer test 30+ days out, country-specific import permit, USDA-endorsed health certificate
- [ ] Update microchip registration to new address + new owner contact
- [ ] Reserve pet-friendly hotel if multi-day drive
- [ ] Plan a "pet decompression room" at destination — one quiet room with bedding, water, litter box away from door traffic
- [ ] ID tags with NEW phone number before move day

### Step 7: Deposit Return Playbook

Maximizing security deposit return is a skill, and it's mostly about **documentation timing**:

**Pre-move (T-1 week):**

- [ ] Timestamp-photograph every room: walls, floors, ceiling, fixtures, appliances
- [ ] Walk-through with landlord if they offer one (mirror their walk-through)
- [ ] Read your lease's **move-out clause** carefully: cleaning checklist, nail hole limits, professional carpet cleaning requirement
- [ ] Note any pre-existing damage they documented at move-IN (your move-in inspection report) — re-photograph those exact spots

**Move-out day:**

- [ ] Professional carpet cleaning IF your lease requires it ($100-200, with receipt)
- [ ] Clean: oven, fridge, bathroom tile grout, baseboards — the 4 things landlords deduct for
- [ ] Hand back keys with a signed receipt (text message counts)
- [ ] Final photo walkthrough

**Post-move (T+1 day to T+30 days):**

- [ ] Forward mail to new address immediately
- [ ] State-mandated return deadline:
  - **California**: 21 days
  - **New York**: 14 days
  - **Texas**: 30 days
  - **Massachusetts**: 30 days
  - Most states: 14-30 days
- [ ] If landlord misses deadline → send a **formal demand letter** (template):

```
[Date]
[Landlord / Property Mgmt Co]

Re: Security deposit return — [Property Address]

Dear [Landlord],

Under [State] law [cite], my security deposit of $[amount] was due no later than [deadline]. I have not yet received it as of today's date [actual date].

Please remit the full deposit to:
[New Address]
Within 7 days of this letter, with an itemized statement of any deductions.

If no response is received by [deadline + 7 days], I will pursue remedies including small claims court and statutory penalties.

Sincerely,
[Your name]
```

- [ ] If they provide an itemized statement and you dispute deductions → respond in writing with photo evidence referencing move-in condition report

### Step 8: International Add-On (if applicable)

When `distance_band = international`, layer these on top of the standard timeline:

**T-12+ weeks (yes, 3 months out):**

- [ ] Visa / work permit secured for all family members
- [ ] Research destination's customs rules — some countries restrict household goods (e.g., >12-month-old used electronics)
- [ ] Pet import — many countries require 4-7 month rabies titer + quarantine prep
- [ ] International shipping: 3 options
  - **Air freight** (fast, expensive — for essentials + documents): $3-8/kg
  - **Sea freight LCL** (Less-than-Container-Load): 4-8 weeks, $1,500-3,500 for a 1BR
  - **Sea freight FCL** (Full Container, 20ft or 40ft): 6-10 weeks, $3,000-8,000
- [ ] Currency: open a destination-country bank account remotely if possible (some banks require in-person)
- [ ] Tax residency / driver's license conversion at destination

**T-6 weeks:**

- [ ] Customs paperwork: most countries require a **detailed inventory** (with serial numbers + values) filed before shipment
- [ ] Notarize key documents: birth certificates, marriage certificate, diplomas (some need apostille)
- [ ] Decide what to leave behind vs. ship — rule of thumb: anything that costs <2x its weight to replace, sell/donate and re-buy at destination

**T-2 weeks:**

- [ ] Clean out fridge + pantry (no food residue for international pest inspection)
- [ ] Lock luggage tags with destination address written in **destination language**
- [ ] Stop mail forwarding — actually you can't do international USPS forwarding. Have a trusted friend collect and forward scan

### Step 9: Hidden-Cost Audit (final review before move)

Most moves run 20-40% over budget because of these buckets:

| Category | Typical surprise $ | How to mitigate |
|---|---|---|
| Last-minute boxes / tape / supplies | $100-200 | Buy in bulk at T-4 weeks |
| Eating out (kitchen is packed) | $200-500 | Plan 2 weeks of no-cook meals + Open-First Kit |
| Hotel on transit night | $80-250 | Book refundable rooms T-6 weeks |
| Pet sitter / boarding | $50-300 | Pre-arrange for pets |
| Childcare on move day | $100-300 | Pre-arrange for kids |
| Utility overlap charges | $50-200 | Schedule disconnect day-after, not day-of |
| Storage-in-transit if delays | $100-400/mo | Avoid by buffer-planning, not booking on month-end |
| Mover upcharges (stair/carry/bulky) | $200-800 | Read contract + take stairs pictures / walkthrough at quote |
| Lease break fee (if mid-lease) | 1-3 months rent | Negotiate with landlord OR sublet OR find replacement tenant |
| Damage deductions at destination | $0-500 | Full-value insurance with mover + photo evidence pre-load |
| New curtains / blinds / rugs (sizes don't fit) | $200-1,000 | Wait-and-see, budget flexibility |
| Pest control / deep clean at origin | $150-400 | Check lease requirements BEFORE quoting |

---

## Example Invocations

### Example 1: Local apartment swap

```
> I'm moving August 15, Brooklyn 1BR (650 sqft) to a 2BR in Queens — same lease 
> end date on both. Just me and a cat. I've got 5 weeks. Hybrid (I'll pack, 
> hire movers for the day). Help me plan it.

Agent runs moving-relocator:

1. Distance = local (<30mi), time = compressed 5-week, services = hybrid
2. Generates compressed timeline starting T-5 weeks
3. Mover comparison: 1 BR + studio-style 2BR (~30 boxes) — hybrid ~$700-1,200 typical
4. Utility plan: ConEd → PSEG (or stay on ConEd if Queens addresses overlap)
5. Single cat, 1 carrier, vet records transfer, new microchip contact
6. Output: 6-week checklist + 3 day-of checklists + utility setup table + 
   mover red-flag list
7. Highlights the 3 things that always go wrong locally:
   - Elevator booking on move-out day (book NOW if not ground-floor)
   - Pet-friendly movers (filter by "no pet fee" before quoting)
   - Mail forwarding timing (start date = move-day + 1)
```

### Example 2: Long-distance relocation

```
> Long-distance move — Boston (2BR, 4 adults incl. 2 teens) to Austin TX, 
> moving August 30. I've got 8 weeks. Mixed: we'll ship most stuff, drive 
> one car. Job relocation, employer covers up to $8k.

Agent runs moving-relocator:

1. Distance = long-distance (1,800mi), services = full-service shipping + personal vehicle drive-down
2. Generates full 8-week plan
3. Highlights employer relocation policy questions:
   - Is it "managed" (they hire for you) or "lump-sum" (you DIY + submit receipts)?
   - What's covered: movers only? Also temp housing? Final-trip drive?
4. School transfer packets for the 2 teens — records request, immunization check
5. Vehicle plan: drive 1, ship 1 (or sell 1 if not worth shipping)
6. Output: full timeline + school transfer packet + employer-coverage checklist + 
   state-specific items (TX doesn't have state income tax — savings calc)
7. Hidden-cost audit: $1,500-2,500 likely over budget → suggest reallocating from 
   "new curtains" to "buffer"
```

### Example 3: International relocation

```
> 帮我整理一下搬家清单。We'll move from Shanghai to Singapore in October — 
> 3BR, 2 adults + 1 kid (8yo), 1 dog. My company is paying for full relocation. 
> How much lead time do I need?

Agent runs moving-relocator:

1. Distance = international (China → Singapore), needs T-12 weeks minimum
2. Triggers international add-on immediately
3. Flags critical path items:
   - Kid's school: Singapore international school waiting lists — apply NOW
   - Dog: Singapore requires rabies titer, AVA permit, import license — 4-7mo lead
   - Customs: detailed inventory with values required before shipping
4. Generates local-language label template (Chinese + English) for boxes going through customs
5. Output: T-12-week timeline + Singapore pet import packet + international school list + 
   shipping company shortlist (LCL vs FCL comparison)
6. Pair recommendation: "use gift-finder for goodbye gifts to colleagues in Shanghai"
```

---

## Common Pitfalls

| Problem | Solution |
|---|---|
| Don't realize how long moving takes — start packing too late | Even 8-week plans feel tight. Compress only if forced. |
| Forget to book movers — peak season (May–Sept) books 4-6 weeks out | Lock mover quote by T-6 weeks, written estimate, not just a phone call |
| Internet gap at destination — work from home days lost | Order ISP at T-3 weeks minimum; have mobile hotspot as backup |
| Boxes have no room labels — 200 unlabelled boxes at destination | Color-code by room, label BOTH top AND side with content summary |
| Important docs packed in moving truck → lost | NEVER pack: passports, vehicle titles, insurance policies, financial records, keys. HAND-CARRY. |
| Plants in long-distance truck — die or contaminate | Long-distance moving companies won't transport plants. Give them away or compost. |
| Land-lord takes egregious deposit deductions | Photo documentation + move-in inspection report is your evidence. Know your state's deadline. |
| USPS forwarding doesn't cover everything | Many services require manual address update separately. Run sweep from `subscription-manager`. |
| Pet escapes during move chaos | Confine pets in one quiet room (bathroom) with door sign; never let movers open that door |
| Food waste — move fridge the day it's still half full | Plan 10-day "eat down the pantry" before move, donate sealed non-perishables |
| Last-minute utility disconnect call → charges | Set reminder alerts at T-4 weeks + T-2 weeks + T-3 days |
| Forgetting DMV / voter registration after cross-state move | Many states have a 10-30 day window. Calendar the appointment before move. |
| Mover quotes wildly different prices → low-baller wins → surprise fees day-of | Always demand "binding" or "not-to-exceed" estimate in writing. |
| Refrigerator won't cool immediately → food spoilage | Don't load perishables until fridge is at temperature. Have 24h cooler plan. |
| Children / pets stressed by move chaos | Plan a decompression day at destination. Don't unpack Day 0. |

---

## Verification Checklist

Before declaring the move "done," confirm with the user:

- [ ] User confirmed move_date, origin, destination, household_size, distance band
- [ ] Mover quote is binding/not-to-exceed, signed, in writing (if applicable)
- [ ] All utilities set up at destination with confirmed activation dates
- [ ] All utilities disconnected at origin OR scheduled
- [ ] Mail forwarding activated (US only) OR manual sweep done
- [ ] DMV / voter registration / schools / medical / vet transfer packets prepared
- [ ] "Open-first" kit identified and ready to load last
- [ ] Important documents folder separated and confirmed hand-carry
- [ ] Color + label system on every box (top + side)
- [ ] Pre-move condition photos taken + saved in 2 places
- [ ] Mover insurance: full-value OR alternative arranged
- [ ] Hidden-cost audit reviewed — buffer set
- [ ] Pet carrier, food, vet records ready
- [ ] Children (if any) prepared + school enrollment confirmed
- [ ] Day-of checklists printed (3 copies: origin, transit, destination)
- [ ] Post-move wrap-up plan exists for T+1 to T+30 days
- [ ] Deposit-return follow-up scheduled (state deadline + 3 days)

---

## Data Sources & Accuracy

- **Utility timelines**: Generally accurate for US states. International utility times vary; recommend local provider confirmation.
- **Mover cost ranges**: Based on typical 2024-2025 US pricing; local markets vary ±30%.
- **State deposit-return deadlines**: Verify against [state-specific landlord-tenant statutes](https://www.nolo.com/legal-encyclopedia/state-security-deposit-laws.html).
- **DMV / voter registration windows**: State-by-state; check with destination state DMV directly.
- **Pet import requirements**: Country-specific; always check embassy + USDA APHIS + destination country agricultural authority. Rules change frequently.
- **International school fees and admission**: Visa, quota, and waitlist data varies year-to-year.
- **Customs / import duties**: Country-specific; consult destination country's customs authority.

This skill does **not** connect to external services — it generates plans, checklists, scripts, and templates that the user executes locally or with their own accounts. No login credentials, no third-party data upload, no tracking. All generated files (inventory CSV, budget, address-sweep list, deposit-demand letter) live on the user's machine.

---

## Pairs Well With

- **`renewal-reminder`** — track IDs / insurance / car registration that change at the new address
- **`personal-crm`** — identify which friends at origin need goodbye touches, which at destination need hello
- **`gift-finder`** — for goodbye / housewarming gifts
- **`weekly-meal-planner`** — "eat down the pantry" plan for the 10 days pre-move + first-week at destination
- **`pantry-manager`** — track what's expiring, prioritize eating first
- **`party-planner`** — housewarming party at destination once unpacked
- **`subscription-manager`** — sweep through subscriptions to update addresses
- **`travel-itinerary-planner`** — the transit-day itinerary is essentially a trip plan
- **`lost-item-recovery`** — if a box or document goes missing mid-move
- **`car-maintenance-tracker`** — pre-move service for the vehicle that's driving the cross-country leg
