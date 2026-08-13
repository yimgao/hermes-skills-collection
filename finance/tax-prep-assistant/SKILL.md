---
name: tax-prep-assistant
description: "Year-round US tax assistant — capture deductible expenses via chat, auto-categorize Schedule A/C items, surface missed write-offs, generate quarterly estimated-tax reminders, and produce a filing-ready Schedule preview + document checklist each April"
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, taxes, deductions, schedule-a, schedule-c, freelancer, self-employment, 1099, w-2, irs, tax-prep, personal-finance, bookkeeping]
    related_skills: [personal-expense-tracker, subscription-manager, net-worth-tracker, report-formatter]
---

# Tax Prep Assistant（报税助手）

> Stop dreading April. Log deductible expenses in plain English all year — Hermes keeps a tax-ready ledger, flags missed write-offs, and assembles your Schedule A / Schedule C preview + document checklist before you file.

| Capability | Description |
|-----------|-------------|
| 🖊️ Chat-based logging | *"Spent $84 at the dentist, that's deductible"* — parsed & tagged instantly |
| 🗂️ IRS Schedule mapping | Auto-bucket into Schedule A (itemized), C (self-employment), or capped categories |
| 🚨 Missed-write-off detector | Surfaces expenses you might not know are deductible (home office, mileage, subscriptions) |
| 📊 Quarter reminders | Apr/Jun/Sep/Jan estimated-tax due dates with safe-harbor calculator |
| 📑 Document checklist | Per-form W-2, 1099, 1098 (mortgage interest), K-1 receipts your CPA needs |
| 📈 Year-end report | January digest of every deductible bucket, totals, and net refund/owed estimate |
| 💾 Local storage | All data in `~/.hermes/data/tax-ledger.json` — no bank link, no privacy leak |

---

## When to Use

- *"Log $129 for a dental cleaning, medical expense"*
- *"Bought $420 of office supplies for my freelance work"*
- *"Drove 86 miles for a client meeting, business mileage"*
- *"When's my next quarterly estimated tax due?"*
- *"How much can I deduct in charitable donations this year?"*
- *"What write-offs am I missing?"*
- *"Generate my 2025 Schedule C preview"*
- *"What's my tax document checklist for filing?"*
- *"今年我能抵多少税？"*
- *"我开了个Freelance，需要自己交税吗？"*

---

## Core Workflow

### Step 1: Log a Deductible Expense

User says *"$84 dental cleaning, medical"* or *"买办公电脑$1,200，自雇支出"*.

The agent parses and stores:

```json
// Stored in ~/.hermes/data/tax-ledger.json
{
  "id": "tx-2026-08-12-001",
  "date": "2026-08-12",
  "amount": 84.00,
  "currency": "USD",
  "merchant": "Downtown Dental",
  "description": "Dental cleaning + x-rays",
  "category": "medical",          // see IRS bucket table
  "schedule": "A",                // A = itemized, C = self-employment, E = rental
  "deductible_pct": 100,          // 100% deductible; AGI-threshold items use lower %
  "agi_threshold_note": null,     // e.g. "medical > 7.5% AGI"
  "needs_receipt": true,
  "receipt_file": null,           // user can attach path later
  "tags": ["health", "preventive"],
  "logged_on": "2026-08-12"
}
```

**IRS category → Schedule mapping** (2025 tax year, US):

