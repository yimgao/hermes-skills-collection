---
name: bill-negotiator
description: "Lower your recurring bills by chat — telecom (cable/phone/internet), insurance (auto/home/renters), medical bills, gym, streaming bundles, even rent. Industry-specific scripts, retention-department playbooks, anchoring tactics, escalation paths, itemized-bill audits, financial-hardship letters, charity-care applications, and a tracked win/loss ledger. Pairs with subscription-manager (kill what you can't negotiate) and lost-item-recovery-style incident-response voice for urgent bills (medical, surprise overage)."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, negotiation, bills, telecom, cable, insurance, medical-bills, gym, rent, consumer-rights, no-surprises-act, fair-billing, anchors, retention-dept, hardship-letter, charity-care, itemized-bill]
    related_skills: [subscription-manager, personal-expense-tracker, net-worth-tracker, lost-item-recovery, salary-negotiation-coach, contract-reviewer, decision-journal]
---

# 💬 Bill Negotiator — 日常账单谈判教练

> Most adults overpay on at least three recurring bills — cable, internet, car insurance, and medical bills routinely take 20–40% off for anyone who asks politely and knows what to say. This skill turns "I've been paying $189/mo for 3 years" into a scripted, tracked, and repeatable negotiation campaign: identify the highest-leverage bill, look up the current competitor rate, draft the chat or call script with anchors, run the escalation ladder (frontline → retention → supervisor → executive office / regulator), and log every win in a local ledger so you remember what worked next renewal cycle.
>
> 大多数成年人在至少三张常客账单上多付了钱——有线电视、车险、医疗账单，只要开口礼貌地问一问，往往能降 20–40%。这个 skill 把「我交了 3 年 $189/月」变成有脚本、有追踪、可复跑的谈判战役。

## Overview / 概述

Bill Negotiator is a **consumer-side bill-reduction coach**. The premise: most recurring bills are **soft prices** that the vendor will discount to keep you from canceling, but the script is awkward, the hold times are long, and most people give up before they reach a retention agent who has actual authority to discount. This skill does the prep work (lookup competitor rates, calculate your leverage, draft the script), walks you through the call in real time, and logs the outcome so next renewal cycle you already know which vendor caves and which you should switch.

It also covers **bills you didn't agree to** — surprise medical charges, wrong auto-renewal increases, post-mortem fees — with itemized-bill audits, No Surprises Act / Fair Billing rights citations, and financial-hardship templates.

All data is stored locally in `~/.hermes/data/bills/` — no login, no upload, no third-party negotiation service required.

| Capability | What It Does | How |
|------------|-------------|-----|
| **Bill inventory** | Catalog every recurring bill you want to negotiate; track current price, original price, competitor rate, leverage score | Chat-based intake + local JSON ledger |
| **Industry playbooks** | Telecom, insurance, medical, gym, streaming, rent — each with the right anchor, retention script, and escalation ladder | Per-industry reference cards (Step 2) |
| **Retention-dept routing** | Skip the frontline agent; "press 1 for billing, then 0 repeatedly, or say 'cancel my service'" to reach someone with discount authority | Universal routing cheat sheet |
| **Live call mode** | Walk you through the call in real time — what to say at each gate, how to respond to common stalls, when to ask for supervisor | Real-time guided prompts |
| **Email / chat fallback** | Not everyone wants to call; produce a paste-ready email/chat script for vendors that don't have a phone-first culture | Channel-adapted templates |
| **Itemized-bill audit** | Catch line items you shouldn't be charged for (duplicate fees, unbundled services, upcharges, "service call" charges you didn't request) | Audit checklist + dispute templates |
| **Medical-bill scrub** | Detect coding errors, duplicate procedure charges, in-network vs. out-of-network mistakes, and uninsured-discount eligibility | CPT-code reference + charity-care template |
| **Hardship & charity-care** | For medical bills you can't pay: hospital financial-assistance policy lookup, payment-plan negotiation, IRS Form 990 charity-care floor | Financial-hardship letter template |
| **No Surprises Act / FCC / state DOI** | Cite the statute when a vendor stalls: federal billing-dispute rights for surprise medical bills, telecom cramming, insurance unfair-claims practices | Statutory citations, regulator complaint URLs |
| **Win/loss ledger** | Every negotiation logged: bill, anchor used, outcome, final price, percentage saved, follow-up date | `~/.hermes/data/bills/ledger.json` |
| **Renewal-cycle cron** | Set a cron to revisit every "won" negotiation 11 months later — most retention discounts expire on the 12-month anniversary | `hermes cron` |

