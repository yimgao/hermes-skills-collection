---
name: site-selection-pipeline
description: "Use when finding the optimal location to open a business. Runs a two-phase analysis: (1) screen top US cities by demographics and competition, (2) deep-dive local competitive analysis on the best city. Produces one comprehensive report."
version: 1.1.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [site-selection, pipeline, restaurant, competitive-analysis, demographics, location-intelligence, market-research]
    related_skills: [writing-plans, competitive-research]
---

# Site Selection Pipeline

> **Phase 1:** Screen US cities by population, demographics, competitor density, income, rent, and growth — find the best city for your business.
> **Phase 2:** Deep-dive competitive analysis on the #1 city — identify gaps, SWOT, and strategic recommendations.
> **Output:** One comprehensive report.

---

## Overview

This skill combines two analysis stages into a single pipeline. Instead of running separate skills and stitching results together, this one skill walks through the entire process:

1. **Screen** 8-12 candidate cities across the US
2. **Score** them on demand, competition, affordability, foot traffic, and growth
3. **Select** the #1 city
4. **Deep-dive** into that city's local competitive landscape
5. **Synthesize** everything into one actionable report

---

## When to Use

- *"Find the best US city to open a ramen + dumplings shop, then analyze local competition"*
- *"我想在美国开奶茶店，选城市再看竞品"*
- *"Full site selection analysis for my restaurant concept"*
- *"Best location for a bubble tea shop + competitive landscape"*

---

## Core Workflow

---

### Phase 1: City Screening

#### Step 1.1: Define Criteria

| Parameter | Required | Default | Example |
|-----------|----------|---------|---------|
| **Cuisine / Business type** | ✅ Yes | — | "Ramen + Dumplings", "Bubble Tea" |
| **Budget** | ❌ No | $300K | $200K, $500K |
| **Region** | ❌ No | Continental US | "West Coast", "Southeast", "Midwest" |
| **City preference** | ❌ No | Balance | "Growing mid-size", "College town", "Major metro" |
| **Priority** | ❌ No | Balanced | "Low competition > Low rent > High traffic" |

#### Step 1.2: Generate Candidate Cities

Generate 8-12 candidate cities. For **Asian cuisine**, consider:

| Tier | Cities |
|------|--------|
| Tier 1 (proven — may be saturated) | San Francisco, Los Angeles, NYC, Seattle |
| Tier 2 (growing — strong opportunity) | Austin, Denver, Raleigh-Durham, Charlotte, Nashville, Portland, Columbus |
| Tier 3 (emerging — first-mover) | Salt Lake City, Boise, Indianapolis, Omaha, Madison, Tulsa |
| Tier 4 (wildcard — research needed) | Spokane, Albuquerque, Knoxville, Greenville |

For other cuisines, adjust accordingly (e.g., taco shop → Southwest/Mountain West, bagel shop → Northeast/Midwest).

#### Step 1.3: Research Per City

For each candidate city, collect:

**Demographics:**
```bash
# Population
Search: "{city} population 2026"
Search: "{city} population growth rate"
Search: "{city} median age"

# Target demographic
Search: "{city} asian population percent"   # for Asian cuisine
Search: "{city} hispanic population percent" # for Latin cuisine
Search: "{city} median household income"
```

**Competitors:**
```bash
# Search Google Maps
Navigate: google.com/maps/search/{cuisine}+near+{city}/

# Extract for each competitor found:
# - Name
# - Rating (stars)
# - Known for / category
# - Address (rough area)
```

**Real estate:**
```bash
Search: "{city} average commercial rent per square foot restaurant"
Search: "{city} downtown retail vacancy"
```

**Growth indicators:**
```bash
Search: "{city} fastest growing neighborhoods 2026"
Search: "{city} new developments"
Search: "{city} tourism visitors per year"
```

#### Step 1.4: Score & Rank

Score each city 1-10 on five weighted dimensions:

| Dimension | Weight | What to measure |
|-----------|--------|-----------------|
| **Market demand** | 25% | Target demographic %, population size, income level |
| **Competition gap** | 25% | # of competitors vs city size, average ratings, saturation |
| **Affordability** | 20% | Commercial rent, startup costs, local income/rent ratio |
| **Foot traffic** | 15% | Walkability, downtown density, tourism, anchor attractions |
| **Growth potential** | 15% | Population growth rate, new developments, employer influx |

**Formula:**
```
Score = (demand × 0.25) + (competition_gap × 0.25) + (affordability × 0.20) + (foot_traffic × 0.15) + (growth × 0.15)
```

**Scoring rubric:**

| Score | Meaning |
|-------|---------|
| 9-10 | Ideal — strong demand, low competition, good economics |
| 7-8 | Good — solid opportunity, minor trade-offs |
| 5-6 | Average — feasible but not optimal |
| 3-4 | Weak — significant challenges |
| 1-2 | Poor — do not recommend |

#### Step 1.5: Output Scoring Matrix

```markdown
### 🏆 Candidate City Rankings

| Rank | City | Total | Demand | Competition | Affordability | Traffic | Growth |
|------|------|-------|--------|-------------|---------------|---------|--------|
| 🥇 | {City} | {N}/10 | {N} | {N} | {N} | {N} | {N} |
| 🥈 | {City} | {N}/10 | {N} | {N} | {N} | {N} | {N} |

**Top pick:** {City} — {one-sentence why}
```

---

### Phase 2: Local Competitive Analysis

Take the **#1 city** from Phase 1 and run a deep competitive analysis.

#### Step 2.1: Search Local Competitors

Use Google Maps to find the top competitors in the city:

```
Navigate: google.com/maps/search/{cuisine}+near+{city}/
```