| User-stated category | IRS Schedule | Deductible % | Notes |
|---|---|---|---|
| `medical` / `dental` / `prescription` / `health-insurance-premium` | A | 100% (only amounts > 7.5% AGI) | Includes premiums under §106 if self-employed |
| `charitable-cash` | A | 100% | Up to 60% AGI |
| `charitable-goods` (Goodwill, etc.) | A | 100% (FMV) | Need receipt with itemization |
| `mortgage-interest` | A | 100% | Up to $750K loan (post-2017) |
| `state-local-taxes-paid` (SALT) | A | 100% | **Capped at $10,000** (SALT cap) |
| `home-office` (self-employed) | C | 100% | Simplified: $5/sqft up to 300 sqft ($1,500 max) |
| `business-supplies` (self-employed) | C | 100% | Office, software, postage |
| `business-meals` (self-employed) | C | 50% | Must have business purpose + attendees |
| `business-mileage` (self-employed) | C | 100% | 2025 IRS rate: $0.70/mile |
| `business-travel` (self-employed) | C | 100% | Lodging + transport, away from tax home |
| `equipment` (self-employed, >$2.5K) | C | 100% | May qualify for §179 / bonus depreciation |
| `professional-fees` (self-employed) | C | 100% | Legal, accounting, contractor fees |
| `education` (self-employed, qualifying) | C | 100% | Must maintain/improve required skills |
| `health-insurance-premium` (self-employed) | C / Sch 1 | 100% | Above-the-line deduction |
| `retirement-contrib` (SEP/SIMPLE/IRA) | Sch 1 | 100% | Above-the-line |
| `student-loan-interest` | Sch 1 | 100% | Up to $2,500/yr, phaseout at higher income |
| `rental-expense` (landlord) | E | 100% | Repairs, insurance, depreciation |
| `personal` | — | 0% | Captured but not deductible — for spending view |

**After logging, reply:**

```markdown
✅ Logged: **$84.00 dental cleaning** (medical, Schedule A)
📅 Date: 2026-08-12
🧾 Receipt needed: Yes — add a path or photo ref later

📊 2026 medical deductible so far: $487.00
⚠️  Only amounts above 7.5% of your AGI (~$9,750 if AGI $130k) are deductible at filing time — but log everything now so we don't miss it.
```

### Step 2: Quarterly Estimated-Tax Reminders

**Self-employed users must pay quarterly** if they expect to owe ≥ $1,000. IRS due dates (US, 2026 cycle):

| Quarter | Income period | Due date | Safe-harbor target |
|---|---|---|---|
| Q1 | Jan 1 – Mar 31 | **Apr 15, 2026** | 22.5% of prior-year tax (or 90% of current) |
| Q2 | Apr 1 – May 31 | **Jun 15, 2026** | 45% cumulative |
| Q3 | Jun 1 – Aug 31 | **Sep 15, 2026** | 67.5% cumulative |
| Q4 | Sep 1 – Dec 31 | **Jan 15, 2027** | 100% / 90% current |

**Proactive cron message** (daily 9 AM, fires once per quarter on the due date):

```markdown
🚨 Quarterly estimated tax due TODAY (Jun 15, 2026)

Based on your 2026 ledger:
- Self-employment income (YTD): $48,200.00
- Total deductible expenses (YTD): $7,840.00
- Net SE income: $40,360.00
- SE tax estimate (15.3% on 92.35%): $5,704.00
- Income tax estimate (22% bracket): $8,879.00
- Federal total estimate: $14,583.00
- Already paid (Q1): $3,200.00
- **Remaining Q2 payment: ~$4,193.00**

💡 Safe harbor: if Q2 cumulative ≥ 45% of prior-year tax ($5,625 if you owed $12,500 last year), no underpayment penalty.

Pay via IRS Direct Pay or EFTPS. Want me to track the payment?
```

User can also ask ad hoc: *"How much do I owe for Q3?"* or *"今年我得交多少税？"*

### Step 3: Missed-Write-Off Detector

User says *"What am I missing?"*. The agent runs a heuristic sweep of `~/.hermes/data/expenses.json` (from `personal-expense-tracker`) plus the tax ledger itself.

**Detector rules** (checks every ledger + expense entry):