## When to Use

- *"I've been paying $189/mo for Comcast for 3 years — can I actually lower it?"*
- *"My car insurance went up 18% at renewal with no accident. How do I push back?"*
- *"I got a $4,200 ER bill — half of it looks like duplicate charges. How do I audit this?"*
- *"My gym won't let me cancel — they keep charging me. What's the actual law?"*
- *"Spectrum quoted me $79 for new customers but I'm paying $129. Help me match it."*
- *"Geico wants $2,400/yr but Progressive quoted me $1,600 for the same coverage — how do I make Geico match?"*
- *"I lost my job — I can't pay this medical bill. Is there a financial-assistance program?"*
- *"My landlord raised rent $300/month with 30 days notice. Can I negotiate?"*
- *"Can you write me an email I can paste into Verizon's chat support?"*
- *"I'm scared to call — can we do this over chat / email instead?"*
- *用中文：帮我写一段话跟运营商谈套餐降价 / 我想跟车险公司谈降低续保费用 / 这张医疗账单我看不懂*
- Any request mentioning **"lower my bill", "negotiate", "retention offer", "loyalty discount", "competitor rate", "bill audit", "itemized bill", "financial hardship", "charity care", "减价", "投诉", "账单不对", "降套餐"**

**Do NOT use** for: salary/offer negotiation (use `salary-negotiation-coach`), contract clause review (use `contract-reviewer`), tax-filing disputes (use `tax-prep-assistant`), or collecting money owed *to* you (different skill). For insurance policy review on what to *buy*, also a different angle — this skill is for getting the price down on bills you already have.

## Core Workflow

### Step 0: Inventory & prioritize

Before any call, build the hit-list. Ask the user three questions:

1. **Which bills** are on your mind? (Or: "give me a list of every recurring charge on your bank statement.")
2. **Have you tried negotiating before?** For most categories, first attempt saves the most; repeat attempts within 12 months usually yield less.
3. **Switching cost?** Some bills (cable, gym) you can cancel tomorrow; others (auto insurance mid-policy, rent mid-lease) you can't — call out which levers apply.

Log the inventory:

```json
// ~/.hermes/data/bills/inventory.json
{
  "created": "2026-09-12",
  "bills": [
    {
      "id": "bill-001",
      "vendor": "Comcast Xfinity",
      "category": "telecom_cable",
      "service": "Starter TV + Internet 300Mbps",
      "current_price": 189.00,
      "currency": "USD",
      "billing_cycle": "monthly",
      "last_increase": "2025-11-01",
      "competitor_rate": {"spectrum": 79.00, "verizon_fios": 89.99},
      "leverage_score": 9,
      "switch_easy": true,
      "status": "untouched",
      "next_action": null,
      "followup_on": null,
      "notes": "Customer since 2021, no complaints filed, auto-pay on"
    }
  ]
}
```

**Leverage score** (0–10) is computed as:

- +3 if you have a credible competitor quote (same or better service for less)
- +2 if you can credibly switch (no contract, equipment free to return)
- +2 if you're past any commitment period
- +2 if you've been a customer >2 years (retention treats you as "save-worthy")
- +1 if you've never asked before (untouched bills have the biggest discount headroom)

Sort the inventory by leverage score, negotiate top-down.

---

### Step 1: Prep — gather anchors and intel

Before you pick up the phone (or open chat), get the numbers right. The agent should walk the user through these 5 lookups:

**a) Competitor rate** — what would they pay elsewhere?

| Category | Where to look |
|----------|---------------|
| Cable / internet | ISP's own "new customer" landing page (often buried under "shop"); third-party comparison sites |
| Cell phone | Mint Mobile, Visible, US Mobile, T-Mobile's own prepaid plans |
| Auto / home insurance | The Zebra, Policygenius, Insurance.com; competitor online quote with same coverage limits |
| Gym | Local competitor monthly rates; many gyms offer "no enrollment fee" promos |
| Streaming bundles | Apple One, Disney+/Hulu/Max bundle, Amazon Prime add-ons |
| Rent | Zillow / Apartments.com comps in the same building or zip |

