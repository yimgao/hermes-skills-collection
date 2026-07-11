---
name: salary-negotiation-coach
description: "Get the offer you deserve — counter-offer scripts, market-rate data, equity negotiation, BATNA strategy, and total-comp modeling for both job offers and freelance contracts"
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [career, salary, negotiation, offer, counter-offer, equity, rsu, freelance-rates, total-compensation, batna, compensation]
    related_skills: [job-hunt-pipeline, jd-resume-matcher, cover-letter-writer, personal-crm, personal-expense-tracker]
---

# Salary Negotiation Coach（薪资谈判教练）

> Don't accept the first number. Whether it's a full-time offer, a freelance gig, or a promotion — get a script, a market range, and a walk-away number in 60 seconds.

| Capability | Description |
|-----------|-------------|
| 💰 Market rate lookup | Pull salary bands by role, level, geo from public + proprietary sources |
| 🧮 Total comp modeling | Base + bonus + equity + 401k match + PTO value + sign-on + benefits — one comparable $/yr |
| 📜 Counter-offer scripts | Word-for-word emails that push back without burning the bridge |
| 🎯 BATNA builder | Define walk-away number from real alternatives, not vibes |
| 📈 Equity negotiation | RSU refreshers, option strike pricing, vesting acceleration, early-exercise |
| 🤝 Freelance rate setting | Day/hour rate from market data + scope; red-flag low offers |
| 🗓️ Multi-round strategy | Plan the 3-5 touchpoints: screen → onsite → verbal → written → close |
| 💾 Offer history | Persist every offer (real or paper) to `~/.hermes/data/offers.json` for leverage |
| 🌐 Bilingual scripts | US English + 中文 scripts for 中美两地 interviews |

---

## When to Use

- *"I got an offer for $130k base + 0.05% equity. Is this good?"*
- *"Help me counter — I want $150k and they came in at $135k"*
- *"I'm a senior iOS dev in Berlin, 8 YOE — what's market rate in 2026?"*
- *"Freelance client offered $80/hour for design work — push back?"*
- *"What should I ask for in Year 1 performance review?"*
- *"Walk me through RSU refresh negotiation after IPO"*
- *"Write a counter-offer email that doesn't sound aggressive"*
- *"我拿到了 Google L5 的 offer，base $180k，要不要 counter?"*
- *"我在深圳 5 年后端，期权怎么谈？"*

---

## Core Workflow

### Step 1: Capture the Offer

User says *"Got an offer: Senior PM at Stripe, $165k base, 0.08% equity over 4 years, $25k sign-on, no relocation"*.

The agent parses into a structured offer record:

```json
// Stored in ~/.hermes/data/offers.json
{
  "id": "offer-2026-07-10-001",
  "company": "Stripe",
  "role": "Senior Product Manager",
  "level": "L5",
  "location": "San Francisco, CA",
  "remote": "hybrid",
  "base_salary": 165000,
  "currency": "USD",
  "bonus_target_pct": 10,
  "equity": {
    "type": "rsu",
    "grant_value_total": 66000,           // 0.08% × post-money est
    "vesting_years": 4,
    "cliff_months": 12,
    "strike_price": null,                 // option only
    "refresh_eligible": false
  },
  "sign_on_bonus": 25000,
  "relocation_package": 0,
  "pto_days": 20,
  "health_insurance_premium_paid_pct": 100,
  "other_perks_value_annual": 4000,       // lunch, gym, phone stipend
  "status": "verbal",
  "received_on": "2026-07-09",
  "decision_deadline": "2026-07-16",
  "competing_offers": ["offer-2026-07-08-002"],
  "notes": "Team is payments infra, hiring manager was director-level"
}
```

**What fields are required vs. optional:**

| Field | Required? | How to ask |
|-------|-----------|------------|
| Company + role | yes | inferred from user message |
| Base salary | yes | ask if missing: "What base did they quote?" |
| Equity details | preferred | "How much equity, what type, what vesting?" |
| Sign-on / relocation | optional | often $0 — note if so |
| Decision deadline | yes | critical for BATNA timing |
| Competing offers | high-value | "Do you have other offers in flight?" |
| Cash flow concerns | optional | "Any equity cliff coming up at current job?" |

---

