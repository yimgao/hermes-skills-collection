---
name: newsletter-digest
description: "Use when generating a curated newsletter or weekly digest on a specific topic. Searches multiple sources, summarizes key stories, and formats output as a polished newsletter ready to send."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [newsletter, content-curation, content-creation, weekly-digest, research, automation]
    related_skills: [competitive-research, content-repurposer, blog-post-writer, writing-plans]
---

# Newsletter Digest

> Generate a curated newsletter or weekly digest on any topic. Searches multiple sources for the latest stories, summarizes key developments, and formats the output as a polished newsletter ready to publish or send.

---

## Overview

This skill helps you create a professional newsletter from scratch — no RSS readers or manual curation needed. Given a topic or set of topics, it researches the latest news, picks the most important stories, summarizes each one with your own commentary, and formats everything into a clean newsletter template.

Designed to pair with cron for fully automated weekly digests. The output is structured so you can copy-paste to Mailchimp, Substack, Revue, ConvertKit, or any email platform.

**What it can produce:**
| Format | Description |
|--------|-------------|
| **Weekly digest** | Top 5-8 stories with summaries and commentary |
| **Industry roundup** | Curated links + one-liner takeaways |
| **Deep-dive single topic** | One major story with context and analysis |
| **Curated list** | "10 tools / articles / resources worth your time" |
| **Bilingual newsletter** | Each story in English + Chinese (side by side) |

---

## When to Use

- User asks: *"Generate a weekly AI newsletter about the latest LLM releases"*
- User asks: *"Create a tech startup digest for this week"*
- User asks: *"I want a daily newsletter about Chinese tech news"*
- User asks: *"Create a curated list of best design tools this month"*
- User asks: *"Set up a weekly cron to send me an AI news digest every Monday"*

---

## Core Workflow

### Step 1: Define Scope

Clarify with the user (or infer from context):

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `topic` | ✅ Yes | Subject area | "AI open source", "Chinese EV market" |
| `timeframe` | ❌ No | "daily", "weekly" (default), "monthly" | "past 7 days" |
| `language` | ❌ No | Output language | "English" (default), "中文", "bilingual" |
| `tone` | ❌ No | "professional", "casual", "curated" | "professional with commentary" |
| `story_count` | ❌ No | Number of stories (default 5-8) | 5 |

### Step 2: Research Sources

Search across multiple sources for the latest relevant content:

**Primary searches:**
```
"{topic} {timeframe} latest news"
"{topic} {timeframe} trends"
"{topic} {timeframe} breakthrough"
```

**Source-specific searches (context-dependent):**
```
# Tech / Startup
"{topic} site:techcrunch.com"
"{topic} site:theverge.com"
"{topic} site:36kr.com"  (Chinese tech)

# AI / ML
"{topic} site:arxiv.org"
"{topic} site:huggingface.co/blog"

# General
"{topic} site:reddit.com"
"{topic} site:news.ycombinator.com"

# Chinese sources (for Chinese-language newsletters)
"{topic} site:mp.weixin.qq.com"
"{topic} site:zhihu.com"
```

> 💡 **Pro tip:** For a weekly digest, use 3-5 different searches to ensure broad coverage. Prioritize sources by credibility: official announcements > reputable media > community discussions.

### Step 3: Select & Summarize

From the search results, select the **most important 5-8 stories** based on:
- **Relevance** — directly related to the topic
- **Recency** — within the intended timeframe
- **Impact** — significant news, not incremental updates
- **Diversity** — cover different angles, not all from one source

For each story, the agent should:
1. **Open the link** (browser) for a thorough read
2. **Extract key information**: what happened, why it matters, who it affects
3. **Write a 2-4 sentence summary** in the user's preferred tone
4. **Add commentary**: why this story matters for the reader

### Step 4: Compile Newsletter

Use the following template:

