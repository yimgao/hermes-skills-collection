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