### Step 2: Market Rate Lookup

Pull **3 data sources** in parallel and triangulate. Always show the range, never a single number.

**Public data sources (free):**

| Source | URL pattern | Best for |
|--------|-------------|----------|
| levels.fyi | `https://www.levels.fyi/companies/{slug}/comp` | Tech, FAANG, levels L3-L7 |
| Glassdoor | search `{role} {city}` | Quick range, older data |
| Blind (anonymous app) | app search | Real recent offers w/ comp breakdown |
| Payscale / Salary.com | search | Mid-market, non-tech |
| H1B salary database | h1bdata.info | US work-visa sponsored roles — usually the cleanest comp data |
| 脉脉 / 看准网 | 国内搜 | 国内互联网 / 独角兽 |

**For US tech roles (default heuristic if user is vague):**

| Level | Base range (SF Bay Area, 2026) |
|-------|-------------------------------|
| L3 / E3 / P2 (new grad) | $130k–$165k base, 0.02–0.05% |
| L4 / E4 / P3 | $165k–$210k base, 0.05–0.12% |
| L5 / E5 / P4 (Senior) | $200k–$280k base, 0.08–0.25% |
| L6 / E6 / P5 (Staff) | $260k–$370k base, 0.15–0.50% |
| L7 / E7 / P6 (Principal) | $330k–$500k base, 0.30–1.00% |
| L8+ (Distinguished) | $400k+ base, 0.50%+ |

**Geo-adjusted multipliers (apply to base, not equity):**

| Location | Multiplier vs SF Bay |
|----------|----------------------|
| San Francisco / San Jose | 1.00 |
| New York / Boston / Seattle | 0.92 |
| Los Angeles / Austin / Denver | 0.85 |
| Chicago / Atlanta / Miami | 0.78 |
| Remote (US company) | 0.88 (often capped lower) |
| London / Berlin / Amsterdam | 0.65 (varies wildly) |
| Singapore / Hong Kong | 0.55 |
| India (Bangalore / Mumbai) | 0.18 |
| China (北上深) | 0.22 |
| China (二线) | 0.14 |

Always cite **at least 2 sources** in the report and note the recency ("levels.fyi pulled Q1 2026 data; reports from 6+ months ago undercount current offers due to 2024–25 market cooling").

---

### Step 3: Total Comp Modeling

Convert everything to a single annualized $/yr number so comparison is honest:

```python
def annual_total_value(offer):
    base = offer["base_salary"]
    bonus = base * (offer.get("bonus_target_pct", 0) / 100)

    # Equity value depends on liquidity. Use these heuristics:
    equity = offer["equity"]
    if equity and equity["type"] == "rsu":
        # Private: apply 0.4–0.6 illiquidity discount
        # Public: divide by vesting years, no discount
        if offer.get("public_company", False):
            equity_annual = equity["grant_value_total"] / equity["vesting_years"]
        else:
            equity_annual = equity["grant_value_total"] * 0.5 / equity["vesting_years"]
    elif equity and equity["type"] == "options":
        # Use Black-Scholes: only count "in the money" portion
        equity_annual = bs_value(equity["strike_price"], current_fmv) / equity["vesting_years"]
    else:
        equity_annual = 0

    sign_on_amortized = offer["sign_on_bonus"] / offer.get("expected_tenure_years", 2)
    pto_value = (offer["base_salary"] / 260) * offer.get("pto_days", 15)
    benefits_value = offer.get("other_perks_value_annual", 0)

    return {
      "cash_now": base + bonus,
      "equity_annualized": equity_annual,
      "amortized_sign_on": sign_on_amortized,
      "pto_value": pto_value,
      "benefits_value": benefits_value,
      "total_annual_value": base + bonus + equity_annual + sign_on_amortized + pto_value + benefits_value,
      "first_year_cash": base + bonus + offer["sign_on_bonus"]  # sign-on hits Y1
    }
```

**Output table (rendered to user):**