| Pattern in expenses | Suggests write-off | Why |
|---|---|---|
| Coffee shop charges tagged `business-meeting` or with attendee note | `business-meals` 50% | Often forgotten |
| Gas/auto charges during work hours | `business-mileage` 70¢/mi | Usually missed vs. actual gas cost |
| Online subscriptions (Adobe, Notion, GitHub, Zoom) | `business-software` | If used for work >50% |
| Phone bill (any amount) | `business-phone` (% of business use) | Even small deductions add up |
| Books/courses tagged `skill`, `cert`, `conference` | `education` | Must improve current skills |
| Coworking / WeWork / desk rental | `home-office` or `office-rent` | Common freelancer deduction |
| Bank / Stripe / PayPal fees | `bank-fees` | Self-employed deduction |
| Domain / hosting / SaaS infra | `business-software` | Schedule C line 22 |
| Internet bill (any amount) | `business-internet` (% business use) | Often 25–50% deductible |
| Half of self-employed health insurance | `health-insurance-premium` (Sch 1) | Above-the-line, very common miss |

**Output:**

```markdown
# 🔎 Missed Write-off Sweep — 2026 YTD

Scanned 142 expense entries ($11,840 total). Found **8 likely-missed deductions** worth ~$1,820.

| Expense | Amount | Suggested category | Est. deduction |
|---|---|---|---|
| Adobe Creative Cloud ($54.99/mo × 6) | $329.94 | business-software | $329.94 (100%) |
| WeWork hot desk ($290/mo × 5) | $1,450.00 | office-rent | $1,450.00 (100%) |
| AAA membership (2× renewals) | $228.00 | business-dues (if pro member) | $114.00 (50%) |
| Coursera annual sub | $399.00 | education | $399.00 (qualifying?) |
| Uber to 3 client meetings | $87.50 | business-mileage-equivalent | $43.75 (alt: $186 actual mileage) |
| Cell phone bill (avg $85/mo × 8) | $680.00 | business-phone (50% biz use) | $340.00 |
| Bank wire fees (5 × $30) | $150.00 | bank-fees | $150.00 |
| Internet (Xfinity, $80/mo × 8) | $640.00 | business-internet (40% biz) | $256.00 |

**Confirm each one?** Reply *"Log them all"* to add, or pick specific ones.
```

### Step 4: Year-End Schedule Preview (January Drill-Down)

User says *"Generate my 2025 Schedule A / C preview"* or *"我今年报税需要哪些信息？"*.

**Step 4a — Schedule A itemized-deduction preview:**

```markdown
# 📋 2025 Schedule A — Itemized Deductions Preview

| Line | Category | Your total | IRS limit | Deductible |
|---|---|---|---|---|
| 1–4 | Medical & dental | $4,820.00 | > 7.5% AGI | **$0** (below threshold — AGI $112k needs > $8,400) |
| 5a | State & local income tax | $6,200.00 | SALT cap | $6,200.00 |
| 5b | Property tax | $3,800.00 | SALT cap | $3,800.00 (combined w/5a = $10,000 cap) |
| 5c | **SALT total** | $10,000.00 | $10,000 | **$10,000.00** ⚠️ capped |
| 6 | Mortgage interest | $7,400.00 | $750K loan | **$7,400.00** |
| 7 | Charitable (cash) | $1,200.00 | 60% AGI | **$1,200.00** |
| 8 | Charitable (goods, FMV) | $340.00 | 50% AGI | **$340.00** |
| 14 | **Total itemized** | | | **$18,940.00** |

💡 Standard deduction (2025 single) = **$15,000** → itemizing saves **$3,940** in deductions.
⚠️  Your medical is below the 7.5% AGI floor; consider bunching elective procedures next year.

Want a Schedule C preview too?
```

**Step 4b — Schedule C (self-employment) preview:**