> ⚠️ **Anchor must be specific.** "Spectrum is cheaper" is weak. "Spectrum is $79/mo for 300Mbps + basic TV in my zip, with no contract" is an anchor.

**b) Your value to the vendor** — length of tenure, on-time payment history, bundled services, equipment owned. These are your retain-me cards; surface them to the retention agent, who is paid on *save rate*.

**c) Your BATNA** — what's plan B if they say no? Be specific: "I'll switch to Spectrum on the 15th — equipment returns to Comcast on the 14th." The clearer your walk-away, the harder the agent works.

**d) Statutory floor** — for some categories, the law caps what they can charge or mandates disclosure:

| Category | Right | Citation |
|----------|-------|----------|
| Medical bills | No surprise billing, good-faith estimate | No Surprises Act (42 USC 300gg-111) |
| Medical bills — uninsured | Hospital financial-assistance / charity care | IRS Schedule H (Form 990), Section 501(r) |
| Telecom | Itemized bill on request, cramming/slamming prohibited | FCC 47 CFR 64.2000 et seq. |
| Auto insurance | Unfair claims practices prohibited | State DOI regulations (varies) |
| Rent (covered buildings) | 30-day notice for >5 units in many jurisdictions | State/local rent stabilization |

**e) The script's two numbers** —

- **Target price** — your realistic goal (e.g. "$99/mo" for cable). Pick a number 25–40% below current.
- **Walk-away price** — the highest price you'll still cancel over. Anything above this, you switch.

The agent should help the user set both *before* the call.

---

### Step 2: The call — live mode

Most users will be on a phone call. The skill works in two modes:

**Mode A: User calls alone (recommended)** — agent produces a one-page script card:

```markdown
## Comcast retention — call: 1-800-XFINITY
### Routing
1. Press `1` (English), then `0` repeatedly until you reach a human
2. Say: "I'd like to discuss my account and possible cancellation"
3. When asked reason: "I'm comparing your rates to Spectrum, which quoted me $79 for similar service in my area"

### Script
- **You:** "Hi, I've been a customer for 5 years and I'd like to stay, but my bill has gone up to $189/month and Spectrum is offering me $79 for similar service. Can you match that or get me closer?"
- **Them:** "I can offer you a $20 loyalty discount for 12 months" (~$169)
- **You:** "I appreciate that, but my target is $99 to stay. Is there anything else you can do — promo pricing, plan downgrade, equipment fee removal?"
- **If they stall:** "I don't want to cancel, but at $189 I really can't justify the cost. Can I speak with a retention specialist?"
- **Retention:** "I can offer $99 for 12 months with a 2-year contract" (anchor works)
- **If still no:** "What's your supervisor's name? I'd like to log this call." (escalation trigger)

### Stalls you'll hear + counter
- "That's the best I can do" → "I understand. What's the cancellation process?"
- "I can only do 6 months" → "Twelve months, or I'll switch today"
- "There's a $20 ETF" → "I have no contract on file; can you check?" (always verify)

### Walk-away
If final offer > $130/month → cancel. Plan B: Spectrum at $79.
```

**Mode B: User wants agent to roleplay** — the agent plays the retention agent in a realistic practice round, then the user does the real call. Useful for first-timers.

**Email / chat fallback** — for vendors with weak phone support (some streaming services, SaaS):

```text
Subject: Loyalty pricing request — account [ID]

Hi,

I've been a [vendor] customer since [year] and I'm writing because my bill
has increased to $[current] per month for [service description]. I've
received a comparable offer from [competitor] at $[competitor_price] for
the same service.

I'd like to stay — can you match the competitor rate, apply a loyalty
discount, or downgrade my plan to a tier that fits my current budget?
I'm happy to lock in for 12 months in exchange for a reduced rate.

Please reply with the best available offer. If we can't reach an
agreement, I'll need to cancel on [date].

Thank you,
[Name]
```

---

### Step 3: Industry playbooks

Each category has quirks. Quick reference:

#### 3a. Cable / internet / phone

