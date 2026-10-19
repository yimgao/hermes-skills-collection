---
name: equity-comp-tracker
description: "Track employer-granted equity (RSU / ESPP / ISO / NQSO / RSUs) — vesting schedules, exercise windows, post-termination deadlines (90 days for ISO), tax elections (83(b), QS vs NQ, AMT, ESPP qualifying disposition rules), net liquidation value at exercise/sale, concentration risk vs net worth. All local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, equity, rsu, espp, iso, nqso, stock-options, vesting, 83b, amt, qualifying-disposition, exercise-window, startup-compensation, personal-finance, tax-prep]
    related_skills: [investment-portfolio-tracker, net-worth-tracker, tax-prep-assistant, salary-negotiation-coach, personal-expense-tracker, reminder]
---

# Equity Compensation Tracker（雇主股权补偿追踪器）

> Stop losing money on RSU vests you forgot to sell, ISO exercises that blow up your AMT, and ESPP disqualifying dispositions that cost you 37% in ordinary income tax. Log every grant, vest, exercise, and sell in chat — Hermes keeps the calendar, the tax math, and the net-liquidation-at-every-exit value so you never miss a cliff, an 83(b) window, or a 90-day post-termination exercise deadline.

## Why this skill, not `investment-portfolio-tracker`

| Concern | `investment-portfolio-tracker` | `equity-comp-tracker` (this) |
|---|---|---|
| Lot origin | You bought on the open market | Employer granted; many vesting/lockup rules |
| Tax | One model — capital gains | Multiple models: ordinary income (RSU vest), AMT preference (ISO exercise), §83(b), ESPP qualifying vs disqualifying disposition |
| Critical deadlines | None | 90-day post-termination ISO exercise, 30-day §83(b) window, ESPP offering-period boundaries, 1-year-from-exercise QS holding rule |
| Value of a "share" | Mark-to-market | Mark-to-market **minus** future tax bill at every event |
| Liquidity | Sell any time | Most startup equity is illiquid; consider strike price + 409A + tender offers |

This skill covers everything employer-granted. Once you sell and the cash is in your brokerage, `investment-portfolio-tracker` takes over.

---

## 📋 Capability Overview

| Capability | Description |
|---|---|
| 📥 Log grants | RSU / ISO / NQSO / ESPP / RSU-with-84(b) — grant date, type, share count, strike, vesting schedule |
| ⏰ Vesting calendar | Monthly/quarterly/annual/ Cliff resync — never miss a vest or a cliff |
| 💵 Income events | RSU vest = ordinary income at FMV. ESPP purchase = per-paycheck contribution log |
| 🏋️ Exercise tracker | ISO exercise → AMT preference item; NQSO exercise → ordinary wage spread |
| 🪖 Tax elections | §83(b) within 30 days for early-exercise ISO/NSO; ESPP qualifying disposition eligibility |
| 💸 Sell events | Cost basis ladder; QS vs NQ treatment; short/long-term holding period check |
| 🧮 Net liquidation value | FMV minus model tax bill (fed+state+FICA+AMT+NIIT) at every hypothetical sale |
| ⚠️ Deadlines radar | 90-day post-termination ISO, 30-day §83(b), ESPP end-of-offering, exercise-window expiry |
| 🎯 Concentration risk | Unvested + vested shares as % of net worth; sale plan to de-risk |
| 🧾 Tax-prep export | Schedule B/D/AMT inputs, ISO exercise summary, §83(b) election reminders |
| 📈 Tender offers / liquidity | Model tender offer, secondary sale, lockup expiry |
| 💾 Local storage | `~/.hermes/data/equity-comp.json` — never hits a server |

---

## When to Use