| Component | Annualized Value | Notes |
|-----------|------------------|-------|
| Base salary | $165,000 | solid for SF L4 |
| Bonus target (10%) | $16,500 | paid quarterly |
| RSU (0.08%, 4-yr vest) | $8,250 | $66k ÷ 4 yrs; private, 0.5 illiquidity discount |
| Sign-on bonus | $12,500 | $25k ÷ 2 yr expected tenure |
| PTO (20 days) | $12,692 | $165k / 260 working days × 20 |
| Health + perks | $4,000 | fully paid premium, lunch |
| **Total annual** | **$218,942** | |
| **First-year cash (incl. sign-on)** | **$218,500** | |

Always show two numbers: annual recurring vs. first-year. Sign-on can mislead.

---

### Step 4: BATNA & Walk-Away Number

Before counter-offering, define the **walk-away number**: the offer below which you decline.

```markdown
## Building your walk-away
1. **Current comp**: your present total comp — opportunity cost of switching
2. **Existing runway**: how long can you stay unemployed? (impacts pressure)
3. **Competing offers**: every other "in flight" offer, even paper ones
4. **Market replacement**: 90-day reapplication probability at current status
5. **Non-cash priorities**: learning, brand, lifestyle, WLB — quant or deprioritize

Output:
- Floor (reject): $X total
- Target (counter): $Y total (typically 10–15% above current offer)
- Aspiration (shoot-for-the-moon): $Z total
```

**Formulas the agent uses:**

```text
walk_away       = max(current_total_comp + 15%, competing_offer_low + $5k)
counter_target  = current_total_comp × 1.10    (if you have alternatives)
                 OR (current_offer × 1.15)     (if you don't)
aspiration      = market_p75_for_your_level    (always justify with data)
```

⚠️ **Guardrails**: if user's walk-away is *below* current comp, flag it. They've underpriced their own floor — common in 2026 with layoffs and weak market.

---

### Step 5: Counter-Offer Script

User says *"Counter to $150k base + 0.10% equity. Keep sign-on. Polite but firm."*

The agent drafts based on:
- **Tone** — "polite-but-firm" / "enthusiastic-and-flexible" / "firm-no-room" / "bluffing leverage" / "cold and calculated"
- **Channel** — email / phone (always recommend email for paper trail)
- **Leverage** — competing offer / strong market data / internal promotion / layoff financial pressure
- **Risk** — how replaceable is the candidate? how late in their hiring cycle?

#### Email script — Polité-but-Firm (US, full-time)

```
Subject: Re: Stripe — Senior PM offer

Hi {Recruiter first name},

Thank you for the offer — I'm genuinely excited about Stripe and the Payments
Infra team. The role lines up with what I want to do next, and {Hiring Manager}
gave me a clear sense of the work.

Before I respond, I'd like to discuss the package. After researching current
market rates for Senior PMs in SF (levels.fyi data, recent offers in my
network), and weighing the cost of my current vesting cliff, I need to be at:

  Base: $185,000
  Equity: 0.10% over 4 years (vesting unchanged)
  Sign-on: maintain at $25,000
  Start date: flexible on my side (can start in 3 weeks)

I'm comparing this against one other offer {truthfully, if you have one} and a
promotion path at my current company, but Stripe is my top choice if we can
get within range.

Is there flexibility here? I'd love to sign by end of week.

Thanks,
{Your name}
```

#### Email script — 强势礼貌 (中文，国内 BAT)

```
主题: 关于 {岗位} 薪资 offer 的沟通

{HR 老师} 您好,

非常感谢贵司的 offer,{团队} 是我目前最心仪的方向,{Hiring Manager} 在面试
中分享的产品路线图与我过去几年的积累非常匹配。

但就 package 部分,经过对市场行情的调研(拉勾、脉脉同期同岗数据,以及两
个对标 offer),我希望在以下几项中调整:

  月薪:从 35k → 42k base(对标 P6 中位数)
  期权:从 0.05% → 0.08%(4 年 vesting 不变)
  签字费:维持 50k

原因是:目前手里的 {competing offer} 给到了 40k base,加之我在现东家的
vesting cliff 即将到来(明年初 ~80k 部分解锁),请理解这次的诉求。

期待您的好消息,这周内给到答复会比较方便我做最终决策。

谢谢!
{姓名}
```

**Always provide:**
- Tone variants (2-3 per scenario)
- What to say if they refuse ("decline politely" script)
- What to say if they say "I'll get back to you" (boundary on timeline)
- A "no" you can live with vs. walk-away hard bottom

---