```markdown
# 📋 2025 Schedule C — Sole Proprietor Preview

## Income
| Line | Source | Amount |
|---|---|---|
| 1 | Gross receipts (1099-NEC + direct) | $86,400.00 |
| 2 | Returns & allowances | $0.00 |
| 7 | **Gross income** | **$86,400.00** |

## Expenses
| Line | Category | Your total |
|---|---|---|
| 8 | Advertising | $240.00 |
| 17 | Legal & professional | $620.00 |
| 18 | Office expense (incl. supplies, software, postage) | $1,840.00 |
| 20 | Rent / coworking (home office alt) | $1,450.00 |
| 22 | Supplies (incl. software, equipment <$2.5K) | $1,210.00 |
| 24a | Travel | $980.00 |
| 24b | Meals (50%) | $487.00 |
| 25 | Utilities & internet (business %) | $256.00 |
| 26 | Wages paid | $0.00 |
| 27a | Other (bank fees, education, mileage) | $612.00 |
| 28 | **Total expenses** | **$7,695.00** |

## Profit
| Line | Item | Amount |
|---|---|---|
| 29 | **Net profit** (gross – expenses) | **$78,705.00** |
| 30–32 | Vehicle / depreciation adjustments | $0.00 |
| 31 | **Tentative profit → Schedule SE → Form 1040** | **$78,705.00** |

💡 Your SE tax will be ~$11,082 (15.3% on $72,711 net SE earnings).
   Half is deductible above-the-line on Schedule 1.
```

### Step 5: Filing Document Checklist (March Onward)

User says *"What's my tax document checklist?"* or *"我4月要交哪些表？"*.

```markdown
# ✅ 2025 Federal Tax Filing Checklist

## 📥 Income Documents (collect from issuers)
- [ ] **W-2** — every employer (due Jan 31)
- [ ] **1099-NEC** — every client that paid you ≥ $600 (due Jan 31)
- [ ] **1099-K** — from Stripe/PayPal/Etsy/etc. if total ≥ $5,000 (2025 threshold; dropping to $2,500 in 2026)
- [ ] **1099-INT** — bank interest > $10
- [ ] **1099-DIV** — brokerage dividends
- [ ] **1099-B** — broker sales (with cost basis)
- [ ] **1099-R** — retirement distributions
- [ ] **1098** — mortgage interest statement
- [ ] **1098-T** — tuition statement (for education credits)
- [ ] **K-1** — if you have partnership / S-corp / trust income

## 📂 From Your Tax-Ledger
- [x] Medical expenses (Schedule A line 1)
- [x] SALT (income + property tax, capped)
- [x] Mortgage interest (1098 should match your ledger)
- [x] Charitable donations (every receipt)
- [ ] Home office square footage + total home expenses (for % calc)
- [ ] Mileage log (start date, end date, odometer readings)

## 🧮 Forms to File
- [ ] **Form 1040** — main return
- [ ] **Schedule 1** — above-the-line deductions (student loan interest, SE health ins., SEP/SIMPLE contrib)
- [ ] **Schedule A** — itemized deductions (only if > $15,000 standard)
- [ ] **Schedule C** — self-employment income/expenses (if 1099-NEC income)
- [ ] **Schedule SE** — SE tax (if net SE earnings ≥ $400)
- [ ] **Form 8995 / 8995-A** — QBI deduction (§199A, 20% of QBI if eligible)

## 📆 Key Deadlines 2026
- **Jan 31** — W-2 / 1099 forms arrive
- **Apr 15** — file or extend (Form 4868) + Q1 estimated payment
- **Jun 15** — Q2 estimated payment
- **Sep 15** — Q3 estimated payment + extended-return deadline
- **Oct 15** — extended-return filing deadline
- **Jan 15, 2027** — Q4 estimated payment
```

### Step 6: Refund / Owed Estimate (April Drill-Down)

User says *"Will I owe or get a refund?"*.

