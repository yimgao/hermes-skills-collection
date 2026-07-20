---
name: net-worth-tracker
description: "Track assets, liabilities, and net worth over time — chat-based portfolio balance sheet with trend charts, debt payoff projections, and asset allocation breakdowns. All data local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, net-worth, assets, liabilities, balance-sheet, portfolio, personal-finance, wealth-tracking, debt-payoff, asset-allocation]
    related_skills: [personal-expense-tracker, subscription-manager, csv-explorer, report-formatter]
---

# Net Worth Tracker（净资产追踪器）

> Track every dollar you own and every dollar you owe — see your true net worth trend, debt-payoff trajectory, and asset allocation over time, all through plain chat.

| Capability | Description |
|-----------|-------------|
| 💼 Log assets | Bank accounts, brokerage, retirement (401k/IRA), real estate, crypto, vehicles, collectibles — by natural language |
| 💳 Log liabilities | Credit cards, student loans, mortgages, auto loans, personal debt, BNPL — keep balances current |
| 📈 Net worth trend | Daily/weekly/monthly snapshot, % change, all-time high, ATH delta |
| 🎯 Debt payoff | Avalanche vs snowball comparison, months-to-debt-free, total interest saved |
| 🥧 Asset allocation | Cash / equities / real estate / retirement / crypto / other — pie breakdown |
| ⚠️ Anomaly alerts | Sudden balance drops, missing monthly updates, debt growing fast |
| 📊 Reports | Monthly net-worth statement (Markdown + ASCII chart), year-over-year deltas |
| 💾 Local storage | All data at `~/.hermes/data/networth.json` — no cloud, no leak |

---

## When to Use

- *"Add $12,400 in my Chase checking account"*
- *"My Vanguard 401k is now $87,500"*
- *"I paid off $1,200 on my credit card this month"*
- *"What's my current net worth?"*
- *"Show me my net worth trend for the last 6 months"*
- *"How long until I'm debt-free if I pay $500/month extra?"*
- *"What's my asset allocation? Am I too heavy in stocks?"*
- *"Record a $4,000 bonus I just deposited"*
- *"My car is worth about $18,000 now (down from $22k)"*
- *"我今天信用卡还了$300"*
- *"我净资产多少了？"*
- *"把房产按$650k估值登记一下"*
- *"Compare avalanche vs snowball for my 3 credit cards"*
- *"Show me what % of my wealth is liquid vs illiquid"*

---

## Core Workflow

### Step 1: Log or Update an Asset or Liability

User says *"Add $12,400 in my Chase checking"* or *"我房产估值$650k，房贷还剩$420k"*. The agent parses:

For **assets**:

- **Name** — display name (e.g. `Chase Checking`, `Vanguard 401k`, `BTC wallet`)
- **Type** — auto-categorize into one of: `cash`, `investment`, `retirement`, `real_estate`, `crypto`, `vehicle`, `collectible`, `other`
- **Balance** — current numeric value
- **Currency** — auto-detect `$`/`¥`/`€`/`£`
- **Liquidity** — `liquid` (cash/brokerage) | `semi-liquid` (retirement w/ penalty) | `illiquid` (real estate, vehicles)
- **Institution** — optional (Chase, Vanguard, Coinbase, etc.)
- **Cost basis** — optional (for cap-gains tracking later)
- **Notes** — optional (account # last 4, plan type, etc.)

For **liabilities**:

- **Name** — display name (e.g. `Chase Sapphire CC`, `FedLoan Student`)
- **Type** — `credit_card`, `student_loan`, `mortgage`, `auto_loan`, `personal_loan`, `bnpl`, `other`
- **Balance owed**
- **APR** — interest rate (e.g. `24.99%`, `0% promo until 2027-03`)
- **Min payment** — minimum monthly
- **Promo/0% expiry** — optional, triggers alert
- **Notes** — optional

```json
// Stored in ~/.hermes/data/networth.json
{
  "version": 1,
  "currency_default": "USD",
  "accounts": [
    {
      "id": "acc-2026-07-19-001",
      "kind": "asset",
      "name": "Chase Checking",
      "type": "cash",
      "balance": 12400.00,
      "currency": "USD",
      "liquidity": "liquid",
      "institution": "Chase",
      "added_on": "2026-07-19",
      "last_updated": "2026-07-19",
      "history": [
        { "date": "2026-07-19", "balance": 12400.00 }
      ],
      "notes": "HYSA @ 4.5% APY"
    },
    {
      "id": "acc-2026-07-19-002",
      "kind": "liability",
      "name": "Chase Sapphire CC",
      "type": "credit_card",
      "balance": 1850.00,
      "apr": 0.2499,
      "min_payment": 45.00,
      "currency": "USD",
      "added_on": "2026-07-19",
      "last_updated": "2026-07-19",
      "history": [
        { "date": "2026-07-19", "balance": 1850.00 }
      ],
      "notes": "Card ending 4521"
    }
  ],
  "snapshots": []
}
```

**Auto-default type → liquidity mapping:**

| Asset type | Liquidity | Notes |
|------------|-----------|-------|
| `cash` | liquid | Checking, savings, money market |
| `investment` | liquid | Brokerage, taxable stock accounts |
| `crypto` | liquid | Wallets you control |
| `retirement` | semi-liquid | 401k, IRA (10% early withdrawal penalty) |
| `vehicle` | illiquid | Cars, motorcycles (depreciating) |
| `real_estate` | illiquid | Primary home, rental property |
| `collectible` | illiquid | Art, watches, jewelry |
| `other` | user-defined | Default semi-liquid |

### Step 2: Take a Snapshot & Compute Net Worth

Run on demand or via cron (`cron-pipeline-builder` compatible). Snapshots are point-in-time balances — the agent freezes current account values and appends to `snapshots[]`.

```bash
# Manual snapshot
python3 ~/.hermes/skills/finance/net-worth-tracker/scripts/snapshot.py

# Or via chat:
# "Take a snapshot for today"
# "Log monthly net worth for July"
```

**Snapshot schema:**

```json
{
  "date": "2026-07-19",
  "total_assets": 142350.00,
  "total_liabilities": 26840.00,
  "net_worth": 115510.00,
  "by_type": {
    "cash": 18400.00,
    "investment": 47200.00,
    "retirement": 58100.00,
    "crypto": 8650.00,
    "real_estate": 10000.00,
    "vehicle": 0.00,
    "other": 0.00
  },
  "by_liquidity": {
    "liquid": 74250.00,
    "semi_liquid": 58100.00,
    "illiquid": 10000.00
  }
}
```

**Computed metrics on each snapshot:**

- **Net worth** = total_assets − total_liabilities
- **Liquid net worth** = liquid_assets − total_liabilities (the wealth you can actually touch)
- **Debt-to-asset ratio** = total_liabilities / total_assets
- **Emergency runway** = liquid_assets / avg_monthly_expenses (auto-pulls from `personal-expense-tracker` if present)

### Step 3: Reports, Trends & Projections

User asks *"Show me my 6-month net worth trend"* or *"Compare avalanche vs snowball"*. The agent computes:

#### 3a. Trend Report

```text
NET WORTH TREND  ·  2026-02-01 → 2026-07-19
─────────────────────────────────────────────
Feb 2026    $  98,200  ▁▁▁
Mar 2026    $ 102,800  ▁▁▂     +$4,600  (+4.7%)
Apr 2026    $ 105,150  ▁▂▂     +$2,350  (+2.3%)
May 2026    $ 108,700  ▁▂▃     +$3,550  (+3.4%)
Jun 2026    $ 112,400  ▁▂▄     +$3,700  (+3.4%)
Jul 2026    $ 115,510  ▁▂▅     +$3,110  (+2.8%)  ← today

6-month change: +$17,310  (+17.6%)
ATH: $115,510 on 2026-07-19
Avg monthly growth: +$2,885
Annualized: +$34,620 (+35.3% YoY)
```

#### 3b. Asset Allocation

```text
ASSET ALLOCATION  ·  2026-07-19
─────────────────────────────────────────────
Investment     $ 47,200  ████████████░░░░░░░░░  33.2%
Retirement     $ 58,100  ██████████████░░░░░░░  40.8%
Cash           $ 18,400  █████░░░░░░░░░░░░░░░░  12.9%
Crypto         $  8,650  ██░░░░░░░░░░░░░░░░░░░   6.1%
Real Estate    $ 10,000  ███░░░░░░░░░░░░░░░░░░   7.0%
                                        TOTAL  $142,350

Liquidity split:
  Liquid         $ 74,250   52.2%
  Semi-liquid    $ 58,100   40.8%
  Illiquid       $ 10,000    7.0%

⚠️  Crypto 6.1% — within healthy range if <10%
✅  Cash 12.9% — solid emergency fund
```

#### 3c. Debt Payoff Projection

User asks *"If I throw $500/month extra at my cards, when am I debt-free?"*. The agent:

1. Sorts liabilities by APR (avalanche) or by balance (snowball)
2. Compounds monthly: `balance_new = balance × (1 + apr/12) + extra_payment − min_payment`
3. Outputs month-by-month until all balances hit 0

```text
DEBT PAYOFF  ·  Avalanche strategy (highest APR first)
Extra monthly payment: $500
─────────────────────────────────────────────
Chase Sapphire CC    $1,850 @ 24.99%   →  paid off mo  4  (saves $387)
AmEx Gold CC         $3,200 @ 21.99%   →  paid off mo  9  (saves $612)
Student Loan (Fed)  $14,800 @  6.50%   →  paid off mo 38

Total months to debt-free: 38
Total interest paid: $4,712
Total interest saved vs. min-only: $8,433

Compare snowball (lowest balance first):
  Chase Sapphire paid off mo 4  (same — both win here)
  AmEx Gold paid off mo 11  (2 months slower)
  Student Loan paid off mo 38  (same)
  Total interest: $4,847  (+$135 vs avalanche)

💡 Avalanche saves $135 over 38 months. Recommended.
```

#### 3d. ASCII Chart Generator

For trend visualization, the agent emits a sparkline-style bar chart:

```bash
# Reusable chart snippet (uses Python stdlib only — no matplotlib needed)
python3 -c "
bars = '▁▂▃▄▅▆▇█'
vals = [98200, 102800, 105150, 108700, 112400, 115510]
mx = max(vals)
print(''.join(bars[min(7, int(v/mx*8))] for v in vals))
"
# Output: ▁▁▂▂▃▄▅
```

---

## Example Invocations

### Example 1: First-Time Setup

> **User:** I want to start tracking my net worth. Help me set it up.
>
> **Agent:** Great — let's build your balance sheet. I'll ask one thing at a time. **First: cash you can access right now.**
>
> **User:** $8,200 in Chase checking, $15,000 in Ally savings @ 4.5%
>
> **Agent:** ✓ Logged:
> - `Chase Checking` — $8,200 (cash, liquid)
> - `Ally Savings` — $15,000 (cash, liquid, @4.5%)
>
> Cash total: $23,200. **Next: investment / brokerage accounts?** (Vanguard, Fidelity, Robinhood, etc.)
>
> **User:** $32,000 in Vanguard brokerage, mostly VTSAX. $51,000 in my 401k.
>
> **Agent:** ✓ Logged:
> - `Vanguard Brokerage` — $32,000 (investment, liquid)
> - `Vanguard 401k` — $51,000 (retirement, semi-liquid)
>
> **Next: real estate, vehicles, or other big assets?**
>
> **User:** My condo worth about $480k, I owe $312k on the mortgage
>
> **Agent:** ✓ Logged:
> - `Condo (Primary Residence)` — $480,000 (real_estate, illiquid)
> - `Condo Mortgage` — $312,000 owed @ 6.25%
>
> **Next: liabilities? Credit cards, student loans, auto loans?**
>
> **User:** $1,850 on Chase Sapphire @ 24.99%. $14,800 in federal student loans @ 6.5%. Car loan $8,400 @ 7.2%.
>
> **Agent:** ✓ Logged 3 liabilities. **Taking your first snapshot...**
>
> ```text
> NET WORTH  ·  2026-07-19 (your very first snapshot)
> ─────────────────────────────────────────────
> Assets:        $586,200
> Liabilities:   $336,200
> ─────────────────────────
> NET WORTH:     $250,000  🎉
>
> Liquid net worth:    $ 39,350  (cash + investments − debt)
> Debt-to-asset ratio:  57.4%
> ```
>
> I'll save monthly snapshots so you can see the trend. Want me to set up a cron reminder on the 1st of each month?

### Example 2: Monthly Check-In

> **User:** Update Chase checking to $14,200. I also paid $400 extra on the credit card this month.
>
> **Agent:** Updating...
> - `Chase Checking`: $8,200 → **$14,200** (+$6,000)
> - `Chase Sapphire CC`: $1,850 → **$1,450** (−$400)
>
> **Taking July snapshot:**
>
> ```text
> NET WORTH  ·  2026-07-31
> ─────────────────────────────────────────────
> Assets:        $592,000  (+$5,800)
> Liabilities:   $335,800  (−$400)
> ─────────────────────────
> NET WORTH:     $256,200  (+$6,200 / +2.5%)
>
> vs. June:        +$6,200  (+2.5%)
> 6-month trend:   ▁▁▂▂▃▅█  ↑ steady climb
> ATH:             $256,200 (today!)
> ```
>
> 🎉 New all-time high! Liquid net worth is now $45,150.

### Example 3: Debt Strategy

> **User:** Compare avalanche vs snowball for my 3 debts. I can throw $500/month extra.
>
> **Agent:** Running both strategies...
>
> | Debt | Balance | APR | Min Pmt |
> |------|---------|-----|---------|
> | Chase Sapphire CC | $1,450 | 24.99% | $35 |
> | AmEx Gold CC | $3,200 | 21.99% | $90 |
> | Car Loan | $8,400 | 7.20% | $240 |
>
> **Avalanche** (highest APR first):
> - Chase Sapphire: paid off **month 3** — saves $487 in interest
> - AmEx Gold: paid off **month 9** — saves $598
> - Car Loan: paid off **month 23**
> - **Total: 23 months, $2,103 interest paid**
>
> **Snowball** (lowest balance first):
> - Chase Sapphire: paid off **month 3** (same)
> - AmEx Gold: paid off **month 11** (2 months slower)
> - Car Loan: paid off **month 24** (1 month slower)
> - **Total: 24 months, $2,261 interest paid**
>
> 💡 **Avalanche wins by $158** and finishes 1 month sooner. But if quick psychological wins matter, snowball gets you a "balance zero'd" dopamine hit slightly earlier on the AmEx.
>
> **Recommended: Avalanche.** Want me to draft a payoff schedule?

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User logs *just* balance, no account type | Default to `other` and ask once. Don't guess liquidity. |
| Liability balance grows (interest accrues) | Note in history; flag at next snapshot if it grew > 2% MoM with no user update — likely missed payment or compounding. |
| Mixing currencies (USD account + EUR property) | Store currency per account. Compute net worth using snapshot-date FX rate (use a free API like `exchangerate.host` or static table). Mark FX as `estimated` in report. |
| Real estate value stale (user hasn't re-appraised in 2+ years) | Show last-updated date in report. Suggest re-valuing annually. Mark illiquid assets > 365 days stale with ⚠️. |
| User logs *net* of mortgage instead of asset + liability separately | Always log asset gross AND liability separately. Net worth math = sum(assets) − sum(liabilities). Don't double-count. |
| Multiple snapshots same day | Keep latest. Don't bloat `snapshots[]` with duplicates. |
| Crypto wallet balance not pulled | Note: this skill does **not** auto-pull from exchanges. User must update by chat (or pair with a `crypto-portfolio-tracker` if added later). |
| Loan paid off but still in accounts | Mark `paid_off: true` + zero balance. Keep in history for record but exclude from active totals. |
| User asks trend with only 1 snapshot | Say so: "You only have 1 snapshot — no trend yet. Want me to backfill last 6 months from memory or bank statements?" |
| Negative net worth | Normal for early-career / heavy student debt. Don't sugarcoat, but show liquid net worth separately and celebrate small positive deltas. |

---

## Verification Checklist

Before claiming a snapshot or projection is correct, verify:

- [ ] All accounts have a `kind` (asset | liability), `type`, and positive `balance`
- [ ] Currency is set per account; default currency declared at top level
- [ ] Liquidity classification follows the default mapping (or user override is noted)
- [ ] Sum of asset balances = `total_assets` in snapshot
- [ ] Sum of liability balances = `total_liabilities` in snapshot
- [ ] `net_worth = total_assets − total_liabilities`
- [ ] Liquid/semi/illiquid split sums to `total_assets`
- [ ] Snapshot date is ISO `YYYY-MM-DD`
- [ ] For debt projections: APR is decimal (`0.2499` not `24.99`); formula compounds monthly
- [ ] Trend chart uses min/max-normalized bars (never raw numbers — bar chart is for *shape*, use a table for values)
- [ ] If paired with `personal-expense-tracker`, emergency runway = liquid_assets / avg_monthly_expenses over last 90 days

---

## Data Sources & Accuracy

| Source | Used for | Accuracy |
|--------|----------|----------|
| User chat input | All account balances & updates | 100% authoritative (it's *your* data) |
| `~/.hermes/data/networth.json` | Persistence | Local-only, encrypted at rest by macOS FileVault if enabled |
| `exchangerate.host` (free, no key) | FX for non-default-currency accounts | Daily rate, ~0.1% deviation from market |
| Manual valuation | Real estate, vehicles, collectibles | User-estimated; flag stale (>365d) |
| `personal-expense-tracker` skill | Avg monthly expenses (for emergency runway) | Derived from local expense JSON |

**This skill does NOT:**

- Connect to banks, brokerages, or crypto exchanges via Plaid/Yodlee/etc.
- Pull live stock or crypto prices (treat investment balances as user-reported)
- Report to credit bureaus or any third party
- Require any account credentials

**Privacy:** All data lives in `~/.hermes/data/networth.json`. The agent never transmits it. To back up, copy the file. To wipe, delete it.

---

## Cron Integration (Optional)

Pair with `cron-pipeline-builder` for monthly auto-snapshots:

```bash
# ~/.hermes/cron/networth-monthly.sh
#!/bin/bash
# 1st of every month at 9am
hermes -s net-worth-tracker "Take this month's snapshot and append to history. \
  Flag any account not updated in 60+ days. \
  Show me net worth vs. last month."
```

```yaml
# ~/.hermes/cron/jobs.yaml
- name: networth-monthly
  schedule: "0 9 1 * *"
  command: ~/.hermes/cron/networth-monthly.sh
  notify: true
```

---

## Related Skills

- **personal-expense-tracker** — pull avg monthly spend for emergency runway calc
- **subscription-manager** — see recurring outflows vs. net worth growth
- **csv-explorer** — import historical balances from a bank CSV export
- **report-formatter** — pretty-print monthly net-worth statements for sharing