---
name: investment-portfolio-tracker
description: "Track investment positions from chat — stocks/ETFs/crypto/bonds/cash lots, cost basis, unrealized P/L, target-vs-actual allocation, rebalancing suggestions, dividend & interest income, tax-loss harvesting candidates. All local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, investing, portfolio, stocks, etf, crypto, bonds, cost-basis, capital-gains, dividends, tax-loss-harvesting, asset-allocation, rebalancing, personal-finance]
    related_skills: [net-worth-tracker, tax-prep-assistant, personal-expense-tracker, csv-explorer, report-formatter]
---

# Investment Portfolio Tracker（投资持仓追踪器）

> Stop maintaining a spreadsheet. Log your buys, sells, dividends, and interest in plain chat — Hermes keeps your cost basis, shows unrealized P/L per position and per account, flags allocation drift, and surfaces tax-loss harvesting candidates before year-end.

| Capability | Description |
|-----------|-------------|
| 📥 Log lots | Buy/sell lots per position — date, shares, price, fees; auto FIFO/average-cost basis |
| 📊 Position dashboard | Cost basis, current value, unrealized P/L (amount + %), per account and per asset class |
| 🥧 Allocation check | Target vs actual allocation (US/INTL stocks, bonds, cash, crypto, REITs) with drift alerts |
| ⚖️ Rebalance plan | Concrete trade suggestions to move N units from overweight to underweight |
| 💰 Income ledger | Dividends, interest, and realized gains — yield on cost, monthly/annual income |
| 🧾 Realized gains | Track sell events with FIFO lots — capital-gains preview for tax-prep |
| 🪓 Tax-loss harvesting | Flag positions at a loss beyond wash-sale window, group same-ish exposures |
| 🧮 Position sizing | Max position size by risk % and conviction tiers (core/satellite) |
| 📈 Scenarios | What-if: market −20% / +20%, yield change, DRIP vs cash comparison |
| 💾 Local storage | All data at `~/.hermes/data/portfolio.json` — no brokerage link, no leak |

---

## When to Use

- *"Bought 10 shares of VTI at $241.32 today"*
- *"Sold 5 shares of AAPL at $228 — I bought them in March"*
- *"Record the $43.20 dividend VTI paid me"*
- *"What's my total unrealized P/L right now?"*
- *"Am I too heavy in tech? Show my allocation vs my 70/20/10 target"*
- *"How do I rebalance back to my target?"*
- *"Which positions are at a loss I could harvest before year-end?"*
- *"What's my dividend yield on cost?"*
- *"If the market drops 20%, how much would I lose?"*
- *"我今天买了两股特斯拉，$305"*
- *"帮我看看我的持仓有没有需要止损的"*
- *"我的仓位是不是太集中了？"*

---

## Core Workflow

### Step 1: Log a Transaction (Buy / Sell / Dividend / Interest)

User says *"Bought 10 shares of VTI at $241.32"*. The agent parses and appends a lot:

```json
{
  "id": "lot-20260815-001",
  "date": "2026-08-15",
  "action": "buy",
  "symbol": "VTI",
  "name": "Vanguard Total Stock Market ETF",
  "account": "brokerage",
  "asset_class": "us_equity",
  "shares": 10.0,
  "price": 241.32,
  "fees": 0.0,
  "amount": 2413.20,
  "currency": "USD"
}
```

For **sells**, add `"action": "sell"` and attach the realized gain calculation:

- Use **FIFO** by default (state it in the reply). Average-cost is OK if the user consistently requests it — store `cost_method` per account.
- Realized P/L = (sell price × shares − fees) − (cost basis of consumed lots).
- If the user says *"sell the shares I bought in March"*, match the specific lot(s) by date; if ambiguous, ask or default to FIFO and note it.

For **dividends / interest**, append to the income ledger:

```json
{
  "id": "inc-20260815-001",
  "date": "2026-08-15",
  "symbol": "VTI",
  "type": "dividend",
  "gross": 43.20,
  "withholding": 0.0,
  "net": 43.20,
  "reinvested": false
}
```

Always ask for missing price/date when you can't infer it. If the user only says *"I bought more VTI"*, request the missing fields instead of guessing.

### Step 2: Maintain the Position Register

After every transaction, recompute the register. For each open position:

```json
{
  "symbol": "VTI",
  "account": "brokerage",
  "shares": 47.5,
  "cost_basis": 11332.10,
  "avg_cost_per_share": 238.57,
  "lots": ["lot-20260815-001", "lot-20260312-002", "..."]
}
```