```markdown
# {Newsletter Title}

**{Day}, {Date} · {Issue #}**
*Curated by {AI/hermes} · {N} stories · {N} min read*

---

## 📌 Top Pick

### {Headline}

**Source:** [{Publication}]({url})

{2-3 paragraph summary with context and significance}

**Why it matters:** {one-sentence impact for the reader}

---

## 📰 This Week's Stories

### {Story 1 Headline}

**Source:** [{Publication}]({url}) · ⏱ {date}

{2-3 sentence summary}

**Key takeaway:** {one-liner}

---

### {Story 2 Headline}

**Source:** [{Publication}]({url}) · ⏱ {date}

{2-3 sentence summary}

**Key takeaway:** {one-liner}

---

[Continue for stories 3–8...]

---

## 🔗 Quick Links

| Story | Source | Read Time |
|-------|--------|-----------|
| {Headline} | [{Publication}]({url}) | {N} min |
| {Headline} | [{Publication}]({url}) | {N} min |
| {Headline} | [{Publication}]({url}) | {N} min |

---

## 💬 Editor's Note

{Personal closing thoughts, what to watch next week, a call to action (reply, subscribe, share), or a personal recommendation}

---

*Generated with Hermes Agent · Want to change topics or frequency? Just ask!*
```

### Step 5: Save & Offer Cron

Save the newsletter to a file:

```
~/newsletters/{topic}/YYYY-MM-DD-weekly-digest.md
```

If the user wants recurring delivery, offer to set up a cron:

```bash
cronjob \
  action=create \
  schedule="0 8 * * 1" \
  name="weekly-digest-{topic}" \
  prompt="Generate a weekly newsletter digest about {topic}. Research latest news, compile top 5-8 stories into newsletter format, and save to ~/newsletters/{topic}/."
  skills=["newsletter-digest"]
```

---

## Example Invocations

### Example 1: One-time weekly digest
```
User: Generate a weekly AI newsletter about open source LLMs
Hermes should:
  1. Search: "open source LLM latest news past week"
  2. Search: "open source LLM releases site:github.com"
  3. Open top 6-8 links for detailed reading
  4. Summarize each with key takeaways
  5. Compile into newsletter format
  6. Save to ~/newsletters/ai-open-source/
  7. Present final newsletter
```

### Example 2: Cron-based automated digest
```
User: Set up a weekly cron for AI startup news
Hermes should:
  1. Run one test generation
  2. Set up a cron job for every Monday 8 AM
  3. Confirm the cron schedule
```

### Example 3: Bilingual newsletter (Chinese tech)
```
User: 每周生成一份中文科技新闻摘要
Hermes should:
  1. Search Chinese sources: 36kr, 虎嗅, 知乎, 微信
  2. Select top 8 stories
  3. Write newsletter entirely in Chinese
  4. Save to ~/newsletters/中国科技/
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Too many search results, not enough signal.** | Prioritize official announcements and reputable media over rumors. Cross-reference before including. |
| 2 | **Same story from multiple sources.** | Use the most authoritative source. Link to primary source, not a reblog. |
| 3 | **Outdated results in search.** | Use explicit time filters in search queries (e.g., "past week", "after:2026-06-10"). |
| 4 | **Newsletter too long.** | Cap at 8 stories. Put less critical items in "Quick Links" table. Aim for <10 min read. |
| 5 | **No editorial voice.** | Add commentary — why each story matters. A newsletter without POV is just a link dump. |
| 6 | **Chinese-language sources harder to verify.** | Cross-reference with multiple Chinese sources (36kr + 虎嗅 + Zhihu). |
| 7 | **Cron-generated newsletters lack timeliness.** | Use tight timeframe in cron prompt ("past 7 days"). Set cron to run on the right day. |

---

## Verification Checklist

- [ ] Topic and scope confirmed with user
- [ ] 3-5 different searches performed for broad coverage
- [ ] Top 5-8 stories selected with diversity of sources
- [ ] Each story opened/read for detailed summary
- [ ] "Why it matters" commentary added per story
- [ ] Newsletter formatted with template structure
- [ ] Sources linked with proper URLs
- [ ] Language matches user's request (English / 中文 / bilingual)
- [ ] Saved to `~/newsletters/{topic}/`
- [ ] Cron job offered (if recurring requested)


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
