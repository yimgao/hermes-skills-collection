---
name: insurance-shopper
description: "Choose the right insurance policy before you buy — auto, home, renters, health (HMO/PPO/EPO/HDHP), life, disability, pet, umbrella, gear. Decodes dense quote PDFs into a structured table, compares every quote on identical limits (not sticker price), scores coverage against what YOU actually risk, flags disqualifying red flags, and returns a BUY / SKIP verdict with a pasteable decision brief. Local JSON, stdlib-only scripts, zero upload."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, insurance, auto-insurance, home-insurance, renters, health-insurance, hmo, ppo, epo, hdhp, life-insurance, disability, pet-insurance, umbrella, coverage-limits, deductible, liability, quotecompare, claims, risk, consumer-protection]
    related_skills: [bill-negotiator, purchase-advisor, personal-expense-tracker, net-worth-tracker, decision-journal, receipt-vault, renewal-reminder, contract-reviewer, tax-prep-assistant, equity-comp-tracker]
---

# 🛡️ Insurance Shopper — 保险选购顾问

> You pulled three auto quotes. The cheapest was $1,180/yr — with **$25,000** bodily injury liability. The most expensive was $1,615/yr — with **$300,000**. The cheap one is $435/yr cheaper and leaves you personally on the hook for **$225,000** if you seriously injure someone. Nobody mentioned this. The quote PDFs were 14 pages of dense tables with a "Bodily Injury Liability per Person" row you were supposed to understand.
>
> 你拿了 3 份车险报价。最便宜的 $1,180/年——第三者责任只有 **$25,000**。最贵的 $1,615/年——责任 **$300,000**。便宜的那份每年省 $435，而一旦你重伤别人，**$225,000 要你自己赔**。没有人提醒过你，报价单只是 14 页密表格。
>
> This skill turns "I got some quotes" into **"here is what I'm actually risking under each one, here's the cheapest plan that still protects me, and here's what to write on the quote form."**

## Overview / 概述

Insurance shopping has a specific failure mode: **the price is legible, the coverage is not.** Every quote leads with a number you understand ($1,180/yr) and hides the numbers that decide whether you're protected (liability limits, replacement-vs-depreciated cost, out-of-pocket max). Two failures follow:

1. **Buying the cheapest quote** — which is priced off liability limits, because liability limits are the cheapest thing to lower and the most expensive thing to need.
2. **Buying the first quote** — which is often the incumbent's renewal, marked up 20% because nobody shopped.

This skill makes the coverage legible and puts the decision on a single page:

| Capability | What It Does | How |
|------------|-------------|-----|
| **Quote decoding** | Turns a dense quote PDF / email / screenshot-OCR text into structured JSON — limits, deductible, premium, features, red flags | `scripts/extract.py` — 25+ label patterns, dotted-leader and `Label: $N` formats, multi-plan section isolation |
| **Equal-footing comparison** | Normalizes every quote to the same table: identical rows, identical units, premiums annualized (6-month × 2, monthly × 12) | `scripts/compare.py` — 9 product registries, weighted coverage scoring |
| **Exposure analysis** | Compares your actual limits against a *realistic worst case* and reports the shortfall in dollars, not adjectives | `scripts/gaps.py` — 11 built-in scenarios + auto-scenario from vehicle value/mileage |
| **Red-flag detection** | Catches disqualifiers: state-minimum liability, ACV-instead-of-replacement-cost, excluded theft, pre-existing exclusions | Built into both scripts |
| **Scenario testing** | "What if I total the car in a flood? What if the ER visit turns into a hospitalization?" | Custom scenario JSON + `--scenario` |
| **Weighted scoring** | You decide what matters (liability in CA vs. price in Ohio) — the scorer uses your weights | `--weights weights.json` |
| **Decision brief** | A paste-ready BUY / SKIP / RENEGOTIATE verdict with the two numbers to quote back to the carrier | Agent-generated from the script output |
| **Policy ledger** | Every quote, every decision, every renewal date — local JSON, cron-remindable | `~/.hermes/data/insurance/` |

All data stays local. Nothing is uploaded. The scripts are stdlib-only Python.

## When to Use

