---
name: personal-expense-tracker
description: "Track daily expenses, categorize spending, set budgets, and generate monthly financial reports — all by chatting with Hermes"
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, expenses, budgeting, tracking, personal-finance, spending]
    related_skills: [report-formatter, format-converter]
---

# Personal Expense Tracker（个人记账助手）

> Log expenses by natural language, categorize spending, set monthly budgets, and get clear financial reports — without opening a single app.

| Capability | Description |
|-----------|-------------|
| 🖊️ Log expenses | Say "spent 45 on lunch" and it's recorded with date/category |
| 🗂️ Auto-categorize | Food, transport, shopping, entertainment — or custom tags |
| 📊 Monthly reports | See where your money went with a breakdown table |
| 🎯 Budget limits | Set per-category caps and get warned when you're close |
| 📈 Trends | Compare this month vs last month spending |
| 💾 Local storage | Data saved to `~/.hermes/data/expenses.json` — no cloud, no leak |

---

## When to Use

- *"I spent ¥35 on coffee this morning"*
- *"Log ¥280 for dinner at the hotpot place"*
- *"Show me my spending this month"*
- *"Set a ¥2000 monthly budget for dining out"*
- *"How much did I spend on transportation last month?"*
- *"Am I over budget on entertainment?"*
- *"这个月花了多少钱？帮我做个报表"*
- *"帮我记一笔：淘宝买书花了128"*

---

## Core Workflow

### Step 1: Log an Expense

User says something like *"Spent 120 on taxi"* or *"买了杯奶茶15块"*.

The agent parses:
- **Amount:** numeric value (support ¥/€/$ — auto-detect symbol)
- **Category:** infer from context (taxi → transport, 奶茶 → food/drink)
- **Note:** optional description
- **Date:** today by default, or *"last Tuesday"* if specified

```json
// Stored entry format in ~/.hermes/data/expenses.json
{
  "id": "2026-06-23-001",
  "date": "2026-06-23",
  "amount": 120,
  "currency": "CNY",
  "category": "transport",
  "note": "taxi to office",
  "tags": []
}
```

**Supported categories** (extensible via custom tags):
| Category | Examples |
|----------|----------|
| `food` | meals, groceries, coffee, snacks |
| `transport` | taxi, subway, gas, parking |
| `shopping` | clothes, electronics, home goods |
| `entertainment` | movies, games, streaming, concerts |
| `housing` | rent, utilities, maintenance |
| `health` | pharmacy, doctor, gym |
| `education` | courses, books, tutoring |
| `utilities` | phone, internet, electricity |
| `other` | anything that doesn't fit |

After logging, reply with a confirmation:

```markdown
✅ Recorded: **¥120.00** — Transport (taxi to office)
📅 2026-06-23

Today's total: ¥155.00
```

### Step 2: Set Budgets

User says *"Set a ¥3000 monthly food budget"*.

```json
// ~/.hermes/data/expenses.json → budgets section
"budgets": {
  "food": { "monthly_limit": 3000, "currency": "CNY" },
  "entertainment": { "monthly_limit": 500, "currency": "CNY" }
}
```

When an expense pushes a category close to its limit (≥80%), warn:

```markdown
⚠️ **Budget Alert:** Food this month: ¥2,530 / ¥3,000 (84%)
You have ¥470 left for the rest of the month.
```

### Step 3: Generate Reports

User says *"Show me this month's spending"*.

```markdown
# 📊 June 2026 Spending Report

## Summary
| Metric | Value |
|--------|-------|
| Total Spent | ¥4,280.00 |
| Daily Avg | ¥186.09 |
| Budget Used | 71% of ¥6,000 |
| Days Tracked | 23 / 30 |

## By Category
| Category | Amount | % of Total | Budget | Left |
|----------|--------|-----------|--------|------|
| 🍔 Food | ¥1,850.00 | 43% | ¥3,000 | ¥1,150 |
| 🚇 Transport | ¥680.00 | 16% | ¥800 | ¥120 |
| 🛍️ Shopping | ¥920.00 | 21% | ¥1,000 | ¥80 ⚠️ |
| 🎬 Entertainment | ¥380.00 | 9% | ¥500 | ¥120 |
| 📚 Education | ¥250.00 | 6% | — | — |
| 🏥 Health | ¥200.00 | 5% | — | — |

## Top Expenses This Month
| Date | Amount | Category | Note |
|------|--------|----------|------|
| 06-20 | ¥450.00 | food | Grocery run |
| 06-15 | ¥320.00 | shopping | New headphones |
| 06-10 | ¥280.00 | food | Team dinner |

💡 **Tip:** Food is 43% of spending — consider meal prep to save.
```