- **Lever:** High — competitor quotes are public, switching is feasible
- **Best lever:** New-customer promo at the same vendor's main competitor (e.g. Spectrum if you're on Comcast)
- **Typical save:** 25–50%
- **Retention trigger:** Mentioning "cancel", "competitor", or "lower my bill" puts you in the retention queue
- **Tactic that works:** "Can I get the new-customer promo rate? I've been loyal for X years"
- **What to refuse:** Equipment rental fees (often $14/mo — buy your modem for $70); premium channel add-ons you never asked for; "service protection plan" you didn't consent to
- **Negotiate every 12 months** — most discounts are 12-month then revert; set a cron for 11 months out

#### 3b. Cell phone (postpaid, the big 3)

- **Lever:** Medium — prepaid carriers (Mint, US Mobile, Visible) have set the floor; the big 3 have retention "win-back" departments
- **Best lever:** A concrete prepaid quote: "Mint Mobile is offering 20GB for $30/mo on my line"
- **Typical save:** $20–40/line/month; can also negotiate to remove device insurance, hotspot fees, premium data add-ons
- **Negotiation frequency:** Every 6 months — carriers run promos constantly; cancel threats work, but they may call your bluff
- **What to refuse:** Device "installment plans" you didn't ask for, third-party content subscriptions (Verizon's "playpass", AT&T's "ActiveArmor"), insurance you don't need

#### 3c. Auto / home / renters insurance

- **Lever:** High at renewal — underwriters re-score you every 6 months; if your credit or driving record improved, you deserve a lower rate
- **Best lever:** A competitor quote with **identical coverage limits** (deductible, liability, comprehensive, uninsured motorist). Match line-by-line — agents will move if the coverage truly apples-to-apples.
- **Typical save:** 10–30%
- **Statutory floor:** State Department of Insurance regulates unfair claims practices. If they refuse to re-quote at renewal, file a DOI complaint (URL per state).
- **What to ask for:** "Can you re-run my quote?" (often triggers a re-underwrite); "review my deductibles" (raising deductible from $500 to $1000 typically saves 8–15%); "remove coverage I don't need" (rental reimbursement, roadside — common add-ons)
- **Annual cadence:** Always shop 30 days before renewal, every year. Insurance is the highest-leverage bill to negotiate yearly.

#### 3d. Medical bills

- **Lever:** Highest in the entire skill. Hospitals routinely bill uninsured patients 2–4× what insurers pay, and itemized bills contain errors on 30–60% of charges (per multiple published studies). Charity care / financial assistance is mandatory for nonprofit hospitals under §501(r).

- **Always ask for an itemized bill.** Then audit it:
  - Duplicate procedure codes (same CPT twice)
  - "Pharmacy" charges for meds you didn't receive
  - "OR time" in 15-minute increments — disputed by anesthesia literature
  - Room-and-board on the date of discharge (often billed in error)
  - Out-of-network provider at an in-network facility (No Surprises Act covers this)

- **Always ask for the cash price.** Uninsured / self-pay patients often qualify for a 40–60% discount under the hospital's "uninsured discount" policy; insured patients can request the same if they'd hit their deductible anyway.

- **Charity care template:**

  ```text
  Subject: Financial Assistance Application — Account [ID]

  To the Patient Financial Services Team,

  I am writing to request consideration for your hospital's financial
  assistance program under IRS Section 501(r)(3), which requires
  nonprofit hospitals to maintain and publicize such a policy.

  My current financial situation: [brief, honest — job loss, reduced
  hours, medical hardship, high-cost chronic care, etc.]

  Household income: ~$[X]
  Household size: [N]
  Insurance status: [uninsured / underinsured / on HDHP]

  Total bill: $[X]
  Account #: [X]

  I am requesting:
  1. The full financial-assistance policy and application (you are
     required to provide it under §501(r)(4))
  2. A 100% write-off if my income is at or below [state Medicaid /
     Federal Poverty Level threshold]
  3. A reduced-rate payment plan if I qualify for partial assistance
  4. A hold on all collections activity while the application is pending

  Please reply within 30 days as required by §501(r)(5). My contact:
  [..]

  [Name, DOB, MRN]
  ```

- **If they refuse / no charity-care policy:** File a complaint with the state Attorney General. Nonprofit hospitals that fail to comply with §501(r) jeopardize their tax-exempt status — that's a real threat.

- **No Surprises Act citations for surprise out-of-network:**

  ```text
  Under the No Surprises Act (42 USC 300gg-111) and its implementing
  regulations (45 CFR 149), this charge is unlawful. [Provider] rendered
  services at an in-network facility; I am only liable for in-network
  cost-sharing. Please rebill at the in-network rate and remove the
  balance-billing charge.
  ```

