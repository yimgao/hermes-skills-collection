---
name: fact-checker
description: "Use when verifying any factual claim before you share, quote, or republish it — verifies numbers, dates, quotes, news events, company facts, and scientific statements against primary sources. Returns a verdict card (VERIFIED / DISPUTED / UNVERIFIABLE) with cited sources, confidence level, and the specific sentence or number that failed. Built for Twitter threads, newsletter drafts, investor memos, slides, and any high-stakes writing."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [research, fact-check, verification, misinformation, source-checking, claims, due-diligence, citation, primary-source, journalism, write-up, due-diligence, twitter, newsletter, investor-memo]
    related_skills: [arxiv-paper-summarizer, competitor-news-monitor, newsletter-digest, content-repurposer, twitter-thread-writer, linkedin-post-generator, investment-memo, llm-output-validator]
---

# 🔍 Fact Checker — 事实核查 / 验证再分享

> Verify before you share. 把一段文字、数字、引语或新闻事件拆成一条条可核查的声明,逐条对照原始来源,返回"已核实/有争议/无法核实"的三色判定卡片 + 具体哪一句错了。避免把错误数字写进推特、newsletter、投资备忘录或路演幻灯片。

---

## Overview

This skill verifies any factual content before the user republishes, quotes, or shares it. The user pastes a paragraph (or a single sentence, or a number), the skill splits it into atomic checkable claims, hunts down primary sources for each, and returns a **verdict card** with three states:

| Verdict | Meaning | What to do |
|---------|---------|------------|
| 🟢 **VERIFIED** | At least one primary source confirms the exact claim | Safe to publish |
| 🟡 **DISPUTED** | Sources conflict, numbers vary, or attribution unclear | Flag + rewrite or hedge |
| 🔴 **FALSE** | Primary source contradicts the claim | Do not publish as-is |

It is built for the moment *before* you hit "Tweet" / "Send" / "Publish" — when you have a draft paragraph and a quiet doubt. It is **not** a full investigative journalism platform; it is a 60-second sanity check backed by primary sources.

| Capability | What It Does | How |
|------------|-------------|-----|
| **Claim splitting** | Decomposes any text into atomic checkable claims | Heuristic segmentation + claim-type tagging (stat / quote / event / attribution / scientific) |
| **Primary-source search** | Hunts the original source (paper, SEC filing, official press release, gov data) | `web_search` + domain-priority filtering (`.gov`, `.edu`, primary publisher, arXiv, SSRN) |
| **Source triangulation** | Cross-checks ≥2 independent sources before grading | Falls back to "UNVERIFIABLE" when only one weak source exists |
| **Numeric normalization** | Recognizes that "1.4M users" may equal "1,400,000" or "≈1M" | Fuzzy numeric match with tolerance % |
| **Quote verification** | Distinguishes "said X" from "said roughly X" | Searches for the exact quote string in known archives |
| **Date sanity check** | Flags impossible dates ("founded in 1820" for a 2010 startup) | Calendar + lifespan lookup |
| **Verdict card** | Returns a one-screen summary: claim, verdict, source, confidence, fix-it | Structured Markdown block |
| **Rewrite suggestions** | For each DISPUTED / FALSE claim, suggests a hedged rewrite | "approximately", "according to", "as of" |

Everything is **local-first** in workflow — no claim database uploaded. Search uses `web_search` and `web_fetch`; verification reasoning stays in-session.

---

## When to Use

- *"Verify this paragraph before I tweet it"* / *"帮我核一下这段话再发推"*
- *"Is this stat real? 'X% of Y have done Z'"* — single-stat sanity check
- *"Did the CEO actually say this?"* — quote attribution verification
- *"I'm about to publish a newsletter, fact-check it"* — batch verification of a draft
- *"Check the numbers in my investor memo"* — pre-publication audit
- *"Was this news event real / when did it actually happen?"* — event verification
- *"Is this academic claim supported by the paper?"* — science claim check
- *"Quick sanity check: did X really happen in 2024?"* — date/event check
- *"我写了一段推文,帮我验证里面所有的数字和引语"*
- Any draft with **specific numbers, dates, names, quotes, or "according to..."**

Do **not** use for: opinion pieces (no factual claims to verify), coding tasks, recipe/numeric-math problems, or "is this email a phishing" (use `phishing-link-inspector`).

---

## Core Workflow

### Step 1: Extract atomic claims

Take the user's text and split it into checkable units. Each unit must be independently verifiable (or not).