### Step 4: Data Management

| Action | Command |
|--------|---------|
| View raw data | `cat ~/.hermes/data/expenses.json \| python3 -m json.tool` |
| Export to CSV | `python3 -c "import json; import csv; ..."` (use `format-converter` skill) |
| Delete entry | *"Remove the ¥450 grocery expense from June 20"* |
| Edit entry | *"Change the taxi expense from yesterday to ¥150"* |
| Reset all data | *"Clear all my expense data"* (confirmation required) |

---

## Example Invocations

### Example 1: Quick log + daily check

**User:** *"Spent 22 on subway this morning"*

**Agent:**
```markdown
✅ Recorded: **¥22.00** — Transport (subway)
📅 2026-06-23

Today's total: ¥22.00
💡 You haven't logged any food today — need lunch ideas?
```

### Example 2: Monthly review with budget comparison

**User:** *"How am I doing on my budget this month?"*

**Agent:**
```markdown
# 📊 June Budget Check (June 23)

## Overall
- **Budget:** ¥8,000 / month
- **Spent:** ¥5,240 (65%)
- **Remaining:** ¥2,760 (35%)
- **Daily budget left:** ¥394/day for 7 days

## Category Breakdown
| Category | Spent | Budget | Status |
|----------|-------|--------|--------|
| Food | ¥2,530 | ¥3,000 | ✅ 84% |
| Transport | ¥580 | ¥800 | ✅ 73% |
| Shopping | ¥920 | ¥1,000 | ⚠️ 92% |
| Entertainment | ¥380 | ¥500 | ✅ 76% |
| Housing | ¥830 | ¥1,500 | ✅ 55% |

⚠️ **Shopping is at 92%** — only ¥80 left this month.
```

### Example 3: 中文场景 — 记录 + 查询

**User:** *"帮我记一笔：今天买菜花了156"*

**Agent:**
```markdown
✅ 已记录：**¥156.00** — 餐饮（买菜）
📅 2026-06-23

📋 今日累计：¥156.00
📅 本月累计：¥2,530.00（餐饮预算 ¥3,000 — 剩余 ¥470）
```

**User:** *"这个月交通费花了多少？"*

**Agent:**
```markdown
🚇 **本月交通费：¥580.00**
- 地铁/公交：¥220.00（10笔）
- 打车：¥360.00（6笔）

📊 交通预算 ¥800.00，还剩 ¥220.00
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User says "spent 50 on dinner" but unclear on currency | Default to user's local currency. Ask once if ambiguous, then remember. |
| Expense data file doesn't exist yet | Auto-create `~/.hermes/data/` directory and `expenses.json` with empty schema on first write. |
| User wants to edit a past entry | Find by date + amount + note fuzzy match. Confirm before modifying. |
| Category not recognized | Default to `other`, then ask *"What category should this be under?"* |
| Duplicate entry (user logs same thing twice) | Check last 3 entries — if identical amount+category+date within 5 minutes, ask *"Did you already log this?"* |
| Large number of entries slows things | Store as array of objects; for querying, filter with `jq` rather than loading full file into LLM context. |

---

## Verification Checklist

- [ ] Expense logged with amount, category, date, and note
- [ ] Data persisted to `~/.hermes/data/expenses.json`
- [ ] Budget alert fires at ≥80% of monthly limit
- [ ] Monthly report shows total, category breakdown, and top expenses
- [ ] User can query spending by category or date range
- [ ] Currency symbol correctly parsed (¥/$/€)
- [ ] Chinese natural language input works (e.g., "花了128块买书")
- [ ] Duplicate detection prevents double-logging within 5 minutes
- [ ] Edit/delete operations succeed with confirmation

---

## Data Sources & Accuracy

- **All data stored locally** at `~/.hermes/data/expenses.json` — no external API calls, no cloud sync, no privacy risk.
- **Currency detection** is heuristic: if user explicitly types ¥/$/€ use that; if just a number, default to environment locale (CNY for zh-CN).
- **Category inference** is LLM-based and may occasionally misclassify (e.g. "bought a switch" could be shopping or entertainment). User can override: *"Actually that was entertainment"*.
- **Budget calculations** are exact math on stored data — no rounding errors.
- **Export formats** (CSV, JSON) are lossless; rely on `format-converter` skill for format transformations.