- *"I just got a 20,000-share RSU grant vesting over 4 years with a 1-year cliff"*
- *"Vested 500 RSU at Acme today — FMV was $84.20"*
- *"Sold 300 ISO shares — original strike $3, I exercised them 18 months ago at $14, sold today at $52"*
- *"What's my net liquidation value if I exercise all my ISOs and sell tomorrow?"*
- *"I just left BigCorp — what do I have to do in the next 90 days?"*
- *"My ESPP purchase was at $45 — FMV today is $72 — should I hold for the qualifying disposition?"*
- *"Calculate AMT if I exercise all 5,000 ISO at $3 when FMV is $28"*
- *"Am I too concentrated? Show unvested RSUs vs my net worth"*
- *"What would the tax bill be on my $120k RSU vest? (CA, single)"*
- *"I just got a tender offer at $55 — should I sell a portion?"*
- *"我刚拿到 4 年 6 万股的 RSU，帮我算一下每年的税"*
- *"我去年的 ISO 行权让我交了 2 万 AMT，现在怎么处理？"*
- *"公司给我 5% 的工资转换为 ESPP，我每期投 15% 进去，帮我算 discount"*

---

## Core Workflow

### Step 1: Initialize Your Comp Profile (once)

Ask the user for context that drives every tax calculation:

```yaml
federal_tax_bracket: "24% / 32% / 35% / 37%"
state: "CA / NY / WA / TX / ..."
filing_status: "single / married_joint / hoh"
niit_applicable: true             # net investment income tax
amt_already_owed_prior_years: 0
```

Store at `~/.hermes/data/equity-comp.json`:

```json
{
  "profile": {
    "federal_tax_bracket": 0.35,
    "state": "CA",
    "state_rate": 0.093,
    "filing_status": "single",
    "niit": true,
    "fica_wage_base_2026": 184500,
    "medicare_addl": 0.009
  },
  "employers": [],
  "grants": [],
  "events": []
}
```

### Step 2: Log Grants

User says *"Got 20,000 RSU at Acme, vesting 25% after 1y then 1/16 quarterly"*. The agent parses and writes a grant record:

```json
{
  "id": "grant-acme-rsu-001",
  "employer": "Acme Inc",
  "type": "RSU",
  "grant_date": "2026-04-15",
  "shares_total": 20000,
  "strike_price": 0,
  "vesting": {
    "cliff_months": 12,
    "cliff_pct": 0.25,
    "post_cliff_period_months": 36,
    "frequency": "quarterly"
  },
  "section_83b_election": false,
  "iso_max_yearly_check": false,
  "notes": "Granted as part of offer; tender offer rights per Section 7 of Stock Agreement"
}
```

**Grant types supported:**

| Type | Strike | Tax at grant | Tax at vest | Tax at exercise | Tax at sale |
|---|---|---|---|---|---|
| RSU | $0 | $0 | Ord. income on FMV | — | Cap. gain on (sale − FMV-at-vest) |
| ISO | $X | $0 | $0 | AMT preference on (FMV − strike) | QS: 100% LTCG; NQ: ord. income on spread |
| NQSO | $X | $0 (without §83(b)) | — | Ord. income on (FMV − strike) | Cap. gain on (sale − FMV-at-exercise) |
| ESPP | $X | — | — | Ord. income on (purchase − FMV-at-purchase) if disqualifying; $0 if qualifying until sale | QS: LTCG on sale − purchase; NQ: ord. income on (sale − FMV-at-purchase) then cap. gain on remainder |

Always show this tax-treatment table to the user once per session so they understand why the math looks the way it does.

### Step 3: Log Vesting Events

User says *"Vested 500 RSU today, FMV was $84.20"*. The agent appends an event and immediately logs the **taxable amount** for the year:

```json
{
  "id": "event-vest-20261001-001",
  "grant_id": "grant-acme-rsu-001",
  "date": "2026-10-01",
  "type": "vest",
  "shares": 500,
  "fmv_at_vest": 84.20,
  "taxable_ordinary_income": 42100.00,
  "withholding_due": 12630.00,   // 30% fed default supplemental rate if RSU sell-to-cover
  "notes": "Q3 vest; sold-to-cover 190 shares at $84.20 for $15,998"
}
```

### Step 4: Log ISO Exercises & AMT Modeling

ISO exercise → AMT preference item only (no regular-tax impact at exercise, *unless* you sell same year = disqualifying disposition).

```json
{
  "id": "event-exercise-20261115-001",
  "grant_id": "grant-acme-iso-001",
  "date": "2026-11-15",
  "type": "exercise_cashless",
  "shares": 5000,
  "strike_price": 3.00,
  "fmv_at_exercise": 28.00,
  "amt_preference_per_share": 25.00,
  "total_amt_preference": 125000.00,
  "amt_likely_owed": 17800.00,  // computed by Step 6
  "notes": "Cashless exercise: net 1,242 shares delivered at $28"
}
```