Extract for each competitor:
- **Name**
- **Rating** (e.g., ⭐ 4.2)
- **Address** (note if downtown, suburban, etc.)
- **Known for** (description/specialty)
- **Hours** (closing time — identify late-night gaps)
- **Price range**

Select the **top 5 most relevant competitors**.

#### Step 2.2: Analyze Market Gaps

Compare the competitive landscape to identify gaps:

| Gap Type | Examples |
|----------|----------|
| **Cuisine gap** | No one serves {specific dish/concept} |
| **Location gap** | Downtown has zero options |
| **Time gap** | No late-night option (all close by 9-10PM) |
| **Price gap** | No premium / no budget option |
| **Experience gap** | Existing options are dine-in; no takeout/delivery focus |
| **Quality gap** | Existing options have mediocre ratings |

#### Step 2.3: Generate SWOT

| Category | Look For |
|----------|----------|
| **Strengths** | What local competitors do well collectively |
| **Weaknesses** | Common complaints across reviews |
| **Opportunities** | Gaps identified above |
| **Threats** | Barriers to entry, market saturation, economic risks |

#### Step 2.4: Strategic Recommendations

Based on gaps + SWOT, recommend:
- **Positioning** — what type of business to open
- **Differentiators** — 3-5 specific ways to stand out
- **Pricing strategy** — suggested price range
- **Best neighborhood** — specific area with reasoning
- **Risk factors** — what to watch out for

---

### Phase 3: Final Report

Combine everything into one report:

```markdown
# Complete Site Selection Report: {Cuisine/Business}

**Date:** {YYYY-MM-DD}
**Generated by:** Site Selection Pipeline

---

## 🎯 Executive Summary

{3-4 sentence bottom line: best city, best neighborhood, best positioning, estimated costs}

---

## PART 1: City Screening

### Criteria
| Parameter | Value |
|-----------|-------|
| Cuisine | {type} |
| Budget | ${N}K |
| Region | {region} |
| Priority | {balanced / low rent / low competition} |

### Candidate Cities
List of 8-12 cities considered…

### Scoring Matrix
[Ranked table with scores]

### 🏆 Top Pick: {City}
{Why this city wins — 2-3 paragraphs}

---

## PART 2: Local Competitive Analysis

### Market Overview
{2-3 paragraphs about the local food scene}

### Top 5 Competitors
| # | Name | Rating | Area | Known For | Price |
|---|------|--------|------|-----------|-------|
| 1 | {Name} | ⭐X.X | {area} | {specialty} | {$$} |

### Competitor Deep Dives
[Per-competitor analysis]

### SWOT
| Category | Findings |
|----------|----------|
| Strengths | … |
| Weaknesses | … |
| Opportunities | … |
| Threats | … |

### Market Gaps
1. {Gap 1}
2. {Gap 2}
3. {Gap 3}

---

## 🎯 Final Recommendation

### Best City
{City, State}

### Best Neighborhood
{Specific neighborhood} — {why}

### Recommended Concept
{What to open — specific concept description}

### Differentiators
1. {Differentiator 1}
2. {Differentiator 2}
3. {Differentiator 3}

### Financial Estimate
| Item | Estimate |
|------|----------|
| Startup costs | ${N}K |
| Monthly rent | ${N} |
| Projected monthly revenue | ${N}K |
| Projected annual profit | ${N}K |

### Next Steps
1. {Action 1}
2. {Action 2}
3. {Action 3}

---

## 📋 Sources
- Google Maps competitor search
- Wikipedia / Census demographic data
- City economic development reports
- Commercial real estate listings
```

---

## Example Invocation

```
User: Find the best US city to open a ramen + dumpling shop, then analyze local competition.
       Budget ~$300K. Prefer growing mid-size cities with low competition.

Agent should:
  Phase 1:
    1. Generate candidate list (Austin, Denver, Raleigh-Durham, Charlotte, 
       Nashville, Columbus, Portland, SLC, Indianapolis, Boise)
    2. Research each city's population, Asian %, income, ramen competitor count
    3. Score & rank → Raleigh-Durham #1
    
  Phase 2:
    4. Google Maps search "ramen near Durham NC"
    5. Extract top 5 competitors with ratings
    6. SWOT analysis
    7. Identify market gaps (downtown gap, late-night gap, dumpling gap)
    
  Phase 3:
    8. Combine into one report
    9. Save to ~/dev/reports/site-analysis/
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Phase 1 picks a city you can't verify in Phase 2.** | If Google Maps shows limited data for the #1 city, fall back to #2. |
| 2 | **Google Maps limited view (not signed in).** | Ratings still visible in list view. Focus on star ratings and names. |
| 3 | **Demographic data out of date.** | Use 2025-2026 census estimates. Note if data is older. |
| 4 | **Skipping the "why" in scoring.** | Don't just assign numbers — explain why Austin scores 5/10 for competition. |
| 5 | **Report too long to read.** | Executive summary on page 1. Detailed analysis in appendices. |

---

## Verification Checklist

- [ ] Cuisine/business type confirmed
- [ ] 8-12 candidate cities generated
- [ ] Population + target demographic data per city
- [ ] Competitor count per city (Google Maps)
- [ ] Rent estimate per city
- [ ] Growth indicators per city
- [ ] Cities scored on 5 weighted dimensions
- [ ] Top city selected with clear reasoning
- [ ] Local competitive analysis on top city (5 competitors)
- [ ] Market gaps identified
- [ ] SWOT completed
- [ ] Strategic recommendations with differentiators
- [ ] Financial estimate
- [ ] Report saved to `~/dev/reports/site-analysis/`