#### 3e. Gym / studio membership

- **Lever:** Medium. Many states (CA, NY, IL, MA, NJ, others) require gyms to let you cancel at any time and prohibit auto-renewal without affirmative consent.
- **Best lever:** State "cooling-off" / "health club" statute. CA: CA Bus Code §17600 et seq. NY: NY Gen Bus Law §627-a.
- **Common stalls:**
  - "You have to come in person" → often illegal; check state law
  - "You have to give 30 days' notice" → fine if true, but you can usually still cancel and the notice period charges only that 30 days, not beyond
  - "There's a cancellation fee" → state law often caps or voids
- **Template cancellation letter (USPS certified mail — keep receipt):**

  ```text
  Re: Membership Cancellation — Member ID [X]

  To [Gym Name]:

  I am hereby cancelling my membership effective immediately, pursuant
  to [state statute name] and your membership agreement clause [X].

  Per your agreement and state law, you must:
  1. Acknowledge cancellation in writing within [X days]
  2. Cease all future billing
  3. Confirm any pro-rated refund within [X days]

  Please confirm receipt and cancellation in writing.

  If I receive any further charges, I will dispute them with my card
  issuer and file a complaint with the [State AG / consumer protection
  office].

  [Name, address, member ID, signed, dated]
  ```

- **Bank/CC chargeback:** if the gym keeps charging after cancellation, dispute with the issuer under "services not received / cancelled". Document the cancellation letter and any reply.

#### 3f. Streaming / SaaS bundles

- **Lever:** Low — most don't negotiate, but they have "pause" features, downgrade options, and bundle partners (Disney+/Hulu/Max, Apple One, Amazon Prime channels)
- **Best move:** Pause (Netflix) or downgrade (Disney+/Hulu with ads tier). If you only watch one show, rotate: subscribe for the season, cancel after.
- **Hidden charges:** Amazon Prime add-ons, App Store subscriptions, Spotify audiobook add-on. Run `subscription-manager` style audit quarterly.

#### 3g. Rent

- **Lever:** Lowest of the categories — leases are contracts. But there are moves:
  - At renewal: comps + landlord's vacancy rate are your anchors
  - Mid-lease: ask for a kitchen-renovation allowance, free parking, waived amenity fees, painting credits — non-price concessions are easier to grant
  - **Stay vs. switch cost:** if moving costs > savings, negotiate longer lease + smaller increase
- **What to refuse:** mid-lease rent increases outside lease terms (illegal in most states)

---

### Step 4: Audit a bill you already paid

Some bills arrive and you pay them. Stop and audit. Common overcharges:

| Item to check | Common error | What to do |
|---------------|--------------|------------|
| **Medical EOB mismatch** | Provider charged $X, insurance paid $Y, you owe the rest — but the "rest" doesn't match the EOB | Call billing, ask for the line-by-line reconciliation; cite the EOB |
| **Duplicate fees** | Same service billed twice (e.g. "OR time" + "OR supplies" both at list price) | Ask for both CPT codes; CMS has reference prices; demand removal |
| **Upcharges you didn't request** | Premium channels, "service plans", "convenience fees", equipment rental | Ask for the consent record; if absent, demand removal |
| **Tax on a non-tax item** | Tax charged on a service that should be tax-exempt (some states exempt groceries, prescriptions, professional services) | File a refund request with the biller |
| **Estimated usage bills** | Utility over-estimated, you paid ahead, they owe you | Ask for a true-up; most states require annual actual-read billing |
| **Late fees during a dispute** | Biller charged a late fee while you were disputing the underlying amount | Cite the state's "good faith dispute" rule; demand removal |

**Dispute template (post-charge):**

```text
Subject: Billing dispute — Account [X], invoice dated [..]

To Billing Department,

I'm writing to dispute the following charges on invoice [..]:

1. $[X] — [category: e.g. "duplicate OR supply charge"]
2. $[X] — [category: e.g. "unrequested service plan"]

My basis: [.. — e.g. "I did not consent to the service plan; please
provide the signed enrollment. If none exists, please remove and
refund." / "Both line items reference CPT code 99213, which cannot
be billed twice on the same date of service per CMS guidelines."]

Please respond within 30 days with either (a) the corrected invoice
and refund, or (b) supporting documentation showing the charge is
correct. If I receive no response, I will file a complaint with the
[State AG / FCC / DOI / CMS] and dispute the charge with my payment
issuer.

[Name, account, attached invoice]
```