### Step 6: Multi-Round Strategy Map

Most negotiations aren't one email — they're 3-5 rounds. Provide a plan:

```markdown
## Negotiation timeline — Stripe PM
| Round | When | What they say (typical) | Your response |
|-------|------|-------------------------|---------------|
| 1 | verbal offer call | "165 base + 0.08%" | "I need 24h, will email a response" |
| 2 | your counter (24h) | (your email above) | — |
| 3 | their reply (1–3 days) | "Can do 175 + 0.08%" | "Closer, but I need 185 + 0.10%" |
| 4 | back-and-forth (1–3 days) | "180 + 0.09%, that's max" | Accept / decline / final counter |
| 5 | close (≤ 7 days from verbal) | "Sign by Friday?" | Decide |

Tactics by round:
- R1: never accept on the call. Always ask for the email.
- R2: counter 12-18% above initial (not 20%+; they need room to "give")
- R3: split the diff. Don't ask for both base + equity — pick one.
- R4: ask for accelerators — extra PTO, sign-on bump, flexible start, title upgrade
- R5: accept or walk. Don't drag past deadline or you burn the bridge.
```

---

### Step 7: Negotiation on Comp Components

Most people negotiate only base. Pros attack every line:

| Lever | What to ask | Typical give |
|-------|-------------|--------------|
| Base | +$10–$25k | Hardest to move above 15% |
| Sign-on | +$5–$30k | Easiest to give — counts toward total but doesn't recur |
| Equity | +0.02–0.10% | Negotiate on percentage, not dollar value |
| Vesting cliff | Reduce 12mo → 6mo or accelerate start | Common ask, often granted |
| Sign-on clawback | Make it non-clawback | Almost always granted on request |
| Relocation | +$10–$20k | Often flat-rate, easy to bump |
| Title | "Senior II" / "Staff I" | Cheap for them, big for your brand |
| Start date | +2–6 weeks PTO bridge | Frequent give |
| Performance review | Move to 6mo from 12mo cycle | Easy give, big impact |
| Bonus target % | +5–10% | Variable — easier at senior levels |
| 401k match | +1–3% | Common, but HR-locked |
| PTO | +3–10 days | Common, cheap |
| Remote policy | 100% remote / 2 days | Lifestyle huge; cost ~$0 |

---

### Step 8: Close & Persist

Final script after agreement:

```markdown
# 🎉 Negotiation closed — total value increased $48k/yr

## Concession summary
| Lever | Before | After | Gain |
|-------|--------|-------|------|
| Base | $165k | $180k | +$15k/yr |
| Equity | 0.080% | 0.095% | +$12.5k/yr (annualized, private) |
| Sign-on | $25k | $30k | +$5k one-time |
| Vesting cliff | 12mo | 12mo (unchanged, but accelerated 25% on start date) | cliff risk ↓ |
| **Total** | $218.9k/yr | $248.4k/yr | **+$29.5k/yr (+13.5%)** |

## What you did right
- Asked, didn't accept
- Cited data (levels.fyi + your network + competing offer)
- Negotiated % on equity, not $ on equity
- Pushed back on tit-for-tat

## Lessons persisted to memory
- Your market band: L5 PM SF = $200–280k base, 0.08–0.25% equity
- Your recurring anchors for future: +12% above initial = realistic
- Verbatim recruiter patterns flagged: "this is our best and final" (often not true at FAANG)
```

Save to `~/.hermes/data/offers.json` with `status: accepted` + `final_accepted_on`. Save also in `~/.hermes/memories/USER.md` under `## Negotiation Profile` so the next session has context.

---

## Example Invocations

### Example 1: First-time negotiator, full-time offer

**User:** *"I got an offer from a Series B startup: Senior Backend Engineer, $145k base, 0.15% equity over 4 years, 1-year cliff, no sign-on. I'm currently at $130k + 0.05% at my current place (pre-IPO, cliff in 18 months). What do I do?"*