**AMT quick formula (2026, simplified):** Tentative AMT = 26% × first $239,100 of AMTI + 28% × remainder. Compare to regular tax — pay the higher.

### Step 5: Log Sell Events

```json
{
  "id": "event-sell-20270115-001",
  "grant_id": "grant-acme-iso-001",
  "date": "2027-01-15",
  "type": "sell",
  "shares": 1500,
  "sale_price": 52.00,
  "cost_basis_method": "specific_lot",
  "acquisition_date_used": "2026-11-15",
  "exercise_basis_per_share": 3.00,
  "fmv_at_exercise_per_share": 28.00,
  "treated_as": "qualifying_disposition",
  "short_or_long_term": "long_term",
  "holding_period_months": 14,
  "ordinary_income_recapture": 0,
  "long_term_capital_gain": 73500.00,
  "tax_owed_estimate": 13230.00,   // 18% LTCG
  "notes": "Held 14 months from exercise + 1 day → QS ISO. 100% LTCG on $78k − $4.5k strike − $0 FMV-at-exercise basis."
}
```

**Qualifying disposition (QS) rules** — required for favorable ISO tax treatment:
1. Sold ≥ **1 year AND 1 day** after the **exercise date** (not vest date)
2. Sold ≥ **2 years** after the **grant date**

Otherwise it's a **disqualifying disposition (NQ)** → full bargain element (FMV − strike at exercise) becomes ordinary income.

### Step 6: Net Liquidation Calculator

User asks *"What if I exercise all my ISOs tomorrow and sell everything at today's FMV?"*

Compute:

```
gross_proceeds   = total_shares × current_fmv
exercise_cost    = total_shares × strike
amt_preference   = total_shares × (current_fmv − strike)        // if ISO
amt_tentative    = approx_amti_25pct                       // see Step 4
regular_tax_amt  = reg_tax_before_amti + amt_tentative − prior_amti_credit
ordinary_income  = bargain_element if NQSO / NQ
ltcg             = (current_fmv − strike) × shares  // only for QS ISO or RSU sold after 1y
state_tax        = approx 9%
fica_medicare    = only on RS at vest / NQSO exercise / ESPP non-qualifying sale, capped at wage base
niit             = 3.8% on net investment income if AGI > $200k single / $250k MJ
net_to_bank      = gross_proceeds − exercise_cost − all_taxes − advisor_fees
```

Output a result table:

```
┌─ Net Liquidation at FMV $52 ─────────────────────────┐
│ Gross proceeds ............. $260,000.00  (5,000 sh) │
│ Exercise cost .............. $ 15,000.00  ($3 strike)│
│ AMT preference item ........ $245,000.00             │
│ Tentative AMT (28%) ....... ~$ 68,600.00            │
│ LT cap gain (QS eligible) .. $200,000.00  ($49 × 5k)│
│   LTCG tax (18%) .......... $ 36,000.00             │
│ NIIT ...................... $  7,600.00             │
│ State CA (9.3%) ........... $ 18,580.00             │
│ Total federal ............. $104,600.00             │
│ Total state ............... $ 18,580.00             │
│ Total tax ................. $123,180.00             │
│ Net to bank ................ $121,820.00             │
│ Effective tax % ........... 47.4%                  │
└──────────────────────────────────────────────────────┘
⚠️  Holding < 1 year + 1 day? → disqualifying disposition → ordinary income on bargain element → effective tax rate ~57%.
```

### Step 7: Deadlines Radar

On every "what should I worry about?" prompt, check:

- **ISO post-termination**: 90 days from last day of employment to exercise, or ISO status is lost → NQ tax treatment
- **§83(b) window**: 30 days from exercise for early-exercise ISO/NSO at start-ups
- **ESPP offering periods**: 6-month look-back + 15% discount + purchase=true vs disqualifying
- **Lockup expiry**: usually 180 days post-IPO for insiders
- **Tender-offer windows**: 10b5-1 plan dates, blackout windows

