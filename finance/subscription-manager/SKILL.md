---
name: subscription-manager
description: "Track recurring subscriptions, free trials, and SaaS spend — get renewal alerts, find unused subs, and see your true monthly burn rate"
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [finance, subscriptions, recurring-bills, saas, free-trial, budgeting, personal-finance, spend-tracking]
    related_skills: [personal-expense-tracker, csv-explorer, report-formatter]
---

# Subscription Manager（订阅管家）

> Catalog every recurring charge, catch free-trial conversions, and find the SaaS zombies you forgot you were paying for — all in plain chat.

| Capability | Description |
|-----------|-------------|
| 📋 Catalog subs | Log Netflix, Spotify, Notion, gym, etc. by natural language |
| 💸 Burn rate | True monthly & annual cost of all your subscriptions |
| ⏰ Renewal alerts | Warn 3 days before a free trial converts, 7 days before annual renewal |
| 🪦 Zombie finder | Highlight subs with 0 usage or low value-per-dollar |
| 📊 Category breakdown | Entertainment, productivity, fitness, news, AI tools, etc. |
| 🔁 Cancellation helper | Step-by-step "how to cancel" + retention-bypass tips |
| 💾 Local storage | All data at `~/.hermes/data/subscriptions.json` — no cloud, no leak |

---

## When to Use

- *"Add Netflix $15.99 monthly, next billing on the 5th"*
- *"I'm starting a 14-day trial of Linear tomorrow"*
- *"What am I paying for every month?"*
- *"Which subscriptions renew next week?"*
- *"Show me all my annual subscriptions"*
- *"What did I subscribe to this year that I never use?"*
- *"Cancel Spotify — how do I do it without losing my playlists?"*
- *"我这个月订阅一共要花多少钱？"*
- *"帮我记一笔：ChatGPT Plus 月费$20"*

---

## Core Workflow

### Step 1: Add a Subscription

User says *"Add Notion AI $10/month starting today"* or *"我订了Figma，年费$180，9月到期"*.

The agent parses:

- **Name** — display name (e.g. `Notion AI`, `Netflix`, `Adobe Creative Cloud`)
- **Amount + currency** — numeric value with `$`/`¥`/`€` (auto-detect)
- **Billing cycle** — `monthly` / `annual` / `quarterly` / `weekly` / custom days
- **Next billing date** — explicit (`on the 5th`) or relative (`in 14 days`); default to today
- **Trial?** — boolean; if true, `trial_end_date` is required
- **Category** — auto-infer; can be overridden
- **Notes** — optional (account email, plan tier, etc.)

```json
// Stored in ~/.hermes/data/subscriptions.json
{
  "id": "sub-2026-07-09-001",
  "name": "Notion AI",
  "amount": 10.00,
  "currency": "USD",
  "cycle": "monthly",
  "next_billing": "2026-08-09",
  "trial": false,
  "trial_end_date": null,
  "category": "productivity",
  "status": "active",
  "added_on": "2026-07-09",
  "notes": "Personal workspace, plan: Plus"
}
```

**Default category list** (extensible via custom tags):

| Category | Examples |
|----------|----------|
| `entertainment` | Netflix, Spotify, Disney+, YouTube Premium |
| `productivity` | Notion, Linear, Todoist, 1Password |
| `ai-tools` | ChatGPT Plus, Claude Pro, Midjourney, Cursor |
| `cloud-storage` | iCloud, Google One, Dropbox, Backblaze |
| `news` | Bloomberg, NYT, The Information, Substack |
| `fitness` | Peloton, Strava, Calm, Headspace |
| `developer` | GitHub Copilot, Vercel, Railway, Heroku |
| `shopping` | Amazon Prime, Walmart+, Costco membership |
| `education` | Coursera, MasterClass, Brilliant, Duolingo Plus |
| `other` | catch-all |

**After logging, reply:**

```markdown
✅ Added: **Notion AI** — $10.00 / month
📅 Next billing: 2026-08-09
🏷️ Category: productivity

📊 You now have 7 active subscriptions (monthly burn: $87.40)
```

### Step 2: Track Trials & Renewal Alerts

When adding a trial, set `trial: true` and `trial_end_date`:

```json
{
  "id": "sub-2026-07-09-002",
  "name": "Linear",
  "amount": 8.00,
  "currency": "USD",
  "cycle": "monthly",
  "next_billing": "2026-07-23",
  "trial": true,
  "trial_end_date": "2026-07-23",
  "category": "productivity",
  "status": "trial",
  "added_on": "2026-07-09",
  "notes": "Standard plan, evaluate after trial"
}
```

**Proactive reminders** (suitable for cron — daily check at 9 AM):

| Condition | Alert |
|-----------|-------|
| Trial ends in ≤ 3 days | 🚨 `Linear trial ends Jul 23 — $8/mo will charge automatically. Cancel before then if not needed.` |
| Annual sub renews in ≤ 14 days | ⚠️ `Adobe CC renews Aug 1 — $239.88/yr. Confirm you still need it.` |
| Monthly sub next charge in ≤ 2 days | 🔔 `Notion AI charges $10 on Jul 11.` |
| Trial already converted (status still "trial" but past `trial_end_date`) | ❗ `Linear: trial expired Jul 23, now charging $8/mo. Did you mean to keep it?` |

User can also ask ad hoc: *"What's renewing this week?"* or *"我有哪些试用快到期了？"*

### Step 3: Analyze Spend

User says *"Show me my monthly burn"* or *"我这个月订阅要花多少？"*.

**Burn rate calculation** — convert every sub to its monthly equivalent:

```python
monthly_cost = {
  "monthly":   amount,
  "annual":    amount / 12,
  "quarterly": amount / 3,
  "weekly":    amount * 52 / 12,
  "daily":     amount * 30,
}
```

**Report output:**

```markdown
# 💸 Subscription Report — July 2026

## Summary
| Metric | Value |
|--------|-------|
| Active subscriptions | 12 |
| Monthly burn | $147.32 |
| Annual cost (if all renew) | $1,767.84 |
| Trials active | 2 |
| Trials ending in ≤ 7 days | 1 (Linear, $96/yr value) |
| Free trials converted this year | 3 ($204 spent) |

## By Category
| Category | # | Monthly | % of Total |
|----------|---|---------|------------|
| 🎬 Entertainment | 3 | $32.97 | 22% |
| 🤖 AI tools | 2 | $48.00 | 33% |
| 💼 Productivity | 4 | $29.50 | 20% |
| ☁️ Cloud storage | 2 | $14.95 | 10% |
| 📰 News | 1 | $22.00 | 15% |

## 🚨 Upcoming Renewals (next 14 days)
| Date | Sub | Amount | Action |
|------|-----|--------|--------|
| Jul 11 | Notion AI | $10.00 | Keep (using daily) |
| Jul 23 | Linear (trial → paid) | $8.00 | ⚠️ Decide before trial ends |
| Aug 1 | Adobe CC (annual) | $239.88 | ⚠️ Big charge — review usage |

## 🪦 Zombie Candidates (low value-per-dollar)
| Sub | Cost | Last used | Verdict |
|-----|------|-----------|---------|
| MasterClass | $19.99/mo | 3 months ago | 💀 Cancel — $240/yr wasted |
| NYT | $22.00/mo | Daily | ✅ Keep |
| Strava | $11.99/mo | 2 weeks ago | ⏸️ Pause until hiking season |

💡 **Tip:** Cancel MasterClass to save $240/year → monthly burn drops to $127.33.
```

### Step 4: Find Zombies & Optimize

User says *"Which subscriptions am I not using?"*.

The agent uses **last_used** field (user logs usage: *"I used Notion today"*) and a **value_score**:

```
value_score = usage_frequency_per_month / monthly_cost
```

Subs scoring below a threshold (default: < 1.0, i.e. less than once per dollar) are flagged.

```markdown
# 🪦 Subscription Audit

## Tier 1: Cancel immediately (< 0.5 uses per $)
- **MasterClass** — 1 use in 90 days / $19.99/mo → score 0.02 💀
- **Calm** — 3 uses in 60 days / $14.99/mo → score 0.05 💀

## Tier 2: Pause and revisit (0.5–1.0)
- **Strava** — 2 uses in 30 days / $11.99/mo → score 0.67 ⏸️

## Tier 3: Worth the money (> 1.0)
- **Notion** — daily use / $10/mo → score 9.0 ✅
- **Spotify** — daily use / $10.99/mo → score 8.2 ✅

💰 If you cancel Tier 1: **-$34.98/mo, -$419.76/yr**
```