---

### Step 5: Escalation ladder

When the frontline agent can't help (or stalls), escalate in order:

1. **Retention specialist** — usually reachable by saying "cancel" or asking to be transferred
2. **Supervisor** — "I'd like to speak with your supervisor" is a hard ask; cite the original agent's name
3. **Executive Customer Office (ECO) / CEO office** — every public company has one; usually responds within 5 business days; reference the "executive escalation" in your email/letter; cite your tenure
4. **Regulator complaint** — for the relevant agency (state DOI for insurance, FCC for telecom, state AG / HHS for hospitals)
5. **Public escalation** — a polite, factual tweet / Google review / BBB complaint often gets an ECO response within 24 hours. Be specific and accurate; do not exaggerate.

Log each escalation:

```json
// ~/.hermes/data/bills/ledger.json (append)
{
  "id": "neg-20260912-001",
  "bill_id": "bill-001",
  "vendor": "Comcast Xfinity",
  "category": "telecom_cable",
  "anchor_used": "Spectrum $79/mo, 300Mbps + basic TV",
  "opening_price": 189.00,
  "target": 99.00,
  "walk_away": 130.00,
  "outcome": "won",
  "final_price": 99.00,
  "savings_monthly": 90.00,
  "savings_annual": 1080.00,
  "agent_name": "Maria",
  "escalations": ["retention"],
  "duration_min": 22,
  "duration_until": "2026-12-12",
  "notes": "12-month promo, must call again Nov 2026"
}
```

---

### Step 6: Renewal-cycle cron

Most "wins" are 12-month promos that revert silently. Set the cron at the time of the win:

```bash
hermes cron add "renewal-cable" \
  --schedule "0 9 1 10 *" \
  --prompt "Comcast negotiation expires 2026-12-12. Re-check current competitor rates (Spectrum, Verizon Fios) and re-negotiate before the bill reverts to $189. Use the bill-negotiator skill with the prior ledger entry as context." \
  --skill bill-negotiator
```

Pair with `subscription-manager` for what you can't negotiate (just kill it) and `personal-expense-tracker` for what you do pay.

## Example Invocations

### Example 1 — Cable / internet (the classic)

> **User:** I've been paying Comcast $189/month for like 3 years. My buddy just signed up for Spectrum for $79. Can I actually get Comcast to lower mine or should I switch?
>
> **Hermes:** You should ask first — keeping Comcast is often better than switching if the price is right, because you avoid install fees and equipment hassle. Spectrum's $79 is your anchor.
>
> Quick prep before the call:
> 1. Find your bill — what's your *exact* plan name? (Usually on page 1, e.g. "Starter TV + Internet 300Mbps")
> 2. What's your current modem rental fee? (Look for "equipment rental" — usually $14/mo)
> 3. When's your last promo expire? (If you can't remember, you're probably on month 13+ of a reverted rate)
>
> Now here's your script — call **1-800-XFINITY**, press 1, then 0 repeatedly until a human picks up:
>
> **You:** "Hi, I've been a customer since 2021 and I'd like to stay, but my bill has gone up to $189 and Spectrum is offering me $79 for 300Mbps plus basic TV. Can you match that or get me closer?"
>
> Expect the first agent to offer $20–30 off — say thanks but your target is $99. If they stall, ask for retention. If retention stalls, ask for a supervisor. Most people land at $99–$110.
>
> **Walk-away:** above $130/month, switch to Spectrum.
>
> Want me to run a practice round with you first? Or do you want to call now and paste back what they offered?

### Example 2 — Medical bill audit