```python
# Estimate (rough; user must verify with actual forms)
gross_income = w2_total + 1099_nec_total + interest + dividends + other
above_the_line = student_loan_int + se_health_premium + sep_contrib
agi = gross_income - above_the_line

# Standard or itemized (pick higher)
standard = standard_deduction[filing_status]            # e.g. $15,000 single 2025
itemized = schedule_a_total                              # from Step 4a
deduction = max(standard, itemized)

taxable_income = agi - deduction

# Federal income tax (using 2025 brackets, single)
brackets = [(11925, 0.10), (48475, 0.12), (103350, 0.22),
            (197300, 0.24), (250525, 0.32), (626350, 0.35), (float('inf'), 0.37)]
income_tax = bracket_tax(taxable_income, brackets)

# QBI deduction (§199A)
qbi = min(0.20 * qbi_base, 0.20 * (taxable_income - net_capital_gain))
taxable_after_qbi = taxable_income - qbi
income_tax_with_qbi = bracket_tax(taxable_after_qbi, brackets)
income_tax = min(income_tax, income_tax_with_qbi)

# SE tax (Schedule SE)
se_tax = 0.153 * 0.9235 * max(0, net_se_profit)        # half is Sch 1 deduction
total_federal_tax = income_tax + se_tax

# Refund owed
refund = total_withheld + estimated_payments - total_federal_tax
```

**Output:**

```markdown
# 💰 2025 Federal Tax Estimate (Single Filer)

| Item | Amount |
|---|---|
| Gross income (W-2 + 1099) | $138,400.00 |
| Above-the-line deductions | ($2,840.00) |
| **AGI** | **$135,560.00** |
| Deduction (itemized > standard) | ($18,940.00) |
| **Taxable income** | **$116,620.00** |
| Income tax (with QBI deduction) | $17,041.00 |
| SE tax (15.3% on $78,705) | $11,082.00 |
| **Total federal tax** | **$28,123.00** |

## Cash flow
| Source | Amount |
|---|---|
| Federal withheld (W-2) | $14,200.00 |
| Estimated payments (Q1–Q4) | $12,000.00 |
| **Total paid** | **$26,200.00** |
| **Estimate: OWED** | **$1,923.00** ⚠️ |

💡 If you can't pay in full, file anyway + pay what you can; IRS offers short-term (180 days) and installment plans.

State tax (not estimated here) typically adds 4–9%.
```

---

## Example Invocations

### Example 1: Quick deductible log + quarterly reminder

**User:** *"Log $129 for a dental cleaning today, that's medical."*

**Agent:**
```markdown
✅ Logged: **$129.00 dental cleaning** (medical, Schedule A)
📅 Date: 2026-08-12
🧾 Receipt needed: yes — drop a photo ref or path anytime with "attach receipt tx-2026-08-12-001"

📊 2026 medical deductible so far: $1,094.00
⚠️  Only amounts above 7.5% of your AGI (~$7,500 if AGI $100k) are deductible at filing. Log everything — we'll bucket the over-threshold amount in January.

📌 By the way, Q2 estimated tax is due **Jun 15** (10 days away). Want a payment reminder?
```

### Example 2: Self-employed year-end preview

**User:** *"Generate my 2025 Schedule C preview. I'm a freelance designer, made about $86K."*

**Agent:**
```markdown
# 📋 2025 Schedule C — Freelance Design Preview

Income (1099-NEC + direct): $86,400.00
Deductible expenses (from your ledger): $7,695.00
Net profit: **$78,705.00**

| Top expenses | Amount |
|---|---|
| Office / coworking | $1,450.00 |
| Software (Adobe, Figma, Notion) | $1,840.00 |
| Travel (client visits + conference) | $980.00 |
| Meals (50%) | $487.00 |
| Equipment (laptop, monitor) | $1,210.00 |
| Professional fees (accountant) | $620.00 |

⚠️  I noticed $1,820 in **potentially missed** write-offs (cell phone, internet %, Coursera, bank fees). Want me to show the sweep?

SE tax estimate: **$11,082.00**
Half deductible on Schedule 1: **$5,541.00** (reduces AGI, then income tax)
```

### Example 3: Filing-ready checklist

**User:** *"What's my tax document checklist for April 2026?"*