### Step 5: Cancellation & Downgrade Help

User says *"Help me cancel MasterClass"*.

The agent outputs:

```markdown
# How to cancel MasterClass

1. Go to masterclass.com → log in
2. Click your profile icon (top right) → **Account Settings**
3. Click **Cancel Subscription** in the Membership section
4. Confirm — you'll keep access until end of billing period

## 💡 Retention bypass tips
- They may offer 50% off or 3 free months. **Just decline** if you really want out.
- If you only want a break, click **Pause Subscription** instead (1–3 months available).
- After cancelling, you can still access downloaded classes offline.
- Check your bank statement in 1–2 billing cycles to confirm the charge stopped.

## 📝 Tracking
- I marked MasterClass as `pending_cancel` in your data.
- Run `hermes -s subscription-manager` next month to verify no charge appeared.
```

**Persistence model** (in `~/.hermes/data/subscriptions.json`):

```json
{
  "id": "sub-2026-07-09-002",
  "name": "MasterClass",
  "status": "pending_cancel",          // active | trial | pending_cancel | cancelled
  "cancelled_on": "2026-07-09",
  "expected_last_charge": "2026-07-12"  // remind to check statement
}
```

After `expected_last_charge` passes, the agent can re-check and confirm.

---

## Example Invocations

### Example 1: Quick add + burn summary

**User:** *"Add Hulu $17.99/month and ChatGPT Plus $20/month, both starting today"*

**Agent:**
```markdown
✅ Added 2 subscriptions.

| Sub | Amount | Cycle | Category | Next billing |
|-----|--------|-------|----------|--------------|
| Hulu | $17.99 | monthly | entertainment | 2026-08-09 |
| ChatGPT Plus | $20.00 | monthly | ai-tools | 2026-08-09 |

📊 You now have 9 active subscriptions
💰 Monthly burn: $112.31 (was $74.32)
💸 Annual cost: $1,347.72

⚠️ AI tools now 35% of your subscription spend ($48/mo).
```

### Example 2: Trial tracking

**User:** *"I'm starting a 14-day trial of Cursor tomorrow"*

**Agent:**
```markdown
✅ Added: **Cursor** — $20.00 / month (trial)
📅 Trial ends: 2026-07-23
💡 On Jul 23, your card will be charged $20 unless you cancel.

📌 I'll remind you 3 days before (Jul 20) so you can decide:
- **Keep** — do nothing, it auto-renews
- **Cancel** — I'll give you the cancellation steps

Want me to set a hard reminder or just a heads-up?
```

### Example 3: Zombie hunt

**User:** *"What subscriptions am I not using anymore?"*

**Agent:**
```markdown
# 🪦 Zombie Audit (last 90 days)

Reviewed 12 active subscriptions worth $147.32/mo.

## 💀 Tier 1 — Cancel (saves $390/yr)
| Sub | Last used | Cost | Verdict |
|-----|-----------|------|---------|
| MasterClass | 92 days ago | $19.99/mo | Cancel — 1 watched class in 3 months |
| Calm | 71 days ago | $14.99/mo | Cancel — meditation habit didn't stick |

## ⏸️ Tier 2 — Pause (saves $144/yr)
| Sub | Last used | Cost | Verdict |
|-----|-----------|------|---------|
| Strava | 28 days ago | $11.99/mo | Pause — you'll ride again in summer |

## ✅ Tier 3 — Keep (high value)
| Sub | Uses / 90d | Cost | Score |
|-----|------------|------|-------|
| Spotify | 89 days | $10.99/mo | 8.1 uses/$ |
| 1Password | 84 days | $4.99/mo | 16.8 uses/$ |

💰 **Total potential savings: $534/year** if you cancel/pause Tier 1+2.

Want me to walk you through cancelling any of these?
```

### Example 4: 中文场景 — 月度复盘

**User:** *"我这个月订阅一共要花多少钱？"*