```text
INPUT: "Tesla delivered 1.8M EVs in 2024, beating BYD's 1.6M. Elon Musk called it 'the best year ever' in the Q4 earnings call."

CLAIMS:
  [1] STAT   — "Tesla delivered 1.8M EVs in 2024"
  [2] STAT   — "BYD delivered 1.6M EVs in 2024"   (implied comparison)
  [3] STAT   — "Tesla beat BYD in 2024 EV deliveries"
  [4] QUOTE  — "Elon Musk said 'the best year ever' on Q4 earnings call"
  [5] EVENT  — "Q4 2024 earnings call occurred"   (context)
```

Claim-type taxonomy:

| Type | Example | What to search |
|------|---------|----------------|
| `STAT` | "X% / $Y / N users / 2024-Q3" | Official reports, gov data, press releases |
| `QUOTE` | "She said '...'" | Primary speech transcript, interview source |
| `EVENT` | "X happened on DATE" | News from ≥2 reputable outlets with same date |
| `ATTRIB` | "According to X, ..." | Trace the original study/report X cited |
| `SCIENTIFIC` | "Studies show X causes Y" | PubMed, arXiv, Cochrane, primary paper |
| `ENTITY` | "Company X was founded in YYYY" | SEC filings, official "About" page, Wikipedia primary refs |
| `COMPARISON` | "A is bigger than B" | Verify both halves independently first |

---

### Step 2: For each claim, find primary sources

Search priority (highest authority first):

```text
1. PRIMARY       — the original issuer (company press release, gov agency, named paper, official transcript)
2. AUTHORITATIVE — Reuters / AP / Bloomberg / WSJ / FT / Nature / Science / gov stats office
3. REFERENCE     — Wikipedia (only for cross-checking, never as the only source)
4. SECONDARY     — news outlets, trade press, industry blogs (use for cross-confirmation)
5. WEAK          — social media, opinion sites, content farms (flag-only, never confirm)
```

Search command template:

```bash
# Numeric / stat verification
curl -s "https://duckduckgo.com/html/?q=Tesla+2024+annual+deliveries+press+release" | grep -oP 'href="[^"]*"' | head -20

# Quote verification (exact-match search)
curl -s "https://duckduckgo.com/html/?q=%22the+best+year+ever%22+Musk+earnings" | head -100

# Scientific claim
curl -s "https://duckduckgo.com/html/?q=site:pubmed.ncbi.nlm.nih.gov+coffee+longevity+2024"
```

For each candidate source, fetch the page (or the abstract for papers) and extract the exact number / quote / date.

---

### Step 3: Match & grade

For each claim, run the match:

```python
# Pseudo-rule (illustrative)
def grade(claim, sources):
    if not sources:
        return "UNVERIFIABLE", 0.0, "No primary source located"

    primary = sources[0]
    match_score = similarity(claim.value, primary.value)  # 0-1

    if claim.type == "STAT":
        # Tolerate rounding if within ±5%
        if numeric_close(claim.value, primary.value, tol=0.05):
            return "VERIFIED", 0.95 if len(sources) >= 2 else 0.75, primary.url
        else:
            return "FALSE", 1.0, f"Source says {primary.value}, claim says {claim.value}"
    elif claim.type == "QUOTE":
        if exact_or_near(claim.text, primary.text):
            return "VERIFIED", 0.9, primary.url
        else:
            return "DISPUTED", 0.7, "Quote does not appear in primary transcript"
    elif claim.type == "EVENT":
        if date_match(claim.date, primary.date):
            return "VERIFIED", 0.85, primary.url
        else:
            return "DISPUTED", 0.7, f"Primary source dates event to {primary.date}"
    # ...
```

Confidence weights (used to grade confidence in the verdict):

| Match quality | Sources | Confidence | Verdict |
|---------------|---------|------------|---------|
| Exact numeric match | ≥2 independent | 0.95 | 🟢 VERIFIED |
| Exact numeric match | 1 primary | 0.75 | 🟢 VERIFIED (single source) |
| Within ±5% of primary | 1 source | 0.60 | 🟡 DISPUTED (rounding) |
| Differs > 5% | 1 source | 0.90 | 🔴 FALSE |
| No source found | 0 | 0.00 | ⚫ UNVERIFIABLE |
| Sources conflict | ≥2 disagree | 0.50 | 🟡 DISPUTED |

---

### Step 4: Produce the verdict card