- `shares` and `cost_basis` are the running totals; `lots[]` links to the lot ledger for FIFO precision.
- When a sell consumes lots, keep the consumed lots in the ledger with `"closed": true` and `"realized_pl"` — they feed the realized-gains report.
- Update **current prices** only when the user provides them (chat) or via a free quote API (see Data Sources). Never fabricate a price. If no fresh price: mark the position `"price_as_of": "<last known date>"` and show it in the dashboard with ⚠️.

### Step 3: Answer Questions with Computed Metrics

Support these at minimum (all computed from local data):

| Question | Metric | Formula |
|----------|--------|---------|
| *"What's my unrealized P/L?"* | Unrealized P/L | Σ (current_value − cost_basis) per open position |
| *"Show my allocation"* | Actual allocation | Σ current_value per `asset_class` ÷ total portfolio value |
| *"Rebalance me"* | Drift + plan | For each class: target% × total − actual; propose sell/buy in whole shares |
| *"Any tax-loss harvests?"* | TLH candidates | Positions with unrealized loss > threshold (default $500) and no buy within 30 days (wash-sale rule) |
| *"What's my yield?"* | Yield on cost | Σ annualized dividends ÷ Σ cost basis |
| *"What if market drops 20%?"* | Scenario | Apply scenario multiplier per asset class (e.g. equities −20%, bonds −3%) and recompute P/L |

For **rebalance suggestions**, output a table:

```
| Class    | Target | Actual | Drift | Action            |
|----------|--------|--------|-------|-------------------|
| US equity| 60%    | 63.4%  | +3.4% | Sell ~$1,700 VTI  |
| INTL eq  | 10%    | 8.1%   | −1.9% | Buy ~$950 VXUS    |
| Bonds    | 20%    | 21.2%  | +1.2% | Sell ~$600 BND    |
| Cash     | 10%    | 7.3%   | −2.7% | Deploy ~$1,350    |
```

### Step 4: Year-End / Tax-Ready Reports

Generate on request (typically January, before filing):

- **Realized gains summary**: total short-term vs long-term realized P/L (holding period > 1 year = long-term). Export as a CSV/table the user can hand to their tax software.
- **Income statement**: dividends + interest by month and by symbol, gross vs net, foreign withholding amounts.
- **Wash-sale watch**: any sell at a loss followed by a buy of a *substantially identical* security within ±30 days — flag it (the loss is disallowed).
- **Unrealized picture**: total unrealized P/L and the biggest winners/losers, which informs TLH before Dec 31.

Keep a `reports/` subfolder or a `yearly_summary` field in the JSON so past years stay queryable.

---

## Example Invocations

### Example 1 — Log a Buy and Check P/L

> **User:** 我今天买了 10 股 VTI，$241.32
>
> **Agent:**
> ```
> ✅ Logged: BUY 10.0 VTI @ $241.32 (fees $0) — $2,413.20
> Account: brokerage · Asset class: US equity
>
> Your VTI position is now 47.5 shares, cost basis $11,332.10
> Unrealized P/L (using last price $255.00 as of 08/10): +$779.65 (+6.9%)
> ```

### Example 2 — Rebalance Back to Target

> **User:** 帮我 rebalance 回 60/10/20/10
>
> **Agent:**
> ```
> Current: US 63.4% · INTL 8.1% · Bonds 21.2% · Cash 7.3%
> Drift vs 60/10/20/10: US +3.4%, INTL −1.9%, Bonds +1.2%, Cash −2.7%
>
> Suggested trades (whole shares):
> - Sell 7 VTI (~$1,785)  → US 60.0%
> - Buy 4 VXUS  (~$960)   → INTL 10.0%
> - Sell 6 BND  (~$450)   → Bonds 20.0%
> - Cash left: deploy ~$1,275 → Cash 10.0%
>
> 💡 Consider harvesting losses first if any of these are at a loss (see tax-loss candidates).
> ```

### Example 3 — Tax-Loss Harvesting Candidates