Output:

```
🚨 Upcoming deadlines
  • ISO at BigCorp — last day to exercise: 2027-01-14 (90-day post-term rule)
  • ESPP offering period closes 2026-12-31 — decide to buy/hold/sell today
  • §83(b) election for Founder share grant due 2026-11-08 (10 days left)
  • 10b5-1 plan window opens 2027-02-01
```

### Step 8: Concentration Risk & Net-Worth Hook

Whenever the user logs a new vest or exercises, ask: *"Update net-worth-tracker with these shares at FMV $X?"* — keep cross-skill coordination explicit.

```yaml
concentration_alert_thresholds:
  warning:  25%  # single-employer vested shares / net worth
  critical: 50%  # including unvested
```

---

## Example Invocations

### Invocation 1 — First-time setup after a job offer

> **User**: Just signed at Stripe — 4-year RSU package, 1-year cliff, then 1/16 quarterly. Total 60,000 shares. Currently 32, single, CA.
>
> **Agent** *(in chat)*:
>
> ```
> [INIT] Equity comp profile created for "Stripe, Inc."
> [ASK] Federal bracket? CA is 9.3% — confirm 35% federal? Estimated income stripe-side?
> [ASK] Are you covered by § 120 (founder / IRS-approved) for any of these RSUs? [default: no]
> [ASK] Do you want to enable 10b5-1 plan tracking when vest starts? [default: yes]
>
> [GRANT] stripe-rsu-2026-grant
>   • 60,000 RSU total
>   • Cliff: 12 months @ 25% (15,000 shares)
>   • Post-cliff: 36 months @ 1/16 = 1,250 / quarter (Q1 vest = month 15)
>   • First vest: ~2027-08-15
>   • Vested-to-date: 0
>   • Vest dashboard created at dashboard://equity-comp/stripe
> ```
>
> **User**: 35% federal, no §120, yes 10b5-1. Tell me what I should be doing right now.
>
> **Agent**:
>
> ```
> [PLAN] Before first vest (~2027-08-15):
>
>   1. Build a 12-month cash buffer (30% of expected annual vest, net-tax)
>      Estimated annual vest ~ FMV × $15,000 ÷ 2 (cliff year) | `FMV × $15,000` post-cliff
>      → Set calendar events to remind you of first vest prep
>
>   2. Open a 10b5-1 plan within 5 trading days of hire to lock in sale windows
>      → Generate sample 10b5-1 with: sell-to-cover at vest + 75 days → next 30% within 90-day window
>
>   3. File Form W-4 to drop supplemental withholding? (RSU vests withhold at 22% federal. If you expect 35% bracket, set add-on $X)
>      → Show W-4 calculator
>
>   4. Open a brokerage that supports your tender / RSU sell-to-cover. Confirm your grant agent (Carta / Fidelity / Schwab / Computershare / E*Trade) and add to profile.
>
> [OK] Created `~/.hermes/data/equity-comp.json` with 1 grant, profile 35%/CA/single, 10b5-1 alert enabled.
> ```

### Invocation 2 — Annual vest-hell dash

> **User**: Vested 15,000 RSU today, FMV was $248.40. Sold-to-cover 5,670, net 9,330 to me.
>
> **Agent**:
>
> ```
> [VEST] acme-rsu-2023-grant → 2026-10-15
>   • 15,000 shares × $248.40 = $3,726,000.00 ordinary income
>   • Sell-to-cover: 5,670 × $248.40 = $1,408,463 withheld (37.8% — Strangler Tax
>     pattern, supplemental withholding rate was 22%, employer topped up)
>   • Net delivered: 9,330 shares to brokerage, can I "drip" `investment-portfolio-tracker`?
>
> [ASK] Update investment-portfolio-tracker with 9,330 ACME @ $248.40 cost basis? [y/n]
> [ASK] Compute Q4 supplemental tax to avoid underpayment penalty?
> [WARN] ⚠️ Fed est. tax threshold — you're at AGI $1.4M; need to check Q1 est. tax in April
>         Pairs with `tax-prep-assistant`: [schedule estimated-tax] [add rsu-vest-income]
> ```
>
> **User**: Yes, drip; yes compute Q4 est tax; and show me concentration vs net worth.
>
> **Agent**:
>
> ```
> [OK] Drip → 9,330 ACME lots logged in investment-portfolio-tracker (cost basis $248.40/sh)
> [OK] Q4 est. tax add-on (single, CA): $382,400 needed to fund 4/15 — set reminder?
>
> [CONCENTRATION]
>   Vested employer shares @ FMV = $6,318,000
>   Net worth (from net-worth-tracker) = $8,140,000
>   → 78% concentration (critical — recommended <50%)
>
>   De-risk plan:
>   • Sell-to-cover only. Re-vest clause? — Next 4 vests will add another $X — adds 22% if held
>   • Open 10b5-1 plan selling 1,500/qtr for next 12 months → targets 35% concentration
>   • Pledge warning: brokerage won't lend against restricted-control equity — check margin rules
> ```