**Agent:**
```markdown
# ✅ 2025 Tax Filing Checklist

## Collect by Jan 31
- [ ] W-2 from your employer
- [ ] 1099-NEC from each client ≥ $600
- [ ] 1099-K from Stripe/PayPal if ≥ $5,000
- [ ] 1098 mortgage interest statement
- [ ] 1098-T tuition (if applicable)

## From your ledger (already done ✅)
- [x] Medical, dental, vision receipts
- [x] Charitable donations
- [x] State income + property tax (SALT)
- [x] All Schedule C expenses
- [x] Quarterly estimated payments tracker

## Forms to file
- [ ] Form 1040
- [ ] Schedule 1 (above-the-line: SE health ins., SEP contrib., student loan int.)
- [ ] Schedule C (self-employment)
- [ ] Schedule SE (SE tax)
- [ ] Schedule A (itemized, only if > $15,000 std)
- [ ] Form 8995 (QBI deduction)

📆 Key dates:
- Jan 31 — forms arrive
- Apr 15 — file + Q1 estimate (or extend via Form 4868)
- Jun 15 / Sep 15 — Q2/Q3 estimates
- Oct 15 — extended-return deadline
```

### Example 4: 中文场景 — 自由职业者季度税

**User:** *"我是自由职业设计师，今年大概挣了 60 万人民币，需要自己报税吗？"*

