---
name: competitor-news-monitor
description: "Use when monitoring competitors for news, product launches, funding rounds, and market moves. Searches multiple sources and generates structured briefings. Designed to pair with cron for recurring checks."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [competitive-intelligence, monitoring, research, cron, news, market-intelligence]
    related_skills: [local-competitive-analysis, product-pricing-tracker, competitive-research, newsletter-digest]
---

# Competitor News Monitor

> Monitor competitors for news, product launches, funding rounds, partnerships, and market moves. Searches multiple sources and generates structured competitive intelligence briefings. Designed to pair with cron for fully automated recurring checks.

---

## Overview

This skill tracks what your competitors are up to. Given a list of competitor names or URLs, it searches across news, blogs, social media, and industry publications for the latest developments — then compiles everything into a structured competitive intelligence briefing.

Perfect for staying ahead of the market without spending hours browsing. When paired with a cron job, you get a weekly or daily briefing delivered automatically.

**What it tracks:**
| Category | Examples |
|----------|----------|
| **Product launches** | New features, new products, beta releases |
| **Funding / investment** | Rounds raised, acquisitions, IPOs |
| **Partnerships** | New integrations, strategic alliances |
| **Hiring** | Key executive hires, team expansions |
| **Pricing changes** | Price increases, new plans, discounts |
| **Marketing moves** | Ad campaigns, rebranding, new positioning |
| **Crisis / PR** | Layoffs, controversies, customer complaints |
| **Content** | Blog posts, thought leadership, research papers |

---

## When to Use

- User asks: *"Monitor what OpenAI, Anthropic, and Google are doing in AI"*
- User asks: *"Check the latest news about my competitors: Linear, Notion, Coda"*
- User asks: *"Set up weekly monitoring for my top 3 competitors"*
- User asks: *"What's new with WeWork and Regus this week?"*
- User asks: *"Track product launches in the AI coding assistant space"*

---

## Core Workflow

### Step 1: Define Competitors

Accept a list of competitors. The user can provide:

```yaml
competitors:
  - name: "OpenAI"
    url: "https://openai.com/blog"
    keywords: ["GPT", "OpenAI", "Sam Altman"]
  - name: "Anthropic"
    url: "https://anthropic.com/blog"
    keywords: ["Claude", "Anthropic"]
  - name: "Google DeepMind"
    url: "https://deepmind.google/blog"
    keywords: ["Gemini", "DeepMind", "Google AI"]
```

Or a simple list:
```
"Monitor: OpenAI, Anthropic, Google DeepMind"
```

### Step 2: Search for News

For each competitor, run multiple searches:

```python
# Core searches
"{competitor} latest news {timeframe}"
"{competitor} product launch {timeframe}"
"{competitor} funding acquisition {timeframe}"

# Source-specific
"{competitor} site:techcrunch.com"
"{competitor} site:theverge.com"
"{competitor} site:bloomberg.com"

# Social / community
"{competitor} site:reddit.com"
"{competitor} news {timeframe}"

# Their own blog (if URL known)
site:{competitor_blog_url}
```

### Step 3: Filter & Prioritize

For each result, assess:
- **Relevance** — directly about the competitor?
- **Significance** — real news, not speculation?
- **Recency** — within the monitoring timeframe?
- **Uniqueness** — not a reblog of the same story

**Priority levels:**
| Level | Label | Examples |
|-------|-------|----------|
| 🚨 **Critical** | Major strategic move | Funding, acquisition, CEO change, product launch |
| ⚠️ **Notable** | Interesting development | New feature, partnership, hire, price change |
| ℹ️ **Informational** | Background noise | Blog post, interview, minor update |
| ❌ **Skip** | Irrelevant | Spam, off-topic, old news |

### Step 4: Generate Briefing