> **User:** I just got a $4,217 ER bill from St. Mary's after a 6-hour visit. Half of these charges look like duplicates or stuff I didn't get. How do I even read this?
>
> **Hermes:** You're right to be skeptical — published audits find 30–60% error rates on itemized medical bills. Here's how to read it:
>
> **Step 1: Get the itemized bill (not the summary).** Call St. Mary's billing at the number on the statement and ask for an "itemized statement with CPT codes". They'll mail it or upload to the patient portal.
>
> **Step 2: Three big red flags to look for:**
>
> | Flag | Why it's wrong | What to do |
> |------|----------------|------------|
> | **Duplicate CPT codes** | Same procedure billed twice on the same day | Demand removal + refund |
> | **"Pharmacy" charges for meds you didn't receive** | Often pulled from a default list | Cross-check with the discharge med list |
> | **"OR time" in 15-minute increments** | Anesthesia literature disputes per-minute billing | Ask for the anesthesia record; demand time-corrected bill |
> | **Discharge-day room-and-board** | You left at 11am — they shouldn't bill a full day | Request an itemized room ledger |
>
> **Step 3: Ask for the cash price.** Uninsured patients qualify for a 40–60% discount under the hospital's "uninsured discount" policy; insured patients on HDHPs can often request the same. The hospital won't volunteer this — you have to ask.
>
> **Step 4: Apply for charity care.** St. Mary's is nonprofit (most US hospitals are). Under IRS §501(r), they're *required* to have a financial-assistance policy and provide it on request. Your household size and income qualify you — I can draft the letter.
>
> **Step 5: No Surprises Act check.** If any charge is from an out-of-network provider at an in-network facility, that balance-billing is **illegal** under 42 USC 300gg-111. Cite the statute; they have to rebill at the in-network rate.
>
> Start by requesting the itemized bill and the charity-care policy in the same call. Want me to draft both letters?

### Example 3 — Insurance renewal

> **User:** My auto insurance just went up 22% at renewal — $2,400/yr from $1,960. I have one not-at-fault accident from 2 years ago. Is this normal?
>
> **Hermes:** 22% is high — it could be legit (your zip re-scored, the insurer took a regional hit) or it could be the "loyalty tax" (insurers count on you not shopping). Always shop at renewal; 30 days out is fine.
>
> Here's the move:
>
> **Step 1: Get 3 competing quotes with identical coverage.** Use The Zebra, Policygenius, or call local independent agents. Match line-by-line:
> - Liability limits (e.g. 100/300/100)
> - Collision + comprehensive deductible (e.g. $500)
> - Uninsured motorist (often forgotten — must match)
> - Rental + roadside (often auto-included; can drop)
>
> **Step 2: Call your current insurer (Geico / State Farm / Progressive — pick yours).** Say:
>
> > "Hi, my renewal came in at $2,400. Progressive quoted me $1,600 with identical 100/300/100 coverage and the same deductible. I'd prefer to stay — can you match that or review my account?"
>
> **Step 3: Three leverage moves:**
> - "Can you re-run my quote?" → often triggers a re-underwrite that catches your improved credit score
> - "Raise my deductible from $500 to $1,000" → typically saves 8–15%, and you're not at-fault
> - "Remove rental reimbursement and roadside" → if you have AAA or don't use them
>
> **Step 4: If they refuse, switch.** Insurance is the easiest bill to switch — no install, just a new policy effective on the cancellation date of the old one. Make sure there's no gap of even 1 day (lapse resets your good-driver discount).
>
> **Walk-away:** if no one can get you under $1,800/yr for equivalent coverage, raise deductible to $1,000 and stay where you are — the move from $1,960 → $1,800 is the win.
>
> Want me to draft the call script for your specific insurer, with the line items I'd ask them to re-quote?

## Common Pitfalls