> **User:** 年末了，哪些持仓可以拿来抵税？
>
> **Agent:**
> ```
> 🪓 Tax-loss harvesting candidates (unrealized loss > $500, no buy in last 30 days):
>
> | Symbol | Shares | Cost basis | Value | Loss | Wash-safe? |
> |--------|--------|-----------|-------|------|------------|
> | PLTR   | 120    | $14,520    | $9,840| −$4,680 | ✅ Yes |
> | ARKK   | 40     | $4,210     | $3,120| −$1,090 | ✅ Yes |
> | TSLA   | 6      | $1,830     | $1,450| −$380   | ⚠️ <$500 threshold |
>
> ⚠️ You bought QQQ 20 days ago — any loss on VOO-like positions would be a wash sale. Consider harvesting before Dec 31.
> ```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| FIFO vs average cost mismatch | Default FIFO. Store `cost_method` per account. When selling, say which lots you consumed. |
| Fabricated current prices | Never invent a price. Use user-provided quotes or a free API (e.g. Yahoo Finance chart endpoint via curl). If unavailable, show `price_as_of` date and ⚠️ stale marker. |
| Wash sale ignored | Check for buy of same/substantially-identical security ±30 days around any loss sale. Flag disallowed losses. |
| Fractional shares lost | Store shares as float (10.25 OK). Round only in display or whole-share trade suggestions. |
| Selling more than held | Validate `sell.shares <= position.shares`. If lots are ambiguous, ask before consuming. |
| Double-counting across skills | This skill tracks **investment lots**. `net-worth-tracker` tracks account-level totals — don't store position P/L there. `tax-prep-assistant` consumes realized-gains summaries — don't duplicate the ledger. |
| Dividend reinvestment | If `reinvested: true`, create a buy lot at the dividend date with the net amount / price — keeps basis accurate. |
| Multi-currency positions | Store `currency` per lot. Convert to default currency at snapshot time for allocation math; mark FX as estimated. |
| User reports only position value, not lots | Fall back to a single synthetic lot with `synthetic: true` and today's date as `date` — basis accuracy is then best-effort; tell the user. |
| Corporate actions (splits/mergers) | Adjust share count and basis manually. For splits: shares × N, price ÷ N, basis unchanged. Note the action in the lot. |

---

## Verification Checklist

Before claiming a number is correct, verify:

- [ ] Every transaction has `date`, `action`, `symbol`, `shares` (float), `price`, `amount`, `currency`
- [ ] Buy lot `amount = shares × price + fees` (fees added to basis)
- [ ] Sell: `shares_sold ≤ shares_held`; consumed lots sum matches; realized P/L recorded per lot
- [ ] Position `shares = Σ open lot shares`; `cost_basis = Σ open lot (shares×price+fees)`
- [ ] `avg_cost_per_share = cost_basis / shares` (guard divide-by-zero)
- [ ] Allocation percentages sum to 100% (±0.1 rounding tolerance)
- [ ] Drift = actual% − target%; rebalance plan states whole-share quantities and expected resulting %
- [ ] Unrealized P/L uses the price's `as_of` date and marks stale prices
- [ ] Wash-sale check done for every realized loss (buy within ±30 days → disallowed flag)
- [ ] Dividends: `net = gross − withholding`; reinvested dividends created a buy lot
- [ ] No P/L numbers claimed without an explicit or stored current price

---

## Data Sources & Accuracy

| Source | Used for | Accuracy |
|--------|----------|----------|
| User chat input | Buys, sells, dividends, prices | 100% authoritative (it's *your* data) |
| `~/.hermes/data/portfolio.json` | Persistence | Local-only, encrypted at rest by macOS FileVault if enabled |
| Yahoo Finance quote endpoint (free, no key) | Optional current prices: `https://query1.finance.yahoo.com/v8/finance/chart/AAPL` | Near-real-time during market hours; treat as reference, not execution price |
| Brokerage statements (user-provided) | Reconciliation of lots & dividends | Source of truth; import as CSV via `csv-explorer` |
| `net-worth-tracker` skill | Account-level totals for the balance sheet | Derived from local JSON |
| `tax-prep-assistant` skill | Year-end realized-gains & wash-sale context | Derived from local JSON |

**This skill does NOT:**

- Connect to brokerages, banks, or exchanges via Plaid/Alpaca/etrade APIs
- Place orders or make investment decisions — it models what you tell it
- Auto-track daily market moves unless the user (or a cron job) refreshes prices
- Provide financial advice — TLH and rebalance outputs are arithmetic, not recommendations

**Privacy:** All data lives in `~/.hermes/data/portfolio.json`. The agent never transmits it. To back up, copy the file. To wipe, delete it.

---

## Cron Integration (Optional)

Pair with `cron-pipeline-builder` for a weekly price-refresh and drift alert:

```bash
# ~/.hermes/cron/portfolio-weekly.sh
#!/bin/bash
hermes -s investment-portfolio-tracker "Refresh prices for all my positions (Yahoo chart endpoint). \
  Recompute P/L and allocation. \
  Alert me if any asset class drifted > 3% from target, or if any new TLH candidate appeared."
```

```yaml
# ~/.hermes/cron/jobs.yaml
- name: portfolio-weekly
  schedule: "0 10 * * 6"
  command: ~/.hermes/cron/portfolio-weekly.sh
  notify: true
```

---

## Related Skills

- **net-worth-tracker** — roll portfolio totals into your balance sheet; keep lot-level detail here
- **tax-prep-assistant** — export realized gains and wash-sale flags for tax season
- **personal-expense-tracker** — see monthly savings rate vs portfolio growth
- **csv-explorer** — import historical lots from brokerage CSV exports
- **report-formatter** — pretty-print the quarterly portfolio report for sharing