```markdown
## Fact-Check Report — {title or first 60 chars of input}

**Checked:** {N} claims · {M} verified · {K} disputed · {F} false · {U} unverifiable
**Overall risk:** {LOW / MEDIUM / HIGH} — {one-line guidance}

| # | Claim | Verdict | Confidence | Source | Fix |
|---|-------|---------|------------|--------|-----|
| 1 | "Tesla delivered 1.8M EVs in 2024" | 🟢 VERIFIED | 0.95 | [Tesla Q4 release](url) | — |
| 2 | "BYD delivered 1.6M EVs in 2024" | 🟡 DISPUTED | 0.65 | [BYD annual](url) says 1,777,000 NEVs | Change to ≈1.77M or specify "passenger NEVs" |
| 3 | "Tesla beat BYD in 2024" | 🔴 FALSE | 0.90 | BYD's 1.77M > Tesla's 1.79M only if counting BEV+PHEV | Rewrite: "narrowly edged out BYD in 2024 BEV-only deliveries" |
| 4 | "Elon said 'the best year ever'" | 🟢 VERIFIED | 0.85 | [Q4 transcript, p.4](url) | — |
| 5 | Q4 2024 earnings call occurred | 🟢 VERIFIED | 0.95 | [Tesla IR](url) | — |

### Suggested safe rewrite (if any claims failed)
> {Revised paragraph with hedging, attribution, or corrected numbers, ready to publish.}

### What I could not check
- {List claims where no primary source was found in time, so the user knows what residual risk remains.}
```

---

### Step 5: Iterate

- If the user says *"the BEV-only figure"* — re-grade claim 3 with the narrower definition.
- If the user provides the original source URL — fast-path to VERIFIED with high confidence.
- If the user wants a **publicly defensible** version — add hedged language + citation footnotes.

---

## Example Invocations

### Example 1: Pre-tweet sanity check

> **User:** *Verify this before I tweet: "OpenAI reached 600M weekly active users in July 2025, up from 400M in February." Source: someone on Twitter.*

```
[INFO] Extracting claims from paste...
  [1] STAT: "OpenAI 600M WAU in July 2025"
  [2] STAT: "OpenAI 400M WAU in February 2025"

[EXEC] Searching primary sources...
  [1] 600M WAU July 2025 → Found: OpenAI official statement Sep 2025 says 600M WAU "as of July"
      → Confirmed in Reuters, The Information, FT (independent corroboration)
  [2] 400M WAU Feb 2025 → Found: OpenAI statement Feb 2025 said "400M users" but ambiguous if monthly vs weekly
      → Best source: OpenAI official X post, mentions "weekly active" implicitly

[INFO] Verdict:
  [1] 🟢 VERIFIED (0.90) — OpenAI official + Reuters
  [2] 🟡 DISPUTED (0.65) — original was "users", not "weekly active users"
      → FIX: change to "400M monthly active users in February 2025" OR drop the qualifier
```

### Example 2: Newsletter draft batch check

> **User:** *"I'm sending my Sunday newsletter. Please fact-check this paragraph:*
> *"According to a Stanford study, 78% of knowledge workers now use AI daily. Average time saved: 2.1 hours per day. The study surveyed 5,000 workers in Q1 2025."*

```
[INFO] Extracting 3 claims...
  [1] SCIENTIFIC: "Stanford study, 78% of knowledge workers use AI daily"
  [2] STAT: "Average 2.1 hours saved per day"
  [3] SCIENTIFIC: "5,000 workers surveyed Q1 2025"

[EXEC] Primary source hunt...
  [1] Search → Stanford HAI 2025 AI Index Report says different figures (annual: 33%, daily: 26%)
      → No Stanford study found with "78% daily" claim
  [2] Same report → no "2.1 hours/day saved" figure
  [3] Could not locate a 5,000-worker survey matching these numbers

[INFO] Verdict:
  [1] 🔴 FALSE (0.90) — No primary source supports 78% daily figure; closest published number is 26%
      → FIX: drop the stat or rewrite as "more than 1 in 4 knowledge workers now use AI daily, per Stanford's 2025 AI Index"
  [2] 🔴 FALSE (0.90) — Not found in primary source
      → FIX: remove the time-saved figure OR replace with a properly attributed source
  [3] ⚫ UNVERIFIABLE — cannot trace to a Stanford publication

OVERALL RISK: 🔴 HIGH — Recommend NOT publishing these claims without primary sources.
SUGGESTED REWRITE:
  "Stanford's 2025 AI Index Report finds that 26% of knowledge workers now use AI daily, more than double the share from 2023."
```

### Example 3: Quote attribution check

> **User:** *"Did Einstein really say 'Insanity is doing the same thing over and over and expecting different results'? I'm including it in a presentation."*

```
[INFO] Single QUOTE claim, attributed to Einstein.

[EXEC] Primary source hunt...
  → No primary publication found. Quote is widely circulated on quote sites.
  → Quote-trace databases (Quote Investigator, Stanford literary database) mark this as
    MISATTRIBUTED. Earliest verifiable similar phrasing: Rita Mae Brown, 1983 novel.

[INFO] Verdict:
  🔴 FALSE (0.95) — Widely misattributed. No Einstein primary source exists.

[INFO] Suggested rewrite:
  "Often misattributed to Einstein; the earliest known phrasing is from Rita Mae Brown's 1983 novel 'Sudden Death'."
```