- *"I got 3 car insurance quotes — which one should I take?"*
- *"GEICO quoted $1,180 and Progressive quoted $1,615. Why is one so much more?"*
- *"My auto renewal went from $980 to $1,340. Did they change my coverage?"*
- *"Is $25,000 liability actually enough?"* (It is not. This is the single most common under-insurance in the US.)
- *"Compare these two homeowners quotes — one is $1,200/yr, the other is $980/yr"*
- *"Should I buy the HMO or the PPO? I'm on a $2,000/month generic prescription"*
- *"HMO says specialist visits are $50 with a referral. PPO says $40 without. Which do I actually want?"*
- *"What deductible should I pick?"*
- *"Does my renters insurance actually cover my laptop?"*
- *"How much life insurance do I need?"*
- *"My pet had ACL surgery — $8,400. Would my pet insurance have covered it?"*
- *"Do I need an umbrella policy if I already have $300k auto liability?"* (Yes, if your net worth is above your liability limits.)
- *"What happens if I'm in a car accident and I'm at fault?"*
- *"Is my home covered at replacement cost or what the house is worth today?"* (Most people don't know, and the difference is $200k.)
- *"Compare my renters insurance against Lemonade"*
- *"Set a cron to remind me 30 days before each insurance renewal"*
- 用中文：*帮我对比这三份车险报价 / 这两个健康保险哪个更划算 / 我该选多少免赔额 / 我的宠物保险能赔手术费吗*
- Any request mentioning **"insurance quote", "compare quotes", "coverage limit", "liability limit", "deductible", "HMO vs PPO", "exclusion", "umbrella", "policy", "renewal", "保险", "报价", "保额", "免赔额", "免责"**

**Do NOT use** for: lowering an *existing* bill (use `bill-negotiator`), reviewing a claim *after* the fact (this skill is pre-purchase), tax questions (use `tax-prep-assistant`), or health/medical advice (this skill is about plan mechanics, not medicine).

---

## Core Workflow

### Step 1: Intake — what are we actually deciding?

Never start by comparing quotes. Start by establishing **what could go wrong**, because that determines which limits matter. Ask (or infer from context):

**For auto:**
1. What state do you drive in? *(liability floors and fault rules vary wildly)*
2. How many drivers, and how long has each had a license?
3. Vehicle value(s), year, and use (commute / business / rideshare)?
4. Annual mileage?
5. Anyone in the household who drives but isn't on the policy? *(unlisted drivers are a top claim-denial cause)*
6. Any at-fault claims in the last 5 years?
7. Do you carry passengers professionally, or tow a trailer, or live in a high-liability state (CA/NY/FL/MI)?

**For home:**
1. Replacement cost of the structure (not market value — use square footage × local rebuild cost)?
2. Year built, construction type (frame vs. brick), roof age, electrical/plumbing age?
3. Distance to the fire hydrant and the fire station?
4. Do you have a mortgage? *(Lender requires specific minimums.)*
5. Any flood zone / earthquake risk?
6. Home business, renters, jewelry, instruments, or other scheduled items?

**For health:**
1. Which doctors and hospitals do you actually use? *(Network adequacy beats every number on the sheet.)*
2. How many prescriptions, and are they generic or brand? Brand costs 4–5×.
3. How many specialist visits per year, and do you need referrals?
4. Any planned procedure or chronic condition this year?
5. Current deductible and out-of-pocket max, and how close are you to hitting them?
6. Is your employer HSA-eligible? (HDHP + HSA can win on paper, but the cash-flow timing is brutal.)

**For life / disability / pet:**
1. Who depends on your income, and for how long?
2. Existing coverage (through employer, other policies)?
3. For pet: age, breed, existing conditions, and what a single major surgery would cost?

**For all products:**
- What is your current premium and current carrier? *(the baseline you're trying to beat)*
- What is your renewal date? *(the deadline that makes this urgent)*
- What does your current policy cover that you'd hate to lose?

Record the answers in a local policy file so the next renewal starts from facts, not from scratch:

```json
// ~/.hermes/data/insurance/context.json
{
  "updated": "2026-10-25",
  "product": "auto",
  "state": "CA",
  "current": {"carrier": "GEICO", "annual_premium": 1180, "limits": {"liability_per_person": 25000}},
  "renewal_date": "2026-11-30",
  "drivers": 1,
  "vehicles": [{"year": 2021, "value": 22000, "use": "commute"}],
  "annual_miles": 12000,
  "notes": "last renewal was a 20% increase with no claim"
}
```

---

### Step 2: Decode every quote into structured JSON

Real quotes arrive as PDFs, emails, or phone photos. `extract.py` parses the text so you never have to eyeball a coverage table.

```bash
# From a digital PDF
pdftotext -layout quote.pdf quote.txt
python3 scripts/extract.py quote.txt --product auto --id q-geico --carrier GEICO --out quotes.json

# From a screenshot / scan — OCR first
ocrmypdf --deskew quote.pdf quote_ocr.pdf && pdftotext -layout quote_ocr.pdf quote.txt
python3 scripts/extract.py quote.txt --product auto --id q-geico --carrier GEICO --out quotes.json

# Multiple quotes into one file
python3 scripts/extract.py q1.txt --product auto --id q1 --carrier GEICO   --out quotes.json
python3 scripts/extract.py q2.txt --product auto --id q2 --carrier Progressive --out quotes.json --append

# Multi-plan health comparison sheet: isolate one plan per call
python3 scripts/extract.py plans.txt --product health --section "PPO Plan" --id ppo --out health.json
python3 scripts/extract.py plans.txt --product health --section "HMO Plan" --id hmo --out health.json --append

# What can this script recognise?
python3 scripts/extract.py --patterns
```

**What the extractor handles:**
- Dotted leaders (`Bodily Injury Liability (per person) ....... $ 100,000`)
- Colon format (`Out-of-Pocket Maximum: $6,500`)
- Parenthetical qualifiers inside the label (`(per accident)`, `(per person)`)
- Slash-compound labels (`Uninsured Motorist / UM-UIM`)
- Scale suffixes (`$1M`, `250k`)
- Premium bases: annual, 6-month (×2), monthly (×12), `$X/mo`
- Plan-scoped premiums in multi-plan sheets (`Annual premium for PPO Silver: $4,320`)
- Percentages as shares (`Coinsurance: 20%` → `0.20`)
- Features with negation (`Rental Reimbursement ... Not included` → `false`)
- Red flags: state-minimum liability, no UM/UIM, ACV-only home coverage, theft-from-unattended-vehicle exclusions, pre-existing-condition exclusions

**Always read the extracted JSON before trusting it.** The extractor gets you 90% of the way; the last 10% (a limit phrased unusually, a bundled endorsement, an exclusion buried in page 9) needs your eyes. `scripts/extract.py` prints a `[WARN] Nothing extracted` when the text is image-based — that means OCR failed, not that the quote is empty.

---

### Step 3: Compare on equal footing

```bash
python3 scripts/compare.py quotes.json
python3 scripts/compare.py quotes.json --scenario scenario.json   # add worst-case testing
python3 scripts/compare.py quotes.json --explain q-statefarm        # full field-by-field breakdown
python3 scripts/compare.py quotes.json --weights weights.json       # your priorities
python3 scripts/compare.py quotes.json --fields                     # what the scorer knows about
```

Output looks like this:

```
PLAN                             PREM/yr     Bodily Injury / Pe    Bodily Injury / Ac    Property Damage    UM / UIM    Collision
-------------------------------  ----------  --------------------  --------------------  ----------------  ----------  -----------
State Farm                      $1,615      $300,000              $500,000              $300,000          $300,000    $50,000
GEICO                           $1,420      $100,000 !            $300,000              $100,000 !        $100,000 !  $25,000
GEICO                           $1,180      $25,000 !             $50,000 !             $25,000 !         $25,000 !   $15,000 !

RANKING
  1. State Farm    score=0.700  coverage=1.000  price_score=0.000  premium=$1,615/yr  flags=0
  2. GEICO         score=0.435  coverage=0.429  price_score=0.448  premium=$1,420/yr  flags=0
  3. GEICO         score=0.420  coverage=0.171  price_score=1.000  premium=$1,180/yr  flags=5
```

`!` marks a limit below the recommended floor. `flags` counts disqualifying issues. **The ranking is not the recommendation** — a plan can score well and still be wrong for your life (a 1,000-mile-a-year commuter doesn't need a rental car, but a rideshare driver needs commercial coverage that *no* personal auto policy provides).

**Weighting.** The default weights treat liability and out-of-pocket exposure as dominant. Override them when your situation differs:

```json
// weights.json — California commuter, price matters more
{
  "liability_per_person": 3.0,
  "liability_per_accident": 3.0,
  "uninsured_motorist": 2.0,
  "property_damage": 1.0,
  "collision": 0.5,
  "comprehensive": 0.5
}
```

---

### Step 4: Exposure analysis — the part that changes decisions

A coverage score tells you which quote is *better*. Only the exposure analysis tells you whether any quote is *enough*.

```bash
# Built-in realistic worst cases
python3 scripts/gaps.py quotes.json --preset auto_liability
python3 scripts/gaps.py quotes.json --preset home_fire
python3 scripts/gaps.py quotes.json --preset health_cancer
python3 scripts/gaps.py quotes.json --preset pet_surgery

# Auto scenario derived from your actual numbers
python3 scripts/gaps.py quotes.json --auto --value 22000 --mileage 18000

# Your own scenario
python3 scripts/gaps.py quotes.json --scenario my_scenario.json

# CI mode: fail the build if a critical gap appears
python3 scripts/gaps.py quotes.json --preset auto_liability --check   # exit 1 on CRITICAL/HIGH
```

Output:

```
  COVER                                      NEED         HAVE        SHORT  SEV
  ------------------------------------------------------------------------------
  liability_per_accident                 $500,000     $300,000     $200,000  CRITICAL!!
  liability_per_person                   $250,000     $100,000     $150,000  CRITICAL!!
  medical_pay                             $15,000       $5,000      $10,000  CRITICAL!!

TOTAL EXPOSURE across the flagged items: $360,000
```

A `$360,000` exposure against a `$435/yr` premium difference is the whole argument, and it's the argument nobody makes for you. **State that number in the brief.**

---

### Step 5: The decision brief

Produce a single pasteable artifact. Structure:

```markdown
# Auto Insurance Decision — [State], renewal [date]

## Recommendation: [CARRIER] — [PLAN TIER] at $[X]/yr
*(vs. current $[Y]/yr with [CARRIER] — [+$Z/yr or -$Z/yr])*

## Why
1. **Exposure.** Under your worst realistic case (serious at-fault injury),
   this policy leaves you on the hook for **$0**. The cheapest quote leaves
   you exposed for **$360,000**.
2. **Price.** The premium difference is **$435/yr** — **$36/mo**. One ER
   visit covers 27 years of that difference.
3. **Nothing else regresses.** [List the features you keep.]

## What you're giving up
- [e.g. No new-car replacement] — costs about $[N] if you do it, and you
  don't plan to.

## Action items
- [ ] Call [CARRIER], quote quote-ID [X], ask for liability $300k/$500k
      with a $500 deductible (you're currently at $1,000).
- [ ] Ask about a multi-vehicle + paperless discount (you left money on
      the table last year).
- [ ] Bundle with renters for the 15% multi-policy discount.
- [ ] Set a reminder for [renewal - 30 days].

## If you decline
[Next-best option and why] — [CARRIER] at $[X]/yr, which still leaves
$[Y] exposed. Acceptable only if you [specific condition, e.g. "have
$400k in liquid assets"].
```

**The "if you decline" section is mandatory.** People need to know what the fallback costs in dollars, not just that there is a fallback.

---

### Step 6: Lock it in

- Save the decision and the chosen quote to `~/.hermes/data/insurance/policies.json`.
- Set a renewal reminder — `renewal-reminder` handles expiry tracking, or use `hermes cron` directly:

```bash
# Remind 30 days before each renewal
hermes cron add --name "auto-renewal" --schedule "0 9 30 11 *" \
  --prompt "Auto renewal with GEICO on 2026-11-30. Re-run the insurance-shopper workflow with the current policy from ~/.hermes/data/insurance/policies.json."
```

- At renewal, the context file from Step 1 makes the whole comparison a 10-minute job instead of a 2-hour one.

---

## Product Reference Cards

### Auto — the four limits that matter

| Limit | Why | Recommended |
|-------|-----|-------------|
| **Bodily injury / person** | Max payout per injured person | $100k min, **$300k target** |
| **Bodily injury / accident** | Max per accident, multiple people | $300k min, **$500k target** |
| **Property damage** | The other driver's car/property | $100k min, **$300k target** |
| **UM / UIM** | The other driver is uninsured/underinsured | $100k min, **$300k target** |

**State minimums are not a floor — they're a floor.** California requires 30/60/15. A $25,000 liability limit policy is a **$25,000 bet** that the other driver is insured and that nobody sues you.

**Also check:** is the vehicle *listed*? Is everyone who drives listed (unlisted drivers are the #1 denial)? Does the policy cover the business use you actually have (rideshare, delivery)? Is gap coverage present if you financed the car?

### Home — replacement cost vs. market value

The single largest home insurance mistake. If your home is worth $480,000 today and would cost $620,000 to rebuild, and the policy says "actual cash value," you are **$140,000 uncovered** in a total loss — and the insurance company pays the market value, not what the rebuild costs.

- Dwelling Coverage (A) should equal **rebuild cost**, not price paid and not market value.
- Add **Extended Replacement Cost** (typically +25%).
- Confirm **Loss of Use** (C) covers 12+ months of living expenses, not 6.
- Personal Property (F) is **actual cash value** unless you buy Replacement Cost Contents.
- Liability (E) should be **$300k–$1M**, because that's the cost of someone being injured on your property.

### Health — the plan-shape decision

| Shape | Good for | Watch for |
|-------|----------|-----------|
| **HMO** | Healthy, predictable care, low premium, network is adequate | PCP referral required; out-of-network = full cost; specialist visit cap often 0 |
| **PPO** | Frequent specialists, out-of-network needs, no referrals | Higher premium; still has cost-sharing |
| **EPO** | PPO without out-of-network | Same as HMO on network strictness |
| **HDHP** | HSA-eligible + you're a cash-flow optimizer | You pay the full deductible up front. **Catastrophe risk.** |

**The comparison that matters is not the premium — it's the worst-case year.** Compare each plan's `out_of_pocket_max` against your realistic annual usage: `premiums + expected medical cost`. A $500/yr-more premium plan with a $1,600 lower out-of-pocket max is cheaper if you use even one specialist visit.

**Verify network adequacy yourself.** Call the plan and ask for the *exact* name and address of your primary care doctor, your endocrinologist, and your preferred hospital. Then call each and confirm they're in-network for that *specific plan* (not just the insurance company). Both calls. Every time.

### Life & disability — the coverage-amount math

- **Life:** rule of thumb is **10× annual income**, or **5× income + largest liability** (mortgage). Subtract existing coverage (term life through work, 401k death benefit, Social Security survivor benefits).
- **Disability:** the **benefit period** matters more than the monthly amount. "To age 65" vs. "2 years" is a 40-year difference in exposure. Many policies also require you to be unable to work *your own occupation*, not any job — read the definition.
- **Umbrella:** cheap ($150–$350/yr for $1M) and the answer to "my auto liability isn't enough." Only useful if your auto/home liability is **at or above** the umbrella's underlying limits ($100k/$300k auto, $300k home). It doesn't "stack" below them.

### Pet — the two numbers to check

1. **Annual maximum** — the ceiling across everything in a year. A $10k accident limit with a $5k annual max means your dog can have one $5,000 accident. Period.
2. **Reimbursement vs. benefit schedule** — reimbursement pays actual vet bills (up to the limit); a benefit schedule pays a fixed table amount regardless of the bill. Reimbursement is better unless the schedule is generous.

---

## Example Invocations

### Example 1 — Three auto quotes, one of them a trap

**User:** *"I got 3 car insurance quotes. GEICO is $1,180, Progressive is $1,420, and State Farm is $1,615. My current policy is $980 and it's up for renewal Nov 30. Which should I pick?"*

**Agent:**

```
[EXEC] pdftotext -layout geico.txt && python3 scripts/extract.py geico.txt --product auto --id q-geico --carrier GEICO --out quotes.json
[EXEC] python3 scripts/extract.py progressive.txt --product auto --id q-prog --carrier Progressive --out quotes.json --append
[EXEC] python3 scripts/extract.py statefarm.txt --product auto --id q-sf --carrier State Farm --out quotes.json --append
[EXEC] python3 scripts/compare.py quotes.json --explain q-sf
```

```
PLAN                             PREM/yr     BI/Person    BI/Accident  Property Damage  UM/UIM    Collision
-------------------------------  ----------  ----------  -----------  --------------  --------  ---------
State Farm                      $1,615      $300,000    $500,000    $300,000        $300,000  $50,000
GEICO                           $1,420      $100,000 !  $300,000    $100,000 !      $100,000! $25,000
GEICO (renewal)                 $1,180      $25,000 !   $50,000 !   $25,000 !       $25,000! $15,000 !

FLAGS — GEICO (renewal)
  [RED] Liability limit below state minimum requirement
  [AMBER] Bodily Injury / Person $25,000 is below the recommended floor $100,000
  [AMBER] UM / UIM $25,000 is below the recommended floor $100,000
```

```
[EXEC] python3 scripts/gaps.py quotes.json --preset auto_liability
```

```
  liability_per_accident                 $500,000     $50,000    $450,000  CRITICAL!!
  liability_per_person                   $250,000     $25,000    $225,000  CRITICAL!!
  property_damage                         $60,000     $25,000     $35,000  CRITICAL!!
  medical_pay                             $15,000      $5,000     $10,000  CRITICAL!!

  TOTAL EXPOSURE across the flagged items: $720,000
```

**Verdict: State Farm, $1,615/yr — with one instruction.**

The $1,180 quote is the cheapest and the worst possible decision. It carries $25,000 of liability — a quarter of the state minimum in some states — leaving you personally exposed for **$720,000** in a serious at-fault crash. The $435/yr saving is $36/month; one ER visit wipes it out, and one hospitalization takes the rest.

But you don't have to take the most expensive quote. The $1,420 GEICO quote already fixes most of it (liability $100k/$300k). Ask both GEICO and State Farm for **$300k/$500k liability** at a $500 deductible — GEICO quoted you $25k because your *current* policy is $25k, and carriers price to your existing limits. Raising them will cost maybe $120–180/yr, still well below State Farm.

Your current $980 policy is the thing to actually end. Its liability is $25,000. That's been true the whole time and nobody mentioned it.

**Action items:**
- [ ] Call State Farm, quote #SF-99213, ask for $300k/$500k liability, $500 deductible
- [ ] Call GEICO, quote #QM-88213, ask for the same limits
- [ ] Ask both about paperless + multi-vehicle discount
- [ ] Set reminder for Nov 1 (29 days before renewal)

---

### Example 2 — "Should I buy the cheaper HMO?"

**User:** *"My employer offers two plans. HMO Bronze is $249/mo, PPO Silver is $360/mo. I have a thyroid condition and see an endocrinologist every 3 months, plus generic levothyroxine. I also had an ER visit last year that cost me $1,400. Which one?"*

**Agent:**

```
[EXEC] python3 scripts/extract.py plans.txt --product health --section "HMO Plan" --id hmo --out health.json
[EXEC] python3 scripts/extract.py plans.txt --product health --section "PPO Plan" --id ppo --out health.json --append
[EXEC] python3 scripts/compare.py health.json
```

```
PLAN                PREM/yr   Deductible  Out-of-Pocket Max  Coinsurance  PCP  Specialist  Generic Rx  Brand Rx  Specialist Visits
Blue Ridge HMO      $2,988    $1,500      $6,500             40%          $25  $50        $15         $60       no
Blue Ridge PPO      $4,320    $750        $3,900             20%          $20  $40        $10         $45       yes
```

```
[EXEC] python3 scripts/gaps.py health.json --preset health_year
```

```
  COVER                                      NEED         HAVE        SHORT  SEV
  ------------------------------------------------------------------------------
  out_of_pocket_max                       $12,000      $6,500      $5,500  CRITICAL!!
  brand_rx                                $2,400         $60      $2,340  CRITICAL!!
  specialist_copay                          $600         $50        $550  CRITICAL!!
  emergency_room_copay                   $1,500        none        none  CRITICAL!!
  hospital_admit_copay                   $4,000        none        none  CRITICAL!!

  TOTAL EXPOSURE across the flagged items: $8,390
```

**Recommendation: PPO Silver — but not for the reason you think.**

Your premium difference is $111/mo = **$1,332/yr**. Here's what it buys against *your* actual usage, not a generic one:

- **Specialist visits.** The HMO says "not covered without referral." You're going to an endocrinologist 4×/yr. If your PCP stops referring you — and they can, for any reason — you're paying 100% out of pocket. On a $40 copay that's $160/yr. On a full endocrinology visit at $280 that's **$1,120/yr for zero care.**
- **Your ER visit.** You paid $1,400 last year against the HMO's $6,500 out-of-pocket max. The PPO's is $3,900. That $2,600 lower ceiling is the real value — it's the difference between a bad year being a bad year and a bad year being a catastrophe.
- **Prescriptions.** Levothyroxine is generic, so this barely matters for you ($10 vs $15). Don't let the table sell you on it.

**One thing to verify before you enroll:** call and ask whether your endocrinologist is in-network for the *PPO Silver* specifically, not just "in-network with Blue Ridge." Both parties, both calls. If they're not, the PPO premium difference buys you the right to see them out-of-network at a balance bill, which is exactly what you were trying to avoid.

**Also:** check your current year's deductible against what you've already paid. If you've already hit $750 of the PPO deductible this year, the PPO may already be cheaper than the HMO for the rest of 2026.

---

### Example 3 — The renters policy that doesn't cover the laptop

**User:** *"I'm a renter in a $1,600/mo apartment. My landlord requires renters insurance with $100k liability. I've never actually shopped it. What should I get?"*

**Agent:**

```
[EXEC] python3 scripts/gaps.py quotes.json --preset home_liability
```

```
  liability_per_person                 $500,000     $100,000    $400,000  CRITICAL!!
  liability_per_accident             $1,000,000     $100,000    $900,000  CRITICAL!!
```

**Your landlord's $100k requirement is a floor, not a target.**

Here's what's actually happening: your landlord requires $100k because *their* mortgage lender requires it. It has nothing to do with your exposure. If a guest falls down your stairs and sues, $100k is gone in a single week of medical bills — and the rest of the judgment is yours personally, not your landlord's.

**What to buy:** a renters policy with **$300k personal liability** (most carriers offer $500k or $1M for free — ask), **$25k–$50k personal property**, and **loss of use** so you have a place to live if the unit becomes unlivable.

**On the laptop.** Standard renters insurance covers personal property but usually at **actual cash value** — depreciated. A $2,400 laptop bought 18 months ago might pay $1,500. Two options:
1. Check your policy's personal property limit. If it's $25k or more, your laptop is covered (subject to ACV depreciation).
2. If you want new-for-old, you need **replacement cost coverage** (some carriers include it; some charge ~10% more), or a separate **electronics rider**.

**Also check:** you're a renter, so no subrogation against your landlord unless you were negligent — but do check whether the policy excludes damage caused by the landlord's failure to maintain the unit. Many do.

**A third option worth 60 seconds:** your renters policy and your auto policy from the *same carrier* usually bundle for 15–25% off both. If you're about to shop auto anyway, quote them together.

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Comparing quotes on premium only | The whole point of this skill. Always run `compare.py`; the cheapest quote is usually the least-insured one. |
| Believing the quote PDF you were given | Quote PDFs show *one* set of limits. The quote that reflects your *current* limits is often deliberately worse than the alternatives. Ask for the limits table, not the price. |
| Trusting `extract.py` blindly | It gets you ~90%. Always read the JSON and check the source PDF for anything phrased unusually — bundled endorsements, exclusions on page 9, effective dates, and whether the quoted limits are what you actually get at renewal. |
| Extractor returns nothing | The PDF is image-based. Run OCR (`ocrmypdf --deskew` → `pdftotext -layout`) first. The `[WARN] Nothing extracted` message means OCR/text extraction failed, not that the quote is empty. |
| Multi-plan health sheet gives wrong numbers | Use `--section "<plan name>"` per plan. Without it the parser takes the first match of every field, which mixes plans together. |
| Comparing health plans on premium | Compare `premium + expected annual cost` against the `out_of_pocket_max`. A higher premium with a lower max wins if you use care. |
| Assuming the highest score is the right plan | The score ranks *quotes*. It can't know you'll never file a claim. The exposure analysis (Step 4) is the real decision input. |
| Forgetting the renewal deadline | Do the shopping 30 days out, not on the renewal date. Do it on the renewal date and you have no negotiating room and no time to fix a lapse. |
| Not checking your current policy first | You may already be under-insured and not know it. Read your current declarations page before shopping — that's your baseline. |
| Ignoring unlisted drivers | The #1 cause of denied auto claims. Everyone who drives the car, ever, must be listed. |
| Assuming the state minimum is "fine" | State minimums (e.g. CA 30/60/15) are catastrophically low. $300k/$500k costs very little and protects everything. |
| Skipping the "if you decline" section | The reader needs to know the dollar cost of the fallback, or they'll default to the cheapest option by inertia. |
| Forgetting to ask about discounts | Paperless, multi-vehicle, multi-policy bundling, loyalty tenure, autopay, and alumni/military/employer-group discounts routinely take 15–30% off. Never accept the first price. |
| Bundling blindly | Bundling is usually good but not always — a bundle can *raise* your auto premium if the auto policy is already cheap. Ask for both prices separately first. |
| Forgetting the network check on health | In-network status is plan-specific. Call the doctor with the plan name, not just the insurance company. |
| Treating this as financial advice | It's a structured comparison of terms you're being offered. Coverage decisions, tax treatment of premiums, and HSA/FSA strategy need a licensed professional. |

## Verification Checklist

Before sending any recommendation, verify all of these:

- [ ] **Current baseline read.** I have the user's current policy's limits, not just its price.
- [ ] **Renewal date known** and the recommendation lands ≥30 days before it.
- [ ] **Every quote decoded** — `quotes.json` has one entry per quote, each with a non-null premium.
- [ ] **Premiums annualized** to a comparable basis (6-month × 2, monthly × 12). No mixed units in the table.
- [ ] **All limit fields present** for each quote. A `-` in the table means "not extracted," which is different from "not offered."
- [ ] **Red flags read and reported**, not silently filtered out.
- [ ] **Exposure analysis run** on the recommended plan, and the dollar exposure is stated in the brief.
- [ ] **Scenario is realistic** for the user's actual life (state, vehicle value, prescriptions, dependents) — not the generic default.
- [ ] **Discounts checked** with the carrier (paperless, bundle, multi-vehicle, tenure, autopay).
- [ ] **Network/provider verification** done where relevant (health: doctors and hospital, both called).
- [ ] **Vehicle/driver completeness** confirmed for auto — no unlisted drivers, business use disclosed.
- [ ] **Replacement cost vs. ACV** explicitly confirmed for home, renters (contents), and auto (total loss).
- [ ] **Effective date** on the quote matches the renewal date, not today's date.
- [ ] **"If you decline"** section includes the dollar exposure of the fallback.
- [ ] **No fabricated numbers.** Every figure in the brief traces to the extracted JSON or the source document. Where the quote was ambiguous, say so.
- [ ] **Scripts ran cleanly** — `compare.py` exited 0 and `gaps.py --check` reflects the final recommendation.

## Data Sources & Accuracy

**Where the numbers come from**

- **All limits, deductibles, and premiums** are taken from the user's own quote documents, parsed by `scripts/extract.py`. Nothing is estimated or recalled from memory.
- **Recommended floors** (e.g. $300k/$500k liability, $1M umbrella) are **industry-standard guidelines** drawn from published consumer guidance (III, NAIC, state Department of Insurance consumer materials). They are conventions, not legal requirements.
- **State minimum liability figures** vary by state and change; the skill flags "below state minimum" heuristically at the $50k threshold rather than asserting a specific state's number. If the exact state minimum matters, verify it against the state DOI directly.

**What the skill cannot know**

- **Discount availability** — carrier-specific and agent-dependent. Always ask.
- **Network adequacy** — must be verified by calling the provider.
- **Underwriting criteria** — a quote is an offer, but approval depends on the full application.
- **Your future behavior** — the exposure scenarios are worst-case modeling, not predictions.

**Accuracy limits of the scripts**

- `extract.py` is a pattern matcher, not a document-understanding model. It handles the common label formats and will miss unusual phrasings. **It always prints what it extracted so you can check it.**
- `compare.py`'s scoring is a weighted heuristic — the weights are documented and adjustable, and the ranking is a starting point for judgment, not a decision.
- `gaps.py`'s presets use plausible cost anchors for common scenarios. **They are illustrative, not actuarial.** Replace them with real numbers from your own history where you have them.

**Privacy**

Everything runs locally: `~/.hermes/data/insurance/`. The scripts make **no network calls**. Insurance quotes contain PII (name, address, driver license, sometimes SSN) — don't paste them into a hosted tool, and redact the declaration-page PII before sharing a quote file with anyone.

**Not licensed advice.** This skill compares terms and models exposure. It does not advise on coverage adequacy for litigation, does not interpret tax treatment of premiums, and does not replace a licensed insurance producer for complex commercial, professional-liability, or high-net-worth placements.

## Companion Skills

| Skill | Where it picks up |
|-------|-------------------|
| `bill-negotiator` | You already bought it — now lower the premium on what you have |
| `purchase-advisor` | The same total-cost-of-ownership logic, applied to hardware instead of policies |
| `decision-journal` | Record *why* you picked this plan; revisit when the claim history changes |
| `renewal-reminder` | Never get caught by a renewal date again |
| `net-worth-tracker` | Umbrella coverage should track your net worth, not a round number |
| `personal-expense-tracker` | Premiums belong in a category you can actually see |
| `contract-reviewer` | When the policy has a contract layer — employer group plans, leases requiring coverage |