```markdown
# Competitive Intelligence Briefing

**Period:** {start_date} – {end_date}
**Competitors monitored:** {N}
**Generated:** {YYYY-MM-DD HH:MM}

---

## 📊 Summary

| Competitor | 🚨 Critical | ⚠️ Notable | ℹ️ Info | Top Story |
|------------|-------------|------------|---------|-----------|
| {Name} | {N} | {N} | {N} | {headline} |
| {Name} | {N} | {N} | {N} | {headline} |

**Total stories found:** {N}
**Most active competitor:** {Name}

---

## 🚨 Critical Stories

### {Date} — {Competitor Name}

#### {Headline}
**Source:** [{Publication}]({url})

{2-4 sentence summary with context}

**Why it matters:** {impact on the competitive landscape}

---

## ⚠️ Notable Stories

### {Date} — {Competitor Name}

#### {Headline}
**Source:** [{Publication}]({url})

{1-2 sentence summary}

**Signal:** {what this tells us about their strategy}

---

## ℹ️ Information

| Date | Competitor | Story | Source |
|------|------------|-------|--------|
| {date} | {Name} | {Brief description} | [{link}]({url}) |
| {date} | {Name} | {Brief description} | [{link}]({url}) |

---

## 🔮 Trends & Insights

{2-3 paragraph analysis of patterns across all competitors:
- Are multiple competitors moving in the same direction?
- Any new category emerging?
- Who's gaining / losing momentum?
- Any threats or opportunities for you?}

---

## 📋 Sources

| Competitor | Sources Searched |
|------------|-----------------|
| {Name} | TechCrunch, The Verge, {blog}, Reddit |
| {Name} | Bloomberg, {blog}, LinkedIn |
```

### Step 5: Save & Set Up Cron

Save the briefing:

```
~/research/competitive-monitoring/{topic}/YYYY-MM-DD-briefing.md
```

Offer to set up recurring monitoring:

```bash
cronjob \
  action=create \
  schedule="0 9 * * 1" \
  name="competitor-monitor-{topic}" \
  prompt="Monitor the following competitors for the past week: {list}. Search for news, product launches, funding, and key moves. Generate a competitive intelligence briefing."
  skills=["competitor-news-monitor"]
```

---

## Example Invocations

### Example 1: One-time check
```
User: Check the latest news about Linear, Notion, and Coda
Hermes should:
  1. For each: search "{name} latest news past week"
  2. Open top stories for detailed reading
  3. Prioritize into Critical / Notable / Info
  4. Compile briefing
  5. Save to ~/research/competitive-monitoring/productivity-tools/
```

### Example 2: Set up cron monitoring
```
User: Set up weekly competitor monitoring for OpenAI, Anthropic, and Google AI
Hermes should:
  1. Run one test briefing
  2. Set up a cron job for every Monday 9 AM
  3. Confirm the schedule
```

### Example 3: Specific event monitoring
```
User: Track if any of my competitors launched new features this week:
  - Notion
  - Coda
  - Monday.com
Hermes should:
  1. Search for product launch / new feature news
  2. Focus only on product-related stories
  3. Generate features-focused briefing
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Too many results for big companies.** | Filter by significance. Apple/Google/Microsoft will have daily news — focus on product/corporate moves. |
| 2 | **Same story from multiple outlets.** | Link to the most authoritative source. Note other outlets as "also reported by...". |
| 3 | **Outdated / recycled news.** | Use explicit time filters ("past week", "after:YYYY-MM-DD"). |
| 4 | **Missing smaller competitors.** | Add broader search terms for smaller companies (they may not appear in major outlets). |
| 5 | **China-based competitors hard to track.** | Search Chinese sources: 36kr, 虎嗅, Zhihu, WeChat. |
| 6 | **Cron generates empty briefings.** | Check if search still works. Layout changes or CAPTCHAs may break automated scraping. |
| 7 | **News about the category, not the competitor.** | Filter strictly to stories that mention the competitor by name. |

---

## Verification Checklist

- [ ] Competitor list confirmed with user
- [ ] Multiple searches per competitor (news + blogs + social)
- [ ] Stories prioritized (Critical / Notable / Info)
- [ ] Each story opened/read for accurate summary
- [ ] "Why it matters" / strategic signal noted per story
- [ ] Briefing formatted with template
- [ ] Trends & insights section has cross-competitor analysis
- [ ] Sources listed per competitor
- [ ] Saved to `~/research/competitive-monitoring/{topic}/`
- [ ] Cron job offered (if recurring monitoring requested)