### Example 4: 帮我核一下推文 (Chinese)

> **用户:** *"帮我核查一下:中国新能源汽车 2024 年销量 1,286 万辆,同比增长 35.5%。来源是中汽协。"*

```
[INFO] 提取声明:
  [1] STAT: "中国新能源汽车 2024 年销量 1,286 万辆"
  [2] STAT: "同比增长 35.5%"

[EXEC] 搜索原始来源:
  → 中汽协 (CAAM) 官方 2025 年 1 月发布会数据
  → 找到: 2024 年新能源车销量 1,286.6 万辆,同比增长 35.5%

[INFO] 裁定:
  [1] 🟢 已核实 (0.95) — 中汽协官方发布会数据一致
  [2] 🟢 已核实 (0.95) — 中汽协官方: 35.5% 同比

总体风险: 🟢 低 — 可以放心发布。
建议补充: 注明"中汽协 2025 年 1 月数据"。
```

---

## Common Pitfalls

| Problem | Why It Happens | Solution |
|---------|---------------|----------|
| Wikipedia cited as the only source | Wikipedia is tertiary; it cites primaries | Always open the Wikipedia references and cite the *primary* directly |
| Round numbers assumed exact | "about 1M" vs exact "1,073,402" — different confidence | If the source says 1.07M and the claim says "1M", mark DISPUTED with a ±5% tolerance or use "approximately 1M" |
| Old stat presented as current | "X% in 2024" but the data is actually from 2019 | Always include the data vintage in the claim, then verify the year matches |
| Quote attribution by hearsay | "Steve Jobs said..." — actually a paraphrase | Use exact-string search for the quote; mark DISPUTED if only paraphrases exist |
| Confusing two companies / two people | Tesla BEV vs total; BYD passenger vs commercial | For comparison claims, verify both halves independently and specify the scope (BEV-only? globally? passenger?) |
| Source paywall / behind login | WSJ / FT paywalled, can't read the article | Fall back to the Reuters / Bloomberg / official IR mirror; mark confidence lower |
| Confirmation bias from search results | Search engine surfaces sources that confirm the claim first | Always check at least one source you'd expect to *disagree* (e.g., a critic, a competing outlet) |
| Outdated by the time you publish | Stat verified last week, but a correction was issued | For high-stakes publishing, re-verify within 24h of publication; consider adding "as of {DATE}" |
| Confusing LLM hallucination with reality | Model "remembers" a plausible-sounding stat that's actually fabricated | Treat your own draft as untrusted input — run every number through the verifier |

---

## Verification Checklist

Before delivering the result, ensure:

- [ ] Each atomic claim was independently identified (no skipped sentences)
- [ ] At least one search was run per claim
- [ ] Primary source was preferred over secondary; Wikipedia was used only as cross-check
- [ ] For numeric claims, the exact figure was compared (with tolerance noted)
- [ ] For quotes, exact or near-exact text match was attempted
- [ ] For dates, the calendar and timezone were checked
- [ ] Confidence score reflects both match quality and number of independent sources
- [ ] Verdict card contains: claim, verdict, confidence, source URL, suggested rewrite if failed
- [ ] User knows which claims are UNVERIFIABLE (residual risk)
- [ ] Output is paste-ready: user can copy-paste the rewrite into their draft directly
- [ ] No fabricated sources — every URL returned was actually fetched and read

---

## Data Sources & Accuracy

This skill is a **reasoning + search layer**, not a fact database. It does not store claims; it queries live sources for each verification. The accuracy of any verdict is bounded by:

1. **Search result freshness** — search engines may surface outdated results; the skill should re-query for "latest" stats on time-sensitive topics
2. **Source authority hierarchy** — primary > authoritative > reference > secondary > weak; the verdict card always names the source tier
3. **Match tolerance** — numeric match uses ±5% by default; the user can request strict (exact) or loose (±10%) mode
4. **LLM extraction risk** — when extracting figures from a long page, the skill should cite the exact sentence or table cell, not paraphrase

**Never-cite list** (treat with extreme suspicion if these are the only sources):
- Content farms (e.g., random SEO "top 10" posts)
- Social media posts without primary backing
- LLM-generated pages (e.g., when the search result is itself an AI summary)
- Stale aggregators (e.g., a "2024 statistics" page last updated 2019)

**Default to "I cannot verify this"** rather than guessing. The verdict "⚫ UNVERIFIABLE" is always preferable to a confident-but-wrong 🟢 VERIFIED.