### Invocation 3 — Post-termination ISO race

> **User**: I just got laid off. Last day is 11/15. I have 4,200 unexercised ISO with strike $2.10 and FMV today $34.50. What do I do?
>
> **Agent**:
>
> ```
> [🚨 CRITICAL] 90-day exercise window for ISO: 2026-11-16 → 2027-02-13 (90 days)
>    After 2027-02-13, all unexercised ISOs expire
>
> [MODEL: exercise all 4,200 on day 1]
>   Cash needed (full exercise):   $   8,820.00  (4,200 × $2.10)
>   Cashless exercise net shares:  ~2,815 shares   (account for withholding)
>   AMT preference (4,200 × $32.40): $136,080.00   → Tentative AMT ~$32,000 (28%)
>   If you sell same year → NQ:  ordinary income on $136,080 → 35% + 9.3% CA + 1.45% FICA
>      Effective tax hit: ~$61,000 (44.7%)
>   If you hold 1y+1d from exercise + 2y from grant → QS: 100% LTCG on appreciation from
>      $2.10 onward; tax ~$18,000 on $108,000 gain at exercise (12% LTCG)
>
> [RECOMMEND]
>   1. Cashless exercise on day 1 (transaction cost ~$200)
>   2. Hold for QS — provided you have ≥$32k AMT cash to pay in April next year
>   3. If cash-constrained: partial exercise
>      • cashless 1,200 shares → ~$28,300 net — much smaller AMT
>      • leave the rest to expire (better than bankruptcy)
>
> [DECISION-JOURNAL] Should I record this exercise decision? [y/n] → call decision-journal
> [CALENDAR] Add 2027-02-13 to renewal-reminder calendar as "Last day ISO exercisable"
> ```

---

## Common Pitfalls

| Problem | Solution |
|---|---|
| AMT surprise in April after ISO exercise | Run `equity-comp-tracker` AMT preview **before** exercising; budget for the AMT hit; consider exercising in stages across two tax years |
| ISO became NQ because you sold within 1 year | Mark exercise + future sale dates in 10b5-1 / Outlook; flag any sale < 1y from exercise in the sell event |
| ESPP disqualifying disposition — discounted shares taxed at ordinary income | Check purchase date + 2-year rule from offering start; if close, do a "qualifying sale" analysis vs holding through to next qualifying purchase |
| Missed 90-day post-term exercise window | Set 3-calendar-alerts: 75 days, 30 days, 7 days; can extend via the employer if it's not hostile — call HR |
| Forgot to file §83(b) for early-exercise startup grant | Default reminder trigger when grant.type ∈ {ISO, NQSO, founder} AND strike > 0 AND there is early-exercise option |
| RSU vest does NOT trigger AMT | Yes it does — no, actually it doesn't: RSU vest is ordinary income, not an AMT preference item. **Don't double-tax RSUs as if they were ISOs.** Verify grant type in every calc |
| Concentration risk ignored until a lockup expires | Run concentration check quarterly; auto-run from a cron alongside `net-worth-tracker` |
| Wash-sale mistakenly applied to RSUs | Wash-sale rule (30-day) does NOT apply to RSU vests; it DOES apply to ESPP disqualposing sales — keep straight in `treated_as` field |
| Selling all ISOs at once triggers top tax bracket + AMT cliff | Stage sales across 2-3 tax years; consider QS holding period spread |
| Employer stock dividends reinvested ≠ RSU | DO NOT confuse DRIP program with employer equity program — they run on different tax rails |
| Currency & exchange (foreign employer / RSUs at intl company) | Add `country_issuer`, `currency`, `withholding_foreign_pct` fields; subtract foreign tax credit on US return — out of scope, flag for tax-pro |

