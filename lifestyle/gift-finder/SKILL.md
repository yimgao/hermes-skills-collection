---
name: gift-finder
description: "Use when searching for gift ideas — takes recipient details (age, relationship, interests, occasion, budget) and returns personalized recommendations with reasoning."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [gift, shopping, recommendations, lifestyle, occasion]
    related_skills: [travel-itinerary-planner, recipe-generator]
---

# Gift Finder

> Find the perfect gift. Takes recipient details — age, relationship, interests, occasion, budget — and searches for personalized recommendations with purchase links and reasoning.

---

## When to Use

- *"What should I get my girlfriend for her birthday? Budget $100"*
- *"找礼物给我爸，60岁喜欢钓鱼"*
- *"White elephant gift ideas under $30"*
- *"Best gifts for a tech startup founder"*

---

## Core Workflow

### Step 1: Gather Details

| Field | Question | Example |
|-------|----------|---------|
| Recipient | Who is it for? | Girlfriend, Dad, Coworker |
| Age | How old? | 30, 60, 25 |
| Occasion | What event? | Birthday, Christmas, Wedding |
| Budget | How much? | $50, $100-200 |
| Interests | What do they like? | Cooking, Tech, Hiking, Gaming |

### Step 2: Generate Ideas

Use reasoning + search to find 3-5 specific gift ideas.

For each:
- **Item name** (specific product)
- **Price**
- **Where to buy** (link if known)
- **Why it fits** (connects to their interests)

### Step 3: Present

```markdown
# 🎁 Gift Recommendations

**For:** {Recipient}
**Occasion:** {Occasion}
**Budget:** ${N}

---

## Top Pick: {Item}
- **Price:** ${N}
- **Why:** {personalized reason}
- **Where:** [Amazon](url) / [Etsy](url)

## Also Great
| Item | Price | Why |
|------|-------|-----|
| {Item} | ${N} | {reason} |
| {Item} | ${N} | {reason} |

## Budget Options
- {Item} — ${N} (if over budget, this is a good backup)
```


---

## 📋 Data Sources & Accuracy

This skill relies on searching external data. Follow these guidelines to ensure accuracy:

### Primary vs Secondary Sources
| Priority | Source Type | Examples |
|----------|-------------|----------|
| 🥇 **Primary (prefer)** | Government / Official | Census.gov, BLS, city economic dev, official APIs |
| 🥈 **Secondary** | Aggregators / Reviews | Google Maps, Yelp, LoopNet, Wikipedia |
| 🥉 **Tertiary** | Estimates / Inferences | Industry reports, blog posts, news articles |

### Accuracy Rules
1. **Always cite the source** for each data point — don't state numbers without attribution
2. **When sources conflict**, prefer: government > official > aggregator > blog
3. **If data is unavailable**, say "Not found" — do NOT fabricate or approximate without stating it's an estimate
4. **Mark estimates clearly** with "~" or "estimated" — never present guesses as facts
5. **Use ranges** when uncertain (e.g., "$20-25/sqft" not "$22.50/sqft")
6. **Timestamp your data** — note when it was collected (e.g., "as of June 2026")

### When Web Search Returns Limited Data
- Note the limitation explicitly: "Google Maps limited view", "Search blocked by CAPTCHA"
- Fall back to known data or general market knowledge
- Explicitly mark knowledge-based data as "based on general market knowledge"
- Never invent competitor names, ratings, or prices

### Verification Checklist
- [ ] Every number attributed to a source
- [ ] Estimates clearly marked (use "~" or "estimated")
- [ ] Unavailable data noted as "not found"
- [ ] Data collection timestamp recorded
- [ ] Confidence level noted (High / Medium / Low)