| Problem | Why it happens | Solution |
|---------|----------------|----------|
| **"They said no" — user gives up at frontline** | Frontline agents have ~10% discount authority; retention has the rest | Always ask for retention after the first "no"; retention exists to keep you from canceling |
| **Anchoring too high** | User says "I want $50 off" and agent counters $10 | Anchor at competitor quote + 25–40% discount; don't start with a small number |
| **User accepts the first offer out of politeness** | Most people are conflict-averse | Set a target + walk-away before the call; remind yourself: agents negotiate all day, this is their job |
| **No documentation of the win** | User forgets the deal 11 months later when bill reverts | Log every negotiation in `ledger.json`; set renewal-cycle cron at win time |
| **Negotiating a contracted service** | Some bills have 12/24-month contracts with ETFs (cell phone, gym, cable) | Check contract status first; "I'm past my commitment" matters for the script |
| **Confusing "price drop" with "permanent"** | Retention offers are usually 12 months then reverts | Always ask: "Will my bill revert after 12 months? Set me a reminder." |
| **User paid the bill before disputing** | Chargeback window expires (60–120 days for most issuers) | Dispute in writing first; if no response in 30 days, dispute with the card issuer |
| **Charity-care application asks for SSN / ITIN** | Hospitals use it for income verification | Provide only what's required; if they ask for SSN of a spouse, ask why (often unnecessary) |
| **Medical bill goes to collections before charity-care is decided** | Hospitals sell debt to collectors while applications are pending | Cite §501(r)(5) — they must pause collections during application review; demand written hold |
| **Insurance "savings" don't match apples-to-apples** | User switched to a cheaper policy with lower liability limits | Always line-by-line; lower limits = lower premium but more risk |
| **Negotiating rent mid-lease** | Leases are contracts; mid-lease rent changes are usually unenforceable | Read the lease; non-price concessions (paint, parking, appliance) are easier |
| **User is being abused by an aggressive collector** | Some debt collectors cross legal lines | FDCPA — collectors can't call before 8am, after 9pm, at work, or after you send a written cease. Send the cease letter first. |

## Verification Checklist

- [ ] Inventory built: every recurring bill on the user's radar is in `inventory.json` with current price, leverage score, status
- [ ] Per-bill prep done: competitor rate, BATNA, target price, walk-away price
- [ ] Industry playbook reviewed with user (cable, insurance, medical, etc.) — agent surfaces the specific anchor and statutory citation
- [ ] Script printed/loaded before the call (not improvised at 8pm on hold)
- [ ] Cancellation / retention routing known (button mash or "cancel" trigger)
- [ ] Negotiation logged with: anchor, opening price, target, walk-away, final, savings $, duration
- [ ] For medical bills: itemized bill requested with CPT codes; charity-care application filed for nonprofit hospitals; No Surprises Act cited for balance-billing
- [ ] For insurance: 3 competing quotes obtained with identical coverage; renegotiation or switch executed
- [ ] For telecom: equipment rental, premium add-ons, third-party content subs all removed
- [ ] Win/loss ledger updated; renewal-cycle cron scheduled at the time of the win (11 months out)
- [ ] All data local at `~/.hermes/data/bills/` — no third-party negotiation service used
- [ ] For disputed bills: written dispute sent within 60 days; chargeback window tracked
- [ ] For collectors: FDCPA cease-and-desist sent in writing before any further contact

## Data Sources & Accuracy

- **Competitor rates** — current public promotional rates from the same vendors' "new customer" landing pages and from third-party comparison aggregators (The Zebra, Insurance.com, WhistleOut). These change constantly — the anchor must be re-verified within 30 days of the negotiation, not the day of the negotiation.
- **Statutory citations** — No Surprises Act (42 USC 300gg-111; 45 CFR 149), IRS §501(r) and Schedule H (Form 990), FCC 47 CFR 64.2000 et seq. (telecom billing protections), FDCPA (15 USC 1692 et seq. — debt collection), state-specific cooling-off / health-club statutes (CA Bus Code §17600 et seq., NY Gen Bus Law §627-a, MA Gen Laws ch. 93 §80 et seq., etc.). Citations are a starting point — this is **not legal advice**; for active litigation or harassment by collectors, consult a consumer-rights attorney.
- **Hospital financial-assistance policy** — every nonprofit hospital is required to maintain one under §501(r)(4); the policy must be public. If you can't find it on the hospital's website, request it in writing — they have 30 days to provide.
- **Leverage scores and typical-savings ranges** — synthesized from published consumer-negotiation guides (Clark Howard, Ramit Sethi's "I Will Teach You to Be Rich" negotiation chapter, Consumer Reports insurance-shopping surveys). They're heuristics, not guarantees; your bill may differ.
- **Retention-department routing** — vendor-specific routing changes frequently; verify with the vendor's own "billing" or "cancel service" IVR tree before relying on the cheat-sheet.
- **All bill data and negotiation history** — user-supplied, stored locally in `~/.hermes/data/bills/`. Nothing uploaded. This skill does not connect to any vendor system or third-party negotiation service.
- **FDCPA, ACA, and No Surprises Act applications** depend on jurisdiction; verify the citation is current in your state before relying on it as a letter-of-the-law threat.