---

## Verification Checklist

Before treating a calculation as authoritative, confirm:

- [ ] Grant type recorded (RSU / ISO / NQSO / ESPP) — drives everything
- [ ] Strike price captured (zero for RSU, never zero for ISO/NSO)
- [ ] Vesting schedule parsed correctly with cliff and post-cliff cadence
- [ ] All vests to date have matching event rows
- [ ] ISO hold: ≥1 year from **exercise**, ≥2 years from **grant** for QS
- [ ] ESPP hold: ≥2 years from **offering start** AND ≥1 year from **purchase** for QS
- [ ] 83(b) election recorded within 30 days of early-exercise if elected
- [ ] 90-day post-term countdown running if user is on rollover/leaving
- [ ] Federal + state + NIIT + AMT accounted for in net-liquidation
- [ ] FICA stopped at wage base for RSU/RSO vest W-2 income
- [ ] Concentration % vs net worth refreshed after every vest and exercise
- [ ] Cross-skill drip into `investment-portfolio-tracker` confirmed for any post-sell cash
- [ ] Q4 / quarterly estimated-tax reminder set whenever vest event adds > $50k ordinary income

---

## Data Sources & Accuracy

This skill does **not** fetch live prices or grant data. All numbers come from the user (statements, brokerage export, grant letter). When the user pastes a screenshot or a number from Carta / Fidelity / Schwab / E*Trade:

- Treat the number as authoritative for that event.
- Always show the user the **computed** fields (tax, AMT, net liquidation) so they can cross-check against their CPA.
- **Tax figures are models**, not advice. Banner at the top of every calculation:

```
⚠️  EDU-ONLY ESTIMATES. RSU/ISO/ESPP tax depends on state, AMT crossover,
    whether you intend to claim AMT credit in future years, and dozens of
    lesser-known provisions (e.g., ESPP §423 look-back, ISO $100k limit
    over the year of grant, §120 founder exclusion). Confirm with a CPA
    or EA before file. This skill assumes US federal + one state.
```

- ISO $100k limit check: aggregate ISOs that vest in any calendar year; current-year vesting × FMV at vest must ≤ $100,000 to stay qualified; excess vests as NQSO automatically. Flag when adding grants.
- ESPP look-back: most plans grant lowest of (1) offering-start price, (2) purchase-date price, with 15% discount. The two-stock-purchase tracking flag is `espp_plan_rules: { discount: 0.15, lookback: true }`.

---

## 🔄 Suggested Cross-Skill Flow

```
equity-comp-tracker
  ├─ vest event → remind to update `investment-portfolio-tracker` (cash from sell-to-cover)
  ├─ exercise/AMT → log into `tax-prep-assistant` (Schedule D, AMT worksheet)
  ├─ ISO deadline → push to `renewal-reminder` (90-day post-term trigger)
  ├─ concentration% → pull from `net-worth-tracker` (refresh quarterly via cron)
  ├─ vest event → suggest 10b5-1 plan refresh
  └─ net-liquidation at FMV → call `investment-portfolio-tracker` "what-if" scenario
```

---

## 📁 File Locations

- `~/.hermes/data/equity-comp.json` — primary state (profile + grants + events)
- `~/.hermes/data/equity-comp-backup.json` — last manual backup
- `~/.hermes/data/equity-comp-export-{YYYY}.csv` — tax-prep export per year

---

## 📌 Out of Scope / For a CPA

- Foreign (non-US) tax-treaty optimization on equity
- §409A valuation disputes
- ISO AMT credit carryforward beyond 5 years
- NQDC (non-qualified deferred comp)
- Stock Appreciation Rights (SARs)
- Founder-stock 5-year business-exclusion §120 (highly situational)
- Filing Form 3921, 3922, 3923 with your tax return — *this skill will remind you but not file them*