**Agent:**
```markdown
# 🇺🇸 美国自雇税务速览（自由职业）

如果你是 **美国税务居民**（绿卡 / 183天测试），自雇收入需要：

1. **联邦层面**
   - 报 **Schedule C**（自雇损益）
   - 缴 **Schedule SE** 自雇税（15.3%）
   - 季度预估税 **Q1/Q2/Q3/Q4**：4/15, 6/15, 9/15, 1/15

2. **州层面**
   - 取决于你所在的州（CA / NY / TX … 各异）

3. **人民币换算**
   - 你的 ¥600,000 收入 ≈ $83,000 USD（按 7.25 汇率）
   - 净利假设 70% ≈ $58,000
   - SE 税 ≈ $8,150（15.3% on $58k×0.9235）
   - 联邦所得税 ≈ $5,800（12% bracket + QBI 抵扣）

4. **可抵扣项**（用中文记账也行）
   - 办公用品、软件订阅、差旅
   - 居家办公 $5/平方英尺（≤300sqft）
   - 健康保险（自雇可抵）
   - SEP-IRA / Solo 401(k) 退休账户

要不要我帮你建一个 2026 年的税务台账？你以后每一笔支出跟我说一声就行。
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User mixes personal + business expenses | Always ask "personal or self-employment?" if ambiguous. Tag `personal` for non-deductible entries (still captured for spending view). |
| User reports a 1099 but no income breakdown | Ask: "How many 1099s? Total gross?" If unsure, save the 1099 amount as `income_pending_verification` for later reconciliation. |
| SALT (state + property) exceeds $10,000 | Always cap at $10K and explain why — this is the most common IRS rejection trigger. Suggest bunching property tax payments in alternating years if applicable. |
| Charitable donations logged without receipts | Always set `needs_receipt: true` and remind: "Audit threshold is $250 per donation — keep the acknowledgment letter from the charity." |
| Medical below 7.5% AGI | Capture it anyway — schedule reminders in January to consider elective procedures in a higher-spending year. |
| Business meal logged at full amount | Auto-cap at 50%. Remind: "Save the receipt + note attendees + business purpose — IRS requires this for meal deductions." |
| Home office claimed without square footage | Ask once for "office sqft + total home sqft" — store the ratio for future % calculations on utilities, insurance, etc. |
| User expects "Schedule C" for W-2 income | W-2 wages go on Form 1040 line 1a — **not** Schedule C. Schedule C is only for self-employment (1099-NEC / 1099-K / cash). |
| Quarterly payment already made but ledger doesn't track it | Add `quarterly_payments` table: `{date, quarter, amount, confirmation}`. Used in Step 6 refund/owed calc. |
| Multi-state filing (CA + NY, etc.) | Note state in entry. Each state has its own due dates — surface those too if relevant. |
| User wants to depreciate equipment > $2,500 | Recommend §179 election or bonus depreciation. For v1, capture as `equipment` and remind in January: "Anything > $2.5K should be depreciated, not expensed. Want me to draft a depreciation schedule?" |
| Mileage logged with $ amount, not miles | Auto-convert: ask for odometer start/end OR miles driven. Never let user claim gas purchases as mileage (different math). |
| Foreign currency (CNY, EUR) expenses | Store native amount + currency; convert at year-end using IRS yearly average rate (or daily rate for big items). |
| Crypto / NFT transactions in expenses | Flag as `capital_gain_pending` — Schedule D + Form 8949 territory. Don't try to compute basis in v1; remind user to import from CoinTracker / Koinly. |

---

## Verification Checklist

- [ ] Expense logged with date, amount, currency, merchant, description, category, schedule, deductible_pct, needs_receipt
- [ ] Data persisted to `~/.hermes/data/tax-ledger.json`
- [ ] Schedule A vs C classification is correct (itemized vs self-employment)
- [ ] SALT auto-capped at $10,000
- [ ] Meals auto-capped at 50%
- [ ] Medical reminder about 7.5% AGI threshold
- [ ] Quarterly reminder fires on correct IRS due date (Apr/Jun/Sep/Jan 15)
- [ ] Quarterly safe-harbor calculation uses 22.5/45/67.5/90% cumulative
- [ ] Missed-write-off detector checks all 11 known patterns
- [ ] Schedule A preview shows line-by-line totals vs IRS limits
- [ ] Schedule C preview shows gross → expenses → net profit
- [ ] Filing checklist includes W-2, 1099-NEC/K, 1098, K-1 + the right Schedules
- [ ] Refund/owed estimate uses correct 2025 brackets for filing status
- [ ] QBI deduction applied if eligible (20% of QBI)
- [ ] Multi-currency supported (each entry has its own currency)
- [ ] Chinese natural-language input works ("买办公电脑$1,200，自雇支出")
- [ ] Duplicate detection prevents double-logging same transaction
- [ ] Cron-friendly: quarterly reminders roll up, not multiple per-day messages

---

## Data Sources & Accuracy

- **All data stored locally** at `~/.hermes/data/tax-ledger.json` — no bank integration, no IRS API link, no third-party tax-software vendor. The user is the source of truth.
- **IRS figures** (standard deduction, SALT cap, mileage rate, brackets, QBI thresholds, quarterly due dates) are baked into the skill at version time. **Last updated for 2025 tax year.** Each January 1, review and bump:
  - Standard deduction amounts (revenue procedure)
  - SALT cap ($10,000 since 2018 — currently political)
  - Mileage rate (IRS Notice; 2025 = $0.70/mi)
  - QBI deduction thresholds (§199A inflation adjustment)
  - Tax brackets (Rev. Proc. 2024-40 for 2025)
- **State-specific logic is out of scope** for v1 — the skill flags "this is federal-only" in every output. Users in CA / NY / WA / TX should verify state separately. A future v2 may add a per-state profile.
- **This skill is not a substitute for a CPA.** Every output ends with a disclaimer: *"Confirm with a tax professional — rules change and edge cases abound."* The skill explicitly recommends a CPA for: multi-state income, K-1s, rental properties, AMT exposure, foreign income, audit responses.
- **Filing thresholds** are conservative defaults: the agent nudges users toward filing even when income is below the filing threshold if they've had withholding — they may get a refund.
- **Privacy posture**: the ledger contains sensitive financial data. The skill never transmits it anywhere — no cloud sync, no AI training, no bank API. Recommend user runs `chmod 600 ~/.hermes/data/tax-ledger.json`.
- **Pair with `personal-expense-tracker`** for raw transaction capture; this skill focuses on **tax classification** of those (and any other deductible) expenses. They are complementary — `personal-expense-tracker` answers "where did my money go?", this skill answers "what can I deduct?".
- **Pair with `net-worth-tracker`** for the full balance-sheet picture (assets, liabilities, debt payoff) which feeds into the refund/owed estimate.

> *This skill is informational only and does not constitute tax advice. Consult a CPA or enrolled agent for your filing. Rules cited are for the 2025 US tax year; verify against current IRS guidance each January.*