**Agent:**
```markdown
# Offer Quick Take: Series B Startup — Sr Backend

## Your offer decoded
- Base: $145k
- Equity: 0.15% over 4 yr, 1-yr cliff (post-money est: ~$60k over 4 yrs → $15k/yr pre-tax)
- Sign-on: $0
- Location: San Francisco

**Total comp (annualized):** ~$163k
**vs. current:** ~$155k + vesting cliff upside = **+$8k/yr if your current vests**, **+$50k/yr if their current doesn't (cliff kills it)**

## Market check (your level: Senior Backend, SF, Series B)
- levels.fyi L5 E5 equivalent: $180–230k base
- Series B-specific (smaller grants but more upside %): $160–200k base, 0.10–0.30% equity

**Verdict:** base is ~12% **below** market. Equity is generous — Series B 0.15% is high.

## My counter proposal (you send this)
- Base: **$165k** (still below market median, easy to defend)
- Equity: maintain 0.15%, ask for **6-month cliff instead of 12-month**
- Sign-on: **$15k** (to compensate for the cliff reduction risk)
- Vesting start: date of offer acceptance (accelerated)

## Why this counter wins
- 12→6 month cliff cuts your downside risk if you wash out in year 1
- If they say "no cliff", you keep sign-on → you have the same $$ risk-free
- If they say "no to everything", they weren't serious — that tells you a lot

I drafted the email — want me to send it as a paste-ready response?
```

### Example 2: Multiple competing offers (BATNA-rich)

**User:** *"I have 3 offers: Google L5 ($220k + 220 RSU), Meta E5 ($245k + $300k RSU), Stripe L5 ($200k + 60k options). I prefer Stripe's mission. Help me decide."*

**Agent:**
```markdown
# Offer Stack Comparison — 3 Options

| Comp | Google L5 | Meta E5 | Stripe L5 |
|------|-----------|---------|-----------|
| Base | $220,000 | $245,000 | $200,000 |
| RSU (annualized) | $55,000 | $75,000 | $8,500 (priv. 0.5 disc.) |
| Bonus | $22,000 (10%) | $24,500 (10%) | $20,000 (10%) |
| Sign-on | $25,000 | $50,000 | $10,000 |
| **Total comp (annual)** | **$325,250** | **$404,500** | **$242,380** |
| Cash first year | $267,000 | $319,500 | $230,000 |

## Decision matrix

If your top variable is **$$$**: Meta, by a wide margin.
If your top variable is **mission + WLB**: Stripe ($200k is below market; you should counter).
If your top variable is **lifestyle + salary hybrid**: Google.

## Suggested negotiation plays

**With Google:** Use Meta as leverage to push RSU to 250k total ($62.5k/yr). Easy ask, you have BATNA.

**With Meta:** Use Google as leverage to push RSU to 350k. Mention the Meta brand isn't uniquely better than Google for resume — harder ask but possible.

**With Stripe (your preference):**
Counter at base $215k + 0.10% equity options + $30k sign-on + **4-year vest starts day 1, no cliff**.
Total comp would jump to ~$270k, which still undercuts Meta but keeps your mission fit.

Tactic: be transparent — *"I'm choosing between Stripe and two FAANG offers. I want to make Stripe work; here's the math on what that looks like."* This is **not** a bluff — it's a fact.

Want me to draft the three emails?
```

### Example 3: Freelance rate negotiation

**User:** *"Client wants to pay me $80/hour for design system work at a YC startup. They said 'we're a startup, budget is tight'. I usually charge $150/hr."*

**Agent:**
```markdown
# Freelance Rate Push-Back — YC Startup

## Your rate check
- Your stated rate: $150/hr
- US freelance market mid-senior product designer (5+ yrs): $125–200/hr
- **Specialized** (design systems, component library): $150–225/hr

Their offer ($80/hr) is roughly **40–55% below market** for the niche. That's not "startup budget" — that's "they're treating you as a contractor with no leverage."

## The right counter
Three options, pick your energy:

### Option A: Rate hold (clean)
> "Hi {name}, my rate for design-system work is $150/hr. I can offer 5% off — $142/hr — if we commit to 6+ months. Below that I lose the ability to prioritize your project. Let me know."

### Option B: Project-based (de-risks for them)
> "Per-hour doesn't work for either of us. Flat-rate for this scope: $24,000. That covers discovery, system audit, library v1 build, and documentation. Comes out to ~$110 effective/hr, but you get a price ceiling."

### Option C: Hybrid (compromise)
> "$120/hr, billed monthly min 40 hours. If we go past 40 hrs/week, I drop to $100/hr. Cap total at $50k. In exchange I commit to 3 months."

## What to watch for
- ❌ "We'll pay you in equity" — almost always a bad deal for contractors. Equity is an employee comp tool.
- ❌ "We can offer visibility / case study" — fine as a bonus, not as substitute for cash.
- ❌ Unpaid trial work — guaranteed to extend; rarely converts to paid.

If they come back at $100/hr after your counter: that's a 33% reduction. Decline or get a scope cut. Don't reduce your rate to a number that makes you resent the work.
```