**Agent:**
```markdown
# 💸 2026年7月订阅总览

## 核心数据
- 在用订阅：**8 个**
- 月度烧钱：**¥468.00**
- 年度总成本：¥5,616.00（如全部续费）

## 按类别
| 类别 | 数量 | 月费 | 占比 |
|------|------|------|------|
| 🎬 影音娱乐 | 3 | ¥108 | 23% |
| 🤖 AI 工具 | 2 | ¥135 | 29% |
| 💼 效率工具 | 2 | ¥70 | 15% |
| ☁️ 云存储 | 1 | ¥21 | 4% |

## 🚨 近期提醒
- **7月12日**：Notion Plus 月费 ¥48 → 自动续费
- **7月23日**：Cursor 试用结束 → ¥140/年 自动扣款（**还有 4 天决定**）
- **8月1日**：Adobe CC 年费 ¥1,488 → **大额扣款，建议评估使用频率**

💡 **建议**：Cursor 试用如果不满意请在 7/20 前取消。
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User says "Netflix" without price | Ask once for price + cycle + next billing. Save preferences. |
| Mixed currencies (USD subs + CNY subs) | Store currency per entry. Convert to base via configurable FX rate (default 1:1 for report; user can set USD→CNY rate). |
| Free trial that requires cancel-by-date vs. auto-converts | Always set `trial_end_date` and warn 3 days prior. If user wants hard "must cancel", set status to `trial_pending_decision`. |
| User has 30+ subscriptions and `subscriptions.json` gets large | Use `jq` for filtering queries; do not load full file into LLM context. Summarize by category in one pass. |
| User cancels a sub but keeps paying for 1 more cycle | Add `cancelled_on` + `expected_last_charge`. On next check after that date, prompt: *"Did the charge stop?"* |
| Annual subscription vs. monthly — wrong conversion | Always divide annual by 12 for monthly burn. Show both numbers in the report to avoid confusion. |
| Duplicate entry (user adds the same sub twice) | Check by name (case-insensitive). If exact match exists, ask: *"You already have Notion AI at $10/mo. Add anyway?"* |
| Cron-driven alert spam | Default to daily digest (one combined message). User can opt into per-sub notifications: *"Alert me individually for any charge > $50."* |

---

## Verification Checklist

- [ ] Subscription added with name, amount, currency, cycle, next billing, category
- [ ] Data persisted to `~/.hermes/data/subscriptions.json`
- [ ] Burn rate calculation handles all cycles (weekly/monthly/quarterly/annual)
- [ ] Trial subs show trial_end_date and trigger 3-day-prior warning
- [ ] Annual subs flagged 14 days before renewal
- [ ] Zombie finder uses last_used field and value_score
- [ ] Report shows monthly + annual total + category breakdown
- [ ] Multi-currency supported (each entry has its own currency)
- [ ] Cancellation flow marks `status: pending_cancel` and tracks `expected_last_charge`
- [ ] Chinese natural language input works (e.g. "订了Figma，年费$180")
- [ ] Duplicate detection prevents double-adding
- [ ] Cron-friendly: daily check returns one digest, not N messages

---

## Data Sources & Accuracy

- **All data stored locally** at `~/.hermes/data/subscriptions.json` — no bank API integration, no third-party SaaS scrapers, no privacy risk.
- **Pricing** is user-supplied; the agent never pulls from vendor websites automatically (too brittle, vendors change layouts). User enters once at add time, then it sticks.
- **FX conversion** is configurable: user sets one base currency + an FX table (default: 1 USD = 7.20 CNY, 1 EUR = 1.08 USD). For accuracy-critical decisions, suggest the user verify with their bank's actual charge.
- **Trial dates** are user-entered from the confirmation email. The agent does not auto-detect trials from bank statements (out of scope for v1).
- **Zombie detection** is heuristic — `value_score` is a rough proxy. The agent should always frame it as a *suggestion*, not a verdict.
- **Cancellation help** is based on publicly documented steps; vendor flows change. The agent should tell the user: *"Verify the steps in the actual interface — vendors update their cancellation flow periodically."*
- **Export** to CSV/JSON is lossless; pair with `csv-explorer` or `format-converter` for deeper analysis.
- **Related skill `personal-expense-tracker`** handles *transactional* one-off spending; this skill handles *recurring* commitments. They are complementary — expenses feed into the monthly budget view, subs feed into the burn-rate view.