### Example 4: 中文场景 — 国内 Offer + 期权谈判

**User:** *"我拿了某 AI 创业公司(A轮)的 offer: 高级算法工程师,base 55k×16,期权 0.04%(4年vest, 1年cliff),签字费 30k。但是手里的另一个大厂 offer 是 base 60k×16 + 25万 RSU/年。创业公司是我想去的。怎么谈?"*

**Agent:**
```markdown
# Offer 谈判方案: AI 创业公司 (你的首选)

## 你手里的牌
| 项目 | 创业公司 | 大厂 | 差距 |
|------|----------|------|------|
| Base | 55k×16 = 88万/年 | 60k×16 = 96万/年 | **-8万/年** |
| 期权/RSU | 0.04%(≈40-60万, 4年) | 25万 RSU/年 | 大厂显著更高 |
| 签字费 | 30k | (待问) | 优势 |
| 时间线 | 一周内决策 | 两周内决策 | 创业公司更紧 |

## 关键判断
- 现金上,创业公司每年少 **8万+25万=33万/年**(对比 4 年期权的潜在价值)
- 大厂 RSU 是确定收益;创业期权是或有
- **但是你想去这家**,那么谈判目标不是"追平大厂",而是"合理补偿你放弃的安全感"

## 我的反提案

### Base:55k → **60k** (打平大厂,合理理由:对标 + 你可以接受降10-15%的现金)
- 创业公司常会说"我们base天花板就是这样",所以准备一个 B 方案

### 期权:0.04% → **0.06%**
- 理由:6 个月 cliff 改为 1 年 cliff 后,风险增加,需要更多 upside
- 同时要求:vesting 改为月度 vest(而不是按年 cliff 后 vest),这样 1 年后你已经有 25% 落袋

### 加签:30k → **50k**
- 这是最容易谈下来的——他们的 HR 不希望因为 cash 流失候选人

### 加码条件(次要诉求,如果上面失败)
- 6 个月 review 一次,触发 bonus / 调薪通道
- 入职即给 3-5 天 PTO 预支
- 远程工作比例可谈(每周 3 天到岗,但如果搬家可换城市)

## 你的三封邮件草稿

我已经写好了,邮件语气是"坚定但留余地"——明确这是双向选择,你在乎这家公司,但也保留了退出路径。需要的话我把中文版本直接给你。
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User accepts on the call | Always ask for the offer in writing first. Even an acceptance email — paper trail matters. |
| User counters with no data | Back every ask with 2+ sources (levels.fyi, Blind, Glassdoor, h1bdata, 脉脉). Numbers > feelings. |
| User uses the "what's your current comp?" trap | Refuse or deflect: "I'm focused on the role's market value, not my current salary." or "What's the budgeted range for this role?" |
| Equity cliff kills your upside | Negotiate cliff reduction or accelerated vesting at signing. Often the single highest-leverage ask. |
| User wants to ask for 25%+ above initial | Compress to 12–18%. Recruiters need room to "give you something." Ask big, expect middle. |
| User takes a "best and final" at face value | Often not true. One polite email "is there any flexibility on the equity refresh after 12 months?" can move things. |
| User compares base only across offers | Force total comp view — show RSU, bonus, sign-on, PTO value. Many "low" offers beat "high" ones once you annualize. |
| User fails to disclose competing offers | "I have another offer" is 3x more effective than vague "I'm evaluating options." Use it precisely (one offer is best — not 'several'). |
| Counter-offer at current job after receiving external offer | Almost never worth it. Counter-offers reset trust; most people leave in 12 months anyway. |
| Freelancer accepts equity instead of cash | Equity ≠ comp for contractors. If they're a real company, they have real cash. Decline and re-quote cash. |
| User lies about competing offer | This skill never recommends lying. "I'm choosing between you and one other option" can be true even if it's not literally an offer. |
| User wants to renegotiate sign-on to be non-clawback | Standard request, almost always granted. If not granted, it's a yellow flag on the company's policies. |
| User silent on visa / relocation timing | Pin this in R3-4. Relocation package usually flat, but timing and tax-equalization can save 10–30k. |
| User accepts too quickly to be polite | Politeness costs money. The polite move is to ask once, professionally. Recruiters are paid to negotiate — that's the job. |
| Walk-away below current comp | Reframe: switch cost includes ramp-down (1-3 months lower output), context loss, social ties. Subtract 10-15% from "raw salary bump" to get "real comp delta." |

---

## Verification Checklist

- [ ] Offer parsed into structured `~/.hermes/data/offers.json` record (company, role, level, base, equity, sign-on, deadline)
- [ ] At least 2 market-rate sources cited, with recency note (current quarter preferred)
- [ ] Total comp modeled — both annual recurring AND first-year cash shown separately
- [ ] Walk-away number calculated from BATNA + current comp + 15% delta minimum
- [ ] Counter-offer target is 10–18% above initial (not >25%, not <8%)
- [ ] Counter script includes: thank-you, market context, specific number, deadline hint, BATNA mention (if exists), graceful tone
- [ ] Multi-round strategy mapped with timing expectations
- [ ] Comp-component levers addressed (not just base)
- [ ] Equity valued correctly: RSU vs options, private vs public, illiquidity discount applied
- [ ] Freelance scenario distinguished: rate ≠ salary, project scope matters
- [ ] No advising deception ("I have 3 offers" if you have zero)
- [ ] Chinese scripts available and natural (not literal translations)
- [ ] Final accepted offer persisted to memory for next session
- [ ] User's negotiation profile (typical asks, style, levers worked) saved to `~/.hermes/memories/USER.md`

---

## Data Sources & Accuracy

| Source | Reliability | When to use |
|--------|-------------|-------------|
| **levels.fyi** | High (self-reported, recent) | Tech companies, levels L3-L8 |
| **Glassdoor** | Medium (anonymous, may be outdated) | Quick range check, non-tech |
| **Blind app** | High (verified employees, anonymous) | Recent offers, real negotiation threads |
| **h1bdata.info** | Very high (public USCIS filings) | US sponsored roles, exact base salary |
| **Payscale / Salary.com** | Medium | Mid-market, not leveled well |
| **脉脉 / 看准网** | Medium (国内, also mixed quality) | 国内 BAT、独角兽 |
| **Built In / Tech NYC / LA** | High (curated) | Local tech markets |
| **Recruiter LinkedIn messages** | Anecdotal but very real | Read with skepticism on equity valuations |

**Accuracy limits the agent should always disclose:**

- Equity grants on **private** companies use post-money estimates that move with each round. Actual vesting value can swing 2-5x by IPO/acquisition. Always present as a range, never a precise number.
- **Hourly → salary conversion**: freelance day rates should not be naively ×2000. Real rates include healthcare, software, taxes, downtime. Annualize at ×1500-1800, not ×2080.
- **Bonus targets** are not guaranteed. Many years, especially 2023-2024, hit 0%. Treat as ceiling, not floor.
- **Sign-on clawback** is common: if you leave in <12 months, you owe it back. Always ask for it to be non-clawback.
- **"Best and final"** is a recruiter saying they're done. **In 60% of cases** it's negotiable one more time, especially on equity or sign-on.
- **Currency conversion** is computed at offer date, but FX moves. For total comp modeling, use a 6-month trailing average.

**Storage:**

- Offers persisted at `~/.hermes/data/offers.json` with full audit trail (status transitions, draft emails, recruiter back-and-forth)
- Negotiation profile in `~/.hermes/memories/USER.md` → `## Negotiation Profile` section
- Related: `job-hunt-pipeline` handles sourcing→apply→track; this skill handles **offers→accept**. `personal-expense-tracker` will use the new total comp as budget input. `personal-crm` knows recruiter contacts for future use.
- Privacy: all data local. Never log into bank/brokerage. Never share `~/.hermes/data/offers.json` outside the user's machine.
